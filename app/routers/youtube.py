import asyncio
import time

from playwright.async_api import async_playwright
import yt_dlp
import httpx
from .proxy_route import get_proxy_config, proxy_off
from .cashe import redis_client
import os
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import redis
#######################################################################

# async def get_video(info, url, proxy_url=None):
#     proxy_config = await get_proxy_config()
#     token = os.urandom(16).hex() if proxy_config else None
#     redis_client.set(token, proxy_url)
#     formats = info.get("formats", [])
#
#     medias = [{
#         "quality": f"{info.get('format', '').split(' ')[-1]}",
#         "type": "video",
#         "ext": "mp4",
#         "url": info.get("url")
#     }]
#
#     medias.extend([
#         {
#             "quality": f"{data.get('format', '').split()[-1]}",
#             "type": "video" if data.get("ext") == "mp4" else "audio",
#             "ext": data.get("ext"),
#             "url": data.get("url")
#         }
#         for data in formats if data.get("url") and data.get("ext") in ["mp4", "m4a", "webm"]
#     ])
#
#     thumbnail = info.get("thumbnail", "")
#
#     if not thumbnail.endswith(".jpg") and "thumbnails" in info:
#         for thumb in reversed(info["thumbnails"]):
#             if thumb.get("url", "").endswith(".jpg"):
#                 thumbnail = thumb["url"]
#                 break
#
#     return {
#         "error": False,
#         "hosting": "youtube",
#         "url": url,
#         "title": info.get("title"),
#         "thumbnail": thumbnail,
#         "duration": info.get("duration"),
#         "token": token,
#         "medias": medias
#     }
#
# import asyncio
# import yt_dlp
#
# async def get_yt_data(url: str):
#
#     ydl_opts = {
#         "quiet": True,
#         "no_warnings": True,
#         "format": "best[ext=mp4]",
#         "noplaylist": True,
#         "skip_download": True,
#         "n_connections": 4,  # Bir nechta parallel ulanishlar
#         "socket-timeout": 30,  # Tarmoq kutish vaqti
#         "retries": 10,  # Qayta urinishlar
#     }
#
#     proxy_config = await get_proxy_config()
#     proxy_url = None
#     if proxy_config:
#         proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
#         ydl_opts["proxy"] = proxy_url
#
#     loop = asyncio.get_running_loop()
#     curr_time = time.time()
#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = await asyncio.to_thread(lambda: ydl.extract_info(url, download=False))
#             data = await get_video(info, url, proxy_url)
#             print(time.time() - curr_time, "seconds")
#             return data
#     except yt_dlp.utils.ExtractorError as e:
#         error_msg = str(e)
#         if "Sign in to confirm you’re not a bot" in error_msg:
#             await proxy_off(proxy_ip=proxy_config["server"], action="youtube")
#             return await get_yt_data(url)
#         return {"error": True, "message": "Invalid response from the server"}
#     except Exception as e:
#         print(f"Xatolik yuz berdi: {e}")
#         return {"error": True, "message": "Invalid response from the server"}


##################################################################################
# Video ma'lumotlarini olish
from typing import Dict, Optional, List, Any
import traceback
async def get_video(info: Dict, url: str, proxy_url: Optional[str] = None) -> Dict:
    """
    YouTube video ma'lumotlarini strukturali formatga keltirib, xatoliklarni loglaydi.
    """
    try:
        # Agar proxy mavjud bo'lsa token hosil qilamiz va redisga yozamiz
        token = os.urandom(16).hex() if proxy_url else None
        if token and proxy_url:
            redis_client.set(token, proxy_url)

        # Asosiy video URL-ni olish
        main_url = info.get("url")
        if not main_url:
            raise ValueError("No URL found in video info")

        medias: List[Dict] = [{
            "quality": f"{info.get('format', 'unknown').split(' ')[-1]}",
            "type": "video",
            "ext": "mp4",
            "url": main_url
        }]

        # Qo'shimcha formatlarni qayta ishlash
        for data in info.get("formats", []):
            try:
                if data.get("url") and data.get("ext") in ["mp4", "m4a", "webm"]:
                    medias.append({
                        "quality": f"{data.get('format', 'unknown').split()[-1]}",
                        "type": "video" if data.get("ext") == "mp4" else "audio",
                        "ext": data.get("ext"),
                        "url": data.get("url")
                    })
            except Exception:
                logging.exception(f"Error processing format {data.get('format_id')}")

        # Thumbnail tanlash: qoniqarli o'lchamga ega bo'lganini tanlaymiz
        thumbnail = None
        for thumb in reversed(info.get("thumbnails", [])):
            try:
                if (thumb.get("url", "").endswith((".jpg")) and
                        (thumb.get("width", 0) >= 336 or thumb.get("height", 0) >= 188)):
                    thumbnail = thumb["url"]
                    break
            except Exception as e:
                logging.exception("Error processing thumbnail:")
                continue

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
        error_details = str(e) or "No error details provided"
        return {
            "error": True,
            "message": f"Video processing failed: {error_details}",
            "traceback": traceback.format_exc() or "No traceback available",
            "original_info": info
        }


async def get_yt_data(url: str) -> Dict:
    """
    YouTube video ma'lumotlarini olish: xatoliklarni kuzatish va qayta urinish mexanizmi bilan.
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best[ext=mp4]",
        "noplaylist": True,
        "skip_download": True,
        "n_connections": 4,
        "socket_timeout": 30,
        "retries": 2,
    }

    retry_count = 0
    max_retries = 2
    last_exception = None

    while retry_count <= max_retries:
        proxy_config = None
        proxy_url = None
        try:
            # Har urinishdan oldin yangi proxy ma'lumotlarini olish
            proxy_config = await get_proxy_config()
            if proxy_config:
                proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
                ydl_opts["proxy"] = proxy_url
                logging.info(f"Proxy configured: {proxy_url[:15]}...")

            logging.info(f"Attempt {retry_count + 1} of {max_retries + 1}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(lambda: ydl.extract_info(url, download=False))
                if not info:
                    raise ValueError("Empty response from YouTube API")
                logging.info("Good request")
                return await get_video(info, url, proxy_url)

        except yt_dlp.utils.ExtractorError as e:
            last_exception = e
            error_msg = str(e) or "No error details provided"
            logging.error(f"Extractor Error [{retry_count}]: {error_msg}")

            # Agar xatolik "Sign in to confirm you're not a bot", "blocked it in your country"
            # yoki "This video is unavailable" bo'lsa, proxy almashtirishni urinamiz
            if any(msg in error_msg for msg in [
                "Sign in to confirm you're not a bot",
                "blocked it in your country",
                "This video is unavailable"
            ]):
                if proxy_config:
                    logging.info("Rotating proxy due to restriction...")
                    await proxy_off(proxy_ip=proxy_config["server"], action="youtube")
                retry_count += 1
                continue

            return {
                "error": True,
                "message": "Content extraction failed",
                "type": "ExtractorError",
                "details": error_msg,
                "traceback": traceback.format_exc() or "No traceback available"
            }

        except yt_dlp.utils.DownloadError as e:
            last_exception = e
            error_msg = str(e) or "No error details provided"
            logging.error(f"Download Error [{retry_count}]: {error_msg}")
            if "Too Many Requests" in error_msg:
                logging.info("Rotating proxy due to rate limiting...")
                await proxy_off(proxy_ip=proxy_config["server"], action="youtube")
                retry_count += 1
                continue

            return {
                "error": True,
                "message": "Download failed",
                "type": "DownloadError",
                "details": error_msg,
                "traceback": traceback.format_exc() or "No traceback available"
            }

        except Exception as e:
            last_exception = e
            error_msg = str(e) or "No error details provided"
            logging.error(f"Unexpected Error [{retry_count}]: {error_msg}")
            logging.exception("Stack trace:")
            retry_count += 1
            continue

    # Agar barcha urinishlar muvaffaqiyatsiz tugasa
    final_error = str(last_exception) or "No error details provided"
    return {
        "error": True,
        "message": "Max retries exceeded",
        "last_exception": final_error,
        "traceback": traceback.format_exc() or "No traceback available",
        "retries": retry_count
    }
##################################################################################
# async def get_yt_data(url: str):
#
#     ydl_opts = {
#         "quiet": True,
#         "no_warnings": True,
#         "format": "best[ext=mp4]",
#         "noplaylist": True,
#         "skip_download": True,
#     }
#
#     proxy_config = await get_proxy_config()
#     proxy_url = None
#     if proxy_config:
#         proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
#         ydl_opts["proxy"] = proxy_url
#
#     loop = asyncio.get_running_loop()
#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = await asyncio.to_thread(lambda: ydl.extract_info(url, download=False))
#             print(info, "Data")
#             data = await get_video(info, url, proxy_url)
#             return data
#     except yt_dlp.utils.ExtractorError as e:
#         error_msg = str(e)
#         if "Sign in to confirm you’re not a bot" in error_msg:
#             await proxy_off(proxy_ip=proxy_config["server"], action="youtube")
#             return await get_yt_data(url)
#         return {"error": True, "message": "Invalid response from the server"}
#     except Exception as e:
#         print(f"Xatolik yuz berdi: {e}")
#         return {"error": True, "message": "Invalid response from the server"}
#


# async def get_youtube_video_info(url: str):
#     proxy = await get_proxy_config()
#     #
#     def extract_info():
#         options = {
#             'quiet': True,
#             'extract_flat': False,
#         }
#         # if proxy:
#         #     options['proxy'] = f"http://{proxy['username']}:{proxy['password']}@{proxy['server'].replace('http://', '')}"
#         with yt_dlp.YoutubeDL(options) as ydl:
#             return ydl.extract_info(url, download=False)
#
#     loop = asyncio.get_event_loop()
#     video_info = await loop.run_in_executor(None, extract_info)
#
#     return video_info

# async def get_youtube_video_info(url):
#     loop = asyncio.get_running_loop()
#     proxy_config = await get_proxy_config()
#     try:
#         # Async wrapper for yt-dlp extraction
#         async def extract_info():
#             def sync_extract():
#                 ydl_opts = {
#                     "quiet": True,
#                     "no_warnings": True,
#                     "format": "best[ext=mp4]",
#                     "noplaylist": True,
#                 }
#                 if proxy_config:
#                     proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
#                     ydl_opts['proxy'] = proxy_url
#
#                 with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                     return ydl.extract_info(url, download=False)
#
#             return await loop.run_in_executor(None, sync_extract)
#
#         info = await extract_info()
#         return info.get("url")
#     except Exception as e:
#         print(f"Error: {e}")
#         return {"error": True, "message": f"Invalid response from the server: {e}"}
#


async def get_youtube_video_info(url):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best[ext=mp4]",
        "noplaylist": True,
        "skip_download": True,
        "n_connections": 4,
        "socket_timeout": 30,
        "retries": 2,
    }
    try:
        loop = asyncio.get_running_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        return info
    except Exception as e:
        print(f"Error: {e}")
        return {"error": True, "message": f"Invalid response from the server: {e}"}

