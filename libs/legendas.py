import json

from libs import filesys
from libs.gpu.whisper_vulkan import driver as transcriber
from libs.gpu.translator_vulkan import VulkanLLMTranslator 

BATCH_SIZE = 5

translator = VulkanLLMTranslator(
    exe_path=r"C:\dev\aloitech\llama.cpp\build\bin\Release\llama-cli.exe",          # binário do llama.cpp Vulkan
    model_path=r"C:\dev\aloitech\llama.cpp\models\mistral-7b-instruct-v0.2.Q4_K_M.gguf"
)

def transcrever_legendas(audio_file, transcript_file):
    segments = transcriber.transcribe(audio_file)
    filesys.salvar_arquivo_json(transcript_file, segments)
    return segments

def traduzir_legendas(segments):
    # texts = [seg["text"] for seg in segments]
    # batch_size = 20
    # translated_texts = []
    # for i in range(0, len(texts), batch_size):
    #     batch = texts[i:i + batch_size]
    #     translated = translator.translate_batch(batch)
    #     translated_texts.extend(translated)
    # result = []
    # for seg, pt_text in zip(segments, translated_texts):
    #     result.append({
    #         **seg,
    #         "text_pt": pt_text
    #     })
    # return result
    result = []
    total = len(segments)
    for i, seg in enumerate(segments):
        print(f"Traduzindo {i+1}/{total}...")
        translated = translator.translate(seg["text"])
        result.append({
            **seg,
            "text_pt": translated
        })
        print(f"Traduzido: {translated}")
    return result

def traduzir_legendas_em_lote(segments):
    traducoes = []
    for i in range(0, len(segments), BATCH_SIZE):
        batch = segments[i:i+BATCH_SIZE]
        texts = [s["text"] for s in batch]

        output = translator.translate(texts)
        traducoes = output

        for seg, trad in zip(batch, traducoes):
            seg["text_pt"] = trad
    return traducoes

def salvar_arquivo_srt_legendas(segments, file):
    return "legendas.srt"

def salvar_arquivo_json_legendas(segments, file):
    filesys.salvar_arquivo_json(file, segments)

#print("Salvando traduções e legendas")
#file_str = save_srt(clip_name, segments, "en", "pt")

# from libs.gpu.whisper_vulkan import driver
# #from deep_translator import GoogleTranslator
# from libs.gpu.whisper_vulkan import driver
# from libs.gpu.translator_vulkan import VulkanLLMTranslator
# import re

# from libs.util import format_time, srt_time_to_ms
# #from application.aloiline import get_timestamp

# # -------------------------
# # Translator
# # -------------------------

# translator = VulkanLLMTranslator(
#     exe_path=r"C:\dev\llm\main.exe",          # binário do llama.cpp Vulkan
#     model_path=r"C:\dev\llm\models\mistral.gguf"
# )

# #def get_translator(source='en', target='pt'):
# #    return GoogleTranslator(source, target)

# # def translate_segment(text="", language_in="en", language_out="pt"):
# #     return get_translator(source=language_in, target=language_out).translate(text)

# def translate_segments(segments, translator):
#     translated = []
#     for seg in segments:
#         pt_text = translator.translate(seg["text"])
#         translated.append({
#             **seg,
#             "text_pt": pt_text
#         })
#     return translated

# def batch_segments(segments, max_chars=500):
#     batch = []
#     current = ""
#     for seg in segments:
#         if len(current) + len(seg["text"]) < max_chars:
#             current += " " + seg["text"]
#         else:
#             batch.append(current.strip())
#             current = seg["text"]
#     if current:
#         batch.append(current.strip())
#     return batch

# # -------------------------
# # Transcrições
# # -------------------------

# def transcrever_legendas(audio_file, clip_name):
#     print("Transcrevendo")
#     segments = transcribe(audio_file)
#     print("Salvando traduções e legendas")
#     file_str = save_srt(clip_name, segments, "en", "pt")
#     return file_str

# def transcribe(audio_file):
#     # O driver_whisper retorna os segmentos formatados
#     segments = driver.transcribe(audio_file)
#     if segments is None:
#         print("Erro: O driver não retornou nenhum segmento.")
#         return []
#     return segments

# # -------------------------
# # Legendas
# # -------------------------

# def process_audio(audio_file):
#     # 1. Transcrição (já com sua GPU AMD)
#     segments = driver.transcribe(audio_file)

#     if not segments:
#         return []

#     # 2. Extrair textos
#     texts = [seg["text"] for seg in segments]

#     # 3. Batching inteligente
#     batch_size = 8
#     translated_texts = []

#     for i in range(0, len(texts), batch_size):
#         batch = texts[i:i + batch_size]
#         translated = translator.translate_batch(batch)
#         translated_texts.extend(translated)

#     # 4. Recombinar com timestamps
#     result = []
#     for seg, pt_text in zip(segments, translated_texts):
#         result.append({
#             **seg,
#             "text_pt": pt_text
#         })

#     return result


# def save_srt(base_name, segments, language_in, language_out):
#     # file_path = f"subtitles/{get_timestamp()}_{base_name}_{language_out}.srt"
#     # with open(file_path, "w", encoding="utf-8") as f:
#     #     for i, seg in enumerate(segments, start=1):
#     #         # Tenta pegar milissegundos do formato novo (offsets: {from, to})
#     #         if "offsets" in seg:
#     #             start_ms = seg["offsets"].get("from", 0)
#     #             end_ms = seg["offsets"].get("to", 0)
#     #         # Tenta formato alternativo (t0, t1 em centésimos de segundo)
#     #         else:
#     #             start_ms = seg.get("t0", 0) * 10 
#     #             end_ms = seg.get("t1", 0) * 10
#     #         # Converte para segundos para a função format_time
#     #         start_sec = start_ms / 1000.0
#     #         end_sec = end_ms / 1000.0
#     #         # Segurança: Se o tempo for igual, adiciona 1ms para evitar divisão por zero
#     #         if start_sec == end_sec:
#     #             end_sec += 0.001
#     #         start = format_time(start_sec)
#     #         end = format_time(end_sec)
#     #         text_in = seg.get("text", "").strip()
#     #         text_out = translate_segment(text_in, language_in, language_out)
#     #         f.write(f"{i}\n")
#     #         f.write(f"{start} --> {end}\n")
#     #         f.write(f"{text_out}\n\n")
#     # return file_path
#     pass

# def parse_srt(path):
#     subtitles = []
#     with open(path, "r", encoding="utf-8") as f:
#         content = f.read()
#     blocks = re.split(r"\n\s*\n", content)
#     for block in blocks:
#         lines = block.strip().split("\n")
#         if len(lines) < 3:
#             continue
#         times = lines[1]
#         text = " ".join(lines[2:])
#         start, end = times.split(" --> ")
#         subtitles.append({
#             "start": start,
#             "end": end,
#             "text": text
#         })
#     return subtitles

# def subtitle_duration_ms(start, end):
#     return srt_time_to_ms(end) - srt_time_to_ms(start)