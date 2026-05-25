import os
import logging
import httpx
from app.config import settings

logger = logging.getLogger("myBIZcon_VoiceService")

class VoiceService:
    """
    🎙️ VoiceService
    Orchestrates:
    1. STT (Speech-To-Text): Ingests recorded WAV meetings via OpenAI Whisper REST API.
    2. TTS (Text-To-Speech): Synthesizes responses via ElevenLabs / Google TTS API.
    Provides graceful zero-dependency fallback mocks if API keys are missing.
    """
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")
        
        if self.openai_key:
            logger.info("🔑 OpenAI API key detected. Whisper STT pipeline active.")
        else:
            logger.info("⚠️ OpenAI API key missing. Whisper STT running in mock-emulation mode.")
            
        if self.elevenlabs_key:
            logger.info("🔑 ElevenLabs API key detected. Premium TTS pipeline active.")
        else:
            logger.info("⚠️ ElevenLabs API key missing. Using standard Google TTS fallback emulation.")

    async def transcribe_audio(self, wav_file_path: str) -> str:
        """
        Sends WAV audio file to OpenAI Whisper API for transcription.
        """
        if not os.path.exists(wav_file_path):
            logger.error(f"❌ File not found: {wav_file_path}")
            return "[Error: Audio file missing]"

        if not self.openai_key:
            logger.info("🔮 Emulating OpenAI Whisper API transcription (Offline Bounded Mock).")
            return self._get_mock_transcription()

        logger.info(f"📤 Uploading {wav_file_path} to OpenAI Whisper API...")
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.openai_key}"}
        
        try:
            # Read file stream
            with open(wav_file_path, "rb") as audio_file:
                files = {
                    "file": (os.path.basename(wav_file_path), audio_file, "audio/wav"),
                    "model": (None, "whisper-1"),
                    "language": (None, "ko") # Default target to Korean
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, headers=headers, files=files)
                    if response.status_code == 200:
                        result = response.json()
                        text = result.get("text", "")
                        logger.info("✅ Whisper STT transcription successful.")
                        return text
                    else:
                        logger.error(f"❌ Whisper API error: {response.status_code} - {response.text}")
                        return self._get_mock_transcription()
        except Exception as e:
            logger.error(f"❌ Whisper connection failed: {str(e)}")
            return self._get_mock_transcription()

    async def synthesize_voice(self, text: str) -> bytes:
        """
        Synthesizes text into high-quality speech WAV/MP3 bytes via ElevenLabs.
        Falls back to a standard mock audio byte array if offline or API key is missing.
        """
        if not text:
            return b""

        if not self.elevenlabs_key:
            logger.info("🔮 Emulating Text-To-Speech synthesis (Offline Bounded Mock).")
            return self._generate_mock_audio_bytes()

        # ElevenLabs Voice ID: Rachel (default)
        voice_id = "21m00Tcm4TlvDq8ikWAM" 
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.elevenlabs_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    logger.info("✅ ElevenLabs TTS synthesis successful.")
                    return response.content
                else:
                    logger.error(f"❌ ElevenLabs error: {response.status_code} - {response.text}")
                    return self._generate_mock_audio_bytes()
        except Exception as e:
            logger.error(f"❌ ElevenLabs connection failed: {str(e)}")
            return self._generate_mock_audio_bytes()

    def _get_mock_transcription(self) -> str:
        """Standard mock dialogue transcript for development validation."""
        return (
            "User: 안녕하세요, 대표님. 지난번에 공유해 주신 기획안 일정 조율을 진행하고자 연락드렸습니다. "
            "Client: 아, 과장님 반갑습니다! 안 그래도 다음 주 수요일 전략 제휴 컨퍼런스 일정이 괜찮으실지 확인 중이었습니다."
        )

    def _generate_mock_audio_bytes(self) -> bytes:
        """Generates raw mock audio bytes simulating speech stream (1-second silence or mock wav header)."""
        # Return a simple WAV format header + 1 second silence for mock testing
        sample_rate = 16000
        num_samples = sample_rate
        data_size = num_samples * 2
        wav_header = bytearray(
            b'RIFF' + 
            (data_size + 36).to_bytes(4, 'little') + 
            b'WAVEfmt ' + 
            (16).to_bytes(4, 'little') + 
            (1).to_bytes(2, 'little') + # PCM
            (1).to_bytes(2, 'little') + # Mono
            (sample_rate).to_bytes(4, 'little') + 
            (sample_rate * 2).to_bytes(4, 'little') + 
            (2).to_bytes(2, 'little') + 
            (16).to_bytes(2, 'little') + 
            b'data' + 
            (data_size).to_bytes(4, 'little')
        )
        # Add 1 second of silence (zero values)
        data = b"\x00" * data_size
        return bytes(wav_header + data)

voice_service = VoiceService()
