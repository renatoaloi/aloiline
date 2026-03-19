import subprocess
import json

from libs import util as utilLib

def PROMPT(list):
    return f"""Translate to Brazilian Portuguese. Return output in format: id|text. One translation per line. No need for aditional comments. No need to include the original text in the output. Keep natural spoken language. Keep translated sentences short. Use informal Brazilian Portuguese. No explanations.

INPUT:
{list}

OUTPUT:
"""

class VulkanLLMTranslator:
    def __init__(self, exe_path, model_path, gpu_layers=35, threads=8):
        self.exe_path = exe_path
        self.model_path = model_path
        self.gpu_layers = gpu_layers
        self.threads = threads
    
    def _build_command(self, prompt):
        return [
            self.exe_path,
            "-m", self.model_path,
            "-p", prompt,
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
            #"--grammar-file", r"C:\dev\aloitech\aloiline\grammars\json_array.gbnf",
            "--ctx-size", "512"
        ]

    def clear(self):
        command = self._build_command("/clear")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        try:
            process.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            process.kill()
            return "[ERRO: timeout]"

    def translate(self, texts):
        prompt = self._build_batch_prompt(texts)
        command = self._build_command(prompt)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        try:
            stdout, stderr = process.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            process.kill()
            return "[ERRO: timeout]"
        if not stdout:
            print("Deu erro: ", stderr)
            return []
        return self._clean_output(stdout)

    def _clean_output(self, output):
        print(f"Output: {output}")
        
        start_point1 = "OUTPUT:"
        start_point2 = "(truncated)"
        end_point = "\n\n"

        if (start_point1 in output):
            part1 = output.strip().split(start_point1)
        else:
            part1 = output.strip().split(start_point2)
        part2 = part1[-1].strip().split(end_point)
        output = part2[0]
        
        lines = output.strip().split("\n")
        translations = [l.split("|", 1)[1] for l in lines if "|" in l]
        
        print(f"Translations: {translations}")
        return translations

    def _build_batch_prompt(self, texts):
        formatted = "\n".join([f"{i+1}|{t}" for i, t in enumerate(texts)])
        return PROMPT(formatted)
