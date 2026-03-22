import subprocess
import json
import os
from pydub import AudioSegment

class WhisperVulkan:
    def __init__(self, exe_path, model_path):
        self.exe_path = exe_path
        self.model_path = model_path

    def prepare_audio(self, input_file, temp_file=""):
        """Converte qualquer áudio para WAV 16kHz Mono (o padrão do whisper.cpp)"""
        base_name = os.path.basename(input_file)
        temp_wav = f"temp_{base_name}.wav"
        if (temp_file != ""):
            temp_wav = temp_file
        audio = AudioSegment.from_file(input_file)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(temp_wav, format="wav")
        return temp_wav

    def transcribe(self, audio_file, is_mp3=True, tmp_path=""):
        ready_audio = tmp_path
        if is_mp3:
            ready_audio = self.prepare_audio(audio_file)
        json_output = f"{ready_audio}.json"
        srt_output = f"{ready_audio}.srt"
        # Usando as flags que funcionaram no seu binário novo
        command = [
            self.exe_path,
            "-m", self.model_path,
            "-f", ready_audio,
            "-dev", "0",
            "-oj",
            "-osrt",
            "-sow",
            "-sns",
            "-t", "8"
        ]
        try:
            subprocess.run(command, check=True, capture_output=True)
            if os.path.exists(json_output):
                with open(json_output, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("transcription", [])
        except subprocess.CalledProcessError as e:
            print(f"Erro na GPU: {e.stderr.decode()}")
        return []

# Configuração (ajuste se necessário)
EXE_PATH = r"C:\dev\aloitech\whisper.cpp\build\bin\Release\whisper-cli.exe"
MODEL_PATH = r"C:\dev\aloitech\whisper.cpp\models\ggml-base.en.bin"

driver = WhisperVulkan(EXE_PATH, MODEL_PATH)