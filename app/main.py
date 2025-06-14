import asyncio

from fastapi import FastAPI, Depends, HTTPException, Request

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from playwright.async_api import async_playwright, Page

from models.user import User, ProxyServers, Download
from database.database import SessionLocal

from schema.user import UserCreate, User
from urllib.parse import urlparse

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
from routers.face_route import face
from routers.yt_search.test_route import test_route
from routers.yt_search.search_route import search_youtube
from routers.shazam_.shazam_route import shazam_router
from routers.track.route import track_router
from routers.platforms.route import platform_route
from routers.new_track.route import new_track_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import httpx
import httpx

EMAIL_FACEBOOK = "abduvohidabdujalilov92@gmail.com"
EMAIL_PASSWORD = "20042629ab"

app = FastAPI()


app.mount("/media", StaticFiles(directory="media"), name="media")

origins = [
    "http://localhost:3000",   # agar React localda bo‘lsa
    "http://127.0.0.1:3000",   # bu ham kerak bo‘lishi mumkin
    "http://localhost:8000",   # agar React localda bo‘lsa
    "https://frontend.example.com",  # agar deploy qilingan bo‘lsa
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # yoki ['*'] barcha manzillar uchun
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE hammasi
    allow_headers=["*"],           
)
app.state.restart_lock = asyncio.Lock()
app.include_router(new_track_router)
app.include_router(platform_route)
# app.include_router(track_router)
# app.include_router(test_route)
app.include_router(insta_router)
app.include_router(proxies)
app.include_router(yt_router)
app.include_router(sender)
app.include_router(check_url)
app.include_router(tk_router)
app.include_router(face)
# app.include_router(shazam_router)
# app.include_router(search_youtube)

MAX_PAGES = 4


# DB sessiyasini olish
# DB sessiyasini olish (Asinxron)
async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db

# @app.get("/")
# async def read_root():
#     return {"message": "Hello, World!"}


async def generate_download(original_url: str, db: AsyncSession = Depends(get_db)):
    file_id = await generate_unique_id()
    new_link = Download(id=file_id, original_url=original_url)
    db.add(new_link)
    await db.commit()
    # return {"download_url": f"http://localhost:8000/download?id={file_id}"}
    return {"download_url": f"https://videoyukla.uz/download?id={file_id}"}

# import os
# @app.get("/get/image")
# async def get_image():
#     file_path = "screenshot.png"
#     if os.path.exists(file_path):
#         return FileResponse(file_path)
#     return {"error": "File not found"}


@app.get("/download", include_in_schema=False)
async def download_file(id: str, db: AsyncSession = Depends(get_db)):
    # Ma'lumotni bazadan olish
    result = await db.get(Download, id)
    if not result or not hasattr(result, 'original_url'):
        print("Status: Link not found or invalid")
        raise HTTPException(status_code=404, detail="Link not found or invalid")

    # URLni to'g'ri formatlash va protokolda xato yo'qligini tekshirish
    url = result.original_url
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url  # Protokolni qo'shish

    # URL formatini tekshirish
    parsed_url = urlparse(url)
    if not parsed_url.netloc:  # Agar host (domain) bo'lmasa
        raise HTTPException(status_code=400, detail="Invalid URL: missing domain")

    # HEAD so'rovni yuborish
    async with httpx.AsyncClient(follow_redirects=True, timeout=None) as head_client:
        try:
            head_resp = await head_client.head(url)
            head_resp.raise_for_status()  # 4xx yoki 5xx xatoliklari uchun
            content_type = head_resp.headers.get("Content-Type", "application/octet-stream")
        except httpx.HTTPStatusError as e:
            print(f"Status: {e.response.status_code} - Cannot access file")
            raise HTTPException(status_code=404, detail="Cannot access file")
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    # Faylni uzatish uchun generator
    async def iterfile():
        async with httpx.AsyncClient(follow_redirects=True, timeout=None) as stream_client:
            async with stream_client.stream("GET", url) as response:
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
    app.state.click_info = False
    playwright = await async_playwright().start()
    app.state.playwright = playwright  # Stopda to‘xtatish uchun kerak bo‘lishi mumkin
    common_args = {'headless': True, 'args': ['--no-sandbox', '--disable-setuid-sandbox']}
    proxy_config = None#await get_proxy_config()
    # if proxy_config:
    #     common_args['proxy'] = {
    #         'server': f"http://{proxy_config['server'].replace('http://', '')}",
    #         'username': proxy_config['username'],
    #         'password': proxy_config['password']
    #     }

    browser_noproxy = await playwright.chromium.launch(**common_args)
    context_noproxy = await browser_noproxy.new_context()
    app.state.browser_noproxy = browser_noproxy
    app.state.context_noproxy = context_noproxy

    # Proxyli variant (agar kerak bo‘lsa)
    new_args = {"headless": True, 'args': ['--no-sandbox', '--disable-setuid-sandbox']}
    if proxy_config:
        new_args["proxy"] = {
             'server': f"http://{proxy_config['server'].replace('http://', '')}",
             'username': proxy_config['username'],
             'password': proxy_config['password']
         }
    browser_proxy = await playwright.chromium.launch(**new_args)
    context_proxy = await browser_proxy.new_context()
    app.state.browser = browser_proxy
    app.state.context = context_proxy

    # browser_face = await playwright.chromium.launch(**common_args)
    # context_face = await browser_face.new_context()
    # app.state.browser_face = browser_face
    # app.state.context_face = context_face

    browser_extra = await playwright.chromium.launch(**common_args)
    extra_context = await browser_extra.new_context()
    app.state.extra_context = extra_context

    # Sahifa pool-lar
    app.state.page_pool = asyncio.Queue()
    app.state.page_pool2 = asyncio.Queue()
    app.state.page_pool3 = asyncio.Queue()

    # Dastlabki sahifalarni qo‘shish helper funksiyasi
    async def add_initial_page(context, url: str, pool: asyncio.Queue, name: str, face_login: bool = False):
        page = None
        try:
            page = await context.new_page()
            await page.goto(url, wait_until="load")
            await pool.put(page)
            print(f"✅ {name} sahifa qo‘shildi")
        except Exception as e:
            print(f"⚠️ {name} sahifani ochishda xato: {e}")
            try:
                await page.close()
            except:
                pass
        finally:
            pass
            # if face_login:
            #     try:
            #         await page.goto("https://facebook.com")
                    
            #         # Email input mavjudligini tekshir
            #         email_input = await page.query_selector('input[name="email"]')
            #         password_input = await page.query_selector('input[name="pass"]')

            #         if email_input and password_input:
            #             await email_input.fill(EMAIL_FACEBOOK)
            #             await password_input.fill(EMAIL_PASSWORD)
            #             await page.click('button[name="login"]')

            #             # Login muvaffaqiyatli bo'lishini tekshirish
            #             await page.wait_for_timeout(3000)
            #             if "login" in page.url:
            #                 print("❌ Login failed, check credentials.")
            #             print("✅ Facebook login successful.")
            #         else:
            #             print("❌ Login form not found.")

            #     except Exception as e:
            #         print("❌ Login error:", e)


    # Sahifalarni yaratish
    # Sahifalarni yaratish
    await add_initial_page(context_noproxy, "https://sssinstagram.com/ru/story-saver", app.state.page_pool, "SSSInstagram")
    await add_initial_page(context_proxy, "https://snaptik.app", app.state.page_pool2, "Snaptik")
    # await add_initial_page(context_proxy, "https://tiktokio.com", app.state.page_pool2, "Snaptik")
    # await add_initial_page(context_face, "https://www.facebook.com", app.state.page_pool3, "Facebook", face_login=True)


    # Page pool tasklari
    app.state.add_page_task = asyncio.create_task(add_page_loop(context_noproxy, app.state.page_pool, app))  # 🛠 TO‘G‘RILANDI
    app.state.add_page_task_snaptik = asyncio.create_task(add_page_loop_snaptik(context_proxy, app.state.page_pool2, app))
    # app.state.add_page_task_face = asyncio.create_task(add_page_loop_facebook(context_face, app.state.page_pool3, app))



    # Brauzerlarni yangilovchi looplar
    # sssinstagram uchun context_noproxy
    asyncio.create_task(restart_browser_loop_generic(
        context_key="context_noproxy",
        browser_key="browser_noproxy",
        page_pool_key="page_pool",
        add_task_key="add_page_task",
        add_page_func=add_page_loop,
        urls=["https://sssinstagram.com/ru/story-saver"],
        interval=10 * 60
    ))

    # snaptik uchun context_proxy
    asyncio.create_task(restart_browser_loop_generic(
        context_key="context",
        browser_key="browser",
        page_pool_key="page_pool2",
        add_task_key="add_page_task_snaptik",
        add_page_func=add_page_loop_snaptik,
        # urls=["https://tiktokio.com"],
        urls=["https://snaptik.app"],
        interval=10 * 60
    ))

    # asyncio.create_task(restart_browser_loop_generic(
    #     context_key="context_face",
    #     browser_key="browser_face",
    #     page_pool_key="page_pool3",
    #     add_task_key="add_page_task_face",
    #     add_page_func=add_page_loop_facebook,
    #     urls=["https://facebook.com"],
    #     interval=20 * 30
    # ))




@app.on_event("shutdown")
async def shutdown():
    components = [
        getattr(app.state, name, None)
        for name in [
            'browser', 'context',
            'browser_noproxy', 'context_noproxy',
            'browser_face', 'context_face',
        ]
    ]
    for component in components:
        if component:
            try:
                await component.close()
            except Exception as e:
                print(f"⚠️ {component} ni yopishda xato: {e}")

    if getattr(app.state, "playwright", None):
        try:
            await app.state.playwright.stop()
        except Exception as e:
            print(f"⚠️ Playwright to‘xtatishda xato: {e}")

    print("🛑 Brauzerlar va kontekstlar yopildi")



@app.get('/status')
async def get_data(request: Request):
    PAGE_POOL = request.app.state.page_pool
    PAGE_POOL2 = request.app.state.page_pool2
    PAGE_POOL3 = request.app.state.page_pool3
    return {"status": "ok", "page_count": PAGE_POOL.qsize(), "page_count2": PAGE_POOL2.qsize(), "page_count3": PAGE_POOL3.qsize()}






async def add_page_loop(context, page_pool, app):
    while True:
        await asyncio.sleep(0.5)
        if page_pool.qsize() < MAX_PAGES:
            async with app.state.restart_lock:
                try:
                    page = await context.new_page()
                    await page.goto("https://sssinstagram.com/ru/story-saver", wait_until="load", timeout=10000)
                    await page_pool.put(page)
                    print("✅ sssinstagram sahifa qo'shildi")
                except Exception as e:
                    print(f"⚠️ sssinstagram Page yaratishda xato !: {e}")
                    try:
                        await page.close()
                    except:
                        pass


async def add_page_loop_snaptik(context, page_pool, app):
    while True:
        await asyncio.sleep(0.5)
        if page_pool.qsize() < MAX_PAGES:
            async with app.state.restart_lock:
                try:
                    page = await context.new_page()
                    # await page.goto("https://tiktokio.com", wait_until="load", timeout=10000)
                    await page.goto("https://snaptik.app", wait_until="load", timeout=10000)
                    await page_pool.put(page)
                    print("✅ snaptik sahifa qo'shildi")
                except Exception as e:
                    
                    print(f"⚠️ snaptik Page yaratishda xato !: {e}")
                    try:
                        await page.close()
                    except:
                        pass

# async def add_page_loop_facebook(context, page_pool, app):
#     while True:
#         await asyncio.sleep(0.5)
#         if page_pool.qsize() < MAX_PAGES:
#             async with app.state.restart_lock:
#                 try:
#                     page = await context.new_page()
#                     await page.goto("https://facebook.com", wait_until="load", timeout=10000)
#                     await page_pool.put(page)
#                     print("✅ facebook sahifa qo'shildi")
#                 except Exception as e:

#                     print(f"⚠️ facebook Page yaratishda xato !: {e}")
#                     try:
#                         await page.close()
#                     except:
#                         pass

from playwright.async_api import async_playwright
import asyncio

async def restart_browser_loop_generic(
    context_key: str,
    browser_key: str,
    page_pool_key: str,
    add_task_key: str,
    add_page_func: callable,
    urls: list[str],
    interval: int
):
    while True:
        await asyncio.sleep(interval)
        print(f"♻️ {context_key} uchun browser va context restart qilinmoqda...")
        async with app.state.restart_lock:
            try:
                # 1. Eski taskni bekor qilish
                old_task = getattr(app.state, add_task_key, None)
                if old_task:
                    old_task.cancel()
                    try:
                        await old_task
                    except asyncio.CancelledError:
                        pass

                # 2. Sahifalarni tozalash
                old_page_pool = getattr(app.state, page_pool_key)
                while True:
                    try:
                        page = await old_page_pool.get_nowait()
                        if not page.is_closed():
                            await page.close()
                    except (asyncio.QueueEmpty, Exception):
                        break

                # 3. Faqat browser va contextni yangilash
                old_browser = getattr(app.state, browser_key)
                old_context = getattr(app.state, context_key)
                await old_context.close()
                await old_browser.close()

                # 4. Yangi brauzer ochish (playwrightni qayta ishga tushirmasdan)
                playwright = app.state.playwright
                new_browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                new_context = await new_browser.new_context()
                setattr(app.state, browser_key, new_browser)
                setattr(app.state, context_key, new_context)

                # 5. Yangi sahifalarni qo‘shish
                new_page_pool = asyncio.Queue()
                setattr(app.state, page_pool_key, new_page_pool)
                for url in urls:
                    try:
                        page = await new_context.new_page()
                        await page.goto(url, wait_until="domcontentloaded")  # Tezroq yuklash
                        await new_page_pool.put(page)
                        print(f"✅ {url} sahifasi qayta ochildi")
                    except Exception as e:
                        print(f"⚠️ {url} ochilmadi: {e}")

                    finally:
                        pass
                        # try:
                        #     await page.goto("https://facebook.com")
                            
                        #     # Email input mavjudligini tekshir
                        #     email_input = await page.query_selector('input[name="email"]')
                        #     password_input = await page.query_selector('input[name="pass"]')

                        #     if email_input and password_input:
                        #         await email_input.fill(EMAIL_FACEBOOK)
                        #         await password_input.fill(EMAIL_PASSWORD)
                        #         await page.click('button[name="login"]')

                        #         # Login muvaffaqiyatli bo'lishini tekshirish
                        #         await page.wait_for_timeout(3000)
                        #         if "login" in page.url:
                        #             print("❌ Login failed, check credentials.")
                        #         print("✅ Facebook login successful.")
                        #     else:
                        #         print("❌ Login form not found.")
                        # except Exception as e:
                        #     print("❌ Login error:", e)
                # 6. Yangi taskni ishga tushirish
                setattr(app.state, add_task_key, asyncio.create_task(
                    add_page_func(new_context, new_page_pool, app)
                ))

                print(f"✅ {context_key} muvaffaqiyatli restart qilindi!")
            except Exception as e:
                print(f"❌ {context_key} restartda xato: {e}")
                await asyncio.sleep(2)  