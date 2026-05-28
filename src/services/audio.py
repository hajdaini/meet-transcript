import threading
import time
import wave
from pathlib import Path

import numpy as np


class AudioDeviceStatus:
    def __init__(self, microphone_available, system_audio_available, microphone_name="", system_name=""):
        self.microphone_available = microphone_available
        self.system_audio_available = system_audio_available
        self.microphone_name = microphone_name
        self.system_name = system_name


class AudioRecorder:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.frames = []
        self.running = False
        self.thread = None
        self.started_at = None
        self.output_path = None
        self.last_level = 0.0
        self.microphone = ""
        self.system_output = ""

    def list_microphones(self):
        try:
            import sounddevice as sd

            devices = sd.query_devices()
            return [device["name"] for device in devices if device.get("max_input_channels", 0) > 0]
        except Exception:
            return []

    def list_system_outputs(self):
        try:
            import soundcard as sc

            return [speaker.name for speaker in sc.all_speakers()]
        except Exception:
            return []

    def detect_devices(self):
        microphone_available = False
        system_audio_available = False
        microphone_name = ""
        system_name = ""
        try:
            import sounddevice as sd

            device = self.selected_microphone_device(sd)
            microphone_available = bool(device)
            microphone_name = device.get("name", "") if isinstance(device, dict) else ""
        except Exception:
            microphone_available = False
        try:
            import soundcard as sc

            speaker = self.selected_speaker(sc)
            system_audio_available = speaker is not None
            system_name = speaker.name if speaker else ""
        except Exception:
            system_audio_available = False
        return AudioDeviceStatus(microphone_available, system_audio_available, microphone_name, system_name)

    def start(self, output_path: Path, settings=None):
        settings = settings or {}
        self.microphone = settings.get("microphone", "")
        self.system_output = settings.get("system_output", "")
        status = self.detect_devices()
        if not status.microphone_available:
            raise RuntimeError("Aucun micro detecte.")
        self.output_path = Path(output_path)
        self.frames = []
        self.running = True
        self.started_at = time.time()
        self.thread = threading.Thread(target=self.record_loop, daemon=True)
        self.thread.start()
        return status

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=3)
        duration = int(time.time() - self.started_at) if self.started_at else 0
        self.write_wav(self.output_path)
        return self.output_path, duration

    def record_loop(self):
        try:
            self.record_micro_and_system()
        except Exception:
            self.record_micro_only()

    def record_micro_and_system(self):
        import soundcard as sc
        import sounddevice as sd

        speaker = self.selected_speaker(sc)
        mic_frames = []

        def callback(indata, frames, time_info, status):
            mic_frames.append(indata.copy())

        with sd.InputStream(device=self.selected_microphone_index(sd), samplerate=self.sample_rate, channels=self.channels, callback=callback):
            with sc.get_microphone(id=str(speaker.name), include_loopback=True).recorder(samplerate=self.sample_rate, channels=self.channels) as recorder:
                while self.running:
                    system_chunk = recorder.record(numframes=1024)
                    mic_chunk = mic_frames.pop(0) if mic_frames else np.zeros_like(system_chunk)
                    chunk = self.normalize_shape(mic_chunk, system_chunk)
                    self.frames.append(chunk)
                    self.last_level = self.audio_level(chunk)

    def record_micro_only(self):
        import sounddevice as sd

        def callback(indata, frames, time_info, status):
            chunk = indata.copy()
            self.frames.append(chunk)
            self.last_level = self.audio_level(chunk)

        with sd.InputStream(device=self.selected_microphone_index(sd), samplerate=self.sample_rate, channels=self.channels, callback=callback):
            while self.running:
                time.sleep(0.05)

    def selected_microphone_device(self, sd):
        if not self.microphone:
            return sd.query_devices(kind="input")
        devices = sd.query_devices()
        for device in devices:
            if device.get("name") == self.microphone and device.get("max_input_channels", 0) > 0:
                return device
        return None

    def selected_microphone_index(self, sd):
        if not self.microphone:
            return None
        devices = sd.query_devices()
        for index, device in enumerate(devices):
            if device.get("name") == self.microphone and device.get("max_input_channels", 0) > 0:
                return index
        return None

    def selected_speaker(self, sc):
        if not self.system_output:
            return sc.default_speaker()
        for speaker in sc.all_speakers():
            if speaker.name == self.system_output:
                return speaker
        return sc.default_speaker()

    def normalize_shape(self, mic_chunk, system_chunk):
        mic_chunk = np.asarray(mic_chunk, dtype=np.float32)
        system_chunk = np.asarray(system_chunk, dtype=np.float32)
        size = min(len(mic_chunk), len(system_chunk))
        if size <= 0:
            return system_chunk
        mixed = (mic_chunk[:size] + system_chunk[:size]) * 0.5
        return np.clip(mixed, -1, 1)

    def audio_level(self, chunk):
        data = np.asarray(chunk, dtype=np.float32)
        rms = float(np.sqrt(np.mean(np.square(data)))) if data.size else 0.0
        return float(np.clip(rms * 9.0, 0, 1))

    def write_wav(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        if self.frames:
            data = np.concatenate(self.frames, axis=0)
        else:
            data = np.zeros((1, self.channels), dtype=np.float32)
        data = np.clip(data, -1, 1)
        pcm = (data * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(self.channels)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            wav.writeframes(pcm.tobytes())
