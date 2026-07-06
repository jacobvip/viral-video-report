#!/usr/bin/env python3
# ============================================================================
#  Viral Video Report — Gmail-safe email generator
# ----------------------------------------------------------------------------
#  Python port of "Newsletter Template.dc.html" (Claude Design handoff).
#  Reproduces the exact email-safe markup: <table> layout, inline literal
#  styles only (no CSS vars / flex / grid), web fonts progressively enhanced
#  with Georgia / Helvetica / Courier fallbacks.
#
#  USAGE
#    - Edit the DAILY DATA BLOCK (`NEWSLETTER` dict) to publish an issue, then
#        python3 vvr_generator.py        ->  writes viral-video-report.html
#    - Or from the pipeline: render_html(data) with a dict of the same shape.
#      A provided dict always wins (mirrors the template's `props.data ?? NEWSLETTER`).
#
#  SECTION TYPES (ordered `sections` list; reorder/add/remove freely)
#    "trend"        NEW THIS WEEK  — category, emoji, headline,
#                   videos[{src,handle,meta}], metrics[{value,label}],
#                   leadLabel, lead, detailsTitle, details[], whyLabel, why, cta
#    "watchlist"    ACCELERATING   — leadLabel, lead, watch[{name,metric,note}]
#    "stillrunning" STILL RUNNING  — running[{name,status,url,linkLabel}]
#    "recreation"   RECREATION     — leadLabel, lead, steps[], cta
#    "sponsor"      TOGETHER WITH  — leadLabel, lead, details[], cta
#  Omit any field to hide its block.
#
#  Blocks render on FIELD PRESENCE, not on `type` — `type` is just a label.
#  brandIcon / banner.src / video.src: for email, host at a public https URL.
# ============================================================================

import html
import os

# ==== DAILY DATA BLOCK — the only part edited each day ======================
NEWSLETTER = {
    "meta": {
        "brandIcon": "https://raw.githubusercontent.com/jacobvip/viral-video-report/main/html-newsletter-template/project/assets/vvr-icon.png",
        "wordmarkPre": "Viral Video ",
        "wordmarkAccent": "Report",
        "tagline": "Your daily short-form video trend brief — what's new, what's accelerating, what to copy.",
        "issueLine": "Weekday · Month D, YYYY · Issue 001",
        "banner": {"src": "", "alt": "your logo + sponsor banner", "url": ""},
        "headerLinks": [
            {"label": "Read online", "url": "#"},
            {"label": "Subscribe", "url": "#"},
            {"label": "Archive", "url": "#"},
        ],
    },
    "intro": {
        "greeting": "Good morning,",
        "paragraphs": [
            "Open with the single biggest change since yesterday — the format that's suddenly everywhere, or the wave about to break. One or two sentences, straight to it.",
            "Then hand off to the rundown below: what's new, what's climbing, and what's still running.",
        ],
    },
    "toc": {
        "label": "In this brief",
        "items": [
            "New this week — the copyable format to run today",
            "Accelerating — a wave to watch",
            "Still running — trends from the last 7 days",
            "Recreation template of the day",
        ],
    },
    "sections": [
        {
            "type": "trend",
            "category": "New this week",
            "emoji": "🔥",
            "headline": "Name the trending format here",
            "videos": [
                {"src": "", "handle": "@creator_one", "meta": "2.4M views · 8K followers"},
                {"src": "", "handle": "@creator_two", "meta": "1.1M views · 40K followers"},
                {"src": "", "handle": "@creator_three", "meta": "890K views · 2K followers"},
            ],
            "metrics": [
                {"value": "38×", "label": "outlier ratio"},
                {"value": "1.2M", "label": "avg views / clip"},
                {"value": "9.7K", "label": "posts · 7d"},
            ],
            "leadLabel": "The format:",
            "lead": "Describe the repeatable structure in one or two sentences — the hook, the beat the sound lands on, the visual gag. This is what a viewer would copy.",
            "detailsTitle": "Why it works:",
            "details": [
                "A small-follower account still pulled big views — the format carries it, not the creator.",
                "The setup reads in the first second, so it survives the scroll.",
                "It's flexible: swap the subject and it still lands.",
            ],
            "whyLabel": "Recreate it:",
            "why": "The exact angle to shoot for your audience — the swap that makes this format yours.",
            "cta": {"label": "Hear the sound →", "url": "#"},
        },
        {
            "type": "watchlist",
            "category": "Accelerating · watch list",
            "emoji": "📈",
            "headline": "Rising, but not a template yet",
            "leadLabel": "The read:",
            "lead": "One line on what's climbing and why it isn't copyable yet.",
            "watch": [
                {"name": "An audio wave", "metric": "+320% posts", "note": "Lots of posts but low views-per-clip — music discovery, not a format. Watch for a structure to form around it."},
                {"name": "An early challenge tag", "metric": "4.1K posts", "note": "Concept is forming but there's no shared beat or gag yet. Not stable enough to recommend recreating."},
            ],
        },
        {
            "type": "stillrunning",
            "category": "Still running",
            "emoji": "🔁",
            "headline": "Featured in the last 7 days",
            "running": [
                {"name": "A format you led with earlier", "status": "cooling", "url": "#", "linkLabel": "watch →"},
                {"name": "Another recent lead", "status": "steady", "url": "#", "linkLabel": "watch →"},
                {"name": "One more from last week", "status": "still climbing", "url": "#", "linkLabel": "watch →"},
            ],
        },
        {
            "type": "recreation",
            "category": "Recreation template of the day",
            "emoji": "🎬",
            "headline": "Shoot today's lead format in 4 steps",
            "leadLabel": "The brief:",
            "lead": "A do-this-now shot list built from today's New This Week lead — rotated daily, never the same as yesterday.",
            "steps": [
                "Open on the hook within the first second — mirror the reference clips.",
                "Land the key action on the sound's drop / beat.",
                "Swap in your subject so it's unmistakably yours.",
                "Caption with the one-line setup so it reads muted.",
            ],
            "cta": {"label": "Grab the sound →", "url": "#"},
        },
        {
            "type": "sponsor",
            "category": "Together with · Partner name",
            "emoji": "🤝",
            "headline": "A short, benefit-led sponsor line",
            "leadLabel": "The pitch:",
            "lead": "One or two sentences in your own voice describing the sponsor and what they do.",
            "details": [
                "A concrete benefit worth naming.",
                "A second reason a reader might click.",
                "An offer or deadline, if there is one.",
            ],
            "cta": {"label": "Check them out →", "url": "#"},
        },
    ],
    "signoff": {
        "paragraphs": [
            "That's today's brief. Forward it to a creator who needs to see what's breaking.",
            "Hit reply with a trend you're seeing — we read everything.",
        ],
        "closing": "See you tomorrow,",
        "from": "The Viral Video Report team",
        "pitch": "Want your product in front of these creators? Reply and let's talk.",
    },
    "footer": {
        "links": [
            {"text": "Subscribe", "url": "#"},
            {"text": "Forward this", "url": "#"},
            {"text": "Say hi", "url": "#"},
        ],
        "org": "© 0000 Viral Video Report",
        "address": "Viral Video Report\n000 Street, City, Country",
        "legalLinks": [
            {"text": "Update preferences", "url": "#"},
            {"text": "Unsubscribe", "url": "#"},
        ],
    },
}
# ==== END DAILY DATA BLOCK ==================================================


# ==== LOCKED ASSEMBLY — do not edit below ==================================
def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def _img(src, alt, style):
    """Emit an <img> only when a real src exists (mirrors imgNode)."""
    if not src:
        return ""
    return f'<img src="{esc(src)}" alt="{esc(alt or "")}" style="{style}">'


_VID_STYLE = "display:block; width:100%; border-radius:8px; border:1px solid #e5e1d8;"


def _masthead(m):
    header_links = "".join(
        f'<td style="padding:0 9px;"><a href="{esc(hl.get("url","#"))}" '
        f'style="font-family:\'IBM Plex Mono\',\'Courier New\',monospace; font-size:10.5px; '
        f'letter-spacing:1.2px; text-transform:uppercase; color:#a09a8d;">{esc(hl.get("label",""))}</a></td>'
        for hl in m.get("headerLinks", [])
    )
    brand_icon = _img(m.get("brandIcon"), (m.get("wordmarkPre", "") + m.get("wordmarkAccent", "")),
                      "display:block; width:50px; height:58px;")
    b = m.get("banner")
    if b and b.get("src"):
        banner = ('<div style="padding-top:22px;">'
                  + _img(b.get("src"), b.get("alt") or "banner",
                         "display:block; width:100%; border-radius:8px; border:1px solid #e5e1d8;")
                  + '</div>')
    elif b is not None:
        alt = esc((b.get("alt") if b else None) or "your logo + sponsor banner")
        banner = (
            '<table role="presentation" width="100%" cellPadding="0" cellSpacing="0" border="0" '
            'style="width:100%; margin-top:22px;"><tr>'
            '<td align="center" valign="middle" height="90" style="height:90px; background:#f2efe8; '
            'border:1px solid #e5e1d8; border-radius:8px;">'
            '<span style="font-family:\'IBM Plex Mono\',\'Courier New\',monospace; font-size:11px; color:#9a9587;">'
            f'&#9633; banner &rarr; {alt}</span></td></tr></table>'
        )
    else:
        banner = ""

    return f'''        <tr><td style="height:4px; line-height:4px; font-size:0; background:#00adee;">&nbsp;</td></tr>
        <tr>
          <td align="center" style="padding:15px 30px 13px;">
            <table role="presentation" cellPadding="0" cellSpacing="0" border="0" align="center"><tr>{header_links}</tr></table>
          </td>
        </tr>
        <tr>
          <td align="center" bgcolor="#111318" style="background:#111318; padding:34px 30px;">
            <table role="presentation" cellPadding="0" cellSpacing="0" border="0" align="center" style="margin:0 auto;"><tr>
              <td valign="middle" style="padding-right:16px;">{brand_icon}</td>
              <td valign="middle" style="font-family:'Newsreader',Georgia,serif; font-weight:600; font-size:35px; line-height:1; letter-spacing:-0.5px; color:#ffffff;"><span>{esc(m.get("wordmarkPre",""))}</span><span style="color:#00adee;">{esc(m.get("wordmarkAccent",""))}</span></td>
            </tr></table>
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:20px 30px 22px; border-bottom:1px solid #ece8df;">
            <div style="font-family:'IBM Plex Sans',Helvetica,Arial,sans-serif; font-size:14px; color:#6b675e; line-height:1.5;">{esc(m.get("tagline",""))}</div>
            <div style="font-family:'IBM Plex Mono','Courier New',monospace; font-size:11px; letter-spacing:0.8px; color:#a7a294; text-transform:uppercase; padding-top:8px;">{esc(m.get("issueLine",""))}</div>
            {banner}
          </td>
        </tr>
'''


def _intro(intro):
    paras = "".join(
        f'<div style="font-size:15.5px; line-height:1.62; color:#33302a; margin-bottom:14px;">{esc(p)}</div>'
        for p in intro.get("paragraphs", [])
    )
    return f'''        <tr>
          <td style="padding:26px 30px 20px; font-family:'IBM Plex Sans',Helvetica,Arial,sans-serif;">
            <div style="font-size:16px; line-height:1.6; color:#1b1a17; font-weight:600; margin-bottom:14px;">{esc(intro.get("greeting",""))}</div>
            {paras}
          </td>
        </tr>
'''


def _toc(toc):
    items = toc.get("items", [])
    if not items:
        return ""
    rows = "".join(
        f'<div style="font-size:14.5px; line-height:1.5; color:#3a372f; margin-bottom:8px;">'
        f'<span style="color:#00adee;">&rsaquo;</span>&nbsp;&nbsp;{esc(it)}</div>'
        for it in items
    )
    return f'''        <tr>
          <td style="padding:0 30px 6px;">
            <table role="presentation" width="100%" cellPadding="0" cellSpacing="0" border="0" style="width:100%; background:#f6f4ef; border:1px solid #ece8df; border-radius:8px;"><tr>
              <td style="padding:18px 20px; font-family:'IBM Plex Sans',Helvetica,Arial,sans-serif;">
                <div style="font-family:'IBM Plex Mono','Courier New',monospace; font-size:11px; letter-spacing:1.4px; text-transform:uppercase; color:#00adee; font-weight:600; margin-bottom:12px;">{esc(toc.get("label","In this brief"))}</div>
                {rows}
              </td>
            </tr></table>
          </td>
        </tr>
'''


def _videos(videos):
    cells = []
    for i, v in enumerate(videos, 1):
        if v.get("src"):
            media = _img(v.get("src"), v.get("handle"), _VID_STYLE)
        else:
            media = (
                '<table role="presentation" width="100%" cellPadding="0" cellSpacing="0" border="0" style="width:100%;"><tr>'
                '<td align="center" valign="middle" height="272" style="height:272px; background:#f2efe8; border:1px solid #e5e1d8; border-radius:8px;">'
                '<span style="font-family:\'IBM Plex Mono\',\'Courier New\',monospace; font-size:10px; color:#9a9587; line-height:1.5;">'
                f'&#9633;<br>video {i}</span></td></tr></table>'
            )
        cells.append(
            f'<td width="33%" valign="top" style="width:33%;">{media}'
            f'<div style="font-family:\'IBM Plex Mono\',\'Courier New\',monospace; font-size:11px; color:#00adee; padding-top:7px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;">{esc(v.get("handle",""))}</div>'
            f'<div style="font-size:10.5px; color:#8a857a; line-height:1.4;">{esc(v.get("meta",""))}</div></td>'
        )
    return ('<table role="presentation" width="100%" cellPadding="0" cellSpacing="0" border="0" '
            'style="width:100%; margin:16px 0 18px; border-spacing:9px 0; border-collapse:separate;"><tr>'
            + "".join(cells) + "</tr></table>")


def _metrics(metrics):
    cells = "".join(
        '<td valign="top" style="background:#eaf7fc; border:1px solid #cfeaf5; border-radius:8px; padding:8px 13px;">'
        f'<div style="font-family:\'IBM Plex Sans\',Helvetica,Arial,sans-serif; font-weight:600; font-size:17px; color:#0284b0; line-height:1;">{esc(mt.get("value",""))}</div>'
        f'<div style="font-family:\'IBM Plex Mono\',\'Courier New\',monospace; font-size:9.5px; letter-spacing:0.8px; text-transform:uppercase; color:#8a857a; padding-top:4px;">{esc(mt.get("label",""))}</div></td>'
        for mt in metrics
    )
    return ('<table role="presentation" cellPadding="0" cellSpacing="0" border="0" '
            'style="margin:0 0 16px; border-spacing:8px 0; border-collapse:separate;"><tr>'
            + cells + "</tr></table>")


def _details(details):
    return "".join(
        '<table role="presentation" width="100%" cellPadding="0" cellSpacing="0" border="0" style="width:100%; margin-bottom:8px;"><tr>'
        '<td width="16" valign="top" style="width:16px; font-size:15px; line-height:1.6; color:#00adee;">&bull;</td>'
        f'<td valign="top" style="font-size:15px; line-height:1.6; color:#33302a;">{esc(dt)}</td></tr></table>'
        for dt in details
    )


def _steps(steps):
    return "".join(
        '<table role="presentation" width="100%" cellPadding="0" cellSpacing="0" border="0" style="width:100%; margin-bottom:10px;"><tr>'
        f'<td width="24" valign="top" style="width:24px; font-family:\'IBM Plex Mono\',\'Courier New\',monospace; font-size:14px; font-weight:600; line-height:1.5; color:#00adee;">{i}</td>'
        f'<td valign="top" style="font-size:15px; line-height:1.55; color:#33302a;">{esc(st)}</td></tr></table>'
        for i, st in enumerate(steps, 1)
    )


def _watch(watch):
    return "".join(
        '<table role="presentation" width="100%" cellPadding="0" cellSpacing="0" border="0" style="width:100%; margin-top:14px; padding-top:14px; border-top:1px solid #f0ece3;"><tr>'
        f'<td valign="top" style="font-size:15px; color:#1b1a17; font-weight:600;">{esc(wl.get("name",""))}</td>'
        f'<td valign="top" align="right" style="font-family:\'IBM Plex Mono\',\'Courier New\',monospace; font-size:11px; color:#0284b0; white-space:nowrap;">{esc(wl.get("metric",""))}</td>'
        f'</tr><tr><td colSpan="2" style="font-size:14px; line-height:1.55; color:#6b675e; padding-top:6px;">{esc(wl.get("note",""))}</td></tr></table>'
        for wl in watch
    )


def _running(running):
    return "".join(
        '<table role="presentation" width="100%" cellPadding="0" cellSpacing="0" border="0" style="width:100%; margin-bottom:10px;"><tr>'
        f'<td valign="top" style="font-size:14.5px; line-height:1.4; color:#33302a;">{esc(rn.get("name",""))}'
        f'<span style="color:#8a857a;"> &middot; {esc(rn.get("status",""))}</span></td>'
        f'<td valign="top" align="right" style="white-space:nowrap;"><a href="{esc(rn.get("url","#"))}" '
        f'style="font-family:\'IBM Plex Mono\',\'Courier New\',monospace; font-size:11px; color:#0284b0; border-bottom:1px solid #bfe6f5;">{esc(rn.get("linkLabel") or "watch →")}</a></td></tr></table>'
        for rn in running
    )


def _cta(cta):
    return ('<table role="presentation" cellPadding="0" cellSpacing="0" border="0" style="margin-top:16px;"><tr>'
            '<td style="background:#00adee; border-radius:8px;">'
            f'<a href="{esc(cta.get("url","#"))}" style="display:inline-block; padding:11px 20px; '
            f'font-family:\'IBM Plex Mono\',\'Courier New\',monospace; font-weight:500; font-size:12.5px; '
            f'letter-spacing:0.6px; text-transform:uppercase; color:#ffffff;">{esc(cta.get("label",""))}</a></td></tr></table>')


def _section(s):
    parts = []
    if s.get("category"):
        parts.append(f'<div style="font-family:\'IBM Plex Mono\',\'Courier New\',monospace; font-size:11px; letter-spacing:1.4px; text-transform:uppercase; color:#00adee; font-weight:600; margin-bottom:10px;">{esc(s["category"])}</div>')
    emoji = (s.get("emoji", "") + " ") if s.get("emoji") else ""
    parts.append(f'<div style="font-family:\'Newsreader\',Georgia,serif; font-weight:600; font-size:26px; line-height:1.2; color:#1b1a17; margin-bottom:6px;">{esc(emoji)}{esc(s.get("headline",""))}</div>')
    if s.get("videos"):
        parts.append(_videos(s["videos"]))
    if s.get("metrics"):
        parts.append(_metrics(s["metrics"]))
    if s.get("lead"):
        parts.append(f'<div style="font-size:15.5px; line-height:1.62; color:#33302a; margin-bottom:14px;"><strong style="color:#1b1a17;">{esc(s.get("leadLabel",""))}</strong> {esc(s["lead"])}</div>')
    if s.get("detailsTitle"):
        parts.append(f'<div style="font-weight:600; color:#1b1a17; font-size:14.5px; margin:16px 0 9px;">{esc(s["detailsTitle"])}</div>')
    if s.get("details"):
        parts.append(_details(s["details"]))
    if s.get("steps"):
        parts.append(_steps(s["steps"]))
    if s.get("watch"):
        parts.append(_watch(s["watch"]))
    if s.get("running"):
        parts.append(_running(s["running"]))
    if s.get("why"):
        parts.append(f'<table role="presentation" width="100%" cellPadding="0" cellSpacing="0" border="0" style="width:100%; margin-top:16px; background:#eaf7fc; border:1px solid #cfeaf5; border-radius:8px;"><tr><td style="padding:13px 16px; font-size:15px; line-height:1.6; color:#33302a;"><strong style="color:#0284b0;">{esc(s.get("whyLabel",""))}</strong> {esc(s["why"])}</td></tr></table>')
    if s.get("cta") and s["cta"].get("label"):
        parts.append(_cta(s["cta"]))
    return (f'''        <tr>
          <td style="padding:28px 30px; border-top:1px solid #ece8df; font-family:'IBM Plex Sans',Helvetica,Arial,sans-serif;">
            {''.join(parts)}
          </td>
        </tr>
''')


def _signoff(so):
    paras = "".join(
        f'<div style="font-size:15.5px; line-height:1.62; color:#33302a; margin-bottom:14px;">{esc(p)}</div>'
        for p in so.get("paragraphs", [])
    )
    pitch = (f'<div style="font-size:13px; color:#8a857a; line-height:1.55; padding-top:10px;">{esc(so["pitch"])}</div>'
             if so.get("pitch") else "")
    return f'''        <tr>
          <td style="padding:26px 30px; border-top:1px solid #ece8df; font-family:'IBM Plex Sans',Helvetica,Arial,sans-serif;">
            {paras}
            <div style="font-size:15.5px; color:#33302a; margin-bottom:4px;">{esc(so.get("closing",""))}</div>
            <div style="font-family:'Newsreader',Georgia,serif; font-size:17px; color:#1b1a17; font-weight:600;">{esc(so.get("from",""))}</div>
            {pitch}
          </td>
        </tr>
'''


def _footer(f, m):
    brand_icon_sm = _img(m.get("brandIcon"), "", "display:block; width:24px; height:28px;")
    links = "".join(
        f'<td style="padding:0 8px;"><a href="{esc(fl.get("url","#"))}" style="font-size:12.5px; color:#0284b0; border-bottom:1px solid #bfe6f5;">{esc(fl.get("text",""))}</a></td>'
        for fl in f.get("links", [])
    )
    legal = "".join(
        f'<td style="padding:0 7px;"><a href="{esc(ll.get("url","#"))}" style="font-family:\'IBM Plex Mono\',\'Courier New\',monospace; font-size:10px; letter-spacing:0.8px; text-transform:uppercase; color:#b3ae9f;">{esc(ll.get("text",""))}</a></td>'
        for ll in f.get("legalLinks", [])
    )
    return f'''        <tr>
          <td align="center" style="padding:26px 30px 30px; background:#faf8f4; border-top:1px solid #ece8df; font-family:'IBM Plex Sans',Helvetica,Arial,sans-serif;">
            <table role="presentation" cellPadding="0" cellSpacing="0" border="0" align="center" style="margin:0 auto 14px;"><tr>
              <td valign="middle" style="padding-right:9px;">{brand_icon_sm}</td>
              <td valign="middle" style="font-family:'Newsreader',Georgia,serif; font-weight:600; font-size:19px; color:#1b1a17;"><span>{esc(m.get("wordmarkPre",""))}</span><span style="color:#00adee;">{esc(m.get("wordmarkAccent",""))}</span></td>
            </tr></table>
            <table role="presentation" cellPadding="0" cellSpacing="0" border="0" align="center" style="margin-bottom:14px;"><tr>{links}</tr></table>
            <div style="font-size:12px; color:#a7a294; line-height:1.6;">{esc(f.get("org",""))}</div>
            <div style="font-size:12px; color:#a7a294; line-height:1.6; white-space:pre-line;">{esc(f.get("address",""))}</div>
            <table role="presentation" cellPadding="0" cellSpacing="0" border="0" align="center" style="margin-top:12px;"><tr>{legal}</tr></table>
          </td>
        </tr>
'''


def render_html(data=None):
    """Render the full Viral Video Report email HTML from a NEWSLETTER-shaped dict."""
    d = data or NEWSLETTER
    m = d.get("meta", {})
    body = (
        _masthead(m)
        + _intro(d.get("intro", {"paragraphs": []}))
        + _toc(d.get("toc", {}))
        + "".join(_section(s) for s in d.get("sections", []))
        + _signoff(d.get("signoff", {"paragraphs": []}))
        + _footer(d.get("footer", {"links": [], "legalLinks": []}), m)
    )
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,600&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  html, body {{ margin: 0; padding: 0; }}
  body {{ background: #eceae4; -webkit-font-smoothing: antialiased; }}
  img {{ border: 0; outline: none; text-decoration: none; }}
  table {{ border-collapse: collapse; }}
  a {{ text-decoration: none; }}
</style>
</head>
<body style="background:#eceae4;">
<table role="presentation" width="100%" cellPadding="0" cellSpacing="0" border="0" style="width:100%; background:#eceae4;">
  <tr>
    <td align="center" style="padding:36px 12px;">
      <table role="presentation" width="640" cellPadding="0" cellSpacing="0" border="0" style="width:640px; max-width:640px; background:#ffffff; border:1px solid #e5e1d8;">
{body}      </table>
    </td>
  </tr>
</table>
</body>
</html>
'''


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "viral-video-report.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render_html())
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
