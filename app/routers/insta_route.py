from .insta import download_instagram_media, get_instagram_direct_links
from schema.schema import InstaSchema, InstaStory
from fastapi import APIRouter, HTTPException, Form, Depends, Request
# from .tiktok import get_video_album
from .proxy_route import get_db, get_proxy_config
from sqlalchemy.ext.asyncio import AsyncSession
from .cashe import generate_unique_id
from models.user import Download
import re

insta_router = APIRouter()

@insta_router.get("/instagram/media")
async def get_instagram_media(in_url: str, request: Request, db : AsyncSession = Depends(get_db)):
    url = in_url.strip()
    proxy_config = await get_proxy_config()
    if "stories" in url:
        data = await get_instagram_direct_links(url, db, request)
        return data
    elif "@" in url:
        data = await get_instagram_direct_links(url, db, request)
        return data
        
    media_urls = await download_instagram_media(url, proxy_config, db, request)

    if not media_urls:
        return {"error": True, "message": "Invalid response from the server."}

    return media_urls


    # url = in_url.strip()
    # context = request.app.state.context

    # try:
    #     page = await context.new_page()

    #     # Saytga kirish
    #     await page.goto("https://sssinstagram.com/ru/story-saver")

    #     # Username kiriting
    #     await page.fill(".form__input", url)
    #     await page.click(".form__submit")

    #     # Yuklab olish tugmasi chiqquncha kutish
    #     await page.wait_for_selector(".button__download", state="attached", timeout=25000)

    #     # Storylar uchun yuklab olish linklari
    #     story_elements = await page.locator(".button__download").all()
    #     story_links = [await el.get_attribute("href") for el in story_elements if await el.get_attribute("href")]

    #     # Thumbnaillar
    #     thumbnail_elements = await page.locator(".media-content__image").all()
    #     thumbnails = [await el.get_attribute("src") for el in thumbnail_elements if await el.get_attribute("src")]

    #     # Sarlavha
    #     title_elements = await page.locator(".output-list__caption p").all()
    #     titles = [await el.text_content() for el in title_elements]
    #     title = titles[0] if titles else None

    #     # Shortcode
    #     match = re.search(r'/p/([^/]+)/', url)
    #     shortcode = match.group(1) if match else "unknown"

    #     if not story_links:
    #         return {"error": True, "message": "Hech qanday media topilmadi."}

    #     def detect_type(url: str):
    #         return "image" if url.lower().endswith(".jpg") else "video"

    #     medias = []
    #     for idx, media_url in enumerate(story_links):
    #         # 1. Media URL uchun
    #         media_id = await generate_unique_id()
    #         media_download = Download(id=media_id, original_url=media_url)
    #         db.add(media_download)

    #         media_download_url = f"https://videoyukla.uz/download?id={media_id}"

    #         # 2. Thumbnail bo‘lsa, alohida saqlaymiz
    #         thumb_url = thumbnails[idx] if idx < len(thumbnails) else None
    #         thumb_download_url = None

    #         if thumb_url:
    #             thumb_id = await generate_unique_id()
    #             thumb_download = Download(id=thumb_id, original_url=thumb_url)
    #             db.add(thumb_download)
    #             thumb_download_url = f"https://videoyukla.uz/download?id={thumb_id}"

    #         medias.append({
    #             "type": detect_type(media_url),
    #             "download_url": media_download_url,
    #             "thumb": thumb_download_url
    #         })

    #     await db.commit()

    #     return {
    #         "error": False,
    #         "shortcode": shortcode,
    #         "hosting": "instagram",
    #         "type": "album" if len(story_links) > 1 else detect_type(story_links[0]),
    #         "url": url,
    #         "title": title,
    #         "medias": medias,
    #         "message": "this is urls 5 min active"
    #     }

    # except Exception as e:
    #     print(f"Xatolik yuz berdi: {e}")
    #     return {"error": True, "message": "Serverdan noto‘g‘ri javob oldik."}
    # return media_urls

@insta_router.post("/instagram/media/service/", include_in_schema=False)
async def get_media(request: Request, url: InstaSchema = Form(...), db : AsyncSession = Depends(get_db)):
    url = url.url.strip()
    proxy_config = await get_proxy_config()
    if "stories" in url:
        data = await get_instagram_direct_links(url, db, request)
        return data
    elif "@" in url:
        data = await get_instagram_direct_links(url, db, request)
        return data
        
    media_urls = await download_instagram_media(url, proxy_config, db, request)

    if not media_urls:
        return {"error": True, "message": "Invalid response from the server."}

    return media_urls