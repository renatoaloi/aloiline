import subprocess
import json
import os
from pydub import AudioSegment

class WhisperVulkan:
    def __init__(self, exe_path, model_path):
        self.exe_path = exe_path
        self.model_path = model_path

    def _prepare_audio(self, input_file):
        """Converte qualquer áudio para WAV 16kHz Mono (o padrão do whisper.cpp)"""
        base_name = os.path.basename(input_file)
        temp_wav = f"temp_{base_name}.wav"
        
        # Carrega o áudio (MP3, WAV, etc)
        audio = AudioSegment.from_file(input_file)
        
        # Converte para os parâmetros exigidos pela GPU
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(temp_wav, format="wav")
        
        return temp_wav

    def transcribe(self, audio_file):
        ready_audio = self._prepare_audio(audio_file)
        json_output = f"{ready_audio}.json"

        # Usando as flags que funcionaram no seu binário novo
        command = [
            self.exe_path,
            "-m", self.model_path,
            "-f", ready_audio,
            "-dev", "0",
            "-oj"
        ]

        try:
            # check=True garante que o Python pare se o Whisper der erro
            subprocess.run(command, check=True, capture_output=True)
            
            if os.path.exists(json_output):
                with open(json_output, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # SÊNIOR TIP: Deletar temporários apenas após o sucesso
                os.remove(json_output)
                os.remove(ready_audio)
                
                return data.get("transcription", [])
        except subprocess.CalledProcessError as e:
            print(f"Erro na GPU: {e.stderr.decode()}")
        
        return []

# Configuração (ajuste se necessário)
EXE_PATH = r"C:\dev\aloitech\whisper.cpp\build\bin\Release\whisper-cli.exe"
MODEL_PATH = r"C:\dev\aloitech\whisper.cpp\models\ggml-medium.bin"
driver = WhisperVulkan(EXE_PATH, MODEL_PATH)