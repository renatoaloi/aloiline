from libs import filesys
from libs.gpu.whisper_vulkan import driver as transcriber
from libs.gpu.whisper_translator import driver as translator

def transcrever_legendas(audio_file, transcript_file):
    segments = transcriber.transcribe(audio_file)
    filesys.salvar_arquivo_json(transcript_file, segments)
    return segments

def traduzir_legendas_em_lote(transcript_file, json_file, srt_file):
    translator.translate(transcript_file, json_file, srt_file)

def salvar_arquivo_json_legendas(segments, file):
    filesys.salvar_arquivo_json(file, segments)

def gerar_arquivo_srt_legendas(data, srt_file):
    translator.json_to_srt(data, srt_file)
