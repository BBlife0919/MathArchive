DB 무결성 검사를 수행해줘. db/mathdb.sqlite 파일을 대상으로:

1. PRAGMA integrity_check 실행
2. 각 테이블 행 수 출력 (questions, solutions, images)
3. 필수 컬럼 null 체크: question_text, answer, chapter, difficulty가 null인 문항 찾기
4. 중복 체크: 같은 file_source + question_number 조합이 중복되는 케이스
5. 고아 레코드: solutions/images에 존재하지만 questions에 없는 question_id
6. chapter 컬럼 유니크 값 목록 + 각 개수 (정규화 이슈 파악용)
7. answer_type별 분포
8. 이상치: points가 0 이하이거나 100 초과인 문항

결과를 표 형태로 깔끔하게 정리해서 보여줘. 문제가 발견되면 수정 방안도 제안해줘.