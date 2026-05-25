# -*- coding: utf-8 -*-
"""
myBIZcon FastAPI Backend - Main Application
===========================================
AGY Step 15 Security Hardening applied:
  - CORS whitelist from ALLOWED_ORIGINS env var (no more wildcard *)
  - X-API-Key header authentication on sensitive endpoints
  - Path traversal protection on /voice/meeting file_path parameter

Role flow: AGY (Coder) → Antigravity (Reviewer/Push Gate)
"""
import os
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Depends, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.config import settings
from app.services.relationship_engine import relationship_engine
from app.services.google_workspace import google_workspace
from app.services.diarization_engine import diarization_engine
from app.services.voice_service import voice_service
from app.services.copilot_search import copilot_search
from app.services.rag_engine import rag_engine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("myBIZcon_Main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Universal AI Business Assistant (myBIZcon) API Server"
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

# Endpoints

@app.get("/")
def read_root():
    return {
        "status": "ONLINE",
        "service": "myBIZcon API Gateway",
        "engine": "Google Gemini 1.5 Flash"
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
