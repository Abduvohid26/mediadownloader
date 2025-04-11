import asyncio
from playwright.async_api import async_playwright
import yt_dlp
import httpx
from .proxy_route import get_proxy_config, proxy_off
from .cashe import redis_client
import os
import redis

async def get_video(info, url, proxy_url=None):
    proxy_config = await get_proxy_config()
    token = os.urandom(16).hex() if proxy_config else None
    redis_client.set(token, proxy_url)
    print(redis_client.get(token), "VALUES")
    formats = info.get("formats", [])

    # **Birinchi obyekt** — `info` ichidan olinadi
    medias = [{
        "quality": f"{info.get('format', '').split(' ')[-1]}",
        "type": "video",
        "ext": "mp4",
        "url": info.get("url")
    }]

    medias.extend([
        {
            "quality": f"{data.get('format', '').split()[-1]}",
            "type": "video" if data.get("ext") == "mp4" else "audio",
            "ext": data.get("ext"),
            "url": data.get("url")
        }
        for data in formats if data.get("url") and data.get("ext") in ["mp4", "m4a", "webm"]
    ])

    thumbnail = info.get("thumbnail", "")

    if not thumbnail.endswith(".jpg") and "thumbnails" in info:
        for thumb in reversed(info["thumbnails"]): 
            if thumb.get("url", "").endswith(".jpg"):
                thumbnail = thumb["url"]
                break   

    return {
        "error": False,
        "hosting": "youtube",
        "url": url,
        "title": info.get("title"),
        "thumbnail": thumbnail,
        "duration": info.get("duration"),
        "token": token,
        "medias": medias
    }

async def get_yt_data(url: str):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,  
        "format": "best[ext=mp4]",
        "noplaylist": True, 
    }

    proxy_config = await get_proxy_config()
    print(proxy_config)
    proxy_url = None
    if proxy_config:
        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
        ydl_opts["proxy"] = proxy_url

    loop = asyncio.get_running_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(lambda: ydl.extract_info(url, download=False)) 
            data = await get_video(info, url, proxy_url)
            return data
    except yt_dlp.utils.ExtractorError as e:
        error_msg = str(e)
        if "Sign in to confirm you’re not a bot" in error_msg:
            await proxy_off(proxy_ip=proxy_config["server"], action="youtube")
            return await get_yt_data(url)
        return {"error": True, "message": "Invalid response from the server"}
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return {"error": True, "message": "Invalid response from the server"}
    


async def get_youtube_video_info(url: str):
    proxy = await get_proxy_config()
    
    def extract_info():
        options = {
            'quiet': True,
            'proxy': proxy,
            'extract_flat': False,
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            return ydl.extract_info(url, download=False)

    loop = asyncio.get_event_loop()
    video_info = await loop.run_in_executor(None, extract_info)
    
    return video_info