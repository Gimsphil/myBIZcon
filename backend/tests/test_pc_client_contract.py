# -*- coding: utf-8 -*-
"""
PC client contract tests.

These tests keep the desktop client aligned with the secured FastAPI backend
without launching a Tkinter window.
"""

from pathlib import Path


PC_CLIENT_SOURCE = Path(__file__).resolve().parents[2] / "pc_client" / "pc_desktop_client.py"


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
