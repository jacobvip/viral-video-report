#!/usr/bin/env python3
# Simulates one daily run OUTSIDE Claude Code: prominence gate -> cluster ->
# outlier enrichment, tracking every API call for a cost report.
# Outputs daily_report_data.json for the analysis/report step.

import json, os, re, subprocess, tempfile, urllib.parse, urllib.request

SC_KEY = os.environ["SCRAPECREATORS_API_KEY"]
BASE = "https://api.scrapecreators.com"
LUFS_GATE = -14.0
TOP_ENRICH = 3

# The 15 Virlo breakout sounds (name, tiktok music id)
SOUNDS = [
    ("is it cool (feat. SZA)", "7655357458621728784"),
    ("Pink Matter", "6928503020053334017"),
    ("Ephemeral", "7655233146027673617"),
    ("World Cup 2026 Anthem", "7644244376386127888"),
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

credits = {"song_details": 0, "song_videos": 0, "video_detail": 0}


def sc(path, **params):
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{BASE}/{path}?{qs}",
                                 headers={"x-api-key": SC_KEY, "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def measure_lufs(audio_url):
    try:
        req = urllib.request.Request(audio_url, headers={"User-Agent": "Mozilla/5.0",
                                                         "Referer": "https://www.tiktok.com/"})
        data = urllib.request.urlopen(req, timeout=45).read()
    except Exception:
        return None
    tf = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tf.write(data); tf.close()
    try:
        out = subprocess.run(["ffmpeg", "-i", tf.name, "-af", "ebur128", "-f", "null", "/dev/null"],
                             capture_output=True, text=True).stderr
        m = re.findall(r"\bI:\s*(-?[0-9.]+)\s*LUFS", out)
        return float(m[-1]) if m else None
    finally:
        os.remove(tf.name)


def g(x, *p, default=None):
    for k in p:
        x = x.get(k) if isinstance(x, dict) else None
    return x if x is not None else default


results = []
for name, mid in SOUNDS:
    row = {"name": name, "music_id": mid}
    try:
        det = sc("v1/tiktok/song", clipId=mid); credits["song_details"] += 1
        mi = det.get("music_info", {})
        row["album"] = mi.get("album"); row["author"] = mi.get("author")
        row["user_count"] = int(mi.get("user_count", 0) or 0)
        pu = mi.get("play_url") or {}
        audio_url = (pu.get("url_list") or [pu.get("uri")])[0] if isinstance(pu, dict) else None
        row["lufs"] = measure_lufs(audio_url) if audio_url else None
    except Exception as e:
        row["error"] = f"details:{e}"; results.append(row); continue

    lufs = row.get("lufs")
    row["prominent"] = (lufs is not None and lufs >= LUFS_GATE)
    if not row["prominent"]:
        row["gate"] = f"FILTERED (LUFS {lufs})"
        results.append(row); continue

    row["gate"] = f"PASS (LUFS {lufs})"
    # cluster + outlier enrichment
    try:
        vids = sc("v1/tiktok/song/videos", clipId=mid).get("aweme_list", []); credits["song_videos"] += 1
    except Exception as e:
        row["error"] = f"videos:{e}"; results.append(row); continue
    vids.sort(key=lambda v: g(v, "statistics", "play_count", default=0), reverse=True)
    top = []
    for v in vids[:5]:
        au = g(v, "author", "unique_id"); au = au if isinstance(au, str) else "user"
        vid = v.get("aweme_id")
        st = g(v, "statistics", default={})
        item = {"handle": au, "views": st.get("play_count", 0), "likes": st.get("digg_count", 0),
                "shares": st.get("share_count", 0), "caption": (v.get("desc") or "")[:120],
                "hashtags": [t.get("hashtag_name") for t in (g(v, "text_extra", default=[]) or []) if t.get("hashtag_name")]}
        if len(top) < TOP_ENRICH:
            try:
                d2 = sc("v2/tiktok/video", url=f"https://www.tiktok.com/@{au}/video/{vid}"); credits["video_detail"] += 1
                a = d2.get("aweme_detail") or d2
                item["followers"] = g(a, "author", "follower_count")
                item["outlier"] = round(item["views"] / item["followers"]) if item.get("followers") else None
            except Exception:
                item["followers"] = None
        top.append(item)
    row["top_videos"] = top
    ratios = [t["outlier"] for t in top if t.get("outlier")]
    row["max_outlier"] = max(ratios) if ratios else None
    results.append(row)

out = {"sounds": results, "credits": credits, "lufs_gate": LUFS_GATE}
with open("daily_report_data.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

# console summary
print("PROMINENCE GATE:")
for r in results:
    lu = r.get("lufs")
    print(f"  {'PASS ' if r.get('prominent') else 'FILTER'}  LUFS {str(lu):>7}  {r['name']}  (uses {r.get('user_count',0):,})")
passed = [r for r in results if r.get("prominent")]
print(f"\n{len(passed)}/{len(results)} passed the gate")
print(f"credits used: {credits}  total={sum(credits.values())}")
