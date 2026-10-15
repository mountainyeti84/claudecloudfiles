#!/usr/bin/env python3
"""Small OpenRouter client for the /openrouter Claude Code skill.

Standard library only. Authentication:
  * In Claude cloud sessions the agent network proxy injects the OpenRouter
    credential into every request to openrouter.ai, so no key is needed here
    and none is sent.
  * Elsewhere (e.g. a local machine without the proxy), OPENROUTER_API_KEY is
    used if it is set. The key is never printed.

Subcommands:
  key                         Check the connection / credit status (free).
  models [--search TEXT]      List models with pricing and context (free).
  resolve NAME                Resolve an alias or exact ID to a model (free).
  aliases                     Show every alias and what it resolves to (free).
  ask NAME --prompt-file F    Send one prompt to one model (billed).
  compare A,B --prompt-file F Send the same prompt to two models (billed x2).

Exit codes: 0 ok, 1 usage/resolve error, 2 API/network error,
            3 prompt blocked by the sensitive-content / size guard.
"""

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = "https://openrouter.ai/api/v1"
HERE = os.path.dirname(os.path.abspath(__file__))
ALIASES_FILE = os.path.join(os.path.dirname(HERE), "aliases.json")
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "openrouter-skill")
MODELS_CACHE = os.path.join(CACHE_DIR, "models.json")
CACHE_TTL = 3600
DEFAULT_MAX_PROMPT_CHARS = 60000

# Variants that are never picked automatically for a bare alias.
AUTO_EXCLUDE = re.compile(r":(batch|free|extended|beta)$|-image|-vision|-exp$|banana|guard|-tts|-audio")

SECRET_PATTERNS = [
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("OpenRouter/OpenAI-style key", re.compile(r"\bsk-(or-v1-|proj-|ant-)?[A-Za-z0-9_\-]{20,}")),
    ("AWS access key", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{20,}")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Stripe key", re.compile(r"\b(sk|rk)_(live|test)_[A-Za-z0-9]{16,}")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
    ("password/secret assignment",
     re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token|client[_-]?secret)\b\s*[:=]\s*['\"]?[^\s'\"]{8,}")),
    ("connection string with credentials", re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s:/@]+:[^\s@/]{3,}@")),
]


class ApiError(Exception):
    pass


# --------------------------------------------------------------------------- HTTP

def _headers():
    h = {
        "Content-Type": "application/json",
        "HTTP-Referer": "https://claude.ai/code",
        "X-Title": "Claude Code /openrouter skill",
    }
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        h["Authorization"] = "Bearer " + key
    return h


def _explain(status, body):
    try:
        msg = json.loads(body).get("error", {}).get("message") or body
    except (ValueError, AttributeError):
        msg = body
    msg = str(msg)[:500]
    hints = {
        400: "Bad request - often an invalid model ID or unsupported parameter.",
        401: "Authentication failed. In a Claude cloud session check that the OpenRouter network "
             "secret is still attached to this environment; elsewhere set OPENROUTER_API_KEY.",
        402: "Insufficient OpenRouter credits for this request (or key spending limit reached).",
        403: "Forbidden - the key's limits or the network proxy policy blocked this request.",
        404: "Model or endpoint not found - the model may have been removed or renamed.",
        408: "OpenRouter timed out waiting for the model.",
        429: "Rate limited by OpenRouter or the upstream provider.",
        502: "Upstream model provider error.",
        503: "No provider is currently available for this model.",
    }
    return "HTTP %s: %s\n%s" % (status, msg, hints.get(status, "OpenRouter API error."))


def request(method, path, payload=None, timeout=60, retries=2):
    data = json.dumps(payload).encode() if payload is not None else None
    attempt = 0
    while True:
        req = urllib.request.Request(API + path, data=data, method=method, headers=_headers())
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code in (429, 502, 503) and attempt < retries:
                wait = e.headers.get("Retry-After")
                wait = float(wait) if wait and wait.replace(".", "", 1).isdigit() else 2 ** (attempt + 1)
                time.sleep(min(wait, 20))
                attempt += 1
                continue
            raise ApiError(_explain(e.code, body))
        except (TimeoutError, OSError) as e:  # URLError is a subclass of OSError
            reason = getattr(e, "reason", e)
            if "timed out" in str(reason).lower():
                raise ApiError("Request timed out after %ss. Retry with --timeout larger, a smaller "
                               "prompt, or a faster model." % timeout)
            raise ApiError("Network error contacting OpenRouter: %s" % reason)


# ------------------------------------------------------------------------- models

def load_models(refresh=False):
    if not refresh and os.path.exists(MODELS_CACHE) and time.time() - os.path.getmtime(MODELS_CACHE) < CACHE_TTL:
        with open(MODELS_CACHE) as f:
            return json.load(f)
    data = request("GET", "/models", timeout=60)["data"]
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(MODELS_CACHE, "w") as f:
        json.dump(data, f)
    return data


def per_million(value):
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return None if v < 0 else v * 1_000_000


def fmt_price(value):
    v = per_million(value)
    if v is None:
        return "variable"
    if v == 0:
        return "free"
    return "$%.2f" % v if v >= 0.1 else "$%.4f" % v


def fmt_ctx(n):
    if not n:
        return "?"
    return "%.3gM" % (n / 1_000_000) if n >= 1_000_000 else "%gK" % round(n / 1000)


def model_summary(m):
    p = m.get("pricing", {})
    provider = m.get("name", "").split(":")[0] if ":" in m.get("name", "") else m["id"].split("/")[0]
    return {
        "id": m["id"],
        "name": m.get("name"),
        "provider": provider,
        "input_per_1M": fmt_price(p.get("prompt")),
        "output_per_1M": fmt_price(p.get("completion")),
        "context": fmt_ctx(m.get("context_length")),
        "context_length": m.get("context_length"),
    }


def summary_line(m):
    s = model_summary(m)
    return "%s (%s) | in %s / out %s per 1M tokens | context %s" % (
        s["name"], s["id"], s["input_per_1M"], s["output_per_1M"], s["context"])


def load_aliases():
    with open(ALIASES_FILE) as f:
        return json.load(f)["aliases"]


def _alias_candidates(rule, models):
    inc = re.compile(rule["match"])
    exc = re.compile(rule["exclude"]) if rule.get("exclude") else None
    out = [m for m in models
           if inc.search(m["id"]) and not (exc and exc.search(m["id"])) and not AUTO_EXCLUDE.search(m["id"])]
    return sorted(out, key=lambda m: m.get("created", 0), reverse=True)


def resolve(name, models=None):
    """Return dict(model, how, alternatives) or raise ValueError with suggestions."""
    models = models if models is not None else load_models()
    by_id = {m["id"]: m for m in models}
    key = name.strip()
    low = key.lower()

    if key in by_id:
        return {"model": by_id[key], "how": "exact model ID", "alternatives": []}

    aliases = load_aliases()
    if low in aliases:
        rule = aliases[low]
        for pid in rule.get("prefer", []):
            if pid in by_id:
                return {"model": by_id[pid], "how": "alias '%s' (pinned preference)" % low, "alternatives": []}
        cands = _alias_candidates(rule, models)
        if cands:
            return {"model": cands[0], "how": "alias '%s' -> newest matching model" % low,
                    "alternatives": [c["id"] for c in cands[1:6]]}
        raise ValueError("Alias '%s' matched no currently available model." % low)

    # Fallback: substring search over IDs and names.
    hits = [m for m in models if low in m["id"].lower() or low in (m.get("name") or "").lower()]
    hits = [m for m in hits if not AUTO_EXCLUDE.search(m["id"])] or hits
    hits.sort(key=lambda m: m.get("created", 0), reverse=True)
    if len(hits) == 1:
        return {"model": hits[0], "how": "unique search match for '%s'" % key, "alternatives": []}
    if hits:
        raise ValueError("'%s' is ambiguous. Candidates (newest first):\n  %s" % (
            key, "\n  ".join(summary_line(m) for m in hits[:10])))
    raise ValueError("No model matches '%s'. Run the 'models --search' subcommand to browse." % key)


# ------------------------------------------------------------------------- guards

def scan_sensitive(text):
    found = []
    for label, pat in SECRET_PATTERNS:
        for mt in pat.finditer(text):
            line_no = text.count("\n", 0, mt.start()) + 1
            snippet = mt.group(0)
            redacted = snippet[:4] + "..." + ("[%d chars]" % len(snippet))
            found.append("line %d: %s (%s)" % (line_no, label, redacted))
    return found


# ------------------------------------------------------------------------- calls

def chat(model_id, prompt, system, max_tokens, temperature, timeout):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model_id,
        "messages": messages,
        "max_tokens": max_tokens,
        "usage": {"include": True},
    }
    if temperature is not None:
        payload["temperature"] = temperature
    t0 = time.time()
    data = request("POST", "/chat/completions", payload, timeout=timeout)
    if "error" in data:
        raise ApiError(_explain(data["error"].get("code", "?"), json.dumps(data)))
    choices = data.get("choices") or []
    if not choices:
        raise ApiError("OpenRouter returned no choices: %s" % json.dumps(data)[:400])
    msg = choices[0].get("message", {})
    return {
        "model_used": data.get("model", model_id),
        "provider": data.get("provider"),
        "content": msg.get("content") or "",
        "finish_reason": choices[0].get("finish_reason"),
        "usage": data.get("usage", {}),
        "seconds": round(time.time() - t0, 1),
    }


def render(label_model, result, how):
    u = result["usage"] or {}
    cost = u.get("cost")
    lines = [
        "=" * 72,
        "OpenRouter response | %s" % summary_line(label_model),
        "Resolved via: %s | served model: %s | provider: %s" % (how, result["model_used"], result["provider"] or "?"),
        "Tokens: %s in / %s out | cost: %s | %ss | finish: %s" % (
            u.get("prompt_tokens", "?"), u.get("completion_tokens", "?"),
            ("$%.6f" % cost) if isinstance(cost, (int, float)) else "n/a",
            result["seconds"], result["finish_reason"]),
        "-" * 72,
        result["content"].strip() or "(empty response)",
        "=" * 72,
    ]
    if result["finish_reason"] == "length":
        lines.append("NOTE: response was cut off by --max-tokens.")
    return "\n".join(lines)


def read_prompt(args):
    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as f:
            text = f.read()
    elif args.prompt:
        text = args.prompt
    else:
        text = sys.stdin.read()
    if not text.strip():
        raise SystemExit("Empty prompt.")
    if len(text) > args.max_prompt_chars and not args.allow_large:
        print("BLOCKED: prompt is %d chars (limit %d). Trim the context, or re-run with --allow-large "
              "after the user agrees." % (len(text), args.max_prompt_chars), file=sys.stderr)
        sys.exit(3)
    hits = scan_sensitive(text)
    if hits and not args.confirmed_sensitive:
        print("BLOCKED: possible secrets/sensitive values in the prompt:\n  " + "\n  ".join(hits) +
              "\nRemove them, or re-run with --confirmed-sensitive only after the user explicitly agrees.",
              file=sys.stderr)
        sys.exit(3)
    return text


# ------------------------------------------------------------------------- CLI

def cmd_key(_args):
    d = request("GET", "/key", timeout=30).get("data", {})
    out = {k: d.get(k) for k in ("limit", "limit_remaining", "usage", "usage_daily", "usage_monthly", "is_free_tier")}
    print("OpenRouter connection OK (credential injected by proxy%s)." %
          (" / OPENROUTER_API_KEY" if os.environ.get("OPENROUTER_API_KEY") else ""))
    print(json.dumps(out, indent=2))


def cmd_models(args):
    models = load_models(refresh=args.refresh)
    if args.search:
        s = args.search.lower()
        models = [m for m in models if s in m["id"].lower() or s in (m.get("name") or "").lower()]
    models = sorted(models, key=lambda m: m.get("created", 0), reverse=True)[: args.limit]
    for m in models:
        print(summary_line(m))
    print("(%d shown; prices are per 1M tokens, live from OpenRouter)" % len(models))


def cmd_resolve(args):
    try:
        r = resolve(args.name, load_models(refresh=args.refresh))
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    s = model_summary(r["model"])
    s.update({"resolved_via": r["how"], "alternatives": r["alternatives"]})
    print(json.dumps(s, indent=2))


def cmd_aliases(args):
    models = load_models(refresh=args.refresh)
    for name, rule in sorted(load_aliases().items()):
        try:
            r = resolve(name, models)
            print("%-14s -> %s" % (name, summary_line(r["model"])))
        except ValueError as e:
            print("%-14s -> (unavailable: %s)" % (name, str(e).splitlines()[0]))
        if args.verbose and rule.get("note"):
            print("%-14s    %s" % ("", rule["note"]))


def _ask_one(name, prompt, args, models):
    r = resolve(name, models)
    res = chat(r["model"]["id"], prompt, args.system, args.max_tokens, args.temperature, args.timeout)
    return render(r["model"], res, r["how"])


def cmd_ask(args):
    prompt = read_prompt(args)
    try:
        print(_ask_one(args.model, prompt, args, load_models()))
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def cmd_compare(args):
    names = [n.strip() for n in args.models.split(",") if n.strip()]
    if len(names) != 2:
        raise SystemExit("compare needs exactly two models, e.g. deepseek,gemini")
    prompt = read_prompt(args)
    models = load_models()
    try:
        resolved = [resolve(n, models) for n in names]
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    if resolved[0]["model"]["id"] == resolved[1]["model"]["id"]:
        raise SystemExit("Both names resolved to the same model; pick two different models.")
    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        futs = [ex.submit(chat, r["model"]["id"], prompt, args.system, args.max_tokens,
                          args.temperature, args.timeout) for r in resolved]
        for label, r, f in zip("AB", resolved, futs):
            print("\n### Model %s" % label)
            try:
                print(render(r["model"], f.result(), r["how"]))
            except ApiError as e:
                failures += 1
                print("Model %s (%s) FAILED:\n%s" % (label, r["model"]["id"], e))
    sys.exit(2 if failures == 2 else 0)


def main():
    p = argparse.ArgumentParser(description="OpenRouter client for the /openrouter skill")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("key")
    m = sub.add_parser("models")
    m.add_argument("--search")
    m.add_argument("--limit", type=int, default=40)
    m.add_argument("--refresh", action="store_true")
    r = sub.add_parser("resolve")
    r.add_argument("name")
    r.add_argument("--refresh", action="store_true")
    a = sub.add_parser("aliases")
    a.add_argument("--verbose", "-v", action="store_true")
    a.add_argument("--refresh", action="store_true")

    for name, target in (("ask", "model"), ("compare", "models")):
        s = sub.add_parser(name)
        s.add_argument(target)
        s.add_argument("--prompt-file")
        s.add_argument("--prompt")
        s.add_argument("--system", default=(
            "You are a senior software engineer consulted for a second opinion by another AI coding "
            "assistant (Claude). Be concrete and concise. Point to specific lines or functions, say how "
            "confident you are, and flag anything you cannot judge from the context given."))
        s.add_argument("--max-tokens", type=int, default=2000)
        s.add_argument("--temperature", type=float, default=None)
        s.add_argument("--timeout", type=int, default=180)
        s.add_argument("--max-prompt-chars", type=int, default=DEFAULT_MAX_PROMPT_CHARS)
        s.add_argument("--allow-large", action="store_true")
        s.add_argument("--confirmed-sensitive", action="store_true")

    args = p.parse_args()
    handler = {"key": cmd_key, "models": cmd_models, "resolve": cmd_resolve, "aliases": cmd_aliases,
               "ask": cmd_ask, "compare": cmd_compare}[args.cmd]
    try:
        handler(args)
    except ApiError as e:
        print("OpenRouter error: %s" % e, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
