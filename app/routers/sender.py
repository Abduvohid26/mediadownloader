from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
import logging

from sqlalchemy.util import await_only

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ROOT_PATH = Path(__file__).parent.parent
sender = APIRouter()

#
# @sender.post("/send_large_video/")
# async def send_large_video(user_id: int, video_url: str, type: str):
#     try:
#         app = Client("bot", bot_token="7784958688:AAFwikdjjS97CJXq9dcSLDq-IV7m1R6VO1o", api_id=25359112, api_hash="5589d52cb52c72686307211a46cb6bae")
#         await app.start()
#         if type == "video":
#             await app.send_video(chat_id=user_id, video=video_url)
#         elif type == "audio":
#             await app.send_audio(chat_id=user_id, audio=video_url)
#         else:
#             await app.send_message(chat_id=user_id, text="Invalid type")
#
#         return {"status": "success"}
#
#     except Exception as e:
#         return {"status": "error", "message": str(e)}
#     finally:
#         await app.stop()

import yt_dlp
import os
import asyncio
import re
from typing import Literal
import cachetools

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


@sender.post("/youtube/media/")
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


async def download_yt(request: Request, url: str, k):
    yt_opts = {
        'format': f'bestvideo[height<={k}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'{ROOT_PATH}/static/output/video/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'overwrites': True,
        'quiet': True,
    }
    try:
        loop = asyncio.get_running_loop()
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            result = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
        file_path = f"{ROOT_PATH}/static/output/video/{result['id']}.mp4"
        exists = await asyncio.to_thread(os.path.exists, file_path)

        if exists:
            base_url = f"{request.base_url}"

            CACHE[result["id"]] = file_path

            asyncio.create_task(delete_file_after_delay(file_path))

            video_info = {
                "title": result.get('title', None),
                "thumb": result.get('thumbnail', None),
                "download_url": f"{base_url.rstrip('/')}{file_path}",
                "type": "video",
                "ext": "mp4",
                "quality": k,
                "info": "This is url 5 minute active"
            }
            return video_info
    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        return {"status": "error", "message": "Invalid response from the server."}