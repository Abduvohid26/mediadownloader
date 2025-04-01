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
from typing import Any

async def _get_data(data: dict[str, Any], video_url: str) -> dict[str, Any]:
    return {
        "error": False,
        "url": video_url,
        "source": "youtube",
        "title": data.get("title"),
        "thumbnail": data.get("thumbnail"),
        "duration": data.get("duration"),
        "medias": [
            {
                "type": m.get("type"),
                "ext": m.get("extension"),
                "is_audio": m.get("is_audio"),
                "quality": m.get("quality"),
                "url": m.get("url"),
            }
            for m in data.get("medias", [])
        ]
    }

async def get_yt_data(video_url: str) -> dict[str, Any]:
    try:
        url = "https://www.clipto.com/api/youtube"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"url": video_url})

        if response.status_code != 200:
            print(f"Xatolik Yuz berdi, {response.status_code}")
            return {"error": True, "message": "Invalid response from the server"}

        try:
            response_data = response.json()
        except Exception as e:
            print(f"Xatolik Yuz berdi: {e}")
            return {"error": True, "message": "Invalid response from the server"}

        return await _get_data(response_data, video_url)

    except httpx.HTTPError as e:
        print(f"HTTP xatosi: {e}")
        return {"error": True, "message": "Invalid response from the server"}

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return {"error": True, "message": "Invalid response from the server"}

