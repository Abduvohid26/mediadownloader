import os
import secrets
import time
import aiofiles
import pathlib
import asyncio
from .shazam import track_backend_songrec_recognize
from .yt_audio import recognize_youtube_audio
from fastapi import UploadFile








async def track_recognize_by_multipart_reader(reader: UploadFile, is_youtube_audio: bool = False):
    safe_filename = os.path.basename(reader.filename)
    temp_file_path = os.path.join("/media-service-files", f"{secrets.token_hex(8)}_{safe_filename}")
    start_time = time.time()

    # Faylni saqlab olish
    async with aiofiles.open(temp_file_path, "wb") as temp_fd:
        while True:
            chunk = await reader.read(1024 * 1024)
            if not chunk:
                break
            await temp_fd.write(chunk)

    print(time.time() - start_time, "SPEND TIME")

    try:
        # Parallel ishga tushurish
        backend_task = asyncio.create_task(track_backend_songrec_recognize(temp_file_path))
        youtube_task = asyncio.create_task(recognize_youtube_audio(temp_file_path))

        tasks = [backend_task, youtube_task]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            try:
                result = task.result()
                if result:  
                    for p in pending:
                        p.cancel()
                    return result
            except Exception as e:
                print(f"Task error: {str(e)}")

        for task in pending:
            try:
                result = await task
                if result:
                    return result
            except Exception as e:
                print(f"Pending task error: {str(e)}")

        return {"error": "Track recognition failed from both sources."}

    finally:
        pathlib.Path(temp_file_path).unlink(missing_ok=True)