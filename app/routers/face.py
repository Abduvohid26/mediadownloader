


# import yt_dlp


# url = "https://www.facebook.com/share/r/1DvHysYTFu"


# ydl_opts = {
#     "quiet": True,
#     "no_warnings": True,
#     "format": "best[ext=mp4]",
#     "noplaylist": True,
#     "skip_download": True,
#     "n_connections": 4,
#     "socket_timeout": 30,
#     "retries": 2,
# }

# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     info = ydl.extract_info(url, download=False)
#     print(info)
import asyncio
import yt_dlp

async def get_video(query, post_url):
    return {
        "error": False,
        "shortcode": None,
        "hosting": "facebook",
        "type": "video",
        "url": post_url,
        "title": query.get("title"),
        "medias": [
            {
                "type": "video",
                "download_url": query.get("url"),
                "thumb": query.get("thumbnails")[0].get("url", None)
            }
        ]
    }

async def get_facebook_video(post_url, proxy):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best[ext=mp4]",
        "noplaylist": True,
        "skip_download": True,
        "n_connections": 4,
        "socket_timeout": 30,
        "retries": 2,
    }
    try:
        loop = asyncio.get_running_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(post_url, download=False))
        return await get_video(info, post_url)
    except Exception as e:
        print(f"Error: {e}")
        return {"error": True, "message": f"Invalid response from the server: {e}"}