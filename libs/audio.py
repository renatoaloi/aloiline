import subprocess
import edge_tts
import contextlib
import wave
import collections
import audioop

from pydub import AudioSegment
from pydub.silence import detect_silence
from pydub.effects import speedup
from libs import util as utilLib, filesys

def merge_segments(segments, max_gap):
    if not segments:
        return []
    merged = []
    current_start, current_end = segments[0]
    for start, end in segments[1:]:
        if start - current_end <= max_gap:
            current_end = end
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    merged.append((current_start, current_end))
    return merged

def filter_segments(segments, min_duration):
    return [(s, e) for s, e in segments if (e - s) >= min_duration]

def refine_start(frames, start_frame, end_frame):
    for i in range(start_frame, end_frame):
        rms = audioop.rms(frames[i], 2)
        if rms > 1200:
            return i
    return start_frame

def is_valid_speech(frame, vad, sample_rate):
    rms = audioop.rms(frame, 2)
    if rms < 900:
        return False
    return vad.is_speech(frame, sample_rate)

def vad_collector(vad, frames, sample_rate, frame_duration, padding_frames):
    segments = []
    triggered = False
    start = 0

    frame_time = frame_duration / 1000
    buffer = collections.deque(maxlen=padding_frames)

    for i, frame in enumerate(frames):
        is_speech = is_valid_speech(frame, vad, sample_rate)
        buffer.append((i, is_speech))

        if not triggered:
            num_voiced = sum(1 for _, speech in buffer if speech)

            if num_voiced > 0.8 * buffer.maxlen:
                triggered = True
                start = buffer[0][0] * frame_time

        else:
            num_unvoiced = sum(1 for _, speech in buffer if not speech)

            if num_unvoiced > 0.8 * buffer.maxlen:
                end = i * frame_time
                segments.append((start, end))
                triggered = False

    return segments

def read_wave(path, sample_rate):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == sample_rate
        pcm_data = wf.readframes(wf.getnframes())
        duration = wf.getnframes() / sample_rate
        return pcm_data, duration

def frame_generator(audio, sample_rate, frame_duration, bytes_per_sample):
    frame_size = int(sample_rate * frame_duration / 1000) * bytes_per_sample
    offset = 0
    while offset + frame_size <= len(audio):
        yield audio[offset:offset + frame_size]
        offset += frame_size

def extract_audio(video_file, audio_file):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_file,
        "-vn",
        "-acodec", "mp3",
        audio_file
    ]
    subprocess.run(cmd)

def calculate_actual_timestamps(subtitle):
    actual_timestamps = subtitle["offsets"]
    actual_from = actual_timestamps["from"]
    actual_to = actual_timestamps["to"]
    return actual_from, actual_to

def calculate_next_timestamps(subtitle):
    next_timestamps = subtitle["offsets"]
    next_from = next_timestamps["from"]
    next_to = next_timestamps["to"]
    return next_from, next_to
    
async def build_audio(subtitles, output, voice_f):
    final_audio = AudioSegment.silent(duration=0)
    for i, sub in enumerate(subtitles):
        actual_from = actual_to = next_from = 0
        actual_from, actual_to = calculate_actual_timestamps(sub)
        if (i < len(subtitles) - 1):
            next_from, next_to = calculate_next_timestamps(subtitles[i+1])
        
        if str(sub["text"]).startswith("- "):
            if next_from != 0:
                final_audio += AudioSegment.silent(duration=next_from - actual_from)
        else:
            voice_file = f"{voice_f}{i}.mp3"
            
            text_pt = sub["text"]
            print(f"Narrando: {text_pt}")
            if i == 0:
                final_audio += AudioSegment.silent(duration=actual_from)
            voice = await save_chunk(text_pt, voice_file)
            
            silent_chunks = detect_silence(
                voice,
                min_silence_len=500,
                silence_thresh=-100000
            )
            voice_len = len(voice)
            print(f"Len voice 1: {voice_len}")
            voice = voice[0:silent_chunks[-1][0]]
            print(f"silent_chunks[-1][0]: {silent_chunks[-1][0]}")
            voice_len = len(voice)
            print(f"Len voice 2: {voice_len}")
            if i < len(subtitles) - 1:
                espaco_legenda = next_from - actual_from
            else:
                espaco_legenda = actual_to - actual_from
            diff_espaco_legenda = espaco_legenda - voice_len
            if diff_espaco_legenda < 0:
                speed = voice_len / espaco_legenda
                print(f"sem espaço, speed: {speed}")
                if (speed > 1.05 and speed < 1.5):
                    voice = speedup(voice, playback_speed=speed)
                    voice_len = len(voice)
                    if i < len(subtitles) - 1:
                        espaco_legenda = next_from - actual_from
                    else:
                        espaco_legenda = actual_to - actual_from
                    diff_espaco_legenda = espaco_legenda - voice_len
            silence = AudioSegment.silent(duration=diff_espaco_legenda)
            print(f"Silencio: {len(silence)}")
            final_audio += voice + silence
    final_audio.export(output, format="wav")
    filesys.limpar_temp_folder()

async def verify_audio(subtitles, chunk_f):
    ret = True
    for i, sub in enumerate(subtitles):
        
        timestamps = sub["timestamps"]
        text_pt = sub["text"]

        chunk_file = f"{chunk_f}{i}.mp3"

        target_duration = 0
        if i + 1 < len(subtitles):
            next_timestamp = subtitles[i + 1]["timestamps"]
            target_duration = utilLib.srt_time_to_ms(next_timestamp["from"]) - utilLib.srt_time_to_ms(timestamps["from"])
        else:
            target_duration = utilLib.srt_time_to_ms(timestamps["to"]) - utilLib.srt_time_to_ms(timestamps["from"])

        if target_duration <= 0:
            target_duration = 1 # Define 1ms como mínimo para evitar erro matemático
        
        chunk = await save_chunk(text_pt, chunk_file)
        speed = len(chunk) / target_duration
        if speed > 2.5:
            print(f"Segmento {i+1}: texto='{text_pt}' | duração alvo={target_duration}ms | duração voz={len(chunk)}ms | velocidade de ajuste necessária: {speed:.2f}x")
            ret = False
        remove_chunks(chunk_file, "")
    return ret

async def save_chunk(chunk, voice_file):
    await generate_tts(chunk, voice_file)
    return AudioSegment.from_mp3(voice_file)

def adjust_chunk(speed, input_file, adjusted_file):
    voice = AudioSegment.from_mp3(input_file)
    if speed > 1.0: 
        adjust_speed(input_file, adjusted_file, speed)
        voice = AudioSegment.from_mp3(adjusted_file)
        #print(f"speed adjusted: {speed} | len(voice): {len(voice)}\n")
    else:
        pass
        #print("Não precisou de ajuste de speed...\n")
    return voice

async def generate_tts(text, filename):
    communicate = edge_tts.Communicate(text=text, voice="pt-BR-AntonioNeural")
    await communicate.save(filename)

def adjust_speed(input_file, output_file, speed):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-filter:a", f"atempo={speed}",
        output_file
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def remove_chunks(voice_file, adjusted_file):
    if filesys.file_exists(voice_file):
        filesys.remove_file(voice_file)
    if filesys.file_exists(adjusted_file):
        filesys.remove_file(adjusted_file)

def get_audio_part(audio_file, start, end, file_out):
    audio = AudioSegment.from_file(audio_file)
    cut_segment = audio[start:end]
    cut_segment = cut_segment.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    cut_segment.export(file_out, format="wav")
