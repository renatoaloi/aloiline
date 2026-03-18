import subprocess
import yt_dlp
import json

from util import get_timestamp

# -------------------------
# Videos
# -------------------------

def load_videos_from_json():
    with open("videos.json", "r", encoding="utf-8") as f:
        return json.load(f)

def download_video(url):
    ydl_opts = {
        'outtmpl': f'downloads/{get_timestamp()}_%(id)s.%(ext)s',
        'format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = f"downloads/{get_timestamp()}_{info['id']}.mp4"
        return video_path
    
def cut_clip(video_file, start, end, output):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_file,
        "-ss", start,
        "-to", end,
        "-c", "copy",
        output
    ]
    subprocess.run(cmd)



def adjust_speed(input_file, output_file, speed):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-filter:a", f"atempo={speed}",
        output_file
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

