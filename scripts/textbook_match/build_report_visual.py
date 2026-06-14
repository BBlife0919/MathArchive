"""Vision 매칭(visual_matches_*.json) 기반 최종 보고서 PDF.

high/medium 만 보고서에 매칭으로 표시. low/none 은 미매칭으로 분류.
각 카드에 시험문제 LaTeX + 교재 크롭 + 매칭 사유 표시.
"""
from __future__ import annotations
import argparse
import base64
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')
CROPS_TB = ROOT / 'crops_textbook'

CONF_LABEL = {
    'high': ('확실 매칭', 'strong'),
    'medium': ('유사 (확인 필요)', 'candidate'),
    'low': ('애매', 'low'),
    'none': ('매칭 없음', 'none'),
}


def load_image_b64(p: Path) -> str:
    if not p.exists():
        return ''
    return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()


def latex_safe(text: str) -> str:
    return (text or '').replace('<<BOX_START>>', '<div class="boxed-block">').replace('<<BOX_END>>', '</div>')


def render_choices(choices):
    if not choices:
        return ''
    items = []
    for c in choices:
        n = c.get('number', 0)
        circ = '①②③④⑤'[n - 1] if 1 <= n <= 5 else f'{n})'
        items.append(f'<span class="choice">{circ} {latex_safe(c.get("text", ""))}</span>')
    return '<div class="choices">' + ''.join(items) + '</div>'


def card(school: str, q: dict, verdict: dict) -> str:
    qno = q['q_no']
    qtxt = latex_safe(q['q_text'])
    qchoices = render_choices(q.get('q_choices', []))
    chapter = q.get('q_chapter', '')
    chapter_html = f'<span class="chapter-tag">{chapter}</span>' if chapter else ''

    conf = verdict.get('confidence', 'none')
    label, level = CONF_LABEL.get(conf, CONF_LABEL['none'])
    code = verdict.get('code', '')
    reason = verdict.get('reason', '')

    if code and conf in ('high', 'medium', 'low'):
        # find matching candidate metadata
        match_meta = None
        for c in q.get('top', []):
            if c['code'] == code:
                match_meta = c
                break
        img = load_image_b64(CROPS_TB / f'{code}.png')
        img_html = f'<img class="tb-img" src="{img}" />' if img else '<div class="no-img">크롭 없음</div>'
        if match_meta:
            ref = f"<div class='ref'>{match_meta['tb_short']} · {code} · p.{match_meta['page']+1}</div>"
        else:
            ref = f"<div class='ref'>{code}</div>"
    else:
        img_html = '<div class="no-img">매칭된 교재 문제 없음</div>'
        ref = ''

    badge = f'<div class="score-badge level-{level}">{label}</div>'
    reason_html = f'<div class="reason">💡 {reason}</div>' if reason and conf != 'none' else ''

    return f'''
    <div class="card level-{level}">
      <div class="card-head">
        <span class="qno">Q{qno}</span>
        {chapter_html}
        {badge}
        {ref}
      </div>
      <div class="card-body">
        <div class="col col-exam">
          <div class="col-title">시험문제</div>
          <div class="exam-text">{qtxt}</div>
          {qchoices}
          {reason_html}
        </div>
        <div class="col col-tb">
          <div class="col-title">교재문제</div>
          {img_html}
        </div>
      </div>
    </div>
    '''


def section_for_school(school: str, results: list[dict], verdicts: list[dict]) -> str:
    # q_no -> verdict
    v_by_q = {v['q_no']: v for v in verdicts}
    high, mid, low, none = [], [], [], []
    for r in results:
        v = v_by_q.get(r['q_no'], {'confidence': 'none'})
        c = v.get('confidence', 'none')
        if c == 'high':
            high.append((r, v))
        elif c == 'medium':
            mid.append((r, v))
        elif c == 'low':
            low.append((r, v))
        else:
            none.append((r, v))

    parts = [f'<section class="school-section"><h1 class="school-title">{school}</h1>']
    parts.append(f'<div class="summary">총 {len(results)}문항 · 확실매칭 {len(high)} · 유사 {len(mid)} · 애매 {len(low)} · 미매칭 {len(none)}</div>')

    if high:
        parts.append('<h2 class="section-h">✅ 확실 매칭 (vision 검증 — 같은 템플릿, 숫자만 변경)</h2>')
        for r, v in high:
            parts.append(card(school, r, v))
    if mid:
        parts.append('<h2 class="section-h">⚠️ 유사 (구조 일부 일치 — 사용자 확인)</h2>')
        for r, v in mid:
            parts.append(card(school, r, v))
    if low:
        parts.append('<h2 class="section-h">— 애매 —</h2>')
        for r, v in low:
            parts.append(card(school, r, v))
    if none:
        parts.append('<h2 class="section-h">— 미매칭 (EBS 교재 3종 후보 중 같은 템플릿 없음) —</h2>')
        for r, v in none:
            parts.append(card(school, r, v))
    parts.append('</section>')
    return '\n'.join(parts)


def render_cover(summary: dict) -> str:
    rows = ''.join(
        f'<tr><td>{s}</td><td class="num">{v["total"]}</td><td class="num">{v["high"]}</td><td class="num">{v["mid"]}</td><td class="num">{v["other"]}</td><td class="num">{v["pct"]}%</td></tr>'
        for s, v in summary.items()
    )
    return f'''
    <section class="cover">
      <h1>광명3개교 ✕ EBS 교재 매칭 분석</h1>
      <h2>2026학년도 1학기 중간 (대수, 고2) — Vision 검증판</h2>
      <div class="meta">분석 일자: 2026-05-08</div>
      <ul>
        <li>분석 대상 시험: 광명고 / 광명북고 / 광문고 (2026-2-1-a 대수)</li>
        <li>교재: EBS 수능특강 수학Ⅰ(181문항) · 올림포스 고난도 대수(346문항) · 올림포스 유형편 대수(889문항) — 총 1,416문항</li>
        <li>방식: ① OCR 정밀 텍스트 매칭으로 후보 top-8 추출 → ② Claude vision이 시험문제와 후보 이미지를 시각적으로 비교 → ③ 같은 템플릿(숫자만 변경)만 "확실 매칭" 판정</li>
        <li>이전 텍스트 매칭의 false positive 제거됨</li>
      </ul>
      <div class="school-summary">
        <table>
          <thead>
            <tr><th>학교</th><th>총문항</th><th>확실매칭</th><th>유사</th><th>애매·미매칭</th><th>확실%</th></tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
      <div class="callout">
      ※ "확실 매칭"은 Claude vision이 시험문제와 교재문제를 시각적으로 비교하여 한글 instruction과 식 구조가 일치하는 경우만 표시.
        후보 풀(텍스트 매처 top-8)에 진짜 정답이 누락된 경우는 "미매칭"으로 잡힐 수 있으므로, 미매칭 문항도 사용자가 한 번 훑어보길 권장.
      </div>
    </section>
    '''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(ROOT / '광명3개교_EBS교재매칭_보고서_vision.pdf'))
    args = ap.parse_args()

    matches = json.load(open(ROOT / 'matches_v2.json'))
    schools_verdicts = {}
    for school in ['광명고', '광명북고', '광문고']:
        v = json.load(open(ROOT / f'visual_matches_{school}.json'))
        schools_verdicts[school] = v['verdicts']

    summary = {}
    for school, results in matches.items():
        v = schools_verdicts.get(school, [])
        v_by_q = {x['q_no']: x for x in v}
        h = sum(1 for r in results if v_by_q.get(r['q_no'], {}).get('confidence') == 'high')
        m = sum(1 for r in results if v_by_q.get(r['q_no'], {}).get('confidence') == 'medium')
        other = len(results) - h - m
        summary[school] = {
            'total': len(results),
            'high': h,
            'mid': m,
            'other': other,
            'pct': round(100 * h / len(results)) if results else 0,
        }

    sections = [render_cover(summary)]
    for school, results in matches.items():
        sections.append(section_for_school(school, results, schools_verdicts.get(school, [])))

    css = '''
    @page { size: A4; margin: 14mm 12mm; }
    * { box-sizing: border-box; }
    body {
      font-family: "AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif;
      color: #222; font-size: 10.5pt; line-height: 1.5; margin: 0;
    }
    .cover { page-break-after: always; min-height: 250mm; padding: 20mm 10mm; background: linear-gradient(180deg, #fff, #eef3fa 70%); border: 1.5pt solid #28406d; border-radius: 6pt; }
    .cover h1 { font-size: 28pt; color:#28406d; margin: 0 0 6pt; font-weight: 900; }
    .cover h2 { font-size: 15pt; color:#444; margin: 0 0 14pt; }
    .cover ul { font-size: 11pt; color:#333; }
    .cover .meta { font-size: 11pt; color:#555; margin-top: 4pt; }
    .school-summary { background:#fff; border:1pt solid #b8c4d8; border-radius:4pt; margin-top: 16pt; padding: 8pt 12pt; }
    .school-summary table { width:100%; border-collapse: collapse; font-size: 10.5pt; }
    .school-summary th, .school-summary td { padding: 4pt 6pt; border-bottom: 0.5pt solid #d8dde8; text-align:left; }
    .school-summary th { background:#28406d; color:#fff; }
    .school-summary td.num { text-align:right; font-weight:700; }
    .callout { margin-top: 14pt; padding: 8pt 12pt; background: #fff8e6; border-left: 3pt solid #d8a72b; font-size: 10pt; color: #5a4214; border-radius: 3pt; }
    .school-section { page-break-before: always; }
    .school-title { font-size: 22pt; color:#fff; background:#28406d; padding: 6pt 10pt; border-radius: 3pt; margin: 0 0 4pt; }
    .summary { font-size: 10pt; color:#555; margin: 2pt 0 10pt; }
    .section-h { font-size: 13pt; color:#28406d; margin: 12pt 0 6pt; border-bottom: 2pt solid #28406d; padding-bottom: 2pt; }
    .card { border: 1pt solid #b8c4d8; border-radius: 4pt; padding: 6pt 8pt; margin-bottom: 6pt; page-break-inside: avoid; background: #fff; }
    .card.level-strong { border-left: 4pt solid #2c8a4f; }
    .card.level-candidate { border-left: 4pt solid #d8a72b; background: #fffdf6; }
    .card.level-low { border-left: 4pt solid #8a8a8a; background: #f7f7f7; }
    .card.level-none { border-left: 4pt solid #b54e4e; background: #fff7f7; }
    .card-head { display: flex; align-items: center; gap: 8pt; margin-bottom: 4pt; font-size: 10pt; }
    .qno { background:#28406d; color:#fff; padding: 2pt 8pt; border-radius:3pt; font-weight:900; font-size: 11pt; min-width: 32pt; text-align:center; }
    .chapter-tag { background:#e8eef7; color:#28406d; padding: 1pt 7pt; border-radius:3pt; font-size: 9pt; font-weight:600; border:0.5pt solid #b8c4d8; }
    .score-badge { font-weight:700; padding: 2pt 7pt; border-radius:3pt; font-size:9.5pt; }
    .score-badge.level-strong { background:#2c8a4f; color:#fff; }
    .score-badge.level-candidate { background:#d8a72b; color:#fff; }
    .score-badge.level-low { background:#8a8a8a; color:#fff; }
    .score-badge.level-none { background:#b54e4e; color:#fff; }
    .ref { color:#28406d; font-weight:600; font-size: 9.8pt; }
    .card-body { display:grid; grid-template-columns: 1fr 1fr; gap: 8pt; }
    .col { border: 0.5pt solid #d8dde8; border-radius: 3pt; padding: 6pt 8pt; background:#fafbfd; }
    .col-title { font-weight:700; color:#28406d; font-size: 9.5pt; margin-bottom: 3pt; border-bottom: 0.5pt solid #d8dde8; padding-bottom:2pt; }
    .col-exam .exam-text { font-size: 10.5pt; line-height: 1.55; word-break: break-word; }
    .choices { margin-top: 4pt; display:flex; flex-wrap: wrap; gap: 4pt 14pt; font-size: 10pt; }
    .choice { white-space: nowrap; }
    .col-tb .tb-img { width: 100%; height: auto; border: 0.3pt solid #ccc; border-radius:2pt; }
    .no-img { font-size: 10pt; color:#888; padding: 12pt 0; text-align:center; }
    .reason { margin-top: 6pt; padding: 4pt 6pt; background: #eef3fa; border-radius: 3pt; font-size: 9.5pt; color: #28406d; line-height: 1.4; }
    '''

    html = f'''<!doctype html>
<html><head><meta charset="utf-8"/>
<title>광명3개교 EBS 매칭 보고서 (Vision)</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {{
    delimiters: [
      {{left:'$$',right:'$$',display:true}},
      {{left:'$',right:'$',display:false}}
    ], throwOnError: false}});"></script>
<style>{css}</style>
</head><body>
{''.join(sections)}
</body></html>'''

    html_path = ROOT / 'report_visual.html'
    html_path.write_text(html)
    print(f'wrote {html_path}')

    out = Path(args.out)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('file://' + str(html_path.resolve()))
        page.wait_for_timeout(2500)
        page.pdf(path=str(out), format='A4', margin={'top': '14mm', 'bottom': '14mm', 'left': '12mm', 'right': '12mm'}, print_background=True)
        browser.close()
    print(f'PDF: {out}')


if __name__ == '__main__':
    main()
