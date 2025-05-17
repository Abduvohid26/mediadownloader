from fastapi import APIRouter, HTTPException
from .test import track_backend_yt_dlp_search, update_direct_links
import time
import asyncio
import json
from .test import redis_client
import httpx
from fastapi.responses import StreamingResponse
from fastapi import BackgroundTasks
from routers.proxy_route import get_proxy_config



test_route = APIRouter()

@test_route.get("/youtube/music/search/")
async def get_direct_links_route(query: str, limit: int = 10):
    start = time.time()
    results = await track_backend_yt_dlp_search(query, 0, limit)
    print("✅ Qidiruv bajardi in", round(time.time() - start, 2), "seconds")

    asyncio.create_task(gather_to_forcee(results))

    return results



async def gather_to_forcee(results, batch_size=10):
    half = len(results) // 2
    first_half = results[:half]
    second_half = results[half:]

    for i in range(0, len(first_half), batch_size):
        batch = first_half[i:i + batch_size]
        tasks = [update_direct_links(track["id"]) for track in batch if track.get("id")]
        await asyncio.gather(*tasks)

    for i in range(0, len(second_half), batch_size):
        batch = second_half[i:i + batch_size]
        tasks = [update_direct_links(track["id"]) for track in batch if track.get("id")]
        await asyncio.gather(*tasks)


@test_route.get("/youtube/", include_in_schema=False)
async def get_stream_(id: str):
    proxy = None
    value = redis_client.get(id)
    proxy_config = await get_proxy_config()
    if proxy_config:
        proxy = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"


    if not value:
        raise HTTPException(status_code=500, detail="Internal server error1")
    url = value.decode("utf-8")
    async with httpx.AsyncClient(follow_redirects=True, timeout=None, proxy=proxy) as head_client:
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
        async with httpx.AsyncClient(follow_redirects=True, timeout=None, proxy=proxy) as stream_client:
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
            "Content-Disposition": f'inline; filename="ziyotech.mp3"',
        }
    )