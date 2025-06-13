import asyncio
import os
import time
import tempfile
import secrets
import aiofiles
import aiohttp
from urllib.parse import urljoin
import uuid
from fastapi import UploadFile
from routers.new_track.backend_track_search import track_backend_yt_dlp_search
from .track import track_backend_songrec_recognize


# WAV ga o‘tkazuvchi funksiya
async def convert_to_wav(input_path: str, output_path: str):
    process = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y", "-i", input_path, "-ac", "1", "-ar", "16000", output_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion failed with code {process.returncode}")

    if not os.path.exists(output_path):
        raise FileNotFoundError("WAV file not created")


async def get_by_file_from_upload(file_path: str):
    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=os.path.basename(file_path), content_type='audio/wav')
                async with session.post(urljoin("http://46.166.162.17:8050", "/track-recognize-by-file"), data=data) as response:
                    json_response = await response.json()
                    return json_response["recognize_result"]
    except Exception as e:
        print(f"API error: {str(e)}")
        return None


async def track_recognize_by_multipart_reader(reader: UploadFile):
    # original_ext = reader.filename.split(".")[-1]
    # input_filename = f"temp_input_{uuid.uuid4()}.{original_ext}"
    # output_filename = f"temp_output_{uuid.uuid4()}.wav"

    # try:
    #     async with aiofiles.open(input_filename, 'wb') as out_file:
    #         content = await reader.read()
    #         await out_file.write(content)

    #     await convert_to_wav(input_filename, output_filename)


    #     # result = await get_by_file_from_upload(output_filename)
    #     # if result:
    #     #     return await track_backend_yt_dlp_search(f'{result.get("performer", None)} {result.get("title", None)}', 0, 10)
    #     return {"error": True, "message": "Error response from the server"}

    # finally:
    #     for file in [input_filename, output_filename]:
    #         if os.path.exists(file):
    #             os.remove(file)



    curr_time = time.time()

    temp_dir = tempfile.mkdtemp()

    try:
        safe_filename = os.path.basename(reader.filename or "audio_temp")
        temp_file_path = os.path.join(temp_dir, f"{secrets.token_hex(8)}_{safe_filename}")

        async with aiofiles.open(temp_file_path, "wb") as temp_fd:
            while chunk := await reader.read(1024 * 1024):  
                await temp_fd.write(chunk)

        print(f"[OK] File saved in {time.time() - curr_time:.2f} sec: {temp_file_path}")

        # WAV ga o‘girish
        wav_file_path = os.path.join(temp_dir, f"{secrets.token_hex(8)}.wav")
        await convert_to_wav(temp_file_path, wav_file_path)

        if os.path.getsize(wav_file_path) > 30 * 1024 * 1024:
            return {"error": "File size exceeds 30 MB limit"}

        print(f"[OK] WAV created: {wav_file_path}")
        return await track_backend_songrec_recognize(wav_file_path)

    finally:
        try:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
        except Exception as cleanup_error:
            print(f"[ERROR] Cleanup failed: {cleanup_error}")