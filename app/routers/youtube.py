import asyncio
import time

from playwright.async_api import async_playwright
import yt_dlp
import httpx
from .proxy_route import get_proxy_config, proxy_off
from .cashe import redis_client
import os
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
#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = await asyncio.to_thread(lambda: ydl.extract_info(url, download=False))
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


##################################################################################
async def get_video(info, url, proxy_url=None):
    proxy_config = await get_proxy_config()
    token = os.urandom(16).hex() if proxy_config else None
    redis_client.set(token, proxy_url)
    formats = info.get("formats", [])

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
        "skip_download": True,
        "n_connections": 4,  # Bir nechta parallel ulanishlar
        "socket-timeout": 30,  # Tarmoq kutish vaqti
        "retries": 2,  # Qayta urinishlar soni ikki martaga o'rnatilgan
    }

    proxy_config = await get_proxy_config()
    proxy_url = None
    retry_count = 0  # Urinishlar sonini hisoblash

    loop = asyncio.get_running_loop()
    while retry_count < 2:  # Ikki marta urinish
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(lambda: ydl.extract_info(url, download=False))
                data = await get_video(info, url, proxy_url)
                return data
        except yt_dlp.utils.ExtractorError as e:
            error_msg = str(e)
            if "Sign in to confirm you’re not a bot" in error_msg:
                # Proxyni faqat "Sign in to confirm you’re not a bot" xatosida ishlatish
                if proxy_config:
                    proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
                    ydl_opts["proxy"] = proxy_url  # Proxyni sozlash
                    await proxy_off(proxy_ip=proxy_config["server"], action="youtube")  # Proxyni o'chirish
                retry_count += 1  # Urinishlar sonini oshirish
            else:
                break  # Agar boshqa xatolik bo'lsa, qaytish
        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")
            break  # Boshqa xatolik yuzaga kelsa, chiqish

    return {"error": True, "message": "Invalid response from the server"}

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
    curr_t = time.time()
    proxy_config = await get_proxy_config()
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        # "format": "bestaudio[ext=m4a]/best[ext=mp4]",
        "extract_flat": True,
        "noplaylist": True,
        "match_filter": yt_dlp.utils.match_filter_func(
            "original_url!*=/shorts/ & url!*=/shorts/ & !is_live & live_status!=is_upcoming & availability=public & ext!*=m3u8 & ext!*=webm"
        ),
        "prefer_ffmpeg": True,
    }


    if proxy_config:
        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
        ydl_opts['proxy'] = proxy_url
    print(time.time() - curr_t, "Time")

    try:
        loop = asyncio.get_running_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        return info
    except Exception as e:
        print(f"Error: {e}")
        return {"error": True, "message": f"Invalid response from the server: {e}"}


