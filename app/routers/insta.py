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

class Example:
    pass


app = FastAPI()

logger = logging.getLogger(__name__)



async def get_instagram_direct_links(post_url: str, db, request):
    """Instagram hikoyalarini yuklab olish va linklarni saqlash funksiyasi."""
    page = None
    async with request.app.state.restart_lock:
        try:
        # Sahifani navbatdan olish
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
                    break  # muvaffaqiyatli tugallangan bo'lsa, tsiklni to'xtatamiz
                except Exception as e:
                    print(f"⚠️ 111111111111111111111111: {e}")
                    error_message1 = await page.query_selector(".error-message__text")
                    if error_message1:
                        error_data = error_message1.text_content()
                        logger.info(f"Xato: {error_data}")
                        if "@имя" in error_message:
                            if attempt < max_retries - 1:  # ikkinchi urinishga o'tish
                                logger.info("Xatolik aniqlangan, URL qayta kiritilmoqda...")
                                continue  # URL'ni qayta kiritish
                            else:
                                print("Ikkinchi urinishdan so'ng xatolik mavjud.")
                                return {"error": True, "message": "Invalid response from the server"}
                        else:
                            pass
                            # return {"error": True, "message": f"Xatolik: {str(e)}"}

            # Yuklab olish linklari
            story_elements = await page.locator(".button__download").all()
            story_links = [await el.get_attribute("href") for el in story_elements if await el.get_attribute("href")]

            # Thumbnail linklari
            thumbnail_elements = await page.locator(".media-content__image").all()
            thumbnails = [await el.get_attribute("src") for el in thumbnail_elements if await el.get_attribute("src")]
            # logger.info(f"THUMBNAILS: {thumbnails}")

            # Sarlavha (title)
            title_elements = await page.locator(".output-list__caption p").all()
            titles = [await el.text_content() for el in title_elements]
            title = titles[0] if titles else None

            # Shortcode ajratish
            match = re.search(r'/p/([^/]+)/', post_url)
            shortcode = match.group(1) if match else "unknown"

            if not story_links:
                return {"error": True, "message": "Hech qanday media topilmadi."}

            def detect_type(url: str):
                return "image" if url.lower().endswith((".jpg", ".jpeg", ".png")) else "video"

            # Medialar ro'yxati
            medias = []

            for idx, media_url in enumerate(story_links):
                media_id = await generate_unique_id()
                media_download = Download(id=media_id, original_url=media_url)
                db.add(media_download)

                media_download_url = f"https://fast.videoyukla.uz/download?id={media_id}"

                thumb_url = thumbnails[idx] if idx < len(thumbnails) else None
                thumb_download_url = None

                if thumb_url and thumb_url.startswith("http"):
                    thumb_id = await generate_unique_id()
                    thumb_download = Download(id=thumb_id, original_url=thumb_url)
                    db.add(thumb_download)
                    thumb_download_url = f"https://fast.videoyukla.uz/download?id={thumb_id}"
                else:
                    thumb_download_url = media_download_url

                # Agar type image bo‘lsa thumbnail va media url bir xil bo‘ladi
                if detect_type(media_url) == "image":
                    thumb_download_url = media_download_url

                medias.append({
                    "type": detect_type(media_url),
                    "download_url": media_download_url,
                    "thumb": thumb_download_url
                })

            await db.commit()

            return {
                "error": False,
                "shortcode": shortcode,
                "hosting": "instagram",
                "type": "album" if len(medias) > 1 else detect_type(story_links[0]),
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

    # Agar 3 martadan keyin ham muvaffaqiyatsiz bo'lsa
    return {"error": True, "message": "Failed to download media after retries", "details": str(last_exception)}

# //##############################3333
# async def download_instagram_media(url, proxy_config, db, request):
#     loop = asyncio.get_running_loop()
#     try:
#         # Async wrapper for yt-dlp extraction
#         async def extract_info():
#             def sync_extract():
#                 proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
#                 options = {
#                     'quiet': True,
#                     'proxy': proxy_url,
#                     'extract_flat': False,
#                 }
#                 with yt_dlp.YoutubeDL(options) as ydl:
#                     return ydl.extract_info(url, download=False)

#             return await loop.run_in_executor(None, sync_extract)

#         info = await extract_info()
#         if "entries" in info and len(info["entries"]) > 1:
#             data = await get_video_album(info, url)
#         elif "formats" in info:
#             print("Get a video")
#             data = await get_video(info, url)
#         else:
#             print("Get media1")
#             data =  await get_instagram_direct_links(
#                 post_url=url,
#                 db=db,
#                 request=request
#             )
#         return data

#     except yt_dlp.utils.DownloadError as e:
#         error_message = str(e)

#         if "There is no video in this post" in error_message:
#             print("Get media2")
#             return await get_instagram_direct_links(
#                 post_url=url,
#                 db=db,
#                 request=request
#             )
#         print("Error", error_message)
#         return {"error": True, "message": "Invalid response from the server"}

#     except Exception as e:
#         print(f"Error downloading Instagram media: {str(e)}")
#         print(traceback.format_exc())
#         return {"error": True, "message": "Invalid response from the server"}



# async def get_instagram_image_and_album_and_reels(post_url, context):
#     print("📥 Media yuklanmoqda...")

#     try:
#         page = await context.new_page()
#         await page.goto(post_url)
#         print(page, "Page")
#         try:
#             await page.wait_for_selector("article", timeout=20000)
#         except Exception as e:
#             print(f"❌ 'section' elementi topilmadi: {e}")
#             return {"error": True, "message": "Invalid response from the server"}


#         await page.mouse.click(10, 10)
#         await page.wait_for_timeout(1500)

#         caption = None
#         if (caption_el := await page.query_selector('article span._ap3a')):
#             caption = await caption_el.inner_text()

#         media_list = []

#         while True:
#             # 1. RASMLAR faqat article section ichidan olinadi
#             images = await page.locator("article ._aagv img").all()
#             for img in images:
#                 src = await img.get_attribute("src")
#                 if src and not any(m["download_url"] == src for m in media_list):
#                     media_list.append({
#                         "type": "image",
#                         "download_url": src,
#                         "thumb": src
#                     })

#             # 2. VIDEOLAR faqat article section ichidan olinadi
#             videos = await page.locator("article video").all()
#             for video in videos:
#                 src = await video.get_attribute("src")
#                 poster = await video.get_attribute("poster")
#                 if src and not any(m["download_url"] == src for m in media_list):
#                     media_list.append({
#                         "type": "video",
#                         "download_url": src,
#                         "thumb": poster or src  # fallback
#                     })

#             # 3. Keyingi media (album ichidagi)
#             try:
#                 next_btn = page.locator("button[aria-label='Next']")
#                 await next_btn.wait_for(timeout=1500)
#                 await next_btn.click()
#                 await page.wait_for_timeout(1000)
#             except Exception:
#                 break

#         if not media_list:
#             print({"error": True, "message": "Hech qanday media topilmadi"})
#             return {"error": True, "message": "Invalid response from the server"}


#         # Shortcode ni URL dan olamiz
#         match = re.search(r'/p/([^/]+)/', post_url)
#         shortcode = match.group(1) if match else "unknown"

#         return {
#             "error": False,
#             "shortcode": shortcode,
#             "hosting": "instagram",
#             "type": "album" if len(media_list) > 1 else media_list[0]["type"],
#             "url": post_url,
#             "title": caption,
#             "medias": media_list
#         }

#     except Exception as e:
#         print(f"❗ Umumiy xatolik: {e}")
#         return {"error": True, "message": "Invalid response from the server"}

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
