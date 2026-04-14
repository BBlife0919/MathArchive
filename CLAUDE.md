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
1. HWPX 파싱 파이프라인 구축 (문항 분리, 수식 변환, 그림 추출)
2. SQLite DB 구축
3. Streamlit UI (시험지 생성, 문제 삭제, 유사문제 추천)

## 디렉토리 구조
- /raw - 원본 HWPX 파일
- /parsed - 파싱된 JSON 중간 결과물
- /images - 추출된 이미지
- /db - SQLite DB 파일
- /app - Streamlit 앱
- /scripts - 파싱/변환 스크립트
