import secrets
import subprocess
from pathlib import Path    
from pydub import AudioSegment
import speech_recognition as sr




async def recognize_youtube_audio(file_path: str):
    temp_dir = Path("/media-service-files")
    wav_path = temp_dir / (secrets.token_hex(8) + ".wav")
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", str(file_path),
            "-ac", "1", "-ar", "16000",  
            str(wav_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        recognizer = sr.Recognizer()

        with sr.AudioFile(str(wav_path)) as source:
            audio_data = recognizer.record(source, duration=5)
        text = recognizer.recognize_google(audio_data, language="uz")
        print(text)
        return {
        "id": None,
        "title": text,
        "performer": None,
        "duration": 0,
        "thumbnail_url": None
    }
    except Exception as e:
        print(str(e))
        return None

    finally:
        if wav_path.exists():
            wav_path.unlink(missing_ok=True)