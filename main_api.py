from fastapi import FastAPI, HTTPException

from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import subprocess
import os

app = FastAPI()

origins = [
    "https://videodownload-frontend.onrender.com",  # replace with the origin of your frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Video(BaseModel):
    url: str
    filename: str


def get_unique_filename(filename):
    counter = 1
    base_filename, extension = os.path.splitext(filename)
    unique_filename = filename

    while os.path.isfile(unique_filename):
        unique_filename = f"{base_filename}({counter}){extension}"
        counter += 1

    return unique_filename

@app.post("/api/download")
async def download_video(video: Video):
    url = video.url
    filename = get_unique_filename(video.filename)

    url += '.json'
    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Video not found")

    json_response = json.loads(response.text)
    video_url = json_response[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]
    audio_url = video_url.rsplit('/', 1)[0] + '/DASH_audio.mp4'

    video_response = requests.get(video_url, stream=True)
    audio_response = requests.get(audio_url, stream=True)

    with open('video_temp.mp4', 'wb') as f:
        for chunk in video_response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
    if audio_response.status_code == 200:
        with open('audio_temp.mp4', 'wb') as f:
            for chunk in audio_response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        subprocess.run(['ffmpeg', '-i', 'video_temp.mp4', '-i', 'audio_temp.mp4', '-c', 'copy', filename])
    else:
        os.rename('video_temp.mp4', filename)

    return FileResponse(filename, media_type='application/octet-stream', filename=filename)