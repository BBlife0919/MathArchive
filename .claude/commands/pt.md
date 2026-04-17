$ARGUMENTS 파일을 파싱 테스트해줘.

1. `python3 scripts/parse_hwpx.py $ARGUMENTS --no-images --debug` 실행
2. 파싱 결과 JSON을 분석해서 다음을 체크:
   - 총 문항 수가 합리적인지 (보통 20~30문항)
   - 정답이 비어있거나 이상한 문항
   - chapter/difficulty가 누락된 문항
   - 수식 변환 품질: LaTeX에 over, bar, root 같은 HWP 키워드가 남아있는지
   - 선택지가 5개 미만인 선택형 문항
   - question_text가 너무 짧은 문항 (10자 미만)
3. 문제가 있는 문항은 번호와 함께 구체적으로 알려줘
4. 파서 수정이 필요한 경우 어느 함수를 수정해야 하는지 제안해줘