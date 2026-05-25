# -*- coding: utf-8 -*-
"""Contract tests for HiNoter-style AI note taking features."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi.testclient import TestClient
from backend.app.main import app


def test_hinoter_note_capture_contract_returns_summary_mind_map_and_searchable_moments():
    with TestClient(app, raise_server_exceptions=True) as client:
        response = client.post(
            "/api/v1/notes/capture",
            json={
                "title": "바이어 주간 회의",
                "source_type": "recording",
                "source_uri": "recordings/buyer_weekly.wav",
                "transcript": "김대표: 다음 주 월요일 견적서를 보내주세요.\n박과장: 네, 월요일 오전까지 공유하겠습니다.\n김대표: 예산은 5% 인상 기준으로 검토하겠습니다.",
                "speaker_labels": ["김대표", "박과장"],
                "calendar_event_id": "cal-123",
                "ask": "핵심 액션아이템은?",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["source_type"] == "recording"
    assert data["encrypted"] is True
    assert "summary" in data and data["summary"]
    assert "mind_map" in data and data["mind_map"]["root"] == "바이어 주간 회의"
    assert data["mind_map"]["branches"]
    assert any(item["speaker"] == "김대표" for item in data["speaker_sections"])
    assert any("월요일" in item["text"] for item in data["searchable_moments"])
    assert "answer" in data["ask_ai"] and data["ask_ai"]["answer"]
    assert data["share_payload"]["permissions"] == "owner-controlled"


def test_hinoter_note_capture_contract_accepts_youtube_and_calendar_auto_join_metadata():
    with TestClient(app, raise_server_exceptions=True) as client:
        response = client.post(
            "/api/v1/notes/capture",
            json={
                "title": "제품 데모 녹취",
                "source_type": "youtube",
                "source_uri": "https://youtube.com/watch?v=demo",
                "transcript": "Speaker A: 신규 기능 데모를 시작합니다. Speaker B: 공유 링크를 보내주세요.",
                "speaker_labels": ["Speaker A", "Speaker B"],
                "auto_join_calendar": True,
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["source_type"] == "youtube"
    assert data["calendar_auto_join"] is True
    assert "calendar_auto_join" in data["feature_flags"]
    assert "youtube_or_audio_upload" in data["feature_flags"]
