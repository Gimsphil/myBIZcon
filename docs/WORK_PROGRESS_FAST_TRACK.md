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

## 다음 작업

1. 전체 테스트 실행 및 실패 수정
2. Codex 검토 재실행
3. Agy CLI에는 Android build 최소 통과선 또는 문서/인코딩 정리 중 작은 단위 작업 지시
4. 검수 후 커밋 및 GitHub push
