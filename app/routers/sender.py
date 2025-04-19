from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
import logging

from sqlalchemy.util import await_only


import yt_dlp
import os
import asyncio
import re
from typing import Literal
import cachetools
from .proxy_route import get_proxy_config

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
ROOT_PATH = Path(__file__).parent.parent
sender = APIRouter()
CACHE = cachetools.TTLCache(maxsize=100, ttl=300)


def check_url(url: str) -> bool:
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)([\w\-]{11})"
    return bool(re.match(regex, url))


async def check_k(k: str) -> bool:
    k_list = ["144", "240", "360", "480", "720", "1080"]
    if k in k_list:
        return True
    return False


async def delete_file_after_delay(file_path: str):
    await asyncio.sleep(300)
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"delete file {file_path}")


# @sender.post("/youtube/media/")
async def get_and_save_yt(
    request: Request,
    url: str = Form(...),
    k: Literal["144", "240", "360", "480", "720", "1080"] = Form(...)
):
    if check_url(str(url)) and await check_k(str(k)):
        result = await download_yt(request, str(url), str(k))
        return result
    else:
        raise HTTPException(status_code=404, detail="Invalid Youtube URL or Invalid Quality")


# async def download_yt(request: Request, url: str, k):
#     proxy_config = await get_proxy_config()
#     yt_opts = {
#         'format': f'bestvideo[height<={k}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
#         'outtmpl': f'{ROOT_PATH}/static/output/video/%(id)s.%(ext)s',
#         'merge_output_format': 'mp4',
#         'noplaylist': True,
#         'overwrites': True,
#         'quiet': True,
#     }
#     print(proxy_config, 'proxy config')
#     if proxy_config:
#         proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
#         yt_opts['proxy'] = proxy_url
#
#     try:
#         loop = asyncio.get_running_loop()
#         with yt_dlp.YoutubeDL(yt_opts) as ydl:
#             result = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
#             print(result, 'result')
#         file_path = f"{ROOT_PATH}/static/output/video/{result['id']}.mp4"
#         exists = await asyncio.to_thread(os.path.exists, file_path)
#
#         if exists:
#             base_url = f"{request.base_url}"
#
#             CACHE[result["id"]] = file_path
#
#             asyncio.create_task(delete_file_after_delay(file_path))
#             video_info = {
#                 "title": result.get('title', None),
#                 "thumb": result.get('thumbnail', None),
#                 "download_url": f"{base_url.rstrip('/')}{file_path.replace('/media_service', '')}",
#                 "type": "video",
#                 "ext": "mp4",
#                 "quality": k,
#                 "info": "This is url 5 minute active"
#             }
#             return video_info
#     except Exception as e:
#         logger.error(f"Xatolik yuz berdi: {e}")
#         return {"status": "error", "message": "Invalid response from the server."}

async def download_yt(request: Request, url: str, k):
    proxy_config = await get_proxy_config()

    video_opts = {
        'format': f'bestvideo[height<={k}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        # 'format': 'bestvideo/best',
        'outtmpl': f'{ROOT_PATH}/static/output/video/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'overwrites': True,
        'quiet': False,
    }

    audio_opts = {
        'format': 'bestaudio[ext=m4a]/best',
        'outtmpl': f'{ROOT_PATH}/static/output/audio/%(id)s.%(ext)s',
        'noplaylist': True,
        'overwrites': True,
        'quiet': False,
    }

    if proxy_config:
        proxy_url = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
        video_opts['proxy'] = proxy_url
        audio_opts['proxy'] = proxy_url
    print(video_opts, '\n', audio_opts)
    try:
        loop = asyncio.get_running_loop()

        with yt_dlp.YoutubeDL(video_opts) as ydl:
            video_result = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            print(video_result, 'video_result')
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            audio_result = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))

        video_path = f"{ROOT_PATH}/static/output/video/{video_result['id']}.mp4"
        audio_path = f"{ROOT_PATH}/static/output/audio/{audio_result['id']}.m4a"

        video_exists = await asyncio.to_thread(os.path.exists, video_path)
        audio_exists = await asyncio.to_thread(os.path.exists, audio_path)

        if video_exists and audio_exists:
            base_url = f"{request.base_url}"
            CACHE[video_result["id"]] = video_path
            CACHE[audio_result["id"]] = audio_path

            asyncio.create_task(delete_file_after_delay(video_path))
            asyncio.create_task(delete_file_after_delay(audio_path))

            return {
                "title": video_result.get('title', None),
                "thumb": video_result.get('thumbnail', None),
                "video_download_url": f"{base_url.rstrip('/')}{video_path.replace('/media_service', '')}",
                "audio_download_url": f"{base_url.rstrip('/')}{audio_path.replace('/media_service', '')}",
                "video_ext": "mp4",
                "audio_ext": "m4a",
                "quality": k,
                "info": "This URL is active for 5 minutes."
            }
    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        return {"status": "error", "message": "Invalid response from the server."}