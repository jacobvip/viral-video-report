import asyncio
import os
from TikTokApi import TikTokApi

# Top mainstream trending sounds (external_id = TikTok music id) from Virlo
SOUNDS = {
    "is it cool? (feat. SZA) — Steve Lacy": "7655357458621728784",
    "Dai Dai — Shakira & Burna Boy": "7637147165290924831",
    "Saxophones getting louder (Sped Up)": "7639417177691473937",
}
COUNT = int(os.environ.get("COUNT", "12"))
TARGET = os.environ.get("SOUND_ID", "7655357458621728784")


async def main():
    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            sleep_after=3,
            headless=True,
            suppress_resource_load_types=["image", "media", "font", "stylesheet"],
            browser="webkit",
        )
        label = next((k for k, v in SOUNDS.items() if v == TARGET), TARGET)
        print(f"Videos using sound: {label}  (id={TARGET})")
        print("-" * 90)
        i = 0
        try:
            async for video in api.sound(id=TARGET).videos(count=COUNT):
                i += 1
                d = video.as_dict
                author = (d.get("author") or {}).get("uniqueId", "?")
                vid_id = d.get("id", "?")
                desc = (d.get("desc") or "").replace("\n", " ")[:70]
                stats = d.get("stats") or {}
                views = int(stats.get("playCount", 0) or 0)
                dur = (d.get("video") or {}).get("duration", "?")
                url = f"https://www.tiktok.com/@{author}/video/{vid_id}"
                print(f"{i:>2}. @{author:<18} {views:>12,} views  {dur}s")
                print(f"    {desc}")
                print(f"    {url}")
        except Exception as e:
            print(f"\n! sound.videos() failed: {type(e).__name__}: {e}")
            print("  (TikTok's music/item_list endpoint may be bot-blocked for this session)")


if __name__ == "__main__":
    asyncio.run(main())
