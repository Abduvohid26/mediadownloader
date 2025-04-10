import asyncio
from playwright.async_api import async_playwright
import yt_dlp
import httpx
from .proxy_route import get_proxy_config
from .cashe import redis_client
import os

async def get_video(info, url):
    proxy_config = await get_proxy_config()
    token = None

    if proxy_config:
        token = os.urandom(16).hex()
        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
        redis_client.set(token, proxy_url, ex=60 * 60)
        print(redis_client.get(token).decode(), "token value")

    formats = info.get("formats", [])
    
    new_datas = [f for f in formats if f.get("url", "").startswith("https://r")]

    audio_data = next((f for f in new_datas if "audio" in f.get("format", "").lower()), None)

    medias = [{
        "quality": f"mp4 {info.get('format', '').split(' ')[-1]}",
        "video_ext": "mp4",
        "audio_ext": "m4a" if audio_data else None,
        "video_url": info.get("url"),
        "audio_url": audio_data["url"] if audio_data else None,
    }]

    for data in new_datas:
        ext = data.get("ext")
        medias.append({
            "quality": data.get("format", "").split(' ')[-1],
            "video_ext": "mp4" if ext == "mp4" else None,
            "audio_ext": ext if ext in ["webm", "m4a"] else None,
            "video_url": data.get("url") if ext == "mp4" else None,
            "audio_url": data.get("url") if ext in ["webm", "m4a"] else None,
        })

    thumbnails = info.get("thumbnails", [])
    thumbnail = next((thumb["url"] for thumb in reversed(thumbnails) if thumb["url"].endswith(".jpg")), None)

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
        "quit": False,
        "format": "best[ext=mp4]",
    }
    proxy_config = await get_proxy_config()
    if proxy_config:
        ydl_opts["proxy"] = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"

    loop = asyncio.get_running_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            data = await get_video(info, url)
            return data
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return {"error": True, "message": "Invalid response from the server"}