from dotenv import load_dotenv
from fastapi import APIRouter
from googleapiclient.discovery import build
import asyncio
import time
import json
import os
import logging

load_dotenv()

search_youtube = APIRouter()
logging.getLogger("google").setLevel(logging.ERROR)


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY, cache_discovery=False)

async def search_youtube_(query: str, max_results: int = 10):
    # Bu blocking funksiyadir — uni background threadda ishlatamiz
    def blocking_search():
        request = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=max_results,
            type="video"
        )
        return request.execute()

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, blocking_search)

    results = []
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        results.append({
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })
    return results


async def get_audio_url(video_url: str):
    cmd = [
        "yt-dlp",
        "--simulate",
        "--skip-download",
        "-j",
        "-f",
        "bestaudio[ext=m4a]",
        video_url
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )
    stdout, _ = await proc.communicate()
    if stdout:
        data = json.loads(stdout.decode())
        return {"title": data.get("title"), "download_url": data.get("url")}
    return {"title": None, "download_url": None}


@search_youtube.get("/search")
async def search(query: str, max_results: int = 10):
    start_time = time.time()

    # 1. Search qilishni background threadda bajaramiz
    search_results = await search_youtube_(query, max_results)

    # 2. Har bir natija uchun paralel yt-dlp ishlatamiz
    tasks = [get_audio_url(item["url"]) for item in search_results]
    audio_links = await asyncio.gather(*tasks)

    print("⏱️ Finished in:", round(time.time() - start_time, 2), "seconds")
    return {"results": audio_links}