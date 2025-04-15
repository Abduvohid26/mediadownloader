import traceback
import logging
import yt_dlp
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
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

async def init_browser(proxy_config=None, action=None):
    print(global_browser, "GLOBAL")
    """ Brauzerni, contextni va sahifani oldindan ochib qo‘yish """
    if global_browser["browser"] is None and action == "instagram":
        print("🔄 Yangi brauzer ishga tushdi in...")
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

        return (global_browser["browser"],
                global_browser["context"],
                global_browser["page"],
                global_browser["playwright"])
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




# async  def get_instagram_image_and_album_and_reels(post_url, proxy_config):
#     print("Bizdan salomlar")

#     try:
#         browser, context, page, playwright = await init_browser(proxy_config)

#         browser_args = {
#             "headless": True,
#             "args": ["--no-sandbox", "--disable-setuid-sandbox"]
#         }

#         # if proxy_config:
#         #     browser_args["proxy"] = proxy_config
#         #
#         # browser = await playwright.chromium.launch(**browser_args)
#         page = await context.new_page()

#         try:
#             await page.goto(post_url, timeout=15000)
#         except PlaywrightTimeoutError:
#             return {"error": True, "message": "⏳ Sahifani yuklash muddati tugadi"}

#         try:
#             await page.wait_for_selector("article", timeout=20000)
#         except PlaywrightTimeoutError:
#             logger.error("🔄 Sahifada article elementi topilmadi")
#             return {"error": True, "message": "Invalid response from the server"}

#         image_urls = set()
#         video_data = []

#         await page.mouse.click(10, 10)
#         await page.wait_for_timeout(1500)
#         caption = None
#         caption_element = await page.query_selector('article span._ap3a')
#         if caption_element:
#             caption = await caption_element.inner_text()

#         while True:
#             # Rasmlar
#             images = await page.locator("article ._aagv img").all()
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
#             images = await page.locator("article ._aagv img").all()
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


async def get_instagram_image_and_album_and_reels(post_url, proxy_config):
    print("Bizdan salomlar")
    try:
        browser, context, page, playwright = await init_browser(proxy_config, action="instagram")

        page = await context.new_page()

        try:
            await page.goto(post_url, timeout=15000)  # TEZROQ yuklash
            await page.wait_for_selector("article", timeout=10000)
            await page.wait_for_selector("article img, video", timeout=10000)
        except PlaywrightTimeoutError:
            return {"error": True, "message": "⏳ Sahifa yoki media elementlar chiqmadi"}

        image_urls = set()
        video_data = []

        await page.mouse.click(10, 10)
        await page.wait_for_timeout(1000)  # Yengil kutish (aniq chiqsin)

        caption = None
        caption_element = await page.query_selector('article span._ap3a')
        if caption_element:
            caption = await caption_element.inner_text()

        while True:
            # Rasmlar
            images = await page.locator("article ._aagv img").all()
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

            # "Next" tugmasi bor bo‘lsa – navbatdagi media
            next_button = page.locator("button[aria-label='Next']")
            try:
                await next_button.wait_for(timeout=2000)
            except PlaywrightTimeoutError:
                break

            prev_count = len(image_urls) + len(video_data)
            await next_button.click()
            await page.wait_for_timeout(1000)

            images = await page.locator("article ._aagv img").all()
            new_urls = {await img.get_attribute("src") for img in images if await img.get_attribute("src")}
            new_video_elements = await page.query_selector_all("video")
            new_video_urls = [
                await video.get_attribute("src") for video in new_video_elements if await video.get_attribute("src")
            ]
            for url in new_video_urls:
                if url and not any(v["url"] == url for v in video_data):
                    video_data.append({"url": url, "type": "video"})

            if len(new_urls - image_urls) == 0 and len(new_video_urls) == 0:
                break

            image_urls.update(new_urls)

        if not image_urls and not video_data:
            return {"error": True, "message": "🚫 Hech qanday media topilmadi"}

        media_items = [{"type": "image", "download_url": url} for url in image_urls]
        media_items += video_data

        return {
            "error": False,
            "hosting": "instagram",
            "type": "album" if len(media_items) > 1 else media_items[0]["type"],
            "caption": caption,
            "medias": media_items
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"error": True, "message": "Noma'lum xatolik yuz berdi"}






#
# import time
# import asyncio
#
# async def get_instagram_story_urls_self(url):
#     try:
#         async with async_playwright() as playwright:
#             options = {
#                 "headless": False,  # Ko'rinadigan rejimda ishga tushiramiz
#                 "args": ["--no-sandbox", "--disable-setuid-sandbox"],
#             }
#             browser = await playwright.chromium.launch(**options)
#             page = await browser.new_page()
#             await page.goto(url, timeout=60000)
#
#             # Modalni yopish (ESC tugmasi)
#             await page.keyboard.press("Escape")
#
#             await page.wait_for_selector("video, img", timeout=10000)  # Video va img kutish
#
#             # Video URL'larini olish
#             video_elements = await page.query_selector_all("video")
#             print(video_elements, "VIDEO")
#             video_data = []
#             for video in video_elements:
#                 video_url = await video.get_attribute("src")
#                 if video_url:  # Agar URL mavjud bo'lsa
#                     video_data.append({"url": video_url, "type": "video"})
#
#             img_elements = await page.query_selector_all("img")
#             print(img_elements, "IMG")
#             img_data = []
#             for img in img_elements:
#                 img_url = await img.get_attribute("src")
#                 # Agar rasm URL'si mavjud bo'lsa va media URL bo'lsa
#                 if img_url and 'media' in img_url:
#                     img_data.append({"url": img_url, "type": "image"})
#
#             # Video va rasm URL'larini birlashtirish
#             all_media = video_data + img_data
#
#             await browser.close()
#             return {"error": False, "media_urls": all_media}
#
#     except Exception as e:
#         print("Error get_instagram_story_urls_self:", e)
#         return {"error": True, "message": "Invalid response from the server"}
#
#
# async def main():
#     curr_time = time.time()
#     url = "https://www.instagram.com/p/DITdnSCNJXC/?utm_source=ig_web_copy_link"
#     result = await get_instagram_story_urls_self(url)
#     print(result)
#     print(time.time() - curr_time, "RES")
# #
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


# import asyncio
# from playwright.async_api import async_playwright
#
# AUTH_FILE = "auth.json"  # Instagram sahifasiga kirish uchun cookies saqlash
#
# async def extract_instagram_media_urls(post_url):
#     """
#     Instagram postidan barcha media URL'larini olish
#     :param post_url: Instagram post linki
#     :return: Dictionary: {'username': str, 'post_id': str, 'media': list[dict]}
#     """
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         context = await browser.new_context(
#             user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
#         )
#
#         # Agar avval login qilingan bo'lsa, sessiyani yuklash
#         try:
#             await context.storage_state(path=AUTH_FILE)
#         except:
#             pass
#
#         page = await context.new_page()
#
#         try:
#             # Post sahifasiga o'tish
#             await page.goto(post_url, timeout=20000)
#             await page.wait_for_load_state("networkidle")  # Sahifa to'liq yuklanguncha kutish
#
#             # Post ma'lumotlarini olish
#             post_id = post_url.split("/")[-2]
#             username = "unknown"
#
#             try:
#                 username_element = await page.query_selector('header a')
#                 username = await username_element.inner_text() if username_element else "unknown"
#             except:
#                 pass
#
#             # Media URL'larini yig'ish
#             media_list = []
#
#             # 1. Barcha rasmlarni olish
#             images = await page.query_selector_all('img[decoding="auto"]')
#             for idx, img in enumerate(images, 1):
#                 img_url = await img.get_attribute('src')
#                 if img_url and 'http' in img_url:
#                     media_list.append({
#                         'type': 'image',
#                         'url': img_url,
#                         'index': idx
#                     })
#
#             # 2. Videolarni olish (source tag ichidan tekshirish)
#             videos = await page.query_selector_all('video')
#             for idx, video in enumerate(videos, 1):
#                 video_url = await video.get_attribute('src')
#                 if not video_url:  # Agar `video` tagining `src` bo'sh bo'lsa, `source` dan olishga harakat qilamiz
#                     sources = await video.query_selector_all("source")
#                     for source in sources:
#                         video_url = await source.get_attribute('src')
#                         if video_url:
#                             break
#
#                 if video_url and 'http' in video_url:
#                     media_list.append({
#                         'type': 'video',
#                         'url': video_url,
#                         'index': idx
#                     })
#
#             return {
#                 'success': True,
#                 'data': {
#                     'username': username,
#                     'post_id': post_id,
#                     'media_count': len(media_list),
#                     'media': media_list
#                 }
#             }
#
#         except Exception as e:
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'url': post_url
#             }
#         finally:
#             await browser.close()
#
#
# async def main():
#     post_url = "https://www.instagram.com/reel/DIWWW-TsHjg/?utm_source=ig_web_copy_link"
#     result = await extract_instagram_media_urls(post_url)
#
#     if result['success']:
#         print("\n📌 Media ma'lumotlari:")
#         print(f"👤 Foydalanuvchi: @{result['data']['username']}")
#         print(f"🆔 Post ID: {result['data']['post_id']}")
#         print(f"📸 Media soni: {result['data']['media_count']}\n")
#
#         for media in result['data']['media']:
#             print(f"🔹 {media['type'].upper()} {media['index']}: {media['url']}")
#     else:
#         print(f"❌ Xatolik: {result['error']}")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
