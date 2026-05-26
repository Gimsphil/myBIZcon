# -*- coding: utf-8 -*-
"""
myBIZcon FastAPI Backend - Main Application
===========================================
AGY Step 15 Security Hardening applied:
  - CORS whitelist from ALLOWED_ORIGINS env var (no more wildcard *)
  - X-API-Key header authentication on sensitive endpoints
  - Path traversal protection on /voice/meeting file_path parameter

Step 19 Enhancement:
  - GET /health endpoint with uptime, RAG index status, CORS origin count
  - .env.example provided for easy deployment configuration

Role flow: AGY (Coder) → Antigravity (Reviewer/Push Gate)
"""
import os
import time
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Depends, Header
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.config import external_services_disabled, settings
from app.services.relationship_engine import relationship_engine
from app.services.google_workspace import google_workspace
from app.services.diarization_engine import diarization_engine
from app.services.voice_service import voice_service
from app.services.copilot_search import copilot_search
from app.services.rag_engine import rag_engine
from app.services.hinoter_notes import hinoter_note_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("myBIZcon_Main")

# Track server start time for uptime reporting
_SERVER_START_TIME = time.time()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.1.0",
    description="Universal AI Business Assistant (myBIZcon) API Server - Phase 6 Secured"
)

# ── Security: API Key Authentication Dependency ────────────────────────────
def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """
    Validates the X-API-Key header against the configured SECRET_API_KEY.
    Used on sensitive admin endpoints to prevent unauthorized access.
    """
    if x_api_key != settings.SECRET_API_KEY:
        logger.warning("⛔ Unauthorized API Key attempt blocked.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key. Access denied."
        )
    return x_api_key


# ── Security: Path Traversal Guard ─────────────────────────────────────────
def validate_recording_path(file_path: str) -> str:
    """
    Ensures the provided file_path resolves strictly within the
    SAFE_RECORDINGS_ROOT directory. Prevents directory traversal attacks.
    """
    safe_root = settings.SAFE_RECORDINGS_ROOT
    abs_path = os.path.abspath(file_path)
    if not abs_path.startswith(safe_root):
        logger.warning(f"⛔ Path traversal attempt blocked: {file_path!r}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Access denied. Recording files must reside within the "
                f"designated recordings directory."
            )
        )
    return abs_path


# ── CORS: Whitelist from environment (no more wildcard *) ──────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Schemas
class ChatMessagePayload(BaseModel):
    sender: str
    content: str
    conversation_title: str
    relationship: Optional[str] = "COWORKER"
    is_group: Optional[bool] = False
    platform: Optional[str] = "WHATSAPP"

class CalendarEventPayload(BaseModel):
    summary: str
    description: str
    start_time: str
    end_time: str

class TaskPayload(BaseModel):
    title: str
    notes: str
    due_date: Optional[str] = None

class BackupPayload(BaseModel):
    title: str
    transcript_markdown: str
    folder_name: Optional[str] = "myBIZcon/Chats"

class VoiceMeetingPayload(BaseModel):
    file_path: str

class STTPayload(BaseModel):
    file_path: str

class TTSPayload(BaseModel):
    text: str

class SearchPayload(BaseModel):
    query: str

class WAconnTranscriptLine(BaseModel):
    speaker: Optional[str] = "Unknown"
    text: str = Field(..., min_length=1)

class WAconnGenerateReplyPayload(BaseModel):
    message: str = Field(..., min_length=1)
    persona: str = Field(..., min_length=1)
    channel: Optional[str] = "workspace chat"

class WAconnMeetingSummaryPayload(BaseModel):
    transcript: List[WAconnTranscriptLine] = Field(..., min_length=1)

class WAconnAskNotesPayload(BaseModel):
    transcript: List[WAconnTranscriptLine] | str
    question: str = Field(..., min_length=1)

class NoteCapturePayload(BaseModel):
    title: str
    source_type: str = "recording"
    source_uri: Optional[str] = None
    transcript: str
    speaker_labels: Optional[List[str]] = None
    calendar_event_id: Optional[str] = None
    auto_join_calendar: Optional[bool] = False
    ask: Optional[str] = None


def _normalise_waconn_persona(persona: str) -> str:
    persona_upper = (persona or "").upper()
    if "BOSS" in persona_upper:
        return "BOSS"
    if "CLIENT" in persona_upper:
        return "CLIENT"
    if "FAMILY" in persona_upper:
        return "FAMILY"
    return "COWORKER"


def _normalise_waconn_channel(channel: str | None) -> str:
    channel_upper = (channel or "WHATSAPP").upper()
    if "SLACK" in channel_upper:
        return "SLACK"
    if "KAKAO" in channel_upper:
        return "KAKAOTALK"
    if "TELEGRAM" in channel_upper:
        return "TELEGRAM"
    return "WHATSAPP"


def _transcript_lines_to_text(transcript: List[WAconnTranscriptLine]) -> str:
    return "\n".join(
        f"{line.speaker or 'Unknown'}: {line.text}" for line in transcript
    )


def _build_waconn_meeting_markdown(transcript_text: str, note: dict) -> str:
    decisions = note.get("decisions") or ["No explicit decisions were detected."]
    action_items = note.get("action_items") or []
    action_lines = [
        f"- {item.get('title', 'Follow up')}"
        + (f" (due: {item['due_date']})" if item.get("due_date") else "")
        for item in action_items
    ] or ["- No explicit action items were detected."]

    transcript_block = "\n".join(f"- {line}" for line in transcript_text.splitlines())
    return (
        "# Executive Summary (핵심 요약)\n"
        f"{note.get('summary', 'Meeting transcript captured for offline analysis.')}\n\n"
        "# Decisions Made (결정 사항)\n"
        + "\n".join(f"- {decision}" for decision in decisions)
        + "\n\n# Auto-Extracted Action Items (조치 사항)\n"
        + "\n".join(action_lines)
        + "\n\n# Transcript\n"
        + transcript_block
    )


# Endpoints

@app.get("/")
def read_root():
    """Root endpoint: basic online check."""
    return {
        "status": "ONLINE",
        "service": "myBIZcon API Gateway",
        "engine": "Google Gemini 1.5 Flash"
    }


@app.post("/api/generate-reply")
async def waconn_generate_reply(payload: WAconnGenerateReplyPayload):
    """
    WAconn-compatible reply drafting endpoint.

    The response shape intentionally matches WAconn frontend expectations:
    draftOriginal, draftTranslated, mode. In offline mode this reuses the
    relationship engine's deterministic mock path and does not call Gemini.
    """
    relationship = _normalise_waconn_persona(payload.persona)
    platform = _normalise_waconn_channel(payload.channel)
    result = await relationship_engine.generate_replies(
        sender="WAconn",
        content=payload.message,
        relationship=relationship,
        is_group=False,
        platform=platform,
    )
    suggestions = result.get("suggestions") or []
    draft_original = (
        suggestions[0].get("content")
        if suggestions and isinstance(suggestions[0], dict)
        else f"Received: {payload.message}"
    )
    return {
        "draftOriginal": draft_original,
        "draftTranslated": result.get("translation", payload.message),
        "mode": "api"
        if settings.GEMINI_API_KEY and not external_services_disabled()
        else "simulation",
    }


@app.post("/api/meeting-summary")
def waconn_meeting_summary(payload: WAconnMeetingSummaryPayload):
    """
    WAconn-compatible meeting minutes endpoint.

    Uses the local HiNoter note logic to extract summary, decisions, and action
    items from client-provided transcript text. No external AI or Workspace
    service is called by this endpoint.
    """
    transcript_text = _transcript_lines_to_text(payload.transcript)
    note = hinoter_note_service.capture_note(
        title="WAconn Meeting",
        source_type="waconn_transcript",
        source_uri=None,
        transcript=transcript_text,
        speaker_labels=None,
        ask=None,
    )
    return {
        "markdown": _build_waconn_meeting_markdown(transcript_text, note),
        "mode": "simulation",
    }


@app.post("/api/ask-notes")
def waconn_ask_notes(payload: WAconnAskNotesPayload):
    """
    WAconn-compatible transcript Q&A endpoint backed by local note logic.
    """
    if isinstance(payload.transcript, list):
        transcript_text = _transcript_lines_to_text(payload.transcript)
    else:
        transcript_text = payload.transcript

    note = hinoter_note_service.capture_note(
        title="WAconn Notes",
        source_type="waconn_transcript",
        source_uri=None,
        transcript=transcript_text,
        speaker_labels=None,
        ask=payload.question,
    )
    return {
        "answer": note.get("ask_ai", {}).get("answer") or note.get("summary", ""),
        "mode": "simulation",
    }


@app.get("/health")
def health_check():
    """
    🟢 Extended Health Check endpoint.
    Returns server uptime, RAG index status, CORS policy count, and engine info.
    Useful for monitoring dashboards and deployment readiness verification.
    Added: Antigravity Step 19 (Phase 7 concurrent work).
    """
    uptime_seconds = round(time.time() - _SERVER_START_TIME, 2)
    return {
        "status": "HEALTHY",
        "version": "1.1.0",
        "engine": "Google Gemini 1.5 Flash",
        "uptime_seconds": uptime_seconds,
        "cors_origins_count": len(settings.ALLOWED_ORIGINS),
        "rag_indexed": rag_engine.is_indexed,
        "rag_corpus_size": len(rag_engine.corpus),
        "safe_recordings_root": settings.SAFE_RECORDINGS_ROOT,
    }

@app.post(f"{settings.API_V1_STR}/chat/message")
async def process_chat_message(payload: ChatMessagePayload):
    """
    Scrapes and syncs message from Android Accessibility client.
    Supports dynamic few-shot style emulation via local RAG TF-IDF engine.
    """
    logger.info(f"✉️ Processing incoming scraped message from '{payload.sender}' on platform '{payload.platform}'")
    is_group_chat = payload.is_group or "Group" in payload.conversation_title or "," in payload.conversation_title
    
    relationship_profile = payload.relationship
    if "부장" in payload.sender or "팀장" in payload.sender or "Boss" in payload.conversation_title:
        relationship_profile = "BOSS"
    elif "대표" in payload.sender or "바이어" in payload.sender or "Client" in payload.conversation_title:
        relationship_profile = "CLIENT"
    elif "엄마" in payload.sender or "자기" in payload.sender or "Family" in payload.conversation_title:
        relationship_profile = "FAMILY"

    result = await relationship_engine.generate_replies(
        sender=payload.sender,
        content=payload.content,
        relationship=relationship_profile,
        is_group=is_group_chat,
        platform=payload.platform
    )
    return result

@app.post(f"{settings.API_V1_STR}/workspace/calendar")
def create_calendar_event(payload: CalendarEventPayload):
    logger.info(f"📅 Request to schedule Google Calendar event: '{payload.summary}'")
    result = google_workspace.sync_calendar_event(
        summary=payload.summary,
        description=payload.description,
        start_time=payload.start_time,
        end_time=payload.end_time
    )
    return result

@app.post(f"{settings.API_V1_STR}/workspace/task")
def create_workspace_task(payload: TaskPayload):
    logger.info(f"📋 Request to add Google Task: '{payload.title}'")
    result = google_workspace.sync_task(
        title=payload.title,
        notes=payload.notes,
        due_date=payload.due_date
    )
    return result

@app.post(f"{settings.API_V1_STR}/workspace/backup")
def archive_transcript(payload: BackupPayload):
    logger.info(f"💾 Request to archive conversation transcript under Title: '{payload.title}'")
    result = google_workspace.backup_to_drive(
        title=payload.title,
        markdown_content=payload.transcript_markdown,
        folder_name=payload.folder_name
    )
    return result

@app.post(f"{settings.API_V1_STR}/workspace/index")
def trigger_rag_indexing(api_key: str = Depends(verify_api_key)):
    """
    Triggers manual indexing of archived Markdown documents to generate TF-IDF RAG weights.
    🔐 PROTECTED: Requires valid X-API-Key header (Step 15 Security Hardening).
    """
    logger.info("⚡ RAG Index trigger requested via API (authenticated).")
    rag_engine.reindex_corpus()
    return {"status": "SUCCESS", "message": f"RAG Corpus indexed with {len(rag_engine.corpus)} documents."}

# --- Phase 3 Voice & Audio Endpoints ---

@app.post(f"{settings.API_V1_STR}/voice/meeting")
async def process_voice_meeting(payload: VoiceMeetingPayload):
    """
    Ingests recorded meeting audio file, performs diarization,
    summarization, and triggers automated workspace sync.
    🔐 PATH GUARD: file_path validated against SAFE_RECORDINGS_ROOT (Step 15 Security Hardening).
    """
    safe_path = validate_recording_path(payload.file_path)
    logger.info(f"🎙️ Request to diarize meeting audio (path validated): '{safe_path}'")
    result = await diarization_engine.process_audio_meeting(safe_path)
    return result

@app.post(f"{settings.API_V1_STR}/voice/stt")
async def transcribe_audio_file(payload: STTPayload):
    """
    Direct endpoint for Whisper Speech-To-Text transcription.
    """
    logger.info(f"🎙️ Request to transcribe: '{payload.file_path}'")
    text = await voice_service.transcribe_audio(payload.file_path)
    return {"text": text}

@app.post(f"{settings.API_V1_STR}/voice/tts")
async def synthesize_text_to_voice(payload: TTSPayload):
    """
    Direct endpoint for Text-To-Speech audio synthesis.
    """
    logger.info(f"🔊 Request to synthesize voice: '{payload.text[:20]}...'")
    audio_bytes = await voice_service.synthesize_voice(payload.text)
    return Response(content=audio_bytes, media_type="audio/wav")

# --- HiNoter-style AI Note Endpoints ---

@app.post(f"{settings.API_V1_STR}/notes/capture")
def capture_ai_note(payload: NoteCapturePayload):
    """
    Creates a HiNoter-style structured AI note from a transcript/audio metadata payload.

    Supports the feature set found in current HiNoter listings: one-tap capture,
    speaker-aware transcription, AI summaries, mind maps, Ask AI, keyword jump,
    calendar auto-join metadata, audio/YouTube ingestion metadata, encrypted note
    flags, and owner-controlled sharing payloads. This endpoint is offline-safe:
    it does not call live calendar, YouTube, or AI services by itself.
    """
    logger.info(f"📝 Capturing HiNoter-style AI note: '{payload.title}' ({payload.source_type})")
    return hinoter_note_service.capture_note(
        title=payload.title,
        source_type=payload.source_type,
        source_uri=payload.source_uri,
        transcript=payload.transcript,
        speaker_labels=payload.speaker_labels,
        calendar_event_id=payload.calendar_event_id,
        auto_join_calendar=bool(payload.auto_join_calendar),
        ask=payload.ask,
    )

@app.post(f"{settings.API_V1_STR}/copilot/search")
async def copilot_background_search(payload: SearchPayload):
    """
    Direct endpoint for background search looking up business facts.
    """
    logger.info(f"🔍 Request to fetch search copilot facts for: '{payload.query}'")
    facts = await copilot_search.lookup_facts(payload.query)
    return {"facts": facts}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
