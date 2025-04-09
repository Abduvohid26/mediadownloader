import asyncio
from typing import Any

from playwright.async_api import async_playwright
import yt_dlp

# async def _get_data(data: dict, thumb_data: dict, url: str) -> dict:
#     """YouTube videoning yuklab olish ma'lumotlarini formatlaydi"""
#     return {
#         "error": False,
#         "url": url,
#         "source": "youtube",
#         "title": data.get("meta", {}).get("title", "Unknown"),
#         "thumbnail": thumb_data.get("thumbnail", ""),
#         "duration": data.get("meta", {}).get("duration", 0),
#         "media": [
#             {
#                 "type": entry.get("type"),
#                 "ext": entry.get("ext"),
#                 "quality": entry.get("quality"),
#                 "filesize": entry.get("filesize"),
#                 "is_audio": entry.get("audio"),
#                 "no_audio": entry.get("no_audio"),
#                 "url": entry.get("url"),
#             }
#             for entry in data.get("url", []) 
#         ]
#     }

# async def get_ssyoutube_download_url(video_url: str):
#     """YouTube video yuklab olish uchun ma'lumotlarni qaytaradi"""
#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(headless=False)
#             page = await browser.new_page()

#             # SSYouTube saytiga kirish
#             # await page.goto("https://ssyoutube.com/en798Df/")
#             await page.goto("https://www.clipto.com/media-downloader/youtube-downloader")
#             await page.fill(".text-black", video_url)
            
#             # await page.click("div.input-wrapper button[type='button']")
#             await page.click("button.form-btn.btn-primary")
#             # await page.click("//button[contains(@class, 'btn-primary')]")


#             async with page.expect_response(lambda response: True) as response_info:
#                 response = await response_info.value
#                 response_text = await response.text()  # JSON emas, oddiy matn shaklida o‘qiymiz
#                 print(response_text)  # Serverdan nima kelayotganini tekshiramiz

        
#             print(await response.json())
#             with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
#                 info = ydl.extract_info(video_url, download=False)

#             response_data = await response.json()
#             print(response_data)
#             result = await _get_data(response_data, info, video_url)

#             await browser.close()
#             return result

#     except Exception as e:
#         print(f"Xatolik yuz berdi: {e}")
#         return {"error": True, "message": "Invalid response from the server"}

# video_url = "https://youtu.be/eJuqhhn6-EE?si=--MemPi_VnpFja7Z"
# download_url = asyncio.run(get_ssyoutube_download_url(video_url))
# print(f"Yuklab olish linki: {download_url}")


# async def _get_data(data: dict[str, Any], video_url: str) -> dict[str, Any]:
#     return {
#         "error": False,
#         "url": video_url,
#         "source": "youtube",
#         "title": data.get("title", None),
#         "thumbnail": data.get("thumbnail", None),
#         "duration": data.get("duration", None),
#         "medias": [
#             {
#                 "type": m.get("type", None),
#                 "ext": m.get("extension", None),
#                 "is_audio": m.get("is_audio", None),
#                 "quality": m.get("quality", None),
#                 "url": m.get("url", None),
#             }
#             for m in data.get("medias", [])
#         ]
#
#     }
#
# import httpx
# async def get_yt_data(video_url: str):
#     try:
#         url = "https://www.clipto.com/api/youtube"
#
#         async with httpx.AsyncClient() as client:
#             response = await client.post(url, json={"url": video_url})
#
#         response_data = response.json()
#         return response_data
#
#     except Exception as e:
#         print(f"Xatolik yuz berdi: {e}")
#         return {"error": True, "message": "Invalid response from the server"}


# print(asyncio.run(get_yt_data("https://youtu.be/eJuqhhn6-EE?si=--MemPi_VnpFja7Z")))
import httpx

from .proxy_route import get_proxy_config
from .cashe import redis_client
import os


# async def _get_data(data, video_url: str):
#     PROXY_URL = await get_proxy_config()
#     token = None
#     if PROXY_URL:
#         token = os.urandom(16).hex()
#         proxy_url = f"http://{PROXY_URL['username']}:{PROXY_URL['password']}@{PROXY_URL['server'].replace('http://', '')}"
#         redis_client.set(token, proxy_url, ex=60 * 60)
#         print(redis_client.get(token).decode(), "token value")
#     else:
#         pass
#     formatted_data = {
#         "error": False,
#         "url": video_url,
#         "source": "youtube",
#         "title": data.get("title", ""),
#         "thumbnail": data.get("thumbnail", ""),
#         "duration": data.get("duration", ""),
#         "proxy_token": token,
#         "medias": [
#             {
#                 "type": m.get("type", ""),
#                 "ext": m.get("extension", ""),
#                 "is_audio": m.get("is_audio", False),
#                 "quality": m.get("quality", ""),
#                 "url": m.get("url", ""),
#             }
#             for m in data.get("medias", [])
#         ]
#     }
#     return formatted_data


# async def get_yt_data(video_url: str):
#     try:
#         url = "https://www.clipto.com/api/youtube"

#         async with httpx.AsyncClient() as client:
#             response = await client.post(url, json={"url": video_url})

#         if response.status_code != 200:
#             print(f"Xatolik yuz berdi, {response.status_code}")
#             return {"error": True, "message": "Invalid response from the server"}

#         try:
#             response_data = response.json()
#         except ValueError as e:  # Maxsus exception turi
#             print(f"JSON decode xatosi: {e}, Response content: {response.text}")
#             return {"error": True, "message": "Invalid JSON response"}

#         data = await _get_data(response_data, video_url)
#         return data  # Debug qismini olib tashlash

#     except httpx.HTTPError as e:
#         print(f"HTTP xatosi: {e}")
#         return {"error": True, "message": f"HTTP error: {str(e)}"}

#     except Exception as e:
#         print(f"Kutilmagan xatolik: {e}")
#         return {"error": True, "message": "Internal server error"}



async def get_video(info, url):
    PROXY_URL = await get_proxy_config()
    token = None
    if PROXY_URL:
        token = os.urandom(16).hex()
        proxy_url = f"http://{PROXY_URL['username']}:{PROXY_URL['password']}@{PROXY_URL['server'].replace('http://', '')}"
        redis_client.set(token, proxy_url, ex=60 * 60)
        print(redis_client.get(token).decode(), "token value")
    else:
        pass

    formats = info.get("formats", [])

    audio_data = next((f for f in formats if f.get("url", "").startswith("https://r") and "audio" in f.get("format", "").lower()), None)

    new_datas = [f for f in formats if f.get("url", "").startswith("https://r")]

    medias = [
        {
            "quality": f"mp4 {info.get('format', '').split(' ')[-1]}",
            "video_ext": "mp4",
            "audio_ext": "m4a" if audio_data else None,
            "video_url": info.get("url"),
            "audio_url": audio_data["url"] if audio_data else None,
        }
    ]

    new_data = [
        {
            "quality": f"{data.get('format', '').split(' ')[-1]}",
            "video_ext": "mp4" if data.get("ext") == "mp4" else None,
            "audio_ext": data.get("ext") if data.get("ext") in ["webm", "m4a"] else None,
            "video_url": data.get("url") if data.get("ext") == "mp4" else None,
            "audio_url": data.get("url") if data.get("ext") in ["webm", "m4a"] else None
        }
        for data in new_datas
    ]

    medias.extend(new_data)
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
    PROXY_URL = await get_proxy_config()
    if PROXY_URL:
        ydl_opts["proxy"] = f"http://{PROXY_URL['username']}:{PROXY_URL['password']}@{PROXY_URL['server'].replace('http://', '')}"

    loop = asyncio.get_running_loop()
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            
            data = await get_video(info, url)
            return data
    except Exception as e:
        print(f"Xatolik Yuz berdi: {e}")
        return {"error": True, "message": "Invalid response from the server"}
    