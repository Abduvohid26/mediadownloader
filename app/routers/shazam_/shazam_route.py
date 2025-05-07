
from fastapi import UploadFile, File, Form, HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from fastapi import BackgroundTasks
from .shazam import get_shazam_mp4, get_shazam_text, get_shazam_mp3, get_direct_audio_link
import os
import redis
import httpx
redis_host = os.environ.get("REDIS_HOST", "redis")
redis_port = os.environ.get("REDIS_PORT", 6379)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
shazam_router = APIRouter()



@shazam_router.post("/shazam/search/")
async def get_shazam_data(
    background_tasks: BackgroundTasks,
    query: str = Form(None),
    mp3: UploadFile = File(None),
    mp4: UploadFile = File(None)
):
    if not any([mp3, mp4, query]):
        raise HTTPException(status_code=400, detail="At least one of mp3, mp4 or query must be provided")

    data = None
    try:
        if mp4:
            data = await get_shazam_mp4(mp4)
        elif mp3:
            data = await get_shazam_mp3(mp3)
        else:
            data = await get_shazam_text(query)
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return {"error": "Xatolik yuz berdi, qayta urinib ko'ring"}

    if not data or "id" not in data:
        return {"error": "Ma'lumotni aniqlab bo'lmadi"}

    # data["url"] = f"http://localhost:8080/shazam?id={data['id']}"
    data["url"] = f"https://fast.videoyukla.uz/shazam?id={data['id']}"

    background_tasks.add_task(get_direct_audio_link, data)
    return data


@shazam_router.get("/shazam/", include_in_schema=False)
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