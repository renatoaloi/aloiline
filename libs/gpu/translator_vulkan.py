# You are a professional subtitle translator.

# Rules:
# - Translate to Brazilian Portuguese
# - Keep natural spoken language
# - Adapt idioms (do not translate literally)
# - Keep sentences short
# - Preserve meaning, not words
# - Use informal Brazilian Portuguese
# - Make it engaging and natural for YouTube
# - No explanations
# - No need to repeat the original sentence
# - No aditional info, only the translated line
# - Do not translate scene description for audio impairing
# - Do not translate description narrative

# Text:
# {text}

# Subtitle:

# You are a professional subtitle translator.

# Rules:
# - Translate to Brazilian Portuguese
# - Keep natural spoken language
# - Adapt idioms (do not translate literally)
# - Keep sentences short
# - Preserve meaning, not words
# - Use informal Brazilian Portuguese
# - Make it engaging and natural for YouTube
# - No explanations
# - No need to repeat the original sentence
# - No aditional info, only the translated line
# - Do not translate scene description for audio impairing
# - Do not translate description narrative
# - Ignore sound descriptions like (laughs), (music), (heavy breathing), etc.
# - If a line is ONLY a sound description, return an empty string ""
# - Translate ONLY spoken dialogue

# Return ONLY a JSON array of strings.

# ### INPUT:
# {formatted}

# ### OUTPUT:

import subprocess
import json

from libs import util as utilLib

class VulkanLLMTranslator:
    def __init__(self, exe_path, model_path, gpu_layers=35, threads=8):
        self.exe_path = exe_path
        self.model_path = model_path
        self.gpu_layers = gpu_layers
        self.threads = threads

    def translate(self, texts):
        command = [
            self.exe_path,
            "-m", self.model_path,
            "-p", self._build_batch_prompt(texts),
            "-n", "512",
            "--temp", "0",
            "--top-k", "1",
            "--repeat-penalty", "1.0",
            "-ngl", str(self.gpu_layers),
            "-t", str(self.threads),
            "-st",
            "--log-disable",
            "--no-display-prompt",
            "--log-colors", "off",
            "--verbosity", "0",
            "--grammar-file", r"C:\dev\aloitech\aloiline\grammars\json_array.gbnf",
            "--ctx-size", "512"
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )

        print(f"Command: {command}")

        try:
            stdout, stderr = process.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            process.kill()
            return "[ERRO: timeout]"

        print("Aqui #1: ", stdout)
        if not stdout:
            print("Deu erro: ", stderr)
        else:
            stdout = utilLib.extract_json_array(stdout)
            print("Aqui #2: ", stdout)

        return self._clean_output(stdout)

    def _clean_output(self, output):
        return json.loads(output)

    def _build_batch_prompt(self, texts):
        formatted = "\n".join([f"{i}. {t}" for i, t in enumerate(texts)])
        
        return f"""Halt any response until you detect the RESPONSE section.
I am not human, I am a virtual agent working by an API contract.
No need comments, notes or whatsoever.
I can not respond and I will accept ONLY a JSON array of strings as response.
The input is under INPUT section and is separated by line and each line starts with a sequence number followed by a dot and a space character.
Translate the INPUT list to Brazilian Portuguese.
The JSON response array item does not need to contain the sequence number nor the dot that follows.
The JSON response array item must be trimmed for start and end spaces.

INPUT:
{formatted}

RESPONSE:
"""


# Halt any response until you detect the RESPONSE section.
# I am not human, I am a virtual agent working by an API contract.
# No need comments, notes or whatsoever.
# I can not respond and I will accept ONLY a JSON array of strings as response.
# The input is under INPUT section and is separated by line and each line starts with a sequence number followed by a dot and a space character.
# Translate the INPUT list to Brazilian Portuguese.
# The JSON response array item does not need to contain the sequence number nor the dot that follows.
# The JSON response array item must be trimmed for start and end spaces.

# INPUT:
# {formatted}

# RESPONSE:



# import subprocess

# class VulkanLLMTranslator:
#     def __init__(self, exe_path, model_path, gpu_layers=35, threads=8):
#         self.exe_path = exe_path
#         self.model_path = model_path
#         self.gpu_layers = gpu_layers
#         self.threads = threads

#     def _build_prompt(self, text):
#         return f"""You are a professional subtitle translator.

# Rules:
# - Translate to Brazilian Portuguese
# - Keep natural spoken language
# - Adapt idioms (do not translate literally)
# - Keep sentences short
# - Preserve meaning, not words
# - Use informal Brazilian Portuguese
# - Make it engaging and natural for YouTube
# - No explanations

# Text:
# {text}

# Subtitle:
# """

#     def translate_batch(self, texts):
#         """
#         Traduz múltiplos segmentos de uma vez (MUITO mais rápido)
#         """
#         joined_text = "\n".join([f"[{i}] {t}" for i, t in enumerate(texts)])
#         prompt = self._build_prompt(joined_text)
#         command = [
#             self.exe_path,
#             "-m", self.model_path,
#             "-p", prompt,
#             "-n", "512",
#             "--temp", "0.3",
#             "--top-k", "40",
#             "--top-p", "0.9",
#             "--repeat-penalty", "1.1",
#             "-ngl", str(self.gpu_layers),
#             "-t", str(self.threads),
#             "--stop", "Subtitle:"
#         ]
#         result = subprocess.run(
#             command,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             timeout=120  # MUITO IMPORTANTE
#         )
#         output = result.stdout.strip()
#         print(output)
#         return self._parse_output(output, len(texts))

#     def _parse_output(self, output, expected_size):
#         """
#         Espera algo tipo:
#         [0] tradução...
#         [1] tradução...
#         """
#         lines = output.split("\n")
#         results = [""] * expected_size
#         for line in lines:
#             if line.startswith("["):
#                 try:
#                     idx = int(line.split("]")[0][1:])
#                     text = line.split("]", 1)[1].strip()
#                     if 0 <= idx < expected_size:
#                         results[idx] = text
#                 except:
#                     pass

#         return results
