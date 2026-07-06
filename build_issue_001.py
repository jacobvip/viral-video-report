#!/usr/bin/env python3
# Build Viral Video Report — Issue 001 from real trend data surfaced this session,
# then render the email HTML. Data sources: Virlo get_trending_sounds /
# get_breakout_sounds / Orbit outliers, plus the template-signal LEGO finding.
# Every number here is real (not placeholder).

from vvr_generator import render_html

ISSUE = {
    "meta": {
        "brandIcon": "",  # local PNG won't load in mail clients; text wordmark carries the brand
        "wordmarkPre": "Viral Video ",
        "wordmarkAccent": "Report",
        "tagline": "Your daily short-form video trend brief — what's new, what's accelerating, what to copy.",
        "issueLine": "Monday · July 6, 2026 · Issue 001",
        "banner": None,
        "headerLinks": [
            {"label": "Read online", "url": "#"},
            {"label": "Subscribe", "url": "#"},
            {"label": "Archive", "url": "#"},
        ],
    },
    "intro": {
        "greeting": "Good morning,",
        "paragraphs": [
            "The copyable format of the week is the lyric-edit: a song's lyrics laid over a simple aesthetic background, tagged with the trending-audio stack. A 42K-follower account (@replicque) is averaging 1.5M views with it — a 35× outlier, which is the tell that the format carries the video, not the creator.",
            "The loudest sound, meanwhile, isn't a template yet: “is it cool?” (SZA × Steve Lacy) is the runaway #1, but its clips are scattered across unrelated creators — music discovery, not a format. Full rundown below.",
        ],
    },
    "toc": {
        "label": "In this brief",
        "items": [
            "New this week — the lyric-edit format",
            "Accelerating — the sounds everyone's on",
            "Still running — formats from the field",
            "Recreation template — shoot a lyric-edit today",
        ],
    },
    "sections": [
        {
            "type": "trend",
            "category": "New this week",
            "emoji": "\U0001F525",
            "headline": "The lyric-edit format",
            "videos": [
                {"src": "", "handle": "@replicque", "meta": "'give it up to me' (Sean Paul) · 14.1M views"},
                {"src": "", "handle": "@replicque", "meta": "'telephone' (Lady Gaga) · 3.9M views"},
                {"src": "", "handle": "@replicque", "meta": "'smooth operator' (Sade) · 1.5M views"},
            ],
            "metrics": [
                {"value": "35×", "label": "outlier ratio"},
                {"value": "1.5M", "label": "avg views / clip"},
                {"value": "42K", "label": "creator followers"},
            ],
            "leadLabel": "The format:",
            "lead": "Overlay a song's lyrics as a clean, one-line-at-a-time caption over a simple nostalgic clip or gradient, revealed on the beat. The trending audio does the reach; the edit is dead simple to copy.",
            "detailsTitle": "Why it works:",
            "details": [
                "A 42K-follower account is averaging 1.5M views — 35× its size. The format carries it, not the following.",
                "Works with any song — throwbacks (Sean Paul, Sade) and new drops alike — so the well never runs dry.",
                "Zero filming: lyrics + a background + the sound. Anyone can ship one in minutes.",
            ],
            "whyLabel": "Recreate it:",
            "why": "Pick a song your audience is nostalgic for, run its trending audio, and put the most-quotable line on screen at the drop.",
            "cta": {"label": "Hear the sound →", "url": "#"},
        },
        {
            "type": "watchlist",
            "category": "Accelerating · watch list",
            "emoji": "\U0001F4C8",
            "headline": "The sounds everyone's on",
            "leadLabel": "The read:",
            "lead": "Huge momentum, but no shared format yet — ride the audio, don't expect a template.",
            "watch": [
                {"name": "“is it cool?” — SZA × Steve Lacy", "metric": "267 clips · 7d",
                 "note": "Runaway #1 trending sound and #1 breakout (score 161). But the clips are scattered across unrelated creators — music discovery, not a copyable format. Watch for a structure to form around it."},
                {"name": "“Dai Dai” — Shakira & Burna Boy", "metric": "106 clips · 7d",
                 "note": "World Cup-driven audio wave with strong reach (417K avg views), but no repeatable gag or beat-structure has formed around it yet."},
                {"name": "“Ephemeral” — yasuhiro soda", "metric": "100% burst",
                 "note": "Brand-new ambient edit sound — all its activity is in the last 7 days. One to watch if a format crystallizes around it."},
            ],
        },
        {
            "type": "stillrunning",
            "category": "Still running",
            "emoji": "\U0001F501",
            "headline": "Formats from the field",
            "running": [
                {"name": "LEGO builds (the @ministrybricks format)", "status": "cooling", "url": "#", "linkLabel": "watch →"},
                {"name": "The “choose one” choice challenge", "status": "steady · 416M-view peak", "url": "#", "linkLabel": "watch →"},
                {"name": "Dramatic classical-piano edits (Lacrimosa)", "status": "climbing · 4.1M avg views", "url": "#", "linkLabel": "watch →"},
            ],
        },
        {
            "type": "recreation",
            "category": "Recreation template of the day",
            "emoji": "\U0001F3AC",
            "headline": "Shoot a lyric-edit today",
            "leadLabel": "The brief:",
            "lead": "Today's New This Week lead, as a four-step shot list.",
            "steps": [
                "Pick a song your audience is nostalgic for and grab its trending audio (a throwback usually beats a new release).",
                "Set one lyric line on screen at a time, plain and centered — reveal each on the beat.",
                "Keep the background dead simple: a nostalgic clip or a soft gradient. No filming required.",
                "Caption it with the song plus the full stack: #lyrics #lyricsedit #virallyrics #trendingaudio #fypsounds.",
            ],
            "cta": {"label": "Grab the sound →", "url": "#"},
        },
    ],
    "signoff": {
        "paragraphs": [
            "That's issue 001. Forward it to a creator chasing their next format.",
            "Reply with a trend you're seeing — we read everything.",
        ],
        "closing": "See you tomorrow,",
        "from": "The Viral Video Report team",
    },
    "footer": {
        "links": [
            {"text": "Subscribe", "url": "#"},
            {"text": "Forward this", "url": "#"},
            {"text": "Say hi", "url": "#"},
        ],
        "org": "© 2026 Viral Video Report",
        "address": "Viral Video Report\nvipplay Inc",
        "legalLinks": [
            {"text": "Update preferences", "url": "#"},
            {"text": "Unsubscribe", "url": "#"},
        ],
    },
}


def main():
    html = render_html(ISSUE)
    with open("issue-001.html", "w", encoding="utf-8") as fh:
        fh.write(html)
    print("wrote issue-001.html", len(html), "bytes")


if __name__ == "__main__":
    main()
