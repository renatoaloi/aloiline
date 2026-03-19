import datetime

from libs import filesys as fileLib, video as videoLib, audio as audioLib, legendas

agora = datetime.datetime.now()
def get_timestamp():
    return agora.strftime("%Y%m%d_%H%M%S")

def recuperar_video(video_url, title, pesquisa):
    downloads = [f for f in fileLib.listar_diretorio("downloads") if pesquisa in f]
    if (downloads):
        i = input("Vídeo já baixado, deseja refazer o download? (s/n): ")
        if i.lower() == "s":
            video_file = baixar_video_youtube(video_url, title)
        else:
            video_file = recuperar_video_local(downloads[0], title)
    else:
        video_file = baixar_video_youtube(video_url, title)
    return video_file

def baixar_video_youtube(video_url, title):
    print("\nBaixando vídeo:", title)
    video_file = videoLib.download_video(video_url, f"downloads/{get_timestamp()}")
    return video_file

def recuperar_video_local(file, title):
    print("\nRecuperando vídeo local:", title)
    video_file = fileLib.recuperar_arquivo_local("downloads", file)
    return video_file

def processar_clip_e_audio(clip_start, clip_end, clip_name, video_file):
    clip_file = f"clips/{get_timestamp()}_{clip_name}.mp4"
    audio_file = f"audio/{get_timestamp()}_{clip_name}.mp3"
    clips = [f for f in fileLib.listar_diretorio("clips") if clip_name in f]
    audios = [f for f in fileLib.listar_diretorio("audio") if clip_name + ".mp3" in f]
    if clips and audios:
        i = input(f"Clip e áudio para '{clip_name}' já existem, deseja reprocessar? (s/n): ")
        if i.lower() == "s":
            cortar_video_processar_audio(clip_start, clip_end, clip_file, video_file, audio_file)
        else:
            clip_file = fileLib.combinar_caminhos("clips", clips[0])
            audio_file = fileLib.combinar_caminhos("audio", audios[0])
    else:
        cortar_video_processar_audio(clip_start, clip_end, clip_file, video_file, audio_file)
    return clip_file, audio_file

def cortar_video_processar_audio(clip_start, clip_end, clip_file, video_file, audio_file):
    print("Cortando:", video_file, "->", clip_file)
    videoLib.cut_clip(video_file, clip_start, clip_end, clip_file)
    print("Extraindo áudio...")
    audioLib.extract_audio(clip_file, audio_file)

def transcrever_audio_gerar_legendas(clip_name, audio_file):
    transcript_file = f"transcripts/{get_timestamp()}_{clip_name}.json"
    srt_file = f"subtitles/{get_timestamp()}_{clip_name}.srt"
    srt_json = f"subtitles/{get_timestamp()}_{clip_name}.json"
    
    # check if transcript already exists
    transcript = [f for f in fileLib.listar_diretorio("transcripts") if clip_name in f]
    if (transcript):
        i = input(f"Transcrição para '{clip_name}' já existe, deseja reprocessar? (s/n): ")
        if i.lower() != "s":
            print(f"Carregando transcrição {transcript[0]}, aguarde...")
            segments = fileLib.carregar_arquivo_json(fileLib.combinar_caminhos("transcripts", transcript[0]))
            srt_json = fileLib.combinar_caminhos("transcripts", transcript[0])
        else:
            print("Transcrevendo, aguarde...")
            segments = legendas.transcrever_legendas(audio_file, transcript_file)
    else:
        print("Transcrevendo, aguarde...")
        segments = legendas.transcrever_legendas(audio_file, transcript_file)

    # check if subtitle already exists
    subtitles = [f for f in fileLib.listar_diretorio("subtitles") if clip_name in f]
    if (subtitles):
        i = input(f"Legenda para '{clip_name}' já existe, deseja reprocessar? (s/n): ")
        if i.lower() != "s":
            srt_json = fileLib.combinar_caminhos("subtitles", subtitles[0])
        else:
            print("Traduzindo legendas, aguarde...")
            segments_out = legendas.traduzir_legendas_em_lote(segments)
            print("Gerando arquivo de legendas...")
            srt_json = legendas.salvar_arquivo_json_legendas(segments_out, srt_json)
    else:
        print("Traduzindo legendas, aguarde...")
        segments_out = legendas.traduzir_legendas_em_lote(segments)
        print("Gerando arquivo de legendas...")
        srt_json = legendas.salvar_arquivo_json_legendas(segments_out, srt_json)

    return transcript_file, srt_json

async def gerar_narracao(subtitles, clip_name):
    if (input(f"Deseja gerar narração para '{clip_name}'? (s/n): ").lower() != "s"):
        return False
    print("Gerando narração em português, aguarde...")
    narration_file = f"audio/{get_timestamp()}_{clip_name}_narration.wav"
    voice_file = f"audio/{get_timestamp()}_tmp_voice_"
    adjusted_file = f"audio/{get_timestamp()}_tmp_voice_adjusted_"
    narracoes = [f for f in fileLib.listar_diretorio("audio") if f"{clip_name}_narration" in f]
    if narracoes:
        i = input(f"Narração para '{clip_name}' já existe, deseja refazer? (s/n): ")
        if i.lower() != "s":
            narration_file = fileLib.combinar_caminhos("audio", narracoes[0])
    
    await audioLib.build_audio(subtitles, narration_file, voice_file, adjusted_file)
    return narration_file
