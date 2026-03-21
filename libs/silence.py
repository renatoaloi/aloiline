import collections
import audioop

# =========================
# CONFIGURAÇÃO
# =========================
SAMPLE_RATE = 16000
FRAME_DURATION = 30  # ms
BYTES_PER_SAMPLE = 2

VAD_MODE = 3
PADDING_FRAMES = 6
MAX_GAP = 0.25
MIN_DURATION = 0.1
#RMS_THRESHOLD = 900

class SilenceTrackDetector:
    def __init__(self, sample_rate, frame_duration, padding_frames, \
                 bytes_per_sample, vad_mode, max_gap, min_duration):
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.padding_frames = padding_frames
        self.bytes_per_sample = bytes_per_sample
        self.vad_mode = vad_mode
        self.max_gap = max_gap
        self.min_duration = min_duration

    def _is_valid_speech(self, frame, vad):
        rms = audioop.rms(frame, 2)
        if rms < 900:
            return False
        return vad.is_speech(frame, SAMPLE_RATE)

    def vad_collector(self, vad, frames):
        segments = []
        triggered = False
        start = 0
        frame_time = FRAME_DURATION / 1000
        buffer = collections.deque(maxlen=PADDING_FRAMES)
        for i, frame in enumerate(frames):
            is_speech = self._is_valid_speech(frame, vad)
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


driver = SilenceTrackDetector(SAMPLE_RATE, FRAME_DURATION, PADDING_FRAMES, \
                              BYTES_PER_SAMPLE, VAD_MODE, MAX_GAP, \
                                MIN_DURATION)





























#     def _prepare_audio(self, input_file):
#         """Converte qualquer áudio para WAV 16kHz Mono (o padrão do whisper.cpp)"""
#         base_name = os.path.basename(input_file)
#         temp_wav = f"temp_{base_name}.wav"
        
#         # Carrega o áudio (MP3, WAV, etc)
#         audio = AudioSegment.from_file(input_file)
        
#         # Converte para os parâmetros exigidos pela GPU
#         audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
#         audio.export(temp_wav, format="wav")
        
#         return temp_wav

#     def read_wave(self, path):
#         """Reads a .wav file.

#         Takes the path, and returns (PCM audio data, sample rate).
#         """
#         path = self._prepare_audio(path)
#         with contextlib.closing(wave.open(path, 'rb')) as wf:
#             num_channels = wf.getnchannels()
#             assert num_channels == 1
#             sample_width = wf.getsampwidth()
#             assert sample_width == 2
#             sample_rate = wf.getframerate()
#             assert sample_rate in (8000, 16000, 32000, 48000)
#             pcm_data = wf.readframes(wf.getnframes())
#             return pcm_data, sample_rate


#     def write_wave(self, path, audio, sample_rate):
#         """Writes a .wav file.

#         Takes path, PCM audio data, and sample rate.
#         """
#         with contextlib.closing(wave.open(path, 'wb')) as wf:
#             wf.setnchannels(1)
#             wf.setsampwidth(2)
#             wf.setframerate(sample_rate)
#             wf.writeframes(audio)


# class Frame(object):
#     """Represents a "frame" of audio data."""
#     def __init__(self, bytes, timestamp, duration):
#         self.bytes = bytes
#         self.timestamp = timestamp
#         self.duration = duration


#     def frame_generator(frame_duration_ms, audio, sample_rate):
#         """Generates audio frames from PCM audio data.

#         Takes the desired frame duration in milliseconds, the PCM data, and
#         the sample rate.

#         Yields Frames of the requested duration.
#         """
#         n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
#         offset = 0
#         timestamp = 0.0
#         duration = (float(n) / sample_rate) / 2.0
#         while offset + n < len(audio):
#             yield Frame(audio[offset:offset + n], timestamp, duration)
#             timestamp += duration
#             offset += n


#     def vad_collector(sample_rate, frame_duration_ms,
#                     padding_duration_ms, vad, frames):
#         """Filters out non-voiced audio frames.

#         Given a webrtcvad.Vad and a source of audio frames, yields only
#         the voiced audio.

#         Uses a padded, sliding window algorithm over the audio frames.
#         When more than 90% of the frames in the window are voiced (as
#         reported by the VAD), the collector triggers and begins yielding
#         audio frames. Then the collector waits until 90% of the frames in
#         the window are unvoiced to detrigger.

#         The window is padded at the front and back to provide a small
#         amount of silence or the beginnings/endings of speech around the
#         voiced frames.

#         Arguments:

#         sample_rate - The audio sample rate, in Hz.
#         frame_duration_ms - The frame duration in milliseconds.
#         padding_duration_ms - The amount to pad the window, in milliseconds.
#         vad - An instance of webrtcvad.Vad.
#         frames - a source of audio frames (sequence or generator).

#         Returns: A generator that yields PCM audio data.
#         """
#         num_padding_frames = int(padding_duration_ms / frame_duration_ms)
#         # We use a deque for our sliding window/ring buffer.
#         ring_buffer = collections.deque(maxlen=num_padding_frames)
#         # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
#         # NOTTRIGGERED state.
#         triggered = False

#         voiced_frames = []
#         for frame in frames:
#             is_speech = vad.is_speech(frame.bytes, sample_rate)

#             sys.stdout.write('1' if is_speech else '0')
#             if not triggered:
#                 ring_buffer.append((frame, is_speech))
#                 num_voiced = len([f for f, speech in ring_buffer if speech])
#                 # If we're NOTTRIGGERED and more than 90% of the frames in
#                 # the ring buffer are voiced frames, then enter the
#                 # TRIGGERED state.
#                 if num_voiced > 0.9 * ring_buffer.maxlen:
#                     triggered = True
#                     sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
#                     # We want to yield all the audio we see from now until
#                     # we are NOTTRIGGERED, but we have to start with the
#                     # audio that's already in the ring buffer.
#                     for f, s in ring_buffer:
#                         voiced_frames.append(f)
#                     ring_buffer.clear()
#             else:
#                 # We're in the TRIGGERED state, so collect the audio data
#                 # and add it to the ring buffer.
#                 voiced_frames.append(frame)
#                 ring_buffer.append((frame, is_speech))
#                 num_unvoiced = len([f for f, speech in ring_buffer if not speech])
#                 # If more than 90% of the frames in the ring buffer are
#                 # unvoiced, then enter NOTTRIGGERED and yield whatever
#                 # audio we've collected.
#                 if num_unvoiced > 0.9 * ring_buffer.maxlen:
#                     sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
#                     triggered = False
#                     yield b''.join([f.bytes for f in voiced_frames])
#                     ring_buffer.clear()
#                     voiced_frames = []
#         if triggered:
#             sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
#         sys.stdout.write('\n')
#         # If we have any leftover voiced audio when we run out of input,
#         # yield it.
#         if voiced_frames:
#             yield b''.join([f.bytes for f in voiced_frames])
