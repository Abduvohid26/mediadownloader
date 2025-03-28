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


import re
from playwright.async_api import async_playwright

import re
from playwright.async_api import async_playwright, TimeoutError

async def get_instagram_story_urls(username, proxy_config):
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True, proxy=proxy_config)
            page = await browser.new_page()

            try:
                await page.goto("https://sssinstagram.com/ru/story-saver", timeout=2000)
            except TimeoutError:
                print("1")
                return {"error": True, "message": "Invalid response from the server"}

            match = re.search(r"stories/([^/]+)/", username)
            uname = match.group(1) if match else username

            try:
                await page.wait_for_selector(".form__input", timeout=2000)
                await page.fill(".form__input", username)
                await page.click(".form__submit")
            except TimeoutError:
                print("2")
                return {"error": True, "message": "Invalid response from the server"}

            try:
                await page.wait_for_selector(".button__download", timeout=3000)
            except TimeoutError:
                print("3")
                return {"error": True, "message": "Invalid response from the server"}

            story_links = await page.locator(".button__download").all()
            thumbnail_links = await page.locator(".media-content__image").all()

            if not story_links:
                print("4")
                return {"error": True, "message": "Invalid response from the server"}

            stories = set()
            for i in range(min(len(story_links), len(thumbnail_links))):
                try:
                    story_url = await story_links[i].get_attribute("href")
                    thumbnail_url = await thumbnail_links[i].get_attribute("src")
                    if story_url:
                        stories.add((story_url, thumbnail_url))
                except TimeoutError:
                    print("5")
                    return {"error": True, "message": "Invalid response from the server"}
            await browser.close()
            if not stories:
                print("6")
                return {"error": True, "message": "Invalid response from the server"}

            return {
                "error": False,
                "hosting": "instagram",
                "type": "stories",
                "username": uname,
                "medias": [{"download_url": url, "thumb": thumb} for url, thumb in stories]
            }
        except TimeoutError:
            print("7")
            return {"error": True, "message": "Invalid response from the server"}
        except Exception as e:
            print("8", e)
            return {"error": True, "message": "Invalid response from the server"}


# async def get_instagram_story_urls(username):
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()
#         try:
#             await page.goto("https://sssinstagram.com/ru/story-saver")
#             match = re.search(r"stories/([^/]+)/", username)
#             uname = match.group(1) if match else username

#             await page.wait_for_selector(".form__input", timeout=10000)
#             await page.fill(".form__input", uname)
#             await page.click(".form__submit")

#             await page.wait_for_selector(".button__download", timeout=20000)
            
#             story_links = await page.locator(".button__download").all()
#             thumbnail_links = await page.locator(".media-content__image").all()
            
#             print(f"Found {len(story_links)} story links and {len(thumbnail_links)} thumbnails")
            
#             if not story_links:
#                 return {"error": True, "message": "Invalid response from the server", "username": uname}

#             stories = set()
#             num_stories = min(len(story_links), len(thumbnail_links))
            
#             for i in range(num_stories):
#                 story_url = await story_links[i].get_attribute("href")
#                 thumbnail_url = await thumbnail_links[i].get_attribute("src")
                
#                 if story_url and story_url not in stories:
#                     stories.add((story_url, thumbnail_url))

#             return {
#                 "error": False,
#                 "hosting": "instagram",
#                 "type": "stories",
#                 "username": uname,
#                 "medias": [{"download_url": url, "thumb": thumb} for url, thumb in stories]
#             }
#         except Exception as e:
#             print("Error", e)
#             return {"error": True, "message": "Invalid response from the server"}
#         finally:
#             await browser.close()




# async def get_instagram_story_urls(username):
#     async with async_playwright() as p:
#         try:
#             browser = await p.chromium.launch(
#                 headless=True,
#                 args=[
#                     '--no-sandbox',
#                     '--disable-setuid-sandbox',
#                     '--disable-dev-shm-usage'
#                 ]
#             )
#             context = await browser.new_context()
#             page = await context.new_page()
            
#             page.set_default_timeout(10000)
            
#             try:
#                 await page.goto("https://sssinstagram.com/ru/story-saver", wait_until="domcontentloaded")
                
#                 try:
#                     await page.wait_for_selector(".form__input", timeout=10000)
                    
#                     await page.fill(".form__input", username)
#                     await page.click(".form__submit")
                    
#                     try:
#                         await page.wait_for_selector(".button__download", timeout=10000)
                        
#                         story_links = await page.locator(".button__download").all()
#                         thumbnail_links = await page.locator(".media-content__image").all()
                        
#                         if not story_links:
#                             print(f"Hikoyalar topilmadi! ({username})")
#                             return {
#                                 "error": True,
#                                 "message": "Invalid response from the server"
#                             }
                        
#                         stories = []
#                         for i, story in enumerate(story_links):
#                             try:
#                                 story_url = await story.get_attribute("href")
#                                 thumbnail_url = await thumbnail_links[i].get_attribute("src") if i < len(thumbnail_links) else None
#                                 stories.append({
#                                     "download_link": story_url,  # Typo fix: donwload_link -> download_link
#                                     "thumbnail_link": thumbnail_url
#                                 })
#                             except Exception as e:
#                                 print(f"Element atributlarini olishda xato: {str(e)}")
#                                 continue
                        
#                         return {
#                             "status": "ok",
#                             "type": "stories",
#                             "username": username,
#                             "stories": stories
#                         }
                        
#                     except Exception as e:
#                         print(f"Natijalarni kutishda xato: {str(e)}")
#                         return {
#                                 "error": True,
#                                 "message": "Invalid response from the server"
#                             }
                        
#                 except Exception as e:
#                     print(f"Formani to'ldirishda xato: {str(e)}")
#                     return {
#                             "error": True,
#                             "message": "Invalid response from the server"
#                             }
                    
#             except Exception as e:
#                 print(f"Sahifaga kirishda xato: {str(e)}")
#                 return {
#                         "error": True,
#                         "message": "Invalid response from the server"
#                         }
                
#         except Exception as e:
#             print(f"Brauzerni ishga tushirishda xato: {str(e)}")
#             return {
#                     "error": True,
#                     "message": "Invalid response from the server"
#                     }
            
#         finally:
#             await browser.close()
























async def get_video(info):
    data = {
            "error": False,
            "hosting": "instagram",
            "type": "video",
            "shortcode": info["id"],
            "caption": info.get("description", ""),
            "thumbnail": info["thumbnails"][-1]["url"] if "thumbnails" in info else None,
            "download_url": info["formats"][1]["url"] if "formats" in info else None,
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

# async def get_instagram_post_images(post_url):
#     """
#     Instagram postidagi barcha rasm URLlarini olish (albumlarni ham to'liq yuklash)
    
#     Args:
#         post_url (str): Instagram post linki
        
#     Returns:
#         dict: Instagram postidagi barcha rasm URLlari va qo‘shimcha ma‘lumotlar
#     """
#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(headless=True)
#             page = await browser.new_page()

#             try:
#                 await page.goto(post_url, timeout=2000)  # 15 soniya ichida yuklanishi kerak
#             except TimeoutError:
#                 print("time out")
#                 return {"error": True, "message": "Invalid response from the server"}

#             caption = None
#             caption_element = page.locator("span._ap3a._aaco._aacu._aacx._aad7._aade")
#             if await caption_element.count() > 0:
#                 caption = await caption_element.text_content()

#             # Shortcode ajratish
#             path = urlparse(post_url).path
#             shortcode = path.strip("/").split("/")[-1]

#             try:
#                 await page.wait_for_selector("article", timeout=1500)
#             except TimeoutError:
#                 print("Time 1")
#                 return {"error": True, "message": "Invalid response from the server"}

#             # Rasmlar to‘plami
#             image_urls = set()
#             await page.mouse.click(10, 10)  
#             await page.wait_for_timeout(100)

#             while True:
#                 images = await page.locator("article ._aagv img").all()
                
#                 for img in images:
#                     url = await img.get_attribute("src")
#                     if url:
#                         image_urls.add(url)
                
#                 next_button = page.locator("button[aria-label='Next']")
#                 if await next_button.count() > 0:
#                     await next_button.click()
#                     await page.wait_for_timeout(100)
#                 else:
#                     break
            
#             await browser.close()

#             if not image_urls:
#                 print("noy url")
#                 return {"error": True, "message": "Invalid response from the server"}

#             return {
#                 "error": False,
#                 "hosting": "instagram",
#                 "type": "album" if len(image_urls) > 1 else "image",
#                 "shortcode": shortcode,
#                 "caption": caption,
#                 "medias": [
#                     {
#                         "type": "image",
#                         "download_url": url,
#                         "thumb": url
#                     }
#                     for url in image_urls
#                 ]
#             }

#     except Exception as e:
#             print("Error:", str(e))
#             return {"error": True, "message": "Invalid response from the server"}

from urllib.parse import urlparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def get_instagram_post_images(post_url, caption, proxy_config):
    """
    Instagram postidagi barcha rasm URLlarini olish (albumlarni ham to'liq yuklash)
    
    Args:
        post_url (str): Instagram post linki
        
    Returns:
        dict: Instagram postidagi barcha rasm URLlari va qo‘shimcha ma‘lumotlar
    """
    browser = None  # Browserni boshlang'ich qiymatga o‘rnatish
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, proxy=proxy_config)
            page = await browser.new_page()

            try:
                await page.goto(post_url, timeout=2500)  # 15 soniya ichida yuklanishi kerak
            except PlaywrightTimeoutError:
                print("⏳ Time out!1")
                return {"error": True, "message": "Invalid response from the server"}

            # caption = None
            # caption_element = page.locator("span._ap3a._aaco._aacu._aacx._aad7._aade")
            # if await caption_element.count() > 0:
            #     caption = await caption_element.text_content()

            # Shortcode ajratish
            path = urlparse(post_url).path
            shortcode = path.strip("/").split("/")[-1]

            try:
                await page.wait_for_selector("article", timeout=1500)
            except PlaywrightTimeoutError:
                print("🔄 Timeout while waiting for article")
                return {"error": True, "message": "Invalid response from the server"}

            # Rasmlar to‘plami
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
                    await page.wait_for_timeout(500)  # 2 soniya kutish
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
                "medias": [
                    {
                        "type": "image",
                        "download_url": url,
                        "thumb": url
                    }
                    for url in image_urls
                ]
            }

    except Exception as e:
        print("❌ Error:", str(e))
        return {"error": True, "message": "Invalid response from the server"}

    finally:
        if browser is not None:
            await browser.close()  # Browserni har doim yopish





#############################################3
import yt_dlp
import asyncio

async def download_instagram_media(url, proxy_config):
    loop = asyncio.get_running_loop()
    try:
        def extract():
            proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
            with yt_dlp.YoutubeDL({'quiet': True, 'proxy': proxy_url}) as ydl:
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