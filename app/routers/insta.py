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
import re
from playwright.async_api import async_playwright

import re
from playwright.async_api import async_playwright, TimeoutError



_browser = None
_playwright = None


async def init_browser(proxy_config):
    """ Brauzerni, contextni va sahifani oldindan ochib qo‘yish """
    global _browser, _context, _page, _playwright
    if _browser is None:
        print("🔄 Yangi brauzer ishga tushdi...")
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
            proxy=proxy_config
        )
        _context = await _browser.new_context()
        _page = await _context.new_page()  

        await _page.goto("https://sssinstagram.com/ru/story-saver", timeout=10000) 
        await _page.wait_for_load_state("domcontentloaded")


    print("Mavjud", _context)
    return _browser, _context, _page

async def close_browser():
    """ Brauzerni to‘g‘ri yopish """
    global _browser, _playwright
    if _browser:
        print("❌ Brauzer yopildi")
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None

async def browser_keepalive(proxy_config, interval=1000):
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
        thumbnail_links = [await el.get_attribute("src") for el in await page.locator(".media-content__image").all()]

        if not story_links:
            return {"error": True, "message": "Invalid response from the server"}

        return {
            "error": False,
            "hosting": "instagram",
            "type": "stories",
            "username": username,
            "medias": [{"download_url": url, "thumb": thumb} for url, thumb in zip(story_links, thumbnail_links)]
        }
    except Exception as e:
        return {"error": True, "message": f"Error: {e}"}



async def get_video(info):
    data = {
            "error": False,
            "hosting": "instagram",
            "type": "video",
            "shortcode": info["id"],
            "caption": info.get("description", ""),
            "thumbnail": info["thumbnails"][-1]["url"] if "thumbnails" in info else None,
            "download_url": info["url"]
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
                "type": "video",
                "download_url": entry["url"],
                "thumbnail": entry["thumbnail"]
            }
            for entry in info["entries"]
        ]
    }
    return data


import asyncio
from urllib.parse import urlparse
from playwright.async_api import async_playwright, TimeoutError


_browser_image = None
_playwright_image = None

async def init_browser_images(proxy_config):
    """ Brauzerni, contextni va sahifani oldindan ochib qo‘yish """
    global _browser_image, _playwright_image
    if _browser_image is None:
        print("🔄 Yangi brauzer ishga tushdi Images...")
        _playwright_image = await async_playwright().start()
        _browser_image = await _playwright_image.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
            proxy=proxy_config
        )
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
        browser = await init_browser_images(proxy_config=proxy_config)  
        page = await browser.new_page()  
        
        try:
            await page.goto(post_url, timeout=15000)
        except PlaywrightTimeoutError:
            print("⏳ Time out!1")
            return {"error": True, "message": "Invalid response from the server"}

        path = urlparse(post_url).path
        shortcode = path.strip("/").split("/")[-1]

        try:
            await page.wait_for_selector("article", timeout=15000)
        except PlaywrightTimeoutError:
            print("🔄 Timeout while waiting for article")
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
                await next_button.click()
                await page.wait_for_timeout(500)
            else:
                break

        if not image_urls:
            print("🚫 No image URLs found")
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
        print("❌ Error:", str(e))
        return {"error": True, "message": "Invalid response from the server"}





#############################################
import yt_dlp
import asyncio

async def download_instagram_media(url, proxy_config):
    loop = asyncio.get_running_loop()
    try:
        def extract():
            proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
            print(proxy_url, 'proxy url')
            options = {
                'quiet': True,
                'proxy': proxy_url,
            }
            with yt_dlp.YoutubeDL(options) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(None, extract)
        if "entries" in info:
            data = await get_video_album(info)
            print(data, 'tyl')
            if data["medias"] == []:
                data = await get_instagram_post_images(post_url=url, caption=data["caption"], proxy_config=proxy_config)
            else:
                return data
        else:
            data = await get_video(info)
        print(data, 'shu')
        return data
    except yt_dlp.utils.DownloadError as e:
        error_message = str(e)
        if "There is no video in this post" in error_message:
            data = await get_instagram_post_images(post_url=url, caption="", proxy_config=proxy_config)
            print(data, 'bizda')
            return data
        else:
            pass
            # print(f"❌ yt-dlp xatosi: {error_message}")
            # return {"error": error_message}

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return None