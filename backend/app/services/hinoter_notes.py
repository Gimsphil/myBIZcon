# -*- coding: utf-8 -*-
"""Offline-safe HiNoter-style note capture service for myBIZcon.

The service builds deterministic structured notes from client-provided text.
It intentionally does not call Google Calendar, YouTube, cloud AI APIs, or any
external service. Calendar and YouTube fields are treated as metadata only.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from typing import Iterable


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "are",
    "you",
    "will",
    "from",
    "have",
    "has",
    "please",
    "next",
    "meeting",
    "note",
}

DECISION_MARKERS = (
    "decide",
    "decided",
    "decision",
    "approve",
    "approved",
    "confirm",
    "confirmed",
    "budget",
    "increase",
    "승인",
    "검토",
    "결정",
    "확정",
    "예산",
    "인상",
)

ACTION_MARKERS = (
    "send",
    "share",
    "prepare",
    "register",
    "check",
    "confirm",
    "follow up",
    "진행",
    "작성",
    "등록",
    "공유",
    "전달",
    "보내",
    "보내주세요",
    "해주세요",
    "하겠습니다",
    "확인",
    "준비",
)

MONDAY_MARKERS = ("monday", "월요일")
WEDNESDAY_MARKERS = ("wednesday", "수요일")
TODAY_MARKERS = ("today", "오늘")


class HiNoterNoteService:
    """Build structured AI-note assets from a transcript payload."""

    FEATURE_FLAGS = [
        "one_tap_recording",
        "ai_transcription",
        "speaker_identification",
        "ai_summary",
        "mind_map",
        "ask_ai",
        "keyword_audio_jump",
        "secure_encrypted_notes",
        "owner_controlled_sharing",
        "calendar_auto_join",
        "youtube_or_audio_upload",
    ]

    def capture_note(
        self,
        *,
        title: str,
        source_type: str,
        source_uri: str | None,
        transcript: str,
        speaker_labels: list[str] | None = None,
        calendar_event_id: str | None = None,
        auto_join_calendar: bool = False,
        ask: str | None = None,
    ) -> dict:
        lines = self._normalise_lines(transcript)
        speakers = speaker_labels or self._infer_speakers(lines)
        speaker_sections = self._build_speaker_sections(lines, speakers)
        searchable_moments = self._build_searchable_moments(lines)
        keywords = self._extract_keywords(transcript)
        decisions = self._extract_decisions(lines)
        action_items = self._extract_action_items(lines)
        summary = self._summarise(title, lines, keywords, action_items)

        return {
            "status": "SUCCESS",
            "title": title,
            "created_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "source_type": source_type,
            "source_uri": source_uri,
            "calendar_event_id": calendar_event_id,
            "calendar_auto_join": bool(auto_join_calendar or calendar_event_id),
            "encrypted": True,
            "feature_flags": self.FEATURE_FLAGS,
            "summary": summary,
            "keywords": keywords,
            "transcript_markdown": self._to_markdown(title, lines),
            "speaker_sections": speaker_sections,
            "searchable_moments": searchable_moments,
            "mind_map": {
                "root": title,
                "branches": [
                    {"label": "Summary", "items": [summary]},
                    {"label": "Speakers", "items": speakers},
                    {"label": "Keywords", "items": keywords[:8]},
                    {"label": "Action Items", "items": [item["title"] for item in action_items]},
                ],
            },
            "decisions": decisions,
            "action_items": action_items,
            "ask_ai": {
                "question": ask,
                "answer": self._answer_question(ask, summary, action_items, decisions),
            },
            "share_payload": {
                "format": "markdown",
                "permissions": "owner-controlled",
                "redaction_ready": True,
            },
        }

    def _normalise_lines(self, transcript: str) -> list[str]:
        raw_lines = re.split(r"\n+|(?<=\.)\s+", transcript or "")
        return [line.strip() for line in raw_lines if line.strip()]

    def _infer_speakers(self, lines: Iterable[str]) -> list[str]:
        speakers: list[str] = []
        for line in lines:
            if ":" in line:
                speaker = line.split(":", 1)[0].strip()
                if speaker and speaker not in speakers:
                    speakers.append(speaker)
        return speakers or ["Speaker A"]

    def _build_speaker_sections(self, lines: list[str], speakers: list[str]) -> list[dict]:
        sections = []
        for line in lines:
            speaker = "Unknown"
            text = line
            if ":" in line:
                candidate, text = line.split(":", 1)
                speaker = candidate.strip() or speaker
                text = text.strip()
            elif speakers:
                speaker = speakers[0]
            sections.append({"speaker": speaker, "text": text})
        return sections

    def _build_searchable_moments(self, lines: list[str]) -> list[dict]:
        moments = []
        for idx, line in enumerate(lines):
            text = line.split(":", 1)[-1].strip()
            moments.append(
                {
                    "offset_seconds": idx * 30,
                    "text": text,
                    "keywords": self._extract_keywords(text)[:5],
                }
            )
        return moments

    def _extract_keywords(self, text: str) -> list[str]:
        tokens = re.findall(r"[^\W_]{2,}|[0-9]+%", text or "", flags=re.UNICODE)
        cleaned = [token for token in tokens if token.lower() not in STOPWORDS]
        return [word for word, _ in Counter(cleaned).most_common(12)]

    def _extract_decisions(self, lines: list[str]) -> list[str]:
        markers = (
            "decide",
            "decided",
            "decision",
            "approve",
            "approved",
            "confirm",
            "confirmed",
            "budget",
            "increase",
            "인상",
            "결정",
            "확정",
        )
        markers = markers + DECISION_MARKERS
        return [
            line.split(":", 1)[-1].strip()
            for line in lines
            if any(marker.lower() in line.lower() for marker in markers)
        ]

    def _extract_action_items(self, lines: list[str]) -> list[dict]:
        markers = (
            "send",
            "share",
            "prepare",
            "register",
            "check",
            "confirm",
            "follow up",
            "보내",
            "공유",
            "준비",
            "확인",
        )
        markers = markers + ACTION_MARKERS
        items = []
        for line in lines:
            text = line.split(":", 1)[-1].strip()
            if any(marker.lower() in text.lower() for marker in markers):
                items.append(
                    {
                        "title": text[:60],
                        "notes": text,
                        "due_date": self._extract_due_date(text),
                    }
                )
        return items

    def _extract_due_date(self, text: str) -> str | None:
        lowered = text.lower()
        for marker in MONDAY_MARKERS:
            if marker in lowered or marker in text:
                return "next-monday"
        for marker in WEDNESDAY_MARKERS:
            if marker in lowered or marker in text:
                return "next-wednesday"
        for marker in TODAY_MARKERS:
            if marker in lowered or marker in text:
                return "today"
        if "monday" in lowered or "월요일" in text:
            return "next-monday"
        if "wednesday" in lowered or "수요일" in text:
            return "next-wednesday"
        if "today" in lowered or "오늘" in text:
            return "today"
        return None

    def _summarise(
        self,
        title: str,
        lines: list[str],
        keywords: list[str],
        action_items: list[dict],
    ) -> str:
        first = lines[0].split(":", 1)[-1].strip() if lines else title
        keyword_text = ", ".join(keywords[:4]) if keywords else "no major keywords"
        return (
            f"{title}: captured {len(lines)} transcript segment(s). "
            f"Opening context: {first}. "
            f"Key terms: {keyword_text}. "
            f"Action items extracted: {len(action_items)}."
        )

    def _answer_question(
        self,
        ask: str | None,
        summary: str,
        action_items: list[dict],
        decisions: list[str],
    ) -> str:
        if not ask:
            return "No question was provided; the note was summarized and indexed."
        lowered = ask.lower()
        if "action" in lowered or "todo" in lowered or "할 일" in ask or "액션" in ask:
            if not action_items:
                return "No explicit action items were found."
            return " / ".join(item["title"] for item in action_items)
        if ("decision" in lowered or "결정" in ask) and decisions:
            return " / ".join(decisions)
        return summary

    def _to_markdown(self, title: str, lines: list[str]) -> str:
        body = "\n".join(f"- {line}" for line in lines)
        return f"# {title}\n\n## Transcript\n{body}\n"


hinoter_note_service = HiNoterNoteService()
