#!/usr/bin/env python3
"""
Score leads from a GHL export (JSON slices pulled via the GHL MCP connector) instead of calling the
GHL API directly. Reuses the Jev scoring, personalisation and report code in ghl_jev_lead_report.py.

  python3 score_from_export.py --raw <dir with slice_*.json, custom_fields.json, stages.json> \
      --limit 1000 --out <dir>

Optional --activity <file>: JSON {contactId: {days_since_last_inbound_msg, days_since_last_msg,
conversation_channels, unread_inbound, trip_chats_booked, upcoming_appointments, no_show_or_cancelled,
notes}} merged in before the personalisation pass (used for the top ~150 only).
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ghl_jev_lead_report as g  # noqa: E402

# Custom fields that only describe email subscription preferences: no buying signal, drop them.
SUBSCRIPTION_VALUES = {"Tuesday Tune-In Updates", "Giveaways & Competition Emails", "EverTrek Community Newsletter",
                       "Trip Announcements & Dates", "Special Promotions & Trip Offers"}


def load(raw):
    contacts = []
    for f in sorted(glob.glob(os.path.join(raw, "slice_*.json"))):
        contacts += json.load(open(f))
    seen, out = set(), []
    for c in sorted(contacts, key=lambda c: c.get("dateAdded") or "", reverse=True):
        if c["id"] not in seen:
            seen.add(c["id"])
            out.append(c)
    cf = json.load(open(os.path.join(raw, "custom_fields.json"))) if os.path.exists(
        os.path.join(raw, "custom_fields.json")) else {}
    stages = json.load(open(os.path.join(raw, "stages.json"))) if os.path.exists(
        os.path.join(raw, "stages.json")) else {}
    return out, cf, stages


RECENT_BOOKING_TAG = re.compile(r"purchased|postbooking|trekbooking$|new booking", re.I)


def stage_weight(name):
    n = name.lower()
    return 25 if "high potential" in n else 18 if "qualified" in n else 12 if "follow up" in n else 6


def to_lead(c, cf_names, stages):
    custom = {}
    for fid, v in (c.get("customFields") or {}).items():
        if v in (None, "", []):
            continue
        if isinstance(v, list) and set(map(str, v)) <= SUBSCRIPTION_VALUES:
            continue
        meta = cf_names.get(fid)
        name = meta.get("name") if isinstance(meta, dict) else (meta or fid)
        custom[name] = v
    open_opps = []
    for o in c.get("opportunities") or []:
        if o.get("status") == "open":
            st = stages.get(o.get("pipelineStageId")) or {}
            name = st.get("stage", "")
            if name == "Unqualified Leads":  # auto-created for every new lead: not a signal
                continue
            open_opps.append({"stage": "%s / %s" % (st.get("pipeline", "?"), name or "?") if st else None,
                              "value": o.get("monetaryValue"), "stage_weight": stage_weight(name)})
    tags = list(c.get("tags") or [])
    if any("unsubscribe" in k.lower() for k in custom):
        tags.append("unsubscribed from all lists")
    att = c.get("attribution") or {}
    a = {"sessionSource": att.get("sessionSource"), "utmSource": att.get("utmSource"),
         "utmMedium": att.get("utmMedium"), "gclid": att.get("hasGclid"), "msclkid": att.get("hasMsclkid")}
    won = c.get("wonOpportunities") or []
    return {
        "id": c["id"],
        "first_name": (c.get("firstName") or "").strip().title(),
        "last_name": (c.get("lastName") or "").strip().title(),
        "email": c.get("email") or "",
        "phone": c.get("phone") or "",
        "country": c.get("country") or "",
        "city": c.get("city") or "",
        "source": c.get("source") or "",
        "channel": g.channel({"attributionSource": a}),
        "campaign": att.get("campaign"),
        "ad_content": att.get("utmContent"),
        "landing_page": att.get("url"),
        "tags": tags,
        "custom": custom,
        "days_since_added": g.days_ago(g.ts(c.get("dateAdded"))),
        "days_since_updated": g.days_ago(g.ts(c.get("dateUpdated"))),
        "days_since_last_activity": g.days_ago(g.ts(c.get("lastActivity"))),
        "hours_since_added": None if not g.ts(c.get("dateAdded")) else
        round((g.NOW - g.ts(c.get("dateAdded"))).total_seconds() / 3600, 1),
        # Filled for the top leads only (see --activity); None means "not checked", not "none".
        "days_since_last_inbound_msg": None,
        "days_since_last_msg": None,
        "conversation_channels": [],
        "unread_inbound": 0,
        "trip_chats_booked": 0,
        "upcoming_appointments": 0,
        "no_show_or_cancelled": 0,
        "notes": [],
        "open_opportunities": open_opps,
        "guides": sorted({t for t in tags if "guide" in t.lower() and "received" in t.lower()}),
        "hours_active_after_signup": None if not (g.ts(c.get("lastActivity")) and g.ts(c.get("dateAdded"))) else
        round((g.ts(c.get("lastActivity")) - g.ts(c.get("dateAdded"))).total_seconds() / 3600, 1),
        "recent_booking_tag": any(RECENT_BOOKING_TAG.search(t) for t in tags),
        "past_bookings": [w.get("tripInfo") or w.get("name") for w in won],
        "previous_customer_older_than_90d": bool(won) or any(t.lower() == "customer" for t in tags),
        "dnd": bool(c.get("dnd")) or len(c.get("dndChannelsActive") or []) >= 3,
        "dnd_channels": c.get("dndChannelsActive") or [],
        "_won": won,
    }


def won_recently(lead, cutoff):
    for w in lead["_won"]:
        when = g.ts(w.get("lastStatusChangeAt")) or g.ts(w.get("createdAt"))
        if when is None or when >= cutoff:  # unknown date: exclude to be safe
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--limit", type=int, default=1000)
    ap.add_argument("--top", type=int, default=100)
    ap.add_argument("--batch", type=int, default=40)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--activity")
    ap.add_argument("--stage", choices=["score", "finish", "all"], default="all",
                    help="score: Jev scoring only (writes scored.json); finish: merge --activity, personalise, report")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    g.OR = g._load_openrouter()
    state = os.path.join(a.out, "scored.json")

    if a.stage in ("score", "all"):
        contacts, cf, stages = load(a.raw)
        contacts = contacts[:a.limit]
        leads = [to_lead(c, cf, stages) for c in contacts]
        cutoff = g.NOW - dt.timedelta(days=g.WON_LOOKBACK_DAYS)
        eligible = [l for l in leads if not won_recently(l, cutoff)]
        n_won = len(leads) - len(eligible)
        eligible = [l for l in eligible if not l["recent_booking_tag"]]
        meta = {"pulled": len(leads), "excluded_won": n_won + (len(leads) - n_won - len(eligible)),
                "excluded_won_opp": n_won, "excluded_booking_tag": len(leads) - n_won - len(eligible),
                "oldest_added": contacts[-1].get("dateAdded") if contacts else None,
                "newest_added": contacts[0].get("dateAdded") if contacts else None}
        for l in eligible:
            l["signal_score"] = g.signal_score(l)
        print("Jev scoring %d leads..." % len(eligible), file=sys.stderr)
        scored = g.score_batches(eligible, a.batch, a.workers)
        for l in eligible:
            j = scored.get(l["id"]) or {}
            l["jev"] = j
            l["activity_level"] = j.get("activity_level") if j.get("activity_level") in g.LEVELS else (
                "Hot" if l["signal_score"] >= 60 else "Warm" if l["signal_score"] >= 40 else
                "Engaged" if l["signal_score"] >= 20 else "Cool" if l["signal_score"] >= 8 else "Dormant")
            js = j.get("score")
            l["jev_score"] = js if isinstance(js, (int, float)) else None
            l["final_score"] = round(0.6 * js + 0.4 * l["signal_score"]) if l["jev_score"] is not None \
                else l["signal_score"]
        meta["scored"] = len(scored)
        json.dump({"meta": meta, "leads": eligible, "cost": g.COST}, open(state, "w"), default=str)
        ranked = sorted([l for l in eligible if not l["dnd"] and (l["phone"] or l["email"])],
                        key=lambda l: (-l["final_score"], l["days_since_last_activity"] or 999))
        with open(os.path.join(a.out, "shortlist_ids.json"), "w") as f:
            json.dump([l["id"] for l in ranked[:int(a.top * 1.5)]], f)
        print(json.dumps(meta | {"cost": g.COST, "levels": {lv: sum(1 for l in eligible if l["activity_level"] == lv)
                                                           for lv in g.LEVELS}}))
        if a.stage == "score":
            return

    st = json.load(open(state))
    meta, leads = st["meta"], st["leads"]
    g.COST.update(st.get("cost") or {})
    if a.activity and os.path.exists(a.activity):
        act = json.load(open(a.activity))
        for l in leads:
            if l["id"] in act:
                l.update({k: v for k, v in act[l["id"]].items() if v is not None})
                old = l["signal_score"]
                l["signal_score"] = g.signal_score(l)
                if l["jev_score"] is not None:
                    l["final_score"] = round(0.6 * l["jev_score"] + 0.4 * l["signal_score"])
                else:
                    l["final_score"] += l["signal_score"] - old
    contactable = [l for l in leads if not l["dnd"] and (l["phone"] or l["email"])]
    top = sorted(contactable, key=lambda l: (-l["final_score"], l["days_since_last_activity"] or 999))[:a.top]
    print("Personalising top %d..." % len(top), file=sys.stderr)
    pers = g.personalise(top, a.workers)
    for l in top:
        l["personalisation"] = pers.get(l["id"]) or {}
    stats = g.aggregate_stats(leads)
    try:
        insights = g.parse_json(g.jev(g.INSIGHT_PROMPT.format(n=len(leads), stats=json.dumps(stats)), g.SYSTEM, 6000))
    except Exception as e:
        print("insight pass failed: %s" % e, file=sys.stderr)
        insights = {}
    cols = ["id", "first_name", "last_name", "email", "phone", "country", "channel", "campaign", "activity_level",
            "final_score", "jev_score", "signal_score", "days_since_added", "days_since_last_activity",
            "days_since_last_inbound_msg", "trip_chats_booked", "upcoming_appointments", "open_opportunities",
            "past_bookings", "tags"]
    g.write_csv(os.path.join(a.out, "leads_scored.csv"),
                [l | {"jev_signals": (l.get("jev") or {}).get("key_signals")}
                 for l in sorted(leads, key=lambda l: -l["final_score"])], cols + ["jev_signals"])
    g.write_csv(os.path.join(a.out, "top100.csv"),
                [l | {"opener": l["personalisation"].get("opener"),
                      "ideas": l["personalisation"].get("personalisation_ideas"),
                      "best_channel": l["personalisation"].get("best_channel"),
                      "urgency": l["personalisation"].get("urgency"),
                      "jev_signals": (l.get("jev") or {}).get("key_signals")} for l in top],
                cols + ["jev_signals", "opener", "ideas", "best_channel", "urgency"])
    json.dump({"stats": stats, "insights": insights, "top": top}, open(os.path.join(a.out, "insights.json"), "w"),
              indent=2, default=str)
    meta |= {"generated": g.NOW.strftime("%d %b %Y %H:%M UTC"), "cost": g.COST["usd"]}
    g.write_html(os.path.join(a.out, "report.html"), leads, top, insights, stats, meta)
    print(json.dumps(meta | {"jev_calls": g.COST["calls"]}))


if __name__ == "__main__":
    main()
