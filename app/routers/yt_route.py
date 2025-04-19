from fastapi import APIRouter, Form, HTTPException
from fastapi.encoders import jsonable_encoder
from schema.schema import YtSchema
from .youtube import get_yt_data, get_youtube_video_info
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


# @yt_router.get("/youtube/test/")
async def get_media(url: str):
    try:
        data = await get_youtube_video_info(url)
        # print(data, "data")
        if not data:
            return {"status": "error", "message": "Invalid response from the server."}
        return data

    except Exception as e:
        print(f"Xatolik Yuz Berdi: {e}")
        return {"status": "error", "message": f"Invalid response from the server. {e}"}




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
