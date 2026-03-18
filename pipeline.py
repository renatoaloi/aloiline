import asyncio
from pdb import main

from application.process import \
    confirmar_gerar_narracao, gerar_legendas, processar_audio_video, \
    recuperando_video_youtube, verificar_legendas_antes_continuar
from libs.util import create_folders
from libs.video import load_videos_from_json

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