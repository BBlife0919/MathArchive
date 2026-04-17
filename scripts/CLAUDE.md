# scripts/ 작업 규칙

## 파서 구조 (parse_hwpx.py)
- HWPX(ZIP) → XML 파싱 → ContentItem 스트림 → 텍스트 직렬화 → [난이도] 기준 문항 분리
- 문항 블록 내부: [정답] 위치 기준으로 해설/문제본문 분리
- 수식: HWP 수식편집기 스크립트 → LaTeX 변환 (hwp_eq_to_latex)

## 수식 변환 규칙
- HWP `over` → `\frac{}{}`, `root`/`sqrt` → `\sqrt{}`, `bar` → `\overline{}`
- LEFT/RIGHT 괄호: 대소문자 모두 처리 (300명 강사 표기 혼재)
- `cases{...#...}` → `\begin{cases}...\end{cases}`
- 그리스문자/기호: GREEK_MAP, SYMBOL_MAP 딕셔너리 기반
- `_postprocess_latex()`에서 잔여 HWP 키워드 2차 정리 (변환 누락 방어)
- 괄호 짝 보정: `_balance_braces()`로 `{}`의 열림/닫힘 자동 보정

## 워터마크/가비지 필터링
- 수식: 흰색(#FFFFFF) 텍스트, "N.G.D", "무단", "공동 작업/저작" 포함 → 제거
- 이미지: `treatAsChar="0"` (본문 흐름 밖 배치) → 워터마크로 판정
- masterpage0.xml에 참조된 이미지 → 워터마크 목록에 추가
- 수식 가비지: 빈 문자열, `To\d+` 패턴, 이중 줄바꿈 이후 내용 → 제거

## 문항 분리 로직
- [난이도] 위치를 문항 블록 종료 마커로 사용
- [정답]이 없는 블록은 문항이 아님 (프리앰블/저작권)
- 저작권 텍스트 필터: "콘텐츠산업", "NGD", "무단.*복제", "제작연월일" 포함 시 제거

## 선택지 추출
- ①②③④⑤ 위치 기반 분할
- 압축형 지원: `① $v1$$v2$$v3$` → 1번=v1, 2번=v2, 3번=v3으로 자동 분배
- 선택지 없으면 서답형으로 처리

## 중단원명 정규화
- CHAPTER_NORMALIZE 딕셔너리로 표기 변형 통합
- "다항함수" → "이차함수"로 통일 (사용자 확인 완료)
- 신규 변형 발견 시 사용자에게 확인 후 추가할 것

## 파일명 메타데이터
- 패턴: `[학교급][연도][학년-학기-시험유형][지역][학교][과목][출판사][단원범위][...]`
- 시험유형: a=중간, b=기말
- 단원범위: "~" 또는 "-"로 연결된 한글 항목

## DB 적재 (build_db.py)
- question_latex = question_text (이미 LaTeX 인라인 포함)
- solution_latex = solution_text (동일)
- 중복 적재 방지: file_source 기준 이미 적재된 파일 건너뜀
- PRAGMA: WAL 모드, foreign_keys ON
