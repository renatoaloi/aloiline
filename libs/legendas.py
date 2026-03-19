from libs import filesys
from libs.gpu.whisper_vulkan import driver as transcriber
from libs.gpu.translator_vulkan import VulkanLLMTranslator 

BATCH_SIZE = 10

translator = VulkanLLMTranslator(
    exe_path=r"C:\dev\aloitech\llama.cpp\build\bin\Release\llama-cli.exe",          # binário do llama.cpp Vulkan
    model_path=r"C:\dev\aloitech\llama.cpp\models\mistral-7b-instruct-v0.2.Q4_K_M.gguf"
)

def transcrever_legendas(audio_file, transcript_file):
    segments = transcriber.transcribe(audio_file)
    filesys.salvar_arquivo_json(transcript_file, segments)
    return segments

def traduzir_legendas(segments):
    result = []
    total = len(segments)
    for i, seg in enumerate(segments):
        translated = translator.translate(seg["text"])
        result.append({
            **seg,
            "text_pt": translated
        })
    return result

def traduzir_legendas_em_lote(segments):
    traducoes = []
    for i in range(0, len(segments), BATCH_SIZE):
        batch = segments[i:i+BATCH_SIZE]
        texts = [s["text"] for s in batch]
        
        translated_texts = translator.translate(texts)
        
        for seg, pt_text in zip(batch, translated_texts):
            traducoes.append({
                **seg,
                "text_pt": pt_text
            })
    return traducoes

def salvar_arquivo_srt_legendas(segments, file):
    return "legendas.srt"

def salvar_arquivo_json_legendas(segments, file):
    filesys.salvar_arquivo_json(file, segments)
