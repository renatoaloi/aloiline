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
pip install pydub openai-whisper yt-dlp deep-translator edge-tts audioop-lts
```

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
