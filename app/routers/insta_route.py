from .insta import download_instagram_media, get_instagram_story_urls
from schema.schema import InstaSchema, InstaStory
from fastapi import APIRouter, HTTPException, Form
# from .tiktok import get_video_album


insta_router = APIRouter()

@insta_router.post("/instagram/media")
async def get_instagram_media(insta_data: InstaSchema = Form(...)):
    url = insta_data.url.strip()

    # if not url.startswith("https://www.instagram.com/"):
    #     return {"status": "error", "message": "Iltimos, URL'ni tekshiring va qayta urinib ko'ring."}
    if "stories" in url:
        data =  await get_instagram_story_urls(url)
        return data
    media_urls = await download_instagram_media(url)

    if not media_urls:
        return {"status": "error", "message": "Iltimos, URL'ni tekshiring va qayta urinib ko'ring."}

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