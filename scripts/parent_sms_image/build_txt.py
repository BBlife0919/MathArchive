"""학부모 안내문자를 텍스트 파일로 정리 (상담실장 전달용)."""
from __future__ import annotations
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from build import STUDENTS, SCHOOL_ANALYSIS  # noqa

OUT_DIR = Path('/Users/youngwoolee/Downloads/학부모_안내문자_2026-07-02')
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / '학부모_안내문자_텍스트_2026-07-02.txt'


def strip_html(s: str) -> str:
    s = s.replace('<br/>', '\n').replace('<br>', '\n')
    s = re.sub(r'</?b>', '', s)
    s = re.sub(r'</?[^>]+>', '', s)
    return s.strip()


def render_student(s: dict) -> str:
    school_lbl = ''
    if s['school']:
        school_lbl = re.sub(r'([가-힣]+고)([12])$', r'\1 \2학년', s['school'])
    else:
        school_lbl = s['grade']

    lines = []
    lines.append(f'{s["name"]} 학생 학부모님, 안녕하세요.')
    lines.append('이음학원 수학과 이영우 강사입니다.')
    lines.append('')
    if s['grade'] in ('고1', '고2'):
        lines.append(
            '2026학년도 1학기 기말고사가 모두 끝났습니다. 이번 시험까지 긴장하면서도 '
            '열심히 준비해 준 우리 아이들, 그리고 함께 마음 쓰셨을 학부모님께도 '
            '진심으로 고생하셨다는 말씀 먼저 전해 드립니다.'
        )
    else:
        lines.append(
            '이번 시험까지 아이가 학원에서 성실히 학습에 임해 주었습니다. '
            '함께 마음 써 주신 학부모님께도 고생하셨다는 말씀 먼저 전해 드립니다.'
        )
    lines.append('')
    lines.append(
        '성적 관련 상담안내 드리기에 앞서, 이번 시험의 난이도와 출제 경향을 '
        '궁금해하실 학부모님을 위해 문자로 먼저 간단히 안내 드립니다. '
        '학생들과는 시험 결과와 문제점, 그리고 앞으로의 방향성에 대해 진지하게 상담을 진행하고 있습니다.'
    )
    lines.append('')
    lines.append('기타 문의사항이 있으시면 하단에 있는 번호로 연락 주시면 감사하겠습니다.')

    if s['school'] and s['school'] in SCHOOL_ANALYSIS:
        lines.append('')
        lines.append('■ 이번 시험 분석')
        lines.append(strip_html(SCHOOL_ANALYSIS[s['school']]))

    if s['class'] == '월금반':
        lines.append('')
        lines.append('■ 다음 수업 안내')
        lines.append('월금반은 다음 수업부터 공통수학2 기초 수업이 진행됩니다.')
    elif s['holiday'] == '화목':
        lines.append('')
        lines.append('■ 휴강 · 다음 수업 안내')
        lines.append('화목반 7월 2일 수업은 안내드린대로 휴강이고, 다음 수업일부터 정상 진행됩니다.')
        lines.append('다음 주부터 미적분1 개념 총 리뷰 및 실전 문제풀이를 바로 진행합니다.')
    elif s['holiday'] == '수토':
        lines.append('')
        lines.append('■ 휴강 · 다음 수업 안내')
        lines.append('수토반 7월 4일(토) 수업은 휴강이고, 다음 수업일부터 정상 진행됩니다.')
        lines.append('다음 주부터 공통수학2 개념 총 리뷰 및 실전 문제풀이를 바로 진행합니다.')

    if s['move'] == '수토':
        lines.append('')
        lines.append('■ 반 이동 안내')
        lines.append('다음 주부터 수토반으로 이동 예정입니다.')
        lines.append('')
        lines.append(
            '이동 사유 · 서희 학생은 습득력이 굉장히 좋고 앞으로의 발전 가능성이 매우 높은 학생입니다. '
            '그러한 학생의 성취도와 잠재력에 맞게, 조금 더 많은 응용문제와 심화 개념을 접할 수 있는 환경을 '
            '만들어 주기 위해 수토반으로의 이동을 결정하게 되었습니다. '
            '사전에 학생과 상담을 마쳤으며, 학생 본인 동의가 있었음을 알려 드립니다.'
        )
    elif s['move'] == '수토_안보민':
        lines.append('')
        lines.append('■ 반 이동 안내')
        lines.append('다음 주부터 수토반으로 이동 예정입니다.')
        lines.append('')
        lines.append(
            '이동 사유 · 사실 이번 시험에서 보민 학생은 수학 공부도 정말 열심히 했고, '
            '제가 볼 때도 이번에는 결과가 잘 나올 것이라 확신했던 학생이었습니다. '
            '그런데 계산 실수도 실수이지만, 충분히 풀 수 있는 문제들을 다 틀려 와서 '
            '결과적으로 찍은 학생들보다도 점수가 안 나오는 안타까운 상황이 생겼습니다.'
        )
        lines.append('')
        lines.append(
            '따라서 일찍부터 다양한 응용문제를 접해 응용력을 대폭 길러야 하는 학생이라 판단되어, '
            '학습량이 더 많은 수토반으로의 이동을 결정하게 되었습니다. '
            '사전에 학생과 상담을 마쳤으며, 학생 본인 동의가 있었음을 알려 드립니다.'
        )

    lines.append('')
    lines.append('이영우 드림')
    lines.append('이음학원 · 010-9954-9820')

    header = (
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        f'  {s["name"]}  ({school_lbl} · {s["class"]})\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    )
    return header + '\n\n' + '\n'.join(lines)


def main():
    blocks = [render_student(s) for s in STUDENTS]
    OUT.write_text('\n\n\n'.join(blocks), encoding='utf-8')
    print(f'생성: {OUT}')


if __name__ == '__main__':
    main()
