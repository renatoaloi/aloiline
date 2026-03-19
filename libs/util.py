import os
import re

def create_folders():
    folders = ["downloads", "clips", "audio", "transcripts", "subtitles"]
    for f in folders:
        os.makedirs(f, exist_ok=True)

def extract_json_array(text):
    match = re.search(r"\[\s*\".*?\"\s*\]", text, re.DOTALL)
    if not match:
        raise ValueError("JSON não encontrado na resposta")
    return match.group(0)

def format_time(seconds):
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = int(seconds // 60) % 60
    h = int(seconds // 3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def srt_time_to_ms(time_str):
    h, m, s = time_str.split(":")
    s, ms = s.split(",")
    total = (
        int(h) * 3600
        + int(m) * 60
        + int(s)
        + int(ms) / 1000
    )
    return int(total * 1000)