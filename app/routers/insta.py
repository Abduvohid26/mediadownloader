import traceback
import logging
import yt_dlp
import asyncio
from playwright.async_api import async_playwright
from fastapi import FastAPI
import weakref

class Example:
    pass


app = FastAPI()

logger = logging.getLogger(__name__)

global_browser = {
    "browser": None,
    "context": None,
    "page": None,
    "playwright": None
}

async def init_browser(proxy_config=None):
    print(global_browser, "GLOBAL")
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

        await page.wait_for_selector(".button__download", timeout=10000)

        story_links = [await el.get_attribute("href") for el in await page.locator(".button__download").all()]

        # Sarlavhalarni olish
        titles = [await p.text_content() for p in await page.locator(".output-list__caption p").all()]
        title = titles[0] if titles else None

        if not story_links:
            return {"error": True, "message": "Invalid response from the server"}

        first_url = story_links[0] if story_links else ""

        return {
            "error": False,
            "hosting": "instagram",
            "type": "album" if len(story_links) != 1 else "image" if first_url.lower().endswith(".jpg") else "video",
            "url": username,
            "title": title,
            "medias": [{"download_url": url, "type": "image" if url.lower().endswith(".jpg") else "video"} for url in
                       story_links]
        }
    except Exception as e:
        print(f"Error xatolik:{e}")
        return {"error": True, "message": "Invalid response from the server"}


async def get_video(info, url):
    data = {
        "error": False,
        "hosting": "instagram",
        "type": "video",
        "url": url,
        "title": info.get("title", ""),
        "medias": [
            {
                "download_url": next((item['url'] for item in info.get('formats', []) if list(item.keys())[0] == 'url'),None),
                "type": "video"
            }
        ]
    }
    return data


async def get_video_album(info, url):
    data = {
        "error": False,
        "hosting": "instagram",
        "type": "album",
        "url": url,
        "title": info.get("title", ""),
        "medias": [
            {
                "download_url": entry["url"],
                "type": "video"
            }
            for entry in info["entries"]
        ]
    }
    return data




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

        info = await extract_info()
        if "entries" in info and len(info["entries"]) > 1:
            data = await get_video_album(info, url)
        elif "formats" in info:
            print("Get a video")
            data = await get_video(info, url)
        else:
            print("Get media1")
            data = await get_instagram_story_urls(
                username=url,
                proxy_config=proxy_config,
            )
        return data

    except yt_dlp.utils.DownloadError as e:
        error_message = str(e)

        if "There is no video in this post" in error_message:
            print("Get media2")
            return await get_instagram_story_urls(
                username=url,
                proxy_config=proxy_config
            )
        print("Error", error_message)
        return {"error": True, "message": "Invalid response from the server"}

    except Exception as e:
        print(f"Error downloading Instagram media: {str(e)}")
        print(traceback.format_exc())
        return {"error": True, "message": "Invalid response from the server"}











import asyncio


async def get_instagram_story_urls_self(url):
    try:
        async with async_playwright() as playwright:
            options = {
                "headless": False,  # Ko'rinadigan rejimda ishga tushiramiz
                "args": ["--no-sandbox", "--disable-setuid-sandbox"],
            }
            browser = await playwright.chromium.launch(**options)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            await page.wait_for_selector("video", timeout=10000)

            video_elements = await page.query_selector_all("video")
            video_urls = [await video.get_attribute("src") for video in video_elements]

            await browser.close()
            return {"error": False, "video_urls": video_urls}

    except Exception as e:
        print("Error get_instagram_story_urls_self:", e)
        return {"error": True, "message": "Invalid response from the server"}

# async def main():
#     url = "https://www.instagram.com/p/DHob-ZCufAH/?utm_source=ig_web_copy_link"
#     result = await get_instagram_story_urls_self(url)
#     print(result)

# import asyncio
# asyncio.run(main())
#
# if global_browser["browser"] is None:
#     print("🔄 Yangi brauzer ishga tushdi...")
#     global_browser["playwright"] = await async_playwright().start()
#
#     options = {
#         "headless": True,
#         "args": ["--no-sandbox", "--disable-setuid-sandbox"]
#     }
#     if proxy_config:
#         options["proxy"] = proxy_config
#
#     global_browser["browser"] = await global_browser["playwright"].chromium.launch(**options)
#     global_browser["context"] = await global_browser["browser"].new_context()
#     global_browser["page"] = await global_browser["context"].new_page()
#
#     await global_browser["page"].goto("https://sssinstagram.com/ru/story-saver", timeout=10000)
#     await global_browser["page"].wait_for_load_state("domcontentloaded")
# return (global_browser["browser"],
#         global_browser["context"],
#         global_browser["page"],
#         global_browser["playwright"])