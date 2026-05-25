# 📋 Tasks: myBIZcon Development Roadmap

## Phase 1: Git, Tracker Setup & Foundations (Completed)
- [x] Create `myBIZcon` subfolder in the workspace `d:\Python Programs\myBIZcon`
- [x] Initialize Git repository in the `myBIZcon` folder
- [x] Connect remote `https://github.com/Gimsphil/myBIZcon.git`
- [x] Push approved `implementation_plan.md` and initial tracker to GitHub
- [x] Create the cumulative execution history tracker `mybizcon_tracker.json`
- [x] Write the core relationship prompt templates (`BOSS`, `CLIENT`, `COWORKER`, `FAMILY`)
- [x] Implement a simulation/mock script to test relationship prompts and tone generation

## Phase 2: MVP Development - WhatsApp Message Integration & Google Sync (Completed)
- [x] Build Android Accessibility Service mock-up configurations
- [x] Design group conversation parser structure (supporting multiple sender IDs)
- [x] Design the floating translation Overlay layout configuration
- [x] Construct FastAPI backend hooks for Google Workspace (Calendar, Tasks, Drive)
- [x] Develop one-click Markdown serialization to Google Drive

## Phase 2.5: PC Desktop Client Development & APK Build Pipeline (Completed)
- [x] Build Tkinter-based PC Desktop Client Dashboard and layout
- [x] Implement floating transparent Windows translation overlays
- [x] Create system loopback audio capture integration
- [x] Setup Android APK Gradle build scripts and compilation pathways

## Phase 3: Real-Time Audio Capture, Meeting Mode & Voice Pipeline (Planning & In Progress)
- [/] Implement physical meeting audio recorder module
- [/] Create Speaker Diarization logic (distinguishing Speaker A, B, and User)
- [/] Set up Whisper STT and Gemini translation pipeline
- [/] Set up TTS voice generation pipeline (ElevenLabs or Google TTS)
- [/] Develop Search-Assisted Web Copilot (background search during meetings/chats)

## Phase 4: Multi-Messenger & Personalization (RAG)
- [ ] Add KakaoTalk, Slack, and Telegram accessibility scraper configurations
- [ ] Set up local vector database pipeline (Chroma/FAISS)
- [ ] Implement historical transcript RAG indexer to adapt to user's personal writing style
