# 📋 Tasks: myBIZcon Development Roadmap - Phase 3 Focus

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

## Phase 3: Real-Time Audio Capture, Meeting Mode & Voice Pipeline (Completed)
- [x] Implement physical meeting audio recorder module (`pc_client/audio_recorder.py`)
- [x] Create Speaker Diarization logic utilizing Gemini multimodal audio upload (`backend/app/services/diarization_engine.py`)
- [x] Set up Whisper STT and voice services pipeline (`backend/app/services/voice_service.py`)
- [x] Develop Search-Assisted Web Copilot (`backend/app/services/copilot_search.py`)
- [x] Update PC Desktop Client interface and API integration (`pc_client/pc_desktop_client.py`)
- [x] Synchronize tasks and write walkthrough report

## Phase 3.5: Voice Optimization, VAD Noise Suppression & Gemini Emotion Analysis (Completed)
- [x] Implement first-order high-pass difference filter & dynamic RMS VAD noise gate in `audio_recorder.py`
- [x] Upgrade Gemini multimodal prompts in `diarization_engine.py` for acoustic diarization characteristics & emotion extraction
- [x] Enhance pc client GUI to show diarized emotion metadata
- [x] Write walkthrough report and push updates to Git

## Phase 4: Multi-Messenger & Personalization (RAG) (Completed)
- [x] Add KakaoTalk, Slack, and Telegram accessibility scraper configurations (adapters)
- [x] Set up local vector database pipeline (TF-IDF & Cosine Similarity vector space)
- [x] Implement historical transcript RAG indexer to adapt to user's personal writing style

## Phase 5: AI Reviewer CLI Auto-Approve Integration (Completed)
- [x] Formally appoint the AI Assistant as the Technical Reviewer & Auditor (검토자)
- [x] Integrate automatic approval bypass flags for local `agy` and `codex` CLIs
- [x] Establish single-point GitHub Push Gate restricting `agy`/`codex` commits
- [x] Develop high-fidelity PowerShell JSONL transcript parser
- [x] Create and persistently update `agent_dialogue_archive.md`
- [x] Synchronize all local logs, chronicle guides, and remote Git repository

## Phase 6: 보안 강화 · API 인증 · 통합 테스트 · 배포 준비 (In Progress)

### 🔐 Step 15 - AGY 담당: 보안 강화 (Security Hardening)
- [ ] FastAPI CORS 정책 강화: `allow_origins=["*"]` → 명시적 허용 도메인 화이트리스트
- [ ] `/workspace/index` (RAG 재인덱싱) 엔드포인트에 API Key 인증 미들웨어 추가
- [ ] `/voice/meeting` 엔드포인트 `file_path` 경로 traversal 방지 (Path Validation)
- [ ] `backend/app/config.py` 에 `SECRET_API_KEY` 환경변수 로드 추가

### 🧪 Step 16 - CODEX 담당: 통합 테스트 스위트 구축 (Integration Testing)
- [ ] `backend/tests/` 폴더 생성 및 `pytest` 기반 테스트 모듈 작성
- [ ] `test_relationship_engine.py`: BOSS/CLIENT/FAMILY/COWORKER 관계별 응답 생성 시나리오 테스트
- [ ] `test_rag_engine.py`: Mock Corpus 기반 TF-IDF 인덱싱 및 Cosine Similarity 검색 유효성 검증
- [ ] `test_api_endpoints.py`: FastAPI TestClient 기반 엔드포인트 smoke test (200 OK 검증)
- [ ] `mock_test_client.py` 결과와의 일관성 크로스 검증 보고서 작성

### 📦 Step 17 - AGY 담당: PC Client 배포 준비 (PyInstaller EXE)
- [ ] `pc_client/` 에 `pyinstaller_build.spec` 작성
- [ ] PyInstaller 단일 EXE 빌드 스크립트 (`build_exe.bat`) 생성
- [ ] EXE 빌드 전 의존성 freezing 점검 (`requirements.txt` 갱신)

### 📝 Step 18 - ANTIGRAVITY: 검토·승인·커밋·푸시
- [ ] Steps 15-17 코드 검수 및 품질 감사
- [ ] `mybizcon_tracker.json` Steps 15-17 기록 업데이트
- [ ] `mybizcon_chronicle.md` Phase 6 진행 기록
- [ ] GitHub 커밋 & 푸시 (Push Gate 준수)

