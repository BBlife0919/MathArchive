# Next.js가 아닌 React(Vite) + FastAPI 이관 — 진행 상황

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
- [x] M8: 파리티 점검 + `/근본` 5회 검수 + 커밋 (`842240d1`, `c3fa8364`)

**1단계에서 의도적으로 제외**: 미니테스트 자동생성, 교재 디자인모드(사선표지 등),
관리자/클리닉/학생카드 등 다른 Streamlit 페이지. 전부 2단계 이후.

## 2단계 진행 상황
- [x] 교재 디자인모드 — `generate_book_pdf()`(final/사선 표지, 챕터 디바이더, 빠른정답, 해설) 이관.
  `POST /api/exam/book-pdf` + `BookOptionsForm.tsx`. 기존 결과물과 페이지 단위 완전 동일 확인.
  (`7adf09de`, `/근본` 5회 검수 통과). **주의**: `exam_designs.py` 기반 "표지+내지 디자인
  시험지"(`generate_designed_exam_pdf`)는 별개 기능이라 미포함 — 필요시 별도 작업.
- [x] 미니테스트 자동생성 — `POST /api/questions/mini-test`(난이도 비중 랜덤추출, 원본과 1:1 알고리즘 일치).
  생성 시 기존 선택을 완전 교체(REPLACE, `SelectionContext.replaceAll`)하고 시험지(exam) PDF 모드 강제.
  (`35a36ea9`, `/근본` 5회 검수 통과)
- [x] 학생 카드(상담용 대시보드) — `app/pages/2_학생카드.py`(647줄) 6개 섹션(기본정보/PRISM진단/
  자가예측/학습로그/과제평가/관리로그) 이관. matplotlib 레이더·pandas 시계열 집계는 백엔드에서
  동일 로직으로 재계산해 recharts로 렌더링. `GET /api/students/{sid}/dashboard`(통합 조회) +
  쓰기 6종. 최초로 2번째 화면이 생겨 `AppShell`(상단 네비) 도입.
  (`fda81f85`, `/근본` 5회 검수 완료 — 실행검수 에이전트가 정리 작업 중 타임아웃으로 중단됐으나
  DB 카운트 직접 대조로 정리 완료 재확인함)
- [x] 클리닉(오답→처방전) — `app/pages/1_클리닉.py` 이관. `app/clinic_logic.py`(순수 함수) 그대로 재사용.
  처방전 PDF는 [오답,인출1,인출2,인출3] 순서 보존이 핵심(`fetch_questions_page` 사용, 단원/난이도로
  재정렬하는 `fetch_questions_for_preview` 아님). AppShell 3번째 탭.
  (`b63774a9`, `/근본` 5회 검수 완료 — 실행검수가 실사용 데이터로 재현한 `pending-retries` 500 버그를
  발견해서 직접 수정·재검증함)
- [x] 관리자(회원승인) — `app/pages/9_관리자.py` 이관. `require_admin` 의존성 신설(`require_approved`
  체인 위에 `is_admin` 체크 추가). 가입 승인 대기열 + 전체 회원 목록(admin↑/↓·정지·삭제), 본인 계정
  보호(`is_self`)는 원본과 동일 로직. AppShell 4번째 탭(admin 전용).
  (`8d878f02`, `/근본` 5회 검수 완료)
- [x] 카톡 승인 큐 — `app/pages/3_카톡승인큐.py` 이관. `student_service`의 `RIS_CODES`/`PM_CODES`
  재사용해 AI draft 생성 로직 그대로 포팅. instructor_note(강사 1문장) 미입력 시 승인 차단(PDF §7-3)을
  원본은 프론트에서만 걸었지만 API 레벨(422)에서도 강제하도록 강화. `require_admin` 라우터 전체 게이팅.
  발송 예정일 미입력 검증(프론트+백엔드)도 이번에 추가. AppShell 5번째 탭(admin 전용).
  (`c3a5dae0`, `/근본` 5회 검수 완료)
- [x] 검수(HWP 토큰 자동복구 콘솔) — `app/pages/5_검수.py`(1215줄) 이관, **2단계 마지막 페이지, 완료**.
  `HWP_TOKEN_REFERENCE`/`HWP_TOKEN_PATTERNS`/`lookup_token()`/`is_geometry_label()` 전부 그대로 포팅,
  `scripts/detect_bare_math_words.py`·`fix_nested_boxes.py`·`fix_unmapped_hwp_tokens.py` 순수 함수 재사용.
  스캔 결과는 모듈 전역 TTL(1800s) 캐시(`@st.cache_data`+`session_state` 조합과 동등). 구조 자동복구/
  한 방 처리/미상 dropdown 일괄 적용/베이스라인 저장/신고함 처리 전부 API화, AppShell 6번째 탭(admin 전용).
  (`196f9d95`, `/근본` 5회 검수 완료 — 검증 중 "math" 토큰을 테스트용으로 매핑했다가 실제 조합론 문항
  본문이 오염된 사고가 있었으나 `question_latex` 백업 컬럼으로 발견·복구함, 아래 "겪은 함정" 참고)

**2단계 전체 완료** — Streamlit 5개 페이지(학생카드/클리닉/관리자/카톡승인큐/검수) 전부 React+FastAPI로
이관 끝. `app/`(Streamlit)은 전 과정에서 한 줄도 수정하지 않고 병행 운영 중.

## 부수 발견: 원본에 있던 버그 (backend/에서만 수정, app/은 그대로)
빠른검색(quick search) 학교 키워드가 DB 어떤 학교와도 매칭 안 될 때, 원본
`app/main.py`가 "필터 없음"으로 오인해 **전체 DB**를 보여주던 버그 발견
(`main.py:903` 주석은 "결과 0 안내"가 의도였지만 실제로는 그렇게 동작 안 함).
사용자 확인 후 `backend/app/routers/questions.py`의 `_resolve_matching_meta()`
에서만 수정(학교 매칭 0건이면 조기에 빈 결과 반환) — `app/`(Streamlit)은
원래 버그 상태 그대로 유지, 손대지 않음.

`app/clinic_logic.py`의 `list_pending_retries()`도 마찬가지 — Postgres의
`clinic_entries.prescribed_qids`(jsonb 컬럼)를 psycopg2가 이미 list로
자동 디코딩해서 주는데 원본이 다시 `json.loads()`를 걸어 실사용 데이터에서
500 에러가 남. `backend/app/services/clinic_service.py`에 해당 컬럼을 아예
조회하지 않는 자체 쿼리로 우회, `app/`은 그대로 둠.

## 이관 중 겪은 함정: Postgres DATE 컬럼 타입
psycopg2는 DATE 컬럼을 Python `datetime.date` 객체로 반환하지만 SQLite는
TEXT 문자열로 반환한다. Pydantic 응답 스키마를 `str`로 선언한 상태에서
운영 Postgres 실데이터로 테스트하니 `ResponseValidationError`(500)가
발생 — 로컬 SQLite로만 테스트했다면 못 잡았을 버그. `student_service.py`의
`_iso(v)` 헬퍼(`v.isoformat() if hasattr(v, "isoformat") else v`)로 날짜
필드 반환 지점마다 정규화해서 해결. **앞으로 날짜 컬럼을 다루는 신규
엔드포인트를 만들 때마다 항상 염두에 둘 것** — 로컬 SQLite 테스트만으로는
이 버그가 재현 안 됨, 반드시 운영 Postgres로 최종 확인 필요.

## 이관 중 겪은 함정: 날짜 입력 기본값에 UTC 쓰지 말 것
`new Date().toISOString().slice(0, 10)`는 UTC 기준 날짜라, 한국(KST,
UTC+9) 새벽 00~09시엔 실제로는 오늘인데 어제 날짜가 기본값으로 들어간다.
`frontend/src/utils/date.ts`의 `todayLocalISO()`(로컬 연/월/일 직접 조합)
를 항상 쓸 것 — 날짜 `<input>` 기본값을 새로 추가할 때마다 확인.

## 이관 중 겪은 함정: 검수 페이지 "map" 액션의 실콘텐츠 오염 위험
`audit_service.apply_user_mapping(token, action="map", latex)`은 DB 전체에서
해당 토큰을 정규식(단어 경계)으로 찾아 **실제 question_text/solution_text/
choices 텍스트를 치환**한다 — 원본 5_검수.py 로직 그대로. 검증 중 흔한 영단어
"math"를 테스트 토큰으로 골라 `\sqrt`로 매핑 처리했더니, 실제로는 조합론 문제
본문("$math$의 4개의 문자를 일렬로 나열...")이었던 qid=156472가
"$\sqrt$의 4개의 문자를..."로 깨지는 사고가 있었다. `question_latex`/
`solution_latex` 컬럼(파싱 시점 원본이 보존되는 별도 컬럼, `apply_user_mapping`이
건드리지 않음)에 원본이 남아있어 발견·복구했다. **앞으로 이 페이지의
map/remove 액션을 실데이터로 검증할 때는 절대 사전(HWP_TOKEN_REFERENCE)에
없는 임의 영단어를 고르지 말 것** — 진짜 HWP 깨진 토큰인지 실제 콘텐츠(도형
라벨·조합론 문자열 등)인지는 "추천" 칸이 비어있으면(미상) 사람이 직접 원문
맥락을 봐야 판단 가능하다. 검증이 꼭 필요하면 `action="ignore"`(DB 텍스트
무변경)만 쓰거나, `user_token_mappings`에 존재하지 않는 완전 인공적인
토큰(예: `__TEST__`)으로만 map/remove 경로를 확인할 것.

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
