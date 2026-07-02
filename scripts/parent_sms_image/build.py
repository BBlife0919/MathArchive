"""학부모 안내문자 이미지 생성 (학생별 1장, 세로 카드).

세로 스마트폰 화면 비율의 PNG. 이음학원 이영우T 브랜드 톤 유지 (크림 배경 + 빨강 강조).
"""
from __future__ import annotations
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path('/Users/youngwoolee/Downloads/학부모_안내문자_2026-07-02')
OUT.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════
# 학교별 시험 특징 (사용자 지정 톤 그대로)
# ══════════════════════════════════════════════════════════════════
SCHOOL_ANALYSIS = {
    '광명고1': (
        '이번 시험은 <b>상위권을 제외한 나머지 학생들에게 변별력이 크게 무너진</b> 시험이었습니다. '
        '단순히 교과서 개념·예제 정리 수준으로는 대응이 어려운 문제 배치가 두드러졌고, 특히 후반부 변별 문항들은 여러 개념을 결합해 사고 과정을 요구하는 형태로 출제됐습니다. '
        '<b>기본기가 아주 탄탄한 상태에서 다양한 유형의 응용 문제를 반복 훈련한 학생</b>만이 고득점 궤도에 진입할 수 있었으며, 중위권-상위권 사이 점수 격차가 예년보다 크게 벌어질 것으로 보입니다. '
        '<br/><br/>본원에서는 <b>자체 교재에서 다룬 유형이 이번 시험에 고루 잘 반영</b>되어 출제됐으며, 자체 교재의 응용 유형을 성실히 소화한 학생은 후반부 문항에서도 안정적으로 대응할 수 있었습니다.'
    ),
    '광명북고1': (
        '이번 시험은 <b>학교에서 배부된 프린트 자료를 대비하여 만든 자체 자료</b>에서 상당 부분 그대로 이어져 온 시험이었습니다. '
        '해당 자체 자료를 성실히 소화한 학생이라면 큰 어려움 없이 안정적으로 득점할 수 있었으며, 난이도·유형 배치 모두 예상 범위 안에 있었던 무난한 시험이었습니다. '
        '<br/><br/>본원에서는 <b>자체 교재에서 다룬 유형이 이번 시험에 고루 잘 반영</b>되어 출제됐으며, 학교에서 배부된 프린트 자료를 대비하여 만든 자체 자료와 병행하여 자체 교재를 성실히 소화한 학생은 상위권 사이 변별 문항까지도 무리 없이 해결할 수 있었습니다.'
    ),
    '광문고1': (
        '이번 시험은 <b>교과서 개념과 시중 표준 참고서 수준</b>의 문제 위주로 구성된 무난한 시험이었습니다. '
        '기본 개념을 정확히 이해하고 대표 유형 문제를 충분히 풀어본 학생이라면 큰 부담 없이 시험 범위를 완성할 수 있는 구성이었으며, 상위권 학생들은 만점 근처 점수까지 노려볼 수 있는 시험이었습니다. '
        '<br/><br/>본원에서는 <b>자체 교재에서 다룬 유형이 이번 시험에 고루 잘 반영</b>되어 출제됐으며, 자체 교재의 대표 유형을 반복 학습한 학생은 시험 전 구간에서 안정적으로 득점할 수 있었습니다.'
    ),
    '명문고1': (
        '이번 시험은 <b>교과서 개념 위주로 아주 평이하게 출제</b>된 시험이었습니다. '
        '개념 정리와 기본 예제만 성실히 소화해도 안정적인 득점이 가능한 구성이었으며, 어려운 응용·심화 문항은 최소화된 시험이었습니다. '
        '이런 시험은 단순 실수 한 문항이 등급을 결정할 수 있어, 계산 정확도와 검토 시간 확보가 매우 중요합니다. '
        '<br/><br/>본원에서는 <b>자체 교재에서 다룬 유형이 이번 시험에 고루 잘 반영</b>되어 출제됐으며, 자체 교재의 기본·필수 유형을 반복 학습한 학생은 실수 없이 안정적으로 고득점을 확보할 수 있는 시험이었습니다.'
    ),
    '운산고1': (
        '이번 시험은 전반적으로 평이한 난이도였지만, 이 학교는 <b>매년 반복되는 결정적 특징</b>이 있습니다. '
        '<b>객관식 변별력 문항은 항상 최근 모의고사 기출 문제</b>에서 그대로 또는 살짝 변형해 출제되기 때문에, 앞으로도 모의고사 기출 대비가 반드시 필요합니다. '
        '이 학교 시험 대비는 "얼마나 많이 풀었느냐"가 아니라 "어떤 문항을 풀었느냐"가 결정적입니다. '
        '<br/><br/>본원에서는 <b>자체 교재와 최근 모의고사 기출 변형 유형이 이번 시험에 고루 잘 반영</b>되어 출제됐으며, 자체 교재의 심화 응용 유형을 학습한 학생은 변별 문항에서도 실점 없이 대응할 수 있었습니다.'
    ),
    '광명고2': (
        '이번 시험은 <b>아주 평이한 난이도</b>로 출제됐습니다. '
        '교과서 개념·예제와 함께 시중 표준 교재의 <b>필수 빈출 유형</b>이 그대로 대거 반영됐으며, 성실히 준비한 학생이라면 안정적으로 고득점을 확보할 수 있는 시험이었습니다. '
        '전반적으로 고득점 학생이 많이 나올 것으로 예상되며, 상위권 학생들이 만점 근처에 몰릴 가능성이 큽니다. 이런 시험일수록 단순 실수 관리가 등급을 결정합니다. '
        '<br/><br/>본원에서는 <b>자체 교재에서 다룬 필수 빈출 유형이 이번 시험에 고루 잘 반영</b>되어 출제됐으며, 자체 교재를 반복 소화한 학생은 만점권 진입에 유리한 환경에서 시험을 치를 수 있었습니다.'
    ),
    '광명북고2': (
        '이번 시험은 지난 <b>중간고사에서 중위권 이하 학생들이 크게 어려워했던 반동</b>으로, '
        '부교재 <b>수특(수능특강)</b>에서 다수 문항이 그대로 또는 살짝 변형되어 출제됐습니다. '
        '그 결과 <b>부교재를 착실히 준비한 학생은 8~90점을 어렵지 않게 확보</b>할 수 있는 시험이었으며, 부교재 소화 여부에 따라 학생 간 점수 격차가 크게 벌어질 것으로 보입니다. '
        '<br/><br/>본원에서는 <b>수특 및 자체 교재에서 다룬 유형이 이번 시험에 고루 잘 반영</b>되어 출제됐으며, 자체 교재의 응용 유형을 병행 학습한 학생은 상위권 변별 문항까지도 안정적으로 대응할 수 있었습니다.'
    ),
    '광문고2': (
        '이번 시험은 교과서 문제와 필수 유형이 대거 출제됐지만, 단순히 유형을 외운 학생이 아니라 <b>개념과 정의를 원리 수준까지 정확히 이해한 학생</b>이 고득점을 확보할 수 있는 시험이었습니다. '
        '이러한 출제 경향은 이전 시험에서도 뚜렷했으며, <b>3학년 때도 동일한 흐름이 이어질 것</b>으로 예상됩니다. 단순 기계적 풀이보다는 <b>교과서 개념을 원리까지 정확히 학습</b>하는 방향이 앞으로도 매우 중요합니다. '
        '<br/><br/>본원에서는 <b>자체 교재에서 다룬 개념·정의 원리 중심 유형이 이번 시험에 고루 잘 반영</b>되어 출제됐으며, 개념 원리 학습을 병행한 학생은 후반부 변별 문항에서도 흔들리지 않고 대응할 수 있었습니다.'
    ),
    '명문고2': (
        '이번 시험은 <b>교과서 수준의 아주 평이한 난이도</b>로 출제됐습니다. '
        '변별력 문항은 <b>학교에서 배부된 프린트 자료를 대비하여 만든 자체 자료</b>에서 그대로 이어져 왔으며, 참고서나 교과서만 제대로 풀어도 <b>고득점을 쉽게 확보</b>할 수 있는 시험이었습니다. '
        '상위권 학생 다수가 만점 근처에 몰릴 가능성이 크므로, 실수 방지·검토 시간 확보가 등급을 결정합니다. '
        '<br/><br/>본원에서는 <b>자체 교재와 학교 배부 프린트 대비 자체 자료 유형이 이번 시험에 고루 잘 반영</b>되어 출제됐으며, 자체 교재를 반복 소화한 학생은 실수 없이 안정적인 등급을 확보할 수 있는 환경에서 시험을 치를 수 있었습니다.'
    ),
}


# ══════════════════════════════════════════════════════════════════
# 학생 데이터
# ══════════════════════════════════════════════════════════════════
STUDENTS = [
    # 월금반 (휴강 없음)
    {'name': '유서희',   'school': None,       'grade': '중3',       'class': '월금반', 'holiday': None, 'move': '수토'},
    {'name': '안보민',   'school': '광명고1', 'grade': '고1',       'class': '월금반', 'holiday': None, 'move': '수토_안보민'},
    {'name': '이예림',   'school': '광명고1', 'grade': '고1',       'class': '월금반', 'holiday': None, 'move': None},
    {'name': '박채현',   'school': '명문고1', 'grade': '고1',       'class': '월금반', 'holiday': None, 'move': None},
    # 화목반 (7/2 휴강)
    {'name': '이준수',   'school': '광명북고2', 'grade': '고2',   'class': '화목반', 'holiday': '화목', 'move': None},
    {'name': '김윤하',   'school': '광명북고2', 'grade': '고2',   'class': '화목반', 'holiday': '화목', 'move': None},
    {'name': '황희정',   'school': '광명고2',    'grade': '고2',   'class': '화목반', 'holiday': '화목', 'move': None},
    {'name': '지윤',       'school': '광명고2',    'grade': '고2',   'class': '화목반', 'holiday': '화목', 'move': None},
    {'name': '한윤아',   'school': '광명고2',    'grade': '고2',   'class': '화목반', 'holiday': '화목', 'move': None},
    {'name': '이나경',   'school': '광문고2',    'grade': '고2',   'class': '화목반', 'holiday': '화목', 'move': None},
    {'name': '안현근',   'school': '광문고2',    'grade': '고2',   'class': '화목반', 'holiday': '화목', 'move': None},
    {'name': '김서하',   'school': '명문고2',    'grade': '고2',   'class': '화목반', 'holiday': '화목', 'move': None},
    {'name': '박지성',   'school': '명문고2',    'grade': '고2',   'class': '화목반', 'holiday': '화목', 'move': None},
    # 수토반 (7/4 토요일 휴강)
    {'name': '배규민',   'school': '광명북고1', 'grade': '고1',   'class': '수토반', 'holiday': '수토', 'move': None},
    {'name': '고민주',   'school': '광명북고1', 'grade': '고1',   'class': '수토반', 'holiday': '수토', 'move': None},
    {'name': '이선호',   'school': '광명북고1', 'grade': '고1',   'class': '수토반', 'holiday': '수토', 'move': None},
    {'name': '이진서',   'school': '광문고1',    'grade': '고1',   'class': '수토반', 'holiday': '수토', 'move': None},
    {'name': '김태희',   'school': '광문고1',    'grade': '고1',   'class': '수토반', 'holiday': '수토', 'move': None},
    {'name': '이규원',   'school': '광명고1',    'grade': '고1',   'class': '수토반', 'holiday': '수토', 'move': None},
    {'name': '홍요셉',   'school': '운산고1',    'grade': '고1',   'class': '수토반', 'holiday': '수토', 'move': None},
]


def _analysis_html(s: dict) -> str:
    """학교별 시험 특징 문단. 학교 정보 없으면(중3) 빈 문자열."""
    if not s['school'] or s['school'] not in SCHOOL_ANALYSIS:
        return ''
    return f'''
<div class="section">
  <div class="section-title">이번 시험 분석</div>
  <div class="section-body">{SCHOOL_ANALYSIS[s['school']]}</div>
</div>'''


def _holiday_html(s: dict) -> str:
    """반별 휴강 + 다음 수업 진행 안내."""
    if s['class'] == '월금반':
        return '''
<div class="section notice">
  <div class="section-title">다음 수업 안내</div>
  <div class="section-body">월금반은 <b>다음 수업부터 공통수학2 기초 수업</b>이 진행됩니다.</div>
</div>'''
    if s['holiday'] == '화목':
        return '''
<div class="section notice">
  <div class="section-title">휴강 · 다음 수업 안내</div>
  <div class="section-body">
    화목반 <b>7월 2일 수업은 안내드린대로 휴강</b>이고, 다음 수업일부터 정상 진행됩니다.<br/><br/>
    다음 주부터 <b>미적분1 개념 총 리뷰 및 실전 문제풀이</b>를 바로 진행합니다.
  </div>
</div>'''
    if s['holiday'] == '수토':
        return '''
<div class="section notice">
  <div class="section-title">휴강 · 다음 수업 안내</div>
  <div class="section-body">
    수토반 <b>7월 4일(토) 수업은 휴강</b>이고, 다음 수업일부터 정상 진행됩니다.<br/><br/>
    다음 주부터 <b>공통수학2 개념 총 리뷰 및 실전 문제풀이</b>를 바로 진행합니다.
  </div>
</div>'''
    return ''


def _move_html(s: dict) -> str:
    """반 이동 안내."""
    if s['move'] == '수토':
        # 유서희
        return '''
<div class="section move">
  <div class="section-title">반 이동 안내</div>
  <div class="section-body">
    다음 주부터 <b>수토반으로 이동 예정</b>입니다.
    <br/><br/>
    <b>이동 사유</b> · 서희 학생은 <b>습득력이 굉장히 좋고 앞으로의 발전 가능성이 매우 높은 학생</b>입니다.
    그러한 학생의 성취도와 잠재력에 맞게, <b>조금 더 많은 응용문제와 심화 개념을 접할 수 있는 환경</b>을 만들어 주기 위해 수토반으로의 이동을 결정하게 되었습니다.
    사전에 학생과 상담을 마쳤으며, <b>학생 본인 동의</b>가 있었음을 알려 드립니다.
  </div>
</div>'''
    if s['move'] == '수토_안보민':
        return '''
<div class="section move">
  <div class="section-title">반 이동 안내</div>
  <div class="section-body">
    다음 주부터 <b>수토반으로 이동 예정</b>입니다.
    <br/><br/>
    <b>이동 사유</b> · 사실 이번 시험에서 보민 학생은 <b>수학 공부도 정말 열심히 했고</b>, 제가 볼 때도 이번에는 결과가 잘 나올 것이라 확신했던 학생이었습니다.
    그런데 <b>계산 실수도 실수이지만, 충분히 풀 수 있는 문제들을 다 틀려 와서</b> 결과적으로 찍은 학생들보다도 점수가 안 나오는 안타까운 상황이 생겼습니다.
    <br/><br/>
    따라서 <b>일찍부터 다양한 응용문제를 접해 응용력을 대폭 길러야 하는 학생</b>이라 판단되어, 학습량이 더 많은 수토반으로의 이동을 결정하게 되었습니다.
    사전에 학생과 상담을 마쳤으며, <b>학생 본인 동의</b>가 있었음을 알려 드립니다.
  </div>
</div>'''
    return ''


def render_student(s: dict) -> str:
    css = '''
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif; color: #1c1c1c; -webkit-print-color-adjust: exact; margin: 0; padding: 0; background: #f2ecd8; }
.card { width: 780px; padding: 44px 46px; background: #f2ecd8; position: relative; }
.frame { position: absolute; inset: 22px 22px 22px 22px; border: 1.5pt solid #1c1c1c; border-radius: 6px; pointer-events: none; }
.brand-top { position: relative; z-index: 2; display: flex; justify-content: flex-end; align-items: center; padding-bottom: 6px; letter-spacing: 3pt; font-size: 12pt; }
.brand-top .eum { color: #333; font-weight: 700; }
.header { position: relative; z-index: 2; margin-top: 24px; padding-bottom: 20px; border-bottom: 2pt solid #1c1c1c; }
.header .title { font-size: 26pt; font-weight: 900; color: #1c1c1c; letter-spacing: -0.5pt; line-height: 1.25; }
.header .subtitle { font-size: 13pt; font-weight: 600; color: #666; margin-top: 6px; letter-spacing: -0.2pt; }
.hello { position: relative; z-index: 2; margin-top: 22px; font-size: 16pt; font-weight: 700; color: #1c1c1c; line-height: 1.55; }
.hello .name { color: #c33a2a; font-weight: 900; }
.para { position: relative; z-index: 2; margin-top: 14px; font-size: 13.5pt; line-height: 1.75; color: #333; }
.para b { color: #c33a2a; font-weight: 800; }
.section { position: relative; z-index: 2; margin-top: 22px; padding: 16px 20px; background: rgba(255,255,255,0.65); border-left: 4pt solid #c33a2a; border-radius: 4px; }
.section.notice { border-left-color: #d8a72b; background: rgba(255,247,224,0.75); }
.section.move { border-left-color: #4a90e2; background: rgba(232,241,252,0.75); }
.section-title { font-size: 13.5pt; font-weight: 900; color: #1c1c1c; margin-bottom: 8px; letter-spacing: -0.3pt; }
.section-body { font-size: 12.5pt; line-height: 1.75; color: #333; }
.section-body b { color: #c33a2a; font-weight: 800; }
.section.notice .section-body b { color: #7a5210; }
.section.move .section-body b { color: #1c4d8c; }
.signoff { position: relative; z-index: 2; margin-top: 28px; padding-top: 18px; border-top: 1pt solid #b8b0a0; text-align: right; }
.signoff .name { font-size: 15pt; font-weight: 900; color: #1c1c1c; letter-spacing: -0.3pt; }
.signoff .name .t { color: #c33a2a; }
.signoff .role { font-size: 10pt; letter-spacing: 3pt; color: #666; margin-top: 4px; font-weight: 500; }
'''
    import re as _re
    display_grade = ''
    if s['school']:
        display_grade = _re.sub(r'([가-힣]+고)([12])$', r'\1 \2학년', s['school'])
    else:
        display_grade = s['grade']

    hello_line = (
        f'<span class="name">{s["name"]}</span> 학생 학부모님, 안녕하세요.<br/>'
        f'<b>이음학원 수학과 이영우 강사</b>입니다.'
    )
    intro = (
        '2026학년도 <b>1학기 기말고사</b>가 모두 끝났습니다. '
        '이번 시험까지 긴장하면서도 열심히 준비해 준 우리 아이들, 그리고 함께 마음 쓰셨을 학부모님께도 '
        '진심으로 <b>고생하셨다는 말씀</b> 먼저 전해 드립니다.'
    ) if s['grade'] in ('고1', '고2') else (
        '이번 시험까지 아이가 학원에서 성실히 학습에 임해 주었습니다. '
        '함께 마음 써 주신 학부모님께도 <b>고생하셨다는 말씀</b> 먼저 전해 드립니다.'
    )
    guide = (
        '성적 관련 <b>상담안내 드리기에 앞서</b>, 이번 시험의 난이도와 출제 경향을 궁금해하실 학부모님을 위해 '
        '문자로 먼저 간단히 안내 드립니다. '
        '학생들과는 <b>시험 결과와 문제점, 그리고 앞으로의 방향성</b>에 대해 진지하게 상담을 진행하고 있습니다.'
        '<br/><br/>'
        '<b>기타 문의사항이 있으시면 하단에 있는 번호로 연락 주시면 감사하겠습니다.</b>'
    )

    html = f'''<!doctype html>
<html><head><meta charset="utf-8"/><style>{css}</style></head><body>
<div class="card">
  <div class="frame"></div>
  <div class="brand-top">
    <span class="eum">이음학원 · 이영우T</span>
  </div>
  <div class="header">
    <div class="title">2026학년도 1학기 기말고사<br/>학부모 안내</div>
    <div class="subtitle">{display_grade} · {s['class']}</div>
  </div>
  <div class="hello">{hello_line}</div>
  <div class="para">{intro}</div>
  <div class="para">{guide}</div>
  {_analysis_html(s)}
  {_holiday_html(s)}
  {_move_html(s)}
  <div class="signoff">
    <div class="name">이영우 드림</div>
    <div class="role">이음학원 · 010-9954-9820</div>
  </div>
</div>
</body></html>'''
    return html


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for s in STUDENTS:
            html = render_student(s)
            html_path = OUT / f'{s["name"]}_안내문자.html'
            html_path.write_text(html, encoding='utf-8')
            page = browser.new_page(viewport={'width': 780, 'height': 1200})
            page.goto('file://' + str(html_path.resolve()), wait_until='networkidle')
            page.wait_for_timeout(500)
            # 카드 요소 크기에 맞춰 full page screenshot
            png_path = OUT / f'{s["name"]}_학부모안내.png'
            page.screenshot(path=str(png_path), full_page=True, omit_background=False)
            page.close()
            print(f'  → {png_path}')
        browser.close()
    print(f'\n완료! {len(STUDENTS)}개 → {OUT}')


if __name__ == '__main__':
    main()
