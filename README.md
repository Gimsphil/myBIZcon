# 🌐 myBIZcon — Universal AI Business Assistant

**myBIZcon** is a state-of-the-art personal business intelligence and productivity system. It bridges real-time messaging environments (WhatsApp, KakaoTalk, Telegram, Slack), standard VOIP/cellular calls, and physical/virtual meetings directly into the secure Google Workspace ecosystem (Calendar, Tasks, Keep, Drive, Docs) using advanced LLM-powered orchestrations (Google Gemini).

---

## 🎯 Core Features

### 1. Real-Time Chat Translation & Tone Recommender
*   **Dual-Translation Overlay**: Display incoming text in premium layouts: "Translation Only", "Original + Translation", or "Original Only".
*   **Relationship Persona Tuner**: Real-time generation of custom reply drafts based on context and relationship presets (`BOSS`, `CLIENT`, `COWORKER`, `FAMILY`).
*   **Multi-Party Group Conversation**: High-context parsing of multi-user conversation flows and threaded replies.

### 2. Meeting Mode & Call Copilot
*   **Physical/VoIP Meeting Recording**: Capture high-fidelity audio during live sessions.
*   **Speaker Diarization**: Separate and tag distinct voices (Speaker A, Speaker B, User).
*   **Meeting Minutes (회의록)**: Automated structured minutes detailing decisions and assigning Tasks/Calendar events, synced directly into Google Docs & Drive.

### 3. Google Workspace Ecosystem Sync
*   **Calendar Integration**: Instantly schedules meetings extracted from chats or voice conversations.
*   **Tasks & Keep Integration**: Saves To-Dos and important memos.
*   **Drive Archival**: Converts finished chats/meetings into clean Markdown logs for secure cloud archival.

### 4. HiNoter-style AI Note Mode
*   **One-Tap Note Capture**: Converts recording, transcript, uploaded audio metadata, or YouTube-link metadata into a structured AI note.
*   **Speaker-Aware Notes**: Splits transcript blocks by speaker labels and keeps searchable note sections.
*   **AI Summary & Mind Map**: Generates executive summary, keywords, action items, decisions, and a mind-map structure.
*   **Ask AI on Recordings**: Accepts a question about the captured note and returns a grounded answer from transcript-derived summary/action items.
*   **Keyword Jump Moments**: Produces timestamp-like searchable moments so the UI can jump to the matching audio/text segment.
*   **Secure Sharing Contract**: Marks notes as encrypted and creates owner-controlled Markdown sharing payloads.
*   **Calendar Auto-Join Metadata**: Keeps calendar meeting identifiers and auto-join flags ready for later approved live Workspace sync.

---

## 🛠️ Tech Stack & Architecture

*   **Core LLM**: Google Gemini 1.5 Flash (primary orchestrator) / Google Gemini 1.5 Pro (complex summarization).
*   **Speech Services**: OpenAI Whisper (STT) + Google TTS or ElevenLabs (TTS).
*   **Backend Server**: Python FastAPI (low-latency APIs).
*   **Mobile Interface**: Android Accessibility Service thin-client (Kotlin).

---

## 📁 Repository Directory Structure

```
myBIZcon/
├── implementation_plan.md   ← Approved multi-phase development plan
├── mybizcon_tracker.json    ← Cumulative run history & execution logs
├── README.md                ← This document
└── templates/               ← Core prompts and templates
```
