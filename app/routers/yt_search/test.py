# import yt_dlp
# import asyncio
# from concurrent.futures import ThreadPoolExecutor

# AUDIO_OPTIONS = {
#     "quiet": True,
#     "noprogress": True,
#     "no_warnings": True,
#     "skip_download": True,
#     "format": "bestaudio[ext=m4a]",  # to'g'ridan-to'g'ri audio link
#     "no_playlist": True,
# }

# def _extract_audio_info(entry):
#     return {
#         "title": entry.get("title"),
#         "direct_url": entry.get("url"),
#     }

# def sync_extract_audio(url: str):
#     with yt_dlp.YoutubeDL(AUDIO_OPTIONS) as ydl:
#         info = ydl.extract_info(url, download=False)
#         return _extract_audio_info(info)

# async def extract_audio(url: str):
#     loop = asyncio.get_running_loop()
#     with ThreadPoolExecutor(max_workers=10) as pool:
#         return await loop.run_in_executor(pool, sync_extract_audio, url)

# async def fast_parallel_links(query: str, limit=10):
#     # Avval video ID larini olish
#     with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "skip_download": True}) as ydl:
#         results = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
#         urls = [f"https://www.youtube.com/watch?v={entry['id']}" for entry in results["entries"][:limit]]

#     # Parallel ishlov berish
#     tasks = [extract_audio(url) for url in urls]
#     return await asyncio.gather(*tasks)

# # Ishga tushirish
# import time
# async def main():
#     start = time.time()
#     results = await fast_parallel_links("shoxrux rep", limit=10)
#     for r in results:
#         print(f"{r['title']} — {r['direct_url']}")
#     print("✅ Bajardi in", round(time.time() - start, 2), "seconds")

# asyncio.run(main())



import yt_dlp
import typing
# from cashe import redis_client
import redis
import os
import asyncio
import json
from routers.proxy_route import get_proxy_config, proxy_off



redis_host = os.environ.get("REDIS_HOST", "redis")
redis_port = os.environ.get("REDIS_PORT", 6379)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)


TRACK_SEARCH_STATIC_OPTIONS = {
  "quiet": True,
  "noprogress": True,
  "no_warnings": True,
  "skip_download": True,
  "extract_flat": True,
  "no_playlist": True,
  "match_filter": yt_dlp.utils.match_filter_func(
    "duration > 50 & duration < 600 & original_url!*=/shorts/ "
    "& url!*=/shorts/ & !is_live & live_status!=is_upcoming & availability=public"
  ),
}


def _track_search_deserialize(track):
  return {
    "id": track["id"],
    "title": track["title"],
    "performer": track["channel"],
    "duration": track["duration"] if "duration" in track and track["duration"] else 0,
    "thumbnail_url": track["thumbnails"][0]["url"],
    "url": f"https://videoyukla.uz/youtube?id={track['id']}"
    # "url": f"http://localhost:8000/youtube?id={track['id']}"

  }

async def track_backend_yt_dlp_search(query: str, offset: int, limit: int, proxy: typing.Union[str, None] = None):
  query = query + " music"
  track_search_options = dict(TRACK_SEARCH_STATIC_OPTIONS)

  if proxy:
    track_search_options["proxy"] = proxy

  with yt_dlp.YoutubeDL(track_search_options) as ytdlp:
    search_results = ytdlp.extract_info(f"ytsearch{offset+limit}:{query}")["entries"]
    deserialized_search_results = [_track_search_deserialize(search_result) for search_result in search_results]
    for track in deserialized_search_results:
        redis_client.set(track["id"], track["url"], 3600)
    return deserialized_search_results[offset:offset+limit]
  

  
# async def update_direct_links(track):
#     options = {
#         "quiet": True,
#         "noprogress": True,
#         "no_warnings": True,
#         "skip_download": True,
#         "format": "bestaudio[ext=m4a]",
#     }
#     with yt_dlp.YoutubeDL(options) as ydl:
#         info = ydl.extract_info(f"https://www.youtube.com/watch?v={track['id']}", download=False)
#         direct_url = info["url"]
#         redis_client.set(track["id"], direct_url)
#     print("set qilindi")

async def update_direct_links(video_id: str):
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    for attempt in range(3):
        try:
            proxy_config = await get_proxy_config()
            proxy = None
            if proxy_config:
                proxy = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"

            cmd = [
                "yt-dlp",
                "--simulate",
                "--skip-download",
                "-j",
                "-f", "bestaudio[ext=m4a]",
                "--match-filter", "duration>50 & duration<600",
            ]
            if proxy:
                cmd += ["--proxy", proxy]
            cmd.append(video_url)

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0 and stdout:
                data = json.loads(stdout.decode())
                url = data.get("url")
                if url:
                    redis_client.set(video_id, url, 3600)
                    print("✅ Set qilindi:", url)
                    return
            else:
                error_msg = stderr.decode()
                print(f"❌ Error [{attempt+1}/3] [{video_id}]: {error_msg.strip()}")

                if proxy_config and any(msg in error_msg for msg in [
                    "Sign in to confirm you're not a bot",
                    "blocked it in your country",
                    "This video is unavailable",
                    "ProxyError",
                    "403", "HTTP Error"
                ]):
                    await proxy_off(proxy_ip=proxy_config["server"], action="youtube")

        except Exception as e:
            print(f"❌ Exception attempt [{attempt+1}] in update_direct_links: {e}")

    print(f"❌ Failed to get direct link for video [{video_id}] after 3 attempts.")
    return {"success": False, "message": "Error response from the server", "retries": 3}



# import time
# import asyncio
# async def main():
#     start = time.time()
#     results = await track_backend_yt_dlp_search("shoxrux rep", 0, 10)
#     print("✅ Bajardi in", round(time.time() - start, 2), "seconds")
#     tasks = [update_direct_links(track) for track in results]
#     await asyncio.gather(*tasks)  # Run in parallel
#     print(results)
#     return results

# asyncio.run(main())