# HiNoter 기능 벤치마크 반영 메모

## 확인한 공개 기능 출처
- Bing 검색 결과: Google Play/App Store의 `HiNoter - AI Note Taker` 설명 요약
- Apple iTunes Search API: `HiNoter - Al Note Taker`, version 4.0.1, release notes `Calendar sync is now available for all users`

## myBIZcon에 반영할 기능 범위
HiNoter가 공개 설명에서 강조하는 기능을 myBIZcon의 회의/통화/노트 모드에 포함한다.

1. 원탭 녹음 및 AI 전사
2. 회의/강의/인터뷰 자동 녹취 정리
3. 발화자 식별 및 발화자별 섹션화
4. AI 요약
5. AI 마인드맵 생성
6. 녹음/노트에 대해 Ask AI 질의응답
7. 키워드 검색으로 해당 오디오 구간으로 점프 가능한 searchable moments
8. 팀 공유용 Markdown 공유 페이로드
9. 사용자 선택 기반 공유 및 암호화 플래그
10. 캘린더 회의 자동 참여/동기화 메타데이터
11. 오디오 파일 또는 YouTube 링크 전사 입력 메타데이터

## 구현 상태
- 신규 서비스: `backend/app/services/hinoter_notes.py`
- 신규 API: `POST /api/v1/notes/capture`
- 신규 계약 테스트: `backend/tests/test_hinoter_note_contract.py`

## 안전 설계
- 현재 구현은 오프라인 안전 계약 계층이다.
- API 자체는 실제 Google Calendar, YouTube, 외부 AI API를 호출하지 않는다.
- Live 연동은 추후 명시 승인 후 `google_workspace`, YouTube transcript/import, Gemini summarization 단계에 연결한다.
