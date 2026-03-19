import os
import json
import shutil 

def create_folders(parent_folder = ""):
    folders = ["downloads", "clips", "audio", "transcripts", "subtitles", "release"]
    for f in folders:
        path_combined = combinar_caminhos(parent_folder, f)
        os.makedirs(path_combined, exist_ok=True)

def create_folder(path):
    os.makedirs(path, exist_ok=True)

def recuperar_arquivo_local(path, title):
    return os.path.join(path, title)

def carregar_arquivo_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_arquivo(file):
    s = ""
    with open(file, "r", encoding="utf-8") as f:
        s += f.read()
    return s
    
def salvar_arquivo_json(file, dados):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def salvar_arquivo(file, dados):
    with open(file, 'w', encoding='utf-8') as f:
        f.write(dados)

def listar_diretorio(dir):
    return os.listdir(dir)

def combinar_caminhos(path, file):
    return os.path.join(path, file)

def file_exists(file):
    return os.path.exists(file)

def remove_file(file):
    os.remove(file)

def copy_file(_from, _to):
    shutil.copyfile(_from, _to)