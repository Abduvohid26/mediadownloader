from fastapi import APIRouter, Form, HTTPException
from schema.schema import YtSchema
from .youtube import get_yt_data
yt_router = APIRouter()

# @yt_router.post("/yt/media")
async def yt_media(yt_url: YtSchema = Form(...)):
    try:
        data = await get_yt_data(video_url=yt_url.url.strip())
        if not data:
            return {"status": "error", "message": "Invalid response from the server."}
        return data
    except Exception as e:
        print(f"Xatolik Yuz Berdi: {e}")
        return {"status": "error", "message": "Invalid response from the server."}





