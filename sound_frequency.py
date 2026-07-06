import asyncio
import os
from collections import Counter
from TikTokApi import TikTokApi

CYCLES = int(os.environ.get("CYCLES", "3"))
PER = int(os.environ.get("PER", "35"))


async def main():
    seen = {}  # video_id -> (music_id, title, is_original)
    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=CYCLES, sleep_after=3, headless=True,
            suppress_resource_load_types=["image", "media", "font", "stylesheet"],
            browser="webkit",
        )
        for c in range(CYCLES):
            got = 0
            try:
                async for v in api.trending.videos(count=PER, session_index=c):
                    d = v.as_dict
                    vid = d.get("id")
                    if not vid or vid in seen:
                        continue
                    m = d.get("music") or {}
                    seen[vid] = (str(m.get("id")), (m.get("title") or "")[:38], bool(m.get("original")))
                    got += 1
            except Exception as e:
                print(f"cycle {c} stopped early: {type(e).__name__}")
            print(f"cycle {c}: +{got} new  (total {len(seen)})")

    n = len(seen)
    if n == 0:
        print("no videos"); return
    freq = Counter(mid for (mid, _, _) in seen.values())
    orig = sum(1 for (_, _, o) in seen.values() if o)
    titles = {mid: t for (mid, t, _) in seen.values()}
    print(f"\n=== {n} unique videos accumulated ===")
    print(f"'original sound' (creator-specific): {orig}/{n} = {round(100*orig/n)}%")
    print(f"distinct sounds: {len(freq)}")
    multi = {mid: c for mid, c in freq.items() if c > 1}
    print(f"sounds used by >1 video: {len(multi)}  <-- the signal we need")
    print("\nTOP SOUNDS BY FREQUENCY:")
    for mid, c in freq.most_common(12):
        print(f"  {c}x  {titles.get(mid,'?'):<38}  (id {mid})")


if __name__ == "__main__":
    asyncio.run(main())
