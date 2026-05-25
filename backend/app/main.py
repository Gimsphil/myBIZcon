import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services.relationship_engine import relationship_engine
from app.services.google_workspace import google_workspace

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("myBIZcon_Main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Universal AI Business Assistant (myBIZcon) API Server"
)

# CORS configuration for cross-platform clients (Android Emulator, custom dashboards, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    Performs dynamic translation and outputs relationship suggested replies.
    """
    logger.info(f"✉️ Processing incoming scraped message from '{payload.sender}'")
    
    # Check if the title indicates a group chat automatically if not explicitly set
    is_group_chat = payload.is_group or "Group" in payload.conversation_title or "," in payload.conversation_title
    
    # Deduce relationship based on sender or conversation title for MVP
    relationship_profile = payload.relationship
    if "부장" in payload.sender or "팀장" in payload.sender or "Boss" in payload.conversation_title:
        relationship_profile = "BOSS"
    elif "바이어" in payload.sender or "대표" in payload.sender or "Client" in payload.conversation_title:
        relationship_profile = "CLIENT"
    elif "엄마" in payload.sender or "자기" in payload.sender or "Family" in payload.conversation_title:
        relationship_profile = "FAMILY"

    result = await relationship_engine.generate_replies(
        sender=payload.sender,
        content=payload.content,
        relationship=relationship_profile,
        is_group=is_group_chat
    )
    return result

@app.post(f"{settings.API_V1_STR}/workspace/calendar")
def create_calendar_event(payload: CalendarEventPayload):
    """
    Registers dates/times schedules on Google Calendar.
    """
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
    """
    Extracts action items and notes into Google Tasks.
    """
    logger.info(f"📋 Request to add Google Task: '{payload.title}'")
    result = google_workspace.sync_task(
        title=payload.title,
        notes=payload.notes,
        due_date=payload.due_date
    )
    return result

@app.post(f"{settings.API_V1_STR}/workspace/backup")
def archive_transcript(payload: BackupPayload):
    """
    Develops one-click Markdown serialization to Google Drive.
    """
    logger.info(f"💾 Request to archive conversation transcript under Title: '{payload.title}'")
    result = google_workspace.backup_to_drive(
        title=payload.title,
        markdown_content=payload.transcript_markdown,
        folder_name=payload.folder_name
    )
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
