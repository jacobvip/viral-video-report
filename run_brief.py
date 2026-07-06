#!/usr/bin/env python3
# ============================================================================
#  Viral Video Report — daily pipeline orchestrator
# ----------------------------------------------------------------------------
#  The deterministic half of the daily job. It:
#    STEP 0  reads the memory DB (vvr-trends-db.json)
#    STEP 3  assembles the NEWSLETTER dict from a virlo_snapshot.json
#            (the day's editorial decisions), enforcing the 7-day dedup rule
#    STEP 3  renders the email via vvr_generator
#    STEP 4  delivers via Resend (send_email.deliver; respects BRIEF_DRY_RUN)
#    STEP 5  writes the memory DB back (new report + bumped meta)
#
#  The Virlo PULL + editorial JUDGMENT (STEP 1-2) happen upstream and land in
#  virlo_snapshot.json — done by the agentic `claude -p` run (see
#  run-brief-prompt.txt) or by hand. This module is pure/testable: same
#  snapshot + same memory => same output.
#
#  Dedup: any trend featured (as New This Week) within dedup_window_days is NOT
#  re-featured — it drops to a one-line "Still Running" item automatically.
# ============================================================================

import datetime
import json
import os

from vvr_generator import render_html

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vvr-trends-db.json")
SNAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "virlo_snapshot.json")


def _today():
    return os.environ.get("BRIEF_DATE") or datetime.date.today().isoformat()


def _days_since(date_str, today):
    a = datetime.date.fromisoformat(date_str)
    b = datetime.date.fromisoformat(today)
    return (b - a).days


def load_memory():
    if not os.path.isfile(DB_PATH):
        return {"trends": {}, "watching": [], "reports": [],
                "meta": {"last_updated": None, "report_count": 0, "dedup_window_days": 7}}
    with open(DB_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def save_memory(m):
    with open(DB_PATH, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=2, ensure_ascii=False)


def build(snapshot, memory, today):
    """Assemble the NEWSLETTER dict + return (newsletter, featured_slugs)."""
    window = memory.get("meta", {}).get("dedup_window_days", 7)
    recent = {slug: rec for slug, rec in memory.get("trends", {}).items()
              if rec.get("last_featured") and _days_since(rec["last_featured"], today) < window}

    accel_slugs = {a.get("slug") for a in snapshot.get("accelerating", []) if a.get("slug")}

    sections = []
    featured = []

    # STEP 2 dedup applied here: skip any New candidate featured within the window.
    for t in snapshot.get("new_this_week", []):
        if t["slug"] in recent:
            continue  # deduped -> falls through to Still Running below
        featured.append(t["slug"])
        sections.append({
            "type": "trend",
            "category": "New this week",
            "emoji": "\U0001F525",
            "headline": t["headline"],
            "videos": t.get("videos", []),
            "metrics": t.get("metrics", []),
            "leadLabel": "The format:",
            "lead": t["lead"],
            "detailsTitle": "Why it works:",
            "details": t.get("details", []),
            "whyLabel": "Recreate it:",
            "why": t.get("why", ""),
            "cta": t.get("cta", {"label": "Hear the sound →", "url": "#"}),
        })

    accel = snapshot.get("accelerating", [])
    if accel:
        sections.append({
            "type": "watchlist",
            "category": "Accelerating · watch list",
            "emoji": "\U0001F4C8",
            "headline": snapshot.get("accelerating_headline", "The sounds everyone's on"),
            "leadLabel": "The read:",
            "lead": snapshot.get("accelerating_lead",
                                 "Huge momentum, but no shared format yet — ride the audio, don't expect a template."),
            "watch": [{"name": a["name"], "metric": a["metric"], "note": a["note"]} for a in accel],
        })

    # Still Running = trends featured within the window that AREN'T today's New
    # or Accelerating items — i.e. yesterday's leads, demoted to one-liners.
    running = []
    for slug, rec in recent.items():
        if slug in featured or slug in accel_slugs:
            continue
        running.append({"name": rec["name"], "status": rec.get("status", "running"),
                        "url": rec.get("url", "#"), "linkLabel": "watch →"})
    if running:
        sections.append({
            "type": "stillrunning",
            "category": "Still running",
            "emoji": "\U0001F501",
            "headline": "Featured in the last 7 days",
            "running": running,
        })

    rec = snapshot.get("recreation")
    if rec:
        sections.append({
            "type": "recreation",
            "category": "Recreation template of the day",
            "emoji": "\U0001F3AC",
            "headline": rec["headline"],
            "leadLabel": "The brief:",
            "lead": rec.get("lead", "Today's New This Week lead, as a shot list."),
            "steps": rec.get("steps", []),
            "cta": rec.get("cta", {"label": "Grab the sound →", "url": "#"}),
        })

    issue_no = memory.get("meta", {}).get("report_count", 0) + 1
    d = datetime.date.fromisoformat(today)
    newsletter = {
        "meta": {
            "brandIcon": os.environ.get("VVR_BRAND_ICON", "https://raw.githubusercontent.com/jacobvip/viral-video-report/main/html-newsletter-template/project/assets/vvr-icon.png"),
            "wordmarkPre": "Viral Video ", "wordmarkAccent": "Report",
            "tagline": "Your daily short-form video trend brief — what's new, what's accelerating, what to copy.",
            "issueLine": f"{d:%A} · {d:%B} {d.day}, {d.year} · Issue {issue_no:03d}",
            "banner": None,
            "headerLinks": [{"label": "Read online", "url": "#"},
                            {"label": "Subscribe", "url": "#"},
                            {"label": "Archive", "url": "#"}],
        },
        "intro": snapshot.get("intro", {"greeting": "Good morning,", "paragraphs": []}),
        "toc": {"label": "In this brief",
                "items": snapshot.get("toc", [s.get("headline", "") for s in sections])},
        "sections": sections,
        "signoff": {
            "paragraphs": ["That's today's brief. Forward it to a creator chasing their next format.",
                           "Reply with a trend you're seeing — we read everything."],
            "closing": "See you tomorrow,",
            "from": "The Viral Video Report team",
        },
        "footer": {
            "links": [{"text": "Subscribe", "url": "#"}, {"text": "Forward this", "url": "#"},
                      {"text": "Say hi", "url": "#"}],
            "org": f"© {d.year} Viral Video Report",
            "address": "Viral Video Report\nvipplay Inc",
            "legalLinks": [{"text": "Update preferences", "url": "#"},
                           {"text": "Unsubscribe", "url": "#"}],
        },
    }
    return newsletter, featured


def update_memory(memory, snapshot, newsletter, featured, today):
    trends = memory.setdefault("trends", {})
    for t in snapshot.get("new_this_week", []):
        if t["slug"] not in featured:
            continue
        rec = trends.setdefault(t["slug"], {"name": t.get("name", t["headline"]), "times_featured": 0})
        rec["name"] = t.get("name", t["headline"])
        rec["status"] = t.get("status", "new")
        rec["last_featured"] = today
        rec["times_featured"] = rec.get("times_featured", 0) + 1
        rec["section"] = "new"
    # track accelerating waves in `watching` (not featured, so no dedup lock)
    watching = memory.setdefault("watching", [])
    for a in snapshot.get("accelerating", []):
        if a.get("slug") and a["slug"] not in watching:
            watching.append(a["slug"])
    meta = memory.setdefault("meta", {})
    issue_no = meta.get("report_count", 0) + 1
    memory.setdefault("reports", []).append({
        "date": today, "issue": issue_no,
        "new": featured,
        "accelerating": [a.get("slug") for a in snapshot.get("accelerating", []) if a.get("slug")],
        "recreation": (snapshot.get("recreation") or {}).get("slug"),
    })
    meta["report_count"] = issue_no
    meta["last_updated"] = today
    return issue_no


def main():
    today = _today()
    memory = load_memory()
    if not os.path.isfile(SNAP_PATH):
        raise SystemExit(f"ERROR: {SNAP_PATH} not found — run the Virlo pull step first.")
    with open(SNAP_PATH, encoding="utf-8") as fh:
        snapshot = json.load(fh)

    newsletter, featured = build(snapshot, memory, today)
    issue_no = memory.get("meta", {}).get("report_count", 0) + 1
    html = render_html(newsletter)
    out = os.path.join(os.path.dirname(DB_PATH), f"issue-{issue_no:03d}.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)

    n_run = sum(1 for s in newsletter["sections"] if s["type"] == "stillrunning" for _ in s["running"])
    print(f"built issue {issue_no:03d} ({today}) -> {os.path.basename(out)}")
    print(f"  new this week : {featured or '(none — all deduped)'}")
    print(f"  accelerating  : {[a['name'] for a in snapshot.get('accelerating', [])]}")
    print(f"  still running : {sum(1 for s in newsletter['sections'] if s['type']=='stillrunning' for _ in s.get('running',[]))} one-liners")

    # STEP 4 — deliver (respects BRIEF_DRY_RUN; no-op raise handled by send_email)
    try:
        import send_email
        subject = f"Viral Video Report — {datetime.date.fromisoformat(today):%A, %B} {datetime.date.fromisoformat(today).day}, {datetime.date.fromisoformat(today).year} · Issue {issue_no:03d}"
        send_email.deliver(html, subject=subject)
    except Exception as e:
        print(f"  delivery skipped/failed: {e}")

    # STEP 5 — persist memory
    update_memory(memory, snapshot, newsletter, featured, today)
    save_memory(memory)
    print(f"  memory updated: report_count={memory['meta']['report_count']}")


if __name__ == "__main__":
    main()
