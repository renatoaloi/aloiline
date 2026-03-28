import datetime

from libs import filesys as fileLib
from libs import video as videoLib
from libs import audio as audioLib, legendas
from libs import util as utilLib

agora = datetime.datetime.now()
def get_timestamp():
    return agora.strftime("%Y%m%d_%H%M%S")

def extrair_trechos_narracao(audio_file):
    segments = legendas.gerar_timestamp_legendas(audio_file)
    print(f"\n🎧 Segmentos de narração detectados: {len(segments)}\n")
    if segments:
        for start, end in segments:
            print(f"{utilLib.format_time(start)} → {utilLib.format_time(end)}")

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

def transcrever_audio_gerar_legendas(clip_name, audio_file, volume):
    transcript_file = f"transcripts/{get_timestamp()}_{clip_name}.json"
    srt_file = f"subtitles/{get_timestamp()}_{clip_name}.srt"
    srt_json = f"subtitles/{get_timestamp()}_{clip_name}.json"
    tmp_file = f"temp/{get_timestamp()}_{clip_name}_"
    
    # check if transcript already exists
    transcript = [f for f in fileLib.listar_diretorio("transcripts") if clip_name in f]
    if (transcript):
        i = input(f"Transcrição para '{clip_name}' já existe, deseja reprocessar? (s/n): ")
        if i.lower() != "s":
            print(f"Carregando transcrição {transcript[0]}, aguarde...")
            fileLib.carregar_arquivo_json(fileLib.combinar_caminhos("transcripts", transcript[0]))
            transcript_file = fileLib.combinar_caminhos("transcripts", transcript[0])
        else:
            print("Transcrevendo, aguarde...")
            legendas.transcrever_legendas(audio_file, transcript_file, tmp_file, volume)
    else:
        print("Transcrevendo, aguarde...")
        legendas.transcrever_legendas(audio_file, transcript_file, tmp_file, volume)

    # check if subtitle already exists
    subtitles = [f for f in fileLib.listar_diretorio("subtitles") if clip_name in f and ".json" in f]
    if (subtitles):
        i = input(f"Legenda para '{clip_name}' já existe, deseja reprocessar? (s/n): ")
        if i.lower() != "s":
            srt_json = fileLib.combinar_caminhos("subtitles", subtitles[0])
            srt_files = [f for f in fileLib.listar_diretorio("subtitles") if clip_name in f and ".srt" in f]
            srt_file = fileLib.combinar_caminhos("subtitles", srt_files[0])
        else:
            print("Traduzindo legendas, aguarde...")
            legendas.traduzir_legendas_em_lote(transcript_file, srt_json, srt_file)
    else:
        print("Traduzindo legendas, aguarde...")
        legendas.traduzir_legendas_em_lote(transcript_file, srt_json, srt_file)

    return transcript_file, srt_json, srt_file

async def gerar_narracao(subtitles, clip_name):
    print("Gerando narração em português, aguarde...")
    narration_file = f"audio/{get_timestamp()}_{clip_name}_narration.wav"
    voice_file = f"temp/{get_timestamp()}_tmp_voice_"
    narracoes = [f for f in fileLib.listar_diretorio("audio") if f"{clip_name}_narration" in f]
    if narracoes:
        narration_file = fileLib.combinar_caminhos("audio", narracoes[0])
        i = input(f"Narração para '{clip_name}' já existe, deseja refazer? (s/n): ")
        if i.lower() == "s":
            await audioLib.build_audio(subtitles, narration_file, voice_file)
    else:
        await audioLib.build_audio(subtitles, narration_file, voice_file)
    return narration_file

async def verificar_legendas_antes_continuar(clip_name, subtitles):
    voice_file = f"audio/{get_timestamp()}_tmp_voice_verify_"
    if (input(f"Deseja verificar a narração para '{clip_name}' antes de gerar? (s/n): ").lower() == "s"):
        if (await audioLib.verify_audio(subtitles, voice_file)):
            print("Áudio verificado com sucesso.")
        else:
            print("Problemas encontrados!")
            return False
    return True

def salvar_projeto_na_pasta_release(video_title, clip_file, narration_file, nome_json, subtitle_file, subtitle_srt):
    print(f"titulo do video: {video_title} | clipe: {clip_file} | narração: {narration_file}")

    # criando pasta do projeto
    print(f"Criando folder {video_title} ...")
    fileLib.create_folder(fileLib.combinar_caminhos("release", video_title))

    # copiando arquivo json de configuração
    config_path = fileLib.combinar_caminhos("release", video_title)
    config_file = fileLib.combinar_caminhos(config_path, nome_json)
    fileLib.copy_file(nome_json, config_file)
    
    # copiando clipe
    clip_filename = clip_file.replace("/", "\\")
    clip_filename = clip_filename.split("\\")[-1]
    clips_path = fileLib.combinar_caminhos("release", video_title)
    print(f"Copiando arquivo {clip_file} para {clips_path}...")
    fileLib.copy_file(clip_file, fileLib.combinar_caminhos(clips_path, clip_filename))

    # copiando narração
    narration_filename = narration_file.replace("/", "\\")
    narration_filename = narration_filename.split("\\")[-1]
    narration_path = fileLib.combinar_caminhos("release", video_title)
    print(f"Copiando arquivo {narration_file} para {narration_path}...")
    fileLib.copy_file(narration_file, fileLib.combinar_caminhos(narration_path, narration_filename))

    # copiando legendas
    legendas_filename = subtitle_file.replace("/", "\\")
    legendas_filename = legendas_filename.split("\\")[-1]
    legendas_path = fileLib.combinar_caminhos("release", video_title)
    print(f"Copiando arquivo {subtitle_file} para {legendas_path}...")
    fileLib.copy_file(subtitle_file, fileLib.combinar_caminhos(legendas_path, legendas_filename))

    # copiando legendas
    legendas_filename = subtitle_srt.replace("/", "\\")
    legendas_filename = legendas_filename.split("\\")[-1]
    legendas_path = fileLib.combinar_caminhos("release", video_title)
    print(f"Copiando arquivo {subtitle_srt} para {legendas_path}...")
    fileLib.copy_file(subtitle_srt, fileLib.combinar_caminhos(legendas_path, legendas_filename))

def gerar_srt_novamente(json_file, srt_file):
    data = fileLib.carregar_arquivo_json(json_file)
    legendas.gerar_arquivo_srt_legendas(data, srt_file)