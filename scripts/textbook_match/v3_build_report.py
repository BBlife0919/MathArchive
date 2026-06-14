"""Vision 검증 결과 + 시험문제 + 교재 매칭 이미지를 합쳐 PDF 보고서 생성.

각 학교별로:
  - 매칭된 교재 출처 모두 표시 (한 시험문제 → 여러 출처 가능)
  - 학교별 최종 페이지에 교재 활용도 top-2 결론
"""
from __future__ import annotations
import base64
import json
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match_v3')
CROPS_EXAM = ROOT / 'crops_exam'


def img_b64(p: Path) -> str:
    if not p.exists():
        return ''
    return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()


def render_choices(choices):
    if not choices:
        return ''
    items = []
    for c in choices:
        n = c.get('number', 0)
        circ = '①②③④⑤'[n-1] if 1 <= n <= 5 else f'{n})'
        items.append(f'<span class="choice">{circ} {c.get("text","")}</span>')
    return '<div class="choices">' + ''.join(items) + '</div>'


def card(school: str, q: dict, matches: list[dict]) -> str:
    qno = q['q_no']
    qtxt = (q.get('q_text') or '').replace('<<BOX_START>>', '<div class="box">').replace('<<BOX_END>>', '</div>')
    qch = render_choices(q.get('q_choices', []))
    chapter = q.get('q_chapter', '')
    chapter_html = f'<span class="chapter-tag">{chapter}</span>' if chapter else ''

    if not matches:
        return f'''
<div class="card level-none">
  <div class="card-head">
    <span class="qno">Q{qno}</span>
    {chapter_html}
    <div class="score-badge level-none">매칭 없음</div>
  </div>
  <div class="card-body">
    <div class="col col-exam">
      <div class="col-title">시험문제</div>
      <div class="exam-text">{qtxt}</div>
      {qch}
    </div>
    <div class="col col-tb"><div class="no-img">매칭된 교재 페이지 없음</div></div>
  </div>
</div>'''

    # 매칭된 교재 페이지들을 모두 표시
    tb_imgs = ''
    refs = []
    for m in matches:
        img = img_b64(ROOT / 'pages_png' / m['tb_key'] / f'p{m["page"]:04d}.png')
        if img:
            tb_imgs += f'''
<div class="tb-block">
  <div class="tb-ref">📚 {m["tb_short"]} · p.{m["page"]} {('· ' + m.get("note", "")) if m.get("note") else ''}</div>
  <img class="tb-img" src="{img}" />
</div>'''
        refs.append(f'{m["tb_short"]} p.{m["page"]}')

    level = 'strong' if matches[0].get('confidence') == 'high' else 'candidate'
    badge = '✅ 확실 매칭' if level == 'strong' else '⚠️ 유사'
    n_src = len(matches)
    src_text = f'출처 {n_src}곳' if n_src > 1 else '출처 1곳'

    return f'''
<div class="card level-{level}">
  <div class="card-head">
    <span class="qno">Q{qno}</span>
    {chapter_html}
    <div class="score-badge level-{level}">{badge} · {src_text}</div>
  </div>
  <div class="card-body">
    <div class="col col-exam">
      <div class="col-title">시험문제</div>
      <div class="exam-text">{qtxt}</div>
      {qch}
    </div>
    <div class="col col-tb">
      <div class="col-title">교재 매칭 ({src_text})</div>
      {tb_imgs}
    </div>
  </div>
</div>'''


def school_conclusion(school: str, verdicts: list[dict]) -> str:
    """교재 활용도 top-2 결론."""
    cnt = Counter()
    high_cnt = Counter()
    for v in verdicts:
        for m in v.get('matches', []):
            cnt[m['tb_short']] += 1
            if m.get('confidence') == 'high':
                high_cnt[m['tb_short']] += 1
    top2_all = cnt.most_common(2)
    top2_high = high_cnt.most_common(2)

    rows = ''
    for tb, c in cnt.most_common(8):
        h = high_cnt[tb]
        rows += f'<tr><td>{tb}</td><td class="num">{c}</td><td class="num">{h}</td></tr>'

    conclusion = ''
    if top2_high:
        if len(top2_high) >= 2 and top2_high[1][1] > 0:
            conclusion = f"<strong>{top2_high[0][0]}</strong>(확실매칭 {top2_high[0][1]}건)과 <strong>{top2_high[1][0]}</strong>(확실매칭 {top2_high[1][1]}건)을 가장 많이 참고한 것으로 판단됨."
        else:
            conclusion = f"<strong>{top2_high[0][0]}</strong>(확실매칭 {top2_high[0][1]}건)을 주로 참고. 2순위는 확실매칭 없음."
    else:
        conclusion = "확실매칭 데이터가 충분하지 않아 결론 보류."

    return f'''
<section class="conclusion">
  <h2 class="conclusion-h">📊 {school} 교재 참고 분석 결론</h2>
  <div class="conclusion-text">{conclusion}</div>
  <table class="conclusion-table">
    <thead><tr><th>교재</th><th>전체 매칭</th><th>확실 매칭</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>'''


def section_for_school(school: str, verdicts: list[dict]) -> str:
    parts = [f'<section class="school-section"><h1 class="school-title">{school}</h1>']
    n_total = len(verdicts)
    n_match = sum(1 for v in verdicts if v.get('matches'))
    n_high = sum(1 for v in verdicts if v.get('matches') and v['matches'][0].get('confidence') == 'high')
    parts.append(f'<div class="summary">총 {n_total}문항 · 확실 매칭 {n_high} · 매칭(전체) {n_match}</div>')

    # 확실 매칭부터
    high = [v for v in verdicts if v.get('matches') and v['matches'][0].get('confidence') == 'high']
    others = [v for v in verdicts if v.get('matches') and v['matches'][0].get('confidence') != 'high']
    none = [v for v in verdicts if not v.get('matches')]

    if high:
        parts.append('<h2 class="section-h">✅ 확실 매칭 (vision 검증 — 같은 템플릿, 숫자만 변경)</h2>')
        for v in high:
            parts.append(card(school, v, v['matches']))
    if others:
        parts.append('<h2 class="section-h">⚠️ 유사 (구조 일부 일치)</h2>')
        for v in others:
            parts.append(card(school, v, v['matches']))
    if none:
        parts.append('<h2 class="section-h">— 매칭 없음 —</h2>')
        for v in none:
            parts.append(card(school, v, []))

    parts.append(school_conclusion(school, verdicts))
    parts.append('</section>')
    return '\n'.join(parts)


def build(out_pdf: Path):
    verdicts = json.load(open(ROOT / 'final_verdicts.json'))
    sections = []
    # 표지
    summary = {}
    for school, v in verdicts.items():
        n_high = sum(1 for x in v if x.get('matches') and x['matches'][0].get('confidence') == 'high')
        n_match = sum(1 for x in v if x.get('matches'))
        summary[school] = {'total': len(v), 'high': n_high, 'match': n_match, 'pct': round(100 * n_high / len(v)) if v else 0}

    rows = ''.join(f'<tr><td>{s}</td><td class="num">{m["total"]}</td><td class="num">{m["high"]}</td><td class="num">{m["match"]}</td><td class="num">{m["pct"]}%</td></tr>' for s, m in summary.items())
    cover = f'''
<section class="cover">
  <h1>광명4개교 × 참고서 20종 매칭 분석</h1>
  <h2>2026학년도 1학기 중간 (대수, 고2)</h2>
  <div class="meta">분석 일자: 2026-06-06</div>
  <ul>
    <li>분석 대상 시험: 광명고 · 광명북고 · 광문고 · 명문고 (2026-2-1-a 대수)</li>
    <li>참고서: 수능특강·수능완성·올림포스(4종)·유형/심화(쎈·일품·1등급494·100발100중·고쟁이·유형ON·마더텅) + 교과서 4종 + 정석 2종 = 총 20권 (약 3,800p)</li>
    <li>방식: 페이지 단위 OCR 텍스트 매칭 → top-8 후보 추출 → Claude vision 시각 검증 → 같은 템플릿만 "확실" 판정</li>
    <li>한 시험문제가 여러 교재에 동일 템플릿으로 등장하면 모두 표시 (출처 다중 표기)</li>
  </ul>
  <div class="school-summary">
    <table>
      <thead><tr><th>학교</th><th>총문항</th><th>확실매칭</th><th>매칭(전체)</th><th>확실%</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</section>'''
    sections.append(cover)

    for school, v in verdicts.items():
        sections.append(section_for_school(school, v))

    css = '''
@page { size: A4; margin: 14mm 12mm; }
* { box-sizing: border-box; }
body { font-family: "AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif; color: #222; font-size: 10.5pt; line-height: 1.5; margin: 0; }
.cover { page-break-after: always; min-height: 250mm; padding: 20mm 10mm; background: linear-gradient(180deg, #fff, #eef3fa 70%); border: 1.5pt solid #28406d; border-radius: 6pt; }
.cover h1 { font-size: 28pt; color:#28406d; margin: 0 0 6pt; font-weight: 900; }
.cover h2 { font-size: 15pt; color:#444; margin: 0 0 14pt; }
.cover .meta { font-size: 11pt; color:#555; margin-top: 4pt; }
.cover ul { font-size: 11pt; color:#333; }
.school-summary { background:#fff; border:1pt solid #b8c4d8; border-radius:4pt; margin-top: 16pt; padding: 8pt 12pt; }
.school-summary table { width:100%; border-collapse: collapse; font-size: 10.5pt; }
.school-summary th, .school-summary td { padding: 4pt 6pt; border-bottom: 0.5pt solid #d8dde8; text-align:left; }
.school-summary th { background:#28406d; color:#fff; }
.school-summary td.num, .conclusion-table td.num { text-align:right; font-weight:700; }
.school-section { page-break-before: always; }
.school-title { font-size: 22pt; color:#fff; background:#28406d; padding: 6pt 10pt; border-radius: 3pt; margin: 0 0 4pt; }
.summary { font-size: 10pt; color:#555; margin: 2pt 0 10pt; }
.section-h { font-size: 13pt; color:#28406d; margin: 12pt 0 6pt; border-bottom: 2pt solid #28406d; padding-bottom: 2pt; }
.card { border: 1pt solid #b8c4d8; border-radius: 4pt; padding: 6pt 8pt; margin-bottom: 8pt; page-break-inside: avoid; background: #fff; }
.card.level-strong { border-left: 4pt solid #2c8a4f; }
.card.level-candidate { border-left: 4pt solid #d8a72b; background: #fffdf6; }
.card.level-none { border-left: 4pt solid #b54e4e; background: #fff7f7; }
.card-head { display: flex; align-items: center; gap: 8pt; margin-bottom: 4pt; font-size: 10pt; }
.qno { background:#28406d; color:#fff; padding: 2pt 8pt; border-radius:3pt; font-weight:900; font-size: 11pt; min-width: 32pt; text-align:center; }
.chapter-tag { background:#e8eef7; color:#28406d; padding: 1pt 7pt; border-radius:3pt; font-size: 9pt; font-weight:600; border:0.5pt solid #b8c4d8; }
.score-badge { font-weight:700; padding: 2pt 7pt; border-radius:3pt; font-size:9.5pt; }
.score-badge.level-strong { background:#2c8a4f; color:#fff; }
.score-badge.level-candidate { background:#d8a72b; color:#fff; }
.score-badge.level-none { background:#b54e4e; color:#fff; }
.card-body { display:grid; grid-template-columns: 1fr 1.2fr; gap: 8pt; }
.col { border: 0.5pt solid #d8dde8; border-radius: 3pt; padding: 6pt 8pt; background:#fafbfd; }
.col-title { font-weight:700; color:#28406d; font-size: 9.5pt; margin-bottom: 3pt; border-bottom: 0.5pt solid #d8dde8; padding-bottom:2pt; }
.col-exam .exam-text { font-size: 10.5pt; line-height: 1.55; word-break: break-word; }
.choices { margin-top: 4pt; display:flex; flex-wrap: wrap; gap: 4pt 14pt; font-size: 10pt; }
.choice { white-space: nowrap; }
.tb-block { margin-bottom: 6pt; }
.tb-ref { font-size: 9.5pt; color:#28406d; font-weight: 700; margin-bottom: 2pt; }
.tb-img { width: 100%; height: auto; border: 0.3pt solid #ccc; border-radius:2pt; }
.no-img { font-size: 10pt; color:#888; padding: 12pt 0; text-align:center; }
.conclusion { background: #f0f7f2; border: 1.5pt solid #2c8a4f; border-radius: 5pt; padding: 12pt 16pt; margin-top: 20pt; page-break-inside: avoid; }
.conclusion-h { font-size: 15pt; color: #1d5d36; margin: 0 0 8pt; }
.conclusion-text { font-size: 11.5pt; color: #1d5d36; margin-bottom: 10pt; line-height: 1.6; }
.conclusion-table { width: 100%; border-collapse: collapse; font-size: 10.5pt; }
.conclusion-table th, .conclusion-table td { padding: 4pt 8pt; border-bottom: 0.5pt solid #c4dccb; text-align: left; }
.conclusion-table th { background: #2c8a4f; color:#fff; }
'''

    html = f'''<!doctype html>
<html><head><meta charset="utf-8"/>
<title>광명4개교 교재 매칭 보고서</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}], throwOnError:false}});"></script>
<style>{css}</style>
</head><body>
{''.join(sections)}
</body></html>'''

    html_path = ROOT / 'report.html'
    html_path.write_text(html)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('file://' + str(html_path.resolve()))
        page.wait_for_timeout(3000)
        page.pdf(path=str(out_pdf), format='A4', margin={'top': '14mm', 'bottom': '14mm', 'left': '12mm', 'right': '12mm'}, print_background=True)
        browser.close()
    print(f'PDF: {out_pdf}')


if __name__ == '__main__':
    build(ROOT / '광명4개교_참고서20종_매칭보고서.pdf')
