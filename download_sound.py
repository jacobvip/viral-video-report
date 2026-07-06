import asyncio
import json
import os
import re
from pathlib import Path
import httpx
from TikTokApi import TikTokApi

TIKWM_ENDPOINT = "https://www.tikwm.com/api/"
SOUND_ID = os.environ.get("SOUND_ID", "7655357458621728784")  # is it cool? (feat. SZA)
COUNT = int(os.environ.get("COUNT", "15"))
OUT_DIR = Path(os.environ.get("OUT_DIR", "downloads_sza"))


def safe(s: str, maxlen: int = 40) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s or "")
    return s[:maxlen].strip("_") or "video"


async def fetch_via_tikwm(client: httpx.AsyncClient, tiktok_url: str, dest: Path) -> int:
    r = await client.post(TIKWM_ENDPOINT, data={"url": tiktok_url}, timeout=30)
    r.raise_for_status()
    j = r.json()
    if j.get("code") != 0:
        raise RuntimeError(f"tikwm error: {j.get('msg')}")
    play_url = (j.get("data") or {}).get("play")
    if not play_url:
        raise RuntimeError("no play URL in tikwm response")
    total = 0
    async with client.stream("GET", play_url, timeout=120) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            async for chunk in resp.aiter_bytes(chunk_size=64 * 1024):
                f.write(chunk)
                total += len(chunk)
    return total


async def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT_DIR / "manifest.jsonl"
    seen_ids = set()
    if manifest_path.exists():
        for line in manifest_path.read_text().splitlines():
            try:
                seen_ids.add(json.loads(line).get("id"))
            except Exception:
                pass
    manifest = open(manifest_path, "a", encoding="utf-8")

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            sleep_after=3,
            headless=True,
            suppress_resource_load_types=["image", "media", "font", "stylesheet"],
            browser="webkit",
        )
        client = httpx.AsyncClient(headers={"user-agent": "Mozilla/5.0"})

        print(f"Downloading videos using sound id={SOUND_ID}")
        i = 0
        async for video in api.sound(id=SOUND_ID).videos(count=COUNT):
            i += 1
            d = video.as_dict
            vid_id = d.get("id", "unknown")
            author = (d.get("author") or {}).get("uniqueId", "unknown")
            desc = (d.get("desc") or "")
            stats = d.get("stats") or {}
            views = int(stats.get("playCount", 0) or 0)
            vinfo = d.get("video") or {}
            web_url = f"https://www.tiktok.com/@{author}/video/{vid_id}"

            fname = f"{i:03d}_{safe(author)}_{vid_id}.mp4"
            fpath = OUT_DIR / fname
            print(f"[{i:>2}/{COUNT}] @{author} • {views:,} views • {vinfo.get('duration','?')}s • {fname}")

            if vid_id in seen_ids:
                print("        · already downloaded, skipping")
                continue

            try:
                nbytes = await fetch_via_tikwm(client, web_url, fpath)
                if nbytes < 1024:
                    print(f"        ! too small ({nbytes} bytes)")
                    fpath.unlink(missing_ok=True)
                    continue
                print(f"        saved {nbytes / (1024*1024):.2f} MB")
            except Exception as e:
                print(f"        ! download failed: {e}")
                fpath.unlink(missing_ok=True)
                continue

            seen_ids.add(vid_id)
            record = {
                "n": i, "id": vid_id, "author": author, "desc": desc,
                "url": web_url, "file": str(fpath), "views": views,
                "likes": int(stats.get("diggCount", 0) or 0),
                "comments": int(stats.get("commentCount", 0) or 0),
                "shares": int(stats.get("shareCount", 0) or 0),
                "duration": vinfo.get("duration"),
                "sound_id": SOUND_ID,
                "sound": (d.get("music") or {}).get("title"),
            }
            manifest.write(json.dumps(record, ensure_ascii=False) + "\n")
            manifest.flush()
            await asyncio.sleep(1)

        await client.aclose()

    manifest.close()
    print(f"\nDone. Files in {OUT_DIR}/, manifest at {manifest_path}")


if __name__ == "__main__":
    asyncio.run(main())
