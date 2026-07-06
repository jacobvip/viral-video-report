import asyncio
import os
from TikTokApi import TikTokApi

MS_TOKEN = os.environ.get("MS_TOKEN")
COUNT = int(os.environ.get("COUNT", "20"))


async def main():
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[MS_TOKEN] if MS_TOKEN else None,
            num_sessions=1,
            sleep_after=3,
            headless=True,
            suppress_resource_load_types=["image", "media", "font", "stylesheet"],
            browser="webkit",
        )
        print(f"{'#':>3}  {'views':>12}  {'likes':>10}  creator            desc")
        print("-" * 100)
        i = 0
        async for video in api.trending.videos(count=COUNT):
            i += 1
            d = video.as_dict
            stats = d.get("stats", {}) or d.get("statsV2", {})
            views = int(stats.get("playCount", 0) or 0)
            likes = int(stats.get("diggCount", 0) or 0)
            author = (d.get("author") or {}).get("uniqueId", "?")
            desc = (d.get("desc") or "").replace("\n", " ")[:50]
            vid = d.get("id", "?")
            url = f"https://www.tiktok.com/@{author}/video/{vid}"
            print(f"{i:>3}  {views:>12,}  {likes:>10,}  @{author:<17}  {desc}")
            print(f"     {url}")


if __name__ == "__main__":
    asyncio.run(main())
