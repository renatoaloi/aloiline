import webrtcvad
import sys

from libs import filesys
from libs.gpu.whisper_vulkan import driver as transcriber
from libs.gpu.whisper_translator import driver as translator
from libs.silence import driver as silenceLib
from libs import audio as audioLib
from libs import util as utilLib

def transcrever_legendas(audio_file, transcript_file, tmp_file):
    temp_wav = transcriber.prepare_audio(audio_file)
    segments_in = gerar_timestamp_legendas(temp_wav, False)
    segments_out = []
    print("\n🎧 Segmentos de narração detectados:\n")
    for start, end in segments_in:
        tmp_file_del = f"{tmp_file}{round(start*1000)}.wav"
        print(f"{utilLib.format_time(start)} → {utilLib.format_time(end)}")
        audioLib.get_audio_part(temp_wav, start, end, tmp_file_del)
        segments = transcriber.transcribe(tmp_file_del)
        text = ""
        for segment in segments:
            text += f" {segment['text']}"
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

    for start, end in segments_in:
        tmp_file_del = f"{tmp_file}{round(start*1000)}.wav"
        filesys.remove_file(tmp_file_del)

    filesys.salvar_arquivo_json(transcript_file, segments_out)
    return segments

def traduzir_legendas_em_lote(transcript_file, json_file, srt_file):
    translator.translate(transcript_file, json_file, srt_file)

def salvar_arquivo_json_legendas(segments, file):
    filesys.salvar_arquivo_json(file, segments)

def gerar_arquivo_srt_legendas(data, srt_file):
    translator.json_to_srt(data, srt_file)

def gerar_timestamp_legendas(audio_file, is_mp3=True):
    # sound = AudioSegment.from_file(audio_file, format="mp3")
    # silent_ranges = detect_silence(
    #     sound, 
    #     min_silence_len=1000, 
    #     silence_thresh=-20
    # )
    # print("Detected silent ranges (ms):", silent_ranges)
    # for start_ms, end_ms in silent_ranges:
    #     print(f"Silence from {start_ms}ms to {end_ms}ms")
    # return silent_ranges

    temp_wav = audio_file
    if is_mp3:
        temp_wav = transcriber.prepare_audio(audio_file)

    audio, _ = audioLib.read_wave(temp_wav, silenceLib.sample_rate)
    frames = list(audioLib.frame_generator(audio, silenceLib.sample_rate, \
                                           silenceLib.frame_duration, \
                                            silenceLib.bytes_per_sample))
    vad = webrtcvad.Vad(silenceLib.vad_mode)
    raw_segments = audioLib.vad_collector(vad, frames, silenceLib.sample_rate, \
                                          silenceLib.frame_duration, \
                                            silenceLib.padding_frames)

    # print("\nRAW SEGMENTS:")
    # for s, e in raw_segments:
    #     print(f"{s:.2f} → {e:.2f}")

    merged = audioLib.merge_segments(raw_segments, silenceLib.max_gap)
    filtered = audioLib.filter_segments(merged, silenceLib.min_duration)

    #filesys.remove_file(temp_wav)
    
    refined_segments = []
    for start, end in filtered:
        start_frame = int(start / (silenceLib.frame_duration / 1000))
        end_frame = int(end / (silenceLib.frame_duration / 1000))
        new_start_frame = audioLib.refine_start(frames, start_frame, end_frame)
        new_start = new_start_frame * (silenceLib.frame_duration / 1000)
        refined_segments.append((new_start, end))

    return refined_segments