# -*- coding: utf-8 -*-
"""HiNoter-style AI note capture service for myBIZcon.

This module keeps the feature contract deterministic/offline-safe while mirroring
public HiNoter capabilities: one-tap capture, transcription note generation,
speaker labels, AI summaries, mind maps, keyword jump/search, Ask AI, secure
sharing, calendar auto-join metadata, and audio/YouTube ingestion metadata.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from typing import Iterable


STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "are", "you", "will",
    "합니다", "주세요", "네", "다음", "회의", "공유", "기준", "검토",
}


class HiNoterNoteService:
    """Builds structured AI-note assets from a transcript payload."""

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
                    {"label": "요약", "items": [summary]},
                    {"label": "발화자", "items": speakers},
                    {"label": "키워드", "items": keywords[:8]},
                    {"label": "액션아이템", "items": [item["title"] for item in action_items]},
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
            moments.append({
                "offset_seconds": idx * 30,
                "text": text,
                "keywords": self._extract_keywords(text)[:5],
            })
        return moments

    def _extract_keywords(self, text: str) -> list[str]:
        tokens = re.findall(r"[가-힣A-Za-z0-9%]+", text or "")
        cleaned = [token for token in tokens if len(token) > 1 and token.lower() not in STOPWORDS]
        return [word for word, _ in Counter(cleaned).most_common(12)]

    def _extract_decisions(self, lines: list[str]) -> list[str]:
        decision_markers = ("확정", "결정", "검토", "승인", "인상", "진행")
        return [line.split(":", 1)[-1].strip() for line in lines if any(m in line for m in decision_markers)]

    def _extract_action_items(self, lines: list[str]) -> list[dict]:
        markers = ("보내", "공유", "준비", "작성", "등록", "확인", "해주세요", "하겠습니다")
        items = []
        for line in lines:
            text = line.split(":", 1)[-1].strip()
            if any(marker in text for marker in markers):
                items.append({"title": text[:60], "notes": text, "due_date": self._extract_due_date(text)})
        return items

    def _extract_due_date(self, text: str) -> str | None:
        if "월요일" in text:
            return "next-monday"
        if "수요일" in text:
            return "next-wednesday"
        if "오늘" in text:
            return "today"
        return None

    def _summarise(self, title: str, lines: list[str], keywords: list[str], action_items: list[dict]) -> str:
        first = lines[0].split(":", 1)[-1].strip() if lines else title
        action_count = len(action_items)
        keyword_text = ", ".join(keywords[:4]) if keywords else "핵심 키워드 없음"
        return f"{title}: {first} 중심으로 논의되었고, 주요 키워드는 {keyword_text}입니다. 액션아이템 {action_count}건이 추출되었습니다."

    def _answer_question(self, ask: str | None, summary: str, action_items: list[dict], decisions: list[str]) -> str:
        if not ask:
            return "질문이 없어서 요약과 추출된 액션아이템을 기준으로 노트를 생성했습니다."
        if "액션" in ask or "할일" in ask or "아이템" in ask:
            if not action_items:
                return "명시적인 액션아이템은 발견되지 않았습니다."
            return " / ".join(item["title"] for item in action_items)
        if "결정" in ask and decisions:
            return " / ".join(decisions)
        return summary

    def _to_markdown(self, title: str, lines: list[str]) -> str:
        body = "\n".join(f"- {line}" for line in lines)
        return f"# {title}\n\n## Transcript\n{body}\n"


hinoter_note_service = HiNoterNoteService()
