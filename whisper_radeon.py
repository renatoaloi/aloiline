import subprocess
import json
import os
import tempfile

class WhisperRadeon:
    def __init__(self, exe_path, model_path):
        self.exe_path = exe_path
        self.model_path = model_path
        
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"Executável não encontrado: {exe_path}")

    def transcribe(self, audio_file):
        # O whisper.cpp gera um arquivo .json com o mesmo nome do áudio
        output_base = audio_file.replace(os.path. Howell.path.splitext(audio_file)[1], "")
        json_output = f"{audio_file}.json"

        # Comando para rodar na RX 7600
        # -ngl 999: Força todas as camadas na GPU
        # -oj: Output JSON
        # -nt: Sem timestamps no console (mais limpo)
        command = [
            self.exe_path,
            "-m", self.model_path,
            "-f", audio_file,
            "-ngl", "999",
            "-oj",
            "-nt"
        ]

        try:
            # Executa a transcrição
            subprocess.run(command, check=True, capture_output=True)
            
            # Lê o resultado gerado pelo whisper.cpp
            if os.path.exists(json_output):
                with open(json_output, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Limpeza: remove o arquivo JSON temporário após ler
                os.remove(json_output)
                
                # Retorna no formato compatível com seu código original (lista de segmentos)
                return data.get("transcription", [])
            
        except subprocess.CalledProcessError as e:
            print(f"Erro na GPU Radeon: {e.stderr.decode()}")
            return []

# Configuração de caminhos
EXE_GPU = r"C:\dev\aloitech\whisper.cpp\build\bin\Release\main.exe"
MODELO = r"C:\dev\aloitech\whisper.cpp\models\ggml-medium.bin"

# Instância global para ser usada no seu app
driver_whisper = WhisperRadeon(EXE_GPU, MODELO)