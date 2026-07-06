# Viral Video Report

Daily short-form-video trend brief. Pulls trend data (Virlo), applies editorial
logic (format vs audio-wave, rank-by-change, 7-day dedup), renders a Gmail-safe
HTML email, and sends it via Resend.

## Files

| File | Role |
|---|---|
| `vvr_generator.py` | Email template as a Python generator (port of the Claude Design `Newsletter Template.dc.html`). Edit the `NEWSLETTER` dict or pass `render_html(data)` a dict of the same shape. Writes `viral-video-report.html`. |
| `send_email.py` | Delivery via Resend. Config from env only. `deliver(html, subject, text)` or run as a script. |
| `.env.example` | Config template — copy to `.env`. |
| `logs/` | Per-run logs (for the scheduled job). |
| `html-newsletter-template/` | Original Claude Design handoff bundle (design source of truth + `assets/vvr-icon.png`). |

## Quick start

```bash
# 1. Generate + preview the email
python3 vvr_generator.py && open viral-video-report.html

# 2. Safe end-to-end test — builds/reads HTML, skips the actual send
BRIEF_DRY_RUN=1 python3 send_email.py

# 3. Live send (needs a Resend key)
set -a; source .env; set +a          # loads RESEND_API_KEY etc.
BRIEF_DRY_RUN=0 python3 send_email.py
```

`send_email.py` reads `viral-video-report.html` by default, accepts a path
argument, or regenerates from `vvr_generator` if no file exists.

## Resend: going from test sender to a real domain

Out of the box `BRIEF_FROM=onboarding@resend.dev` (Resend's test sender). It can
**only deliver to the email that owns your Resend account** — fine for testing,
useless for a real list.

To send to anyone:
1. In the Resend dashboard → **Domains** → add your domain and follow the DNS
   steps (SPF, DKIM, and a DMARC record). Wait for it to verify.
2. Set `BRIEF_FROM` to an address on that domain, e.g. `brief@yourdomain.com`.
3. Set `BRIEF_TO` to your real recipient list (comma-separated).

Nothing else changes — the sender is a single env seam.

## Future: Substack (second delivery channel)

Delivery is intentionally swappable. `send_email.py` has a stubbed
`publish_substack(html, subject)` next to `deliver()`. When you want to also
publish to Substack, wire its publish API inside that function and call it from
the pipeline alongside `deliver()` — don't scatter send logic elsewhere.

## Still to wire (pipeline)

- **Virlo pull → `NEWSLETTER` dict** — daily trend fetch (`get_trending_sounds`,
  `get_breakout_sounds`, `get_sound_videos`) building the sections, ≤ $0.80/run.
- **Memory / dedup DB** — JSON state read first / written last, 7-day dedup so
  nothing featured in the last week is re-featured (appears only as "Still Running").
- **Schedule** — a daily cron invoking the run headless, logging to `logs/`.
