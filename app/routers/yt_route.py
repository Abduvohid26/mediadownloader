from fastapi import APIRouter, Form, HTTPException
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
async def yt_media(yt_url: str):
    try:
        data = await get_yt_data(url=yt_url.strip())
        if not data:
            return {"status": "error", "message": "Invalid response from the server."}
        if data.get("error") == False:
            medias = data.get("medias", [])
            for media in medias:
                generated_uuid = str(uuid.uuid4())
                redis_client.set(generated_uuid, media["url"], 3600)
                if media["url"].startswith("https://manifest"):
                    media["url"] = f"https://videoyukla.uz/medias/youtube/m3u8?id={generated_uuid}"
                    # media["url"] = f"http://localhost:8000/medias/youtube/m3u8?id={generated_uuid}"

                else:
                    media["url"] = f"https://videoyukla.uz/medias/youtube?id={generated_uuid}"
                    # media["url"] = f"http://localhost:8000/medias/youtube?id={generated_uuid}"

        return data
    except Exception as e:
        print(f"Xatolik Yuz Berdi: {e}")
        return {"status": "error", "message": "Invalid response from the server."}


@yt_router.post("/youtube/media/service/", include_in_schema=False)
async def yt_media_service(yt_url: YtSchema = Form(...)):
    try:
        data = await get_yt_data(url=yt_url.url.strip())
        if not data:
            return {"status": "error", "message": "Invalid response from the server."}
        return data
    except Exception as e:
        print(f"Xatolik Yuz Berdi: {e}")
        return {"status": "error", "message": "Invalid response from the server."}




@yt_router.get("/medias/youtube/m3u8/")
async def stream_youtube_video(id: str):
    original_url = redis_client.get(id)
    if not original_url:
        raise HTTPException(status_code=404, detail="Video not found or expired.")
    
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
    _dataurl = redis_client.get(id)
    url = _dataurl.decode("utf-8")
    if not url:
        raise HTTPException(status_code=404, detail="Link not found or expired")
    proxy_config = await get_proxy_config()
    if proxy_config:
        proxy = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"

    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL: missing domain")

    async with httpx.AsyncClient(follow_redirects=True, timeout=None, proxy=proxy) as head_client:
        try:
            head_resp = await head_client.head(url)
            head_resp.raise_for_status()
            content_type = head_resp.headers.get("Content-Type", "application/octet-stream")
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=404, detail="Cannot access file")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Internal server error")

    async def iterfile():
        async with httpx.AsyncClient(follow_redirects=True, timeout=None, proxy=proxy) as stream_client:
            async with stream_client.stream("GET", url) as response:
                if response.status_code != 200:
                    raise HTTPException(status_code=404, detail="Cannot stream file")
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        iterfile(),
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="media"',
        }
    )

# @yt_router.get("/youtube/test/")
# async def get_media(url: str):
#     try:
#         data = await get_youtube_video_info(url)
#         # print(data, "data")
#         if not data:
#             return {"status": "error", "message": "Invalid response from the server."}
#         return data

#     except Exception as e:
#         print(f"Xatolik Yuz Berdi: {e}")
#         return {"status": "error", "message": f"Invalid response from the server. {e}"}




# import requests
# from .proxy_route import get_proxy_config
# import time
# @yt_router.get("/checker/")
# async def check_proxy_fast():
#     proxy_config = await get_proxy_config()
#     if not proxy_config:
#         return {"status": "error", "message": "Proxy topilmadi"}
#
#     proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
#     proxies = {
#         "http": proxy_url,
#         "https": proxy_url,
#     }
#
#     test_url = "https://www.google.com"
#
#     try:
#         start = time.time()
#         response = requests.get(test_url, proxies=proxies, timeout=10)
#         end = time.time()
#
#         return {
#             "status": "ok",
#             "response_code": response.status_code,
#             "duration": round(end - start, 2),
#             "proxy": proxy_url
#         }
#     except requests.exceptions.RequestException as e:
#         return {
#             "status": "error",
#             "message": str(e),
#             "proxy": proxy_url
#         }
#
# @yt_router.get("/checker/not/")
# async def check_proxy_fast():
#     test_url = "https://www.google.com"
#     try:
#             start = time.time()
#             response = requests.get(test_url, timeout=10)
#             end = time.time()
#
#             return {
#                 "status": "ok",
#                 "response_code": response.status_code,
#                 "duration": round(end - start, 2),
#             }
#     except requests.exceptions.RequestException as e:
#             return {
#                 "status": "error",
#                 "message": str(e),
#
#             }
