import traceback
import logging
import yt_dlp
import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, async_playwright
from fastapi import FastAPI
from .model import BrowserManager
from .proxy_route import get_proxy_config
import re

class Example:
    pass


app = FastAPI()

logger = logging.getLogger(__name__)


manager = BrowserManager(interval=100)


async def get_instagram_story_urls(username, proxy_config):
    """ Instagram storylarini olish """
    try:
        await manager.init_browser()
        page = manager.page
        print(page, "PAGE")
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
        match = re.search(r'/p/([^/]+)/', username)
        shortcode = match.group(1) if match else "unknown"
        return {
            "error": False,
            "shortcode": shortcode,
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
    match = re.search(r'/p/([^/]+)/', url)
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
                "download_url": next((item['url'] for item in info.get('formats', []) if list(item.keys())[0] == 'url'),None),
                "type": "video"
            }
        ]
    }
    return data


async def get_video_album(info, url):
    match = re.search(r'/p/([^/]+)/', url)
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
            data = await get_instagram_image_and_album_and_reels(
                post_url=url,
                proxy_config=proxy_config,
            )
        return data

    except yt_dlp.utils.DownloadError as e:
        error_message = str(e)

        if "There is no video in this post" in error_message:
            print("Get media2")
            return await get_instagram_image_and_album_and_reels(
                post_url=url,
                proxy_config=proxy_config
            )
        print("Error", error_message)
        return {"error": True, "message": "Invalid response from the server"}

    except Exception as e:
        print(f"Error downloading Instagram media: {str(e)}")
        print(traceback.format_exc())
        return {"error": True, "message": "Invalid response from the server"}




async def get_instagram_image_and_album_and_reels(post_url, proxy_config):
    print("📥 Media yuklanmoqda...")
    # async with async_playwright() as p:
    #     options = {
    #         "headless": True,
    #         "args": ["--no-sandbox", "--disable-setuid-sandbox"],
    #     }

    #     if proxy_config:
    #         options["proxy"] = {
    #             "server": f"http://{proxy_config['server'].replace('http://', '')}",
    #             "username": proxy_config['username'],
    #             "password": proxy_config['password']
    #         }

    #     browser = await p.chromium.launch(**options)
    #     context = await browser.new_context()
    #     page = await context.new_page()

    try:
        await manager.init_browser()
        await manager.goto_reel(url=post_url)
        page = manager.page_in

        try:
            await page.wait_for_selector("section", timeout=20000)
        except Exception as e:
            print(f"❌ 'section' elementi topilmadi: {e}")
            return {"error": True, "message": "Invalid response from the server"}
            # return {"error": True, "message": "Sahifa elementlari topilmadi"}

        await page.mouse.click(10, 10)
        await page.wait_for_timeout(1500)

        caption = None
        if (caption_el := await page.query_selector('section span._ap3a')):
            caption = await caption_el.inner_text()

        image_urls, video_data = set(), []

        while True:
            images = await page.locator("section ._aagv img").all()
            new_images = {await img.get_attribute("src") for img in images if await img.get_attribute("src")}
            image_urls.update(new_images)

            videos = await page.query_selector_all("video")
            for video in videos:
                video_url = await video.get_attribute("src")
                if video_url and not any(v["url"] == video_url for v in video_data):
                    video_data.append({"url": video_url, "type": "video"})

            try:
                next_btn = page.locator("button[aria-label='Next']")
                await next_btn.wait_for(timeout=1500)
                await next_btn.click()
                await page.wait_for_timeout(1000)
            except Exception:
                break

        if not image_urls and not video_data:
            return {"error": True, "message": "Invalid response from the server"}
            # return {"error": True, "message": "Hech qanday media topilmadi"}

        # Shortcode ni URL dan olamiz
        match = re.search(r'/p/([^/]+)/', post_url)
        shortcode = match.group(1) if match else "unknown"

        medias = [{"type": "image", "download_url": url} for url in image_urls] + video_data

        return {
            "error": False,
            "shortcode": shortcode,
            "hosting": "instagram",
            "type": "album" if len(medias) > 1 else medias[0]["type"],
            "caption": caption,
            "medias": medias
        }

    except Exception as e:
        print(f"❗ Umumiy xatolik: {e}")
        return {"error": True, "message": "Invalid response from the server"}
            # return {"error": True, "message": "Xatolik yuz berdi"}
        
        # finally:
        #     await browser.close()



# async  def get_instagram_image_and_album_and_reels(post_url, proxy_config):
#     print("Bizdan salomlar")

#     try:
#         await manager.init_browser()
#         # page = await manager.context.new_page()

#         # try:
#         #     await page.goto(post_url, timeout=15000)
#         # except PlaywrightTimeoutError:
#         #     return {"error": True, "message": "⏳ Sahifani yuklash muddati tugadi"}
#         await manager.goto_reel(url=post_url)
#         page = manager.page_in

#         try:
#             # await page.wait_for_selector(".x1iyjqo2 xdj266r xkrivgy x1gryazu x1yztbdb x1ykew4q xs9x0gt xc73u3c x18d9i69 x5ib6vp x19sv2k2 xt0jiz3 x17zrpsu x1m1r3dp x1d81r3v x1yj74s3", timeout=20000)
#             await page.wait_for_selector("section")
#         except Exception as e:
#             print(f"🔄 Sahifada section elementi topilmadi: {e}")
#         except PlaywrightTimeoutError:
#             logger.error("🔄 Sahifada section elementi topilmadi")
#             return {"error": True, "message": "Invalid response from the server"}
        
#         image_urls = set()
#         video_data = []

#         await page.mouse.click(10, 10)
#         await page.wait_for_timeout(1500)
#         caption = None
#         caption_element = await page.query_selector('section span._ap3a')
#         if caption_element:
#             caption = await caption_element.inner_text()

#         while True:
#             # Rasmlar
#             images = await page.locator("section ._aagv img").all()
#             for img in images:
#                 url = await img.get_attribute("src")
#                 if url:
#                     image_urls.add(url)

#             # Videolar
#             video_elements = await page.query_selector_all("video")
#             for video in video_elements:
#                 video_url = await video.get_attribute("src")
#                 if video_url and not any(v["url"] == video_url for v in video_data):
#                     video_data.append({"url": video_url, "type": "video"})

#             # Keyingi tugmasini aniqlash
#             next_button = page.locator("button[aria-label='Next']")
#             try:
#                 await next_button.wait_for(timeout=3000)
#             except PlaywrightTimeoutError:
#                 break  # Endi keyingi media yo‘q

#             prev_count = len(image_urls) + len(video_data)

#             await next_button.click()
#             await page.wait_for_timeout(1000)

#             # Yangi rasm yoki video chiqmagan bo‘lsa, to‘xtaymiz
#             images = await page.locator("section ._aagv img").all()
#             new_urls = {await img.get_attribute("src") for img in images if await img.get_attribute("src")}
#             new_video_elements = await page.query_selector_all("video")
#             new_video_urls = [
#                 await video.get_attribute("src") for video in new_video_elements if await video.get_attribute("src")
#             ]
#             for url in new_video_urls:
#                 if url and not any(v["url"] == url for v in video_data):
#                     video_data.append({"url": url, "type": "video"})

#             if len(new_urls - image_urls) == 0 and len(new_video_urls) == 0:
#                 break

#             image_urls.update(new_urls)

#         if not image_urls and not video_data:
#             logger.error(msg="🚫 Media URLlari topilmadi")
#             return {"error": True, "message": "Invalid response from the server"}

#         media_items = [{"type": "image", "download_url": url} for url in image_urls]
#         media_items += video_data  # videolarni ham qo‘shamiz

#         return {
#             "error": False,
#             "hosting": "instagram",
#             "type": "album" if len(media_items) > 1 else media_items[0]["type"],
#             "caption": caption,
#             "medias": media_items
#         }
#     except Exception as e:
#         print(f"Error: {e}")
#         return {"error": True, "message": "Invalid response from the server"}