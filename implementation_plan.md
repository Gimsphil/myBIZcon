# 🌐 Universal AI Business Assistant (myBIZcon) Implementation Plan [APPROVED]

Welcome! This approved implementation plan outlines the strategic decisions, technical architecture, and phase-by-phase development schedule for **myBIZcon (Universal AI Business Assistant)**—a personal business intelligence system that bridges communication channels (WhatsApp, Meetings, PC Notifications, etc.) with the Google Workspace ecosystem (Calendar, Tasks, Keep, Drive, Docs) using advanced LLM-powered orchestration.

---

## ⚖️ Strategic Feasibility Assessment & Tech Selection

Before diving into the development phases, we must align on two critical technical decisions: **AI Model Selection** and **Target Platform Selection**. Below is an engineering evaluation of the options.

### 1. AI Model Selection: Google Gemini vs. Meta Llama 3

| Criteria | Google Gemini (1.5 Flash / Pro) | Meta Llama 3 (Cloud / On-Device) |
| :--- | :--- | :--- |
| **Workspace Integration** | 🌟 **Superior**: Direct ecosystem integration with Google APIs. Gemini is designed to orchestrate Workspace data seamlessly. | ⚠️ **Manual**: Requires building complex API connectors, tool-calling pipelines, and mapping data schemas manually. |
| **Context Window** | 🌟 **Unmatched (up to 2M tokens)**: Can ingest massive chat histories, multi-party group chats, and long meeting transcripts for high-accuracy RAG. | ⚠️ **Limited (8k - 128k)**: Requires aggressive summarization and chunking of chat transcripts. |
| **Multilingual (Korean)** | 🌟 **Excellent**: Out-of-the-box native understanding of Korean business nuances, honorifics, and dual translation. | 📈 **Moderate**: Llama 3 is strong, but sometimes lacks deep local context and localized business etiquette defaults. |
| **Latency & Cost** | 🌟 **Low Latency (Flash)**: Gemini 1.5 Flash provides near real-time token generation at extremely low cost. | ⚠️ **High Infrastructure Cost**: Cloud deployment (e.g., RunPod, AWS) is expensive. On-device is slow and drains mobile battery. |
| **Privacy & Compliance**| 📈 **Enterprise Cloud Privacy**: Governed by Google Cloud's data isolation agreements (no model training on customer data). | 🌟 **Ultimate Privacy**: If run fully on-premise, data never leaves the client's network. |

> [!TIP]
> **Decision: Google Gemini (Core) + Llama 3 Adapter Pattern**
> We use **Google Gemini (Gemini 1.5 Flash)** as the primary translation and orchestration engine for the MVP. Its low latency (crucial for live audio/text translation) and native Google API integrations are perfect. However, we will build a **modular LLM interface layer** (Adapter Pattern) so that the core logic can easily swap to a self-hosted **Meta Llama 3** engine in the future if required for enterprise local-data compliance.

---

### 2. Platform Selection: Android & PC Co-Existence

| Capability | Android Client (Kotlin) | PC Client (Python Tkinter) |
| :--- | :--- | :--- |
| **On-Screen Capture** | 🌟 **Accessibility Services**: Scrapes WhatsApp messages. | 🌟 **Win32 / PyAutoGUI**: Monitors desktop notifications and active messenger windows. |
| **Audio Capture** | 🌟 **Internal Audio Capture / Mic**: Captures VOIP calls and live in-person meetings. | 🌟 **PyAudio / WASAPI Loopback**: Captures PC system audio (Zoom/Slack calls) and microphone inputs. |
| **Overlays** | 🌟 **System Overlays**: Floating bubbles over WhatsApp. | 🌟 **Frameless Transparent Tkinter Overlays**: Floating roll subtitles on Windows desktop. |
| **Compilation** | 🌟 **APK Build**: Gradle-assembled production package. | 🌟 **PyInstaller EXE**: Zero-dependency executable. |

> [!IMPORTANT]
> **Decision: Multi-Platform Ecosystem (Android APK + PC Windows Client)**
> To deliver a comprehensive bi-modal ecosystem:
> 1.  **Android Client (Kotlin)**: Scrapes mobile WhatsApp/messengers, renders custom overlays, and captures VoIP calls/meetings. Compiles into an **APK** via Android Studio/Gradle.
> 2.  **PC Desktop Client (Python Tkinter)**: Monitors PC notifications, captures system audio (Zoom, Teams, Slack calls) using loopback, renders frameless floating subtitles directly on Windows, and communicates with the FastAPI backend. Compiles into a single **EXE** via PyInstaller.
> 3.  **FastAPI Backend (Python)**: Unified gateway handling core AI requests and Google Workspace Sync for both clients.

---

## 📐 High-Platform Unified Architecture

```mermaid
graph TD
    subgraph Android Device
        A1[WhatsApp / Group Chats] -->|Accessibility Service| B1[myBIZcon Android Client]
        B1 -->|Audio Capture / Mic| C1[Real-Time STT/TTS & Speaker Diarization]
        B1 -->|Overlay API| D1[Floating Overlay UI]
    end

    subgraph PC Desktop - Windows
        A2[Zoom / Teams / PC WhatsApp] -->|PyAudio / WASAPI Loopback| B2[myBIZcon PC Desktop Client]
        B2 -->|Tkinter Threading| C2[Desktop Mic & System Audio Capture]
        B2 -->|Tkinter Overlay| D2[Desktop Floating Transparent Subtitles]
    end

    subgraph Backend Server - FastAPI
        B1 & B2 -->|Payloads| E[App Gateway / API Controller]
        E -->|Secure Context| F[LLM Router & Orchestrator]
        F -->|Prompt Context: Relationship & Tone| G[Gemini 1.5 Flash]
        F -->|Search Queries| H[Google Search tool API]
        F -->|Workspace Sync| I[Google Workspace Connectors]
    end

    subgraph Google Workspace Ecosystem
        I -->|Events| J[Google Calendar]
        I -->|Tasks| K[Google Tasks / Keep]
        I -->|Transcripts & Backups| L[Google Drive / Docs]
    end
```

---

## 📋 Comprehensive 4-Phase Implementation Plan (Revised)

### 🚀 Phase 1: Architecture, Security, Prompt Engineering & GIT Setup [Completed]
*   Git workspace connection and cumulative JSON execution tracker initialization.
*   Relationship prompting definitions and REST simulation client testing.

---

### 📦 Phase 2: MVP Development - WhatsApp Message Integration & Google Sync [Completed]
*   Android Accessibility scraping configurations and floating translation Overlay implementation.
*   FastAPI backend endpoints and Google Workspace Sync integrations (Calendar, Tasks, Drive Markdown).

---

### 🖥️ Phase 2.5: PC Desktop Client Development & APK Build Pipeline [Completed]
*   **2.5.1 PC Desktop Client (Tkinter)**:
    *   Build a beautiful frameless dark-themed desktop dashboard using **Tkinter**.
    *   Implement **Windows Floating Overlays**: Semi-transparent, click-through overlay labels to show live subtitles and translations over PC Zoom/WhatsApp.
    *   Create desktop notification grabber/monitor.
    *   Implement **WASAPI Loopback Capture**: Capture system sound (speaker output) and local mic input for call recording.
*   **2.5.2 Android APK Compilation Setup**:
    *   Create Gradle compilation scripts (`build.gradle`, `settings.gradle`) and automated batch scripts (`build_apk.bat`) for zero-click local Gradle compiling into an **APK** file.

---

### 🎙️ Phase 3: Real-Time Audio Capture, Meeting Mode & Voice Pipeline [In Progress]

This phase implements multi-modal voice processing, physical meeting capture, AI-driven speaker diarization, TTS integration, and an asynchronous Web Search Copilot.

#### ⚖️ Technical Architecture for Phase 3
1. **Hybrid Audio Capture (PC Client)**:
   - A robust audio capture engine utilizing `sounddevice` and `numpy` (with WASAPI loopback support).
   - **Zero-Dependency Fallback**: If system audio libraries or drivers are missing, the recorder dynamically switches to a synthetic PCM generator (generating standard WAV files with fake conversation frequencies) to guarantee error-free local simulations.
2. **Gemini Multimodal Diarization & STT**:
   - Instead of running resource-heavy local models (e.g. pyannote, local Whisper), we leverage **Google Gemini 1.5 Flash's native multimodal audio parsing**. 
   - Audio files (WAV) are sent directly to the backend, which feeds them to Gemini. The prompt instructs Gemini to perform **Joint Speech-to-Text and Speaker Diarization**, returning a structured markdown transcript with speaker tags (`[00:15 - Speaker A]`, `[00:45 - Speaker B]`, `[01:10 - User]`) and automatic Korean translation.
3. **Dual-Tier TTS Engine**:
   - **Standard (Offline/Free)**: Utilizes Google Text-to-Speech (`gTTS`) to generate local MP3 audio files.
   - **Premium**: Supports **ElevenLabs API** token-based generation for ultra-premium voice synthesis.
4. **Search-Assisted Web Copilot**:
   - A background utility that scans meeting transcripts or chat messages for key business entities (e.g. stock names, corporate acronyms, trending tech).
   - Performs asynchronous web search queries and returns context-rich "Fact Bubbles" shown on the transparent PC overlay.

---

## ⚠️ User Review Required (Phase 3)

> [!IMPORTANT]
> ### 1. Google Gemini 1.5 Multimodal Audio Requirements
> Raw audio files uploaded to Gemini 1.5 Flash must be under 20MB for fast REST processing. Long meetings (over 20 mins) will be automatically chunked or compressed by the PC recorder before transmission.
>
> ### 2. Audio Library Driver Dependencies
> Python recording via `sounddevice` requires standard system audio drivers (MME, WASAPI). If the client PC has no active microphone or speaker devices, it will automatically fallback to the **Synthetic Mock Conversation Recorder** to allow development and UI testing to continue smoothly.

---

## ❓ Open Questions (Phase 3)

> [!WARNING]
> 1. **TTS Playback Mechanism**: Do we want the Windows PC Client to automatically read aloud every suggested reply, or should it only play audio when a speaker clicks a "Play Voice (🎙️)" button next to the recommendation?
>    * *Proposed Default: Add a "Speak" icon/button next to suggested replies on the overlay to prevent unwanted audio in corporate environments.*
> 2. **Diarization Accents**: Should we pre-configure speaker profiles (e.g. "Speaker A" -> "Client", "Speaker B" -> "Manager") in the prompt, or let Gemini dynamically label speakers based on context?
>    * *Proposed Default: Let Gemini dynamically detect speaker roles and titles from context, falls back to Speaker A/B/C.*

---

## 🛠️ Proposed Changes (Phase 3)

### 1. Backend API Server Components

#### ➕ [NEW] [tts_engine.py](file:///d:/Python%20Programs/myBIZcon/backend/app/services/tts_engine.py)
* Encapsulates the Google TTS (`gTTS`) and ElevenLabs API connectors.
* Exposes a method `generate_tts_audio(text: str, provider: str = "gtts") -> bytes` returning raw MP3 audio bytes.

#### ➕ [NEW] [search_copilot.py](file:///d:/Python%20Programs/myBIZcon/backend/app/services/search_copilot.py)
* Scans input text using regex/Gemini keyword extraction.
* Initiates background web searches and compiles neat summary bullets (fact cards).

#### 📝 [MODIFY] [requirements.txt](file:///d:/Python%20Programs/myBIZcon/backend/requirements.txt)
* Append `gTTS>=2.3.0` and library options for PC-side recordings.

#### 📝 [MODIFY] [main.py](file:///d:/Python%20Programs/myBIZcon/backend/app/main.py)
* Add `/api/v1/voice/tts` GET/POST endpoint to stream MP3 bytes.
* Add `/api/v1/meeting/upload` POST endpoint supporting multipart WAV file uploads for Gemini-powered diarization and scheduling.
* Add `/api/v1/copilot/search` POST endpoint to fetch facts for active messages.

---

### 2. PC Client Components

#### ➕ [NEW] [audio_recorder.py](file:///d:/Python%20Programs/myBIZcon/pc_client/audio_recorder.py)
* A threaded recorder utilizing `sounddevice`, `numpy`, and `wave` to record `.wav` files.
* Includes a fully functional `SyntheticAudioGenerator` fallback producing dynamic conversation-mimicking wave files in case audio libraries or devices are missing.

#### 📝 [MODIFY] [pc_desktop_client.py](file:///d:/Python%20Programs/myBIZcon/pc_client/pc_desktop_client.py)
* Replace mock recording controls with the new `audio_recorder.py` thread.
* Add a "Play suggested response" button next to translations that queries `/api/v1/voice/tts` and plays it via standard Windows media tools.
* Embed an asynchronous "Fact Bubble" overlay section displaying web search facts retrieved from `/api/v1/copilot/search`.

---

## 🔬 Verification Plan (Phase 3)

### Automated Tests
1. **Audio Recording Fallback Test**: Run `python audio_recorder.py` independently to verify standard library fallback behavior and generation of playable WAV files.
2. **Diarization API Test**: Post a multipart WAV file payload to `/api/v1/meeting/upload` and assert that the response contains Speaker-separated segments and automatic Calendar/Task JSON structures.
3. **TTS Stream Test**: Query `/api/v1/voice/tts?text=안녕하세요` and verify that the response header is `audio/mpeg` and plays audio cleanly.

### Manual Verification
1. Open the PC Desktop Client, click `🎙️ START MEETING CAPTURE`, let it run, then click `🛑 STOP & SAVE MINUTES`. Verify that a complete diarized Markdown file is generated and synced directly to Google Drive.
2. Click the transparent Windows subtitle overlay suggestion button and verify that the corresponding text-to-speech audio plays instantly.

---

### 🧬 Phase 4: Multi-Messenger Expansion & Hyper-Personalized RAG
*   KakaoTalk, Slack, and Telegram scraper adapters for both mobile and desktop.
*   Contextual RAG pipeline: Ingest historical transcripts from Google Drive, train embedding vectors, and personalize tone generation to sound exactly like the user.

---

## 🛠️ Git Synchronization & Execution Tracking Guidelines

To ensure robust progress tracking, error logging, and flexible design iterations:
1.  **Tracker Setup**: All workspace actions will be tracked in `d:\Python Programs\myBIZcon\mybizcon_tracker.json`. This tracker will include:
    *   `run_count`: Incrementing counter of steps executed.
    *   `current_stage`: Current phase of implementation.
    *   `last_commit_hash`: Git hash of the latest sync.
    *   `operations_log`: Cumulative array of steps, actions taken, code changes, and debug statuses.
2.  **Continuous Git Sync**:
    *   Before making significant changes, execute a `git pull` from the remote repository.
    *   After completing a discrete step or writing a component, execute `git add`, `git commit` (with detailed commit messages referencing step counts), and `git push` to `https://github.com/Gimsphil/myBIZcon.git`.

---

## ⚠️ User Review Required

> [!WARNING]
> ### 1. PC Audio Capturing (WASAPI Loopback)
> Windows loopback capture requires specialized PyAudio/SoundCard setups. We will supply detailed setup guidelines and zero-dependency mock inputs to ensure the PC Client works seamlessly on standard Windows environments.
