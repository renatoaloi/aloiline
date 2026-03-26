from libs import audio as audioLib
from libs.gpu.whisper_vulkan import driver as transcriber

#tmp_file = ""
video_file = r"G:\Youtube\YoutubeCursos\AloiNoticias\Lei Felca Aloi noticias.mp4"
tmp_part_file = "G:\Youtube\YoutubeCursos\AloiNoticias\Lei Felca Aloi noticias.mp3"
audioLib.extract_audio(video_file, tmp_part_file)
#audioLib.get_audio_part(tmp_file, 0, 10000, tmp_part_file)
#audio = audioLib.get_audio_segment(tmp_part_file)
segments = transcriber.transcribe(tmp_part_file)
for s in segments:
    print(s)