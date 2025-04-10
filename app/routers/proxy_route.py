from .insta import download_instagram_media, get_instagram_story_urls
from schema.schema import InstaSchema, InstaStory
from fastapi import APIRouter, HTTPException, Form, UploadFile, Depends
from models.user import ProxyServers
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import SessionLocal
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError

proxies = APIRouter()
    

async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db




@proxies.post("/proxy/file/add/", include_in_schema=False)
async def get_file_and_create(file: UploadFile, db: AsyncSession = Depends(get_db)):
    content = await file.read()
    text_data = content.decode("utf-8")
    proxies_to_add = []
    
    existing_proxies = await db.execute(select(ProxyServers.proxy))
    existing_proxies = {row[0] for row in existing_proxies.fetchall()}  
    
    for data in text_data.split("\r"):
        curr = data.strip().split(":")
        if len(curr) < 4:
            continue  

        proxy = f"{curr[0]}:{curr[1]}"
        if proxy in existing_proxies:
            continue  

        proxies_to_add.append(
            ProxyServers(proxy=proxy, username=curr[2], password=curr[3])
        )

    if proxies_to_add:
        db.add_all(proxies_to_add)
        await db.commit()
    
    return {"status": "ok"}


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
            print("Salom", proxy_config)
            return proxy_config
        
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
