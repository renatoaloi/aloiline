import subprocess
import edge_tts

from pydub import AudioSegment
from pydub.silence import detect_silence
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
        text_pt = sub["text"]

        target_duration = 0
        if i + 1 < len(subtitles):
            # da segunda legenda em diante pega a diferença do espaço entre elas
            next_timestamp = subtitles[i + 1]["timestamps"]
            next_timestamp_from = utilLib.srt_time_to_ms(next_timestamp["from"])
            actual_timestamp_from = utilLib.srt_time_to_ms(timestamps["from"])
            target_duration = next_timestamp_from - actual_timestamp_from
            print(f"##{i}## :: Next time [from]: {next_timestamp_from} | Actual time [from]: {actual_timestamp_from}")
        else:
            # se for o primeiro, pega o tamanho da legenda
            actual_timestamp_to = utilLib.srt_time_to_ms(timestamps["to"])
            actual_timestamp_from = utilLib.srt_time_to_ms(timestamps["from"])
            target_duration = actual_timestamp_to - actual_timestamp_from
            print(f"##{i}## :: Actual time [to]: {actual_timestamp_to} | Actual time [from]: {actual_timestamp_from}")

        # if target_duration == 0:
        #     target_duration = 1
        # elif target_duration < 0:
        #     target_duration *= -1

        # salvar cada pedaço de áudio em um arquivo temporário
        voice = await save_chunk(text_pt, voice_file)

        # determinando velocidade de ajuste necessária para o pedaço de áudio se encaixar na duração da legenda
        speed = len(voice) / target_duration

        # ajuste de silêncio
        silent = AudioSegment.silent(duration=target_duration - len(voice))

        print(f"text: {text_pt}")
        
        voice_adjusted = adjust_chunk(speed, voice_file, adjusted_file)
        
        if filesys.file_exists(adjusted_file):
            #silent = AudioSegment.silent(duration=target_duration - len(voice_adjusted))
            final_audio += voice_adjusted + silent
        else:
            final_audio += voice + silent

        print(f"silent: {len(silent)} | silent_duration: {target_duration - len(voice)} | speed: {speed} | len(voice): {len(voice)} | target_duration: {target_duration}\n")
        remove_chunks(voice_file, adjusted_file)

    final_audio.export(output, format="wav")

async def verify_audio(subtitles, chunk_f):
    ret = True
    for i, sub in enumerate(subtitles):
        
        timestamps = sub["timestamps"]
        text_pt = sub["text"]

        chunk_file = f"{chunk_f}{i}.mp3"

        target_duration = 0
        if i + 1 < len(subtitles):
            next_timestamp = subtitles[i + 1]["timestamps"]
            target_duration = utilLib.srt_time_to_ms(next_timestamp["from"]) - utilLib.srt_time_to_ms(timestamps["from"])
        else:
            target_duration = utilLib.srt_time_to_ms(timestamps["to"]) - utilLib.srt_time_to_ms(timestamps["from"])

        if target_duration <= 0:
            target_duration = 1 # Define 1ms como mínimo para evitar erro matemático
        
        chunk = await save_chunk(text_pt, chunk_file)
        speed = len(chunk) / target_duration
        if speed > 2.5:
            print(f"Segmento {i+1}: texto='{text_pt}' | duração alvo={target_duration}ms | duração voz={len(chunk)}ms | velocidade de ajuste necessária: {speed:.2f}x")
            ret = False
        remove_chunks(chunk_file, "")
    return ret

async def save_chunk(chunk, voice_file):
    await generate_tts(chunk, voice_file)
    return AudioSegment.from_mp3(voice_file)

def adjust_chunk(speed, input_file, adjusted_file):
    voice = AudioSegment.from_mp3(input_file)
    if speed > 1.0: 
        adjust_speed(input_file, adjusted_file, speed)
        voice = AudioSegment.from_mp3(adjusted_file)
        #print(f"speed adjusted: {speed} | len(voice): {len(voice)}\n")
    else:
        pass
        #print("Não precisou de ajuste de speed...\n")
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