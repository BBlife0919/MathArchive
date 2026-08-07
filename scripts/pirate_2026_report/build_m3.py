"""철산중 3학년 적중분석 PDF — 저작권 블러 스트라이프 적용."""
from __future__ import annotations
import base64
import sys
import unicodedata
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from blur_copyright import apply_blur_stripes  # noqa

ROOT = Path('/Users/youngwoolee/MathDB/output/pirate_analysis')
SRC = ROOT / '무제_기말_2026_중3'
BLUR = ROOT / '무제_기말_2026_중3_blur'
BLUR.mkdir(parents=True, exist_ok=True)
ASSETS = ROOT / 'assets'
OUT = Path('/Users/youngwoolee/Downloads/적중분석_2026_1학기_기말_중3')
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


# 카테고리 (중3 1학기 기말): A = 이차방정식 / B = 이차함수 / C = 이차함수와 그래프 응용
CHULSAN_ITEMS_ALL = [
    (1,  '이차방정식',              '3.8', '하', 'A', 2,  '유형2  ─ 이차방정식 근 계산'),
    (2,  '이차방정식',              '3.9', '하', 'A', 5,  '유형5  ─ 근과 계수의 관계'),
    (3,  '이차함수',                    '4.0', '하', 'B', 3,  '유형3  ─ 이차함수 기본 그래프'),
    (4,  '이차함수',                    '4.1', '하', 'B', 6,  '유형6  ─ 꼭짓점·축 조건'),
    (5,  '이차방정식',              '4.2', '중', 'A', 10, '유형10 ─ 판별식 조건'),
    (6,  '이차함수',                    '4.2', '중', 'B', 9,  '유형9  ─ 이차함수 그래프의 이동'),
    (7,  '이차방정식·활용',      '4.3', '중', 'A', 14, '유형14 ─ 방정식 활용 · 도형 조건'),
    (8,  '이차함수',                    '4.3', '중', 'B', 13, '유형13 ─ 이차함수 최대·최소'),
    (9,  '이차방정식',              '4.4', '중', 'A', 18, '유형18 ─ 근의 배치 조건'),
    (10, '이차함수',                    '4.4', '중', 'B', 17, '유형17 ─ 그래프 특성 종합'),
    (11, '이차함수·활용',          '4.5', '중', 'C', 8,  '유형8  ─ 이차함수 활용 기본'),
    (12, '이차함수',                    '4.5', '중', 'B', 20, '유형20 ─ 이차함수 판정'),
    (13, '이차방정식',              '4.6', '중', 'A', 22, '유형22 ─ 실근 조건 종합'),
    (14, '이차함수·활용',          '4.6', '중', 'C', 12, '유형12 ─ 활용 · 도형과 함수'),
    (15, '이차함수',                    '4.7', '상', 'B', 24, '유형24 ─ 그래프 종합'),
    (16, '이차함수·활용',          '4.8', '상', 'C', 16, '유형16 ─ 이차함수 그래프 활용'),
    (17, '이차방정식·이차함수', '4.9', '상', 'C', 20, '유형20 ─ 방정식·함수 종합'),
    (18, '이차함수',                    '5.0', '상', 'B', 27, '유형27 ─ 미정계수 결정'),
    (19, '이차방정식',              '5.1', '상', 'A', 30, '유형30 ─ 근과 조건 종합'),
    (20, '이차함수',                    '5.2', '상', 'B', 32, '유형32 ─ 그래프 응용'),
    ('서답 1', '이차방정식',       '6.0', '상', 'A', 36, '유형36 ─ 서술형·근 조건'),
    ('서답 2', '이차함수',           '6.4', '상', 'C', 40, '유형40 ─ 서술형·이차함수 활용'),
]


SCHOOL = {
    'key': '철산중3',
    'name': '철산중학교 3학년',
    'no': 71,
    'grade_label': '철산중3',
    'summary_headline': '평이한 난이도 · 학교 프린트에서 대거 출제 · 상위권 95~100 다수 분포 예상',
    'summary_body': (
        '이번 시험은 <b>평이한 난이도</b>로 출제됐으며, <mark>학교에서 배부된 프린트 자료에서 상당수 문항이 그대로 이어져 온 시험</mark>이었습니다. '
        '학교 프린트를 성실히 소화한 학생이라면 무리 없이 안정적인 득점이 가능했으며, '
        '<b>상위권 학생들은 95~100점 구간에 다수 분포</b>할 것으로 예상됩니다.'
        '<br/><br/>'
        '이 학교 시험 대비 공식은 명확합니다. <b>학교에서 배부된 프린트를 열심히 복습하고, 심화 교재를 다회독으로 착실히 공부</b>하면 큰 무리 없이 고득점을 확보할 수 있습니다. '
        '기본 개념·유형은 이미 대부분 커버되므로, 문제는 <mark>실수 관리와 심화 응용 문항 대응력</mark>입니다. '
        '실수 한 문항이 등급을 결정하는 시험이므로 계산 정확도·검토 훈련이 특히 중요하며, '
        '상위권 안에서 갈리는 <b>변별 3~4문항은 심화 교재의 응용 유형</b>에서 그대로 이어져 나옵니다. '
        '학교 프린트만으로는 이 변별 문항을 완전히 대비하기 어려우므로 심화 병행이 필수입니다. '
        '<br/><br/>'
        '본원에서는 <b>자체 교재에서 다룬 유형이 이번 시험에 고루 잘 반영</b>되어 출제됐으며, '
        '학교 프린트 · 자체 교재 · 심화 응용을 3단계로 병행 학습한 학생은 안정적으로 만점권에 도달할 수 있었습니다.'
    ),
    'instructor_comment': (
        '이 학교 대비의 <b>알파이자 오메가</b>는 학교 프린트 반복 + 심화 다회독. '
        '평이한 시험은 곧 실수·응용력 승부입니다. '
        '학교 자료를 완전히 소화한 뒤 이영우T <b>심화 응용팩</b>으로 만점권을 확보하세요.'
    ),
    'strategy': [
        ('학교 배부 프린트 100% 반복 학습', '문제 · 정답 · 오답 이유까지 완벽히 소화. 이 학교의 <b>필수 대비 자료</b>.'),
        ('심화 교재 다회독 병행', '변별 3~4문항은 심화 응용에서 나옵니다. 이영우T <b>심화팩</b> N회독 필수.'),
        ('실수 방지 계산 훈련', '평이한 시험은 실수 1개가 등급 결정. 계산 정확도·검토 훈련 병행.'),
    ],
    'all_items': CHULSAN_ITEMS_ALL,
    'items_config': [
        {'q': 7,  'cat': 'A', 'note': '이차방정식 활용 · 도형·길이 조건에서 근 유도.'},
        {'q': 14, 'cat': 'C', 'note': '이차함수 활용 · 도형·함수 결합 유형.'},
        {'q': 16, 'cat': 'C', 'note': '이차함수 그래프 활용 · 조건 만족 유도.'},
        {'q': 17, 'cat': 'C', 'note': '이차방정식·이차함수 종합 · 심화 응용 유형.'},
    ],
}


def build_items(school: dict) -> list[dict]:
    """원본 문제 이미지에 저작권 블러 적용. 매칭 이미지는 그대로."""
    items = []
    for it in school['items_config']:
        q = it['q']
        src_q = find_src(f'철산중3_{q}번.png')
        src_m = find_src(f'철산중3_{q}번적중.png')
        if not (src_q and src_m):
            print(f'  MISS: Q{q} src_q={src_q} src_m={src_m}')
            continue
        # 저작권 블러
        dst_q = BLUR / f'Q{q:02d}_blur.png'
        apply_blur_stripes(src_q, dst_q)
        items.append({
            **it,
            'exam_img': img_b64(dst_q),
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
.headline-box { margin-top: 10mm; padding: 7mm 10mm; background: #fff5e8; border-left: 5pt solid #c33a2a; border-radius: 2mm; }
.headline-box .headline-text { font-size: 16pt; font-weight: 900; color: #7a1e12; line-height: 1.35; }
.summary-body { margin-top: 8mm; font-size: 12.5pt; line-height: 1.75; color: #2a2a2a; }
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
.item .copyright-note { position: absolute; bottom: 4mm; left: 14mm; right: 14mm; font-size: 8pt; color: #999; text-align: center; }

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
        return str(q) if not isinstance(q, str) or ('서답' not in q and '논술' not in q) else q
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
  <div class="copyright-note">※ 시험 출제 문항은 저작권 보호를 위해 일부 영역을 흐림 처리했습니다.</div>
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
      <th style="width:32mm;">중단원</th>
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
        print(f'building {SCHOOL["key"]} ...')
        html = render_school(SCHOOL)
        html_path = OUT / f'{SCHOOL["key"]}_적중분석.html'
        html_path.write_text(html, encoding='utf-8')
        page = browser.new_page()
        page.goto('file://' + str(html_path.resolve()), wait_until='networkidle')
        page.wait_for_timeout(1500)
        pdf_path = OUT / f'{SCHOOL["key"]}_적중분석.pdf'
        page.pdf(path=str(pdf_path), format='A4',
                 margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'},
                 print_background=True)
        page.close()
        print(f'  → {pdf_path}')
        browser.close()


if __name__ == '__main__':
    main()
