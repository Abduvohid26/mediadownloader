import asyncio
from playwright.async_api import async_playwright
import yt_dlp
import httpx
from .proxy_route import get_proxy_config
from .cashe import redis_client
import os

async def get_video(info, url, proxy_url=None):
    # Proxy konfiguratsiyasini olish
    proxy_config = await get_proxy_config()
    token = None

    if proxy_config:
        token = os.urandom(16).hex()

    # Faqat "https://r" bilan boshlanadigan formatlarni olish
    formats = info.get("formats", [])
    new_datas = [f for f in formats if f.get("url", "").startswith("https://r")]

    # **Birinchi obyekt** — `info` ichidan olinadi
    medias = [{
        "quality": f"{info.get('format', '').split(' ')[-1]}",
        "type": "video",
        "ext": "mp4",
        "url": info.get("url")
    }]

    # **Qolgan obyektlar** — `formats` ichidan olinadi
    medias.extend([
        {
            "quality": f"{data.get('format', '').split()[-1]}",
            "type": "video" if data.get("ext") == "mp4" else "audio",
            "ext": data.get("ext"),
            "url": data.get("url")  # **`info.get("url")` emas!**
        }
        for data in new_datas
    ])

    return {
        "error": False,
        "hosting": "youtube",
        "url": url,
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),  # **`.get()` ishlatildi**
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
        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
        ydl_opts["proxy"] = proxy_url

    loop = asyncio.get_running_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            data = await get_video(info, url, proxy_url)
            return data
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return {"error": True, "message": "Invalid response from the server"}