import asyncio


from fastapi import FastAPI, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from playwright.async_api import async_playwright, Page

from models.user import User, ProxyServers, Download
from database.database import SessionLocal

from schema.user import UserCreate, User

from routers.insta_route import insta_router
from routers.proxy_route import proxies
from routers.yt_route import yt_router
from routers.sender import sender
# from routers.insta import browser_keepalive, close_browser
from routers.check import check_url
from routers.tiktok_route import tk_router
from fastapi.responses import FileResponse
from routers.cashe import generate_unique_id
from fastapi.responses import StreamingResponse
# from routers.new_inta import checker_router
import httpx
import os

app = FastAPI()
# app.include_router(checker_router)
app.include_router(insta_router)
app.include_router(proxies)
app.include_router(yt_router)
app.include_router(sender)
app.include_router(check_url)
app.include_router(tk_router)


MAX_PAGES = 25


# DB sessiyasini olish
# DB sessiyasini olish (Asinxron)
async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


async def generate_download(original_url: str, db: AsyncSession = Depends(get_db)):
    file_id = await generate_unique_id()
    new_link = Download(id=file_id, original_url=original_url)
    db.add(new_link)
    await db.commit()
    # return {"download_url": f"http://localhost:8000/download?id={file_id}"}
    return {"download_url": f"https://videoyukla.uz/download?id={file_id}"}





from fastapi import HTTPException
import httpx
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession


# @app.get("/download", include_in_schema=False)
# async def download_file(id: str, db: AsyncSession = Depends(get_db)):
#     result = await db.get(Download, id)
#     if not result or not hasattr(result, 'original_url'):
#         print("Status: Link not found or invalid")
#         raise HTTPException(status_code=404, detail="Link not found or invalid")

#     async def iterfile():
#         async with httpx.AsyncClient(follow_redirects=True, timeout=None) as client:
#             async with client.stream("GET", result.original_url) as response:
#                 if response.status_code != 200:
#                     print("Status: Cannot stream file")
#                     raise HTTPException(status_code=404, detail="Cannot stream file")

#                 async for chunk in response.aiter_bytes():
#                     yield chunk

#     return StreamingResponse(
#         iterfile(),
#         media_type="application/octet-stream",
#         headers={
#             "Content-Disposition": "attachment; filename=ziyotech"
#         }
#     )

# @app.get("/download", include_in_schema=False)
# async def download_file(id: str, db: AsyncSession = Depends(get_db)):
#     result = await db.get(Download, id)
#     if not result or not hasattr(result, 'original_url'):
#         print("Status: Link not found or invalid")
#         raise HTTPException(status_code=404, detail="Link not found or invalid")

#     async with httpx.AsyncClient(follow_redirects=True, timeout=None) as client:
#         head_resp = await client.head(result.original_url)
#         content_type = head_resp.headers.get("Content-Type", "application/octet-stream")

#         async def iterfile():
#             async with client.stream("GET", result.original_url) as response:
#                 if response.status_code != 200:
#                     print("Status: Cannot stream file")
#                     raise HTTPException(status_code=404, detail="Cannot stream file")

#                 async for chunk in response.aiter_bytes():
#                     yield chunk

#     return StreamingResponse(
#         iterfile(),
#         media_type=content_type,  # bu yerda aniqlangan MIME turi
#         headers={
#             "Content-Disposition": f"inline; filename=ziyotech"
#         }
#     )


@app.get("/download", include_in_schema=False)
async def download_file(id: str, db: AsyncSession = Depends(get_db)):
    # Ma'lumotni bazadan olish
    result = await db.get(Download, id)
    if not result or not hasattr(result, 'original_url'):
        print("Status: Link not found or invalid")
        raise HTTPException(status_code=404, detail="Link not found or invalid")

    # HEAD so'rovni alohida client bilan yuboramiz
    async with httpx.AsyncClient(follow_redirects=True, timeout=None) as head_client:
        head_resp = await head_client.head(result.original_url)
        content_type = head_resp.headers.get("Content-Type", "application/octet-stream")

    async def iterfile():
        # Streaming uchun clientni shu yerda ochamiz
        async with httpx.AsyncClient(follow_redirects=True, timeout=None) as stream_client:
            async with stream_client.stream("GET", result.original_url) as response:
                if response.status_code != 200:
                    print("Status: Cannot stream file")
                    raise HTTPException(status_code=404, detail="Cannot stream file")

                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        iterfile(),
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="ziyotech"',
        }
    )

async def get_proxy_config():
    async with SessionLocal() as db:
        try:
            result = await db.execute(
                select(ProxyServers)
                .filter(ProxyServers.instagram == True)
                .order_by(func.random())  
                .limit(1)  
            )
            _proxy = result.scalars().first()

            if not _proxy:  
                print("No proxy servers available in the database.")
                return None

            proxy_config = {    
                "server": f"http://{_proxy.proxy}",
                "username": _proxy.username,
                "password": _proxy.password
            }
            return proxy_config
        
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None


@app.on_event("startup")
async def startup():
    proxy_config = await get_proxy_config()
    playwright = await async_playwright().start()

    # Proxy bilan browser
    proxy_options = {
        'headless': True,
        'args': ['--no-sandbox', '--disable-setuid-sandbox']
    }
    if proxy_config:
        proxy_options['proxy'] = {
            'server': f"http://{proxy_config['server'].replace('http://', '')}",
            'username': proxy_config['username'],
            'password': proxy_config['password']
        }
    browser_proxy = await playwright.chromium.launch(**proxy_options)
    context_proxy = await browser_proxy.new_context()
    app.state.browser = browser_proxy
    app.state.context = context_proxy

    # Proxysiz browser
    browser_noproxy = await playwright.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    context_noproxy = await browser_noproxy.new_context()
    app.state.browser_noproxy = browser_noproxy
    app.state.context_noproxy = context_noproxy

    PAGE_POOL = asyncio.Queue()
    app.state.page_pool = PAGE_POOL
    

    print("✅ Proxy bilan:", browser_proxy, context_proxy)
    print("✅ Proxysiz:", browser_noproxy, context_noproxy)


    for _ in range(10):
        page = await context_proxy.new_page()
        await page.goto("https://sssinstagram.com/ru/story-saver", wait_until="load")
        await PAGE_POOL.put(page)

    # Avtomatik yangilanish uchun sahifalar qo'shish
    async def add_page_loop():
        while True:
            await asyncio.sleep(1)
            if PAGE_POOL.qsize() < MAX_PAGES:
                page = await context_proxy.new_page()
                await page.goto("https://sssinstagram.com/ru/story-saver", wait_until="load")
                await PAGE_POOL.put(page)
    asyncio.create_task(add_page_loop())

    asyncio.create_task(restart_browser_loop())



# @app.on_event("startup")
# async def startup():
#     proxy_config = await get_proxy_config()
#     playwright = await async_playwright().start()

#     # Proxy bilan browser
#     proxy_options = {
#         'headless': True,
#         'args': ['--no-sandbox', '--disable-setuid-sandbox']
#     }
#     if proxy_config:
#         proxy_options['proxy'] = {
#             'server': f"http://{proxy_config['server'].replace('http://', '')}",
#             'username': proxy_config['username'],
#             'password': proxy_config['password']
#         }
#     browser_proxy = await playwright.chromium.launch(**proxy_options)
#     context_proxy = await browser_proxy.new_context()
#     app.state.browser = browser_proxy
#     app.state.context = context_proxy

#     # Proxysiz browser
#     browser_noproxy = await playwright.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
#     context_noproxy = await browser_noproxy.new_context()
#     app.state.browser_noproxy = browser_noproxy
#     app.state.context_noproxy = context_noproxy

#     PAGE_POOL = asyncio.Queue()
#     app.state.page_pool = PAGE_POOL

#     print("✅ Proxy bilan:", browser_proxy, context_proxy)
#     print("✅ Proxysiz:", browser_noproxy, context_noproxy)

#     # Sahifa yaratish
#     page = await context_noproxy.new_page()
#     await page.goto("https://sssinstagram.com/ru/story-saver", wait_until="load")
#     await PAGE_POOL.put(page)

#     # Avtomatik page qo'shish
#     async def add_page_loop():
#         while True:
#             await asyncio.sleep(1)
#             if PAGE_POOL.qsize() < MAX_PAGES:
#                 page = await app.state.context_noproxy.new_page()
#                 await page.goto("https://sssinstagram.com/ru/story-saver", wait_until="load")
#                 await PAGE_POOL.put(page)
#     asyncio.create_task(add_page_loop())

#     # 🔥 Browser restart qilish
#     asyncio.create_task(restart_browser_loop())




@app.on_event("shutdown")
async def shutdown():
    await app.state.browser.close()
    await app.state.context.close()
    await app.state.browser_noproxy.close()
    await app.state.browser_proxy.close()
    await app.state.context_noproxy.close()
    await app.state.context_proxy.close()
    print("Browser closes")



async def restart_browser_loop():
    while True:
        await asyncio.sleep(5 * 60)  # Har 3 soatda browserni yangilaymiz

        print("♻️ Browser va context restart qilinmoqda...")

        try:
            # Eski browser va contextni tozalaymiz
            await app.state.context_noproxy.close()
            await app.state.browser_noproxy.close()

            playwright = await async_playwright().start()
            browser_noproxy = await playwright.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            context_noproxy = await browser_noproxy.new_context()
            
            app.state.browser_noproxy = browser_noproxy
            app.state.context_noproxy = context_noproxy

            # Eski PAGE_POOL ni yangilaymiz
            PAGE_POOL = asyncio.Queue()
            app.state.page_pool = PAGE_POOL

            # 1 dona yangi sahifa ochamiz
            page = await context_noproxy.new_page()
            await page.goto("https://sssinstagram.com/ru/story-saver", wait_until="load")
            await PAGE_POOL.put(page)

            print("♻️ Browser va context yangilandi!")
        
        except Exception as e:
            print(f"♻️ Browserni yangilashda xatolik: {e}")




# import time

# import re
# from urllib.parse import urlparse


# @app.get("/instagram/check/")
# async def scrape_instagram_post(url: str):
#     page = await PAGE_POOL.get()
#     try:
#         curr_time = time.time()
#         result = await get_instagram_image_and_album_and_reels(url, page)
#         print(time.time() - curr_time)
#         return result

#     finally:
#         # await page.goto("about:blank")  # Sahifani tozalash
#         if not page.is_closed():
#             await PAGE_POOL.put(page)

# async def get_instagram_image_and_album_and_reels(post_url, page: Page):
#     print("📥 Media yuklanmoqda...")

#     try:
#         # print(page, "one")
#         # match = re.search(r'https://www.instagram.com/p/([^/?]+)', post_url)
#         # if not match:
#         #     return {"error": True, "message": "Invalid URL format"}

#         # post_path = f"/p/{match.group(1)}/"
#         # full_url = f"https://www.instagram.com{post_path}"

#         # await page.evaluate(f"window.location.href = '{full_url}'")
#         # await page.goto(full_url, timeout=20000, wait_until="load")
#         # parsed_url = urlparse(post_url)
#         # path_parts = parsed_url.path.strip("/").split("/")

#         # # Tekshirish: p bo'limi va shortcode borligini aniqlash
#         # if len(path_parts) < 2 or path_parts[0] != "p":
#         #     return {"error": True, "message": "Invalid Instagram post URL"}

#         # # Shortcode ajratiladi
#         # shortcode = path_parts[1]

#         # full_url = f"https://www.instagram.com/p/{shortcode}/"

#         # await page.evaluate(f"window.location.href = '{full_url}'")


#         # print(page, "Page", full_url)
#         # await asyncio.sleep(1)
#         # await page.screenshot(path="screenshot.png", full_page=True)
#         match = re.search(r"https://www\.instagram\.com/p/([^/?#&]+)", post_url)
#         if not match:
#             return {"error": True, "message": "❌ Noto‘g‘ri URL format"}

#         shortcode = match.group(1)
#         full_url = f"https://www.instagram.com/p/{shortcode}/"

#         # await page.goto(full_url, wait_until="networkidle")

#         await page.evaluate(f"window.location.href = '{full_url}'")

#         await asyncio.sleep(1)


#         await page.mouse.click(10, 10)

#         # Post yuklanishini kutamiz
#         try:
#             await page.wait_for_selector("article", timeout=20000)
#         except Exception as e:
#             print(f"❌ 'section' elementi topilmadi: {e}")
#             return {"error": True, "message": "Invalid response from the server"}


#         await page.mouse.click(10, 10)
#         # await page.wait_for_timeout(1500)

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
#                 await next_btn.wait_for(timeout=500)
#                 await next_btn.click()
#                 await page.wait_for_timeout(500)
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
#         print(f"❗ Xatolik: {e}")
#         return {"error": True, "message": "Server error"}

#     finally:
#         await PAGE_POOL.put(page)
