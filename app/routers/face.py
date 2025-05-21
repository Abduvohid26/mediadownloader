



import asyncio
import yt_dlp
from playwright.async_api import async_playwright
from urllib.parse import urlparse

async def scrape_facebook_album_json(album_url: str, request):
    page = None
    # async with request.app.state.restart_lock:
    click_info = request.app.state.click_info

    if click_info is True:
        print({"success": False, "message": "Restart time bro"})
        return await download_from_facebook_extra(album_url, request)
        # return {"success": False, "message": "Restart time bro"}

    try:
        page = await asyncio.wait_for(request.app.state.page_pool3.get(), timeout=10)
    except asyncio.TimeoutError:
            return {"error": True, "message": "Server band. Iltimos, keyinroq urinib ko‘ring."}
    try:
        path = urlparse(album_url).path.lstrip("/")
        full_url = f"https://facebook.com/{path}"
        await page.evaluate(f"window.location.href = '{full_url}'")
        await page.wait_for_timeout(4000)
        # await page.screenshot(path="screenshot.png", full_page=True)
        medias = []

        # await page.wait_for_timeout(1000)
        # await page.mouse.click(10, 10)

        # 📷 Rasmlar
        img_elements = await page.locator("div.x10l6tqk.x13vifvy img").all()

        for img in img_elements:
            src = await img.get_attribute("src")
            if (
                src and
                "scontent" in src and
                "fbcdn" in src and
                not any(bad in src for bad in ["emoji", "static", "profile", "safe_image"])
            ):
                medias.append({
                    "type": "image",
                    "download_url": src,
                    "thumb": src
                })

        # # 🎥 Videolar
        # video_elements = await page.locator("div[role=article] video source[src*='fbcdn']").all()

        # for video in video_elements:
        #     video_src = await video.get_attribute("src")
        #     thumb = await video.get_attribute("poster")
        #     if video_src and "scontent" in video_src:
        #         medias.append({
        #             "type": "video",
        #             "download_url": video_src,
        #             "thumb": thumb if thumb else video_src
        #         })

        result = {
            "error": False,
            "shortcode": "unknown",
            "hosting": "facebook",
            "type": "album",
            "url": album_url,
            "title": None,
            "medias": medias
        }

        return result
    except Exception as e:
        print("Xatolik yuz berdi:", e)
        return {"error": True, "message": "Error response from the server."}
    
    finally:
        if page:
            await page.close()
        




async def download_from_facebook_extra(album_url, request):
    """Snaptik orqali TikTok videolarini yuklab olish funksiyasi."""
    page = None

    try:
        context = request.app.state.extra_context
        page = await context.new_page()
        await page.goto("https://facebook.com", wait_until="load", timeout=7000)
    except Exception as e:
        print(f"Xatolik yuzb berdi: {e}")
        return {"error": True, "message": "Error response from the server."}
    
    try:
        path = urlparse(album_url).path.lstrip("/")
        full_url = f"https://facebook.com/{path}"
        await page.evaluate(f"window.location.href = '{full_url}'")
        await page.wait_for_timeout(2000)

        medias = []

        await page.wait_for_timeout(1000)
        await page.mouse.click(10, 10)

        # 📷 Rasmlar
        img_elements = await page.locator("div.x10l6tqk.x13vifvy img").all()

        for img in img_elements:
            src = await img.get_attribute("src")
            if (
                src and
                "scontent" in src and
                "fbcdn" in src and
                not any(bad in src for bad in ["emoji", "static", "profile", "safe_image"])
            ):
                medias.append({
                    "type": "image",
                    "download_url": src,
                    "thumb": src
                })
        result = {
            "error": False,
            "shortcode": "unknown",
            "hosting": "facebook",
            "type": "album",
            "url": album_url,
            "title": None,
            "medias": medias
        }

        return result
    except Exception as e:
        print("Xatolik yuz berdi:", e)
        return {"error": True, "message": "Error response from the server."}
    
    finally:
        if page:
            await page.close()
        
        






async def get_video(query, post_url):
    return {
        "error": False,
        "shortcode": None,
        "hosting": "facebook",
        "type": "video",
        "url": post_url,
        "title": query.get("title"),
        "medias": [
            {
                "type": "video",
                "download_url": query.get("url"),
                "thumb": query.get("thumbnails")[0].get("url", None)
            }
        ]
    }
from .proxy_route import get_proxy_config

async def get_facebook_video(post_url, proxy, request):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best[ext=mp4]",
        "noplaylist": True,
        "skip_download": True,
        "n_connections": 4,
        "socket_timeout": 30,
        "retries": 2,
    }

    proxy_config = await get_proxy_config()
    if proxy_config:
        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
        ydl_opts['proxy'] = proxy_url

    loop = asyncio.get_running_loop()

    for attempt in range(3):  # 3 martagacha urinish
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(post_url, download=False))
            return await get_video(info, post_url)
        except yt_dlp.utils.DownloadError as e:
            error_message = str(e)
            if "There is no video in this post" or "This video is only available for registered users" in error_message:
                return await scrape_facebook_album_json(post_url, request)
            
            error_message = str(e)
            print(f"[Attempt {attempt + 1}] DownloadError: {error_message}")
            
            
            if attempt == 2:  
                return {"error": True, "message": f"Download failed after 3 attempts: {error_message}"}
        
        except Exception as e:
            print(f"[Attempt {attempt + 1}] Unexpected error: {e}")
            if attempt == 2:
                return {"error": True, "message": f"Invalid response from the server: {e}"}
