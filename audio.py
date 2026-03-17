import os
import subprocess
import edge_tts
from legendas import subtitle_duration_ms
from pydub import AudioSegment
from pydub.silence import split_on_silence
from util import get_timestamp, srt_time_to_ms
from legendas import parse_srt
from video import adjust_speed
# -------------------------
# Voice
# -------------------------
def get_voice():
    return "pt-BR-AntonioNeural"

# -------------------------
# Audios
# -------------------------

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

async def generate_tts(text, filename):
    communicate = edge_tts.Communicate(
        text=text,
        voice=get_voice()
    )
    await communicate.save(filename)

async def verify_audio(subtitles):
    ret = True
    for i, sub in enumerate(subtitles):
        target_duration = subtitle_duration_ms(sub["start"], sub["end"])
        chunk, chunk_file = await save_chunk(sub["text"], i)
        speed = len(chunk) / target_duration
        if speed > 2.5:
            print(f"Segmento {i+1}: texto='{sub['text']}' | duração alvo={target_duration}ms | duração voz={len(chunk)}ms | velocidade de ajuste necessária: {speed:.2f}x")
            ret = False
        remove_chunks(chunk_file, "")
    return ret

def clear_silence(audio_file):
    audio = AudioSegment.from_mp3(audio_file)
    chunks = split_on_silence(
        audio,
        min_silence_len = 1000,
        silence_thresh = audio.dBFS - 20 #,
        #keep_silence = 250, # optional
    )
    if (chunks):
        return chunks[0]
    else:
        return audio

async def save_chunk(chunk, i):
    voice_file = f"audio/{get_timestamp()}_tmp_voice_{i}.mp3"
    await generate_tts(chunk, voice_file)
    return AudioSegment.from_mp3(voice_file), voice_file

def adjust_chunk(chunk, i, speed, input_file):
    voice = AudioSegment.from_mp3(input_file)
    adjusted_file = f"audio/{get_timestamp()}_tmp_voice_adjusted_{i}.mp3"
    if speed > 1.0: # <= speed <= 2.0:
        #print(f"Velocidade de ajuste: {speed:.2f}x | start_ms={start_ms} | len={len(final_audio)} | duration={start_ms - len(final_audio)}")
        print(f"Velocidade de ajuste: {speed:.2f}x para o segmento '{chunk}'")
        adjust_speed(input_file, adjusted_file, speed)
        voice = AudioSegment.from_mp3(adjusted_file)
    else:
        print("Sem ajuste de velocidade necessário")
    return voice, adjusted_file

def adjust_silence(sub, final_audio):
    # inicio e duração da legenda em ms
    start_ms = srt_time_to_ms(sub["start"])
    if start_ms > len(final_audio):
        duration = start_ms - len(final_audio)
        silence = AudioSegment.silent(duration)
        print(f"Adicionando silêncio de {len(silence)}ms para alinhar com o início do segmento\n")
        final_audio += silence
    else:
        print("\n")

def remove_chunks(voice_file, adjusted_file):
    if os.path.exists(voice_file):
        os.remove(voice_file)
    if os.path.exists(adjusted_file):
        os.remove(adjusted_file)

async def gerar_narracao(subtitles, audio, output):
    parsed_subtitles = parse_srt(subtitles)
    await build_audio(parsed_subtitles, audio, output)

async def build_audio(subtitles, audio, output):
    final_audio = AudioSegment.silent(duration=0)
    #segments = transcribe(audio)
    for i, sub in enumerate(subtitles):
        target_duration = subtitle_duration_ms(sub["start"], sub["end"])
        # salvar cada pedaço de áudio em um arquivo temporário
        voice, voice_file = await save_chunk(sub["text"], i)
        # determinando velocidade de ajuste necessária para o pedaço de áudio se encaixar na duração da legenda
        speed = len(voice) / target_duration
        voice_adjusted, adjusted_file = adjust_chunk(sub["text"], i, speed, voice_file)
        # adicionando silêncio se necessário para alinhar o início do áudio com o início da legenda
        adjust_silence(sub, final_audio)
        if os.path.exists(adjusted_file):
            print(f"Adicionando ao áudio final: '{sub['text']}' | duração={len(voice_adjusted)}ms | início={sub['start']} | fim={sub['end']}\n")
            final_audio += voice_adjusted
        else:
            print(f"Adicionando ao áudio final: '{sub['text']}' | duração={len(voice)}ms | início={sub['start']} | fim={sub['end']}\n")
            final_audio += voice
        remove_chunks(voice_file, adjusted_file)
    final_audio.export(output, format="wav")
