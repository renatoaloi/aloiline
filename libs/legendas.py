import webrtcvad
import sys

from libs import filesys
from libs.gpu.whisper_vulkan import driver as transcriber
from libs.gpu.whisper_translator import driver as translator
from libs.silence import driver as silenceLib
from libs import audio as audioLib
from libs import util as utilLib

def transcrever_legendas(audio_file, transcript_file, tmp_file):

    x_file = tmp_file + "full_temp.wav"
    print(f"temp_full_wav #0: {x_file}")

    # from mp3 to wav e retorna arquivo temp wave
    temp_full_wav = transcriber.prepare_audio(audio_file, x_file)

    print(f"temp_full_wav #1: {temp_full_wav} | X File: {x_file}")

    # separa segmentos de timestamp de legendas
    segments_in = gerar_timestamp_legendas(temp_full_wav, "", False)

    segments_out = []
    print("\n🎧 Segmentos de narração detectados:\n")
    for start, end in segments_in:
        start_ms = int(start * 1000)
        end_ms = int(end * 1000)
        print(f"{utilLib.format_time(start)} → {utilLib.format_time(end)}")

        print(f"temp_full_wav #2: {temp_full_wav}")
        
        temp_part_wav = tmp_file + f"part_temp_{start_ms}.wav"
        audioLib.get_audio_part(temp_full_wav, start_ms, end_ms, temp_part_wav)
        print(f"Part temp file: {temp_part_wav}")

        print(f"temp_full_wav #3: {temp_full_wav}")

        segments = transcriber.transcribe("", False, temp_part_wav)

        text = ""
        for segment in segments:
            text += f" {segment['text']}"
        
        if len(text.strip()) > 4: #minimo de caracteres para gerar timestamp, senão ignora
            segments_out.append({
                "timestamps": {
                    "from": utilLib.format_time(start),
                    "to": utilLib.format_time(end)
                },
                "offsets": {
                    "from": round(start*1000),
                    "to": round(end*1000)
                },
                "text": text.replace("  ", " ").strip()
            })

    #for start, end in segments_in:
    #    tmp_file_del = f"{tmp_file}{round(start*1000)}.wav"
    #    filesys.remove_file(tmp_file_del)

    filesys.limpar_temp_folder()
    filesys.salvar_arquivo_json(transcript_file, segments_out)
    return segments
    #return []

def traduzir_legendas_em_lote(transcript_file, json_file, srt_file):
    translator.translate(transcript_file, json_file, srt_file)

def salvar_arquivo_json_legendas(segments, file):
    filesys.salvar_arquivo_json(file, segments)

def gerar_arquivo_srt_legendas(data, srt_file):
    translator.json_to_srt(data, srt_file)

def gerar_timestamp_legendas(audio_file, tmp_file="", is_mp3=True):
    temp_wav = audio_file
    if is_mp3:
        temp_wav = transcriber.prepare_audio(audio_file, tmp_file + "timestamps.wav")

    audio, _ = audioLib.read_wave(temp_wav, silenceLib.sample_rate)
    frames = list(audioLib.frame_generator(audio, silenceLib.sample_rate, \
                                           silenceLib.frame_duration, \
                                            silenceLib.bytes_per_sample))
    vad = webrtcvad.Vad(silenceLib.vad_mode)
    raw_segments = audioLib.vad_collector(vad, frames, silenceLib.sample_rate, \
                                          silenceLib.frame_duration, \
                                            silenceLib.padding_frames)
    merged = audioLib.merge_segments(raw_segments, silenceLib.max_gap)
    filtered = audioLib.filter_segments(merged, silenceLib.min_duration)

    #filesys.remove_file(temp_wav)
    
    refined_segments = []
    for start, end in filtered:
        frame_duration_ms = round(silenceLib.frame_duration / 1000, 2)
        
        start_frame = int(start / frame_duration_ms)
        end_frame = int(end / frame_duration_ms)

        print(f"Start Frame: {start_frame} | End Frame: {end_frame}")

        new_start_frame = audioLib.refine_start(frames, start_frame, end_frame)
        new_start = new_start_frame * frame_duration_ms

        new_start = round(new_start, 2)
        print(f"New Start Frame: {new_start} | End Frame: {end_frame}")

        refined_segments.append((new_start, end))

    return refined_segments