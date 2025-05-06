import yt_dlp
import typing
import asyncio

import yt_dlp
import typing
import asyncio

AUDIO_DIRECT_OPTIONS = {
    "quiet": True,
    "noprogress": True,
    "no_warnings": True,
    "skip_download": True,
    "extract_flat": False,  # kerak, aks holda linklar olinmaydi
    "no_playlist": True,
    "format": "bestaudio[ext=m4a]"  # eng yaxshi audio
}

def _extract_audio_info(entry):
    return {
        "title": entry.get("title"),
        "duration": entry.get("duration"),
        "webpage_url": entry.get("webpage_url"),
        "direct_url": entry.get("url"),  # bu - direct audio link
    }

async def get_audio_direct_links(query: str, limit: int = 10, proxy: typing.Optional[str] = None):
    query += " music"
    options = dict(AUDIO_DIRECT_OPTIONS)
    if proxy:
        options["proxy"] = proxy

    with yt_dlp.YoutubeDL(options) as ydl:
        search_results = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        entries = search_results.get("entries", [])[:limit]
        return [_extract_audio_info(entry) for entry in entries]

# import time
# async def main():
#     curr = time.time()
#     results = await get_audio_direct_links("shoxrux rep", 10)
#     for r in results:
#         print(f"{r['title']} — {r['direct_url']}")
#     print("Spend time", time.time() - curr)
# asyncio.run(main())