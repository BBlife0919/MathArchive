"""고2 4개교 적중분석 카드뉴스 PDF — build.py 스타일 그대로 (고2 스크린샷 사용).

학교: 광명고2 · 광명북고2 · 광문고2 · 명문고2 (운산고2 제외)
"""
from __future__ import annotations
import base64
import unicodedata
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path('/Users/youngwoolee/MathDB/output/pirate_analysis')
SRC = ROOT / '무제_기말_2026_고2'
ASSETS = ROOT / 'assets'
OUT = Path('/Users/youngwoolee/Downloads/적중분석_2026_1학기_기말_고2')
OUT.mkdir(parents=True, exist_ok=True)


def find_src(name: str) -> Path | None:
    target = unicodedata.normalize('NFC', name)
    for p in SRC.iterdir():
        if unicodedata.normalize('NFC', p.name) == target:
            return p
    return None


def img_b64(p: Path | str | None) -> str:
    if not p:
        return ''
    p = Path(p)
    if not p.exists():
        return ''
    ext = p.suffix.lstrip('.').lower()
    mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg'}.get(ext, 'application/octet-stream')
    return f'data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}'


INSTRUCTOR_URI = img_b64(ASSETS / 'instructor.png')
EUM_LOGO_URI = img_b64(ASSETS / 'eum_logo.png')


# ══════════════════════════════════════════════════════════════════
# 고2 시험 범위 예상: 함수의 극한·연속 / 미분법 / 도함수 활용 / 적분법
# 카테고리:  A = 함수의 극한·연속 / B = 미분법 / C = 적분법
# ══════════════════════════════════════════════════════════════════

GWANGMYEONG2_ITEMS_ALL = [
    (1,  '함수의 극한',        '3.8', '하', 'A', 3,  '유형3  ─ 극한값 계산 기본'),
    (2,  '함수의 극한',        '3.9', '하', 'A', 6,  '유형6  ─ 극한 대입·부정형'),
    (3,  '함수의 연속',        '4.0', '하', 'A', 9,  '유형9  ─ 연속 판정 기본'),
    (4,  '미분계수',            '4.1', '하', 'B', 4,  '유형4  ─ 미분계수 정의'),
    (5,  '도함수',                '4.2', '중', 'B', 7,  '유형7  ─ 도함수 계산 기본'),
    (6,  '접선의 방정식',    '4.3', '중', 'B', 12, '유형12 ─ 접선의 방정식'),
    (7,  '함수의 연속',        '4.3', '중', 'A', 15, '유형15 ─ 연속 조건 상수 결정'),
    (8,  '도함수 활용',        '4.4', '중', 'B', 18, '유형18 ─ 증감·극값 판정'),
    (9,  '적분법 기본',        '4.4', '중', 'C', 5,  '유형5  ─ 부정적분 기본'),
    (10, '정적분',                '4.5', '중', 'C', 9,  '유형9  ─ 정적분 계산'),
    (11, '함수의 극한',        '4.5', '중', 'A', 18, '유형18 ─ 극한 계산 응용'),
    (12, '도함수 활용',        '4.6', '중', 'B', 22, '유형22 ─ 극값 조건'),
    (13, '접선의 방정식',    '4.6', '중', 'B', 24, '유형24 ─ 접선 조건'),
    (14, '적분법',                '4.7', '상', 'C', 14, '유형14 ─ 정적분 함수'),
    (15, '도함수 활용',        '4.8', '상', 'B', 27, '유형27 ─ 함수 최대·최소'),
    (16, '적분법',                '4.9', '상', 'C', 18, '유형18 ─ 정적분 활용'),
    (17, '도함수 활용',        '5.0', '상', 'B', 30, '유형30 ─ 방정식 실근 개수'),
    (18, '적분법',                '5.1', '상', 'C', 22, '유형22 ─ 넓이 응용'),
    (19, '도함수 활용',        '5.2', '상', 'B', 33, '유형33 ─ 함수 분석·그래프'),
    ('서답 1', '함수의 극한',   '5.0', '상', 'A', 40, '유형40 ─ 서술형·극한 응용'),
    ('서답 2', '도함수 활용',   '5.0', '상', 'B', 44, '유형44 ─ 서술형·최적화'),
    ('서답 3', '적분법',            '5.3', '상', 'C', 48, '유형48 ─ 서술형·정적분 응용'),
]

GWANGBUK2_ITEMS_ALL = [
    (1,  '함수의 극한',      '3.9', '하', 'A', 4,  '유형4  ─ 극한 계산 기본'),
    (2,  '함수의 극한',      '4.0', '하', 'A', 7,  '유형7  ─ 부정형 극한'),
    (3,  '함수의 연속',      '4.0', '하', 'A', 10, '유형10 ─ 연속 조건'),
    (4,  '미분계수',            '4.1', '하', 'B', 5,  '유형5  ─ 미분계수 정의'),
    (5,  '도함수',                '4.2', '중', 'B', 8,  '유형8  ─ 도함수 계산'),
    (6,  '접선의 방정식',    '4.3', '중', 'B', 13, '유형13 ─ 접선 조건'),
    (7,  '도함수 활용',        '4.3', '중', 'B', 17, '유형17 ─ 증감·극값'),
    (8,  '부정적분',            '4.4', '중', 'C', 4,  '유형4  ─ 부정적분 기본'),
    (9,  '정적분',                '4.4', '중', 'C', 8,  '유형8  ─ 정적분 계산'),
    (10, '함수의 극한',      '4.4', '중', 'A', 16, '유형16 ─ 극한 응용'),
    (11, '함수의 연속',      '4.5', '중', 'A', 19, '유형19 ─ 연속 조건 상수'),
    (12, '도함수 활용',        '4.5', '중', 'B', 22, '유형22 ─ 극값 조건'),
    (13, '적분법',                '4.6', '중', 'C', 12, '유형12 ─ 정적분 함수'),
    (14, '접선의 방정식',    '4.6', '중', 'B', 26, '유형26 ─ 접선 응용'),
    (15, '도함수 활용',        '4.7', '상', 'B', 29, '유형29 ─ 실근 개수'),
    (16, '적분법',                '4.7', '상', 'C', 16, '유형16 ─ 넓이 계산'),
    (17, '함수의 연속',      '4.7', '상', 'A', 23, '유형23 ─ 연속 응용'),
    (18, '도함수 활용',        '4.8', '상', 'B', 33, '유형33 ─ 함수 분석'),
    (19, '적분법',                '4.9', '상', 'C', 21, '유형21 ─ 넓이 응용'),
    (20, '도함수 활용',        '5.0', '상', 'B', 37, '유형37 ─ 최대·최소'),
    ('논술 1', '함수의 극한',   '5.0', '상', 'A', 42, '유형42 ─ 서술형·극한'),
    ('논술 2', '적분법',            '5.0', '상', 'C', 46, '유형46 ─ 서술형·정적분'),
]

GWANGMUN2_ITEMS_ALL = [
    (1,  '함수의 극한',      '3.8', '하', 'A', 3,  '유형3  ─ 극한 계산 기본'),
    (2,  '함수의 극한',      '3.9', '하', 'A', 6,  '유형6  ─ 부정형 극한'),
    (3,  '함수의 연속',      '4.0', '하', 'A', 9,  '유형9  ─ 연속 판정'),
    (4,  '미분계수',            '4.1', '하', 'B', 4,  '유형4  ─ 미분계수 정의'),
    (5,  '도함수',                '4.2', '중', 'B', 7,  '유형7  ─ 도함수 계산'),
    (6,  '접선의 방정식',    '4.3', '중', 'B', 11, '유형11 ─ 접선의 방정식'),
    (7,  '함수의 연속',      '4.3', '중', 'A', 14, '유형14 ─ 연속 조건 상수'),
    (8,  '도함수 활용',        '4.4', '중', 'B', 17, '유형17 ─ 증감·극값 판정'),
    (9,  '부정적분',            '4.4', '중', 'C', 4,  '유형4  ─ 부정적분 기본'),
    (10, '정적분',                '4.5', '중', 'C', 8,  '유형8  ─ 정적분 계산'),
    (11, '함수의 극한',      '4.5', '중', 'A', 18, '유형18 ─ 극한·연속 종합'),
    (12, '도함수 활용',        '4.6', '중', 'B', 21, '유형21 ─ 극값 조건'),
    (13, '접선의 방정식',    '4.7', '상', 'B', 25, '유형25 ─ 접선·개념 이해'),
    (14, '도함수 활용',        '4.7', '상', 'B', 28, '유형28 ─ 함수 분석 개념'),
    (15, '적분법',                '4.8', '상', 'C', 14, '유형14 ─ 정적분 함수'),
    (16, '함수의 연속',      '4.8', '상', 'A', 24, '유형24 ─ 연속·정의 이해'),
    (17, '도함수 활용',        '4.9', '상', 'B', 32, '유형32 ─ 함수 극값·개념'),
    (18, '적분법',                '5.0', '상', 'C', 19, '유형19 ─ 넓이·정의 활용'),
    (19, '적분법',                '5.1', '상', 'C', 24, '유형24 ─ 정적분 응용(서술형)'),
    (20, '도함수 활용',        '5.2', '상', 'B', 36, '유형36 ─ 함수·개념 종합'),
    ('서답 1', '함수의 연속',   '6.0', '상', 'A', 41, '유형41 ─ 서술형·정의 이해'),
    ('서답 2', '도함수 활용',   '6.4', '상', 'B', 45, '유형45 ─ 서술형·개념 응용'),
]

MYEONGMUN2_ITEMS_ALL = [
    (1,  '함수의 극한',      '3.8', '하', 'A', 2,  '유형2  ─ 극한 계산 기본'),
    (2,  '함수의 극한',      '3.9', '하', 'A', 5,  '유형5  ─ 부정형 극한'),
    (3,  '함수의 연속',      '4.0', '하', 'A', 7,  '유형7  ─ 연속 판정'),
    (4,  '미분계수',            '4.1', '하', 'B', 3,  '유형3  ─ 미분계수 정의'),
    (5,  '도함수',                '4.2', '중', 'B', 6,  '유형6  ─ 도함수 계산'),
    (6,  '접선의 방정식',    '4.3', '중', 'B', 10, '유형10 ─ 접선 조건'),
    (7,  '함수의 연속',      '4.3', '중', 'A', 13, '유형13 ─ 연속 조건 상수'),
    (8,  '도함수 활용',        '4.4', '중', 'B', 16, '유형16 ─ 증감·극값'),
    (9,  '부정적분',            '4.4', '중', 'C', 3,  '유형3  ─ 부정적분 기본'),
    (10, '정적분',                '4.5', '중', 'C', 7,  '유형7  ─ 정적분 계산'),
    (11, '함수의 극한',      '4.5', '중', 'A', 17, '유형17 ─ 극한 응용'),
    (12, '도함수 활용',        '4.6', '중', 'B', 19, '유형19 ─ 극값 조건'),
    (13, '접선의 방정식',    '4.7', '상', 'B', 22, '유형22 ─ 접선 응용'),
    (14, '적분법',                '4.7', '상', 'C', 11, '유형11 ─ 정적분 함수'),
    (15, '도함수 활용',        '4.8', '상', 'B', 25, '유형25 ─ 함수 최대·최소'),
    (16, '적분법',                '4.9', '상', 'C', 15, '유형15 ─ 넓이 계산'),
    (17, '도함수 활용',        '5.0', '상', 'B', 28, '유형28 ─ 실근 개수'),
    (18, '함수의 연속',      '5.0', '상', 'A', 22, '유형22 ─ 연속 조건 응용'),
    (19, '적분법',                '5.1', '상', 'C', 18, '유형18 ─ 넓이 응용'),
    (20, '도함수 활용',        '5.4', '상', 'B', 32, '유형32 ─ 함수 분석·그래프'),
    ('서답 1', '함수의 극한',   '6.0', '상', 'A', 37, '유형37 ─ 서술형·극한 활용'),
    ('서답 2', '적분법',            '6.4', '상', 'C', 40, '유형40 ─ 서술형·정적분'),
]


SCHOOLS = [
    {
        'key': '광명고2',
        'name': '광명고등학교 2학년',
        'no': 61,
        'grade_label': '광명고2',
        'summary_headline': '아주 평이 · 교과서 + 시중교재 필수빈출 대거 출제',
        'summary_body': (
            '이번 시험은 <mark>아주 평이한 난이도</mark>로 출제됐습니다. 교과서 개념·예제와 함께 시중 표준 교재의 '
            '<b>필수 빈출 유형</b>이 그대로 대거 반영됐으며, 성실히 준비한 학생이라면 안정적으로 고득점을 확보할 수 있는 구성이었습니다.'
            '<br/><br/>'
            '전반적으로 <b>고득점 학생이 많이 나올 것으로 예상</b>되며, 상위권에서는 만점 근처 점수 분포가 두터워질 가능성이 큽니다. '
            '이런 시험의 특성상 <mark>단순 실수 한 문항이 등급 밀림의 결정적 원인</mark>이 됩니다. '
            '개념·유형 학습에 더해 계산 정확도·검토 시간 확보 훈련이 병행되어야 하며, '
            '평이한 시험일수록 <b>기본기 완성 + 실수 관리</b>가 등급을 만듭니다. '
            '지금 성실히 준비한 학생이라면 이번 시험을 발판으로 다음 학기에도 안정적인 상위권 유지가 가능합니다.'
        ),
        'instructor_comment': (
            '평이한 시험일수록 <b>실수 1개가 등급 하락</b>입니다. 개념·필수 유형은 이미 다 아는 상태에서 '
            '계산 정확도와 검토 시간 확보가 결정적입니다. 필수 빈출 유형 반복 소화 + 실수 방지 훈련이 이번 학교 대비의 핵심.'
        ),
        'strategy': [
            ('교과서·시중교재 필수 유형 완주', '이 학교 시험의 정공법. <b>필수 빈출 유형</b> 반복 소화가 곧 고득점.'),
            ('실수 방지 계산 훈련', '평이한 시험은 실수 1개가 등급을 결정합니다. 계산 정확도·검토 훈련 병행.'),
            ('상위권 유지 위한 심화 병행', '만점 근처 분포가 두터워지므로, 상위권은 <b>이영우T 심화팩</b>으로 여유 확보.'),
        ],
        'all_items': GWANGMYEONG2_ITEMS_ALL,
        'items_config': [
            {'q': 14, 'cat': 'C', 'lbl': 14, 'note': '정적분 함수 유도 · 기본 공식 활용.'},
            {'q': 16, 'cat': 'C', 'lbl': 18, 'note': '정적분 활용 · 넓이 계산.'},
            {'q': 18, 'cat': 'C', 'lbl': 22, 'note': '적분법 응용 · 넓이·조건.'},
            {'q': 20, 'cat': 'A', 'lbl': 40, 'note': '서술형 · 극한 활용 응용.'},
        ],
    },
    {
        'key': '광명북고2',
        'name': '광명북고등학교 2학년',
        'no': 62,
        'grade_label': '광명북고2',
        'summary_headline': '수특 · 부교재 대거 출제 · 착실히 준비한 학생 8~90점 확보',
        'summary_body': (
            '이번 시험은 지난 <mark>중간고사에서 중위권 이하 학생들이 크게 어려워했던 반동</mark>으로, '
            '부교재 <b>수특(수능특강)</b>과 학교 부교재에서 <mark>다수 문항이 그대로 또는 살짝 변형되어 출제</mark>됐습니다. '
            '그 결과 부교재를 착실히 준비한 학생은 <b>8~90점을 어렵지 않게 확보</b>할 수 있었던 시험이었습니다.'
            '<br/><br/>'
            '중간고사 대비의 방향을 조정한 학교의 배려가 반영된 시험 구성으로 볼 수 있으며, '
            '이번 시험에서 부교재를 제대로 소화한 학생과 그렇지 않은 학생 사이 <mark>점수 격차가 매우 크게 벌어질 것</mark>입니다. '
            '다음 시험에서도 부교재 출제 비중은 상당히 유지될 가능성이 높으므로, '
            '<b>수특·학교 부교재 반복 학습</b>이 이 학교 대비의 가장 확실한 방법입니다. '
            '단, 상위권 사이 변별은 학교 별도 자료 및 심화 응용 문항에서 갈리므로 병행 학습이 필요합니다.'
        ),
        'instructor_comment': (
            '이 학교는 <b>부교재 완주 → 8~90점 확보</b> 라는 명확한 공식이 성립합니다. '
            '수특·학교 부교재를 <b>N회독 + 오답 이유까지</b> 잡으면 대부분 대응됩니다. '
            '그 위 등급은 이영우T 심화팩으로 병행하면 안정권 확보 가능.'
        ),
        'strategy': [
            ('수특 · 학교 부교재 100% 완주', '이번 시험의 <b>핵심 대비 자료</b>. 반복이 답.'),
            ('부교재 오답 이유까지 정리', '단순 정답만 확인하지 말고 <b>왜 틀렸는지</b>까지 완벽 소화.'),
            ('상위권용 심화 병행', '변별 문항 대비는 이영우T <b>심화 응용팩</b>으로.'),
        ],
        'all_items': GWANGBUK2_ITEMS_ALL,
        'items_config': [
            {'q': 11, 'cat': 'A', 'lbl': 19, 'note': '연속 조건 상수 결정 · 수특 유형.'},
            {'q': 13, 'cat': 'C', 'lbl': 12, 'note': '정적분 함수 유도 · 부교재 빈출.'},
            {'q': 15, 'cat': 'B', 'lbl': 29, 'note': '방정식 실근 개수 · 도함수 활용.'},
            {'q': 18, 'cat': 'B', 'lbl': 33, 'note': '함수 분석·그래프 · 심화 응용.'},
        ],
    },
    {
        'key': '광문고2',
        'name': '광문고등학교 2학년',
        'no': 63,
        'grade_label': '광문고2',
        'summary_headline': '교과서 · 필수 유형 출제, 그러나 개념·정의의 정확한 이해를 묻는 시험',
        'summary_body': (
            '이번 시험은 <mark>교과서 문제와 필수 유형이 대거 출제</mark>됐지만, '
            '단순히 유형을 외운 학생이 아니라 <b>개념과 정의를 원리 수준까지 정확히 이해한 학생</b>이 고득점을 확보할 수 있는 시험이었습니다. '
            '이전 시험에서도 이러한 출제 경향이 뚜렷했으며, <b>3학년 때도 동일한 흐름이 이어질 것</b>으로 예상됩니다.'
            '<br/><br/>'
            '이 학교의 시험은 <mark>단순 기계적 풀이로는 후반부 변별 문항에서 반드시 무너집니다</mark>. '
            '"이 공식이 왜 성립하는가", "이 정의는 정확히 무엇을 의미하는가"까지 파고들지 않으면 응용 문항에서 답을 도출할 수 없는 구조로 짜여 있기 때문입니다. '
            '따라서 이 학교 대비는 <b>교과서를 여러 번 정독하고, 각 개념·정의를 스스로 설명할 수 있는 수준</b>까지 끌어올리는 것이 핵심입니다. '
            '유형서·문제집만 여러 권 풀기보다는 교과서 1권을 원리까지 완벽 소화하는 것이 훨씬 효과적입니다.'
        ),
        'instructor_comment': (
            '이 학교는 <b>"왜?"를 묻는 시험</b>입니다. 공식 외우기·유형 반복이 아니라 '
            '개념·정의를 <b>스스로 설명할 수 있는 수준</b>까지 학습해야 후반부 변별 문항에서 살아남습니다. '
            '이영우T의 <b>개념 원리 강의</b>가 이 학교 대비의 정공법.'
        ),
        'strategy': [
            ('교과서 개념·정의 원리까지 학습', '"왜 그러한가" 질문에 스스로 답할 수 있는 수준까지.'),
            ('개념 원리 강의 반복 수강', '이영우T <b>개념 원리 강의</b>로 정의·정리의 배경까지 이해.'),
            ('기계적 유형 반복 지양', '유형만 외우면 후반부 변별에서 반드시 무너집니다.'),
        ],
        'all_items': GWANGMUN2_ITEMS_ALL,
        'items_config': [
            {'q': 11, 'cat': 'A', 'lbl': 18, 'note': '극한·연속 종합 · 정의 이해 필수.'},
            {'q': 13, 'cat': 'B', 'lbl': 25, 'note': '접선·개념 정확한 이해.'},
            {'q': 17, 'cat': 'B', 'lbl': 32, 'note': '함수 극값 · 개념 응용.'},
            {'q': 19, 'cat': 'C', 'lbl': 24, 'note': '정적분 응용 (서술형) · 정의 활용.'},
        ],
    },
    {
        'key': '명문고2',
        'name': '명문고등학교 2학년',
        'no': 64,
        'grade_label': '명문고2',
        'summary_headline': '교과서 수준 · 학교대비 프린트에서 변별력 문제 출제 · 평이',
        'summary_body': (
            '이번 시험은 <mark>교과서 수준의 아주 평이한 난이도</mark>로 출제됐습니다. '
            '변별력 문항은 <b>학교에서 배포한 대비 프린트에서 그대로 이어져 왔으며</b>, '
            '참고서나 교과서만 제대로 풀어도 <mark>고득점을 쉽게 확보</mark>할 수 있는 구성이었습니다.'
            '<br/><br/>'
            '이런 시험 구성에서는 <b>단순 실수 관리와 학교 대비 프린트 소화 여부</b>가 등급을 결정합니다. '
            '상위권 학생 다수가 만점 근처에 몰릴 가능성이 크므로, 한 문항 실수도 곧바로 등급 하락으로 이어질 수 있습니다. '
            '중위권 학생은 이 시험을 <mark>기본기 완성의 절호의 기회</mark>로 활용해야 하며, '
            '평이한 난이도이기에 교과서 개념·유제 완주 + 학교 프린트 반복만으로도 <b>큰 폭의 성적 도약이 가능</b>합니다. '
            '학교 배포 프린트는 반드시 <b>오답 이유까지 완벽 소화</b>해야 다음 시험까지 성적이 이어집니다.'
        ),
        'instructor_comment': (
            '평이한 시험 + 학교 프린트 → <b>고득점 확보 공식</b>이 명확한 학교입니다. '
            '참고서·교과서 + 학교 프린트만 완주해도 안정적인 등급 확보 가능. '
            '중위권 학생에게는 <b>도약의 기회</b>가 되는 시험입니다.'
        ),
        'strategy': [
            ('교과서 · 참고서 완주', '기본만 정확히 소화해도 고득점 가능.'),
            ('학교 배포 프린트 반복', '<b>변별력 문항의 출처</b>. 반드시 오답 이유까지.'),
            ('실수 방지 계산 훈련', '평이한 시험은 실수 1개가 등급 결정.'),
        ],
        'all_items': MYEONGMUN2_ITEMS_ALL,
        'items_config': [
            {'q': 13, 'cat': 'B', 'lbl': 22, 'note': '접선 응용 · 학교 프린트 유형.'},
            {'q': 14, 'cat': 'C', 'lbl': 11, 'note': '정적분 함수 · 교과서 유형.'},
            {'q': 17, 'cat': 'B', 'lbl': 28, 'note': '실근 개수 · 학교 프린트 변별.'},
            {'q': 20, 'cat': 'B', 'lbl': 32, 'note': '함수 분석·그래프 · 학교 프린트 심화.'},
        ],
    },
]


def _prefix(school_key: str) -> str:
    return {'광명고2': '광명2_', '광명북고2': '광북2_', '광문고2': '광문2_', '명문고2': '명문2_'}[school_key]


def build_items(school: dict) -> list[dict]:
    pfx = _prefix(school['key'])
    items = []
    for it in school['items_config']:
        q = it['q']
        src_q = find_src(f'{pfx}{q}.png')
        # 매칭은 적중.png 우선, 없으면 적중1.png
        src_m = find_src(f'{pfx}{q}적중.png') or find_src(f'{pfx}{q}적중1.png')
        if not (src_q and src_m):
            print(f'  MISS: {school["key"]} Q{q} src_q={src_q} src_m={src_m}')
            continue
        items.append({
            **it,
            'exam_img': img_b64(src_q),
            'match_img': img_b64(src_m),
        })
    return items


def render_school(school: dict) -> str:
    items = build_items(school)
    all_items = school.get('all_items', [])
    total_score = sum(float(t[2]) for t in all_items) if all_items else 100.0

    css = '''
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif; color: #1c1c1c; -webkit-print-color-adjust: exact; }
mark { background: #fff2a8; padding: 0 3px; border-radius: 2px; color: inherit; font-weight: 700; }
.page { width: 210mm; height: 297mm; padding: 0; page-break-after: always; position: relative; background: #fff; overflow: hidden; }
.page:last-child { page-break-after: auto; }

.cover { background: #f2ecd8; padding: 0; }
.cover .frame { position: absolute; inset: 10mm 10mm 10mm 10mm; border: 1.5pt solid #1c1c1c; border-radius: 2mm; }
.cover .top-row { position: absolute; top: 18mm; left: 22mm; right: 22mm; display: flex; justify-content: space-between; align-items: center; font-size: 11pt; letter-spacing: 3pt; z-index: 2; }
.cover .no { color: #c33a2a; font-weight: 900; }
.cover .brand { color: #333; font-weight: 700; }
.cover .kicker { position: absolute; top: 34mm; left: 22mm; right: 22mm; color: #c33a2a; font-size: 22pt; font-weight: 800; letter-spacing: -0.5pt; z-index: 2; }
.cover .main-row { position: absolute; top: 52mm; left: 22mm; right: 22mm; display: flex; gap: 8mm; align-items: flex-start; z-index: 2; }
.cover .name-col { flex: 1; min-width: 0; }
.cover .school-big { font-size: 62pt; font-weight: 900; color: #1c1c1c; line-height: 1.0; letter-spacing: -3.5pt; white-space: nowrap; }
.cover .school-sub { font-size: 62pt; font-weight: 900; color: #1c1c1c; line-height: 1.0; letter-spacing: -3.5pt; margin-top: 3mm; white-space: nowrap; }
.cover .instructor-name-big { font-size: 62pt; font-weight: 900; color: #1c1c1c; line-height: 1.0; letter-spacing: -3.5pt; margin-top: 3mm; white-space: nowrap; }
.cover .instructor-name-big .t { color: #c33a2a; }
.cover .photo-col { flex: 0 0 auto; width: 66mm; }
.cover .photo-col .instructor-photo { width: 66mm; height: 84mm; overflow: hidden; background: transparent; }
.cover .photo-col .instructor-photo img { width: 100%; height: 100%; object-fit: cover; object-position: center top; }
.cover .hit-badge { position: absolute; bottom: 62mm; right: 30mm; width: 40mm; height: 40mm; border-radius: 50%; background: #c33a2a; color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 3; }
.cover .hit-badge .num { font-size: 32pt; font-weight: 900; line-height: 1; }
.cover .hit-badge .pct { font-size: 11pt; font-weight: 700; letter-spacing: 1pt; margin-top: 1mm; }
.cover .hit-badge::before { content: ""; position: absolute; inset: -3mm; border-radius: 50%; border: 1.5pt solid #c33a2a; }
.cover .bottom-line { position: absolute; bottom: 38mm; left: 22mm; right: 22mm; height: 0.5pt; background: #1c1c1c; z-index: 1; }
.cover .bottom-row { position: absolute; bottom: 18mm; left: 22mm; right: 22mm; display: flex; align-items: center; justify-content: space-between; z-index: 2; }
.cover .instructor-role { font-size: 8.5pt; letter-spacing: 4pt; color: #666; font-weight: 500; }
.cover .logo-block { text-align: right; }
.cover .logo-block img { width: 22mm; height: 22mm; object-fit: contain; }

.analysis { padding: 20mm 16mm; }
.badge-tag { display: inline-block; background: #c33a2a; color: #fff; padding: 3mm 8mm; border-radius: 20pt; font-size: 12pt; font-weight: 800; letter-spacing: 2pt; }
.big-title { font-size: 34pt; font-weight: 900; color: #1c1c1c; margin-top: 8mm; letter-spacing: -1pt; line-height: 1.15; }
.headline-box { margin-top: 12mm; padding: 8mm 10mm; background: #fff5e8; border-left: 5pt solid #c33a2a; border-radius: 2mm; }
.headline-box .headline-text { font-size: 18pt; font-weight: 900; color: #7a1e12; line-height: 1.35; }
.summary-body { margin-top: 10mm; font-size: 14pt; line-height: 1.8; color: #2a2a2a; }
.summary-body b { color: #c33a2a; font-weight: 800; }

.strategy { padding: 20mm 16mm; }
.strategy-title-block { margin-top: 8mm; }
.strategy-title { font-size: 30pt; font-weight: 900; color: #1c1c1c; letter-spacing: -0.5pt; line-height: 1.2; }
.strategy-card { margin-top: 8mm; padding: 7mm 10mm; background: #fafafa; border-left: 5pt solid #c33a2a; border-radius: 2mm; }
.strategy-card .row { display: flex; align-items: baseline; gap: 6mm; }
.strategy-card .num { font-size: 20pt; font-weight: 900; color: #c33a2a; letter-spacing: -0.5pt; }
.strategy-card .head { font-size: 16pt; font-weight: 800; color: #1c1c1c; }
.strategy-card .body { margin-top: 3mm; font-size: 12pt; color: #333; line-height: 1.65; padding-left: 20mm; }
.strategy-card .body b { color: #c33a2a; }
.instructor-comment { margin-top: 10mm; padding: 7mm 10mm; background: #fff2ee; border-radius: 2mm; }
.instructor-comment .comment-title { display: inline-block; background: #c33a2a; color: #fff; padding: 2mm 6mm; border-radius: 20pt; font-size: 11pt; font-weight: 800; letter-spacing: 1pt; }
.instructor-comment .comment-body { margin-top: 5mm; font-size: 12pt; line-height: 1.7; color: #333; }
.instructor-comment .comment-body b { color: #c33a2a; }

.analysis-table { padding: 14mm 12mm; }
.at-title-row { display: flex; align-items: center; gap: 4mm; }
.at-title-bar { width: 4mm; height: 10mm; background: #c33a2a; }
.at-title { font-size: 24pt; font-weight: 900; color: #1c1c1c; letter-spacing: -0.5pt; }
.at-sub { margin-top: 4mm; font-size: 12pt; color: #444; line-height: 1.6; }
.at-sub b { color: #c33a2a; font-weight: 800; }
.at-table { width: 100%; border-collapse: collapse; margin-top: 6mm; font-size: 9pt; }
.at-table th { background: #f3f0e5; color: #1c1c1c; padding: 3mm 2mm; font-weight: 800; text-align: center; font-size: 9pt; border-bottom: 2pt solid #d5cfb8; }
.at-table td { padding: 2mm 2mm; border-bottom: 0.5pt solid #eae4d0; text-align: center; }
.at-table td.q { font-weight: 700; }
.at-table td.unit { text-align: left; font-weight: 500; }
.at-table td.match { text-align: left; color: #6a1e40; font-weight: 500; font-size: 8.5pt; }
.lvl { display: inline-block; padding: 1mm 4mm; border-radius: 8pt; font-weight: 800; color: #fff; font-size: 8.5pt; min-width: 8mm; }
.lvl.하 { background: #6bce8a; color: #0f3b1e; }
.lvl.중 { background: #f3c14a; color: #4d3900; }
.lvl.상 { background: #ea6060; }

.item { padding: 16mm 14mm; }
.item .top-row { display: flex; align-items: baseline; justify-content: space-between; }
.item .idx { font-size: 11pt; color: #666; letter-spacing: 2pt; font-weight: 600; }
.item .item-title-block { display: flex; align-items: center; gap: 8mm; margin-top: 6mm; padding-bottom: 5mm; border-bottom: 2pt solid #1c1c1c; }
.item .black-tag { background: #1c1c1c; color: #fff; padding: 4mm 8mm; border-radius: 3mm; font-size: 22pt; font-weight: 900; letter-spacing: -0.5pt; }
.item .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; margin-top: 8mm; }
.item .box { border: 1pt solid #e0e0e0; border-radius: 3mm; padding: 5mm; background: #fff; min-height: 130mm; }
.item .caption { display: inline-block; padding: 2mm 6mm; border-radius: 2mm; font-size: 11pt; font-weight: 800; letter-spacing: 0.5pt; }
.item .caption.exam { background: #1c1c1c; color: #fff; }
.item .caption.match { background: #c33a2a; color: #fff; }
.item img { width: 100%; height: auto; max-height: 130mm; object-fit: contain; margin-top: 4mm; }
.item .note { position: absolute; bottom: 16mm; left: 14mm; right: 14mm; font-size: 11pt; color: #666; border-top: 1pt solid #e5e5e5; padding-top: 4mm; }
.item .note b { color: #c33a2a; }

.closing { padding: 60mm 20mm 30mm; text-align: center; }
.closing .promise-tag { display: inline-block; background: #c33a2a; color: #fff; padding: 3mm 10mm; border-radius: 20pt; font-size: 11pt; font-weight: 800; letter-spacing: 2pt; }
.closing .promise-quote { margin-top: 20mm; font-size: 24pt; font-weight: 900; color: #1c1c1c; line-height: 1.5; letter-spacing: -0.5pt; }
.closing .promise-sub { margin-top: 10mm; font-size: 14pt; color: #555; }
.closing .signoff-block { margin-top: 30mm; }
.closing .signoff-line { display: inline-block; width: 90mm; height: 1pt; background: #1c1c1c; margin: 0 auto; }
.closing .signoff { margin: 8mm 0; font-size: 26pt; font-weight: 900; color: #1c1c1c; letter-spacing: -0.5pt; }
.closing .signature { position: absolute; bottom: 40mm; left: 0; right: 0; font-size: 11pt; letter-spacing: 3pt; color: #666; }
.closing .signature .name { color: #1c1c1c; font-weight: 900; font-size: 14pt; margin-left: 8mm; }
'''

    def q_label(q):
        return str(q) if not isinstance(q, str) or '서답' not in q and '논술' not in q else q
    rows = ''
    for (q, unit, score, lvl, cat, lbl, match_desc) in all_items:
        rows += f'''<tr>
  <td class="q">{q_label(q)}</td>
  <td class="unit">{unit}</td>
  <td>{score}</td>
  <td><span class="lvl {lvl}">{lvl}</span></td>
  <td class="match">유형{lbl:02d} ─ {match_desc.split("─",1)[-1].strip()}</td>
</tr>'''

    items_html = ''
    for i, it in enumerate(items, 1):
        items_html += f'''
<section class="page item">
  <div class="top-row"><div class="idx">핵심문제 {i} / {len(items)}</div></div>
  <div class="item-title-block">
    <div class="black-tag">시험지 {it["q"]}번</div>
  </div>
  <div class="grid">
    <div class="box"><div class="caption exam">시험 출제 문항</div><img src="{it["exam_img"]}"/></div>
    <div class="box"><div class="caption match">매칭 유형</div><img src="{it["match_img"]}"/></div>
  </div>
  <div class="note">이 <b>패턴</b>은 이영우T 교재 · 핵심노트에 <b>동일 풀이 절차</b>로 정리되어 있습니다. {it["note"]}</div>
</section>'''

    strategy_html = ''.join(
        f'''<div class="strategy-card">
  <div class="row"><div class="num">0{i}</div><div class="head">{h}</div></div>
  <div class="body">{b}</div>
</div>'''
        for i, (h, b) in enumerate(school['strategy'], 1)
    )

    html = f'''<!doctype html>
<html><head><meta charset="utf-8"/><title>{school['name']} 적중분석</title>
<style>{css}</style></head><body>

<section class="page cover">
  <div class="frame"></div>
  <div class="top-row">
    <span class="no">No. {school['no']} / 2026</span>
    <span class="brand">MATHARCHIVE · 이음학원</span>
  </div>
  <div class="kicker">2026학년도 1학기 기말고사 분석</div>
  <div class="main-row">
    <div class="name-col">
      <div class="school-big">{school['grade_label']}</div>
      <div class="school-sub">수학</div>
      <div class="instructor-name-big">이영우<span class="t">T</span></div>
    </div>
    <div class="photo-col">
      <div class="instructor-photo">{f'<img src="{INSTRUCTOR_URI}"/>' if INSTRUCTOR_URI else ''}</div>
    </div>
  </div>
  <div class="hit-badge"><div class="num">100</div><div class="pct">% HIT</div></div>
  <div class="bottom-line"></div>
  <div class="bottom-row">
    <div class="instructor-role">MATH INSTRUCTOR · 이영우T</div>
    <div class="logo-block">
      {f'<img src="{EUM_LOGO_URI}"/>' if EUM_LOGO_URI else ''}
    </div>
  </div>
</section>

<section class="page analysis">
  <span class="badge-tag">SCHOOL ANALYSIS</span>
  <div class="big-title">{school['name']}<br/>이번 시험, 한눈에.</div>
  <div class="headline-box"><div class="headline-text">{school['summary_headline']}</div></div>
  <div class="summary-body">{school['summary_body']}</div>
</section>

<section class="page strategy">
  <span class="badge-tag">시험대비 전략</span>
  <div class="strategy-title-block"><div class="strategy-title">{school['name']} 맞춤 전략</div></div>
  {strategy_html}
  <div class="instructor-comment">
    <span class="comment-title">이영우T 코멘트</span>
    <div class="comment-body">{school['instructor_comment']}</div>
  </div>
</section>

<section class="page analysis-table">
  <div class="at-title-row">
    <div class="at-title-bar"></div>
    <div class="at-title">{school['name']} 출제 분석</div>
  </div>
  <div class="at-sub">이번 시험의 <b>중단원 · 배점 · 난이도 · 교재 매칭</b> 을 한눈에 정리했습니다. 총 <b>{len(all_items)}문항 · {total_score:.1f}점</b>.</div>
  <table class="at-table">
    <thead><tr>
      <th style="width:10mm;">번호</th>
      <th style="width:30mm;">중단원</th>
      <th style="width:10mm;">배점</th>
      <th style="width:12mm;">난이도</th>
      <th>교재 매칭</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>

{items_html}

<section class="page closing">
  <span class="promise-tag">이영우T의 약속</span>
  <div class="promise-quote">"{school['name']} 내신 족보,<br/>핵심노트와 교재에 모두 담았습니다."</div>
  <div class="promise-sub">이 교재를 믿고 반복하는 학생이 결국 1등급을 쟁취합니다.</div>
  <div class="signoff-block">
    <div class="signoff-line"></div>
    <div class="signoff">성적으로 증명하겠습니다.</div>
    <div class="signoff-line"></div>
  </div>
  <div class="signature">수학 Instructor <span class="name">이영우</span></div>
</section>

</body></html>'''
    return html


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for school in SCHOOLS:
            print(f'building {school["key"]} ...')
            html = render_school(school)
            html_path = OUT / f'{school["key"]}_적중분석.html'
            html_path.write_text(html, encoding='utf-8')
            page = browser.new_page()
            page.goto('file://' + str(html_path.resolve()), wait_until='networkidle')
            page.wait_for_timeout(1500)
            pdf_path = OUT / f'{school["key"]}_적중분석.pdf'
            page.pdf(path=str(pdf_path), format='A4',
                     margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'},
                     print_background=True)
            page.close()
            print(f'  → {pdf_path}')
        browser.close()
    print(f'\n완료! → {OUT}')


if __name__ == '__main__':
    main()
