import traceback
from cachetools import TTLCache
import logging

logger = logging.getLogger(__name__)
cache = TTLCache(maxsize=500, ttl=600)


async def finall_browser(proxy_config):
    pass


async def init_browser(proxy_config):
    """ Brauzerni, contextni va sahifani oldindan ochib qo‘yish """
    if cache.get("browser") is None:
        print("🔄 Yangi brauzer ishga tushdi...")
        _playwright = await async_playwright().start()
        options = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-setuid-sandbox"]
        }
        if proxy_config:
            options["proxy"] = proxy_config
        _browser = await _playwright.chromium.launch(**options)
        cache["browser"] = _browser
        cache["playwright"] = _playwright
        _context = await _browser.new_context()
        cache["context"] = _context

        _page = await _context.new_page()
        cache["page"] = _page

        await _page.goto("https://sssinstagram.com/ru/story-saver", timeout=10000)
        await _page.wait_for_load_state("domcontentloaded")
    print(cache.get("browser"))
    return cache.get("browser"), cache.get("context"), cache.get("page")


async def close_browser():
    """ Brauzerni to‘g‘ri yopish """
    if cache.get("browser") is not None:
        print("❌ Brauzer yopildi")
        await cache.get("browser").close()
        cache["browser"] = None
    if cache.get("playwright") is not None:
        await cache.get("playwright").stop()
        cache["playwright"] = None


async def browser_keepalive(proxy_config, interval=600):
    """ 🔄 Har `interval` sekundda brauzerni qayta ishga tushiradi """
    while True:
        await asyncio.sleep(interval)
        await close_browser()
        await init_browser(proxy_config)


async def get_instagram_story_urls(username, proxy_config):
    """ Instagram storylarini olish """
    try:
        browser, context, page = await init_browser(proxy_config) 

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

from playwright.async_api import async_playwright, TimeoutError


_browser_image = None
_playwright_image = None


    


async def init_browser_images(proxy_config):
    """ Brauzerni, contextni va sahifani oldindan ochib qo‘yish """
    global _browser_image, _playwright_image
    if _browser_image is None:
        print("🔄 Yangi brauzer ishga tushdi Images...")
        _playwright_image = await async_playwright().start()
        options = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-setuid-sandbox"]
        }
        if proxy_config:
            options["proxy"] = proxy_config
        _browser_image = await _playwright_image.chromium.launch(**options)
    return _browser_image

async def close_browser_images():
    """ Brauzerni to‘g‘ri yopish """
    global _browser_image, _playwright_image
    if _browser_image:
        print("❌ Brauzer yopildi")
        await _browser_image.close()
        _browser_image = None
    if _playwright_image:
        await _playwright_image.stop()
        _playwright_image = None

async def browser_keepalive_images(proxy_config, interval=1000):
    """ 🔄 Har `interval` sekundda brauzerni qayta ishga tushiradi """
    while True:
        await asyncio.sleep(interval)
        await close_browser_images()
        await init_browser_images(proxy_config)

from urllib.parse import urlparse
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


async def get_instagram_post_images(post_url, caption, proxy_config):
    """
    Instagram postidagi barcha rasm URLlarini olish (albumlarni ham to'liq yuklash)

    Args:
        post_url (str): Instagram post linki

    Returns:
        dict: Instagram postidagi barcha rasm URLlari va qo‘shimcha ma‘lumotlar
    """
    try:
        browser, context, _ = await init_browser(proxy_config)
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


# async def get_instagram_post_images(post_url, caption, proxy_config):
#     """
#     Instagram postidagi barcha rasm URLlarini olish (albumlarni ham to'liq yuklash)
#     
#     Args:
#         post_url (str): Instagram post linki
#         
#     Returns:
#         dict: Instagram postidagi barcha rasm URLlari va qo‘shimcha ma‘lumotlar
#     """
#     try:
#         browser, context, page1 = await init_browser(proxy_config)
#         try:
#             page = await context.new_page()
#         except Exception as e:
#             print(e)
#             return {"error": True, "message": "Invalid response from the server"}
#         try:
#             await page.goto(post_url, timeout=15000)
#         except PlaywrightTimeoutError:
#             print("⏳ Time out!1")
#             return {"error": True, "message": "Invalid response from the server"}
# 
#         path = urlparse(post_url).path
#         shortcode = path.strip("/").split("/")[-1]
# 
#         try:
#             await page.wait_for_selector("article", timeout=15000)
#         except PlaywrightTimeoutError:
#             print("🔄 Timeout while waiting for article")
#             return {"error": True, "message": "Invalid response from the server"}
# 
#         image_urls = set()
#         await page.mouse.click(10, 10)  
#         await page.wait_for_timeout(500)
# 
#         while True:
#             images = await page.locator("article ._aagv img").all()
#             for img in images:
#                 url = await img.get_attribute("src")
#                 if url:
#                     image_urls.add(url)
#             
#             next_button = page.locator("button[aria-label='Next']")
#             if await next_button.count() > 0:
#                 await next_button.click()
#                 await page.wait_for_timeout(500)
#             else:
#                 break
# 
#         if not image_urls:
#             print("🚫 No image URLs found")
#             return {"error": True, "message": "Invalid response from the server"}
# 
#         return {
#             "error": False,
#             "hosting": "instagram",
#             "type": "album" if len(image_urls) > 1 else "image",
#             "shortcode": shortcode, 
#             "caption": caption,
#             "medias": [{"type": "image", "download_url": url, "thumb": url} for url in image_urls]
#         }
# 
#     except Exception as e:
#         print("❌ Error:", str(e))
#         return {"error": True, "message": "Invalid response from the server"}





#############################################
import yt_dlp
import asyncio


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
            raise ValueError("No info returned from yt-dlp")

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
        return {"error": error_message}

    except Exception as e:
        print(f"Error downloading Instagram media: {str(e)}")
        print(traceback.format_exc())
        return {"error": str(e)}

# async def download_instagram_media(url, proxy_config):
#     loop = asyncio.get_running_loop()
#     try:
#         def extract():
#             proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
#             print(proxy_url, 'proxy url')
#             options = {
#                 'quiet': False,
#                 'proxy': proxy_url,
#             }
#             with yt_dlp.YoutubeDL(options) as ydl:
#                 return ydl.extract_info(url, download=False)
#
#         info = await loop.run_in_executor(None, extract)
#
#         if not info:
#             raise ValueError("No info returned from yt-dlp")
#
#         if "entries" in info:
#             data = await get_video_album(info)
#             print(data, 'tyl')
#             if not data.get("medias"):
#                 data = await get_instagram_post_images(
#                     post_url=url,
#                     caption=data.get("caption", ""),
#                     proxy_config=proxy_config
#                 )
#             return data
#         else:
#             data = await get_video(info)
#             print(data, 'shu')
#             return data
#
#     except yt_dlp.utils.DownloadError as e:
#         error_message = str(e)
#         if "There is no video in this post" in error_message:
#             data = await get_instagram_post_images(
#                 post_url=url,
#                 caption="",
#                 proxy_config=proxy_config
#             )
#             print(data, 'bizda')
#             return data
#         else:
#             print(f"❌ yt-dlp error: {error_message}")
#             return {"error": error_message}
#
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         print(f"Error type: {type(e)}")
#         print(f"Traceback: {traceback.format_exc()}")
#         return {"error": str(e)}
#

# async def download_instagram_media(url, proxy_config):
#     loop = asyncio.get_running_loop()
#     try:
#         def extract():
#             proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
#             print(proxy_url, 'proxy url')
#             options = {
#                 'quiet': False,
#                 'proxy': proxy_url,
#             }
#             with yt_dlp.YoutubeDL(options) as ydl:
#                 return ydl.extract_info(url, download=False)
#         print(url, 'url')
#         info = await loop.run_in_executor(None, extract)
#         if "entries" in info:
#             data = await get_video_album(info)
#             print(data, 'tyl')
#             if data["medias"] == []:
#                 data = await get_instagram_post_images(post_url=url, caption=data["caption"], proxy_config=proxy_config)
#             else:
#                 return data
#         else:
#             data = await get_video(info)
#         print(data, 'shu')
#         return data
#     except yt_dlp.utils.DownloadError as e:
#         error_message = str(e)
#         if "There is no video in this post" in error_message:
#             data = await get_instagram_post_images(post_url=url, caption="", proxy_config=proxy_config)
#             print(data, 'bizda')
#             return data
#         else:
#             pass
#             # print(f"❌ yt-dlp xatosi: {error_message}")
#             # return {"error": error_message}
#
#     except Exception as e:
#         print(f"Xatolik yuz berdi1: {e}")
#         return None