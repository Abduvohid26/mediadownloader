import asyncio
import traceback
import asyncio
import json
import os
import re
import logging
from playwright.async_api import async_playwright
from typing import Dict, Optional, List, Any
from .proxy_route import get_proxy_config, proxy_off
from .cashe import redis_client




logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



async def get_video_and_audio_formats(formats: List[Dict]) -> Dict[str, Dict]:
    """
    480p va undan yuqori video + eng yaxshi audio formatlarini qaytaradi.
    Xatoga chidamli: tbr/abr None bo‘lsa, 0 sifatida ishlaydi.
    """

    if not formats:
        raise ValueError("No formats found in video info")

    quality_map: Dict[str, Dict] = {}
    best_audio: Dict = {}

    for f in formats:
        height = f.get("height")
        vcodec = f.get("vcodec")
        acodec = f.get("acodec")

        if height and vcodec and vcodec != "none":
            if height >= 480:
                label = f"{height}p"
                cur_best = quality_map.get(label)
                cur_tbr = (cur_best or {}).get("tbr") or 0
                new_tbr = f.get("tbr") or 0
                if not cur_best or new_tbr > cur_tbr:
                    quality_map[label] = f

        elif (not height) and acodec and acodec != "none":
            cur_abr = (best_audio.get("abr") if best_audio else 0) or 0
            new_abr = f.get("abr") or 0
            if new_abr > cur_abr:
                best_audio = f

    if best_audio:
        quality_map["audio"] = best_audio

    def sort_key(item):
        label, _ = item
        return (label == "audio", int(label.rstrip("p")) if label != "audio" else 0)

    return dict(sorted(quality_map.items(), key=sort_key))




async def get_video(info: Dict, url: str, proxy_url: Optional[str] = None) -> Dict:
    """
    YouTube video ma'lumotlarini strukturali formatga keltirib, xatoliklarni loglaydi.
    """
    try:
        token = os.urandom(16).hex() if proxy_url else None
        if token and proxy_url:
            redis_client.set(token, proxy_url, ex=300)

        main_url = info.get("url")
        if not main_url:
            raise ValueError("No URL found in video info")

        quality = info.get("format", "unknown").split(' ')[-1].strip("()")

        medias: List[Dict] = [{
            "quality": quality,
            "type": "video",
            "ext": "mp4",
            "url": main_url
        }]

        video_audio_formats = await get_video_and_audio_formats(info.get("formats", []))

        for q, f in video_audio_formats.items():
            media_type = "video" if q != "audio" else "audio"
            medias.append({
                "quality": q if q != "audio" else "medium",
                "type": media_type,
                "ext": f.get("ext"),
                "url": f.get("url")
            })

        thumbnail = f"https://i.ytimg.com/vi/{info.get('id')}/sddefault.jpg"

        return {
            "error": False,
            "hosting": "youtube",
            "url": url,
            "title": info.get("title", "Unknown Title"),
            "thumbnail": thumbnail,
            "duration": info.get("duration", 0),
            "token": token,
            "medias": medias
        }

    except Exception as e:
        logging.exception("CRITICAL ERROR in get_video:")
        return {
            "error": True,
            "message": f"Video processing failed: {str(e) or 'No error details provided'}",
            "traceback": traceback.format_exc() or "No traceback available",
            "original_info": info
        }

async def get_yt_data(url: str) -> Dict:
    """
    YouTube video uchun proxy tayyorlash urinishlar sonini boshqarish 
    """
    retry_count = 0
    max_retries = 2
    last_exception = None

    while retry_count <= max_retries:
        proxy_config = None
        proxy_url = None

        try:
            proxy_config = await get_proxy_config()
            if proxy_config:
                proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
                logging.info(f"[Proxy] {proxy_url[:15]}...")

            logging.info(f"[Try] {retry_count + 1} of {max_retries + 1}")
            info = await run_yt_dlp(url, proxy_url)

            if info.get("error"):
                raise Exception(info["message"])

            return await get_video(info, url, proxy_url)

        except Exception as e:
            last_exception = e
            logging.error(f"[Error {retry_count}] {str(e)}")
            logging.exception("Stack trace:")

            if proxy_config:
                await proxy_off(proxy_ip=proxy_config["server"], action="youtube")

            retry_count += 1
            continue

    return {
        "error": True,
        "message": str(last_exception),
        "retries": retry_count
    }


async def run_yt_dlp(url: str, proxy_url: str = None) -> dict:
    cmd = [
    "yt-dlp",
    "-j",                      
    "--no-playlist",           
    "--no-warnings",           
    "--quiet",                 
    "--format", "best[ext=mp4]",
    "--geo-bypass",
    "--no-check-certificate",
    "--socket-timeout", "10"
]
    
    if proxy_url:
        cmd.append(f"--proxy={proxy_url}")

    cmd.append(url)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            return {
                "error": True,
                "message": stderr.decode().strip()
            }

        return json.loads(stdout.decode())

    except Exception as e:
        return {
            "error": True,
            "message": str(e)
        }
