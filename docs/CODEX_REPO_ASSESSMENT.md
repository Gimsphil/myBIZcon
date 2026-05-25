# CODEX 저장소 평가서 - myBIZcon

작성일: 2026-05-25  
범위: `README.md`, `implementation_plan.md`, `NEXT_SESSION_START.md`, `backend/app`, `backend/tests`, `pc_client`, `android`, `templates`, tracker/roadmap 문서  
원칙: 기능 코드 변경 없음, 외부 API/시크릿 사용 없음

## 1. 제품 요약

myBIZcon은 메시지 앱, PC 알림/회의, 음성 통화를 수집해 번역, 톤별 답장 제안, 회의록, 업무/일정/아카이브 동기화를 제공하려는 개인 비즈니스 AI 어시스턴트이다. 현재 구현은 실제 외부 서비스 연동보다 로컬 FastAPI, Tkinter PC 클라이언트, Android Accessibility 서비스, 오프라인 mock/fallback 흐름을 중심으로 MVP 검증에 맞춰져 있다.

핵심 기능은 관계별 답장 생성(`BOSS`, `CLIENT`, `COWORKER`, `FAMILY`), Slack/KakaoTalk/Telegram/WhatsApp 플랫폼 어댑터, 로컬 Markdown 백업 기반 TF-IDF RAG, 음성 녹음/회의록 mock 파이프라인, Google Workspace mock sync이다.

## 2. 현재 아키텍처

- Backend: FastAPI `backend/app/main.py`가 채팅, Workspace, RAG reindex, 음성, STT/TTS, copilot search endpoint를 제공한다.
- Config: `backend/app/config.py`에서 `GEMINI_API_KEY`, `SECRET_API_KEY`, `ALLOWED_ORIGINS`, `SAFE_RECORDINGS_ROOT`를 환경 변수로 로드한다.
- Services: `relationship_engine.py`, `rag_engine.py`, `google_workspace.py`, `diarization_engine.py`, `voice_service.py`, `copilot_search.py`로 기능이 분리되어 있다.
- Tests: `backend/tests`는 API 보안 smoke, RAG, relationship engine을 pytest로 검증한다.
- PC Client: `pc_client/pc_desktop_client.py`는 Tkinter 대시보드, 오버레이, 녹음 제어, backend 호출을 담당한다. `audio_recorder.py`는 PyAudio가 없으면 simulated WAV를 생성한다.
- Android: Kotlin Accessibility 서비스가 메시지 노드를 backend로 전송하고 overlay service가 추천 답장을 표시한다.
- Templates: `templates/relationship_prompts.py`에 관계별 system prompt가 있다.
- Tracking: `mybizcon_tracker.json`, `task.md`, `walkthrough.md`, `mybizcon_chronicle.md`, `NEXT_SESSION_START.md`가 진행 상태를 기록한다.

## 3. 완료/진행 단계

- Phase 1-4: 계획서 기준 완료. Git/tracker, prompt template, Android/PC MVP, FastAPI Workspace mock, 음성/회의 mock, RAG/멀티 메신저 어댑터가 구현되어 있다.
- Phase 5: AI reviewer/agy/codex 역할과 push gate 문서화 완료로 기록되어 있으나, 위험한 승인 bypass 문구는 운영 기본값이 아니라 통제된 로컬 절차로 취급해야 한다.
- Phase 6: 보안 강화 완료. CORS whitelist, `/workspace/index` API key, `/voice/meeting` path guard, pytest suite, PyInstaller 준비가 반영되어 있다.
- Phase 7: `/health`, `.env.example`, 테스트 감사 반영, resume kit 준비 완료로 tracker에 기록되어 있다.
- 문서 불일치: `implementation_plan.md`는 Phase 4 진행 중으로 오래되어 있고, `task.md`/tracker는 Phase 7 완료에 가깝다. README도 실제 디렉터리보다 축약되어 있다.

## 4. 테스트/빌드 명령 및 현재 리스크

검증한 명령:

```powershell
python -m compileall -f -q backend pc_client templates mock_test_client.py
python -m pytest backend\tests --tb=short -q
```

현재 결과:

- Python compile: 통과
- Backend tests: `46 passed in 0.76s`
- Git: local `HEAD`와 `origin/main`이 `820715f421c3d512c1119a33f8b24e64451ba847`로 일치
- 작업트리: `docs/` 및 `__pycache__/` 계열이 untracked

추가 빌드/실행 명령:

```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
python pc_client\pc_desktop_client.py
pc_client\build_exe.bat
android\build_apk.bat
```

주요 리스크:

- PC client 계약 불일치: 서버 상태 체크가 `/api/v1`에 GET을 보내지만 backend에는 해당 root endpoint가 없다. `/health`로 바꿔야 한다.
- PC client RAG reindex 실패 가능성: `/workspace/index`는 `X-API-Key`가 필수인데 PC client는 header를 보내지 않는다.
- PC voice 경로 불일치: PC 녹음 파일은 기본적으로 현재 작업 폴더의 `meeting_capture.wav`에 저장되지만 backend 기본 `SAFE_RECORDINGS_ROOT`는 `./recordings`라 `/voice/meeting`에서 403이 날 수 있다.
- Android native build 미완성 가능성: manifest가 `MainActivity`, `@mipmap/ic_launcher`, `@string/app_name`, `@style/Theme.MyBIZcon`을 참조하지만 현재 파일 목록에는 관련 리소스/Activity가 없다.
- Android overlay injection 설계 문제: `TranslationOverlayService`가 `MyBIZconAccessibilityService()`를 직접 생성해 `injectSuggestedReply()`를 호출한다. 실제 활성 AccessibilityService 인스턴스와 연결되지 않는다.
- `build_apk.bat`의 mock APK 생성은 실제 APK 검증을 대체하지 못한다.
- `pc_client/requirements_pc.txt`의 `tkinter`는 pip 패키지가 아니라 Python 설치 구성 요소라 `pip install -r`에서 실패할 수 있다.
- 다수 문서/문자열에 mojibake가 있어 한국어 프롬프트 품질, 리뷰 가능성, Android UI 텍스트 품질에 영향을 준다.
- `copilot_search.py`, STT/TTS/Gemini 경로는 키가 있으면 외부 API를 호출한다. 테스트/리뷰 기본값은 키 없는 mock 모드로 고정해야 한다.

## 5. Agy 1차 코딩용 다음 3개 station-sized 작업

1. PC client와 backend API 계약 정렬  
   `/health` 상태 체크로 변경, `/workspace/index`에 `X-API-Key` header 지원, 녹음 저장 경로를 `recordings/meeting_capture.wav`로 정렬, 관련 backend API smoke test 추가.

2. Android native build 최소 통과선 만들기  
   `MainActivity.kt`, `strings.xml`, theme, launcher resource placeholder를 추가하고 `TranslationOverlayService`와 AccessibilityService 간 통신을 broadcast/bound service/shared singleton 중 하나로 정리한다. mock APK 대신 실제 `gradlew assembleDebug` 성공을 기준으로 기록한다.

3. 문서/인코딩 정리와 tracker 동기화  
   `implementation_plan.md`, README, `task.md`, `NEXT_SESSION_START.md`의 phase 상태를 Phase 7 기준으로 맞추고, mojibake가 사용자 노출 prompt/mock 텍스트에 남아 있는 파일 목록을 정리한 뒤 우선순위대로 복구한다.

## 6. GitHub 동기화 권장사항

- `.gitignore`에 `__pycache__/`, `*.pyc`, `pc_client/build/`, `pc_client/dist/`, Android build 산출물, mock APK, 로컬 녹음 파일, `drive_backups/`, `.env`, credential/token 파일을 명시한다.
- 이번 문서 변경은 기능 코드와 분리해 별도 커밋으로 남긴다.
- push 전 표준 확인 순서: `git status --short --branch`, `git rev-parse HEAD`, `git ls-remote origin refs/heads/main`, `compileall`, `pytest`.
- tracker의 `last_commit_hash`는 실제 push가 끝난 뒤 갱신한다. 문서상 hash와 GitHub hash가 달라지는 상태를 오래 두지 않는다.
- agy/codex는 코딩/검수 역할로 제한하고, 원격 push는 지정된 push gate가 수행한다는 규칙을 계속 유지한다.
- GitHub에는 secrets를 올리지 않는다. `.env.example`만 유지하고 실제 키는 로컬 환경 변수 또는 비추적 `.env`에 둔다.
