import asyncio
from pdb import main

from libs import filesys
from application import aloiline

# -------------------------
# pipeline principal
# -------------------------

async def main():
    # Criar pastas necessárias
    filesys.create_folders()

    # Variáveis locais
    video = { 
        "title": None, 
        "code": None, 
        "url": None, 
        "clip": None, 
        "file": None, 
        "audio": None, 
        "subtitle": None, 
        "transcript": None,
        "narracao": None,
        "json": None
    }
    def isVideoLoaded():
        return video["title"] and video["code"] and video["url"] and video["clip"]
    def isAudioLoaded():
        return video["audio"]
    def isSubtitleLoaded():
        return video["subtitle"]
    def isJsonLoaded():
        return video["json"]
    
    # Menu de opções
    while(True):
        print('\n')
        print("===============================")
        print("Bem-vindo ao AloiLine!")
        print("===============================")
        print("Escolha uma opção:")
        print("-------------------------------")
        print("1. Importar vídeo do YouTube")
        print("2. Recortar Clipe e Audio")
        print("3. Transcrever e Gerar Legendas")
        print("4. Verificar Legendas")
        print("5. Gerar Narração")
        print("6. Mostrar dados do video")
        print("7. Salvar projeto")
        print("8. Gerar arquivo SRT")
        print("-------------------------------")
        print("9. Sair")
        print("===============================")
        choice = input("Digite o número da opção: ")
        if choice == "1":
            print("Importando vídeo...")
            print("------------------------------------------")
            nome_json_default = "videoclipe.json"
            nome_json = input("Digite o nome do arquivo (videoclipe.json): ")
            if not nome_json:
                nome_json = nome_json_default
            video["json"] = nome_json

            video_json = filesys.carregar_arquivo_json(nome_json)

            video["title"] = video_json["title"]
            video["code"] = video_json["code"]
            video["url"] = video_json["url"]
            video["clip"] = video_json["clip"]

            full_url = f"{video['url']}{video['code']}"
            video["file"] = aloiline.recuperar_video(full_url, video["title"], video["code"])
            print("------------------------------------------")
            print("Importação de vídeo finalizada!")
            print('\n')
        elif choice == "2":
            print("Recortando clipe e audio...")
            print("------------------------------------------")
            if (isVideoLoaded()):
                clip = video["clip"]
                clip_file, audio_file = aloiline.processar_clip_e_audio(clip["start"], clip["end"], clip["name"], video["file"])
                clip["file"] = clip_file
                video["audio"] = { "file": audio_file }
            else:
                print("Arquivo de vídeo não encontrado! Baixe o vídeo primeiro...")
            print("------------------------------------------")
            print("Recorte de clipe e audio finalizado!")
            print('\n')
        elif choice == "3":
            print("Transcrevendo audio e gerando legendas...")
            print("------------------------------------------")
            if (isVideoLoaded() and isAudioLoaded()):
                clip = video["clip"]
                audio = video["audio"]
                transcript_file, json_file, srt_file = aloiline.transcrever_audio_gerar_legendas(clip["name"], audio["file"])
                video["transcript"] = { "file": transcript_file }
                video["subtitle"] = { "file": json_file, "srt_file": srt_file }
            else:
                print("Arquivos de vídeo/áudio não encontrados! Execute as etapas anteriores, antes de continuar...")
            print("------------------------------------------")
            print("Transcrição e geração de legendas finalizadas!")
            print('\n')
        elif choice == "4":
            print("Verificar legendas...")
            print("------------------------------------------")
            if (isVideoLoaded() and isAudioLoaded() and isSubtitleLoaded()):
                subtitle = video["subtitle"] 
                clip = video["clip"]
                subtitles = filesys.carregar_arquivo_json(subtitle["file"])
                await aloiline.verificar_legendas_antes_continuar(clip["name"], subtitles)
            else:
                print("Arquivos de vídeo/áudio/legendas não encontrados! Execute as etapas anteriores, antes de continuar...")
            print("------------------------------------------")
            print("Verificação de legendas finalizada!")
            print('\n')
        elif choice == "5":
            print("Gerando narração...")
            print("------------------------------------------")
            if (isVideoLoaded() and isAudioLoaded() and isSubtitleLoaded()):
                subtitle = video["subtitle"] 
                clip = video["clip"]
                subtitles = filesys.carregar_arquivo_json(subtitle["file"])
                narracao_file = await aloiline.gerar_narracao(subtitles, clip["name"])
                video["narracao"] = { "file": narracao_file }
            else:
                print("Arquivo de vídeo não encontrado! Baixe o vídeo primeiro...")
            print("------------------------------------------")
            print("Geração de narração finalizada!")
            print('\n')
        elif choice == "6":
            print("Apresentando dados vídeo...")
            print("------------------------------------------")
            print(video)
            print("------------------------------------------")
            print("Apresentação de dados do vídeo finalizada!")
            print('\n')
        elif choice == "7":
            print("Salvando projeto de vídeo...")
            print("------------------------------------------")
            if (isVideoLoaded() and isAudioLoaded() and isSubtitleLoaded() and isJsonLoaded()):
                clip = video["clip"]
                narration = video["narracao"]
                nome_json = video["json"]
                subtitle = video["subtitle"]
                aloiline.salvar_projeto_na_pasta_release(video["title"], clip["file"], narration["file"], nome_json, subtitle["file"], subtitle["srt_file"])
            else:
                print("Arquivos de vídeo/áudio/legendas não encontrados! Execute as etapas anteriores, antes de continuar...")
            print("------------------------------------------")
            print("Salvamento do projeto de vídeo finalizada!")
            print('\n')
        elif choice == "8":
            print("Gerando arquivo SRT novamente...")
            print("------------------------------------------")
            subtitle = video["subtitle"]
            aloiline.gerar_srt_novamente(subtitle["file"], subtitle["srt_file"])
            print("------------------------------------------")
            print("Geração do arquivo SRT finalizada!")
            print('\n')
        elif choice == "9":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente...")

if __name__ == "__main__":
    asyncio.run(main())