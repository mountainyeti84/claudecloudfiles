# GHL → Jev lead scoring report

Pulls the newest GHL contacts, drops anyone with a **won opportunity in the last 90 days**, enriches each lead
with activity (conversations, appointments incl. Trip Chats, open opportunities, notes, tags, custom fields,
attribution), then uses **Jev** (`typesafe/jev-router` via OpenRouter) to:

1. sort leads into activity levels (Hot / Warm / Engaged / Cool / Dormant) and score them 0–100
2. write personalisation ideas and an opener for the Top 100
3. recommend the data points and activity that best predict booking a trip

Final score = 60% Jev judgement + 40% a transparent signal score. Email, phone and surname are never sent to Jev.

```bash
GHL_API_KEY=... python3 lead_scoring/ghl_jev_lead_report.py --limit 1000 --out out
# or: --ghl-config /path/to/.ghl_config.json   (scale up with --limit 20000)
```

Outputs in `--out`: `report.html`, `top100.csv`, `leads_scored.csv`, `insights.json`, `leads_enriched.json`.
Needs network access to `services.leadconnectorhq.com` and `openrouter.ai`.
