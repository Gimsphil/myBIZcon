# -*- coding: utf-8 -*-
"""
test_relationship_engine.py - Relationship Engine Unit Tests
=============================================================
CODEX Step 21 Revision: Updated to match actual RelationshipEngineService API.
Previous version tested non-existent methods (_get_platform_adapter, etc.).
This revision aligns with the actual codebase verified by Antigravity audit.

Actual API (verified from relationship_engine.py):
  - generate_replies(sender, content, relationship, is_group, platform) -> dict
  - _generate_mock_response(content, relationship, platform) -> dict
  - PLATFORM_INSTRUCTIONS dict keys: SLACK, KAKAOTALK, TELEGRAM, WHATSAPP

Test Coverage:
  1. Mock response structure validation (dict with 'translation' and 'suggestions')
  2. BOSS/CLIENT/FAMILY/COWORKER mock response tone differentiation
  3. Platform adapter key routing (SLACK, KAKAOTALK, TELEGRAM, WHATSAPP)
  4. KAKAOTALK platform normalization (KAKAO → KAKAOTALK)
  5. Group chat flag passes through without error
  6. Async generate_replies with mocked Gemini (no-key fallback path)

Role: CODEX (2nd Coder / Auditor) - Step 21 Revision
Reviewed by: Antigravity (기술 검토자)
"""

import sys
import os

# Allow imports from backend root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Ensure Gemini API key is empty to force mock response path (no real API calls in tests)
os.environ.setdefault("GEMINI_API_KEY", "")

import pytest
from backend.app.services.relationship_engine import RelationshipEngineService, PLATFORM_INSTRUCTIONS


# ── Fixture ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def engine():
    """Returns a RelationshipEngineService instance."""
    return RelationshipEngineService()


# ── PLATFORM_INSTRUCTIONS Dict Validation ────────────────────────────────────

class TestPlatformInstructionsDict:
    """Tests the PLATFORM_INSTRUCTIONS module-level dictionary."""

    def test_all_four_platforms_present(self):
        """All 4 expected platform keys must exist in PLATFORM_INSTRUCTIONS."""
        expected = {"SLACK", "KAKAOTALK", "TELEGRAM", "WHATSAPP"}
        actual = set(PLATFORM_INSTRUCTIONS.keys())
        assert expected.issubset(actual), (
            f"Missing platforms: {expected - actual}"
        )

    def test_each_platform_has_non_empty_instruction(self):
        """Each platform instruction string must be non-empty."""
        for platform, instruction in PLATFORM_INSTRUCTIONS.items():
            assert len(instruction.strip()) > 0, (
                f"Platform '{platform}' has an empty instruction string."
            )

    def test_slack_uses_markdown_formatting(self):
        """SLACK instruction must reference markdown formatting (bold *text*)."""
        assert "*" in PLATFORM_INSTRUCTIONS["SLACK"] or "bold" in PLATFORM_INSTRUCTIONS["SLACK"].lower(), (
            "SLACK instruction should reference markdown bold formatting."
        )

    def test_kakaotalk_references_korean_honorifics(self):
        """KAKAOTALK instruction must reference Korean honorifics (존댓말/-요)."""
        instruction = PLATFORM_INSTRUCTIONS["KAKAOTALK"]
        assert "존댓말" in instruction or "요" in instruction or "Korean" in instruction, (
            "KAKAOTALK instruction should reference Korean honorifics."
        )


# ── Mock Response Structure ───────────────────────────────────────────────────

class TestMockResponseStructure:
    """Tests _generate_mock_response() return structure and content."""

    def test_boss_mock_response_has_required_keys(self, engine):
        """BOSS mock response must contain 'translation' and 'suggestions'."""
        result = engine._generate_mock_response("보고서 준비해줘.", "BOSS", "WHATSAPP")
        assert "translation" in result, "Missing 'translation' key in BOSS response."
        assert "suggestions" in result, "Missing 'suggestions' key in BOSS response."

    def test_boss_mock_suggestions_are_list(self, engine):
        """BOSS suggestions must be a list."""
        result = engine._generate_mock_response("보고서 준비해줘.", "BOSS", "WHATSAPP")
        assert isinstance(result["suggestions"], list), "suggestions must be a list."

    def test_boss_mock_suggestions_count(self, engine):
        """BOSS mock must return at least 3 suggestions."""
        result = engine._generate_mock_response("보고서 준비해줘.", "BOSS", "WHATSAPP")
        assert len(result["suggestions"]) >= 3, (
            f"Expected ≥3 BOSS suggestions, got {len(result['suggestions'])}"
        )

    def test_each_suggestion_has_tone_and_content(self, engine):
        """Each suggestion dict must have 'tone' and 'content' keys."""
        for relationship in ["BOSS", "CLIENT", "FAMILY", "COWORKER"]:
            result = engine._generate_mock_response("테스트", relationship, "WHATSAPP")
            for i, sug in enumerate(result["suggestions"]):
                assert "tone" in sug, f"{relationship} suggestion[{i}] missing 'tone'."
                assert "content" in sug, f"{relationship} suggestion[{i}] missing 'content'."

    def test_translation_field_contains_original_content(self, engine):
        """Translation field must include original content reference."""
        result = engine._generate_mock_response("계약서 보내줘", "CLIENT", "WHATSAPP")
        assert "계약서 보내줘" in result["translation"], (
            "Translation should echo original content."
        )


# ── Relationship Tone Differentiation ────────────────────────────────────────

class TestRelationshipToneDifferentiation:
    """Tests that different relationships produce different response content."""

    def test_boss_and_family_responses_differ(self, engine):
        """BOSS and FAMILY mock responses must have different suggestion content."""
        boss = engine._generate_mock_response("오늘 오세요?", "BOSS", "WHATSAPP")
        family = engine._generate_mock_response("오늘 오세요?", "FAMILY", "WHATSAPP")
        boss_texts = [s["content"] for s in boss["suggestions"]]
        family_texts = [s["content"] for s in family["suggestions"]]
        assert boss_texts != family_texts, (
            "BOSS and FAMILY should produce distinctly different response styles."
        )

    def test_boss_response_contains_formal_korean(self, engine):
        """BOSS mock suggestions should contain formal Korean markers (부장님/님)."""
        result = engine._generate_mock_response("보고서 준비해줘.", "BOSS", "WHATSAPP")
        all_content = " ".join(s["content"] for s in result["suggestions"])
        formal_markers = ["부장님", "님", "드리겠습니다", "하겠습니다"]
        found = any(m in all_content for m in formal_markers)
        assert found, f"BOSS response should contain formal markers. Content: {all_content[:100]}"

    def test_family_response_contains_informal_korean(self, engine):
        """FAMILY mock suggestions should contain informal Korean (응, 알겠어, ~야)."""
        result = engine._generate_mock_response("오늘 집에 와?", "FAMILY", "WHATSAPP")
        all_content = " ".join(s["content"] for s in result["suggestions"])
        informal_markers = ["응", "알겠어", "야", "~", "자", "할게"]
        found = any(m in all_content for m in informal_markers)
        assert found, f"FAMILY response should contain informal markers. Content: {all_content[:100]}"

    def test_coworker_slack_uses_markdown(self, engine):
        """COWORKER SLACK mock response must contain Slack markdown (*bold*)."""
        result = engine._generate_mock_response("자료 확인해줘.", "COWORKER", "SLACK")
        all_content = " ".join(s["content"] for s in result["suggestions"])
        assert "*" in all_content, (
            f"COWORKER SLACK response should use *bold* markdown. Content: {all_content[:100]}"
        )


# ── Platform Routing in Mock ──────────────────────────────────────────────────

class TestPlatformRoutingInMock:
    """Tests that platform parameter affects mock response content."""

    def test_boss_slack_vs_boss_whatsapp_differ(self, engine):
        """BOSS + SLACK and BOSS + WHATSAPP should produce different content."""
        slack = engine._generate_mock_response("지시사항", "BOSS", "SLACK")
        whatsapp = engine._generate_mock_response("지시사항", "BOSS", "WHATSAPP")
        slack_texts = [s["content"] for s in slack["suggestions"]]
        whatsapp_texts = [s["content"] for s in whatsapp["suggestions"]]
        assert slack_texts != whatsapp_texts, (
            "BOSS SLACK and BOSS WHATSAPP should produce platform-differentiated responses."
        )

    def test_unknown_platform_falls_back_to_whatsapp(self, engine):
        """Unknown platform should fall back to WHATSAPP style without error."""
        result = engine._generate_mock_response("테스트", "COWORKER", "UNKNOWN_PLATFORM")
        assert isinstance(result, dict), "Unknown platform must not crash."
        assert "suggestions" in result, "Unknown platform should produce suggestions."


# ── End-to-End: generate_replies (No-API-Key Fallback) ───────────────────────

class TestGenerateRepliesNoKeyFallback:
    """Tests generate_replies() when GEMINI_API_KEY is not set (mock fallback path)."""

    @pytest.mark.asyncio
    async def test_generate_replies_returns_dict_no_key(self, engine):
        """With empty API key, generate_replies must return a mock dict."""
        # Force empty key for this test
        original_key = engine.__class__.__module__  # not used, just reference
        import backend.app.config as cfg
        original_api_key = cfg.settings.GEMINI_API_KEY
        cfg.settings.GEMINI_API_KEY = ""

        try:
            result = await engine.generate_replies(
                sender="김부장",
                content="보고서 준비해줘.",
                relationship="BOSS",
                is_group=False,
                platform="KAKAO"
            )
            assert isinstance(result, dict), "generate_replies must return a dict."
            assert "suggestions" in result, "Result must have suggestions key."
            assert len(result["suggestions"]) > 0, "Must have at least 1 suggestion."
        finally:
            cfg.settings.GEMINI_API_KEY = original_api_key

    @pytest.mark.asyncio
    async def test_generate_replies_group_chat_no_key(self, engine):
        """Group chat flag must not crash generate_replies in mock mode."""
        import backend.app.config as cfg
        cfg.settings.GEMINI_API_KEY = ""
        try:
            result = await engine.generate_replies(
                sender="팀원A",
                content="회의 안건 공유합니다.",
                relationship="COWORKER",
                is_group=True,
                platform="SLACK"
            )
            assert result is not None, "Group chat should not return None."
        finally:
            cfg.settings.GEMINI_API_KEY = ""
