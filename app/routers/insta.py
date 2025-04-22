import traceback
import logging
import yt_dlp
import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, async_playwright
from fastapi import FastAPI
from .model import BrowserManager
from .proxy_route import get_proxy_config
import re
from playwright.async_api import async_playwright

class Example:
    pass


app = FastAPI()

logger = logging.getLogger(__name__)


manager = BrowserManager(interval=100)


# async def get_instagram_story_urls(username, context):
#     """ Instagram storylarini olish """
#     try:
#         # await manager.init_browser()
#         # page = manager.page
#         # print(page, "PAGE")
#         page = await context.new_page()
#         await page.goto("https://sssinstagram.com/ru/story-saver", wait_until="domcontentloaded")
#         await page.fill(".form__input", username)
#         await page.click(".form__submit")
#         print(page, "page")
#         await page.wait_for_selector(".button__download", state="attached")

#         story_links = [await el.get_attribute("href") for el in await page.locator(".button__download").all()]

#         # Sarlavhalarni olish
#         titles = [await p.text_content() for p in await page.locator(".output-list__caption p").all()]
#         title = titles[0] if titles else None

#         if not story_links:
#             return {"error": True, "message": "Invalid response from the server"}

#         first_url = story_links[0] if story_links else ""
#         match = re.search(r'/p/([^/]+)/', username)
#         shortcode = match.group(1) if match else "unknown"
#         return {
#             "error": False,
#             "shortcode": shortcode,
#             "hosting": "instagram",
#             "type": "album" if len(story_links) != 1 else "image" if first_url.lower().endswith(".jpg") else "video",
#             "url": username,
#             "title": title,
#             "medias": [{"download_url": url, "type": "image" if url.lower().endswith(".jpg") else "video"} for url in
#                        story_links]
#         }
#     except Exception as e:
#         print(f"Error xatolik:{e}")
#         return {"error": True, "message": "Invalid response from the server"}

# async def check_itorya():
#     async with async_playwright() as playwright:
#         browser = await playwright.chromium.launch(headless=False, args=["--no-sandbox", "--disable-setuid-sandbox"])
#         context = await browser.new_context()
#         result = await get_instagram_image_and_album_and_reels("https://www.instagram.com/p/DHgWbewsTwH/?utm_source=ig_web_copy_link", context)
#         print(result)
#         await browser.close()


# async def get_instagram_story_urls(username: str, context):
#     """Instagram hikoyalarini yuklab olish funksiyasi."""
#     async with async_playwright() as playwright:
#         # proxy = await get_proxy_config()
#         options = {
#             "headless": True,
#             "args": ["--no-sandbox", "--disable-setuid-sandbox"]
#         }
#         # if proxy:
#         #     options["proxy"] = {
#         #         "server": f"http://{proxy['server'].replace('http://', '')}",
#         #         "username": proxy['username'],
#         #         "password": proxy['password']   
#         #     }

#         browser = await playwright.chromium.launch(**options)
#         page = await browser.new_page()
#         try:
#             # page = await context.new_page()
#             # print(page, "PAGE")

#             # Saytga kirish
#             await page.goto("https://sssinstagram.com/ru/story-saver")
#             print(page, "page")
#             # Inputga username qo'yish
#             await page.fill(".form__input", username)
#             await page.click(".form__submit")

#             # Yuklab olish tugmasi chiqquncha kutish
#             await page.wait_for_selector(".button__download", state="attached", timeout=25000)

#             # Storylar uchun yuklab olish linklari
#             story_elements = await page.locator(".button__download").all()
#             story_links = [await el.get_attribute("href") for el in story_elements if await el.get_attribute("href")]

#             # Har bir media uchun thumbnail (prevyu rasm)
#             thumbnail_elements = await page.locator(".media-content__image").all()
#             thumbnails = [await el.get_attribute("src") for el in thumbnail_elements if await el.get_attribute("src")]

#             # Sarlavha olish
#             title_elements = await page.locator(".output-list__caption p").all()
#             titles = [await el.text_content() for el in title_elements]
#             title = titles[0] if titles else None

#             # Shortcode ajratish (ixtiyoriy, agar URLdan topilsa)
#             match = re.search(r'/p/([^/]+)/', username)
#             shortcode = match.group(1) if match else "unknown"

#             if not story_links:
#                 return {"error": True, "message": "Hech qanday media topilmadi."}

#             # Media turini aniqlash
#             def detect_type(url: str):
#                 return "image" if url.lower().endswith(".jpg") else "video"

#             # Media elementlarini to'plash (thumbnail bilan)
#             medias = []
#             for idx, url in enumerate(story_links):
#                 medias.append({
#                     "type": detect_type(url),
#                     "download_url": url,
#                     "thumbnail": thumbnails[idx] if idx < len(thumbnails) else None
#                 })

#             return {
#                 "error": False,
#                 "shortcode": shortcode,
#                 "hosting": "instagram",
#                 "type": "album" if len(story_links) > 1 else detect_type(story_links[0]),
#                 "url": username,
#                 "title": title,
#                 "medias": medias,
#             }

#         except Exception as e:
#             print(f"Xatolik yuz berdi: {e}")
#             return {"error": True, "message": "Serverdan noto‘g‘ri javob oldik."}
        
#         finally:
#             await browser.close()

async def get_instagram_story_urls(username: str, context):
     """Instagram hikoyalarini yuklab olish funksiyasi."""
     try:
         await manager.init_browser()
         page = manager.page
         print(page, "PAGE")
         page = await context.new_page()
 
         # Saytga kirish
         await page.goto("https://sssinstagram.com/ru/story-saver")
 
         # Inputga username qo'yish
         await page.fill(".form__input", username)
         await page.click(".form__submit")
 
         await page.wait_for_selector(".button__download", timeout=10000)
         # Yuklab olish tugmasi chiqquncha kutish
         await page.wait_for_selector(".button__download", state="attached", timeout=25000)
 
         story_links = [await el.get_attribute("href") for el in await page.locator(".button__download").all()]
         # Storylar uchun yuklab olish linklari
         story_elements = await page.locator(".button__download").all()
         story_links = [await el.get_attribute("href") for el in story_elements if await el.get_attribute("href")]
 
         # Sarlavhalarni olish
         titles = [await p.text_content() for p in await page.locator(".output-list__caption p").all()]
         title = titles[0] if titles else None
         # Har bir media uchun thumbnail (prevyu rasm)
         thumbnail_elements = await page.locator(".media-content__image").all()
         thumbnails = [await el.get_attribute("src") for el in thumbnail_elements if await el.get_attribute("src")]
 
         if not story_links:
             return {"error": True, "message": "Invalid response from the server"}
         # Sarlavha olish
         title_elements = await page.locator(".output-list__caption p").all()
         titles = [await el.text_content() for el in title_elements]
         title = titles[0] if titles else None
 
         first_url = story_links[0] if story_links else ""
         # Shortcode ajratish (ixtiyoriy, agar URLdan topilsa)
         match = re.search(r'/p/([^/]+)/', username)
         shortcode = match.group(1) if match else "unknown"
 
         if not story_links:
             return {"error": True, "message": "Hech qanday media topilmadi."}
 
         # Media turini aniqlash
         def detect_type(url: str):
             return "image" if url.lower().endswith(".jpg") else "video"
 
         # Media elementlarini to'plash (thumbnail bilan)
         medias = []
         for idx, url in enumerate(story_links):
             medias.append({
                 "type": detect_type(url),
                 "download_url": url,
                 "thumbnail": thumbnails[idx] if idx < len(thumbnails) else None
             })
 
         return {
             "error": False,
             "shortcode": shortcode,
             "hosting": "instagram",
             "type": "album" if len(story_links) != 1 else "image" if first_url.lower().endswith(".jpg") else "video",
             "type": "album" if len(story_links) > 1 else detect_type(story_links[0]),
             "url": username,
             "title": title,
             "medias": [{"download_url": url, "type": "image" if url.lower().endswith(".jpg") else "video"} for url in
                        story_links]         }
     
 
     except Exception as e:
         print(f"Error xatolik:{e}")
         return {"error": True, "message": "Invalid response from the server"}
         print(f"Xatolik yuz berdi: {e}")
         return {"error": True, "message": "Serverdan noto‘g‘ri javob oldik."}


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




async def download_instagram_media(url, proxy_config, context):
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
            print(context, "context")
            data = await get_instagram_image_and_album_and_reels(
                post_url=url,
                context=context,
            )
        return data

    except yt_dlp.utils.DownloadError as e:
        error_message = str(e)

        if "There is no video in this post" in error_message:
            print("Get media2")
            return await get_instagram_image_and_album_and_reels(
                post_url=url,
                context=context
            )
        print("Error", error_message)
        return {"error": True, "message": "Invalid response from the server"}

    except Exception as e:
        print(f"Error downloading Instagram media: {str(e)}")
        print(traceback.format_exc())
        return {"error": True, "message": "Invalid response from the server"}



async def get_instagram_image_and_album_and_reels(post_url, context):
    print("📥 Media yuklanmoqda...")

    try:
        await manager.init_browser()
        await manager.goto_reel(url=post_url)
        page = manager.page_in

        try:
            await page.wait_for_selector("section", timeout=20000)
        except PlaywrightTimeoutError as e:
            print(f"❌ 'section' elementi topilmadi: {e}")
            return {"error": True, "message": "Invalid response from the server"}

        image_urls = set()
        video_data = []

        await page.mouse.click(10, 10)
        await page.wait_for_timeout(1500)

        # Captionni olish
        caption = None
        caption_element = await page.query_selector('section span._ap3a')
        if caption_element:
            caption = await caption_element.inner_text()

        while True:
            # Rasmlar
            images = await page.locator("section ._aagv img").all()
            for img in images:
                url = await img.get_attribute("src")
                if url:
                    image_urls.add(url)

            # Videolar
            video_elements = await page.query_selector_all("video")
            for video in video_elements:
                video_url = await video.get_attribute("src")
                if video_url and not any(v["url"] == video_url for v in video_data):
                    video_data.append({"url": video_url, "type": "video"})

            # Keyingi tugma
            next_button = page.locator("button[aria-label='Next']")
            try:
                await next_button.wait_for(timeout=3000)
                await next_button.click()
                await page.wait_for_timeout(1000)
            except PlaywrightTimeoutError:
                break  # Endi boshqa media yo'q

            # Yangi media tekshirish
            new_images = await page.locator("section ._aagv img").all()
            new_urls = {await img.get_attribute("src") for img in new_images if await img.get_attribute("src")}
            new_video_elements = await page.query_selector_all("video")
            new_video_urls = [
                await video.get_attribute("src") for video in new_video_elements if await video.get_attribute("src")
            ]

            for url in new_video_urls:
                if url and not any(v["url"] == url for v in video_data):
                    video_data.append({"url": url, "type": "video"})

            if len(new_urls - image_urls) == 0 and len(new_video_urls) == 0:
                break  # Hech qanday yangi media topilmadi

            image_urls.update(new_urls)

        if not image_urls and not video_data:
            print("🚫 Media URLlari topilmadi")
            return {"error": True, "message": "Invalid response from the server"}

        media_items = [{"type": "image", "download_url": url} for url in image_urls] + video_data

        match = re.search(r'/p/([^/]+)/', post_url)
        shortcode = match.group(1) if match else "unknown"

        return {
            "error": False,
            "shortcode": shortcode,
            "hosting": "instagram",
            "type": "album" if len(media_items) > 1 else media_items[0]["type"],
            "caption": caption,
            "medias": media_items
        }

    except Exception as e:
        print(f"❗ Umumiy xatolik: {e}")
        return {"error": True, "message": "Invalid response from the server"}

# async def get_instagram_image_and_album_and_reels(post_url, context):
#     print("📥 Media yuklanmoqda...")
#     async with async_playwright() as playwright:
#         proxy = await get_proxy_config()
#         options = {
#             "headless": True,
#             "args": ["--no-sandbox", "--disable-setuid-sandbox"]
#         }
#         if proxy:
#             options["proxy"] = {
#                 "server": f"http://{proxy['server'].replace('http://', '')}",
#                 "username": proxy['username'],
#                 "password": proxy['password']   
#             }

#         browser = await playwright.chromium.launch(**options)
#         page = await browser.new_page()
#         await page.goto(post_url)
#         try:
#             try:
#                 await page.wait_for_selector("article", timeout=20000)
#             except Exception as e:
#                 print(f"❌ 'section' elementi topilmadi: {e}")
#                 return {"error": True, "message": "Invalid response from the server"}

#             await page.mouse.click(10, 10)
#             await page.wait_for_timeout(1500)

#             caption = None
#             if (caption_el := await page.query_selector('article span._ap3a')):
#                 caption = await caption_el.inner_text()

#             media_list = []

#             while True:
#                 # 1. RASMLAR faqat article ichidan olinadi
#                 images = await page.locator("article ._aagv img").all()
#                 for img in images:
#                     src = await img.get_attribute("src")
#                     if src and not any(m["download_url"] == src for m in media_list):
#                         media_list.append({
#                             "type": "image",
#                             "download_url": src,
#                             "thumbnail": src
#                         })

#                 # 2. VIDEOLAR faqat article ichidan olinadi
#                 videos = await page.locator("article video").all()
#                 for video in videos:
#                     src = await video.get_attribute("src")
#                     poster = await video.get_attribute("poster")
#                     if src and not any(m["download_url"] == src for m in media_list):
#                         media_list.append({
#                             "type": "video",
#                             "download_url": src,
#                             "thumbnail": poster or src
#                         })

#                 # 3. Keyingi media (agar mavjud bo‘lsa)
#                 next_btn = page.locator("button[aria-label='Next']")
#                 if await next_btn.count() > 0:
#                     await next_btn.click()
#                     await page.wait_for_timeout(1000)
#                 else:
#                     break

#             if not media_list:
#                 return {"error": True, "message": "Hech qanday media topilmadi"}

#             # Shortcode ni URL dan olamiz
#             match = re.search(r'/p/([^/]+)/', post_url)
#             shortcode = match.group(1) if match else "unknown"

#             return {
#                 "error": False,
#                 "shortcode": shortcode,
#                 "hosting": "instagram",
#                 "type": "album" if len(media_list) > 1 else media_list[0]["type"],
#                 "caption": caption,
#                 "medias": media_list
#             }

#         except Exception as e:
#             print(f"❗ Umumiy xatolik: {e}")
#             return {"error": True, "message": "Invalid response from the server"}
#         finally:
#             await browser.close()

# async def get_instagram_image_and_album_and_reels(post_url, proxy_config):
#     print("📥 Media yuklanmoqda...")
#     # async with async_playwright() as p:
#     #     options = {
#     #         "headless": True,
#     #         "args": ["--no-sandbox", "--disable-setuid-sandbox"],
#     #     }

#     #     if proxy_config:
#     #         options["proxy"] = {
#     #             "server": f"http://{proxy_config['server'].replace('http://', '')}",
#     #             "username": proxy_config['username'],
#     #             "password": proxy_config['password']
#     #         }

#     #     browser = await p.chromium.launch(**options)
#     #     context = await browser.new_context()
#     #     page = await context.new_page()

#     try:
#         await manager.init_browser()
#         await manager.goto_reel(url=post_url)
#         page = manager.page_in

#         try:
#             await page.wait_for_selector("section", timeout=20000)
#         except Exception as e:
#             print(f"❌ 'section' elementi topilmadi: {e}")
#             return {"error": True, "message": "Invalid response from the server"}
#             # return {"error": True, "message": "Sahifa elementlari topilmadi"}

#         await page.mouse.click(10, 10)
#         await page.wait_for_timeout(1500)

#         caption = None
#         if (caption_el := await page.query_selector('section span._ap3a')):
#             caption = await caption_el.inner_text()

#         image_urls, video_data = set(), []

#         while True:
#             images = await page.locator("section ._aagv img").all()
#             new_images = {await img.get_attribute("src") for img in images if await img.get_attribute("src")}
#             image_urls.update(new_images)

#             videos = await page.query_selector_all("video")
#             for video in videos:
#                 video_url = await video.get_attribute("src")
#                 if video_url and not any(v["url"] == video_url for v in video_data):
#                     video_data.append({"url": video_url, "type": "video"})

#             try:
#                 next_btn = page.locator("button[aria-label='Next']")
#                 await next_btn.wait_for(timeout=1500)
#                 await next_btn.click()
#                 await page.wait_for_timeout(1000)
#             except Exception:
#                 break

#         if not image_urls and not video_data:
#             return {"error": True, "message": "Invalid response from the server"}
#             # return {"error": True, "message": "Hech qanday media topilmadi"}

#         # Shortcode ni URL dan olamiz
#         match = re.search(r'/p/([^/]+)/', post_url)
#         shortcode = match.group(1) if match else "unknown"

#         medias = [{"type": "image", "download_url": url} for url in image_urls] + video_data

#         return {
#             "error": False,
#             "shortcode": shortcode,
#             "hosting": "instagram",
#             "type": "album" if len(medias) > 1 else medias[0]["type"],
#             "caption": caption,
#             "medias": medias
#         }

#     except Exception as e:
#         print(f"❗ Umumiy xatolik: {e}")
#         return {"error": True, "message": "Invalid response from the server"}
#             # return {"error": True, "message": "Xatolik yuz berdi"}
