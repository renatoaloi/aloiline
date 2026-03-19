import os
import json

def create_folders():
    folders = ["downloads", "clips", "audio", "transcripts", "subtitles"]
    for f in folders:
        os.makedirs(f, exist_ok=True)

def recuperar_arquivo_local(path, title):
    return os.path.join(path, title)

def carregar_video_do_arquivo_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)
    
def salvar_arquivo_json(file, dados):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def listar_diretorio(dir):
    return os.listdir(dir)

def combinar_caminhos(path, file):
    return os.path.join(path, file)
