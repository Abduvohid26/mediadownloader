import traceback
import logging
import yt_dlp
import asyncio
from .cashe import redis_client

from urllib.parse import urlparse
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright
import pickle
from fastapi import FastAPI
import json
import gc
import diskcache

gc.disable()

app = FastAPI()

logger = logging.getLogger(__name__)

global_browser = {
    "browser": None,
    "context": None,
    "page": None,
    "playwright": None
}

async def init_browser(proxy_config=None):
    """ Brauzerni, contextni va sahifani oldindan ochib qo‘yish """
    if global_browser["browser"] is None:
        print("🔄 Yangi brauzer ishga tushdi...")
        global_browser["playwright"] = await async_playwright().start()

        options = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-setuid-sandbox"]
        }
        if proxy_config:
            options["proxy"] = proxy_config

        global_browser["browser"] = await global_browser["playwright"].chromium.launch(**options)
        global_browser["context"] = await global_browser["browser"].new_context()
        global_browser["page"] = await global_browser["context"].new_page()

        await global_browser["page"].goto("https://sssinstagram.com/ru/story-saver", timeout=10000)
        await global_browser["page"].wait_for_load_state("domcontentloaded")
    print(global_browser["browser"],
            global_browser["context"],
            global_browser["page"],
            global_browser["playwright"])
    return (global_browser["browser"],
            global_browser["context"],
            global_browser["page"],
            global_browser["playwright"])

async def close_browser():
    """ Brauzerni yopish """
    if global_browser["browser"]:
        await global_browser["browser"].close()
        global_browser["browser"] = None
    if global_browser["playwright"]:
        await global_browser["playwright"].stop()
        global_browser["playwright"] = None


async def browser_keepalive(proxy_config, interval=600):
    """ 🔄 Har `interval` sekundda brauzerni qayta ishga tushiradi """
    while True:
        await asyncio.sleep(interval)
        await close_browser()
        await init_browser(proxy_config)


async def get_instagram_story_urls(username, proxy_config):
    """ Instagram storylarini olish """
    try:
        browser, context, page, _ = await init_browser(proxy_config)

        await page.fill(".form__input", username)
        await page.click(".form__submit")

        await page.wait_for_selector(".button__download", timeout=5000)

        story_links = [await el.get_attribute("href") for el in await page.locator(".button__download").all()]
        print(len(story_links), 'len')
        if not story_links:
            return {"error": True, "message": "Invalid response from the server"}

        return {
            "error": False,
            "hosting": "instagram",
            "type": "stories",
            "username": username,
            "medias": [{"download_url": url, "type": "video" if url.lower().endswith(".mp4") else "image"} for url in story_links]
        }
    except Exception as e:
        return {"error": True, "message": f"Error: {e}"}

async def get_video(info):
    print(info)
    data = {
        "error": False,
        "hosting": "instagram",
        "type": "video",
        "title": info.get("title", None),
        "shortcode": info.get("id", None),
        "caption": info.get("description", None),
        "thumbnail": info["thumbnails"][-1]["url"] if "thumbnails" in info else None,
        "download_url": next((item['url'] for item in info.get('formats', []) if list(item.keys())[0] == 'url'), None)
    }
    return data


async def get_video_album(info):
    data = {
        "error": False,
        "type": "album",
        "shortcode": info["id"],
        "caption": info.get("description", ""),
        "medias": [
            {
                "download_url": entry["url"],
                "thumbnail": entry["thumbnail"],
                "type": "video"
            }
            for entry in info["entries"]
        ]
    }
    return data




async def get_instagram_post_images(post_url, caption, proxy_config):
    """
    Instagram postidagi barcha rasm URLlarini olish (albumlarni ham to'liq yuklash)

    Args:
        post_url (str): Instagram post linki

    Returns:
        dict: Instagram postidagi barcha rasm URLlari va qo‘shimcha ma‘lumotlar
    """
    try:
        browser, context, page, _ = await init_browser(proxy_config)
        try:
            page = await context.new_page()
        except Exception as e:
            logger.error(msg=f"Page yaratishda xatolik:: {e}")
            return {"error": True, "message": "Invalid response from the server"}

        try:
            await page.goto(post_url, timeout=15000)
        except PlaywrightTimeoutError:
            logger.error(msg=f"⏳ Sahifani yuklash muddati tugadi")
            return {"error": True, "message": "Invalid response from the server"}

        path = urlparse(post_url).path
        shortcode = path.strip("/").split("/")[-1]

        try:
            await page.wait_for_selector("article", timeout=15000)
        except PlaywrightTimeoutError:
            logger.error(msg=f"🔄 Sahifada article elementi topilmadi")
            return {"error": True, "message": "Invalid response from the server"}

        image_urls = set()
        await page.mouse.click(10, 10)
        await page.wait_for_timeout(500)

        while True:
            images = await page.locator("article ._aagv img").all()
            for img in images:
                url = await img.get_attribute("src")
                if url:
                    image_urls.add(url)

            next_button = page.locator("button[aria-label='Next']")
            if await next_button.count() > 0:
                prev_count = len(image_urls)
                await next_button.click()
                await page.wait_for_timeout(500)
                if len(image_urls) == prev_count:
                    break  # Agar yangi rasm topilmasa, loopni to‘xtatish
            else:
                break

        if not image_urls:
            logger.error(msg="🚫 Rasm URLlari topilmadi")
            return {"error": True, "message": "Invalid response from the server"}

        return {
            "error": False,
            "hosting": "instagram",
            "type": "album" if len(image_urls) > 1 else "image",
            "shortcode": shortcode,
            "caption": caption,
            "medias": [{"type": "image", "download_url": url, "thumb": url} for url in image_urls]
        }

    except Exception as e:
        logger.error(msg=f"❌ Noma'lum xatolik: {str(e)}")
        return {"error": True, "message": "Invalid response from the server"}



async def download_instagram_media(url, proxy_config):
    loop = asyncio.get_running_loop()
    try:
        # Async wrapper for yt-dlp extraction
        async def extract_info():
            def sync_extract():
                proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
                options = {
                    'quiet': True,
                    'proxy': proxy_url,
                    'extract_flat': False,
                }
                with yt_dlp.YoutubeDL(options) as ydl:
                    return ydl.extract_info(url, download=False)

            return await loop.run_in_executor(None, sync_extract)

        # Get media info asynchronously
        info = await extract_info()

        if not info:
            print("No info returned from yt-dlp")
            return {"error": True, "message": "Invalid response from the server"}

        if "entries" in info:  # This is an album/multi
            data = await get_video_album(info)
            if not data.get("medias"):
                data = await get_instagram_post_images(
                    post_url=url,
                    caption=data.get("caption", ""),
                    proxy_config=proxy_config
                )
        else:  # Single media item
            data = await get_video(info)

        return data

    except yt_dlp.utils.DownloadError as e:
        error_message = str(e)
        if "There is no video in this post" in error_message:
            return await get_instagram_post_images(
                post_url=url,
                caption="",
                proxy_config=proxy_config
            )
        print("Error", error_message)
        return {"error": True, "message": "Invalid response from the server"}

    except Exception as e:
        print(f"Error downloading Instagram media: {str(e)}")
        print(traceback.format_exc())
        return {"error": True, "message": "Invalid response from the server"}
