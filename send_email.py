#!/usr/bin/env python3
# ============================================================================
#  Viral Video Report — delivery module (Resend)
# ----------------------------------------------------------------------------
#  Sends the generated email via the Resend HTTP API. Stdlib only (urllib) so a
#  cron job has no dependencies to install.
#
#  CONFIG — environment variables only, never hardcode secrets:
#    RESEND_API_KEY   (required for a live send)  Resend API key.
#    BRIEF_FROM       sender. Default "onboarding@resend.dev" (Resend test
#                     sender — can ONLY deliver to the account owner's address
#                     until you verify a real domain).
#    BRIEF_TO         comma-separated recipients. Default "kanyeshrayz@gmail.com".
#    BRIEF_DRY_RUN    if "1", build/read the HTML but skip the actual send.
#    BRIEF_SUBJECT    optional subject override; else derived from today's date.
#
#  USAGE
#    BRIEF_DRY_RUN=1 python3 send_email.py            # safe end-to-end test
#    RESEND_API_KEY=... python3 send_email.py         # live send
#    python3 send_email.py path/to/email.html         # send a specific file
#    from send_email import deliver; deliver(html, subject=..., text=...)
#
#  Delivery target is intentionally swappable: one BRIEF_FROM/BRIEF_TO seam here
#  (and a stubbed publish_substack hook) rather than send logic sprinkled through
#  the pipeline. Fails loudly (non-zero exit) on misconfig so a scheduled run
#  never silently no-ops.
# ============================================================================

import datetime
import json
import os
import sys
import urllib.error
import urllib.request

RESEND_ENDPOINT = "https://api.resend.com/emails"
DEFAULT_FROM = "onboarding@resend.dev"
DEFAULT_TO = "kanyeshrayz@gmail.com"
DEFAULT_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "viral-video-report.html")


class ConfigError(Exception):
    """Missing/invalid configuration — a live send cannot proceed."""


class SendError(Exception):
    """Resend rejected the message or the network failed."""


def build_subject(date=None):
    d = date or datetime.date.today()
    return f"Viral Video Report — {d:%A, %B} {d.day}, {d.year}"


def _recipients():
    raw = os.environ.get("BRIEF_TO", DEFAULT_TO)
    to = [r.strip() for r in raw.split(",") if r.strip()]
    if not to:
        raise ConfigError("BRIEF_TO is empty — no recipients to send to.")
    return to


def send_via_resend(html, subject, text, api_key, sender, recipients):
    """POST to Resend. Returns the message id. Raises SendError on failure."""
    payload = {"from": sender, "to": recipients, "subject": subject, "html": html, "text": text}
    req = urllib.request.Request(
        RESEND_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Resend sits behind Cloudflare, which WAF-blocks urllib's default
            # "Python-urllib/x" UA with error 1010. Send a normal UA.
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("id")
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8")
        except Exception:
            detail = ""
        raise SendError(f"Resend returned HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise SendError(f"network error reaching Resend: {e.reason}") from e


def deliver(html, subject=None, text=None):
    """Deliver the email per env config. Returns the Resend message id (or None on dry run)."""
    if not html or not html.strip():
        raise ConfigError("empty HTML body — nothing to send.")

    sender = os.environ.get("BRIEF_FROM", DEFAULT_FROM)
    recipients = _recipients()
    subject = subject or os.environ.get("BRIEF_SUBJECT") or build_subject()
    text = text or "Your daily short-form video trend brief — what's new, what's accelerating, what to copy. View this email in an HTML-capable client."

    if os.environ.get("BRIEF_DRY_RUN") == "1":
        print(f"[DRY RUN] would send:\n  subject: {subject}\n  from:    {sender}\n"
              f"  to:      {', '.join(recipients)}\n  html:    {len(html)} bytes")
        return None

    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise ConfigError("RESEND_API_KEY is not set (and BRIEF_DRY_RUN != 1). "
                          "Set the key for a live send, or BRIEF_DRY_RUN=1 to test.")

    msg_id = send_via_resend(html, subject, text, api_key, sender, recipients)
    print(f"sent '{subject}' -> {', '.join(recipients)}  resend_id={msg_id}")
    return msg_id


def publish_substack(html, subject=None):
    """Placeholder for a future Substack publish target. Wire the Substack
    publish API here; deliver() stays the email seam, this becomes the second
    swappable channel. Intentionally not implemented yet."""
    raise NotImplementedError("Substack publishing is not wired up yet.")


def _load_html(argv):
    """Load HTML from an explicit path arg, the default output file, or by
    generating it fresh from vvr_generator if no file exists."""
    if len(argv) > 1:
        path = argv[1]
        if not os.path.isfile(path):
            raise ConfigError(f"HTML file not found: {path}")
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    if os.path.isfile(DEFAULT_HTML):
        with open(DEFAULT_HTML, encoding="utf-8") as fh:
            return fh.read()
    # no file yet — build it from the generator's current DAILY DATA BLOCK
    try:
        from vvr_generator import render_html
    except Exception as e:
        raise ConfigError(f"no HTML file and could not import vvr_generator: {e}") from e
    return render_html()


def main():
    try:
        html = _load_html(sys.argv)
        deliver(html)
    except (ConfigError, SendError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
