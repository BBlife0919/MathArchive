"""v4 컴팩트 보고서.

- 시험 측: 시험 페이지 전체를 작게 (학생이 직관적으로 찾을 수 있게)
- 교재 측: vision 검증 후 매칭 문제 영역만 크롭한 이미지
- 한 카드가 한 페이지 안에 들어가게 컴팩트
- 한 시험문제에 여러 출처면 가로 나열
- 학교별 끝에 교재 활용도 top-2 결론
"""
from __future__ import annotations
import base64
import json
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_V3 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v3')
ROOT_V4 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v4')
EXAM_CROPS = ROOT_V4 / 'exam_crops'  # 문제별 자동 크롭(부정확)
EXAM_PAGES = ROOT_V4 / 'exam_pages'   # 페이지 전체
TB_CROPS = ROOT_V4 / 'tb_crops'


def img_b64(p: Path) -> str:
    if not p.exists():
        return ''
    return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()


def load_data():
    # 모든 매칭 (final_matches.json) + 학교별 시험 문항 목록 (final_verdicts.json)
    matches = json.load(open(ROOT_V4 / 'final_matches.json'))
    verdicts = json.load(open(ROOT_V3 / 'final_verdicts.json'))
    # 시험 문제별 매칭 모음
    by_q = {}
    for m in matches:
        key = (m['school'], m['q_no'])
        by_q.setdefault(key, []).append(m)
    return verdicts, by_q


def card(school: str, q: dict, matches: list[dict]) -> str:
    qno = q['q_no']
    # 시험 문제 표시: 크롭 부정확하므로 페이지 전체 사용
    # 페이지 번호는 bbox JSON에서 가져옴
    import json as _json
    try:
        bxs = _json.loads((ROOT_V4 / f'{school}_bboxes.json').read_text())
        page_no = next((b['page'] for b in bxs['problems'] if b['q_no'] == qno), 1)
    except Exception:
        page_no = 1
    exam_page_path = EXAM_PAGES / f'{school}_p{page_no}.png'
    exam_img = img_b64(exam_page_path) if exam_page_path.exists() else ''
    exam_page_label = f'p.{page_no}'

    if not matches:
        return f'''
<div class="card level-none">
  <div class="card-head">
    <span class="qno">Q{qno}</span>
    <span class="badge none">매칭 없음</span>
  </div>
  <div class="card-body">
    <div class="exam-col">
      <div class="col-title">시험지 {exam_page_label}</div>
      {f'<img class="exam-img" src="{exam_img}"/>' if exam_img else '<div class="no-img">시험 페이지 없음</div>'}
    </div>
    <div class="tb-col no-match">매칭된 교재 문제 없음</div>
  </div>
</div>'''

    # 매칭별 정렬: high → medium → low
    order = {'high': 0, 'medium': 1, 'low': 2}
    matches_sorted = sorted(matches, key=lambda m: order.get(m.get('confidence', 'medium'), 1))
    top_conf = matches_sorted[0].get('confidence', 'medium')
    level = 'strong' if top_conf == 'high' else ('candidate' if top_conf == 'medium' else 'low')
    badge_label = {'strong': '✅ 확실', 'candidate': '⚠️ 유사', 'low': '🔍 후보'}[level]
    n_src = len(matches_sorted)

    tb_blocks = ''
    for m in matches_sorted:
        cf = m.get('confidence', 'medium')
        cf_label = {'high': '확실', 'medium': '유사', 'low': '후보'}[cf]
        cf_color = {'high': '#2c8a4f', 'medium': '#d8a72b', 'low': '#888'}[cf]
        crop_path = TB_CROPS / m['crop_file']
        crop_img = img_b64(crop_path)
        tb_blocks += f'''
<div class="tb-item">
  <div class="tb-header">
    <span class="tb-name">📚 {m['tb_short']}</span>
    <span class="tb-page">p.{m['page']}</span>
    <span class="tb-conf" style="background:{cf_color}">{cf_label}</span>
  </div>
  <img class="tb-img" src="{crop_img}"/>
</div>'''

    return f'''
<div class="card level-{level}">
  <div class="card-head">
    <span class="qno">Q{qno}</span>
    <span class="badge {level}">{badge_label} · 출처 {n_src}곳</span>
  </div>
  <div class="card-body">
    <div class="exam-col">
      <div class="col-title">시험지 {exam_page_label}</div>
      {f'<img class="exam-img" src="{exam_img}"/>' if exam_img else '<div class="no-img">시험 페이지 없음</div>'}
    </div>
    <div class="tb-col">
      <div class="col-title">교재 출처</div>
      <div class="tb-grid">{tb_blocks}</div>
    </div>
  </div>
</div>'''


def school_conclusion(school: str, verdicts: list[dict], by_q: dict) -> str:
    cnt = Counter()
    high_cnt = Counter()
    seen_q = {}
    for v in verdicts:
        ms = by_q.get((school, v['q_no']), [])
        for m in ms:
            cnt[m['tb_short']] += 1
            if m.get('confidence') == 'high':
                high_cnt[m['tb_short']] += 1

    rows = ''
    for tb, c in cnt.most_common(8):
        h = high_cnt[tb]
        rows += f'<tr><td>{tb}</td><td class="num">{c}</td><td class="num">{h}</td></tr>'

    top2_high = high_cnt.most_common(2)
    conclusion = ''
    if top2_high:
        if len(top2_high) >= 2 and top2_high[1][1] > 0:
            conclusion = f'<b>{top2_high[0][0]}</b>(확실매칭 {top2_high[0][1]}건)과 <b>{top2_high[1][0]}</b>(확실매칭 {top2_high[1][1]}건)을 가장 많이 참고함.'
        else:
            conclusion = f'<b>{top2_high[0][0]}</b>(확실매칭 {top2_high[0][1]}건)을 주로 참고. 2순위는 확실매칭 없음.'
    else:
        conclusion = '확실매칭 데이터 부족으로 결론 보류 (학생 답안지 손글씨 가림 영향).'

    return f'''
<section class="conclusion">
  <h2>📊 {school} — 교재 참고 분석 결론</h2>
  <div class="conclusion-text">{conclusion}</div>
  <table class="conclusion-table">
    <thead><tr><th>교재</th><th>전체 매칭</th><th>확실 매칭</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>'''


def section_for_school(school: str, verdicts: list[dict], by_q: dict) -> str:
    parts = [f'<section class="school-section"><h1 class="school-title">{school}</h1>']
    n_total = len(verdicts)
    n_match = sum(1 for v in verdicts if by_q.get((school, v['q_no'])))
    n_high = sum(1 for v in verdicts
                 if any(m.get('confidence') == 'high'
                        for m in by_q.get((school, v['q_no']), [])))
    parts.append(f'<div class="summary">총 {n_total}문항 · 확실 매칭 {n_high} · 매칭(전체) {n_match}</div>')

    # 매칭 있는 것 먼저 (high 우선), 매칭 없는 것 뒤로
    def sort_key(v):
        ms = by_q.get((school, v['q_no']), [])
        if not ms:
            return (3, v['q_no'])
        confs = [m.get('confidence', 'medium') for m in ms]
        if 'high' in confs:
            return (0, v['q_no'])
        if 'medium' in confs:
            return (1, v['q_no'])
        return (2, v['q_no'])

    sorted_verdicts = sorted(verdicts, key=sort_key)
    for v in sorted_verdicts:
        ms = by_q.get((school, v['q_no']), [])
        parts.append(card(school, v, ms))

    parts.append(school_conclusion(school, verdicts, by_q))
    parts.append('</section>')
    return '\n'.join(parts)


def build(out_pdf: Path):
    verdicts, by_q = load_data()

    # 표지 요약
    summary = {}
    for school, v in verdicts.items():
        n_high = sum(1 for x in v
                     if any(m.get('confidence') == 'high'
                            for m in by_q.get((school, x['q_no']), [])))
        n_match = sum(1 for x in v if by_q.get((school, x['q_no'])))
        summary[school] = {'total': len(v), 'high': n_high, 'match': n_match,
                          'pct': round(100 * n_high / len(v)) if v else 0}

    rows = ''.join(
        f'<tr><td>{s}</td><td class="num">{m["total"]}</td><td class="num">{m["high"]}</td>'
        f'<td class="num">{m["match"]}</td><td class="num">{m["pct"]}%</td></tr>'
        for s, m in summary.items()
    )

    cover = f'''
<section class="cover">
  <h1>광명4개교 × 참고서 20종 매칭 분석 (v4)</h1>
  <h2>2026학년도 1학기 중간 (대수, 고2)</h2>
  <div class="meta">분석 일자: 2026-06-06</div>
  <ul>
    <li>분석 대상: 광명고 · 광명북고 · 광문고 · 명문고</li>
    <li>참고서 20권 (약 3,800p) · 페이지 단위 OCR + Claude vision 검증</li>
    <li>같은 템플릿(숫자만 변경)만 "확실 매칭"으로 표시</li>
    <li>한 시험문제 → 여러 교재 출처가 있으면 모두 표시</li>
  </ul>
  <div class="school-summary">
    <table>
      <thead><tr><th>학교</th><th>총문항</th><th>확실매칭</th><th>매칭(전체)</th><th>확실%</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</section>'''

    sections = [cover]
    for school, v in verdicts.items():
        sections.append(section_for_school(school, v, by_q))

    css = '''
@page { size: A4; margin: 10mm 10mm; }
* { box-sizing: border-box; }
body {
  font-family: "AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif;
  color: #222; font-size: 9pt; line-height: 1.4; margin: 0;
}
.cover {
  page-break-after: always; min-height: 250mm; padding: 18mm 8mm;
  background: linear-gradient(180deg, #fff, #eef3fa 70%);
  border: 1.5pt solid #28406d; border-radius: 6pt;
}
.cover h1 { font-size: 24pt; color:#28406d; margin: 0 0 6pt; font-weight: 900; }
.cover h2 { font-size: 13pt; color:#444; margin: 0 0 12pt; }
.cover .meta { font-size: 10pt; color:#555; }
.cover ul { font-size: 10pt; color:#333; }
.school-summary { background:#fff; border:1pt solid #b8c4d8; border-radius:4pt; margin-top: 14pt; padding: 8pt 12pt; }
.school-summary table, .conclusion-table { width:100%; border-collapse: collapse; font-size: 10pt; }
.school-summary th, .school-summary td, .conclusion-table th, .conclusion-table td {
  padding: 3pt 6pt; border-bottom: 0.5pt solid #d8dde8; text-align:left;
}
.school-summary th { background:#28406d; color:#fff; }
.school-summary td.num, .conclusion-table td.num { text-align:right; font-weight:700; }
.school-section { page-break-before: always; }
.school-title {
  font-size: 16pt; color:#fff; background:#28406d;
  padding: 3pt 7pt; border-radius: 3pt; margin: 0 0 3pt;
}
.summary { font-size: 9pt; color:#555; margin: 2pt 0 6pt; }
.card {
  border: 1pt solid #b8c4d8; border-radius: 4pt; padding: 5pt 7pt;
  margin-bottom: 5pt; page-break-inside: avoid; background: #fff;
}
.card.level-strong { border-left: 3pt solid #2c8a4f; }
.card.level-candidate { border-left: 3pt solid #d8a72b; background: #fffdf6; }
.card.level-low { border-left: 3pt solid #888; background: #f7f7f7; }
.card.level-none { border-left: 3pt solid #b54e4e; background: #fff7f7; }
.card-head { display: flex; align-items: center; gap: 6pt; margin-bottom: 3pt; font-size: 9pt; }
.qno {
  background:#28406d; color:#fff; padding: 1pt 6pt; border-radius:3pt;
  font-weight:900; font-size: 10pt; min-width: 30pt; text-align:center;
}
.badge { font-weight:700; padding: 1pt 6pt; border-radius:3pt; font-size:8.5pt; color:#fff; }
.badge.strong { background:#2c8a4f; }
.badge.candidate { background:#d8a72b; }
.badge.low { background:#888; }
.badge.none { background:#b54e4e; }
.card-body {
  display: grid;
  grid-template-columns: 0.85fr 1.15fr;
  gap: 6pt;
}
.exam-col, .tb-col {
  border: 0.5pt solid #d8dde8; border-radius: 3pt; padding: 4pt 5pt; background:#fafbfd;
}
.col-title {
  font-weight:700; color:#28406d; font-size: 8.5pt; margin-bottom: 3pt;
  border-bottom: 0.5pt solid #d8dde8; padding-bottom:2pt;
}
.exam-img {
  width: 100%; max-height: 80mm; object-fit: contain;
  border: 0.3pt solid #ccc; border-radius:2pt;
}
.no-img, .no-match { font-size: 9pt; color:#888; padding: 8pt 0; text-align:center; }
.tb-grid {
  display: flex; flex-direction: column; gap: 3pt;
}
.tb-item {
  border: 0.5pt solid #d8dde8; border-radius: 3pt; padding: 3pt 4pt; background: #fff;
}
.tb-header { display: flex; align-items: center; gap: 4pt; font-size: 8.5pt; margin-bottom: 2pt; }
.tb-name { font-weight:700; color:#28406d; }
.tb-page { color:#555; }
.tb-conf { color:#fff; padding: 1pt 5pt; border-radius:3pt; font-size: 8pt; font-weight:700; }
.tb-img {
  width: 100%; max-height: 35mm; object-fit: contain;
  border: 0.3pt solid #ccc; border-radius:2pt;
}
.conclusion {
  background: #f0f7f2; border: 1.5pt solid #2c8a4f; border-radius: 5pt;
  padding: 10pt 14pt; margin-top: 12pt; page-break-inside: avoid;
}
.conclusion h2 { font-size: 13pt; color: #1d5d36; margin: 0 0 6pt; }
.conclusion-text { font-size: 10.5pt; color: #1d5d36; margin-bottom: 8pt; line-height: 1.5; }
.conclusion-table th { background: #2c8a4f; color:#fff; }
'''

    html = f'''<!doctype html>
<html><head><meta charset="utf-8"/>
<title>광명4개교 교재 매칭 v4</title>
<style>{css}</style>
</head><body>
{''.join(sections)}
</body></html>'''

    html_path = ROOT_V4 / 'report.html'
    html_path.write_text(html)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('file://' + str(html_path.resolve()))
        page.wait_for_timeout(2000)
        page.pdf(path=str(out_pdf), format='A4',
                 margin={'top': '10mm', 'bottom': '10mm', 'left': '10mm', 'right': '10mm'},
                 print_background=True)
        browser.close()
    print(f'PDF: {out_pdf}')


if __name__ == '__main__':
    build(ROOT_V4 / '광명4개교_참고서20종_매칭보고서_v4.pdf')
