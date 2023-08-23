import requests
import json
import subprocess
import os

def download_video(url, filename):
    # Append .json to the URL
    url += '.json'

    # Send a GET request to the URL
    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})

    # The response is a JSON object, parse it with json.loads()
    json_response = json.loads(response.text)

    # The actual video URL is within the JSON object
    video_url = json_response[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]

    # The audio is typically located at the same URL as the video, but with DASHAudio.mp4 at the end
    audio_url = video_url.rsplit('/', 1)[0] + '/DASH_audio.mp4'

    # Download the video and audio by sending another GET request
    video_response = requests.get(video_url, stream=True)
    audio_response = requests.get(audio_url, stream=True)

    # Save the video and audio to files
    with open('video_temp.mp4', 'wb') as f:
        for chunk in video_response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
    if audio_response.status_code == 200:  # check if audio file exists
        with open('audio_temp.mp4', 'wb') as f:
            for chunk in audio_response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        # Use ffmpeg to merge the video and audio files
        subprocess.run(['ffmpeg', '-i', 'video_temp.mp4', '-i', 'audio_temp.mp4', '-c', 'copy', filename])
    else:
        os.rename('video_temp.mp4', filename)  # if no audio, rename video file to final filename

    print(f"Video downloaded successfully as {filename}")

# Example usage:
download_video(
    'https://www.reddit.com/r/StrangeEarth/comments/15au3mw/heres_a_video_i_compiled_of_different_presidents/',
    'video.mp4')