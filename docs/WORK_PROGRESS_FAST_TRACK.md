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

## 다음 작업

1. 전체 테스트 실행 및 실패 수정
2. Codex 검토 재실행
3. Agy CLI에는 Android build 최소 통과선 또는 문서/인코딩 정리 중 작은 단위 작업 지시
4. 검수 후 커밋 및 GitHub push
