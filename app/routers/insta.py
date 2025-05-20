import traceback
import logging
import yt_dlp
import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, async_playwright
from fastapi import FastAPI, Depends, Request
from .proxy_route import get_db
from .model import BrowserManager
from .proxy_route import get_proxy_config, proxy_off
import re
from playwright.async_api import async_playwright
from .cashe import generate_unique_id
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import Download
from .cashe import redis_client


class Example:
    pass


app = FastAPI()

logger = logging.getLogger(__name__)



async def get_instagram_direct_links(post_url: str, db, request):
    """Instagram hikoyalarini yuklab olish va linklarni saqlash funksiyasi."""
    click_info = request.app.state.click_info
    if click_info is True:
        return await get_instagram_direct_links_extra(post_url, db, request)
    page = None
    try:
        try:
            page = await asyncio.wait_for(request.app.state.page_pool.get(), timeout=10)
        except asyncio.TimeoutError:
            return {"error": True, "message": "Invalid response from the server."}

        max_retries = 2  # maksimal urinishlar soni
        for attempt in range(max_retries):
            await page.fill(".form__input", post_url)
            try:
                await page.click(".form__submit")
                await page.wait_for_selector(".button__download", state="attached", timeout=7000)
                break  
            except Exception as e:
                print(f"⚠️ 111111111111111111111111: {e}")
                error_message1 = await page.query_selector(".error-message__text")
                if error_message1:
                    error_data = error_message1.text_content()
                    logger.info(f"Xato: {error_data}")
                    if "@имя" in error_message1:
                        if attempt < max_retries - 1:  
                            logger.info("Xatolik aniqlangan, URL qayta kiritilmoqda...")
                            continue  
                        else:
                            print("Ikkinchi urinishdan so'ng xatolik mavjud.")
                            return {"error": True, "message": "Invalid response from the server"}
                    else:
                        pass
        title_elements = await page.locator(".output-list__caption p").all()
        titles = [await el.text_content() for el in title_elements]
        title = titles[0] if titles else None
        medias = []
        videos = await page.query_selector_all(".button__download")

        if videos:
            for video in videos:
                video_link = await video.get_attribute("href")
                if video_link:
                    media_id = await generate_unique_id()
                    redis_client.set(media_id, video_link, ex=3600)

                    download_url = f"https://fast.videoyukla.uz/download/instagram?id={media_id}"
                    # download_url = f"https://localhost:8000/download/instagram?id={media_id}"


                    if video_link.endswith((".webp", ".jpg", ".jpeg", ".png")):
                        media_type = "image"
                        thumb = download_url  
                    else:
                        media_type = "video"
                        thumb_el = await page.query_selector(".media-content__image")
                        if thumb_el:
                            thumb_link = await thumb_el.get_attribute("src")
                            thumb_id = await generate_unique_id()
                            redis_client.set(thumb_id, thumb_link, ex=3600)
                            thumb = f"https://fast.videoyukla.uz/download/instagram?id={thumb_id}"
                            # thumb = f"https://localhost:8000/download/instagram?id={thumb_id}"

                        else:
                            thumb = None

                    medias.append({
                        "type": media_type,
                        "download_url": download_url,
                        "thumb": thumb
                    })
        if not medias:
            print({"error": True, "message": "hech qanday media topilmadi"})
            return {"error": True, "message": "Invalid response from the server."}


        post_type = medias[0]["type"] if len(medias) == 1 else "album"

        return {
            "error": False,
            "hosting": "instagram",
            "type": post_type,
            "url": post_url,
            "title": title,
            "medias": medias,
        }


    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        return {"error": True, "message": "Serverdan noto‘g‘ri javob oldik."}

    finally:
        try:
            if page and not page.is_closed():
                error_message = await page.query_selector(".error-message")
                if error_message:
                    logger.warning("⚠️ Error message topildi, sahifa yopilyapti...")
                    await page.close()
                else:
                    await page.evaluate('document.querySelector(".form__input").value = ""')
                    await request.app.state.page_pool.put(page)
        except Exception as e:
            logger.warning(f"⚠️ Sahifani yopishda xatolik: {e}")
            if page and not page.is_closed():
                await page.close()




async def get_instagram_direct_links_extra(post_url: str, db, request):
    """Instagram hikoyalarini yuklab olish va linklarni saqlash funksiyasi."""
    page = None
    try:
        try:
            context = request.app.state.extra_context
            page = await context.new_page()
            await page.goto("https://sssinstagram.com/ru/story-saver", wait_until="load", timeout=7000)
        except Exception as e:
            print(f"Xatolik yuzb berdi: {e}")
            return {"error": True, "message": "Error response from the server."}

        max_retries = 2  
        for attempt in range(max_retries):
            await page.fill(".form__input", post_url)
            try:
                await page.click(".form__submit")
                await page.wait_for_selector(".button__download", state="attached", timeout=7000)
                break 
            except Exception as e:
                print(f"⚠️ 111111111111111111111111: {e}")
                error_message1 = await page.query_selector(".error-message__text")
                if error_message1:
                    error_data = error_message1.text_content()
                    logger.info(f"Xato: {error_data}")
                    if "@имя" in error_message1:
                        if attempt < max_retries - 1: 
                            logger.info("Xatolik aniqlangan, URL qayta kiritilmoqda...")
                            continue  
                        else:
                            print("Ikkinchi urinishdan so'ng xatolik mavjud.")
                            return {"error": True, "message": "Invalid response from the server"}
                    else:
                        pass
        title_elements = await page.locator(".output-list__caption p").all()
        titles = [await el.text_content() for el in title_elements]
        title = titles[0] if titles else None
        medias = []
        videos = await page.query_selector_all(".button__download")

        if videos:
            for video in videos:
                video_link = await video.get_attribute("href")
                if video_link:
                    media_id = await generate_unique_id()
                    redis_client.set(media_id, video_link, ex=3600)

                    download_url = f"https://fast.videoyukla.uz/download/instagram?id={media_id}"
                    # download_url = f"https://localhost:8000/download/instagram?id={media_id}"

                    if video_link.endswith((".webp", ".jpg", ".jpeg", ".png")):
                        media_type = "image"
                        thumb = download_url  
                    else:
                        media_type = "video"
                        thumb_el = await page.query_selector(".media-content__image")
                        if thumb_el:
                            thumb_link = await thumb_el.get_attribute("src")
                            thumb_id = await generate_unique_id()
                            redis_client.set(thumb_id, thumb_link, ex=3600)
                            thumb = f"https://fast.videoyukla.uz/download/instagram?id={thumb_id}"
                            # thumb = f"https://localhost:8000/download/instagram?id={thumb_id}"


                        else:
                            thumb = None

                    medias.append({
                        "type": media_type,
                        "download_url": download_url,
                        "thumb": thumb
                    })
        if not medias:
            print({"error": True, "message": "hech qanday media topilmadi"})
            return {"error": True, "message": "Invalid response from the server."}

        post_type = medias[0]["type"] if len(medias) == 1 else "album"
        match = re.search(r'/(?:p|reel|tv)/([A-Za-z0-9_-]+)', post_url)
        shortcode = match.group(1) if match else "unknown"
        return {
            "error": False,
            "shortcode": shortcode,
            "hosting": "instagram",
            "type": post_type,
            "url": post_url,
            "title": title,
            "medias": medias,
        }


    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        return {"error": True, "message": "Serverdan noto‘g‘ri javob oldik."}

    finally:
        if page:
            await page.close()


async def get_video(info, url):
    match = re.search(r'/(?:p|reel|tv)/([A-Za-z0-9_-]+)', url)
    shortcode = match.group(1) if match else "unknown"
    data = {
        "error": False,
        "shortcode": shortcode,
        "hosting": "instagram",
        "type": "video",
        "url": url,
        "title": info.get("title", ""),
        "medias": [
            {
                "type": "video",
                "download_url": next((item['url'] for item in info.get('formats', []) if list(item.keys())[0] == 'url'),None),
                "thumb": info.get("thumbnail")
            }
        ]
    }
    return data


async def get_video_album(info, url):
    match = re.search(r'/(?:p|reel|tv)/([A-Za-z0-9_-]+)', url)
    shortcode = match.group(1) if match else "unknown"
    data = {
        "error": False,
        "shortcode": shortcode,
        "hosting": "instagram",
        "type": "album",
        "url": url,
        "title": info.get("title", ""),
        "medias": [
            {
                "type": "video",
                "download_url": entry.get("url"),
                "thumb": entry.get("thumbnail")
            }
            for entry in info["entries"]
        ]
    }
    return data


async def download_instagram_media(url, proxy_config, db, request):
    loop = asyncio.get_running_loop()
    retry_count = 0
    max_retries = 3
    last_exception = None

    while retry_count <= max_retries:
        try:
            async def extract_info():
                def sync_extract():
                    options = {
                        'quiet': True,
                        'extract_flat': False,
                    }
                    # if proxy_config:
                    #     proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
                    #     options['proxy'] = proxy_url
                    with yt_dlp.YoutubeDL(options) as ydl:
                        return ydl.extract_info(url, download=False)
                return await loop.run_in_executor(None, sync_extract)

            info = await extract_info()

            if "entries" in info and len(info["entries"]) > 1:
                data = await get_video_album(info, url)
            elif "formats" in info:
                print("Get a video")
                data = await get_video(info, url)
            else:
                print("Get media1")
                data = await get_instagram_direct_links(
                    post_url=url,
                    db=db,
                    request=request
                )
            return data

        except yt_dlp.utils.ExtractorError as e:
            last_exception = e
            error_msg = str(e) or "No error details provided"
            logging.error(f"Extractor Error [{retry_count}]: {error_msg}")

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
            else:
                break  # Agar boshqa xatolik bo'lsa, retry qilmaymiz

        except yt_dlp.utils.DownloadError as e:
            error_message = str(e)

            if "There is no video in this post" in error_message:
                print("Get media2")
                return await get_instagram_direct_links(
                    post_url=url,
                    db=db,
                    request=request
                )
            print("DownloadError", error_message)
            return {"error": True, "message": "Invalid response from the server"}

        except Exception as e:
            print(f"Error downloading Instagram media: {str(e)}")
            print(traceback.format_exc())
            return {"error": True, "message": "Invalid response from the server"}

    return {"error": True, "message": "Failed to download media after retries", "details": str(last_exception)}

