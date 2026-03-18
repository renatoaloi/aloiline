from whisper_vulkan import driver
from deep_translator import GoogleTranslator
import re

from util import format_time, get_timestamp, srt_time_to_ms

# -------------------------
# Translator
# -------------------------
def get_translator(source='en', target='pt'):
    return GoogleTranslator(source, target)

def translate_segment(text="", language_in="en", language_out="pt"):
    return get_translator(source=language_in, target=language_out).translate(text)

# -------------------------
# Transcrições
# -------------------------

def transcrever_legendas(audio_file, clip_name):
    print("Transcrevendo")
    segments = transcribe(audio_file)
    print("Salvando traduções e legendas")
    file_str = save_srt(clip_name, segments, "en", "pt")
    return file_str

def transcribe(audio_file):
    # O driver_whisper retorna os segmentos formatados
    segments = driver.transcribe(audio_file)
    if segments is None:
        print("Erro: O driver não retornou nenhum segmento.")
        return []
    return segments

# -------------------------
# Legendas
# -------------------------
def save_srt(base_name, segments, language_in, language_out):
    file_path = f"subtitles/{get_timestamp()}_{base_name}_{language_out}.srt"
    with open(file_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            # Tenta pegar milissegundos do formato novo (offsets: {from, to})
            if "offsets" in seg:
                start_ms = seg["offsets"].get("from", 0)
                end_ms = seg["offsets"].get("to", 0)
            # Tenta formato alternativo (t0, t1 em centésimos de segundo)
            else:
                start_ms = seg.get("t0", 0) * 10 
                end_ms = seg.get("t1", 0) * 10
            # Converte para segundos para a função format_time
            start_sec = start_ms / 1000.0
            end_sec = end_ms / 1000.0
            # Segurança: Se o tempo for igual, adiciona 1ms para evitar divisão por zero
            if start_sec == end_sec:
                end_sec += 0.001
            start = format_time(start_sec)
            end = format_time(end_sec)
            text_in = seg.get("text", "").strip()
            text_out = translate_segment(text_in, language_in, language_out)
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text_out}\n\n")
    return file_path

def parse_srt(path):
    subtitles = []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    blocks = re.split(r"\n\s*\n", content)
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        times = lines[1]
        text = " ".join(lines[2:])
        start, end = times.split(" --> ")
        subtitles.append({
            "start": start,
            "end": end,
            "text": text
        })
    return subtitles

def subtitle_duration_ms(start, end):
    return srt_time_to_ms(end) - srt_time_to_ms(start)