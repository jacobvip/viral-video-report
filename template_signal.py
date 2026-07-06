import asyncio
import os
import re
from collections import Counter
from TikTokApi import TikTokApi

SOUND_ID = os.environ.get("SOUND_ID", "7478404064235030545")
COUNT = int(os.environ.get("COUNT", "50"))
STOP = {"fyp", "fypシ", "foryou", "foryoupage", "viral", "viralvideo", "trending",
        "xyzbca", "zyxcba", "tiktok", "the", "this", "you", "for", "and", "with",
        "that", "your", "was", "are", "but", "not", "have", "get", "got"}

# origin-attribution patterns: how creators credit the format they're copying
IB_RE = re.compile(r"\b(?:ib|inspo|inspired\s*by|cred(?:it)?|dc)\b[:\s]*@?([A-Za-z0-9._]+)?", re.I)


def hashtags_of(d):
    tags = [(t.get("hashtagName") or "").lower().strip() for t in (d.get("textExtra") or [])]
    if not any(tags):
        tags = [w.lower() for w in re.findall(r"#(\w+)", d.get("desc") or "")]
    return [t for t in tags if t and t not in STOP]


def caption_words(d):
    txt = re.sub(r"#\w+|@[\w.]+", "", d.get("desc") or "").lower()
    return [w for w in re.findall(r"[a-z']{3,}", txt) if w not in STOP]


async def main():
    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1, sleep_after=3, headless=True,
            suppress_resource_load_types=["image", "media", "font", "stylesheet"],
            browser="webkit",
        )
        vids = []
        async for video in api.sound(id=SOUND_ID).videos(count=COUNT):
            vids.append(video.as_dict)

    n = len(vids)
    if n == 0:
        print("no videos returned"); return

    ib_targets = Counter()      # who is being credited as origin
    ib_count = 0                # how many videos credit anyone
    bigrams = Counter()
    tag_docs = Counter()
    for d in vids:
        desc = d.get("desc") or ""
        credited = set()
        for m in IB_RE.finditer(desc):
            # prefer an explicit @mention near the IB marker
            for mn in re.findall(r"@([\w.]+)", desc):
                credited.add(mn.lower())
        if re.search(r"\b(ib|inspired\s*by|inspo|cred|dc)\b", desc, re.I) and credited:
            ib_count += 1
            for c in credited:
                ib_targets[c] += 1
        ws = caption_words(d)
        for a, b in zip(ws, ws[1:]):
            bigrams[(a, b)] += 1
        for t in set(hashtags_of(d)):
            tag_docs[t] += 1

    print(f"SOUND {SOUND_ID} — {n} videos\n")

    print("ORIGIN ATTRIBUTION  (videos that credit an 'inspired-by' source):")
    print(f"  {ib_count}/{n} videos ({100*ib_count/n:.0f}%) cite an origin creator")
    for who, c in ib_targets.most_common(5):
        print(f"    @{who:<18} credited by {c} videos")

    print("\nREPEATED CAPTION PHRASES (2-grams appearing in >1 video):")
    for (a, b), c in bigrams.most_common(8):
        if c > 1:
            print(f"    \"{a} {b}\"  ×{c}")

    print("\nTOP HASHTAGS:")
    for t, c in tag_docs.most_common(6):
        print(f"    #{t:<18} {c}/{n}  {100*c/n:.0f}%")

    # composite template score: max of (origin-attribution rate, dominant hashtag coverage)
    origin_rate = ib_count / n
    dom_tag = (tag_docs.most_common(1)[0][1] / n) if tag_docs else 0
    score = max(origin_rate, dom_tag)
    print(f"\nTEMPLATE SCORE: {100*score:.0f}%  "
          f"(origin-attribution {100*origin_rate:.0f}% | dominant-hashtag {100*dom_tag:.0f}%)")
    print("VERDICT:", "TEMPLATE — creators are copying a defined format"
          if score >= 0.3 else "GENERIC SOUND — no shared format signature")

    if ib_targets:
        origin = ib_targets.most_common(1)[0][0]
        print(f"\nLIKELY ORIGIN OF THE TREND: @{origin}")
        print("Videos copying it:")
        for d in vids:
            if origin in (d.get("desc") or "").lower():
                a = (d.get("author") or {}).get("uniqueId", "?")
                vid = d.get("id", "?")
                print(f"    https://www.tiktok.com/@{a}/video/{vid}")


if __name__ == "__main__":
    asyncio.run(main())
