# db/ 작업 규칙

## 스키마 (3 테이블)
- questions: 문항 본문, 메타데이터, 정답, 배점, 단원, 난이도
- solutions: 해설 (question_id FK)
- images: 이미지 참조/경로 (question_id FK)

## 인덱스
- school, chapter, difficulty, year, (year+semester+exam_type) 복합
- solutions/images: question_id

## 스키마 변경 시 주의
- build_db.py의 SCHEMA 상수와 INSERT 구문을 반드시 함께 수정
- app/main.py의 SELECT 쿼리에 신규 컬럼 반영 필요 여부 확인
- 기존 DB 파일이 있으면 `--rebuild` 플래그로 재구축하거나 ALTER TABLE 사용
