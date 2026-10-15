---
name: openrouter
description: Get a second opinion from a non-Claude model (DeepSeek, Gemini, GLM, Qwen, Kimi, Jev, GPT, Grok) via OpenRouter, or compare two models. Runs only when the user types /openrouter.
argument-hint: "[model|compare [modelA,modelB]] <task>"
disable-model-invocation: true
allowed-tools:
  - Bash(python3 *openrouter.py key*)
  - Bash(python3 *openrouter.py models*)
  - Bash(python3 *openrouter.py resolve*)
  - Bash(python3 *openrouter.py aliases*)
---

# /openrouter: second opinions from other models

Claude stays the primary assistant. It does all the project work: reading files, using tools, editing code
and running commands. OpenRouter models are **consultants** only. They get a focused prompt, Claude shows
their answer labelled with the model used, and then Claude evaluates it. Never apply an external model's
suggestions automatically. Never change Claude's own model, provider or global settings from this skill.

User arguments: `$ARGUMENTS`

Client script: `python3 ${CLAUDE_SKILL_DIR}/scripts/openrouter.py`, called `OR` below.
If `${CLAUDE_SKILL_DIR}` is not expanded, use `~/.claude/skills/openrouter/scripts/openrouter.py`,
or `<repo>/.claude/skills/openrouter/...` if the skill was installed at project scope.

## Authentication (do not change)

- In Claude cloud sessions, the agent network proxy injects the OpenRouter credential into requests to
  `openrouter.ai`. The script sends **no** Authorization header and needs no key.
- Outside the proxy, the script uses `OPENROUTER_API_KEY` if that variable is set.
- Never ask the user to paste a key. Never write a key into files. Never print headers or env values.

## Step 1: parse `$ARGUMENTS`

| Input | Action |
|---|---|
| empty or `help` | Show the **Help** screen (below). No paid calls. |
| `models [search]` | `OR models --search <search>`. Free. |
| `info <name>` | `OR resolve <name>`, then show name, provider, ID, input and output price per 1M tokens, and context window. Free. |
| `compare [a,b] <question>` | **Comparison mode** (step 5). |
| `<name> <task>` | **Single-model mode** (steps 2–4). |

`<name>` is either an alias (`deepseek`, `jev`, `gemini`, `glm`, `qwen`, `kimi`, `gpt`, `grok`, `mistral`,
`minimax`, `llama`, `codex`, `devstral`, the `-flash`/`-code` variants, `free`) or an exact OpenRouter ID such as
`deepseek/deepseek-v4-flash`. If the first word is neither an alias nor contains `/`, check it with
`OR resolve` before deciding it is part of the task.

## Step 2: resolve the model (free)

Run `OR resolve <name>`. It reads the live `/api/v1/models` list (cached for 1 hour) and returns the ID,
provider, live pricing, context window, how it resolved, and alternatives.
- Aliases pick the **newest** matching model. Always tell the user which model was selected, for example:
  "`deepseek` → DeepSeek V4 Pro (deepseek/deepseek-v4-pro-0813), $0.66/$1.98 per 1M, 1.05M context".
- If resolve exits 1 because the name is ambiguous, show the candidates and ask the user to choose. Do not
  guess between models whose prices differ a lot.
- If pricing is `variable` (routers such as Jev), say so.

## Step 3: build a minimal, safe prompt

Write the prompt to a temp file in the scratchpad or `$TMPDIR`, never inside the repo. Include:
1. The user's task, verbatim.
2. Only the context needed: the specific functions, diff hunks or error output under discussion, with
   file paths and line numbers. Use excerpts, not whole files. **Never send whole repositories.**
3. One or two lines about language, framework and constraints, if relevant.

Do **not** include `.env*` files, credentials, keys, tokens, private keys, customer data, PII, `~/.ssh`,
`~/.aws`, secrets config, or proprietary data that isn't needed. If the task truly needs something that might
be sensitive, stop and ask the user before sending, and say exactly what would be sent.

The script also guards the prompt. It exits with code **3** if it detects secret-like strings or if the prompt
is longer than 60,000 characters. When that happens, remove the material. Re-run with `--confirmed-sensitive`
or `--allow-large` only after the user explicitly agrees.

Before the first paid call in a conversation, mention once that OpenRouter calls are billed to the user's
OpenRouter credits, and give the model's price.

## Step 4: call and present (paid)

```
OR ask <name-or-id> --prompt-file <file> [--max-tokens 2000] [--timeout 180] [--system "..."]
```
Run it with a Bash timeout of at least 200000 ms. Present:

1. **The external response, verbatim**, under a heading like `### DeepSeek V4 Pro (deepseek/deepseek-v4-pro-0813)`,
   with the script's tokens/cost line.
2. **Claude's assessment**: what is correct, what is wrong or unsupported (verify claims against the actual
   code with your own tools), and what is worth acting on.
3. **Suggested next steps**: concrete actions Claude can take. Ask before making changes the user hasn't
   requested.

Errors (exit 2): explain the message the script printed and what to do:
- 401: proxy secret detached or key invalid.
- 402: no credits.
- 404/400: model gone, so re-resolve or choose another.
- 429/503: the script already retried; suggest waiting or another model.
- Timeout: shorter prompt, or a `-flash` model.

Never retry a paid call more than once without asking.

## Step 5: comparison mode (2 paid calls)

- `compare <question>`: choose two strong models from **different providers** that suit the question. The
  default is `deepseek,gemini`. For coding-heavy questions consider `kimi-code`, `qwen-coder`, `codex`, `glm`.
  Resolve both and tell the user which two were chosen and what each costs before calling.
- `compare a,b <question>`: use the two named models.
- Build one prompt file as in step 3, then run `OR compare a,b --prompt-file <file>`. Both calls run in parallel.
  If one model fails, the other is still shown.

Present:
1. **Model A**: name, ID, and its recommendation (verbatim or faithfully condensed, labelled).
2. **Model B**: the same.
3. **Comparison**: where they agree, where they disagree, and each one's strengths and weaknesses or blind spots.
4. **Claude's own assessment**: informed by the actual project code, not only the two answers.
5. **Recommended next step**: one practical action.

Never call more than two models per `compare`, and never re-run a comparison without asking.

## Help screen (for `/openrouter` with no arguments)

Run `OR aliases` and `OR key`. Both are free and show the current alias → model mapping with live prices and
the credit balance. Then show:

```
/openrouter                              this help + alias table + credit balance
/openrouter models [search]              browse models with live price/context
/openrouter info <alias|id>              details for one model
/openrouter <alias|id> <task>            ask one model (e.g. deepseek, gemini, glm, qwen, kimi, jev)
/openrouter compare [a,b] <question>     ask two models, compare, and get Claude's verdict
```

Note that requests cost OpenRouter credits, at the per-1M-token prices shown, and that Claude remains the
default model for everything else.
