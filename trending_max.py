import asyncio
import os
from TikTokApi import TikTokApi

TARGET = int(os.environ.get("TARGET", "300"))


async def main():
    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1, sleep_after=3, headless=True,
            suppress_resource_load_types=["image", "media", "font", "stylesheet"],
            browser="webkit",
        )
        seen = set()
        total = 0
        stop = "generator finished (hasMore=false)"
        # track how unique-count grows to see where it plateaus
        milestones = {}
        try:
            async for v in api.trending.videos(count=TARGET):
                total += 1
                seen.add(v.as_dict.get("id"))
                if total % 20 == 0:
                    milestones[total] = len(seen)
        except Exception as e:
            stop = f"ERROR: {type(e).__name__}: {str(e)[:140]}"

        ids_out = os.environ.get("IDS_OUT")
        if ids_out:
            with open(ids_out, "w") as fh:
                fh.write("\n".join(sorted(x for x in seen if x)))
        print(f"requested up to : {TARGET}")
        print(f"total yielded   : {total}")
        print(f"UNIQUE videos   : {len(seen)}")
        print(f"stop reason     : {stop}")
        print("unique growth (yielded -> unique):")
        for k in sorted(milestones):
            print(f"   {k:>4} yielded -> {milestones[k]} unique")


if __name__ == "__main__":
    asyncio.run(main())
