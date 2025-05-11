from fastapi import  UploadFile
from shazamio import Shazam
import aiofiles 
import os
import uuid
from moviepy import   AudioFileClip
import asyncio
import json
import redis

redis_host = os.environ.get("REDIS_HOST", "redis")
redis_port = os.environ.get("REDIS_PORT", 6379)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
shazam = Shazam()


def _track_popular_deserialize(track):
  return {
    "id": track["id"],
    "title": track["attributes"]["name"],
    "performer": track["attributes"].get("composerName", ""),
    "duration": 0
  }


# # query data serializer
async def get_shazam_text(query):
    results = await shazam.search_track(query=query, limit=1)
    track = results["tracks"]["hits"][0]
    response_data = {
        "id": track["key"],
        "title": track["heading"]["title"],
        "performer": track["heading"]["subtitle"],
        "duration": 0
    }
    track_info = await shazam.track_about(track["key"])
    print(track_info)
    if "sections" in track_info:
        for section in track_info["sections"]:
            if section["type"] == "LYRICS":
                lyrics = section["text"]
                print("\n".join(lyrics))
                response_data["text"] = lyrics
                break
    else:
        response_data["text"] = ""
    return response_data



# mp3 data serializer
async def get_shazam_mp3(mp3: UploadFile):
    file_ext = mp3.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await mp3.read()
        await out_file.write(content)
    try:
        result = await shazam.recognize(file_path)
        track = result.get("track")
        if not track:
            return {"detail": "Qoshiq aniqlanmadi"}

        data = {
            "id": track["key"],
            "title": track.get("title"),
            "performer": track.get("subtitle"),
            "duration": 0,
        }
        return data
    finally:
        os.remove(file_path)
        print("DELETED")

# mp4 data serializer

async def get_shazam_mp4(mp4: UploadFile):
    file_ext = mp4.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    video_path = os.path.join(UPLOAD_FOLDER, file_name)

    # 1. Save MP4 to disk first
    async with aiofiles.open(video_path, 'wb') as out_file:
        content = await mp4.read()
        await out_file.write(content)

    # 2. Convert MP4 to MP3
    audio_path = video_path.replace(f".{file_ext}", ".mp3")
    audio_clip = AudioFileClip(video_path)
    audio_clip.write_audiofile(audio_path)
    audio_clip.close()

    try:
        result = await shazam.recognize(audio_path)
        track = result.get("track")
        if not track:
            return {"detail": "Qoshiq aniqlanmadi"}
        return {
            "id": track["key"],
            "title": track.get("title"),
            "performer": track.get("subtitle"),
            "duration": 0,
        }
    finally:
        os.remove(video_path)
        os.remove(audio_path)
        print("DELETED MP4 and MP3")



async def get_direct_audio_link(data_query):
    query = f"{data_query['title']} {data_query['performer']} audio"
    cmd = [
        "yt-dlp",
        "--simulate",
        "--skip-download",
        "-j",
        "-f", "bestaudio[ext=m4a]",
        "--match-filter", "duration>50 & duration<600",
        f"ytsearch1:{query}"
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )
    stdout, _ = await proc.communicate()

    if stdout:
        try:
            data = json.loads(stdout.decode())
            url = data.get("url")
            title = data.get("title")
            print(f"✅ Topildi: {title}\n🔗 URL: {url}")
            redis_client.set(data_query["id"], url, 3600)
            print("set qilindi", data_query['id'])
            return url
        except json.JSONDecodeError:
            print("❌ JSON xatolik")
    else:
        print("❌ Hech narsa topilmadi")

    return None