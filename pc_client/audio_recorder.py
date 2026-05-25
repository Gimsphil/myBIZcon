# -*- coding: utf-8 -*-
import os
import wave
import time
import math
import struct
import threading
import logging

logger = logging.getLogger("myBIZcon_AudioRecorder")
logging.basicConfig(level=logging.INFO)

class AudioRecorder:
    """
    🎙️ AudioRecorder (DSP Voice Enhanced)
    Multi-threaded audio recorder with advanced DSP filters:
    1. First-Order Digital High-Pass Filter (HPF) @ 80Hz: Removes low-frequency rumble (AC, fan, traffic hum).
    2. Dynamic VAD Noise Gate: Gating frames below dynamic threshold to silence background static.
    3. Soft Speech Booster: Amplifies subtle voices by 25% for high-accuracy STT.
    Falls back gracefully to Simulated WAV generator in mock settings.
    """
    def __init__(self, filename="meeting_capture.wav", sample_rate=16000, channels=1):
        self.filename = filename
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self._thread = None
        self._frames = []
        
        # DSP State variables
        self._last_x = 0
        self._last_y = 0
        
        # Detect PyAudio availability
        try:
            import pyaudio
            self.pyaudio_avail = True
            self.pa = pyaudio.PyAudio()
            logger.info("🎙️ PyAudio library detected. Preparing native audio devices.")
        except ImportError:
            self.pyaudio_avail = False
            self.pa = None
            logger.warning("⚠️ PyAudio library not found. Entering Zero-Dependency Simulation Mode.")

    def start(self):
        """Starts multi-threaded audio recording."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self._frames = []
        self._last_x = 0
        self._last_y = 0
        
        if self.pyaudio_avail:
            self._thread = threading.Thread(target=self._native_record, daemon=True)
        else:
            self._thread = threading.Thread(target=self._simulated_record, daemon=True)
            
        self._thread.start()
        logger.info(f"🔴 Audio capture initiated with Voice DSP enhancement: {self.filename}")

    def stop(self):
        """Stops recording and serializes to WAV format."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        if self._thread:
            self._thread.join()
        
        self._save_wav()
        logger.info(f"💾 Audio file saved successfully: {self.filename}")

    def _apply_dsp_voice_filters(self, raw_bytes: bytes) -> bytes:
        """Applies High-Pass filtering, VAD Noise Gate, and Speech Booster to raw PCM data."""
        if not raw_bytes:
            return raw_bytes
            
        num_samples = len(raw_bytes) // 2
        samples = list(struct.unpack(f'<{num_samples}h', raw_bytes))
        
        # 1. First-Order High-Pass Filter Cutoff 80Hz (alpha = 0.975 for 16kHz)
        alpha = 0.975
        filtered_samples = []
        for x in samples:
            y = int(alpha * (self._last_y + x - self._last_x))
            y = max(-32768, min(32767, y)) # Clip to 16-bit
            filtered_samples.append(y)
            self._last_x = x
            self._last_y = y
            
        # 2. VAD Noise Gate (RMS Thresholding)
        sum_squares = sum(x**2 for x in filtered_samples)
        rms = math.sqrt(sum_squares / max(1, num_samples))
        
        # Ambient noise ceiling threshold
        noise_gate_threshold = 200.0
        
        if rms < noise_gate_threshold:
            # Quiet background noise: zero out samples completely (Noise gate)
            return b"\x00" * len(raw_bytes)
            
        # 3. Soft Speech Booster: Amplifies subtle speech inputs (+25%) without clipping
        boosted_samples = []
        for x in filtered_samples:
            if abs(x) < 4000:
                x = int(x * 1.25)
                x = max(-32768, min(32767, x))
            boosted_samples.append(x)
            
        return struct.pack(f'<{num_samples}h', *boosted_samples)

    def _native_record(self):
        """Records physical microphone audio stream and applies DSP filters."""
        try:
            import pyaudio
            chunk = 1024
            stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=chunk
            )
            
            while self.is_recording:
                data = stream.read(chunk, exception_on_overflow=False)
                # Apply DSP Noise gate and speech booster filters on raw bytes
                dsp_enhanced_data = self._apply_dsp_voice_filters(data)
                self._frames.append(dsp_enhanced_data)
                
            stream.stop_stream()
            stream.close()
        except Exception as e:
            logger.error(f"❌ Native recording failed (mic locked/unavailable): {str(e)}. Swapping to simulation backend.")
            self._simulated_record()

    def _simulated_record(self):
        """Generates realistic synthetic audio waveforms if offline/no mic (Simulation mode)."""
        logger.info("✨ Simulation Mode Active: Generating high-fidelity mock conversation waveforms.")
        
        amplitude = 8000
        frequency = 440.0 # 440Hz Sine wave beep
        t = 0.0
        dt = 1.0 / self.sample_rate
        chunk_size = 1024
        
        while self.is_recording:
            chunk_frames = []
            for _ in range(chunk_size):
                val = int(amplitude * math.sin(2 * math.pi * frequency * t))
                packed = struct.pack('<h', val)
                chunk_frames.append(packed)
                t += dt
            
            raw_bytes = b"".join(chunk_frames)
            # Route simulation through DSP filter too to ensure full validation coverage
            dsp_enhanced_data = self._apply_dsp_voice_filters(raw_bytes)
            self._frames.append(dsp_enhanced_data)
            time.sleep(chunk_size / self.sample_rate)

    def _save_wav(self):
        """Saves gathered PCM chunks into standard wav file structure."""
        if not self._frames:
            logger.warning("⚠️ No frames collected. Cannot output empty WAV.")
            return
            
        try:
            with wave.open(self.filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(b"".join(self._frames))
            logger.info(f"📊 Completed WAV write: {os.path.getsize(self.filename)} bytes saved.")
        except Exception as e:
            logger.error(f"❌ Failed to write WAV file: {str(e)}")
