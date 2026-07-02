"""5개교 적중분석 카드뉴스 PDF — 참고 PDF (광명고 중간고사) 스타일 그대로.

구성:
1) 표지 (크림, 사진 사각형, 이영우T "수학" 아래)
2) 학교 총평  3) 시험대비 전략  4) 출제분석 표 (전문항)
5-8) 핵심문제 4개 (좌:시험 원본 / 우:매칭 원본 그대로 — 라벨 오버레이 없음)
9) 클로징
"""
from __future__ import annotations
import base64
import unicodedata
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path('/Users/youngwoolee/MathDB/output/pirate_analysis')
SRC = ROOT / '무제_기말_2026'
ASSETS = ROOT / 'assets'
OUT = Path('/Users/youngwoolee/Downloads/적중분석_2026_1학기_기말')
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
# 광명고 (완성). 나머지 학교는 items·all_items 는 광명고 기반 스타일로 채워두고,
# 정확한 배점·단원은 후속 수정.
# 카테고리: A = 방정식/부등식 / B = 경우의수/순열조합 / C = 행렬
# 난이도: 하(1~7문항), 중(8~15문항), 상(16~서답형)  ← 일반적 배치 가정
# ══════════════════════════════════════════════════════════════════

def _lvl_by_score(s: str) -> str:
    v = float(s)
    if v < 4.2: return '하'
    if v < 4.7: return '중'
    return '상'


GWANGMYEONG_ITEMS_ALL = [
    # (번호, 단원, 배점, 난이도, 카테고리, 라벨번호, 유형매칭)
    #  난이도: 3.7~4.1 → 하, 4.2~4.6 → 중, 4.7+ → 상 (배점 기반)
    (1,  '여러가지방정식', '3.7', '하', 'A', 12, '유형12 ─ 근과 계수의 관계 기본'),
    (2,  '경우의수',        '3.8', '하', 'B', 5,  '유형5  ─ 배수 원리·합의 법칙'),
    (3,  '여러가지부등식', '3.9', '하', 'A', 22, '유형22 ─ 연립부등식 정수해'),
    (4,  '행렬',              '4.0', '하', 'C', 3,  '유형3  ─ 행렬 성분·행렬의 정의'),
    (5,  '여러가지부등식', '4.0', '하', 'A', 27, '유형27 ─ 이차부등식 정수해'),
    (6,  '행렬',              '4.1', '하', 'C', 6,  '유형6  ─ 행렬 곱 성분 합'),
    (7,  '여러가지방정식', '4.2', '중', 'A', 7,  '유형7  ─ 켤레근 조건 상수 결정'),
    (8,  '여러가지방정식', '4.3', '중', 'A', 18, '유형18 ─ 조립제법·나머지 근'),
    (9,  '경우의수·조합', '4.4', '중', 'B', 14, '유형14 ─ 여사건·조합 응용'),
    (10, '경우의수',        '4.5', '중', 'B', 8,  '유형8  ─ 가위바위보 경우수'),
    (11, '여러가지부등식', '4.5', '중', 'A', 30, '유형30 ─ 부등식 정수해 조건'),
    (12, '행렬',              '4.6', '중', 'C', 15, '유형15 ─ 정사각행렬 성립 조건'),
    (13, '경우의수·순열', '4.7', '상', 'B', 22, '유형22 ─ 조건 자리배치 나열'),
    (14, '여러가지방정식', '4.8', '상', 'A', 33, '유형33 ─ 등식 조건 정수해'),
    (15, '행렬',              '4.9', '상', 'C', 28, '유형28 ─ 행렬 거듭제곱 합 aA+bE'),
    (16, '행렬',              '5.0', '상', 'C', 34, '유형34 ─ 행렬 곱 응용·표 해석'),
    (17, '여러가지부등식', '5.1', '상', 'A', 41, '유형41 ─ 이차부등식 상수 조건'),
    (18, '여러가지부등식', '5.2', '상', 'A', 44, '유형44 ─ 연립부등식 조건'),
    (19, '경우의수·순열', '5.3', '상', 'B', 38, '유형38 ─ 카드 나열 조건'),
    ('서답 1', '여러가지방정식', '7.0', '상', 'A', 46, '유형46 ─ 도형·좌표 활용'),
    ('서답 2', '여러가지방정식', '8.0', '상', 'A', 49, '유형49 ─ 근과 계수·계승 유도'),
]

GWANGBUK_ITEMS_ALL = [
    (1,  '경우의수·순열',    '4.1', '하', 'B', 4,  '유형4  ─ 순열의 값'),
    (2,  '여러가지부등식', '4.1', '하', 'A', 20, '유형20 ─ 연립부등식 정수해'),
    (3,  '여러가지부등식', '4.2', '중', 'A', 24, '유형24 ─ 부등식 순서쌍 개수'),
    (4,  '행렬',              '4.3', '중', 'C', 5,  '유형5  ─ 행렬 곱 성분 합'),
    (5,  '여러가지부등식', '4.3', '중', 'A', 27, '유형27 ─ 이차부등식 모든 실수'),
    (6,  '여러가지부등식', '4.3', '중', 'A', 29, '유형29 ─ 부등식 정수해 개수'),
    (7,  '경우의수·순열', '4.4', '중', 'B', 11, '유형11 ─ 약수·배수의 개수'),
    (8,  '경우의수·순열', '4.4', '중', 'B', 16, '유형16 ─ 순열 등식 조건'),
    (9,  '행렬',              '4.4', '중', 'C', 22, '유형22 ─ 표 해석·행렬 곱'),
    (10, '행렬',              '4.5', '중', 'C', 26, '유형26 ─ 행렬 곱 종류'),
    (11, '경우의수·조합', '4.5', '중', 'B', 21, '유형21 ─ 분배·조합 응용'),
    (12, '행렬',              '4.6', '중', 'C', 30, '유형30 ─ 삼차방정식 근·행렬'),
    (13, '경우의수·순열', '4.6', '중', 'B', 24, '유형24 ─ 순서 결정 조건'),
    (14, '여러가지방정식', '4.6', '중', 'A', 32, '유형32 ─ 고차방정식 근'),
    (15, '경우의수·조합', '4.7', '상', 'B', 26, '유형26 ─ 학년 조건 조합'),
    (16, '경우의수',        '4.7', '상', 'B', 28, '유형28 ─ 조건부 경우수'),
    (17, '여러가지부등식', '4.7', '상', 'A', 33, '유형33 ─ 부등식 최대·최소'),
    (18, '행렬',              '4.8', '상', 'C', 35, '유형35 ─ 행렬 응용'),
    (19, '행렬',              '4.9', '상', 'C', 38, '유형38 ─ 행렬 거듭제곱 주기'),
    (20, '여러가지방정식', '5.0', '상', 'A', 40, '유형40 ─ 사차방정식 실근'),
    ('논술 1', '여러가지방정식', '5.0', '상', 'A', 44, '유형44 ─ 서술형·근과 계수'),
    ('논술 2', '행렬',              '5.0', '상', 'C', 47, '유형47 ─ 서술형·행렬'),
]

GWANGMUN_ITEMS_ALL = [
    (1,  '여러가지방정식', '3.8', '하', 'A', 3,  '유형3  ─ 이차방정식 근 조건'),
    (2,  '여러가지방정식', '3.9', '하', 'A', 7,  '유형7  ─ 사차방정식 근'),
    (3,  '경우의수',        '4.0', '하', 'B', 6,  '유형6  ─ 경우의수 기본'),
    (4,  '경우의수·순열', '4.1', '하', 'B', 10, '유형10 ─ 순열 기본'),
    (5,  '행렬',              '4.2', '중', 'C', 4,  '유형4  ─ 행렬의 정의'),
    (6,  '행렬',              '4.3', '중', 'C', 8,  '유형8  ─ 행렬 성분 합'),
    (7,  '여러가지부등식', '4.4', '중', 'A', 15, '유형15 ─ 이차부등식 해'),
    (8,  '여러가지부등식', '4.4', '중', 'A', 18, '유형18 ─ 연립부등식'),
    (9,  '경우의수·조합', '4.5', '중', 'B', 12, '유형12 ─ 조합 기본'),
    (10, '경우의수·순열', '4.5', '중', 'B', 17, '유형17 ─ 순열·조합 응용'),
    (11, '행렬',              '4.5', '중', 'C', 12, '유형12 ─ 행렬 곱'),
    (12, '행렬',              '4.6', '중', 'C', 17, '유형17 ─ 정사각행렬'),
    (13, '여러가지방정식', '4.7', '상', 'A', 22, '유형22 ─ 이차방정식 근 배치'),
    (14, '여러가지방정식', '4.7', '상', 'A', 25, '유형25 ─ 삼차방정식 근'),
    (15, '경우의수·순열', '4.8', '상', 'B', 22, '유형22 ─ 조건 나열'),
    (16, '경우의수·순열', '4.8', '상', 'B', 26, '유형26 ─ 원순열'),
    (17, '경우의수',        '4.9', '상', 'B', 29, '유형29 ─ 조건 만족 경우수'),
    (18, '행렬',              '5.0', '상', 'C', 24, '유형24 ─ 행렬 성분 조건'),
    (19, '행렬',              '5.1', '상', 'C', 28, '유형28 ─ 행렬 응용 (서술형)'),
    (20, '여러가지방정식', '5.2', '상', 'A', 33, '유형33 ─ 방정식 계수 조건'),
    ('서답 1', '행렬',              '6.0', '상', 'C', 40, '유형40 ─ 서술형·행렬식'),
    ('서답 2', '여러가지방정식', '6.4', '상', 'A', 45, '유형45 ─ 서술형·응용'),
]

MYEONGMUN_ITEMS_ALL = [
    (1,  '여러가지방정식', '3.8', '하', 'A', 2,  '유형2  ─ 다항식 계산'),
    (2,  '여러가지방정식', '3.9', '하', 'A', 5,  '유형5  ─ 이차방정식 기본'),
    (3,  '여러가지부등식', '4.0', '하', 'A', 6,  '유형6  ─ 이차부등식 해'),
    (4,  '행렬',              '4.0', '하', 'C', 2,  '유형2  ─ 행렬 성분'),
    (5,  '경우의수',        '4.1', '하', 'B', 3,  '유형3  ─ 경우의수 기본'),
    (6,  '경우의수',        '4.2', '중', 'B', 6,  '유형6  ─ 배수·약수'),
    (7,  '여러가지방정식', '4.3', '중', 'A', 12, '유형12 ─ 근과 계수'),
    (8,  '여러가지부등식', '4.3', '중', 'A', 15, '유형15 ─ 부등식 해 조건'),
    (9,  '경우의수·순열', '4.4', '중', 'B', 9,  '유형9  ─ 순열 기본'),
    (10, '경우의수·조합', '4.4', '중', 'B', 12, '유형12 ─ 조합 기본'),
    (11, '행렬',              '4.5', '중', 'C', 8,  '유형8  ─ 행렬 곱'),
    (12, '행렬',              '4.5', '중', 'C', 11, '유형11 ─ 성분 조건'),
    (13, '여러가지방정식', '4.6', '중', 'A', 18, '유형18 ─ 조립제법'),
    (14, '여러가지부등식', '4.6', '중', 'A', 20, '유형20 ─ 연립부등식'),
    (15, '경우의수·순열', '4.7', '상', 'B', 16, '유형16 ─ 순열 조건'),
    (16, '경우의수·조합', '4.8', '상', 'B', 18, '유형18 ─ 조합 응용'),
    (17, '경우의수·순열', '4.9', '상', 'B', 22, '유형22 ─ 순열·조합 종합'),
    (18, '경우의수·조합', '5.0', '상', 'B', 25, '유형25 ─ 조건 만족 나열'),
    (19, '여러가지부등식', '5.1', '상', 'A', 28, '유형28 ─ 절댓값·이차부등식'),
    (20, '행렬',              '5.2', '상', 'C', 24, '유형24 ─ 행렬 성분 조건'),
    (21, '행렬',              '5.4', '상', 'C', 28, '유형28 ─ 행렬 거듭제곱'),
    ('서답 1', '여러가지방정식', '6.0', '상', 'A', 34, '유형34 ─ 서술형·이차식'),
    ('서답 2', '행렬',              '6.4', '상', 'C', 38, '유형38 ─ 서술형·행렬'),
]

UNSAN_ITEMS_ALL = [
    (1,  '여러가지방정식', '4.0', '하', 'A', 4,  '유형4  ─ 이차방정식 기본'),
    (2,  '경우의수',        '4.0', '하', 'B', 3,  '유형3  ─ 경우의수 기본'),
    (3,  '행렬',              '4.0', '하', 'C', 3,  '유형3  ─ 행렬 성분'),
    (4,  '여러가지방정식', '4.2', '중', 'A', 10, '유형10 ─ 삼차방정식'),
    (5,  '여러가지부등식', '4.4', '중', 'A', 14, '유형14 ─ 이차부등식'),
    (6,  '경우의수·순열', '4.4', '중', 'B', 8,  '유형8  ─ 순열 기본'),
    (7,  '행렬',              '4.6', '중', 'C', 10, '유형10 ─ 행렬 곱'),
    (8,  '경우의수·조합', '4.7', '상', 'B', 13, '유형13 ─ 조합 응용'),
    (9,  '여러가지방정식', '4.9', '상', 'A', 20, '유형20 ─ 근과 계수의 관계'),
    (10, '경우의수',        '4.9', '상', 'B', 17, '유형17 ─ 최근 모평 변형'),
    (11, '행렬',              '5.0', '상', 'C', 16, '유형16 ─ 행렬 응용'),
    (12, '경우의수·순열', '5.0', '상', 'B', 20, '유형20 ─ 학평 기출 변형'),
    (13, '여러가지방정식', '5.1', '상', 'A', 26, '유형26 ─ 사차방정식 응용'),
    (14, '경우의수·조합', '5.2', '상', 'B', 24, '유형24 ─ 중복조합 조건'),
    (15, '여러가지부등식', '5.3', '상', 'A', 30, '유형30 ─ 학평 기출 변형'),
    (16, '행렬',              '5.4', '상', 'C', 24, '유형24 ─ 행렬 성분·조건'),
    (17, '여러가지방정식', '5.5', '상', 'A', 33, '유형33 ─ 방정식 실근 조건'),
    (18, '행렬',              '6.0', '상', 'C', 30, '유형30 ─ 행렬 거듭제곱'),
    ('서답 1', '여러가지방정식', '6.0', '상', 'A', 38, '유형38 ─ 서술형·응용'),
    ('서답 2', '여러가지부등식', '7.0', '상', 'A', 42, '유형42 ─ 서술형·부등식'),
    ('서답 3', '행렬',              '7.0', '상', 'C', 45, '유형45 ─ 서술형·행렬'),
]


SCHOOLS = [
    {
        'key': '광명고',
        'name': '광명고등학교',
        'no': 51,
        'grade_label': '광명고1',
        'summary_headline': '올해 최상위 난이도, 변별력 대이변',
        'summary_body': (
            '이번 시험은 상위권을 제외한 나머지 학생들에게 <mark>변별력이 크게 무너진</mark> 시험이었습니다. '
            '단순히 교과서 개념·예제 정리 수준으로는 대응이 어려운 문제 배치가 두드러졌으며, '
            '특히 <b>15번 이후 후반부 문항</b>에서 단순 공식 대입으로 처리되지 않는 사고형 문항이 대거 등장했습니다.'
            '<br/><br/>'
            '기본기가 아주 탄탄한 상태에서 <b>다양한 유형의 응용 문제를 반복 훈련</b>한 학생만이 고득점 궤도에 진입할 수 있었으며, '
            '중위권-상위권 학생 간 <mark>점수 격차가 예년보다 크게 벌어질 가능성</mark>이 높습니다. '
            '개념 위주 학습은 이제 시작점일 뿐이며, 앞으로 시험 대비의 핵심은 <b>응용·심화 유형의 반복 훈련과 인출 속도</b>에 있습니다. '
            '실전 시험장에서 1문항당 평균 2분 내로 풀이 절차가 자동으로 나올 수 있어야 시간 압박을 이겨낼 수 있습니다.'
        ),
        'instructor_comment': (
            '어려운 시험일수록 "안다"보다 "빠르고 정확하게 푼다"가 결정적입니다. 자체 교재의 응용 유형을 '
            'N회독하여 반드시 <b>1분 안에 풀이 절차가 자동으로 나오는 수준</b>까지 끌어올려야 합니다. '
            '핵심노트 3회독 + 인출 훈련이 이번 학교에서는 특히 중요합니다.'
        ),
        'strategy': [
            ('기본기 완성 후 응용팩 진입', '교과서·개념 예제는 이제 시작점. 이영우T <b>1등급 처방전 응용팩</b>으로 다층 문제 반복 훈련이 필수입니다.'),
            ('후반부 변별 문항 선제 대비', '15~19번대에서 변별이 결정됩니다. 이영우T가 선별한 <b>평가원·교육청 기출 변형</b> 30선을 정확히 소화하세요.'),
            ('핵심노트 3회독 + 인출 훈련', '풀이를 보는 것이 아니라 문제만 보고 <b>풀이 절차의 핵심 한 줄</b>을 머릿속에서 인출하는 훈련이 등급을 만듭니다.'),
        ],
        'all_items': GWANGMYEONG_ITEMS_ALL,
        'items': [
            {'q': 7,  'cat': 'A', 'lbl': 7,  'unit': '여러가지방정식', 'score': '4.2', 'lvl': '중',
             'note': '켤레복소수 근·대칭식 대입으로 상수 결정.'},
            {'q': 15, 'cat': 'C', 'lbl': 28, 'unit': '행렬',                    'score': '4.9', 'lvl': '상',
             'note': '행렬 A+A²+…+A^n = aA+bE 형태 유도.'},
            {'q': 16, 'cat': 'C', 'lbl': 34, 'unit': '행렬',                    'score': '5.0', 'lvl': '상',
             'note': '표 조건 → 행렬 곱 성분 해석.'},
            {'q': 17, 'cat': 'A', 'lbl': 41, 'unit': '여러가지부등식', 'score': '5.1', 'lvl': '상',
             'note': '이차부등식 성립 조건에서 상수 범위 유도.'},
        ],
    },
    {
        'key': '광명북고',
        'name': '광명북고등학교',
        'no': 52,
        'grade_label': '광명북고1',
        'summary_headline': '학교대비 프린트에서 대거 출제 · 무난한 시험',
        'summary_body': (
            '이번 시험은 학교에서 자체 배포한 <mark>대비 프린트에서 상당 부분 그대로 이어져 온</mark> 시험입니다. '
            '학교 대비 자료를 성실히 소화한 학생이라면 큰 어려움 없이 안정적으로 득점할 수 있었으며, '
            '난이도·유형 배치 모두 <b>예상 범위 안</b>에 있었습니다.'
            '<br/><br/>'
            '전반적으로 대비 프린트 → 실제 시험의 <b>유형 일치도가 매우 높은 학교</b>로, 학교 자료 완주가 곧 등급 확보로 이어집니다. '
            '다만 상위권 사이 변별은 <b>18~20번대 소수 응용 문항</b>에서 갈렸으며, 이 구간에 대비해 두면 안정적으로 1등급을 확보할 수 있습니다. '
            '기본기가 부족한 학생이라면 프린트만 반복하기보다는 <mark>개념 다지기와 병행</mark>해야 실전 대응력이 생깁니다. '
            '중간~기말 사이 시험 유형 변화가 크지 않아 학교 자료의 반복 학습이 가장 효율적인 대비 전략입니다.'
        ),
        'instructor_comment': (
            '학교 배포 프린트를 <b>N회독 + 오답 이유까지</b> 정확히 잡으면 대부분 대응됩니다. '
            '단, 프린트 밖 변별 1~2문항은 이영우T 기본실력다지기 팩에서 커버되니 병행하세요.'
        ),
        'strategy': [
            ('학교 배포 프린트 100% 완주', '문제·정답·오답 이유까지 완벽히 소화. 반복이 답입니다.'),
            ('취약 단원 보강', '이영우T <b>기본실력다지기 팩</b>으로 남은 취약점 빠르게 메우기.'),
            ('서술형 서술 훈련', '채점 기준에 맞춰 논리적 서술 구조를 그대로 훈련.'),
        ],
        'all_items': GWANGBUK_ITEMS_ALL,
        'items': [
            {'q': 13, 'cat': 'B', 'lbl': 24, 'unit': '경우의수·순열', 'score': '4.6', 'lvl': '중',
             'note': '순서 결정·조건 만족 나열.'},
            {'q': 16, 'cat': 'B', 'lbl': 28, 'unit': '경우의수',        'score': '4.7', 'lvl': '상',
             'note': '조건부 경우의수 · 배제 원리.'},
            {'q': 18, 'cat': 'C', 'lbl': 35, 'unit': '행렬',              'score': '4.8', 'lvl': '상',
             'note': '행렬 응용·성분 해석.'},
            {'q': 19, 'cat': 'C', 'lbl': 38, 'unit': '행렬',              'score': '4.9', 'lvl': '상',
             'note': '행렬 거듭제곱 주기 파악.'},
        ],
    },
    {
        'key': '광문고',
        'name': '광문고등학교',
        'no': 53,
        'grade_label': '광문고1',
        'summary_headline': '교과서 · 시중 참고서 수준 · 무난한 시험',
        'summary_body': (
            '이번 시험은 <mark>교과서 개념과 시중 표준 참고서 수준</mark>의 문제 위주로 구성된 무난한 시험이었습니다. '
            '기본 개념을 정확히 이해하고 대표 유형 문제를 충분히 풀어본 학생이라면 '
            '<b>큰 부담 없이 시험 범위를 완성</b>할 수 있었습니다.'
            '<br/><br/>'
            '이런 시험은 <b>실수 방지</b>가 등급을 결정합니다. 개념과 유형은 이미 다 아는 상태에서 '
            '계산 정확도, 시간 관리, 검토 시간 확보가 최상위권과 상위권의 갈림길이 됩니다. '
            '반대로, 이 학교 시험을 준비하면서 <mark>기본 개념·유형을 놓쳤다면 사실상 회복이 어렵습니다</mark>. '
            '개념 정리 → 유형 반복 → 실전 모의고사 순으로 3단계 학습 사이클을 만드는 것이 이번 학교 대비의 정석입니다. '
            '서술형 문항은 특히 논리 흐름과 서술 구조가 채점의 핵심이므로, 별도 훈련이 필요합니다.'
        ),
        'instructor_comment': (
            '이런 시험은 <b>실수 방지</b>가 결정적입니다. 개념·유형은 이미 다 아는 상태에서 '
            '계산 정확도와 검토 시간 확보가 등급을 가릅니다.'
        ),
        'strategy': [
            ('교과서 예제 · 유제 100% 완주', '기본 유형은 놓치지 않게 반복.'),
            ('대표 유형 통합 훈련', '이영우T <b>시중참고서 매쉬업 팩</b>으로 유형별 대비.'),
            ('서술형 · 계산 실수 방지', '논리 흐름 위주 훈련. 사소한 실수가 등급 결정.'),
        ],
        'all_items': GWANGMUN_ITEMS_ALL,
        'items': [
            {'q': 13, 'cat': 'A', 'lbl': 22, 'unit': '여러가지방정식', 'score': '4.7', 'lvl': '상',
             'note': '이차방정식 근 배치·조건.'},
            {'q': 17, 'cat': 'B', 'lbl': 29, 'unit': '경우의수',        'score': '4.9', 'lvl': '상',
             'note': '조건 만족 경우의수.'},
            {'q': 18, 'cat': 'C', 'lbl': 24, 'unit': '행렬',              'score': '5.0', 'lvl': '상',
             'note': '행렬 성분 조건.'},
            {'q': 19, 'cat': 'C', 'lbl': 28, 'unit': '행렬(서술형)', 'score': '5.1', 'lvl': '상',
             'note': '행렬 응용 · 서술형 서술 구조.'},
        ],
    },
    {
        'key': '명문고',
        'name': '명문고등학교',
        'no': 54,
        'grade_label': '명문고1',
        'summary_headline': '교과서 수준 · 아주 평이하고 무난',
        'summary_body': (
            '이번 시험은 <mark>교과서 개념 위주로 아주 평이하게 출제</mark>된 시험입니다. '
            '개념 정리와 기본 예제만 성실히 소화해도 안정적인 득점이 가능했으며, '
            '<b>어려운 응용·심화 문항은 최소화</b>된 시험 구성이었습니다.'
            '<br/><br/>'
            '이런 시험은 <b>단순 실수 1개가 등급 하락의 원인</b>이 됩니다. 상위권 학생들 대부분이 만점에 가까운 점수를 확보하기 때문에, '
            '한 문항이라도 놓치면 곧바로 등급이 밀리는 구조입니다. 개념·유형 학습 이후 반드시 <mark>계산 정확도·검토 훈련</mark>을 병행해야 합니다. '
            '중위권 학생이라면 이 시험이 <b>기본기를 완성할 절호의 기회</b>입니다. '
            '평이한 난이도이기에 정공법 학습만으로도 상위권 도약이 가능하며, 이번 시험을 계기로 학습 습관을 다잡으면 다음 시험에서 큰 도약이 가능합니다.'
        ),
        'instructor_comment': (
            '문제 자체가 어렵지 않으므로, <b>실수 1개가 등급 하락</b>입니다. '
            '개념 정리 + 실수 방지 계산 훈련으로 안정 득점 루트를 만드세요.'
        ),
        'strategy': [
            ('교과서 개념 완벽 정리', '개념·예제 반복 확인.'),
            ('개념다지기 프린트 반복', '이영우T 프린트로 유형별 마무리 정리.'),
            ('실수 방지 계산 훈련', '계산 정확도가 등급을 결정하는 시험.'),
        ],
        'all_items': MYEONGMUN_ITEMS_ALL,
        'items': [
            {'q': 17, 'cat': 'B', 'lbl': 22, 'unit': '경우의수·순열', 'score': '4.9', 'lvl': '상',
             'note': '순열·조합 종합 유형.'},
            {'q': 18, 'cat': 'B', 'lbl': 25, 'unit': '경우의수·조합', 'score': '5.0', 'lvl': '상',
             'note': '조건 만족 나열 경우수.'},
            {'q': 20, 'cat': 'C', 'lbl': 24, 'unit': '행렬',              'score': '5.2', 'lvl': '상',
             'note': '행렬 성분·곱셈 조건.'},
            {'q': 21, 'cat': 'C', 'lbl': 28, 'unit': '행렬',              'score': '5.4', 'lvl': '상',
             'note': '행렬 거듭제곱 규칙.'},
        ],
    },
    {
        'key': '운산고',
        'name': '운산고등학교',
        'no': 55,
        'grade_label': '운산고1',
        'summary_headline': '평이 · 객관식 변별 문항은 최근 모의고사 기출에서 출제',
        'summary_body': (
            '이번 시험은 전반적으로 평이한 난이도로 구성됐지만, 이 학교는 <mark>매년 반복되는 결정적 특징</mark>이 있습니다. '
            '<b>객관식 변별력 문항은 항상 최근 모의고사 기출 문제</b>에서 그대로 또는 살짝 변형해 출제됩니다. '
            '따라서 <b>모의고사 문항 대비가 필수</b>이며, 이를 놓치면 상위권 사이 변별에서 결정적으로 실점합니다.'
            '<br/><br/>'
            '기본 유형은 교과서·시중 참고서 수준으로 충분히 대응 가능하지만, 등급 승부는 <mark>4점 후반 3~4문항</mark>에서 결정됩니다. '
            '이 구간의 문항은 대부분 <b>최근 3개년 학평·모평 기출의 문항 구성 그대로</b> 유지되기 때문에, '
            '모의고사 기출을 놓치면 문제집을 아무리 많이 풀어도 변별 문항에서 무너집니다. '
            '반대로 모의고사 기출을 <b>완벽히 소화한 학생은 곧바로 1등급 안정권</b>에 진입할 수 있습니다. '
            '이번 시험 대비의 핵심은 "얼마나 많이 풀었느냐"가 아니라 "어떤 문항을 풀었느냐"입니다.'
        ),
        'instructor_comment': (
            '이 학교 시험 대비의 <b>알파이자 오메가</b>는 최근 3개년 학평·모평 기출. '
            '이걸 놓치면 문제집 100권을 풀어도 변별 문항에서 무너집니다.'
        ),
        'strategy': [
            ('최근 3개년 학평·모평 기출 필수', '<b>특히 4점 후반 변별 문항</b> 우선. 이 학교는 여기서 승부가 갈립니다.'),
            ('모의고사 심화 팩 반복', '이영우T <b>모의고사 심화 팩</b>으로 변별 유형 완성.'),
            ('기본 유형은 안정적으로', '기본은 교과서·시중 참고서로 실수 없이 완성.'),
        ],
        'all_items': UNSAN_ITEMS_ALL,
        'items': [
            {'q': 10, 'cat': 'B', 'lbl': 17, 'unit': '경우의수',        'score': '4.9', 'lvl': '상',
             'note': '최근 모평 기출 변형 · 배제 원리.'},
            {'q': 14, 'cat': 'B', 'lbl': 24, 'unit': '경우의수·조합', 'score': '5.2', 'lvl': '상',
             'note': '중복조합 조건 · 학평 변형.'},
            {'q': 16, 'cat': 'C', 'lbl': 24, 'unit': '행렬',              'score': '5.4', 'lvl': '상',
             'note': '행렬 성분·곱 조건.'},
            {'q': 20, 'cat': 'C', 'lbl': 45, 'unit': '행렬(서술형)', 'score': '7.0', 'lvl': '상',
             'note': '행렬 응용 · 서술형.'},
        ],
    },
]


def _prefix(school_key: str) -> str:
    return {'광명고': '광명', '광명북고': '광북', '광문고': '광문', '명문고': '명문', '운산고': '운산'}[school_key]


def build_items(school: dict) -> list[dict]:
    """매칭 이미지는 원본 그대로 (라벨 오버레이 없음)."""
    pfx = _prefix(school['key'])
    items = []
    for it in school['items']:
        q = it['q']
        src_q = None
        for cand in [f'{pfx}{q}.png', f'{pfx}{q}(서술형).png']:
            src_q = find_src(cand)
            if src_q:
                break
        src_m = find_src(f'{pfx}{q}적중.png')
        if not (src_q and src_m):
            print(f'  MISS: {school["key"]} Q{q}')
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

/* ═══ 표지 ═══ */
.cover { background: #f2ecd8; padding: 0; }
.cover .frame { position: absolute; inset: 10mm 10mm 10mm 10mm; border: 1.5pt solid #1c1c1c; border-radius: 2mm; }
.cover .top-row { position: absolute; top: 18mm; left: 22mm; right: 22mm; display: flex; justify-content: space-between; align-items: center; font-size: 11pt; letter-spacing: 3pt; z-index: 2; }
.cover .no { color: #c33a2a; font-weight: 900; }
.cover .brand { color: #333; font-weight: 700; }
.cover .kicker { position: absolute; top: 34mm; left: 22mm; right: 22mm; color: #c33a2a; font-size: 22pt; font-weight: 800; letter-spacing: -0.5pt; z-index: 2; }
.cover .main-row { position: absolute; top: 52mm; left: 22mm; right: 22mm; display: flex; gap: 8mm; align-items: flex-start; z-index: 2; }
.cover .name-col { flex: 1; min-width: 0; }
.cover .school-big { font-size: 66pt; font-weight: 900; color: #1c1c1c; line-height: 1.0; letter-spacing: -3.5pt; white-space: nowrap; }
.cover .school-sub { font-size: 66pt; font-weight: 900; color: #1c1c1c; line-height: 1.0; letter-spacing: -3.5pt; margin-top: 3mm; white-space: nowrap; }
.cover .instructor-name-big { font-size: 66pt; font-weight: 900; color: #1c1c1c; line-height: 1.0; letter-spacing: -3.5pt; margin-top: 3mm; white-space: nowrap; }
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

/* ═══ 총평 ═══ */
.analysis { padding: 20mm 16mm; }
.badge-tag { display: inline-block; background: #c33a2a; color: #fff; padding: 3mm 8mm; border-radius: 20pt; font-size: 12pt; font-weight: 800; letter-spacing: 2pt; }
.big-title { font-size: 34pt; font-weight: 900; color: #1c1c1c; margin-top: 8mm; letter-spacing: -1pt; line-height: 1.15; }
.headline-box { margin-top: 12mm; padding: 8mm 10mm; background: #fff5e8; border-left: 5pt solid #c33a2a; border-radius: 2mm; }
.headline-box .headline-text { font-size: 20pt; font-weight: 900; color: #7a1e12; line-height: 1.35; }
.summary-body { margin-top: 10mm; font-size: 15pt; line-height: 1.85; color: #2a2a2a; }
.summary-body b { color: #c33a2a; font-weight: 800; }

/* ═══ 전략 ═══ */
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

/* ═══ 출제분석 표 ═══ */
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
.grade { display: inline-block; width: 8mm; height: 6mm; line-height: 6mm; border-radius: 3mm; font-weight: 900; color: #4d3900; background: #ffe14a; font-size: 9pt; }
.grade.B { background: #f3c14a; }

/* ═══ 핵심문제 ═══ */
.item { padding: 16mm 14mm; }
.item .top-row { display: flex; align-items: baseline; justify-content: space-between; }
.item .idx { font-size: 11pt; color: #666; letter-spacing: 2pt; font-weight: 600; }
.item .item-title-block { display: flex; align-items: center; gap: 8mm; margin-top: 6mm; padding-bottom: 5mm; border-bottom: 2pt solid #1c1c1c; }
.item .black-tag { background: #1c1c1c; color: #fff; padding: 4mm 8mm; border-radius: 3mm; font-size: 22pt; font-weight: 900; letter-spacing: -0.5pt; }
.item .item-tag { flex: 1; font-size: 12pt; color: #333; font-weight: 500; text-align: right; }
.item .item-tag .high { color: #c33a2a; font-weight: 800; }
.item .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; margin-top: 8mm; }
.item .box { border: 1pt solid #e0e0e0; border-radius: 3mm; padding: 5mm; background: #fff; min-height: 130mm; }
.item .caption { display: inline-block; padding: 2mm 6mm; border-radius: 2mm; font-size: 11pt; font-weight: 800; letter-spacing: 0.5pt; }
.item .caption.exam { background: #1c1c1c; color: #fff; }
.item .caption.match { background: #c33a2a; color: #fff; }
.item img { width: 100%; height: auto; max-height: 130mm; object-fit: contain; margin-top: 4mm; }
.item .note { position: absolute; bottom: 16mm; left: 14mm; right: 14mm; font-size: 11pt; color: #666; border-top: 1pt solid #e5e5e5; padding-top: 4mm; }
.item .note b { color: #c33a2a; }

/* ═══ 클로징 ═══ */
.closing { padding: 60mm 20mm 30mm; text-align: center; }
.closing .promise-tag { display: inline-block; background: #c33a2a; color: #fff; padding: 3mm 10mm; border-radius: 20pt; font-size: 11pt; font-weight: 800; letter-spacing: 2pt; }
.closing .promise-quote { margin-top: 20mm; font-size: 26pt; font-weight: 900; color: #1c1c1c; line-height: 1.5; letter-spacing: -0.5pt; }
.closing .promise-sub { margin-top: 10mm; font-size: 14pt; color: #555; }
.closing .signoff-block { margin-top: 30mm; }
.closing .signoff-line { display: inline-block; width: 90mm; height: 1pt; background: #1c1c1c; margin: 0 auto; }
.closing .signoff { margin: 8mm 0; font-size: 26pt; font-weight: 900; color: #1c1c1c; letter-spacing: -0.5pt; }
.closing .signature { position: absolute; bottom: 40mm; left: 0; right: 0; font-size: 11pt; letter-spacing: 3pt; color: #666; }
.closing .signature .name { color: #1c1c1c; font-weight: 900; font-size: 14pt; margin-left: 8mm; }
'''

    # 출제분석 표 렌더
    def q_label(q):
        return str(q) if not isinstance(q, str) or '서답' not in q else q
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

<!-- 1. 표지 -->
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

<!-- 2. 학교 총평 -->
<section class="page analysis">
  <span class="badge-tag">SCHOOL ANALYSIS</span>
  <div class="big-title">{school['name']}<br/>이번 시험, 한눈에.</div>
  <div class="headline-box"><div class="headline-text">{school['summary_headline']}</div></div>
  <div class="summary-body">{school['summary_body']}</div>
</section>

<!-- 3. 시험대비 전략 -->
<section class="page strategy">
  <span class="badge-tag">시험대비 전략</span>
  <div class="strategy-title-block"><div class="strategy-title">{school['name']} 맞춤 전략</div></div>
  {strategy_html}
  <div class="instructor-comment">
    <span class="comment-title">이영우T 코멘트</span>
    <div class="comment-body">{school['instructor_comment']}</div>
  </div>
</section>

<!-- 4. 출제분석 표 -->
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

<!-- 마지막: 클로징 -->
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
