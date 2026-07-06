import asyncio
import json
from TikTokApi import TikTokApi


async def main():
    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            sleep_after=3,
            headless=True,
            suppress_resource_load_types=["image", "media", "font", "stylesheet"],
            browser="webkit",
        )
        async for video in api.trending.videos(count=1):
            print(json.dumps(video.as_dict, indent=2, default=str))
            break


if __name__ == "__main__":
    asyncio.run(main())
