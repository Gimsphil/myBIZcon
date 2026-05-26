# -*- coding: utf-8 -*-
"""WAconn frontend compatibility contract tests.

These tests cover the local offline-safe API shape expected by the reference
WAconn frontend server.ts endpoints. They must remain deterministic when
MYBIZCON_DISABLE_EXTERNAL_SERVICES=1 is set.
"""

import os
import sys
from unittest.mock import patch


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["MYBIZCON_DISABLE_EXTERNAL_SERVICES"] = "1"
os.environ["GEMINI_API_KEY"] = "live-key-that-must-not-be-used"
os.environ["SECRET_API_KEY"] = "test-api-key-codex-step16"

from fastapi.testclient import TestClient
from backend.app.main import app


def test_waconn_generate_reply_contract_uses_offline_relationship_mock():
    with patch("app.services.relationship_engine.httpx.AsyncClient") as async_client:
        with TestClient(app, raise_server_exceptions=True) as client:
            response = client.post(
                "/api/generate-reply",
                json={
                    "message": "Please send the revised proposal by Friday.",
                    "persona": "CLIENT",
                    "channel": "Slack",
                },
            )

    async_client.assert_not_called()
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"draftOriginal", "draftTranslated", "mode"}
    assert data["draftOriginal"]
    assert data["draftTranslated"]
    assert data["mode"] == "simulation"


def test_waconn_meeting_summary_contract_returns_markdown_and_mode():
    with TestClient(app, raise_server_exceptions=True) as client:
        response = client.post(
            "/api/meeting-summary",
            json={
                "transcript": [
                    {
                        "speaker": "Alex",
                        "text": "We decided to approve the budget increase.",
                    },
                    {
                        "speaker": "User",
                        "text": "I will prepare the contract and send it today.",
                    },
                ]
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"markdown", "mode"}
    assert data["mode"] == "simulation"
    assert "# Executive Summary" in data["markdown"]
    assert "# Decisions Made" in data["markdown"]
    assert "# Auto-Extracted Action Items" in data["markdown"]
    assert "budget increase" in data["markdown"]


def test_waconn_ask_notes_contract_returns_answer_and_mode():
    with TestClient(app, raise_server_exceptions=True) as client:
        response = client.post(
            "/api/ask-notes",
            json={
                "transcript": [
                    {
                        "speaker": "Alex",
                        "text": "We decided to approve the budget increase.",
                    },
                    {
                        "speaker": "User",
                        "text": "I will prepare the contract and send it today.",
                    },
                ],
                "question": "What action items were mentioned?",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"answer", "mode"}
    assert data["mode"] == "simulation"
    assert "prepare the contract" in data["answer"]


def test_waconn_contract_rejects_invalid_payloads():
    with TestClient(app, raise_server_exceptions=True) as client:
        reply_response = client.post(
            "/api/generate-reply",
            json={"message": "Missing persona"},
        )
        summary_response = client.post(
            "/api/meeting-summary",
            json={"transcript": "not-a-list"},
        )
        ask_response = client.post(
            "/api/ask-notes",
            json={"transcript": [], "question": ""},
        )

    assert reply_response.status_code == 400
    assert summary_response.status_code == 400
    assert ask_response.status_code == 400
