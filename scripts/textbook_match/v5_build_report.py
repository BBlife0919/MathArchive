"""v5 최종 1:1 보고서.

광명고 / 광명북고만. 각 시험문제 ↔ best 매칭 1개 (또는 매칭 없음).
시험 크롭은 PDF 텍스트 레이어로 자동 추출 (정확).
교재 크롭은 vision agent로 매칭 문제 영역만 추출.
"""
from __future__ import annotations
import base64
import json
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_V3 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v3')
ROOT_V5 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v5')
EX_CROPS = ROOT_V5 / 'exam_crops'
TB_CROPS = ROOT_V5 / 'tb_crops'


def img_b64(p: Path) -> str:
    if not p.exists():
        return ''
    return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()


CONF_ORDER = {'high': 0, 'medium': 1, 'low': 2}


def card(school: str, qno: int, qname: str, match: dict | None) -> str:
    # 시험 크롭
    if qno >= 100:
        exam_path = EX_CROPS / f'{school}_QS{qno-100}.png'
    else:
        exam_path = EX_CROPS / f'{school}_Q{qno:02d}.png'
    exam_img = img_b64(exam_path)
    qlabel = f'Q서답형{qno-100}' if qno >= 100 else f'Q{qno}'

    if not match:
        return f'''
<div class="card level-none">
  <div class="card-head">
    <span class="qno">{qlabel}</span>
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
    <span class="qno">{qlabel}</span>
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


def school_conclusion(school: str, matches: list[dict | None]) -> str:
    cnt = Counter()
    high_cnt = Counter()
    for m in matches:
        if not m:
            continue
        cnt[m['tb_short']] += 1
        if m.get('confidence') == 'high':
            high_cnt[m['tb_short']] += 1

    rows = ''
    for tb, c in cnt.most_common(10):
        h = high_cnt[tb]
        rows += f'<tr><td>{tb}</td><td class="num">{c}</td><td class="num">{h}</td></tr>'

    top2 = high_cnt.most_common(2)
    if top2:
        if len(top2) >= 2 and top2[1][1] > 0:
            conclusion = f'<b>{top2[0][0]}</b>(확실 {top2[0][1]}건)과 <b>{top2[1][0]}</b>(확실 {top2[1][1]}건)을 가장 많이 참고함.'
        else:
            conclusion = f'<b>{top2[0][0]}</b>(확실 {top2[0][1]}건)을 주로 참고. 2순위는 확실매칭 없음.'
    else:
        conclusion = '확실매칭 부족으로 결론 보류.'

    return f'''
<section class="conclusion">
  <h2>📊 {school} — 교재 참고 분석 결론</h2>
  <div class="conclusion-text">{conclusion}</div>
  <table class="conclusion-table">
    <thead><tr><th>교재</th><th>매칭</th><th>확실</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>'''


def section_for_school(school: str) -> str:
    verdicts = json.load(open(ROOT_V5 / f'visual_matches_{school}.json'))['verdicts']
    final = json.load(open(ROOT_V5 / 'final_matches.json'))
    # (school, q_no) → final match
    by_q = {}
    for m in final:
        if m['school'] == school:
            by_q[m['q_no']] = m

    parts = [f'<section class="school-section"><h1 class="school-title">{school}</h1>']
    n_total = len(verdicts)
    matches_ordered = []
    for v in sorted(verdicts, key=lambda x: x['q_no']):
        m = by_q.get(v['q_no'])
        matches_ordered.append(m)

    n_high = sum(1 for m in matches_ordered if m and m.get('confidence') == 'high')
    n_match = sum(1 for m in matches_ordered if m)
    parts.append(f'<div class="summary">총 {n_total}문항 · 확실 매칭 {n_high} · 매칭(전체) {n_match}</div>')

    for v, m in zip(sorted(verdicts, key=lambda x: x['q_no']), matches_ordered):
        parts.append(card(school, v['q_no'], v.get('q_name', ''), m))

    parts.append(school_conclusion(school, matches_ordered))
    parts.append('</section>')
    return '\n'.join(parts)


def build(out_pdf: Path):
    schools = ['광명고', '광명북고']
    # 표지 요약
    summary = {}
    for school in schools:
        verdicts = json.load(open(ROOT_V5 / f'visual_matches_{school}.json'))['verdicts']
        final = json.load(open(ROOT_V5 / 'final_matches.json'))
        by_q = {m['q_no']: m for m in final if m['school'] == school}
        bms = [by_q.get(v['q_no']) for v in verdicts]
        n_high = sum(1 for m in bms if m and m.get('confidence') == 'high')
        n_match = sum(1 for m in bms if m)
        summary[school] = {'total': len(verdicts), 'high': n_high, 'match': n_match,
                          'pct': round(100 * n_high / len(verdicts)) if verdicts else 0}

    rows = ''.join(
        f'<tr><td>{s}</td><td class="num">{m["total"]}</td><td class="num">{m["high"]}</td>'
        f'<td class="num">{m["match"]}</td><td class="num">{m["pct"]}%</td></tr>'
        for s, m in summary.items()
    )

    cover = f'''
<section class="cover">
  <h1>광명고 · 광명북고 × 참고서 28종 매칭 분석</h1>
  <h2>2026학년도 1학기 중간 (대수, 고2) — 1:1 매칭</h2>
  <div class="meta">분석 일자: 2026-06-09</div>
  <ul>
    <li>분석 대상: 광명고 · 광명북고 (깨끗한 텍스트 PDF)</li>
    <li>참고서 28권 (수능특강·수능완성·올림포스 4종·교과서 4종·정석 2종·유형서 6종·이음학습지 8권 = 약 4,100p)</li>
    <li>시험문제 자동 추출(텍스트레이어 기반) → 페이지 단위 OCR 매칭 → Claude vision 시각 검증</li>
    <li>각 시험문제에 best 매칭 1개를 1:1로 표시</li>
  </ul>
  <div class="school-summary">
    <table>
      <thead><tr><th>학교</th><th>총문항</th><th>확실매칭</th><th>매칭(전체)</th><th>확실%</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</section>'''

    sections = [cover]
    for school in schools:
        sections.append(section_for_school(school))

    css = '''
@page { size: A4; margin: 8mm 8mm; }
* { box-sizing: border-box; }
body { font-family: "AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif; color: #222; font-size: 9pt; line-height: 1.4; margin: 0; }
.cover { page-break-after: always; min-height: 270mm; padding: 16mm 8mm; background: linear-gradient(180deg, #fff, #eef3fa 70%); border: 1.5pt solid #28406d; border-radius: 6pt; }
.cover h1 { font-size: 22pt; color:#28406d; margin: 0 0 6pt; font-weight: 900; }
.cover h2 { font-size: 13pt; color:#444; margin: 0 0 12pt; }
.cover .meta { font-size: 10pt; color:#555; }
.cover ul { font-size: 10pt; color:#333; }
.school-summary { background:#fff; border:1pt solid #b8c4d8; border-radius:4pt; margin-top: 14pt; padding: 8pt 12pt; }
.school-summary table, .conclusion-table { width:100%; border-collapse: collapse; font-size: 10pt; }
.school-summary th, .school-summary td, .conclusion-table th, .conclusion-table td { padding: 3pt 6pt; border-bottom: 0.5pt solid #d8dde8; text-align:left; }
.school-summary th { background:#28406d; color:#fff; }
.school-summary td.num, .conclusion-table td.num { text-align:right; font-weight:700; }
.school-section { page-break-before: always; }
.school-title { font-size: 16pt; color:#fff; background:#28406d; padding: 3pt 7pt; border-radius: 3pt; margin: 0 0 3pt; }
.summary { font-size: 9pt; color:#555; margin: 2pt 0 6pt; }
.card { border: 1pt solid #b8c4d8; border-radius: 4pt; padding: 4pt 6pt; margin-bottom: 4pt; page-break-inside: avoid; background: #fff; }
.card.level-strong { border-left: 3pt solid #2c8a4f; }
.card.level-candidate { border-left: 3pt solid #d8a72b; background: #fffdf6; }
.card.level-low { border-left: 3pt solid #888; background: #f7f7f7; }
.card.level-none { border-left: 3pt solid #b54e4e; background: #fff7f7; }
.card-head { display: flex; align-items: center; gap: 6pt; margin-bottom: 3pt; font-size: 9pt; flex-wrap: wrap; }
.qno { background:#28406d; color:#fff; padding: 1pt 6pt; border-radius:3pt; font-weight:900; font-size: 10pt; min-width: 30pt; text-align:center; }
.badge { font-weight:700; padding: 1pt 6pt; border-radius:3pt; font-size:8.5pt; color:#fff; }
.badge.strong { background:#2c8a4f; }
.badge.candidate { background:#d8a72b; }
.badge.low { background:#888; }
.badge.none { background:#b54e4e; }
.src-ref { font-size: 9pt; color:#28406d; font-weight:700; }
.card-body { display: grid; grid-template-columns: 1fr 1fr; gap: 6pt; }
.exam-col, .tb-col { border: 0.5pt solid #d8dde8; border-radius: 3pt; padding: 3pt; background:#fafbfd; min-height: 25mm; display: flex; align-items: center; justify-content: center; }
.exam-img, .tb-img { max-width: 100%; max-height: 70mm; object-fit: contain; border: 0.3pt solid #ccc; border-radius:2pt; }
.no-img, .no-match { font-size: 9pt; color:#888; text-align:center; padding: 8pt 0; }
.conclusion { background: #f0f7f2; border: 1.5pt solid #2c8a4f; border-radius: 5pt; padding: 10pt 14pt; margin-top: 12pt; page-break-inside: avoid; }
.conclusion h2 { font-size: 13pt; color: #1d5d36; margin: 0 0 6pt; }
.conclusion-text { font-size: 10.5pt; color: #1d5d36; margin-bottom: 8pt; line-height: 1.5; }
.conclusion-table th { background: #2c8a4f; color:#fff; }
'''

    html = f'''<!doctype html>
<html><head><meta charset="utf-8"/>
<title>광명고/광명북고 1:1 매칭</title>
<style>{css}</style>
</head><body>
{''.join(sections)}
</body></html>'''

    html_path = ROOT_V5 / 'report.html'
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
    build(ROOT_V5 / '광명2개교_매칭보고서_v5.pdf')
