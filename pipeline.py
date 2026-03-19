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
        "narracao": None
    }
    def isLoaded():
        return video["title"] and video["code"] and video["url"] and video["clip"]
    
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
            if (isLoaded()):
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
            if (isLoaded()):
                clip = video["clip"]
                audio = video["audio"]
                transcript_file, srt_file = aloiline.transcrever_audio_gerar_legendas(clip["name"], audio["file"])
                video["transcript"] = { "file": transcript_file }
                video["subtitle"] = { "file": srt_file }
            else:
                print("Arquivo de vídeo não encontrado! Baixe o vídeo primeiro...")
            print("------------------------------------------")
            print("Transcrição e geração de legendas finalizadas!")
            print('\n')
        elif choice == "4":
            print("Verificar legendas...")
            print("------------------------------------------")
            if (isLoaded()):
                subtitle = video["subtitle"] 
                clip = video["clip"]
                subtitles = filesys.carregar_arquivo_json(subtitle["file"])
                await aloiline.verificar_legendas_antes_continuar(clip["name"], subtitles)
            else:
                print("Arquivo de vídeo não encontrado! Baixe o vídeo primeiro...")
            print("------------------------------------------")
            print("Verificação de legendas finalizada!")
            print('\n')
        elif choice == "5":
            print("Gerando narração...")
            print("------------------------------------------")
            if (isLoaded()):
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
            if (isLoaded()):
                print(video)
            else:
                print("Arquivo de vídeo não encontrado! Baixe o vídeo primeiro...")
            print("------------------------------------------")
            print("Apresentação de dados do vídeo finalizada!")
            print('\n')
        elif choice == "7":
            print("Salvando projeto de vídeo...")
            print("------------------------------------------")
            if (isLoaded()):
                print(video)
            else:
                print("Arquivo de vídeo não encontrado! Baixe o vídeo primeiro...")
            print("------------------------------------------")
            print("Salvamento do projeto de vídeo finalizada!")
            print('\n')
        elif choice == "9":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente...")

if __name__ == "__main__":
    asyncio.run(main())