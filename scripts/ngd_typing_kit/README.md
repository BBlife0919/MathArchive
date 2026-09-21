# ngd_typing_kit — NGD 기출 HWPX 타이핑 조립 툴킷 (포산중 3-2 기말, 2026-09-21)

`/타이핑` 스킬(`~/.claude/commands/타이핑.md`)의 규칙을 코드로 옮긴 것. 다음 시험지에 재사용.

- `content.py` : 문항 데이터(문제·선지·해설·정답·단원·난이도). `$...$`=HWP 수식, 그 외 일반 텍스트. **새 시험지는 이 파일만 새로 쓴다.**
- `build.py` : 골격(사용자 제출본 hwpx의 첫 문단)에 본문을 생성해 HWPX 조립. 수식 폭 추정(한컴 실측 보정), 선지 탭, 끝노트 해설, 단 배치(동분할), 그림 삽입, 보기 박스 clone. 골격 경로는 환경변수 `NGD_SKELETON`으로 바꿀 수 있다. 상단 상수(학교·학기·단원·제작일)와 `FILENAME_STEM` 수정.
- `figures/figlib.py` + `q*.py`,`s*.py` : matplotlib 그림. 실행하면 `figures/png/`에 PNG+json 생성(`python3 q01.py`). 규칙: NGD 마크 `ngd_on`(직선과 나란히 겹치기), 길이 `dimarc_pt`(점선 사이 숫자), 각도 `angle`(호 바로 바깥).
- `check.py`/`dump.py` : 조립 결과 규칙 점검·구조 덤프(경로는 스크립트 안 scratchpad 경로를 새로 지정해야 함).
- 그림 PNG는 재생성 가능하므로 저장하지 않는다.
