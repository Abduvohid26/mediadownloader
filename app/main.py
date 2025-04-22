import asyncio


from fastapi import FastAPI, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from playwright.async_api import async_playwright

from models.user import User, ProxyServers
from database.database import SessionLocal

from schema.user import UserCreate, User

from routers.insta_route import insta_router
from routers.proxy_route import proxies
from routers.yt_route import yt_router
from routers.sender import sender
# from routers.insta import browser_keepalive, close_browser
from routers.check import check_url
from routers.tiktok_route import tk_router
# from routers.new_inta import checker_router

app = FastAPI()
# app.include_router(checker_router)
app.include_router(insta_router)
app.include_router(proxies)
app.include_router(yt_router)
app.include_router(sender)
app.include_router(check_url)
app.include_router(tk_router)
# DB sessiyasini olish
# DB sessiyasini olish (Asinxron)
async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

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
    options = {
        'headless': True,
        'args': ['--no-sandbox', '--disable-setuid-sandbox']

    }
    # if proxy_config:
    #     options['proxy'] = {
    #         'server': f"http://{proxy_config['server'].replace('http://', '')}",
    #         'username': proxy_config['username'],
    #         'password': proxy_config['password']
    #     }
    browser = await playwright.chromium.launch(**options)
    app.state.browser = browser
    context = await browser.new_context()
    app.state.context = context
    print("Ishga tushdi", browser, context)


@app.on_event("shutdown")
async def shutdown():
    await app.state.browser.close()
    await app.state.context.close()
    print("Browser closes")