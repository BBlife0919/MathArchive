db/mathdb.sqlite의 chapter 컬럼을 감사해줘.

1. 모든 유니크 chapter 값과 문항 수를 출력
2. 정규화 이슈 탐색:
   - 같은 단원인데 표기가 다른 것 (띄어쓰기, 오타, 약칭 등)
   - 예: "항등식과 나머지정리" vs "항등식과 나머지 정리" vs "나머지정리"
3. scripts/parse_hwpx.py의 CHAPTER_NORMALIZE 딕셔너리에 이미 등록된 매핑 확인
4. 새로 추가해야 할 매핑 후보 제안
5. chapter가 빈 문자열이거나 null인 문항의 file_source 목록

매핑 추가가 필요하면 CHAPTER_NORMALIZE에 넣을 코드도 함께 제안해줘. 단, 실제 추가는 내가 확인 후 진행할게.