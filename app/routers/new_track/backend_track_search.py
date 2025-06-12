import yt_dlp
import typing

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

TRACK_DOWNLOAD_STATIC_OPTIONS = {
  "quiet": True,
  "noprogress": False,
  "nooverwrites": True,
  "no_warnings": True,
  "format": "bestaudio[ext=m4a]",
  "extract_flat": True,
  "no_playlist": True,
  "audio_format": "mp3",
  "embed_thumbnail": True,
  "add_metadata": True,
  "extract_audio": True
}

def _track_search_deserialize(track):
  return {
    "id": track["id"],
    "title": track["title"],
    "performer": track["channel"],
    "duration": track["duration"] if "duration" in track and track["duration"] else 0,
    "thumbnail_url": track["thumbnails"][0]["url"]
  }

async def track_backend_yt_dlp_search(query: str, offset: int, limit: int, proxy: typing.Union[str, None] = None):
  query = query + " music"
  track_search_options = dict(TRACK_SEARCH_STATIC_OPTIONS)

  track_search_options["proxy"] = proxy

  with yt_dlp.YoutubeDL(track_search_options) as ytdlp:
    search_results = ytdlp.extract_info(f"ytsearch{offset+limit}:{query}")["entries"]
    deserialized_search_results = [_track_search_deserialize(search_result) for search_result in search_results]
    return deserialized_search_results[offset:offset+limit]