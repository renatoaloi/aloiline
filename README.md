# AloiLine

Pipeline de automatização de criação de vídeos para canais dark do Youtube

# Instalação

### Instalar Python

Baixe:

https://www.python.org/downloads/

Instale normalmente.

> **Atenção**
>
> Caso tenha problemas com a versão mais atual do python, por causa de conflitos, utilize a versão 3.11, clicando no link da versão específica, abaixo:
>
> https://www.python.org/downloads/release/python-3119/

### Criar ambiente virtual

Dentro do seu projeto:

```bash
py -m venv venv
```

> **Atenção**:
>
> > Caso tenha problemas com a versão do Python, faça o downgrade para a versão 3.11 e execute o comando abaixo para criar o ambiente virtual.
>
> ```bash
> py -3.11 -m venv venv
> ```

### Ativar o ambiente

Windows:

```bash
venv\Scripts\activate
```

### Instalar dependências

Antes, atualize o pip:

```bash
python.exe -m pip install --upgrade pip
```

Agora sim:

```bash
pip install pydub openai-whisper yt-dlp deep-translator edge-tts audioop-lts torch torchvision torchaudio
```

> **Atenção**:
>
> > Caso esteja executando a versão 3.11 use o comando abaixo para instalar as dependências.
>
> ```bash
> pip install pydub openai-whisper yt-dlp deep-translator edge-tts torch torchvision torchaudio
> ```

# Utilização

Modos de utilizar

## Arquivo de configuração dos vídeos

Arquivo videos.json

```json
[
  {
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "clips": [
      { "start": "00:01:10", "end": "00:02:30" },
      { "start": "00:05:20", "end": "00:06:10" }
    ]
  }
]
```

# Revisões

## 2026-03-17

### feat: Implement audio processing pipeline with video transcription and subtitle generation

- Added audio.py for audio extraction, TTS generation, and audio adjustment.
- Introduced legendas.py for video transcription and subtitle translation.
- Created util.py for utility functions including timestamp generation and folder creation.
- Developed video.py for video downloading and clipping functionalities.
- Established pipeline.py to orchestrate video processing, audio generation, and subtitle handling.
- Added videos.json to define video metadata and clip segments.
- Integrated error handling and user prompts for existing files during processing.

### fix: Better silence alignment and transcription accuracy

- update .gitignore to include venv_11;
- modify audio processing logic for better subtitle alignment;
- change Whisper model to medium for improved transcription accuracy
