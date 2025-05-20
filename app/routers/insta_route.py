from .insta import download_instagram_media, get_instagram_direct_links
from schema.schema import InstaSchema, InstaStory
from fastapi import APIRouter, HTTPException, Form, Depends, Request
from fastapi.responses import StreamingResponse
# from .tiktok import get_video_album
from .proxy_route import get_db, get_proxy_config
from sqlalchemy.ext.asyncio import AsyncSession
from .cashe import generate_unique_id
from models.user import Download
import re
import httpx
from .cashe import redis_client
from urllib.parse import urlparse

insta_router = APIRouter()

@insta_router.get("/instagram/media")
async def get_instagram_media(in_url: str, request: Request, db : AsyncSession = Depends(get_db)):
    url = in_url.strip()
    proxy_config = await get_proxy_config()
    if "stories" in url:
        data = await get_instagram_direct_links(url, db, request)
        return data
    elif "@" in url:
        url = f"https://www.instagram.com/stories/{url[1:]}"
        data = await get_instagram_direct_links(url, db, request)
        return data
        
    media_urls = await download_instagram_media(url, proxy_config, db, request)

    if not media_urls:
        return {"error": True, "message": "Invalid response from the server."}

    return media_urls


 

@insta_router.post("/instagram/media/service/", include_in_schema=False)
async def get_media(request: Request, url: InstaSchema = Form(...), db : AsyncSession = Depends(get_db)):
    url = url.url.strip()
    proxy_config = await get_proxy_config()
    if "stories" in url:
        data = await get_instagram_direct_links(url, db, request)
        return data
    elif "@" in url:
        url = f"https://www.instagram.com/stories/{url[1:]}"
        data = await get_instagram_direct_links(url, db, request)
        return data
        
    media_urls = await download_instagram_media(url, proxy_config, db, request)

    if not media_urls:
        return {"error": True, "message": "Invalid response from the server."}

    return media_urls





@insta_router.get("/download/instagram/", include_in_schema=False)
async def download_file(id: str):
    # Redis'dan URL ni olish
    _dataurl = redis_client.get(id)
    url = _dataurl.decode("utf-8")
    print(url, "url")
    if not url:
        raise HTTPException(status_code=404, detail="Link not found or expired")

    # Protokol qo'shish agar kerak bo‘lsa
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    # URL validatsiyasi
    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL: missing domain")

    # HEAD so‘rov yuborish
    async with httpx.AsyncClient(follow_redirects=True, timeout=None) as head_client:
        try:
            head_resp = await head_client.head(url)
            head_resp.raise_for_status()
            content_type = head_resp.headers.get("Content-Type", "application/octet-stream")
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=404, detail="Cannot access file")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Internal server error")

    # Faylni stream qilish
    async def iterfile():
        async with httpx.AsyncClient(follow_redirects=True, timeout=None) as stream_client:
            async with stream_client.stream("GET", url) as response:
                if response.status_code != 200:
                    raise HTTPException(status_code=404, detail="Cannot stream file")
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        iterfile(),
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="media"',
        }
    )