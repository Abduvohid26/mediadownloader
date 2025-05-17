from dotenv import load_dotenv
from fastapi import APIRouter
from googleapiclient.discovery import build
from ..proxy_route import get_proxy_config
import asyncio
import time
import json
import os
import logging
import isodate
load_dotenv()

search_youtube = APIRouter()
logging.getLogger("google").setLevel(logging.ERROR)
MAX_RETRIES_GET_AUDIO_LINKS = 3


# YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_KEY = "AIzaSyDDKvKdCPHT3tA2XNpGjolWGSOGAVWGkEc"
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY, cache_discovery=False)
async def search_youtube_(query: str, max_results: int = 10):
    def blocking_search():
        request = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=40,
            type="video"
        )
        return request.execute()

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, blocking_search)

    video_ids = [item["id"]["videoId"] for item in response["items"]]

    # Endi videolar haqida to‘liq ma’lumotni olamiz
    def get_video_details():
        request = youtube.videos().list(
            part="contentDetails,snippet",
            id=",".join(video_ids)
        )
        return request.execute()

    video_details = await loop.run_in_executor(None, get_video_details)

    results = []
    for item in video_details["items"]:
        video_id = item["id"]
        duration_iso = item["contentDetails"]["duration"]
        duration_seconds = isodate.parse_duration(duration_iso).total_seconds()

        # Stream (live, premiere) emasligini tekshirish
        definition = item["contentDetails"].get("definition", "")
        live_broadcast_content = item["snippet"].get("liveBroadcastContent", "")

        # Shartlar:
        if (
            50 <= duration_seconds <= 600 and
            live_broadcast_content == "none"
        ):
            title = item["snippet"]["title"]
            results.append({
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "duration": int(duration_seconds)
            })

    return results[:max_results]



async def get_audio_url(video_url: str, proxy_url: str = None):
    cmd = [
        "yt-dlp",
        "--simulate",
        "--skip-download",
        "-j",
        "-f",
        "bestaudio[ext=m4a]",
        video_url
    ]
    if proxy_url:
        cmd.append(f"--proxy={proxy_url}")
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


async def get_audio_url_manage(video_url: str):
    retries = 0
    while retries < MAX_RETRIES_GET_AUDIO_LINKS:
        try:
            proxy_config = await get_proxy_config()
            proxy_url = None
            if proxy_config:
                proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
            result = await get_audio_url(video_url, proxy_url)
            if result:
                return result
        except Exception as e:
            print(f"Error fetching {video_url}: {e}")
        retries += 1
    return {"title": None, "download_url": None}

@search_youtube.get("/new/search/")
async def search(query: str, max_results: int = 10):
    start_time = time.time()
    
    search_results = await search_youtube_(f"{query} music", max_results)
    tasks = [get_audio_url_manage(item["url"]) for item in search_results]
    audio_links = await asyncio.gather(*tasks, return_exceptions=True)
    
    duration = round(time.time() - start_time, 2)
    print(f"⏱️ Finished in: {duration} seconds")
    
    results = []
    for idx, audio_url in enumerate(audio_links):
        # faqat audio_url mavjud va xato bo'lmasa, natijaga qo'shamiz
        if not isinstance(audio_url, Exception) and audio_url is not None:
            results.append({
                "title": search_results[idx]["title"],
                "audio_url": audio_url
            })
    
    return results