import yt_dlp
import time
import asyncio
from fastapi import HTTPException
import instaloader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By

import asyncio
from playwright.async_api import async_playwright
import yt_dlp
import aiohttp
from bs4 import BeautifulSoup




async def get_instagram_story_urls(username):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # username = f"https://www.instagram.com/stories/{username}/"
        try:
            await page.goto("https://sssinstagram.com/ru/story-saver")

            # Form input yuklanishini kutish
            await page.wait_for_selector(".form__input")

            # Username kiritish va tugmani bosish
            await page.fill(".form__input", username)
            await page.click(".form__submit")

            # Natijalar chiqishini kutish
            await page.wait_for_selector(".button__download", timeout=5000)  # 5 soniya kutish

            # Hikoya va thumbnail linklarini olish
            story_links = await page.locator(".button__download").all()
            thumbnail_links = await page.locator(".media-content__image").all()

            if not story_links:
                print(f"Hikoyalar topilmadi! ({username})")
                return []

            stories = []
            for i, story in enumerate(story_links):
                story_url = await story.get_attribute("href")
                thumbnail_url = await thumbnail_links[i].get_attribute("src") if i < len(thumbnail_links) else None
                stories.append({"donwload_link": story_url, "thumbnail_link": thumbnail_url})

            return {
                "status": "ok",
                "type": "stories",
                "username": username.split("/")[-2],
                "stories": stories
            }
        finally:
            await browser.close()



























async def get_video(info):
    data = {
            "status": "ok",
            "type": "video",
            "shortcode": info["id"],
            "caption": info.get("description", ""),
            "thumbnail": info["thumbnails"][-1]["url"] if "thumbnails" in info else None,
            "download_link": info["formats"][1]["url"] if "formats" in info else None,
            "like_count": info.get("like_count", 0),
            "comment_count": info.get("comment_count", 0),
            "duration": info.get("duration", 0),
            "author": {
                "id": info.get("uploader_id", ""),
                "username": info.get("channel", ""),
                "full_name": info.get("uploader", ""),
            }
        }
    return data

async def get_video_album(info):
    data = {
        "status": "ok",
        "type": "album",
        "shortcode": info["id"],
        "caption": info.get("description", ""),
        "medias": [
            {
                "type": "video",
                "download_link": entry["url"],
                "thumnail": entry["thumbnail"]
            }
            for entry in info["entries"]
        ]
    }
    return data


import asyncio
from urllib.parse import urlparse
from playwright.async_api import async_playwright, TimeoutError

async def get_instagram_post_images(post_url):
    """
    Instagram postidagi barcha rasm URLlarini olish (albumlarni ham to'liq yuklash)
    
    Args:
        post_url (str): Instagram post linki
        
    Returns:
        dict: Instagram postidagi barcha rasm URLlari va qo‘shimcha ma‘lumotlar
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            try:
                await page.goto(post_url, timeout=15000)  # 15 soniya ichida yuklanishi kerak
            except TimeoutError:
                return {"status": "error", "message": "Iltimos, URL'ni tekshiring va qayta urinib ko'ring."}

            caption = None
            caption_element = page.locator("span._ap3a._aaco._aacu._aacx._aad7._aade")
            if await caption_element.count() > 0:
                caption = await caption_element.text_content()

            # Shortcode ajratish
            path = urlparse(post_url).path
            shortcode = path.strip("/").split("/")[-1]

            try:
                await page.wait_for_selector("article", timeout=10000)
            except TimeoutError:
                return {"status": "error", "message": "Iltimos, URL'ni tekshiring va qayta urinib ko'ring."}

            # Rasmlar to‘plami
            image_urls = set()
            await page.mouse.click(10, 10)  
            await page.wait_for_timeout(100)

            while True:
                images = await page.locator("article ._aagv img").all()
                
                for img in images:
                    url = await img.get_attribute("src")
                    if url:
                        image_urls.add(url)
                
                next_button = page.locator("button[aria-label='Next']")
                if await next_button.count() > 0:
                    await next_button.click()
                    await page.wait_for_timeout(100)
                else:
                    break
            
            await browser.close()

            if not image_urls:
                return {"status": "error", "message": "Iltimos, URL'ni tekshiring va qayta urinib ko'ring."}

            return {
                "status": "ok",
                "type": "album" if len(image_urls) > 1 else "image",
                "shortcode": shortcode,
                "caption": caption,
                "medias": [
                    {
                        "type": "image",
                        "download_link": url,
                        "thumbnail": url
                    }
                    for url in image_urls
                ]
            }

    except Exception as e:
        return {"status": "error", "message": f"Xatolik yuz berdi: {str(e)}"}






#############################################3
import yt_dlp
import asyncio

async def download_instagram_media(url):
    loop = asyncio.get_running_loop()
    try:
        def extract():
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(None, extract)
        if "entries" in info:
            data = await get_video_album(info)
            print(data, 'tyl')
            if data["medias"] == []:
                data = await get_instagram_post_images(post_url=url)
            else:
                return data
        else:
            data = await get_video(info)
        print(data, 'shu')
        return data
    except yt_dlp.utils.DownloadError as e:
        error_message = str(e)
        if "There is no video in this post" in error_message:
            data = await get_instagram_post_images(post_url=url)
            print(data, 'bizda')
            return data
        else:
            pass
            # print(f"❌ yt-dlp xatosi: {error_message}")
            # return {"error": error_message}

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return None