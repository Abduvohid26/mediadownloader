from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from schema.schema import YtSchema
from .youtube import get_yt_data
from .cashe import redis_client
from urllib.parse import urlparse
from .proxy_route import get_proxy_config
import uuid
import httpx

yt_router = APIRouter()

@yt_router.get("/youtube/media/")
async def yt_media(yt_url: str, request: Request):
    try:
        data = await get_yt_data(url=yt_url.strip())
        if not data:
            return {"status": "error", "message": "Invalid response from the server."}

        if data.get("error") == False:
            medias = data.get("medias", [])
            base_url = str(request.base_url).rstrip("/")  # https://videoyukla.uz

            for media in medias:
                generated_uuid = str(uuid.uuid4())
                redis_client.set(generated_uuid, media["url"], 3600)

                if media["url"].startswith("https://manifest"):
                    media["url"] = f"{base_url}/medias/youtube/m3u8?id={generated_uuid}.m3u8"
                else:
                    media["url"] = f"{base_url}/medias/youtube?id={generated_uuid}.{media['ext']}"

        return data

    except Exception as e:
        print(f"Xatolik Yuz Berdi: {e}")
        return {"status": "error", "message": "Invalid response from the server."}



@yt_router.post("/youtube/media/service/", include_in_schema=False)
async def yt_media_service(
    request: Request,
    yt_url: YtSchema = Form(...)
):
    try:
        data = await get_yt_data(url=yt_url.url.strip())
        if not data:
            return {"status": "error", "message": "Invalid response from the server."}

        if data.get("error") == False:
            medias = data.get("medias", [])
            base_url = str(request.base_url).rstrip("/")  # https://videoyukla.uz

            for media in medias:
                generated_uuid = str(uuid.uuid4())
                redis_client.set(generated_uuid, media["url"], 3600)

                if media["url"].startswith("https://manifest"):
                    media["url"] = f"{base_url}/medias/youtube/m3u8?id={generated_uuid}.m3u8"
                else:
                    media["url"] = f"{base_url}/medias/youtube?id={generated_uuid}.{media['ext']}"

        return data

    except Exception as e:
        print(f"Xatolik Yuz Berdi: {e}")
        return {"status": "error", "message": "Invalid response from the server."}



@yt_router.get("/medias/youtube/m3u8/")
async def stream_youtube_video(id: str):
    uuid_part = id.rsplit(".", 1)[0]
    original_url = redis_client.get(uuid_part)
    if not original_url:
        raise HTTPException(status_code=404, detail="Video not found or expired.")
    proxy = None
    proxy_config = await get_proxy_config()
    if proxy_config:
        proxy = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"

    original_url = original_url.decode("utf-8")  
    async with httpx.AsyncClient(follow_redirects=True, timeout=None, proxy=proxy) as client:
        response = await client.get(original_url, timeout=None)
        return StreamingResponse(
            content=response.aiter_bytes(),
            media_type="application/vnd.apple.mpegurl"  
        )



@yt_router.get("/medias/youtube/", include_in_schema=False)
async def download_file(id: str):
    uuid_part = id.rsplit(".", 1)[0]
    _dataurl = redis_client.get(uuid_part)
    if not _dataurl:
        raise HTTPException(status_code=404, detail="Link not found or expired")

    url = _dataurl.decode("utf-8")

    proxy = None
    proxy_config = await get_proxy_config()
    if proxy_config:
        proxy = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"

    # Validate URL
    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL: missing domain")

    content_type = "application/octet-stream"

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=None, proxy=proxy) as client:
            head_resp = await client.head(url)
            if head_resp.status_code == 200:
                guessed_type = head_resp.headers.get("Content-Type", "")
                if guessed_type and not guessed_type.startswith("text/html"):
                    content_type = guessed_type
            else:
                get_resp = await client.get(url, stream=True)
                guessed_type = get_resp.headers.get("Content-Type", "")
                if guessed_type and not guessed_type.startswith("text/html"):
                    content_type = guessed_type
    except Exception:
        pass

    async def iterfile():
        async with httpx.AsyncClient(follow_redirects=True, timeout=None, proxy=proxy) as stream_client:
            async with stream_client.stream("GET", url) as response:
                if response.status_code != 200:
                    raise HTTPException(status_code=404, detail="Cannot stream file")
                if response.headers.get("Content-Type", "").startswith("text/html"):
                    raise HTTPException(status_code=415, detail="Received HTML instead of media")

                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        iterfile(),
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="media"',
        }
    )