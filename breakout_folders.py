#!/usr/bin/env python3
# For each Virlo breakout sound: pull its top videos from ScrapeCreators
# (song/videos?clipId=<tiktok music id>), then download PER of them via tikwm
# into breakout_sounds/<sound name>/.  No webkit needed — pure HTTP.

import os
import re
import time
import httpx

SC_KEY = os.environ.get("SCRAPECREATORS_API_KEY")
if not SC_KEY:
    raise SystemExit("set SCRAPECREATORS_API_KEY (see .env)")

SC = "https://api.scrapecreators.com"
TIKWM = "https://www.tikwm.com/api/"
OUT = "breakout_sounds"
PER = int(os.environ.get("PER", "5"))

# Virlo get_breakout_sounds (name, TikTok music id) — today's pull
SOUNDS = [
    ("is it cool (feat. SZA)", "7655357458621728784"),
    ("Pink Matter", "6928503020053334017"),
    ("Ephemeral", "7655233146027673617"),
    ("World Cup 2026 Anthem (Shakira Style)", "7644244376386127888"),
    ("Dai Dai", "7637147165290924831"),
    ("On a Mission", "7274043399086426113"),
    ("Whisper and Roar", "7577311419314604049"),
    ("Always", "7217868767252973570"),
    ("World Cup Song 2026", "7623136614244845569"),
    ("Sanarie", "7656522782335174657"),
    ("Meme no ha", "7656522782335125505"),
    ("Saxophones getting louder - Sped Up", "7639417177691473937"),
    ("Haaland (Ha Ha Ha)", "7128005345142425601"),
    ("Mexico Mundial 2026", "7627049993715419137"),
    ("Endless Snow", "7629065989276403713"),
]


def safe(s):
    return re.sub(r"[^A-Za-z0-9 ._()+-]+", "_", str(s)).strip()[:60] or "x"


def sc_song_videos(client, clip_id):
    r = client.get(f"{SC}/v1/tiktok/song/videos", params={"clipId": clip_id},
                   headers={"x-api-key": SC_KEY, "User-Agent": "Mozilla/5.0"}, timeout=40)
    r.raise_for_status()
    return r.json().get("aweme_list", [])


def tikwm_download(client, url, dest):
    r = client.post(TIKWM, data={"url": url}, timeout=40)
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 0:
        raise RuntimeError(j.get("msg") or "tikwm error")
    play = (j.get("data") or {}).get("play")
    if not play:
        raise RuntimeError("no play url")
    total = 0
    with client.stream("GET", play, timeout=120) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_bytes(65536):
                f.write(chunk)
                total += len(chunk)
    if total < 1024:
        os.remove(dest)
        raise RuntimeError(f"too small ({total}b)")
    return total


def main():
    os.makedirs(OUT, exist_ok=True)
    client = httpx.Client(headers={"user-agent": "Mozilla/5.0"})
    for name, clip in SOUNDS:
        folder = os.path.join(OUT, safe(name))
        os.makedirs(folder, exist_ok=True)
        print(f"\n=== {name}  (music id {clip}) ===")
        try:
            vids = sc_song_videos(client, clip)
        except Exception as e:
            print(f"  ! ScrapeCreators failed: {e}")
            continue
        vids.sort(key=lambda v: (v.get("statistics") or {}).get("play_count", 0), reverse=True)
        got = 0
        for v in vids:
            if got >= PER:
                break
            au = (v.get("author") or {}).get("unique_id")
            au = au if isinstance(au, str) else "user"
            vid = v.get("aweme_id") or v.get("id")
            if not vid:
                continue
            url = f"https://www.tiktok.com/@{au}/video/{vid}"
            dest = os.path.join(folder, f"{got+1:02d}_{safe(au)}_{vid}.mp4")
            try:
                nbytes = tikwm_download(client, url, dest)
                pc = (v.get("statistics") or {}).get("play_count", 0)
                print(f"  {got+1}/{PER}  @{au}  {pc:,} views  {nbytes/1024/1024:.1f}MB")
                got += 1
                time.sleep(1.5)
            except Exception as e:
                print(f"  ! failed @{au}: {e}")
        print(f"  -> {got}/{PER} in {folder}/")
    client.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
