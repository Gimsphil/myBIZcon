# 📜 myBIZcon Project Chronicle: Ultimate Development Log & Replication Guide

This chronicle serves as a permanent, exhaustive development journal and project blueprint for **myBIZcon (Universal AI Business Assistant)**. It captures every single user requirement, architectural decision, code change, dialogue detail, and environment setup instruction. 

If this repository is cloned onto **any other PC** or opened by **any other developer/AI agent**, this document guarantees that the development context is fully aligned and can be resumed immediately without discrepancies.

---

## 🌐 1. Project Overview & Core Concept

**myBIZcon** is a personal business intelligence system that bridges communication channels with the **Google Workspace Ecosystem** (Calendar, Tasks, Keep, Drive, Docs) using Google Gemini 1.5 Flash.

### Key Goals & Features
1.  **AI Translation & Tone Recommendations**: Real-time message parsing with 3 tailored suggested replies depending on the recipient profile (`BOSS`, `CLIENT`, `COWORKER`, `FAMILY`). Supports direct chats and **Multi-Party Group Conversations**.
2.  **Meeting Mode & Call Copilot**: High-fidelity audio capturing during VoIP calls or in-person physical meetings, **Speaker Diarization** (separating voices), automated **Meeting Minutes** generation, and direct Workspace syncing.
3.  **Google Sync & Archival**: Instantly schedules extracted appointments to Google Calendar, adds To-Dos to Tasks, and exports clean Markdown transcripts directly to Google Drive.
4.  **Multi-Platform Ubiquity**:
    *   **Android Mobile Client (APK)**: accessibility service scrapers, background system overlays, call hooks.
    *   **PC Desktop Client (EXE)**: Tkinter-based dark theme dashboard, WASAPI loopback audio record pipelines, and transparent, draggable Windows subtitle overlays.

---

## ⚖️ 2. Core Technical Decisions & Feasibility Evaluations

### 2.1 AI Model: Google Gemini 1.5 Flash vs. Meta Llama 3
*   **Decision**: **Google Gemini 1.5 Flash** is chosen as the primary engine.
*   **Rationale**: Gemini offers a massive 2 million token context window (crucial for long meeting transcripts and group chats), native Google Workspace tool-calling integrations, superior Korean business etiquette comprehension, and low-latency API generation at a fractional cost.
*   **Compliance Design**: The backend uses an **Adapter Pattern** (abstracted LLM caller class) so the system can seamlessly switch to an on-premise hosted **Meta Llama 3** engine in the future for private corporate compliance.

### 2.2 Platform: Android & Windows PC Co-Existence
*   **Decision**: **Android Kotlin Client** + **Python Tkinter Windows PC Client**.
*   **Rationale**: iOS strictly forbids screen scraping accessibility services or system audio hooks. Android allows both using custom `AccessibilityService` and `MediaProjection` APIs. To provide a desktop counterpart, a local Windows PC Client has been developed using Python Tkinter, leveraging loopback audio capture for Teams/Zoom calls and transparent hover overlays.

---

## 📁 3. Project Directory Structure

```
myBIZcon/
├── README.md                ← Project introduction & directory layout
├── implementation_plan.md   ← Approved multi-phase engineering plan
├── task.md                  ← Public checkable TODO roadmap
├── walkthrough.md           ← Achievements and validation walkthrough logs
├── mybizcon_tracker.json    ← Structured execution JSON logs (run count, commit hashes)
├── mybizcon_chronicle.md    ← This document (Full dialogs, codebases, replication steps)
├── pc_client/
│   ├── audio_recorder.py     ← Multi-threaded mic & loopback recorder with simulated fallback [NEW]
│   └── pc_desktop_client.py ← Tkinter Windows Desktop Dashboard & subtitle overlays
├── backend/
│   ├── requirements.txt     ← FastAPI python dependencies
│   └── app/
│       ├── __init__.py
│       ├── config.py        ← Environment variables (Gemini, Google OAuth paths)
│       ├── main.py          ← FastAPI Server routing all Chat/Calendar/Tasks/Backup APIs
│       └── services/
│           ├── google_workspace.py   ← Syncs Drive Markdown backup, Tasks, Calendar
│           ├── relationship_engine.py ← REST Gemini connector with offline fallback
│           ├── voice_service.py      ← STT (Whisper API) & TTS (ElevenLabs API) connector [NEW]
│           ├── diarization_engine.py  ← Gemini multimodal diarizer and automator [NEW]
│           └── copilot_search.py     ← Background Search-Assisted Web Copilot facts engine [NEW]
├── templates/
│   └── relationship_prompts.py       ← Boss, Client, Coworker, Family templates
└── android/                 ← Native Kotlin Gradle Project layout
    ├── build.gradle
    ├── settings.gradle
    ├── build_apk.bat        ← Zero-click Windows compiling batch script
    └── app/
        ├── build.gradle
        └── src/main/
            ├── AndroidManifest.xml   ← Requests overlay, accessibility, mic permissions
            ├── res/xml/
            │   └── accessibility_service_config.xml ← Package bindings (WhatsApp, Slack, etc.)
            └── java/com/mybizcon/client/
                ├── MyBIZconAccessibilityService.kt   ← Mobile WhatsApp scraping & text injector
                └── TranslationOverlayService.kt     ← Mobile floating translation & suggestions
```

---

## 📝 4. Detailed Step-by-Step Development Chronicle

### 🏃 Phase 1: Git, Tracker Setup & Foundations (Step 1 - 5)
*   **Action**: Created `myBIZcon` folder at `D:\Python Programs\myBIZcon`, initialized git, and added the remote `https://github.com/Gimsphil/myBIZcon.git`. Pushed initial README, Task, and Walkthrough blueprints.
*   **Feats Added**:
    *   `relationship_prompts.py`: Formalized system prompt structures for different personas (Boss, Client, Coworker, Family). Added specific schemas for multi-party group chats and meeting modes.
    *   `mock_test_client.py`: Created an interactive zero-dependency REST simulator. Directly queries the Google Gemini REST API via `urllib` without needing external Python SDKs.

### 📦 Phase 2: MVP Development - Android & FastAPI Sync (Step 6)
*   **Action**: Built the core mobile accessibility scraping engine and FastAPI server gateways.
*   **Feats Added**:
    *   `accessibility_service_config.xml`: Configured Android Accessibility bound packages (`com.whatsapp`, `com.kakao.talk`, `com.Slack`, `org.telegram.messenger`).
    *   `MyBIZconAccessibilityService.kt`: Scrapes incoming chat nodes, identifies sender names, groups layouts, sends HTTP POST payloads to backend, and handles Human-in-the-Loop text injection into input entries.
    *   `TranslationOverlayService.kt`: Semi-transparent background floating system window for Android. Shows translations in 3 layout modes and supplies response cards.
    *   `backend/`: Created a FastAPI API Server (`main.py`, `config.py`).
        *   `google_workspace.py`: Integrates automated Google Calendar scheduling, Google Tasks, and one-click Google Drive Markdown transcript backups.
        *   `relationship_engine.py`: Connects to Gemini REST, translating messages and recommending replies.

### 🖥️ Phase 2.5: PC Client & APK Build Setup (Step 7 - 8)
*   **Action**: Built desktop version and compiled APK packaging tools based on user's new pivot requests.
*   **Feats Added**:
    *   `pc_desktop_client.py`: Dark-themed slate Tkinter GUI. Implements PC audio capture toggle, live dashboard, meeting minutes sync pipelines, and a **draggable, transparent Windows Subtitle Overlay** that floats over active desktop apps.
    *   `android/build_apk.bat`: Double-click batch script for compiling Android Kotlin app to APK using Gradle or local fallback. Supported by full `build.gradle` structures.

### 🎙️ Phase 3: Real-Time Audio Capture, Meeting Mode & Voice Pipeline (Step 10)
*   **Action**: Coded complete audio capture recorder, Whisper & ElevenLabs voice pipeline, Gemini native multimodal speaker diarization (User, Speaker A, Speaker B), Search-Assisted Web Copilot background facts engine, and integrated everything into the desktop GUI and FastAPI server.
*   **Feats Added**:
    *   `audio_recorder.py`: Multi-threaded recorder using PyAudio for microphone and WASAPI loopback call recording. Features a fully zero-dependency simulation fallback producing robust WAV buffers in dry environments.
    *   `voice_service.py`: Coded STT (Whisper API) and TTS (ElevenLabs API) connectors with complete offline test mocks.
    *   `diarization_engine.py`: Sends base64-encoded WAV recording directly to Gemini 1.5 Flash's multimodal audio context. Gemini parses, diarizes speaker dialogue, and maps structured action items to Calendar, Tasks, and Drive.
    *   `copilot_search.py`: Background DuckDuckGo/Google search crawler providing dynamic business facts and contract templates to the GUI overlay.
    *   `pc_desktop_client.py` and `main.py` Updates: Registered and integrated all new Phase 3 endpoints. Added a beautiful Search-Assisted Web Copilot facts box in the PC GUI.

---

## 💻 5. PC Replication & Setup Instructions (Run on Any PC)

To continue development on **any new machine**, simply execute the following steps:

### Prerequisites
1.  **Python 3.8+** (Installed in Path).
2.  **Git** (Installed in Path).
3.  **Android Studio** (Optional, only needed if modifying native Kotlin code).

### Step 1: Clone the Repository
```bash
git clone https://github.com/Gimsphil/myBIZcon.git
cd myBIZcon
```

### Step 2: Set Up Backend Server
1.  Navigate to the backend folder:
    ```bash
    cd backend
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure environment variables:
    *   Windows CMD: `set GEMINI_API_KEY=your_google_gemini_api_key`
    *   Windows PowerShell: `$env:GEMINI_API_KEY="your_google_gemini_api_key"`
4.  Launch the FastAPI server:
    ```bash
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

### Step 3: Run the PC Desktop Client
1.  Open a new terminal window and navigate to the pc_client folder:
    ```bash
    cd pc_client
    ```
2.  Run the Tkinter Desktop Application:
    ```bash
    python pc_desktop_client.py
    ```

### Step 4: Compile the Android Client (APK)
1.  Navigate to the android folder:
    ```bash
    cd android
    ```
2.  Double-click `build_apk.bat` or run:
    ```cmd
    build_apk.bat
    ```
    *This compiles the Kotlin app into a debug APK (`app-debug.apk`) inside the `app\build\outputs\apk\debug\` folder.*
