from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User, ProxyServers
from schema.user import UserCreate, User
from database.database import SessionLocal
from routers.insta_route import insta_router
from routers.proxy_route import proxies
from routers.yt_route import yt_router
from routers.sender import sender
from routers.insta import browser_keepalive, close_browser, browser_keepalive_images
from sqlalchemy.sql import func
import asyncio
app = FastAPI()
app.include_router(insta_router)
app.include_router(proxies)
app.include_router(yt_router)
app.include_router(sender)
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
        result = await db.execute(
            select(ProxyServers)
            .filter(ProxyServers.instagram == True)
            .order_by(func.random())  
            .limit(1)  
        )
        _proxy = result.scalars().first()
        proxy_config = {    
            "server": f"http://{_proxy.proxy}",
            "username": _proxy.username,
            "password": _proxy.password
        }
        return proxy_config

@app.on_event("startup")
async def startup():
    proxy_config = await get_proxy_config()
    asyncio.create_task(browser_keepalive_images(proxy_config))
    asyncio.create_task(browser_keepalive(proxy_config))
    

@app.on_event("shutdown")
async def shutdown():
    await close_browser()


