from fastapi import APIRouter
from .face import get_facebook_video





face = APIRouter()


@face.get("/facebook/media/")
async def face_media(url: str):
    try:
        data = await  get_facebook_video(post_url=url.strip(), proxy=None)
        return data
    except Exception as e:
        print(e)
        return {"status": "error", "message": "Invalid response from the server."}




