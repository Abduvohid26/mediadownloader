import traceback
import logging
import yt_dlp
import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from fastapi import FastAPI
from .model import BrowserManager


class Example:
    pass


app = FastAPI()

logger = logging.getLogger(__name__)

manager = BrowserManager(proxy_config=None, interval=200)


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



async  def get_instagram_image_and_album_and_reels(post_url, proxy_config):
    print("Bizdan salomlar")

    try:
        await manager.init_browser(action="instagram")
        page = await manager.context.new_page()

        try:
            await page.goto(post_url, timeout=15000)
        except PlaywrightTimeoutError:
            return {"error": True, "message": "⏳ Sahifani yuklash muddati tugadi"}

        try:
            await page.wait_for_selector("article", timeout=20000)
        except PlaywrightTimeoutError:
            logger.error("🔄 Sahifada article elementi topilmadi")
            return {"error": True, "message": "Invalid response from the server"}
        
        image_urls = set()
        video_data = []

        await page.mouse.click(10, 10)
        await page.wait_for_timeout(1500)
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

            # Keyingi tugmasini aniqlash
            next_button = page.locator("button[aria-label='Next']")
            try:
                await next_button.wait_for(timeout=3000)
            except PlaywrightTimeoutError:
                break  # Endi keyingi media yo‘q

            prev_count = len(image_urls) + len(video_data)

            await next_button.click()
            await page.wait_for_timeout(1000)

            # Yangi rasm yoki video chiqmagan bo‘lsa, to‘xtaymiz
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
            logger.error(msg="🚫 Media URLlari topilmadi")
            return {"error": True, "message": "Invalid response from the server"}

        media_items = [{"type": "image", "download_url": url} for url in image_urls]
        media_items += video_data  # videolarni ham qo‘shamiz

        return {
            "error": False,
            "hosting": "instagram",
            "type": "album" if len(media_items) > 1 else media_items[0]["type"],
            "caption": caption,
            "medias": media_items
        }
    except Exception as e:
        print(f"Error: {e}")
        return {"error": True, "message": "Invalid response from the server"}