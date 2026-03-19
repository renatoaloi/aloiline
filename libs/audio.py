import subprocess
import edge_tts

from pydub import AudioSegment
from libs import util as utilLib, filesys

def extract_audio(video_file, audio_file):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_file,
        "-vn",
        "-acodec", "mp3",
        audio_file
    ]
    subprocess.run(cmd)

async def build_audio(subtitles, output, voice_f, adjusted_f):
    final_audio = AudioSegment.silent(duration=0)
    for i, sub in enumerate(subtitles):

        voice_file = f"{voice_f}{i}.mp3"
        adjusted_file = f"{adjusted_f}{i}.mp3"
        
        timestamps = sub["timestamps"]
        text_pt = sub["text_pt"]

        target_duration = 0
        if i + 1 < len(subtitles):
            next_timestamp = subtitles[i + 1]["timestamps"]
            target_duration = utilLib.srt_time_to_ms(next_timestamp["from"]) - utilLib.srt_time_to_ms(timestamps["from"])
        else:
            target_duration = utilLib.srt_time_to_ms(timestamps["to"]) - utilLib.srt_time_to_ms(timestamps["from"])

        if target_duration <= 0:
            target_duration = 1 # Define 1ms como mínimo para evitar erro matemático

        # salvar cada pedaço de áudio em um arquivo temporário
        voice = await save_chunk(text_pt, voice_file)

        # determinando velocidade de ajuste necessária para o pedaço de áudio se encaixar na duração da legenda
        speed = len(voice) / target_duration

        print(f"text: {text_pt}")
        print(f"speed: {speed} | len(voice): {len(voice)} | target_duration: {target_duration}\n")

        voice_adjusted = adjust_chunk(speed, voice_file, adjusted_file)

        if filesys.file_exists(adjusted_file):
            final_audio += voice_adjusted
        else:
            final_audio += voice

        remove_chunks(voice_file, adjusted_file)

    final_audio.export(output, format="wav")

async def save_chunk(chunk, voice_file):
    await generate_tts(chunk, voice_file)
    return AudioSegment.from_mp3(voice_file)

def adjust_chunk(speed, input_file, adjusted_file):
    voice = AudioSegment.from_mp3(input_file)
    if speed > 1.0: 
        adjust_speed(input_file, adjusted_file, speed)
        voice = AudioSegment.from_mp3(adjusted_file)
    print(f"speed adjusted: {speed} | len(voice): {len(voice)}")
    return voice

async def generate_tts(text, filename):
    communicate = edge_tts.Communicate(text=text, voice="pt-BR-AntonioNeural")
    await communicate.save(filename)

def adjust_speed(input_file, output_file, speed):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-filter:a", f"atempo={speed}",
        output_file
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def remove_chunks(voice_file, adjusted_file):
    if filesys.file_exists(voice_file):
        filesys.remove_file(voice_file)
    if filesys.file_exists(adjusted_file):
        filesys.remove_file(adjusted_file)