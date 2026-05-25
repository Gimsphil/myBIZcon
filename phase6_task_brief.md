# 📋 Phase 6 작업 지시서 (Work Order)
발행: **Antigravity** (기술 검토자 · 감수자)  
일시: 2026-05-25  
상태: 🔴 즉시 실행

---

## 🔴 AGY CLI - Step 15: 보안 강화 (Security Hardening)

아래 파일들을 순서대로 수정하시오. **GitHub 커밋/푸시 금지. 코딩만 수행.**

### 📝 수정 대상 1: `backend/app/config.py`
- `SECRET_API_KEY` 환경변수를 로드하는 설정 항목 추가
- 기본값: `"dev-insecure-key"` (개발 환경 fallback)

### 📝 수정 대상 2: `backend/app/main.py`
1. **CORS 강화**: `allow_origins=["*"]` → `allow_origins=settings.ALLOWED_ORIGINS` (환경변수 기반 리스트)
2. **API Key 인증 미들웨어 추가**: `X-API-Key` 헤더 검증 dependency 구현
   - `/workspace/index` 엔드포인트: API Key 필수 (의도치 않은 외부 RAG 재인덱싱 방지)
3. **Path Traversal 방지**: `/voice/meeting` 에서 `file_path`가 프로젝트 루트 내에 있는지 검증
   ```python
   # 예시 패턴
   import os
   safe_root = os.path.abspath("./recordings")
   abs_path = os.path.abspath(payload.file_path)
   if not abs_path.startswith(safe_root):
       raise HTTPException(status_code=403, detail="Invalid file path.")
   ```

### 📝 수정 대상 3: `backend/requirements.txt`
- `python-dotenv` 추가 (환경변수 `.env` 파일 로드용)

---

## 🔵 CODEX CLI - Step 16: 통합 테스트 스위트 구축 (Integration Testing)

아래 파일들을 신규 생성하시오. **GitHub 커밋/푸시 금지. 코딩 및 검수만 수행.**

### 📁 신규 생성: `backend/tests/` 디렉토리

#### `backend/tests/__init__.py`
- 빈 파일 (Python 패키지 선언)

#### `backend/tests/test_rag_engine.py`
```python
# pytest 기반 RAG 엔진 테스트
# 1. reindex_corpus() 호출 후 corpus가 비어있지 않음을 검증
# 2. retrieve_personal_examples("NDA 계약서")가 string을 반환함을 검증
# 3. _cosine_similarity({}, {}) == 0.0 엣지케이스 검증
# 4. _tokenize("Hello World 한국어") 결과가 비어있지 않음을 검증
```

#### `backend/tests/test_api_endpoints.py`
```python
# FastAPI TestClient 기반 smoke test
# 1. GET "/" → 200 OK, "status": "ONLINE" 검증
# 2. POST "/api/v1/copilot/search" with {"query": "회의"} → 200 검증
# 3. POST "/api/v1/workspace/index" → API Key 없으면 401/403, 있으면 200
```

#### `backend/tests/test_relationship_engine.py`
```python
# 관계 엔진 테스트 (Mock Gemini 응답 사용)
# 1. BOSS 관계 시나리오에서 응답이 존중 표현("부장님") 포함 검증
# 2. FAMILY 관계에서 친근한 반말 패턴이 결과에 반영되는지 확인
# 3. platform="KAKAO" 시 KakaoTalk 어댑터 스타일이 적용되는지 검증
```

---

## 🟡 AGY CLI - Step 17: PC Client 배포 준비 (PyInstaller EXE)

### 📝 신규 생성: `pc_client/pyinstaller_build.spec`
- `pc_desktop_client.py`를 단일 EXE로 패키징
- `--onefile`, `--windowed`, `--name myBIZcon` 옵션 반영

### 📝 신규 생성: `pc_client/build_exe.bat`
```batch
@echo off
echo [myBIZcon] Starting PyInstaller EXE build...
cd /d %~dp0
pip install pyinstaller
pyinstaller pyinstaller_build.spec --clean
echo [myBIZcon] Build complete. Check dist/ folder.
pause
```

### 📝 갱신: `pc_client/requirements_pc.txt`
- `pyinstaller>=5.0` 추가

---

## ⚠️ 공통 규칙 (AGY & CODEX 양측)
1. **Git commit/push 절대 금지** - 검토 후 Antigravity가 직접 처리
2. 모든 코드는 `# -*- coding: utf-8 -*-` 헤더 포함
3. 함수/클래스에 docstring 필수
4. 작업 완료 후 완료 메시지를 화면에 출력할 것

---
*이 지시서는 Antigravity (AI 기술 검토자)가 공식 발행한 Phase 6 Work Order입니다.*
