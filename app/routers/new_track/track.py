

import asyncio
import json

def _track_recognize_deserialize(track):
  return {
    "id": track["key"],
    "title": track["title"],
    "performer": track["subtitle"],
    "duration": 0,
    "thumbnail_url": track["images"].get("coverart", track["images"].get("coverarthq", None)) if "images" in track else None
  }

async def track_backend_songrec_recognize(file_path: str):
  songrec_proc = await asyncio.create_subprocess_shell(
    f"proxychains4 -f proxychains4.conf -q songrec recognize {file_path} --json",
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
    shell=True,
  )

  songrec_proc_stdout, songrec_proc_stderr = await songrec_proc.communicate()
  if songrec_proc_stderr:
    return None

  recognize_result = json.loads(songrec_proc_stdout)["track"]
  return _track_recognize_deserialize(recognize_result)


# async def track_backend_songrec_recognize(file_path: str):
#     try:
#         # Komandani ishga tushurish
#         process = await asyncio.create_subprocess_shell(
#             f"proxychains4 -f proxychains4.conf -q songrec recognize {file_path} --json",
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.PIPE,
#             shell=True,
#         )

#         stdout, stderr = await process.communicate()

#         # Agar stderr bo‘lsa
#         if stderr:
#             print("❌ Songrec stderr:", stderr.decode().strip())
#             return None

#         # Agar stdout bo‘sh bo‘lsa
#         if not stdout:
#             print("⚠️ Songrec hech qanday natija qaytarmadi")
#             return None

#         # JSON parse qilish
#         try:
#             result_json = json.loads(stdout)
#         except json.JSONDecodeError as e:
#             print("❌ JSON decode xatoligi:", str(e))
#             print("⛔ Raw output:", stdout.decode())
#             return None

#         # 'track' mavjudligini tekshirish
#         if "track" not in result_json:
#             print("⚠️ 'track' kaliti topilmadi")
#             return None

#         # Natijani deserialize qilish
#         return _track_recognize_deserialize(result_json["track"])

#     except Exception as e:
#         print("❗ Noma'lum xatolik:", str(e))
#         return None