from .insta import download_instagram_media, get_instagram_story_urls
from schema.schema import InstaSchema, InstaStory
from fastapi import APIRouter, HTTPException, Form, Depends
# from .tiktok import get_video_album
from .proxy_route import get_db 
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import ProxyServers
from sqlalchemy.future import select
insta_router = APIRouter()

@insta_router.post("/instagram/media")
async def get_instagram_media(insta_data: InstaSchema = Form(...), db : AsyncSession = Depends(get_db)):
    url = insta_data.url.strip()
    result = await db.execute(select(ProxyServers).filter(ProxyServers.instagram == True))
    _proxy = result.scalars().first()
    proxy_config = {    
        "server": f"http://{_proxy.proxy}",
        "username": _proxy.username,
        "password": _proxy.password
    }
    # if not url.startswith("https://www.instagram.com/"):
    #     return {"status": "error", "message": "Iltimos, URL'ni tekshiring va qayta urinib ko'ring."}
    if "stories" in url:
        data =  await get_instagram_story_urls(url, proxy_config)
        return data
    media_urls = await download_instagram_media(url, proxy_config)

    if not media_urls:  
        return {"status": "error", "message": "Invalid response from the server."}

    return media_urls


# @insta_router.post("/instgram/stories")
# async def get_stories(username: InstaStory = Form(...)):
#     uname = username.username
#     story_data = await get_instagram_story_urls(f"https://www.instagram.com/stories/{uname}/")
#     if not story_data: 
#         return {"success": False, "message": f"{uname} stories not found"}
    
#     data = {}
#     c = 0
#     for story in story_data:
#         c += 1
#         data[f'istory{c}'] = {
#             "story_url": story["story_url"],
#             "thumbnail_url": story["thumbnail_url"]
#         }
#     return data