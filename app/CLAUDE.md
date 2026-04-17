# app/ 작업 규칙

## Streamlit 앱 구조 (main.py)
- DB 연결: `@st.cache_resource`로 싱글턴 커넥션 (check_same_thread=False)
- 필터 옵션: `@st.cache_data(ttl=600)`으로 캐싱
- 세션 상태: `st.session_state.selected_ids` (set)로 선택 문제 관리

## UI 구조
- 사이드바: 필터 (지역/학교/단원/난이도/문제유형/키워드)
- 탭1: 문제 목록 (검색 결과 + 추가/제거 버튼)
- 탭2: 시험지 미리보기 + PDF 다운로드 + 정답/해설 토글

## 수식 렌더링
- 인라인 수식 `$...$`은 Streamlit markdown이 자동 렌더링 (KaTeX)
- `<<IMG:imageN>>` 플레이스홀더 → 이모지로 대체

## PDF 생성
- fpdf2 사용, 한글 폰트: AppleSDGothicNeo (macOS 전용)
- 정답표를 별도 페이지로 생성

## 주의사항
- SQL 쿼리에 파라미터 바인딩 필수 (injection 방지)
- 난이도 정렬: 하 < 중 < 상 < 킬 (DIFF_ORDER 딕셔너리)
