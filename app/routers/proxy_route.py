from .insta import download_instagram_media, get_instagram_story_urls
from schema.schema import InstaSchema, InstaStory
from fastapi import APIRouter, HTTPException, Form, UploadFile, Depends
from models.user import ProxyServers
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import SessionLocal
from sqlalchemy.future import select

proxies = APIRouter()


async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db




@proxies.post("/proxy/file/add/")
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