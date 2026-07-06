import asyncio
import json
import os
import re
from pathlib import Path
import httpx
from TikTokApi import TikTokApi

TIKWM_ENDPOINT = "https://www.tikwm.com/api/"

MS_TOKEN = os.environ.get("MS_TOKEN")
COUNT = int(os.environ.get("COUNT", "20"))
OUT_DIR = Path(os.environ.get("OUT_DIR", "downloads"))


def safe(s: str, maxlen: int = 40) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s or "")
    return s[:maxlen].strip("_") or "video"


async def fetch_via_tikwm(client: httpx.AsyncClient, tiktok_url: str, dest: Path) -> int:
    """Stream an unwatermarked MP4 to disk via tikwm.com's public API.
    TikTok's own CDN 403s the signed URLs outside a real tiktok.com session."""
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
            ms_tokens=[MS_TOKEN] if MS_TOKEN else None,
            num_sessions=1,
            sleep_after=3,
            headless=True,
            suppress_resource_load_types=["image", "media", "font", "stylesheet"],
            browser="webkit",
        )
        client = httpx.AsyncClient(headers={"user-agent": "Mozilla/5.0"})

        i = 0
        async for video in api.trending.videos(count=COUNT):
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

            print(f"[{i:>3}/{COUNT}] @{author} • {views:,} views • {vinfo.get('duration','?')}s • {fname}")

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
            await asyncio.sleep(1)

            seen_ids.add(vid_id)
            record = {
                "n": i,
                "id": vid_id,
                "author": author,
                "desc": desc,
                "url": f"https://www.tiktok.com/@{author}/video/{vid_id}",
                "file": str(fpath),
                "views": views,
                "likes": int(stats.get("diggCount", 0) or 0),
                "comments": int(stats.get("commentCount", 0) or 0),
                "shares": int(stats.get("shareCount", 0) or 0),
                "saves": int(stats.get("collectCount", 0) or 0),
                "createTime": d.get("createTime"),
                "duration": vinfo.get("duration"),
                "definition": vinfo.get("definition"),
                "width": vinfo.get("width"),
                "height": vinfo.get("height"),
                "cover": vinfo.get("cover"),
                "music": {
                    "id": (d.get("music") or {}).get("id"),
                    "title": (d.get("music") or {}).get("title"),
                    "author": (d.get("music") or {}).get("authorName"),
                    "original": (d.get("music") or {}).get("original"),
                },
                "hashtags": [c.get("title") for c in (d.get("challenges") or [])],
            }
            manifest.write(json.dumps(record, ensure_ascii=False) + "\n")
            manifest.flush()

        await client.aclose()

    manifest.close()
    print(f"\nDone. Files in {OUT_DIR}/, manifest at {manifest_path}")


if __name__ == "__main__":
    asyncio.run(main())
