# -*- coding: utf-8 -*-
"""
Contract tests for MYBIZCON_DISABLE_EXTERNAL_SERVICES.

When the flag is set to 1/true/yes, live Gemini, OpenAI, ElevenLabs, and
Workspace sync paths must be bypassed even if API keys are present.
"""

import os
import sys
from unittest.mock import patch

import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.mark.parametrize("flag_value", ["1", "true", "yes"])
@pytest.mark.asyncio
async def test_relationship_engine_disable_flag_bypasses_gemini(flag_value, monkeypatch):
    from app.config import settings
    from app.services.relationship_engine import RelationshipEngineService

    monkeypatch.setenv("MYBIZCON_DISABLE_EXTERNAL_SERVICES", flag_value)
    settings.GEMINI_API_KEY = "live-key-that-must-not-be-used"

    with patch("app.services.relationship_engine.httpx.AsyncClient") as async_client:
        result = await RelationshipEngineService().generate_replies(
            sender="Client",
            content="Please send the revised proposal.",
            relationship="CLIENT",
            is_group=False,
            platform="WHATSAPP",
        )

    async_client.assert_not_called()
    assert result["translation"]
    assert result["suggestions"]


@pytest.mark.asyncio
async def test_voice_service_disable_flag_bypasses_openai_and_elevenlabs(tmp_path, monkeypatch):
    from app.services.voice_service import VoiceService

    monkeypatch.setenv("MYBIZCON_DISABLE_EXTERNAL_SERVICES", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "live-openai-key-that-must-not-be-used")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "live-elevenlabs-key-that-must-not-be-used")
    wav_path = tmp_path / "sample.wav"
    wav_path.write_bytes(b"RIFFmock")

    service = VoiceService()
    service.openai_key = "live-openai-key-that-must-not-be-used"
    service.elevenlabs_key = "live-elevenlabs-key-that-must-not-be-used"

    with patch("app.services.voice_service.httpx.AsyncClient") as async_client:
        transcript = await service.transcribe_audio(str(wav_path))
        audio = await service.synthesize_voice("hello")

    async_client.assert_not_called()
    assert transcript
    assert audio.startswith(b"RIFF")


@pytest.mark.asyncio
async def test_diarization_disable_flag_bypasses_gemini_and_uses_workspace_mock(tmp_path, monkeypatch):
    from app.config import settings
    from app.services.diarization_engine import DiarizationEngineService

    monkeypatch.setenv("MYBIZCON_DISABLE_EXTERNAL_SERVICES", "yes")
    settings.GEMINI_API_KEY = "live-gemini-key-that-must-not-be-used"
    wav_path = tmp_path / "meeting.wav"
    wav_path.write_bytes(b"RIFFmock")

    with patch("app.services.diarization_engine.httpx.AsyncClient") as async_client:
        result = await DiarizationEngineService().process_audio_meeting(str(wav_path))

    async_client.assert_not_called()
    assert result["transcript_markdown"]
    assert result["tasks"]
    assert result["schedules"]


def test_workspace_disable_flag_returns_offline_mocks(monkeypatch):
    from app.services.google_workspace import GoogleWorkspaceService

    monkeypatch.setenv("MYBIZCON_DISABLE_EXTERNAL_SERVICES", "1")
    service = GoogleWorkspaceService()

    calendar = service.sync_calendar_event("Review", "desc", "2026-05-26T10:00:00", "2026-05-26T11:00:00")
    task = service.sync_task("Follow up", "notes", "2026-05-26")
    drive = service.backup_to_drive("Chat", "Transcript")

    assert calendar["status"] == "MOCK"
    assert task["status"] == "MOCK"
    assert drive["status"] == "MOCK"
    assert calendar["offline"] is True
    assert task["offline"] is True
    assert drive["offline"] is True
