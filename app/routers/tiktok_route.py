from fastapi import APIRouter, Form, HTTPException
from fastapi.encoders import jsonable_encoder
from schema.schema import TkSchema
from .tiktok import download_from_snaptik
tk_router = APIRouter()

@tk_router.get("/tiktok/media/")
async def tk_media(tk_url: str):
    try:
        data = await download_from_snaptik(tk_url.strip())
        print(data, "Data")
        if not data:
            return {"status": "error", "message": "Invalid response from the server."}
        return data
    except Exception as e:
        print(f"Xatolik Yuz Berdi: {e}")
        return {"status": "error", "message": "Invalid response from the server."}



@tk_router.post("/tiktok/media/service/", include_in_schema=False)
async def tk_media_service(url: TkSchema = Form(...)):
    try:
        data = await download_from_snaptik(url.url.strip())
        print(data, "Data")
        if not data:
            return {"status": "error", "message": "Invalid response from the server."}
        return data
    except Exception as e:
        print(f"Xatolik Yuz Berdi: {e}")
        return {"status": "error", "message": "Invalid response from the server."}
