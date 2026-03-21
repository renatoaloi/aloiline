import json
import torch_directml
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class WhisperTranslator:
    def __init__(self, model_name, batch_size, tgt_lang):
        self.model_name = model_name
        self.batch_size = batch_size
        self.tgt_lang = tgt_lang
        self.device = torch_directml.device()
        print(f"Usando dispositivo: {self.device}")
        print("Carregando modelo...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name,
            use_safetensors=True
        ).to(self.device)
    
    def translate(self, input_file, output_file, srt_file):
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        buffer = []
        indices = []
        for i, item in enumerate(data):
            text = item["text"].strip()
            if text:
                buffer.append(text)
                indices.append(i)
            if len(buffer) >= self.batch_size:
                translated = self._translate_batch(buffer)
                for idx, t in zip(indices, translated):
                    data[idx]["text"] = t
                buffer = []
                indices = []
        if buffer:
            translated = self._translate_batch(buffer)
            for idx, t in zip(indices, translated):
                data[idx]["text"] = t
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        self.json_to_srt(data, srt_file)
        print("✅ Tradução JSON concluída!")

    def json_to_srt(self, data, srt_file):
        srt_lines = []
        for i, item in enumerate(data, start=1):
            start = item["timestamps"]["from"]
            end = item["timestamps"]["to"]
            text = item["text"]
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(text)
            srt_lines.append("")  # linha em branco
        with open(srt_file, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_lines))

    def _translate_batch(self, text_list):
        inputs = self.tokenizer(
            text_list,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        outputs = self.model.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(self.tgt_lang),
            max_new_tokens=128,
            num_beams=1,
            do_sample=False,
            repetition_penalty=1.2,
        )

        decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        return [t.strip() for t in decoded]


MODEL_NAME = "facebook/nllb-200-distilled-600M"
SRC_LANG = "eng_Latn"
TGT_LANG = "por_Latn"
BATCH_SIZE = 16

driver = WhisperTranslator(MODEL_NAME, BATCH_SIZE, TGT_LANG)