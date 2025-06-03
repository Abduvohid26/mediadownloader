import os
import asyncio
from ..proxy_route import get_proxy_config
import logging
from .model import ShazamWrapper

MAX_FILE_SIZE = 10 * 1024 * 1024


logger = logging.getLogger(__name__)


def _track_recognize_deserialize(track):
  return {
    "id": track["key"],
    "title": track["title"],
    "performer": track["subtitle"],
    "duration": 0,
    "thumbnail_url": track["images"].get("coverart", track["images"].get("coverarthq", None)) if "images" in track else None
  }


async def track_backend_songrec_recognize(file_path: str, max_retries: int = 3):
    if not os.path.exists(file_path):
        print(f"[XATO] Fayl topilmadi: {file_path}")
        return None

    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        print(f"[XATO] Fayl juda katta (>10MB): {file_path}")
        return None

    retry_count = 0
    while retry_count < max_retries:
        proxy = None
        proxy_config = await get_proxy_config()
        if proxy_config:
            proxy = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
        shazam_wrapper = ShazamWrapper()
        await shazam_wrapper.setup(proxy=proxy)
        try:
            result = await shazam_wrapper.recognize(file_path)
            if not result or "track" not in result:
                print("[XATO] Trek topilmadi.")
                return None
            return _track_recognize_deserialize(result["track"])
        except Exception as e:
            print(f"[XATO] {type(e).__name__}: {e}")
            retry_count += 1
            await asyncio.sleep(0.1)
        finally:
            await shazam_wrapper.close()

    print("[XATO] Maksimal urinishlar soni oshib ketdi.")
    return None

