# -*- coding: utf-8 -*-
"""
PC client contract tests.

These tests keep the desktop client aligned with the secured FastAPI backend
without launching a Tkinter window.
"""

from pathlib import Path
import inspect
import sys


PC_CLIENT_SOURCE = Path(__file__).resolve().parents[2] / "pc_client" / "pc_desktop_client.py"
sys.path.insert(0, str(PC_CLIENT_SOURCE.parent))

from pc_desktop_client import PCDesktopClient


def _source() -> str:
    """Return the PC desktop client source as UTF-8 text."""
    return PC_CLIENT_SOURCE.read_text(encoding="utf-8")


def test_pc_client_uses_health_endpoint_for_status_check():
    """The status poller must call /health, not the API v1 root."""
    source = _source()
    assert 'f"{self.backend_base_url}/health"' in source
    assert "urllib.request.urlopen(self.backend_url" not in source


def test_pc_client_sends_api_key_for_rag_reindex():
    """The secured /workspace/index endpoint requires X-API-Key."""
    source = _source()
    assert 'extra_headers={"X-API-Key": self.api_key}' in source
    assert "MYBIZCON_API_KEY" in source


def test_pc_client_records_inside_safe_recordings_root():
    """Meeting recordings must be saved under SAFE_RECORDINGS_ROOT/recordings."""
    source = _source()
    assert "SAFE_RECORDINGS_ROOT" in source
    assert "os.makedirs(self.recordings_dir, exist_ok=True)" in source
    assert 'os.path.join(self.recordings_dir, "meeting_capture.wav")' in source


def test_pc_client_exposes_hinoter_note_capture_contract():
    """Desktop client should post current transcript/message content to notes capture."""
    source = _source()
    assert "capture_current_note" in source
    assert "_post_note_capture_to_api" in source
    assert 'f"{self.backend_url}/notes/capture"' in source
    assert '"source_type": "pc_client"' in source
    assert "_current_note_transcript" in source
    assert "threading.Thread(target=self._post_note_capture_to_api" in source
    assert "urllib.request.urlopen(req, timeout=10.0)" in source


class _FakeText:
    def __init__(self, value: str):
        self.value = value

    def get(self, *_args):
        return self.value


def test_pc_client_note_capture_uses_last_meeting_transcript_state_without_display_marker():
    client = object.__new__(PCDesktopClient)
    client.last_meeting_transcript = "Speaker A: 회의록을 작성해서 오늘 등록해주세요."
    client.message_txt = _FakeText("현재 메시지는 별도 입력입니다.")

    assert client._current_note_transcript() == "Speaker A: 회의록을 작성해서 오늘 등록해주세요."


def test_pc_client_note_capture_falls_back_to_current_message_when_no_meeting_transcript():
    client = object.__new__(PCDesktopClient)
    client.last_meeting_transcript = ""
    client.message_txt = _FakeText("현재 메시지 내용을 캡처합니다.")

    assert client._current_note_transcript() == "현재 메시지 내용을 캡처합니다."


def test_pc_client_note_capture_no_longer_depends_on_full_transcript_display_text():
    method_source = inspect.getsource(PCDesktopClient._current_note_transcript)

    assert "Full Transcript:" not in method_source
    assert "copilot_txt" not in method_source
    assert "last_meeting_transcript" in method_source
