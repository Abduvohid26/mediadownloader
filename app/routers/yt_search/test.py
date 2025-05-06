import yt_dlp
import asyncio
import typing

AUDIO_DIRECT_OPTIONS = {
    "quiet": True,
    "noprogress": True,
    "no_warnings": True,
    "skip_download": True,
    "extract_flat": False,  # real media link olish
    "no_playlist": True,
    "format": "bestaudio[ext=m4a]",  # eng yaxshi audio format
}

def _extract_audio_info(entry):
    return {
        "title": entry.get("title"),
        "direct_url": entry.get("url"),  # Audio faylning direct linki
    }

# Asinxron video qidirish
async def extract_audio(query: str, proxy: typing.Optional[str] = None):
    options = dict(AUDIO_DIRECT_OPTIONS)
    if proxy:
        options["proxy"] = proxy
    with yt_dlp.YoutubeDL(options) as ydl:
        result = ydl.extract_info(query, download=False)
        return _extract_audio_info(result)

# Asinxron parallel qidiruv
async def fast_parallel_links(query: str, limit=10):    
    with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "skip_download": True}) as ydl:
        search_results = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        
        # URL ni to'g'ri formatda olish
        urls = [entry["url"] for entry in search_results["entries"][:limit]]
    
    # Har bir video uchun parallel ravishda link olish
    tasks = [extract_audio(url) for url in urls]
    return await asyncio.gather(*tasks)
import time
# Asinxron ishga tushurish
async def main():
    curr_time = time.time()
    results = await fast_parallel_links("shoxrux rep", limit=10)  # 10 ta result
    for res in results:
        print(f"{res['title']} — {res['direct_url']}")
    print("time", time.time() - curr_time)
# Asinxron ishni boshqarish
# asyncio.run(main())
