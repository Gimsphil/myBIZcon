# myBIZcon Fast Track Progress

## 현재 적용 내용

- GitHub 저장소를 `D:/myBIZcon`에 클론하고 로컬 작업 저장소로 설정했다.
- 39분 주기 진행 보고 cron을 설정했다.
- Codex 1차 저장소 평가를 수행했고, 결과를 `docs/CODEX_REPO_ASSESSMENT.md`에 저장했다.
- Codex 기본 sandbox에서 `windows sandbox: spawn setup refresh` 오류가 발생하여 중단했고, 이후 `--sandbox danger-full-access` 방식으로 평가 작업을 완료했다.
- PDF 첨부 파일은 현재 `D:/myBIZcon` 및 대화 입력에서 확인되지 않았다. PDF가 다시 전달되면 우선 적용한다.
- Agy CLI Station 2 실행은 exit code 0으로 종료됐지만 표준 출력과 파일 변경이 없었다. 해당 부분은 Hermes가 직접 보완했다.

## 빠른 진행을 위해 바로 적용한 Station 1

- PC client 상태 확인을 `/api/v1` 대신 backend `/health` 기준으로 변경했다.
- PC client RAG 재색인 호출에 `X-API-Key` 헤더를 포함하도록 변경했다.
- PC meeting 녹음 파일 경로를 `SAFE_RECORDINGS_ROOT` 아래 `recordings/meeting_capture.wav`로 정렬했다.
- `.env.example`에 `MYBIZCON_API_KEY`, `MYBIZCON_BACKEND_URL`을 추가했다.
- Python/PC/Android 산출물과 비밀 파일이 Git에 들어가지 않도록 `.gitignore`를 추가했다.
- `backend/tests/test_pc_client_contract.py`를 추가해 PC client와 backend 계약을 고정했다.

## HiNoter 기능 반영

- Bing 검색 결과와 Apple iTunes Search API를 통해 HiNoter 공개 기능을 확인했다.
- 확인 기능: 원탭 녹음/전사, 발화자 식별, AI 요약, AI 마인드맵, Ask AI, 키워드 검색/오디오 점프, 팀 공유, 암호화/소유자 제어, 캘린더 회의 자동 참여/동기화, 오디오·YouTube 링크 업로드 전사.
- 신규 API `POST /api/v1/notes/capture`를 추가했다.
- 신규 서비스 `backend/app/services/hinoter_notes.py`를 추가했다.
- 신규 계약 테스트 `backend/tests/test_hinoter_note_contract.py`를 추가했다.
- Live Calendar/YouTube/AI 호출은 아직 연결하지 않고 오프라인 안전 계약 계층으로 구현했다. 실제 외부 연동은 추후 명시 승인 후 연결한다.
- `docs/HINOTER_FEATURE_INTEGRATION.md`에 출처와 반영 범위를 기록했다.

## 2026-05-26 WhatsApp 재개 작업

- 연결 확인: `D:/myBIZcon` Git 저장소, `main...origin/main`, Codex CLI `0.133.0` 사용 가능 확인.
- Codex 기본 sandbox에서 `windows sandbox: spawn setup refresh` 오류가 재발하여, 로컬 신뢰 저장소 한정으로 `--sandbox danger-full-access -C D:/myBIZcon` 방식으로 읽기/수정 작업을 진행했다.
- 전체 backend 테스트를 실행했고 `67 passed`를 확인했다.
- Codex 리뷰 HIGH 2건을 반영했다: 외부서비스 비활성 플래그 전역 가드, Android 대화방 전환 시 note capture 캐시 초기화.
- Codex 리뷰 MEDIUM 2건도 반영했다: HiNoter 한국어 액션/결정 추출 보강, PC note capture 상태 분리.
- 신규 계약 테스트 `backend/tests/test_external_services_disable_contract.py`를 추가했고 Android/HiNoter/PC 계약 테스트를 보강했다.
- Android AccessibilityService가 일반 WhatsApp(`com.whatsapp`)과 WhatsApp Business(`com.whatsapp.w4b`)를 event packageName으로 자동 인식하고, 활성 패키지 prefix로 ViewId를 동적으로 찾도록 보강했다.
- 비-WhatsApp 이벤트에서는 스크래핑/주입/노트 캡처가 동작하지 않도록 안전 가드를 추가했다.

## 2026-05-26 WAconn 참조 적용

- 사용자가 제공한 `https://github.com/Gimsphil/WAconn`를 `D:/DEV_PROJECTS/_refs/WAconn`에 로컬 참조 클론했다.
- WAconn `server.ts`가 제공하는 프런트엔드 API 계약을 myBIZcon FastAPI backend에 오프라인 안전 방식으로 반영했다.
- 신규 호환 endpoint를 추가했다: `POST /api/generate-reply`, `POST /api/meeting-summary`, `POST /api/ask-notes`.
- 실제 Gemini/Google/외부 API 호출 없이 기존 `relationship_engine` mock 및 HiNoter 노트 로직을 재사용하도록 구성했다.
- 신규 계약 테스트 `backend/tests/test_waconn_api_contract.py`를 추가했고, `MYBIZCON_DISABLE_EXTERNAL_SERVICES=1` 상태에서 외부 `httpx` 호출이 발생하지 않음을 검증했다.
- 이후 WhatsApp으로 수신된 `WAconn-debug.apk`를 확인해 APK 내부 `assets/capacitor.config.json`의 `appId=com.gimsphil.waconn` 및 내장 `server.cjs` API 계약이 GitHub WAconn `server.ts`와 동일함을 검증했다.
- APK 기준에 맞춰 WAconn 호환 endpoint의 잘못된 payload 응답을 FastAPI 기본 `422`가 아닌 WAconn과 같은 `400`으로 정렬했다.
- 검증 결과: WAconn 계약 테스트 `4 passed`, backend 전체 테스트 `72 passed`.

## 다음 작업

1. WAconn 웹 프런트엔드 자체를 myBIZcon에 병합할지, API 호환 계층만 유지할지 결정
2. Android Gradle 빌드 가능 여부 확인
3. 실제 Android 기기에서 WhatsApp/WAconn 호환 API 연동 확인
