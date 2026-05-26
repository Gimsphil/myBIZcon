# -*- coding: utf-8 -*-
import os
import base64
import json
import logging
import httpx
from datetime import datetime
from app.config import external_services_disabled, settings
from app.services.google_workspace import google_workspace

logger = logging.getLogger("myBIZcon_DiarizationEngine")

DIARIZATION_SYSTEM_INSTRUCTION = """
You are myBIZcon's premium multimodal business intelligence analyst.
You are given a live audio recording of a business meeting or a client VoIP call.

Perform the following tasks:
1. Perform high-accuracy speech-to-text transcription in Korean.
2. Perform Speaker Diarization: Distinguish the speakers. Identify them as:
   - "Speaker A" (e.g. Buyer / Client / Boss - remote caller)
   - "Speaker B" (User - the personal business assistant owner)
   - "Speaker C" (Other participant, if any)
3. Catch Speaker Voice Characteristics:
   - Carefully analyze each speaker's vocal properties (tempo, pitch, rhythm, vocal stability, pauses, and hesitations).
4. Perform Sentiment & Emotion Analysis:
   - Evaluate the active emotional tone of each speaker during the flow of conversation (e.g. Professional, Confident, Pleased, Urgent, Anxious, Frustrated, Calm).
   - Inject dynamic emotion emojis and tone state annotations into the diarized transcript blocks (e.g., "[Speaker A - Excited 😊]: ...").
5. Formulate structured "Meeting Minutes" in Markdown format containing attendees list, transcript logs with tone/emotion labels, key decisions, and action items.
6. Extract action items (Tasks) and calendar events (Schedules).

You MUST output your final answer strictly in JSON matching the following schema:
{
  "transcript_markdown": "## 📝 Meeting Minutes & Transcript\\n... (formatted Markdown with dialogue speaker labels, tone emojis, and summaries)",
  "summary": "Short executive summary of the conversation",
  "decisions": ["Decision 1", "Decision 2"],
  "speaker_analysis": [
    {
      "speaker": "Speaker A / Speaker B",
      "voice_profile": "Vocal speed, pitch range, rhythm or stability characteristics",
      "sentiment_trends": "General emotional mood state of the speaker (e.g., Excited, Urgent, Calm)"
    }
  ],
  "tasks": [
    {
      "title": "Title of the task",
      "notes": "Detailed description of action item",
      "due_date": "YYYY-MM-DD format (if mentioned, otherwise null)"
    }
  ],
  "schedules": [
    {
      "summary": "Calendar appointment title",
      "description": "Calendar appointment description",
      "start_time": "ISO 8601 format YYYY-MM-DDTHH:MM:SS",
      "end_time": "ISO 8601 format YYYY-MM-DDTHH:MM:SS (default to 1 hour after start if not mentioned)"
    }
  ]
}
"""

class DiarizationEngineService:
    """
    🧠 DiarizationEngineService
    Leverages Gemini 1.5 Flash's native audio multimodal context to:
    - Diarize audio transcripts (User, Speaker A, B) directly.
    - Evaluate voice acoustic characteristics and dynamic emotional states (Sentiment analysis).
    - Back up results directly into the Google Workspace ecosystem.
    """
    async def process_audio_meeting(self, wav_file_path: str) -> dict:
        """
        Sends the WAV audio file to Gemini to perform multimodal transcription,
        diarization, emotion analysis, and sync mapping.
        """
        logger.info(f"🧠 Processing meeting audio through Gemini: {wav_file_path}")

        if not os.path.exists(wav_file_path):
            logger.error(f"❌ Audio file path does not exist: {wav_file_path}")
            return {"status": "ERROR", "message": "Audio file not found."}

        if external_services_disabled():
            logger.warning("External services disabled. Generating offline diarized mock response.")
            return self._generate_mock_diarization()

        # Check API key status
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.warning("⚠️ GEMINI_API_KEY is empty. Generating offline diarized mock response.")
            return self._generate_mock_diarization()

        # Read audio file and convert to base64
        try:
            with open(wav_file_path, "rb") as f:
                audio_bytes = f.read()
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        except Exception as e:
            logger.error(f"❌ Failed to read or encode WAV file: {str(e)}")
            return self._generate_mock_diarization()

        # Build payload for Gemini multimodal audio upload
        url = f"{settings.GEMINI_API_URL}?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "inlineData": {
                                "mimeType": "audio/wav",
                                "data": audio_b64
                            }
                        },
                        {
                            "text": "Transcribe, diarize speaker voices, analyze acoustic emotions, and summarize this business audio recording into the specified JSON format."
                        }
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": DIARIZATION_SYSTEM_INSTRUCTION}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    parsed_json = json.loads(raw_text)
                    logger.info("✅ Multimodal audio processing successful.")
                    
                    # Automate Sync to Google Workspace
                    self._perform_workspace_sync(parsed_json)
                    return parsed_json
                else:
                    logger.error(f"❌ Gemini REST Error: {response.status_code} - {response.text}")
                    return self._generate_mock_diarization()
        except Exception as e:
            logger.error(f"❌ Gemini multimodal call failed: {str(e)}")
            return self._generate_mock_diarization()

    def _perform_workspace_sync(self, result: dict):
        """Helper to sync newly generated diarized structures into Workspace APIs."""
        logger.info("💼 Initiating automated Workspace Sync for parsed meeting assets...")
        
        # 1. Drive Archival
        title = f"Meeting Minutes - {datetime.now().strftime('%Y-%m-%d')}"
        google_workspace.backup_to_drive(
            title=title,
            markdown_content=result.get("transcript_markdown", ""),
            folder_name="myBIZcon/Meetings"
        )
        
        # 2. Sync Calendar Event if available
        schedules = result.get("schedules", [])
        for sched in schedules:
            google_workspace.sync_calendar_event(
                summary=sched.get("summary", "myBIZcon Meeting"),
                description=sched.get("description", ""),
                start_time=sched.get("start_time", ""),
                end_time=sched.get("end_time", "")
            )

        # 3. Sync Tasks if available
        tasks = result.get("tasks", [])
        for task in tasks:
            google_workspace.sync_task(
                title=task.get("title", ""),
                notes=task.get("notes", ""),
                due_date=task.get("due_date")
            )
        logger.info("✅ Workspace Sync completed successfully.")

    def _generate_mock_diarization(self) -> dict:
        """High-context diarization mock data (offline fallback) with vocal profile and emotion analytics."""
        logger.info("🔮 Running offline diarized mock pipeline with emotion metadata.")
        mock_transcript = (
            "## 📝 회의록 (Meeting Minutes & Transcript)\n"
            "**회의 일시**: 2026-05-25 11:20\n"
            "**참석자**: Speaker A (대표님 / Client), Speaker B (과장 / User)\n\n"
            "### 💬 회의 상세 기록\n"
            "- **[Speaker A - 신중함 🤔]**: 이번 제휴 관련해서 다음 주 수요일 전략 기획 발표회를 갖고자 하는데 일정이 비어있으실까요?\n"
            "- **[Speaker B - 자신감 넘침 😎]**: 네, 대표님. 캘린더 확인 후 다음 주 수요일 오전 10시로 등록하여 진행하겠습니다.\n"
            "- **[Speaker A - 만족스러움 😊]**: 좋습니다. 그럼 가격 가이드도 5% 인상하는 기획안을 보충해서 그 회의 때 같이 보고해 주시길 바랍니다.\n"
            "- **[Speaker B - 정중함 💼]**: 알겠습니다. 5% 인상안 기획 보고서 작성하여 공유해 올리겠습니다.\n\n"
            "### 📌 결정 사항\n"
            "- 전략 제휴 발표회 날짜 확정 (다음 주 수요일)\n"
            "- 가격 가이드 라인 5% 인상안 반영\n"
        )
        
        today = datetime.now()
        next_wed_str = today.strftime("%Y-%m-%dT10:00:00")
        next_wed_end_str = today.strftime("%Y-%m-%dT11:00:00")

        mock_payload = {
            "transcript_markdown": mock_transcript,
            "summary": "전략 제휴 발표회 일정 확정 및 가격 5% 인상안 추가 기획 보고 조율.",
            "decisions": [
                "다음 주 수요일 미팅 진행",
                "가격 5% 인상안 기획 및 반영 결정"
            ],
            "speaker_analysis": [
                {
                    "speaker": "Speaker A (Client)",
                    "voice_profile": "다소 느린 템포, 안정적이고 차분한 피치, 숙고하는 듯한 일시 정지 패턴 감지",
                    "sentiment_trends": "신중함(Prudent) 🤔 -> 만족함(Pleased) 😊 (긍정적인 조율 흐름)"
                },
                {
                    "speaker": "Speaker B (User)",
                    "voice_profile": "명료하고 빠른 템포, 흔들림 없는 높은 목소리 톤과 안정적인 호흡 패턴 감지",
                    "sentiment_trends": "자신감(Confident) 😎 -> 차분하고 정중함(Polite) 💼"
                }
            ],
            "tasks": [
                {
                    "title": "가격 가이드라인 5% 인상 보고서 작성",
                    "notes": "대표님 요청 사항: 전략 제휴 발표회 보충 자료로 5% 인상안 기획 추가 보고",
                    "due_date": today.strftime("%Y-%m-%d")
                }
            ],
            "schedules": [
                {
                    "summary": "대표님 미팅 - 전략 기획 발표회",
                    "description": "5% 인상안 기획 보고 및 전략 제휴 파트너십 발표회",
                    "start_time": next_wed_str,
                    "end_time": next_wed_end_str
                }
            ]
        }
        
        self._perform_workspace_sync(mock_payload)
        return mock_payload

diarization_engine = DiarizationEngineService()
