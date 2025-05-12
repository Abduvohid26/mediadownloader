from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from schema.schema import TkSchema
from .tiktok import download_from_snaptik
import time
import httpx
import os
import redis
from fastapi.responses import StreamingResponse
import asyncio


redis_host = os.environ.get("REDIS_HOST", "redis")
redis_port = os.environ.get("REDIS_PORT", 6379)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

tk_router = APIRouter()


@tk_router.get("/tiktok/media/")
async def tk_media(tk_url: str, request: Request):
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post("https://downloader.bot/api/tiktok/info", json={"url": tk_url})
            data = response.json()
            return await serializer_data(data, tk_url)
    except Exception as e:
        print("Xatolik Yuz Berdi: ", e)
        return {"status": "error", "message": "Invalid response from the server."}

    # start_time = time.time() 
    # try:
    #     data = await download_from_snaptik(tk_url.strip(), request)
    #     if not data:
    #         return {"status": "error", "message": "Invalid response from the server."}
    #     print(time.time() - start_time, "SPEND TIME")
    #     return data
    # except Exception as e:
    #     print(f"Xatolik Yuz Berdi: {e}")
    #     return {"status": "error", "message": "Invalid response from the server."}



@tk_router.post("/tiktok/media/service/", include_in_schema=False)
async def tk_media_service(request: Request, url: TkSchema = Form(...)):
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post("https://downloader.bot/api/tiktok/info", json={"url": url.url.strip()})
            data = response.json()
            await asyncio.sleep(3.5)
            return await serializer_data(data, url)
    except Exception as e:
        print("Xatolik Yuz Berdi: ", e)
        return {"status": "error", "message": "Invalid response from the server."}
    # try:
    #     data = await download_from_snaptik(url.url.strip(), request)
    #     if not data:
    #         return {"status": "error", "message": "Invalid response from the server."}
    #     return data
    # except Exception as e:  
    #     print(f"Xatolik Yuz Berdi: {e}")
    #     return {"status": "error", "message": "Invalid response from the server."}





import uuid


async def serializer_data(data, url):
    if not data or not isinstance(data, dict):
        return {"status": "error", "message": "Invalid response from the server."}

    inner_data = data.get("data")
    if not inner_data or not isinstance(inner_data, dict):
        return {"status": "error", "message": "Invalid response from the server."}

    video_info = inner_data.get("video_info")
    mp4_url = inner_data.get("mp4")
    video_img = inner_data.get("video_img")
    uuid4 = str(uuid.uuid4())


    if not video_info or not mp4_url or not video_img:
        return {"status": "error", "message": "Missing video data in the response."}
    new_url = f"https://fast.videoyukla.uz/tiktok?id={uuid4}"
    # new_url = f"http://localhost:8000/tiktok?id={uuid4}"
    redis_client.set(uuid4, mp4_url, 3600)


    return {
        "error": False,
        "shortcode": None,
        "hosting": "tiktok",
        "type": "video",
        "title": video_info,
        "url": url,
        "medias": [
            {
                "type": "video",
                "download_url": new_url,
                "thumb": video_img
            }
        ]
    }



@tk_router.get("/tiktok/", include_in_schema=False)
async def get_stream_(id: str):
    print(id, "id")
    value = redis_client.get(id)
    print(value, "value")
    if not value:
        raise HTTPException(status_code=500, detail="Internal server error1")
    url = value.decode("utf-8")
    async with httpx.AsyncClient(follow_redirects=True, timeout=None) as head_client:
        try:
            head_resp = await head_client.head(url)
            head_resp.raise_for_status()
            content_type = head_resp.headers.get("Content-Type", "application/octet-stream")
        except httpx.HTTPStatusError as e:
            print(f"Status: {e.response.status_code} - Cannot access file")
            raise HTTPException(status_code=404, detail="Cannot access file")
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def iterfile():
        async with httpx.AsyncClient(follow_redirects=True, timeout=None) as stream_client:
            async with stream_client.stream("GET", url) as response:
                if response.status_code != 200:
                    print("Status: Cannot stream file")
                    raise HTTPException(status_code=404, detail="Cannot stream file")

                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        iterfile(),
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="ziyotech"',
        }
    )