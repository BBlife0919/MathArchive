# Next.js가 아닌 React(Vite) + FastAPI 이관 — 1단계 진행 상황

기존 Streamlit 앱(`app/`)이 느리고 무거워서 이관 결정. Next.js는 배제하고
React(Vite) 프론트 + FastAPI(Python) 백엔드 단일 구성으로 진행 중. 배경·설계
전체는 `~/.claude/plans/smooth-percolating-journal.md` 참고.

**절대 원칙**: `app/`(기존 Streamlit)은 이 작업 중 전혀 수정하지 않는다.
`streamlit run app/main.py`로 계속 병행 운영 가능해야 함. `app/pdf_engine.py`는
재작성 없이 그대로 import 해서 재사용.

## 1단계 범위 진행 상황 (2026-08-06 기준)
- [x] M0: `backend/`(FastAPI) + `frontend/`(Vite+React) 스켈레톤
- [x] M1: `/api/filters`, `/api/questions/search`, `/api/questions/by-ids`
- [x] M2: `/api/auth/{signup,login,logout,me}` — 기존 HMAC 세션 토큰을 HTTP 쿠키로
- [x] M3: `/api/exam/pdf` — `pdf_engine.generate_exam_pdf()` 그대로 호출, 기존 Streamlit 결과물과 **픽셀 단위 완전 동일** 확인
- [x] M4: 로그인/회원가입/승인대기 화면
- [x] M5: 필터 사이드바(지역/학교/학년/년도/학기/중간·기말/단원 계층/난이도/유형/키워드) + 빠른검색 + 문제카드(수식·이미지·보기박스) + 페이지네이션
- [x] M6: 선택(장바구니) — `SelectionContext`(localStorage 동기화), 담기/제거, "전체(N)→시험지" 일괄담기
- [x] M7: 시험지 미리보기 + PDF 다운로드 — 브라우저 실제 다운로드까지 확인
- [ ] M8: 파리티 점검 + `/근본` 5회 검수 + 커밋 (진행 중)

**1단계에서 의도적으로 제외**: 미니테스트 자동생성, 교재 디자인모드(사선표지 등),
관리자/클리닉/학생카드 등 다른 Streamlit 페이지. 전부 2단계 이후.

## 로컬 실행 방법
```bash
# 백엔드 (루트 .env 의 SUPABASE_DB_URL 등을 그대로 읽음)
python3 -m uvicorn backend.app.main:app --reload --port 8000

# 프론트 (별도 터미널)
cd frontend && npm run dev -- --port 5173
```
- `SUPABASE_DB_URL` 이 설정돼 있으면 운영 Postgres, 없으면(unset) 로컬 `db/mathdb.sqlite` 사용 (기존 `app/db.py` 동작 그대로).
- `frontend/.env` 에 `VITE_API_BASE_URL=http://localhost:8000` 고정 (커밋됨, 시크릿 아님).
- 기존 `streamlit run app/main.py --server.port 8501` 과 동시에 띄워서 대조 가능.

## 재사용 매핑 (핵심)
- `backend/app/legacy_bridge.py` 가 `app/` 를 `sys.path` 에 넣어 `db.py`/`curriculum.py`/`pdf_engine.py`/`auth.py`/`main.py` 를 그대로 import.
- `backend/app/services/content_parser.py` — `main.py`의 `render_question_content()`/`_render_image()` 파싱 로직(정규식 100% 동일)을 세그먼트 리스트로 포팅. 로컬 폴백 이미지는 `/static/images/...` 상대경로로 내려주고, **프론트(`QuestionContent.tsx`)가 `VITE_API_BASE_URL`을 붙여 절대경로로 해석**한다 (백엔드가 자기 origin을 알 수 없으므로 이 방향이 맞음).
- `backend/app/services/db_service.py` — `search_question_ids()` 에 TTL(300s) 캐시 적용 (원본 Streamlit의 `@st.cache_data(ttl=300)`과 동등 — 이거 빠뜨리면 검색 1회에 최대 수십 초 걸림, 실제로 이관 중 겪은 회귀).

## 남은 할 일 / 알려진 이슈
- `/api/questions/search-ids` 캐시(`_SEARCH_IDS_CACHE`)는 프로세스 재시작 전까지 무한 누적 방지를 위해 500개 조합 넘으면 통째로 clear — 필터 조합이 매우 다양해지면 캐시 적중률이 낮아질 수 있음. 실사용 패턴 보고 조정.
- 2단계 착수 시 이 문서를 갱신하고, 완료된 마일스톤은 위 체크리스트에 표시할 것.
