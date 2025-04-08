from fastapi import APIRouter, Form, HTTPException
from fastapi.encoders import jsonable_encoder
from schema.schema import YtSchema
from .youtube import get_yt_data
yt_router = APIRouter()

@yt_router.get("/youtube/media/")
async def yt_media(yt_url: str):
    try:
        data = await get_yt_data(url=yt_url.strip())
        if not data:
            return {"status": "error", "message": "Invalid response from the server."}
        return data
    except Exception as e:
        print(f"Xatolik Yuz Berdi: {e}")
        return {"status": "error", "message": "Invalid response from the server."}





