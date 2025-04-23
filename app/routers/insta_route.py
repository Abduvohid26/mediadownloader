from .insta import download_instagram_media, get_instagram_story_urls
from schema.schema import InstaSchema, InstaStory
from fastapi import APIRouter, HTTPException, Form, Depends, Request
# from .tiktok import get_video_album
from .proxy_route import get_db, get_proxy_config
from sqlalchemy.ext.asyncio import AsyncSession
insta_router = APIRouter()

@insta_router.get("/instagram/media")
async def get_instagram_media(in_url: str, request: Request, db : AsyncSession = Depends(get_db)):
    url = in_url.strip()
    context = request.app.state.context
    proxy_config = await get_proxy_config()
    if "stories" in url:
        data =  await get_instagram_story_urls(url, context)
        return data
    media_urls = await download_instagram_media(url, proxy_config, context)

    if not media_urls:  
        return {"error": True, "message": "Invalid response from the server."}

    return media_urls

@insta_router.post("/instagram/media/service/", include_in_schema=False)
async def get_media(request: Request, url: InstaSchema = Form(...)):
    url = url.url.strip()
    context = request.app.state.context
    proxy_config = await get_proxy_config()
    if "stories" in url:
        data = await get_instagram_story_urls(url, context)
        return data
    media_urls = await download_instagram_media(url, proxy_config, context)

    if not media_urls:
        return {"error": True, "message": "Invalid response from the server."}

    return media_urls

