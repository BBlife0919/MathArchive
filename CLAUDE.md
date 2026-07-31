# MathDB - 수학 기출문제 문제은행

## 프로젝트 개요
NGD(수학적실험실) 공동작업 기출 파일(HWPX) 약 6,000개를 파싱하여 SQLite 기반 문제은행 DB를 구축하고, Streamlit UI로 시험지 생성기를 만드는 프로젝트.

## 원본 파일 구조 (HWPX)
- HWPX는 ZIP 형식. 내부에 XML(본문) + 이미지 파일 포함
- 각 파일 내부 구조: [정답] → 해설 → 문제 → [중단원] → [난이도] 순서로 한 문제씩 묶여있음
- [정답]을 구분자로 문항 분리 가능
- 수식: 한글 수식편집기 포맷 → LaTeX 변환 필요
- 그림: 문제용 그림 외에 워터마크/로고 등 숨겨진 그림 존재 → 필터링 필요
- 300명+ 강사 공동작업이라 양식 예외 존재 가능

## DB 구조 (SQLite)
- questions: question_id, file_source, school, grade, year, semester, exam_type, question_number, question_text, question_latex, choices(JSON), answer, answer_type, points, chapter, difficulty, has_image, error_note
- solutions: solution_id, question_id(FK), solution_text, solution_latex
- images: image_id, question_id(FK), image_path, image_order, image_type

## 기술 스택
- Python 3, SQLite, Streamlit
- HWPX 파싱: zipfile + xml.etree.ElementTree
- 작업 환경: macOS (MacBook Pro M5 Pro)

## 로드맵
1. HWPX 파싱 파이프라인 구축 (문항 분리, 수식 변환, 그림 추출) — 완료, 운영 중
2. SQLite DB 구축 — 완료, HWPX 신규 배치가 들어올 때마다 지속 적재
3. Streamlit UI (시험지·교재 PDF 생성기) — 완료, 운영 중 (matharchive.streamlit.app)

## 디렉토리 구조
- /raw - 원본 HWPX 파일 (git 미추적)
- /parsed - 파싱된 JSON 중간 결과물 (git 미추적, 재생성 가능)
- /images - 추출된 이미지 (git 추적)
- /output - 시험지·교재 등 빌드 산출 PDF (git 추적)
- /db - SQLite DB 파일 (git 미추적, `db/*.bak_review*` 백업도 미추적)
- /app - Streamlit 앱
- /scripts - 파싱/변환/교재 빌드 스크립트
- /docs - 설계 메모

## 핵심 작업 규칙 (반드시 준수)
- **말투**: 사용자에게 명령조 절대 금지. 존댓말·"~드립니다" 형태 사용.
- **폰트 불가침**: 매쏠로지·PDF 어디서든 KaTeX 수식·문제·선지 폰트는 절대 건드리지 않는다. 전역 `*` 셀렉터로 폰트 지정 금지.
- **오검/채점메모 비노출**: 편집자 검토메모(오검·벌점 등)는 페이지·교재 어디에도 노출 금지. `strip_review_notes.py`로 제거 (파서 적재 시 자동 호출됨).
- **수식 크기 균일성**: `\dfrac`/`\Biggl` 등으로 특정 수식만 부분 확대하지 않는다. KaTeX 기본 textstyle 유지.
- **중단원명 정규화**: 표기 변형(예: 다항함수→이차함수)을 임의로 통합하지 말고 사용자 확인 후 진행.
- **정규화 3영역**: 본문·해설·선지(choices JSON) 세 컬럼 모두에 동일하게 정규화 적용, 잔여 검수도 세 컬럼 전체 대상.
- **파서 리빌드 후**: `build_db.py` 실행 후 `scan_db_issues` 결과 상위 5건을 선제적으로 보고.
- **HWP 토큰 매핑**: `SYMBOL_MAP`에 항목 추가할 때 `SUSPECT_KEYWORDS`도 함께 갱신.
- **문제 클리닉 알고리즘 의존 금지**: 유사문항 추천·단원 세부분류·자동 라벨링은 미구현 상태. 이를 전제로 하는 작업(예: 교차연습) 제안 금지.
- **외부 절차 안내**: 사용자가 터미널/설정 등 외부 절차를 따라야 할 때는 한 번에 한 단계만 안내하고, 완료 보고를 받은 뒤 다음 단계로.
- **작업 완료 워크플로우**: 코드/데이터 변경 후 `/근본`(5회 교차검수: 본인 3회 + 서브에이전트 2회) → 문제 없으면 커밋. 병렬 에이전트를 쓸 때도 교차검증을 반드시 포함.
- **컴팩션 대비**: 이미지·에러 등을 받으면 바로 핵심을 텍스트로 받아적고 작업을 이어간다 (재작업 최소화).
- 상세 배경·과거 결정 근거는 `~/.claude/projects/-Users-youngwoolee-MathDB/memory/MEMORY.md`의 개별 메모리 파일 참고.
