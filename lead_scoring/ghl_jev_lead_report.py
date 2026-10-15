#!/usr/bin/env python3
"""
GHL newest-leads -> Jev (OpenRouter) scoring -> Top 100 call list report.

Pipeline
  1. Pull the N newest contacts from GoHighLevel (POST /contacts/search, dateAdded desc).
  2. Pull every WON opportunity and drop contacts with a win in the last 90 days.
  3. Enrich each remaining lead with activity signals (conversations, appointments,
     open opportunities, tags, custom fields, attribution).
  4. Compute a deterministic "signal score" so Jev starts from facts, not vibes.
  5. Send leads to Jev in batches (no email/phone sent) for activity level + 0-100 score.
  6. Send the Top 100 back to Jev for personalisation ideas, plus one pass for
     "propensity to book" data-point recommendations from the aggregate stats.
  7. Write leads_scored.csv, top100.csv and report.html to --out.

Usage
  GHL_API_KEY=... python3 ghl_jev_lead_report.py --limit 1000 --out ./out
  (or --ghl-config path/to/.ghl_config.json with {"api_key": ..., "location_id": ...})

Needs network access to services.leadconnectorhq.com and openrouter.ai.
"""
import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

GHL = "https://services.leadconnectorhq.com"
DEFAULT_LOCATION = "F0BBx1rOTRGj2zzaBvqY"
TRIP_CHAT_CALENDAR = "2bjXinaFCiriasCKvi0E"
EMAIL_PREF_FORM = "pvAALgrXT6xL6aLmvPhD"
JEV = "typesafe/jev-router"
WON_LOOKBACK_DAYS = 90
LEVELS = ["Hot", "Warm", "Engaged", "Cool", "Dormant"]

NOW = dt.datetime.now(dt.timezone.utc)


# ------------------------------------------------------------------ OpenRouter

def _load_openrouter():
    """Reuse the /openrouter skill client (proxy-injected auth, retries, secret scan)."""
    candidates = [os.environ.get("OPENROUTER_SCRIPT_DIR", "")]
    candidates += [os.path.join(d, "openrouter", "scripts")
                   for d in sorted(__import__("glob").glob("/root/.claude/skills/synced/*"))]
    candidates += [os.path.expanduser("~/.claude/skills/openrouter/scripts")]
    for c in candidates:
        if c and os.path.exists(os.path.join(c, "openrouter.py")):
            sys.path.insert(0, c)
            import openrouter  # noqa
            return openrouter
    sys.exit("openrouter skill script not found; set OPENROUTER_SCRIPT_DIR")


OR = None
COST = {"usd": 0.0, "calls": 0}


def jev(prompt, system, max_tokens=8000, timeout=300):
    for attempt in range(2):
        try:
            r = OR.chat(JEV, prompt, system, max_tokens, 0.2, timeout)
            u = r.get("usage") or {}
            if isinstance(u.get("cost"), (int, float)):
                COST["usd"] += u["cost"]
            COST["calls"] += 1
            return r["content"]
        except OR.ApiError as e:
            if attempt:
                raise
            print("  Jev error, retrying once:", str(e)[:200], file=sys.stderr)
            time.sleep(5)


def parse_json(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1)
    start = min([i for i in (text.find("["), text.find("{")) if i >= 0], default=0)
    return json.loads(text[start:])


# ------------------------------------------------------------------ GHL client

class GHLClient:
    def __init__(self, key, location):
        self.key, self.loc = key, location

    def call(self, method, path, params=None, body=None, version="2021-07-28"):
        url = GHL + path + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
        data = json.dumps(body).encode() if body is not None else None
        for attempt in range(5):
            req = urllib.request.Request(url, data=data, method=method, headers={
                "Authorization": "Bearer " + self.key, "Version": version,
                "Accept": "application/json", "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    return json.loads(r.read() or b"{}")
            except urllib.error.HTTPError as e:
                if e.code == 429 or e.code >= 500:
                    time.sleep(2 ** attempt)
                    continue
                if e.code == 404:
                    return {}
                raise RuntimeError("GHL %s %s -> %s %s" % (method, path, e.code, e.read()[:300]))
            except OSError:
                time.sleep(2 ** attempt)
        raise RuntimeError("GHL %s %s failed after retries" % (method, path))

    def newest_contacts(self, limit):
        out, search_after = [], None
        while len(out) < limit:
            body = {"locationId": self.loc, "pageLimit": min(100, limit - len(out)),
                    "sort": [{"field": "dateAdded", "direction": "desc"}]}
            if search_after:
                body["searchAfter"] = search_after
            d = self.call("POST", "/contacts/search", body=body)
            batch = d.get("contacts") or []
            if not batch:
                break
            out += batch
            search_after = batch[-1].get("searchAfter")
            if not search_after:
                break
            print("  contacts: %d" % len(out), file=sys.stderr)
        return out[:limit]

    def opportunities(self, status):
        out, page = [], 1
        while True:
            d = self.call("GET", "/opportunities/search",
                          {"location_id": self.loc, "status": status, "limit": 100, "page": page})
            batch = d.get("opportunities") or []
            out += batch
            if len(batch) < 100 or page > 500:
                return out
            page += 1

    def custom_field_names(self):
        d = self.call("GET", "/locations/%s/customFields" % self.loc)
        return {f["id"]: f.get("name", f["id"]) for f in d.get("customFields", [])}

    def conversation(self, cid):
        d = self.call("GET", "/conversations/search", {"locationId": self.loc, "contactId": cid, "limit": 5})
        return d.get("conversations") or []

    def appointments(self, cid):
        return self.call("GET", "/contacts/%s/appointments" % cid).get("events") or []

    def notes(self, cid):
        return self.call("GET", "/contacts/%s/notes" % cid).get("notes") or []


# ------------------------------------------------------------------ helpers

def ts(v):
    """GHL returns ISO strings or epoch ms. Return aware datetime or None."""
    if v in (None, "", 0):
        return None
    try:
        if isinstance(v, (int, float)) or str(v).isdigit():
            return dt.datetime.fromtimestamp(int(v) / 1000, dt.timezone.utc)
        return dt.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None


def days_ago(d):
    return None if d is None else max(0, (NOW - d).days)


def channel(c):
    a, l = c.get("attributionSource") or {}, c.get("lastAttributionSource") or {}
    sess = (a.get("sessionSource") or l.get("sessionSource") or "").lower()
    src = (a.get("utmSource") or l.get("utmSource") or a.get("source") or l.get("source") or "").lower()
    med = (a.get("utmMedium") or l.get("utmMedium") or a.get("medium") or l.get("medium") or "").lower()
    if a.get("gclid") or l.get("gclid") or "paid search" in sess or "google" in src or "cpc" in med:
        return "PPC - Google"
    if a.get("msclkid") or l.get("msclkid") or "bing" in src:
        return "PPC - Bing"
    if "paid social" in sess or "social media" in sess or "facebook" in src or "fb" in src or "instagram" in med:
        return "Meta - Paid Social"
    if "organic" in sess:
        return "Organic Search"
    return "Direct traffic/Referral"


# ------------------------------------------------------------------ enrichment + signal score

def enrich(client, c, cf_names, open_opps, won_before):
    cid = c["id"]
    convs, appts, notes = client.conversation(cid), client.appointments(cid), client.notes(cid)
    last_in = max([ts(x.get("lastMessageDate")) for x in convs
                   if (x.get("lastMessageDirection") or "").lower() == "inbound"] or [None],
                  key=lambda d: d or dt.datetime.min.replace(tzinfo=dt.timezone.utc))
    last_msg = max([ts(x.get("lastMessageDate")) for x in convs] or [None],
                   key=lambda d: d or dt.datetime.min.replace(tzinfo=dt.timezone.utc))
    trip_chats = [a for a in appts if a.get("calendarId") == TRIP_CHAT_CALENDAR]
    upcoming = [a for a in appts if (ts(a.get("startTime")) or NOW) > NOW]
    custom = {}
    for f in c.get("customFields") or c.get("customField") or []:
        v = f.get("value") if isinstance(f, dict) else None
        if v not in (None, "", []):
            custom[cf_names.get(f.get("id"), f.get("id"))] = v if not isinstance(v, str) else v[:120]
    opps = open_opps.get(cid, [])
    return {
        "id": cid,
        "first_name": (c.get("firstName") or "").strip().title(),
        "last_name": (c.get("lastName") or "").strip().title(),
        "email": c.get("email") or "",
        "phone": c.get("phone") or "",
        "country": c.get("country") or "",
        "city": c.get("city") or "",
        "source": c.get("source") or "",
        "channel": channel(c),
        "tags": c.get("tags") or [],
        "custom": custom,
        "days_since_added": days_ago(ts(c.get("dateAdded"))),
        "days_since_updated": days_ago(ts(c.get("dateUpdated"))),
        "days_since_last_activity": days_ago(ts(c.get("lastActivity"))),
        "days_since_last_inbound_msg": days_ago(last_in),
        "days_since_last_msg": days_ago(last_msg),
        "conversation_channels": sorted({(x.get("lastMessageType") or "").replace("TYPE_", "") for x in convs} - {""}),
        "unread_inbound": sum(int(x.get("unreadCount") or 0) for x in convs),
        "trip_chats_booked": len(trip_chats),
        "upcoming_appointments": len(upcoming),
        "no_show_or_cancelled": sum(1 for a in appts if (a.get("appointmentStatus") or "").lower()
                                    in ("noshow", "cancelled", "no_show")),
        "open_opportunities": [{"name": o.get("name"), "stage": o.get("pipelineStageName") or o.get("pipelineStageId"),
                                "value": o.get("monetaryValue")} for o in opps],
        "previous_customer_older_than_90d": cid in won_before,
        "dnd": bool(c.get("dnd")),
        "notes": [re.sub(r"\s+", " ", (n.get("body") or ""))[:200] for n in notes[:3]],
    }


INTENT_TAG = re.compile(r"brochure|enquir|quote|deposit|trip.?chat|webinar|registered|plan builder|couchto|"
                        r"saveaspace|interest|booking|abandon|checkout|price|dates", re.I)
NEGATIVE_TAG = re.compile(r"unsub|bounce|spam|not.?interested|dnd|lost|competition|outdoorexpoentry", re.I)


def signal_score(l):
    """Transparent 0-100 heuristic. Jev uses it as a starting point, not the answer."""
    s = 0
    s += 25 if l["upcoming_appointments"] else 0
    s += min(15, 8 * l["trip_chats_booked"])
    s += max([o.get("stage_weight", 15) for o in l["open_opportunities"]] or [0])
    h = l.get("hours_active_after_signup")
    s += 0 if h is None else 8 if h > 24 else 4 if h > 1 else 0
    s += 5 if len(l.get("guides") or []) > 1 else 0
    s += 10 if l["previous_customer_older_than_90d"] else 0
    d = l["days_since_last_inbound_msg"]
    s += 0 if d is None else 20 if d <= 7 else 14 if d <= 30 else 7 if d <= 90 else 0
    d = l["days_since_last_activity"]
    s += 0 if d is None else 10 if d <= 7 else 6 if d <= 30 else 2 if d <= 90 else 0
    s += min(10, 3 * sum(1 for t in l["tags"] if INTENT_TAG.search(t)))
    s += 5 if l["unread_inbound"] else 0
    h = l.get("hours_since_added")
    s += 0 if h is None else 8 if h <= 48 else 4 if h <= 96 else 0
    s += 6 if any("plan builder" in k.lower() or "readiness" in k.lower() for k in l["custom"]) else 0
    s += 3 if l["phone"] else 0
    s -= 8 * sum(1 for t in l["tags"] if NEGATIVE_TAG.search(t))
    s -= 5 * l["no_show_or_cancelled"]
    s -= 40 if l["dnd"] else 0
    return max(0, min(100, s))


def for_llm(l):
    """Strip direct identifiers before sending to Jev."""
    keep = {k: v for k, v in l.items() if k not in ("email", "phone", "last_name")}
    keep["has_phone"] = bool(l["phone"])
    keep["has_email"] = bool(l["email"])
    return keep


# ------------------------------------------------------------------ Jev passes

SYSTEM = ("You are a senior sales analyst for EverTrek, a UK adventure travel company selling guided treks "
          "(Everest Base Camp, Kilimanjaro, Machu Picchu, etc.). You score CRM leads on how likely they are "
          "to book a trip soon. Be evidence-based: only cite signals present in the data. Reply with JSON only.")

SCORE_PROMPT = """Score each lead below. For each, return:
  id, activity_level (one of: Hot, Warm, Engaged, Cool, Dormant), score (0-100 propensity to book in next 60 days),
  key_signals (max 3 short phrases citing the data), recommended_action (one short phrase).

Activity level guide (most leads are only days old, so judge depth of engagement, not just recency):
  Hot = booking-adjacent action: save-a-space, trip enquiry, upcoming trip chat, qualified/high-potential sales
        stage, or Plan Builder answers showing near-term travel timing / ready to book.
  Warm = engagement beyond the free guide: Plan Builder completed, webinar or Couch-to registration, website
        form submission, several different guides, a manual follow-up stage, or real activity after sign-up.
  Engaged = one guide plus some activity after sign-up (hours_active_after_signup > 1).
  Cool = one guide download and nothing since.
  Dormant = unsubscribed, DND, no usable contact details, or clearly not a fit.
Use the full 0-100 range: a single guide download with nothing else is about 15-30.
signal_score is a heuristic 0-100 computed from the same data; adjust it with judgement.

Return a JSON array, one object per lead, same order. Leads:
{leads}"""

PERSONALISE_PROMPT = """These are the top leads to contact this week. For each, return:
  id, opener (one natural first line a sales rep could say or write, using real details from the data),
  personalisation_ideas (2-3 specific ideas: trip to mention, timing hook, objection to pre-empt, channel to use),
  best_channel (Call, WhatsApp/SMS, Email), urgency (Today, This week, Next week).
Do not invent facts that are not in the data. Return a JSON array. Leads:
{leads}"""

INSIGHT_PROMPT = """Below are aggregate statistics from {n} recently added EverTrek CRM leads (won-in-last-90-days excluded),
showing how often each signal appears overall vs in the Hot/Warm group, and the data fields that are
available vs mostly empty.

{stats}

Return JSON: {{"propensity_signals": [{{"signal": ..., "why_it_matters": ..., "how_to_use": ...}}] (6-10 items, ranked),
"data_gaps": [{{"field_or_event": ..., "why_capture_it": ..., "how_to_capture_in_ghl": ...}}] (4-8 items),
"segments": [{{"name": ..., "definition": ..., "play": ...}}] (3-5 items)}}"""


def score_batches(leads, batch_size, workers):
    batches = [leads[i:i + batch_size] for i in range(0, len(leads), batch_size)]
    results = {}

    def run(b):
        payload = json.dumps([for_llm(l) | {"signal_score": l["signal_score"]} for l in b], default=str)
        return jev(SCORE_PROMPT.format(leads=payload), SYSTEM, max_tokens=12000)

    with cf.ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(run, b): b for b in batches}
        for i, f in enumerate(cf.as_completed(futs), 1):
            b = futs[f]
            try:
                for r in parse_json(f.result()):
                    results[r.get("id")] = r
            except Exception as e:  # keep going; unscored leads fall back to signal score
                print("  batch failed (%d leads): %s" % (len(b), str(e)[:200]), file=sys.stderr)
            print("  Jev scoring batch %d/%d" % (i, len(batches)), file=sys.stderr)
    return results


def personalise(top, workers):
    batches = [top[i:i + 20] for i in range(0, len(top), 20)]
    out = {}
    with cf.ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(jev, PERSONALISE_PROMPT.format(
            leads=json.dumps([for_llm(l) | {"jev": l.get("jev")} for l in b], default=str)), SYSTEM, 12000)
            for b in batches]
        for f in futs:
            try:
                for r in parse_json(f.result()):
                    out[r.get("id")] = r
            except Exception as e:
                print("  personalisation batch failed: %s" % str(e)[:200], file=sys.stderr)
    return out


def aggregate_stats(leads):
    hot = [l for l in leads if l["activity_level"] in ("Hot", "Warm")]

    def pct(group, fn):
        return round(100 * sum(1 for l in group if fn(l)) / len(group), 1) if group else 0

    signals = {
        "upcoming appointment": lambda l: l["upcoming_appointments"] > 0,
        "trip chat booked ever": lambda l: l["trip_chats_booked"] > 0,
        "open opportunity": lambda l: bool(l["open_opportunities"]),
        "inbound message <30d": lambda l: (l["days_since_last_inbound_msg"] or 999) <= 30,
        "activity <7d": lambda l: (l["days_since_last_activity"] or 999) <= 7,
        "previous customer (>90d)": lambda l: l["previous_customer_older_than_90d"],
        "has phone": lambda l: bool(l["phone"]),
        "intent tag": lambda l: any(INTENT_TAG.search(t) for t in l["tags"]),
        "no-show/cancelled appt": lambda l: l["no_show_or_cancelled"] > 0,
    }
    for ch in sorted({l["channel"] for l in leads}):
        signals["channel = " + ch] = (lambda c: lambda l: l["channel"] == c)(ch)
    tag_counts = {}
    for l in leads:
        for t in l["tags"]:
            tag_counts[t] = tag_counts.get(t, 0) + 1
    cf_fill = {}
    for l in leads:
        for k in l["custom"]:
            cf_fill[k] = cf_fill.get(k, 0) + 1
    return {
        "total": len(leads), "hot_warm": len(hot),
        "signal_rates_pct": {k: {"all": pct(leads, f), "hot_warm": pct(hot, f)} for k, f in signals.items()},
        "top_tags": sorted(tag_counts.items(), key=lambda x: -x[1])[:40],
        "custom_field_fill_pct": {k: round(100 * v / len(leads), 1) for k, v in
                                  sorted(cf_fill.items(), key=lambda x: -x[1])[:40]},
    }


# ------------------------------------------------------------------ output

def write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in r.items()})


def write_html(path, leads, top, insights, stats, meta):
    e = lambda s: html.escape(str(s if s is not None else ""))
    counts = {lv: sum(1 for l in leads if l["activity_level"] == lv) for lv in LEVELS}
    rows = []
    for i, l in enumerate(top, 1):
        p = l.get("personalisation") or {}
        ideas = "".join("<li>%s</li>" % e(x) for x in p.get("personalisation_ideas", []))
        sig = "".join("<li>%s</li>" % e(x) for x in (l.get("jev") or {}).get("key_signals", []))
        rows.append(f"""<tr><td>{i}</td><td><b>{e(l['first_name'])} {e(l['last_name'])}</b><br>
<span class=m>{e(l['email'])}<br>{e(l['phone'])}</span></td>
<td><span class="lv {e(l['activity_level'])}">{e(l['activity_level'])}</span><br><b>{e(l['final_score'])}</b></td>
<td><ul>{sig}</ul></td><td><i>{e(p.get('opener'))}</i><ul>{ideas}</ul></td>
<td>{e(p.get('best_channel'))}<br><span class=m>{e(p.get('urgency'))}</span></td></tr>""")

    def ul(items, keys):
        return "".join("<li><b>%s</b> %s</li>" % (e(it.get(keys[0])), " · ".join(e(it.get(k)) for k in keys[1:]))
                       for it in items)
    level_cards = "".join(f"<div class=card><div class=n>{counts[lv]}</div><span class='lv {lv}'>{lv}</span></div>"
                          for lv in LEVELS)
    sig_rows = "".join(f"<tr><td>{e(k)}</td><td>{v['all']}%</td><td>{v['hot_warm']}%</td></tr>"
                       for k, v in stats["signal_rates_pct"].items())
    doc = f"""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Top 100 Leads</title><style>
:root{{--bg:#fff;--fg:#1a1a1a;--mut:#666;--bd:#e3e3e3;--card:#f7f7f5}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151515;--fg:#eee;--mut:#aaa;--bd:#333;--card:#1f1f1f}}}}
body{{background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif;margin:0 auto;max-width:1200px;padding:24px 16px}}
h1{{margin:0 0 4px}}.m{{color:var(--mut);font-size:12px}}table{{border-collapse:collapse;width:100%}}
td,th{{border-bottom:1px solid var(--bd);padding:8px;vertical-align:top;text-align:left}}ul{{margin:4px 0;padding-left:18px}}
.cards{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}}.card{{background:var(--card);border-radius:8px;padding:12px 16px;min-width:110px}}
.n{{font-size:26px;font-weight:700}}.lv{{border-radius:10px;padding:1px 8px;font-size:12px;color:#fff}}
.Hot{{background:#c0392b}}.Warm{{background:#e67e22}}.Engaged{{background:#2e86c1}}.Cool{{background:#7f8c8d}}.Dormant{{background:#444}}
.wrap{{overflow-x:auto}}</style>
<h1>Top 100 Leads to Contact</h1>
<div class=m>{e(meta['generated'])} · {meta['pulled']} newest GHL contacts · {meta['excluded_won']} excluded (won opp in last 90 days) ·
{meta['scored']} scored by Jev ({e(JEV)}) · Jev cost ${meta['cost']:.2f}</div>
<div class=cards>{level_cards}</div>
<h2>Top 100</h2><div class=wrap><table><tr><th>#</th><th>Lead</th><th>Level / score</th><th>Why</th><th>Personalisation</th><th>Channel</th></tr>
{''.join(rows)}</table></div>
<h2>Signals that predict booking</h2><ul>{ul(insights.get('propensity_signals', []), ['signal', 'why_it_matters', 'how_to_use'])}</ul>
<h2>Data worth capturing</h2><ul>{ul(insights.get('data_gaps', []), ['field_or_event', 'why_capture_it', 'how_to_capture_in_ghl'])}</ul>
<h2>Segments and plays</h2><ul>{ul(insights.get('segments', []), ['name', 'definition', 'play'])}</ul>
<h2>Signal rates</h2><div class=wrap><table><tr><th>Signal</th><th>All leads</th><th>Hot + Warm</th></tr>{sig_rows}</table></div>
<p class=m>Scores combine a transparent signal score (appointments, opportunities, recent inbound messages, activity recency,
intent tags) with Jev's judgement. Email and phone were not sent to Jev.</p></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


# ------------------------------------------------------------------ main

def main():
    global OR
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=1000)
    ap.add_argument("--top", type=int, default=100)
    ap.add_argument("--batch", type=int, default=40)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--ghl-config")
    ap.add_argument("--location", default=os.environ.get("GHL_LOCATION_ID", DEFAULT_LOCATION))
    ap.add_argument("--out", default="out")
    a = ap.parse_args()

    key = os.environ.get("GHL_API_KEY", "")
    if a.ghl_config:
        cfg = json.load(open(a.ghl_config))
        key, a.location = cfg.get("api_key", key), cfg.get("location_id", a.location)
    if not key:
        sys.exit("Set GHL_API_KEY or pass --ghl-config")
    OR = _load_openrouter()
    os.makedirs(a.out, exist_ok=True)
    client = GHLClient(key, a.location)

    print("1/6 Pulling newest contacts...", file=sys.stderr)
    contacts = client.newest_contacts(a.limit)

    print("2/6 Pulling opportunities...", file=sys.stderr)
    cutoff = NOW - dt.timedelta(days=WON_LOOKBACK_DAYS)
    won_recent, won_before = set(), set()
    for o in client.opportunities("won"):
        cid = o.get("contactId") or (o.get("contact") or {}).get("id")
        when = ts(o.get("lastStatusChangeAt")) or ts(o.get("updatedAt")) or ts(o.get("createdAt"))
        (won_recent if when and when >= cutoff else won_before).add(cid)
    open_opps = {}
    for o in client.opportunities("open"):
        cid = o.get("contactId") or (o.get("contact") or {}).get("id")
        open_opps.setdefault(cid, []).append(o)
    eligible = [c for c in contacts if c["id"] not in won_recent]
    excluded = len(contacts) - len(eligible)
    cf_names = client.custom_field_names()

    print("3/6 Enriching %d leads with activity..." % len(eligible), file=sys.stderr)
    leads = []
    with cf.ThreadPoolExecutor(8) as ex:
        for i, l in enumerate(ex.map(lambda c: enrich(client, c, cf_names, open_opps, won_before), eligible), 1):
            l["signal_score"] = signal_score(l)
            leads.append(l)
            if i % 100 == 0:
                print("  enriched %d" % i, file=sys.stderr)
    json.dump(leads, open(os.path.join(a.out, "leads_enriched.json"), "w"), default=str)

    print("4/6 Jev scoring...", file=sys.stderr)
    scored = score_batches(leads, a.batch, a.workers)
    for l in leads:
        j = scored.get(l["id"]) or {}
        l["jev"] = j
        l["activity_level"] = j.get("activity_level") if j.get("activity_level") in LEVELS else (
            "Hot" if l["signal_score"] >= 60 else "Warm" if l["signal_score"] >= 40 else
            "Engaged" if l["signal_score"] >= 20 else "Cool" if l["signal_score"] >= 8 else "Dormant")
        jscore = j.get("score")
        l["jev_score"] = jscore if isinstance(jscore, (int, float)) else None
        # Blend: Jev judgement 60%, deterministic signals 40%.
        l["final_score"] = round(0.6 * l["jev_score"] + 0.4 * l["signal_score"]) if l["jev_score"] is not None \
            else l["signal_score"]
    contactable = [l for l in leads if not l["dnd"] and (l["phone"] or l["email"])]
    top = sorted(contactable, key=lambda l: (-l["final_score"], l["days_since_last_activity"] or 999))[:a.top]

    print("5/6 Jev personalisation for top %d..." % len(top), file=sys.stderr)
    pers = personalise(top, a.workers)
    for l in top:
        l["personalisation"] = pers.get(l["id"]) or {}

    print("6/6 Propensity insights...", file=sys.stderr)
    stats = aggregate_stats(leads)
    try:
        insights = parse_json(jev(INSIGHT_PROMPT.format(n=len(leads), stats=json.dumps(stats)), SYSTEM, 6000))
    except Exception as e:
        print("  insight pass failed: %s" % e, file=sys.stderr)
        insights = {}

    cols = ["id", "first_name", "last_name", "email", "phone", "country", "channel", "activity_level",
            "final_score", "jev_score", "signal_score", "days_since_added", "days_since_last_activity",
            "days_since_last_inbound_msg", "trip_chats_booked", "upcoming_appointments", "open_opportunities", "tags"]
    write_csv(os.path.join(a.out, "leads_scored.csv"),
              [l | {"jev_signals": (l["jev"] or {}).get("key_signals")} for l in
               sorted(leads, key=lambda l: -l["final_score"])], cols + ["jev_signals"])
    write_csv(os.path.join(a.out, "top100.csv"),
              [l | {"opener": l["personalisation"].get("opener"),
                    "ideas": l["personalisation"].get("personalisation_ideas"),
                    "best_channel": l["personalisation"].get("best_channel"),
                    "urgency": l["personalisation"].get("urgency"),
                    "jev_signals": (l["jev"] or {}).get("key_signals")} for l in top],
              cols + ["jev_signals", "opener", "ideas", "best_channel", "urgency"])
    json.dump({"stats": stats, "insights": insights}, open(os.path.join(a.out, "insights.json"), "w"), indent=2)
    meta = {"generated": NOW.strftime("%d %b %Y %H:%M UTC"), "pulled": len(contacts), "excluded_won": excluded,
            "scored": len(scored), "cost": COST["usd"]}
    write_html(os.path.join(a.out, "report.html"), leads, top, insights, stats, meta)
    print(json.dumps(meta | {"jev_calls": COST["calls"],
                             "levels": {lv: sum(1 for l in leads if l["activity_level"] == lv) for lv in LEVELS}}))


if __name__ == "__main__":
    main()
