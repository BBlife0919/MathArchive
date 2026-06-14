"""v4 1:1 매칭 보고서.

- 시험문제 N개 → 카드 N개
- 카드 = 시험 크롭 1개 ↔ 교재 크롭 1개 (best 매칭)
- 매칭 없으면 "매칭 없음" 표시
- 카드 컴팩트 — 한 페이지에 여러 카드
"""
from __future__ import annotations
import base64
import json
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_V3 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v3')
ROOT_V4 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v4')
EX_CROPS = ROOT_V4 / 'exam_crops_v2'
TB_CROPS = ROOT_V4 / 'tb_crops'


def img_b64(p: Path) -> str:
    if not p.exists():
        return ''
    return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()


CONF_ORDER = {'high': 0, 'medium': 1, 'low': 2}


def best_match(matches: list[dict]) -> dict | None:
    if not matches:
        return None
    return sorted(matches, key=lambda m: CONF_ORDER.get(m.get('confidence', 'medium'), 1))[0]


def card(school: str, q_no: int, q_text: str, match: dict | None) -> str:
    exam_img = img_b64(EX_CROPS / f'{school}_Q{q_no:02d}.png')

    if not match:
        return f'''
<div class="card level-none">
  <div class="card-head">
    <span class="qno">Q{q_no}</span>
    <span class="badge none">매칭 없음</span>
  </div>
  <div class="card-body">
    <div class="exam-col">
      {f'<img class="exam-img" src="{exam_img}"/>' if exam_img else '<div class="no-img">크롭 없음</div>'}
    </div>
    <div class="tb-col">
      <div class="no-match">매칭된 교재 문제 없음</div>
    </div>
  </div>
</div>'''

    cf = match.get('confidence', 'medium')
    level = 'strong' if cf == 'high' else ('candidate' if cf == 'medium' else 'low')
    badge_label = {'strong': '✅ 확실', 'candidate': '⚠️ 유사', 'low': '🔍 후보'}[level]
    tb_img = img_b64(TB_CROPS / match['crop_file'])

    return f'''
<div class="card level-{level}">
  <div class="card-head">
    <span class="qno">Q{q_no}</span>
    <span class="badge {level}">{badge_label}</span>
    <span class="src-ref">📚 {match['tb_short']} · p.{match['page']}</span>
  </div>
  <div class="card-body">
    <div class="exam-col">
      {f'<img class="exam-img" src="{exam_img}"/>' if exam_img else '<div class="no-img">크롭 없음</div>'}
    </div>
    <div class="tb-col">
      <img class="tb-img" src="{tb_img}"/>
    </div>
  </div>
</div>'''


def school_conclusion(school: str, best_matches: list[dict | None]) -> str:
    cnt = Counter()
    high_cnt = Counter()
    for m in best_matches:
        if not m:
            continue
        cnt[m['tb_short']] += 1
        if m.get('confidence') == 'high':
            high_cnt[m['tb_short']] += 1

    rows = ''
    for tb, c in cnt.most_common(8):
        h = high_cnt[tb]
        rows += f'<tr><td>{tb}</td><td class="num">{c}</td><td class="num">{h}</td></tr>'

    top2 = high_cnt.most_common(2)
    if top2:
        if len(top2) >= 2 and top2[1][1] > 0:
            conclusion = f'<b>{top2[0][0]}</b>(확실 {top2[0][1]}건)과 <b>{top2[1][0]}</b>(확실 {top2[1][1]}건)을 가장 많이 참고함.'
        else:
            conclusion = f'<b>{top2[0][0]}</b>(확실 {top2[0][1]}건)을 주로 참고. 2순위는 확실매칭 없음.'
    else:
        conclusion = '확실매칭 부족으로 결론 보류 (학생 답안지 손글씨 가림 영향).'

    return f'''
<section class="conclusion">
  <h2>📊 {school} — 교재 참고 분석 결론</h2>
  <div class="conclusion-text">{conclusion}</div>
  <table class="conclusion-table">
    <thead><tr><th>교재</th><th>매칭</th><th>확실</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>'''


def section_for_school(school: str, verdicts: list[dict], by_q: dict) -> str:
    parts = [f'<section class="school-section"><h1 class="school-title">{school}</h1>']
    n_total = len(verdicts)
    best_matches = []
    for v in verdicts:
        ms = by_q.get((school, v['q_no']), [])
        best_matches.append(best_match(ms))

    n_high = sum(1 for m in best_matches if m and m.get('confidence') == 'high')
    n_match = sum(1 for m in best_matches if m)
    parts.append(f'<div class="summary">총 {n_total}문항 · 확실 매칭 {n_high} · 매칭(전체) {n_match}</div>')

    for v, m in zip(verdicts, best_matches):
        parts.append(card(school, v['q_no'], v.get('q_text', ''), m))

    parts.append(school_conclusion(school, best_matches))
    parts.append('</section>')
    return '\n'.join(parts)


def build(out_pdf: Path):
    verdicts = json.load(open(ROOT_V3 / 'final_verdicts.json'))
    final = json.load(open(ROOT_V4 / 'final_matches.json'))
    by_q = {}
    for m in final:
        by_q.setdefault((m['school'], m['q_no']), []).append(m)

    # 표지 요약
    summary = {}
    for school, vs in verdicts.items():
        bms = [best_match(by_q.get((school, v['q_no']), [])) for v in vs]
        n_high = sum(1 for m in bms if m and m.get('confidence') == 'high')
        n_match = sum(1 for m in bms if m)
        summary[school] = {'total': len(vs), 'high': n_high, 'match': n_match,
                          'pct': round(100 * n_high / len(vs)) if vs else 0}

    rows = ''.join(
        f'<tr><td>{s}</td><td class="num">{m["total"]}</td><td class="num">{m["high"]}</td>'
        f'<td class="num">{m["match"]}</td><td class="num">{m["pct"]}%</td></tr>'
        for s, m in summary.items()
    )

    cover = f'''
<section class="cover">
  <h1>광명4개교 × 참고서 20종 매칭 분석</h1>
  <h2>2026학년도 1학기 중간 (대수, 고2) — 1:1 매칭</h2>
  <div class="meta">분석 일자: 2026-06-06</div>
  <ul>
    <li>분석 대상: 광명고 · 광명북고 · 광문고 · 명문고</li>
    <li>참고서 20권 (약 3,800p)</li>
    <li>각 시험문제마다 가장 신뢰도 높은 매칭 1개를 1:1로 표시</li>
    <li>같은 템플릿(숫자만 변경)만 "확실 매칭"으로 표시</li>
  </ul>
  <div class="school-summary">
    <table>
      <thead><tr><th>학교</th><th>총문항</th><th>확실매칭</th><th>매칭(전체)</th><th>확실%</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</section>'''

    sections = [cover]
    for school, vs in verdicts.items():
        sections.append(section_for_school(school, vs, by_q))

    css = '''
@page { size: A4; margin: 8mm 8mm; }
* { box-sizing: border-box; }
body {
  font-family: "AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif;
  color: #222; font-size: 9pt; line-height: 1.4; margin: 0;
}
.cover {
  page-break-after: always; min-height: 270mm; padding: 16mm 8mm;
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
  border: 1pt solid #b8c4d8; border-radius: 4pt; padding: 4pt 6pt;
  margin-bottom: 4pt; page-break-inside: avoid; background: #fff;
}
.card.level-strong { border-left: 3pt solid #2c8a4f; }
.card.level-candidate { border-left: 3pt solid #d8a72b; background: #fffdf6; }
.card.level-low { border-left: 3pt solid #888; background: #f7f7f7; }
.card.level-none { border-left: 3pt solid #b54e4e; background: #fff7f7; }
.card-head { display: flex; align-items: center; gap: 6pt; margin-bottom: 3pt; font-size: 9pt; flex-wrap: wrap; }
.qno {
  background:#28406d; color:#fff; padding: 1pt 6pt; border-radius:3pt;
  font-weight:900; font-size: 10pt; min-width: 30pt; text-align:center;
}
.badge { font-weight:700; padding: 1pt 6pt; border-radius:3pt; font-size:8.5pt; color:#fff; }
.badge.strong { background:#2c8a4f; }
.badge.candidate { background:#d8a72b; }
.badge.low { background:#888; }
.badge.none { background:#b54e4e; }
.src-ref { font-size: 9pt; color:#28406d; font-weight:700; }
.card-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6pt;
}
.exam-col, .tb-col {
  border: 0.5pt solid #d8dde8; border-radius: 3pt; padding: 3pt; background:#fafbfd;
  min-height: 30mm;
  display: flex; align-items: center; justify-content: center;
}
.exam-img, .tb-img {
  max-width: 100%; max-height: 55mm; object-fit: contain;
  border: 0.3pt solid #ccc; border-radius:2pt;
}
.no-img, .no-match { font-size: 9pt; color:#888; text-align:center; padding: 8pt 0; }
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
<title>광명4개교 1:1 매칭</title>
<style>{css}</style>
</head><body>
{''.join(sections)}
</body></html>'''

    html_path = ROOT_V4 / 'report_11.html'
    html_path.write_text(html)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('file://' + str(html_path.resolve()))
        page.wait_for_timeout(2000)
        page.pdf(path=str(out_pdf), format='A4',
                 margin={'top': '8mm', 'bottom': '8mm', 'left': '8mm', 'right': '8mm'},
                 print_background=True)
        browser.close()
    print(f'PDF: {out_pdf}')


if __name__ == '__main__':
    build(ROOT_V4 / '광명4개교_매칭보고서_1대1.pdf')
