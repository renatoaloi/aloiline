import asyncio
import os
from pdb import main

from legendas import parse_srt, transcrever_legendas
from util import create_folders, get_timestamp
from video import download_video, cut_clip, load_videos_from_json
from audio import extract_audio, gerar_narracao, verify_audio

def recuperando_video_youtube(video, title):
    print("\nBaixando vídeo:", title)
    pesquisa = video["url"].split("v=")[-1]
    downloads = [f for f in os.listdir("downloads") if pesquisa in f]
    if (downloads):
        i = input("Vídeo já baixado, deseja refazer o download? (s/n): ")
        if i.lower() == "s":
            video_file = download_video(video["url"])
        else:
            video_file = os.path.join("downloads", downloads[0])
    else:
        video_file = download_video(video["url"])
    return video_file

def cortar_video_processar_audio(clip, clip_file, video_file, audio_file):
    print("Cortando:", video_file, "->", clip_file)
    cut_clip(video_file, clip["start"], clip["end"], clip_file)
    print("Extraindo áudio")
    extract_audio(clip_file, audio_file)

def processar_audio_video(clip, clip_name, video_file):
    clip_file = f"clips/{get_timestamp()}_{clip_name}.mp4"
    audio_file = f"audio/{get_timestamp()}_{clip_name}.mp3"
    clips = [f for f in os.listdir("clips") if clip_name in f]
    audios = [f for f in os.listdir("audio") if clip_name + ".mp3" in f]
    if clips and audios:
        i = input(f"Clip e áudio para '{clip_name}' já existem, deseja reprocessar? (s/n): ")
        if i.lower() == "s":
            cortar_video_processar_audio(clip, clip_file, video_file, audio_file)
        else:
            clip_file = os.path.join("clips", clips[0])
            audio_file = os.path.join("audio", audios[0])
    else:
        cortar_video_processar_audio(clip, clip_file, video_file, audio_file)
    return audio_file

def gerar_legendas(clip_name, audio_file):
    subtitles = [f for f in os.listdir("subtitles") if clip_name in f]
    if (subtitles):
        i = input(f"Legenda para '{clip_name}' já existe, deseja reprocessar? (s/n): ")
        if i.lower() != "s":
            file_str = os.path.join("subtitles", subtitles[0])
        else:
            file_str = transcrever_legendas(audio_file, clip_name)
    else:
        file_str = transcrever_legendas(audio_file, clip_name)
    return file_str, True

async def verificar_legendas_antes_continuar(clip_name, file_str):
    if (input(f"Deseja verificar a narração para '{clip_name}' antes de gerar? (s/n): ").lower() == "s"):
        if (await verify_audio(parse_srt(file_str))):
            print("Áudio verificado com sucesso.")
        else:
            if input("Problemas encontrados, deseja continuar mesmo assim? (s/n): ").lower() != "s":
                return False
    return True

async def confirmar_gerar_narracao(clip_name, file_str, audio_file):
    if (input(f"Deseja gerar narração para '{clip_name}'? (s/n): ").lower() != "s"):
        return False
    print("Gerando narração em português")
    narration_file = f"audio/{get_timestamp()}_{clip_name}_narration.wav"
    narracoes = [f for f in os.listdir("audio") if f"{clip_name}_narration" in f]
    if narracoes:
        i = input(f"Narração para '{clip_name}' já existe, deseja refazer? (s/n): ")
        if i.lower() != "s":
            return False
        narration_file = os.path.join("audio", narracoes[0])
    await gerar_narracao(file_str, audio_file, narration_file)
    return True

# -------------------------
# pipeline principal
# -------------------------

async def main():
    create_folders()
    videos = load_videos_from_json()
    for video in videos:
        title = video["title"]
        video_file = recuperando_video_youtube(video, title)
        for clip in video["clips"]:
            clip_name = f"{title}_{clip['name']}"
            audio_file = processar_audio_video(clip, clip_name, video_file)
            file_str, resposta = gerar_legendas(clip_name, audio_file)
            if resposta:
                await verificar_legendas_antes_continuar(clip_name, file_str)
                await confirmar_gerar_narracao(clip_name, file_str, audio_file)
    print("\nPipeline concluído!")


if __name__ == "__main__":
    asyncio.run(main())