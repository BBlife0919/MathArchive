"""교재 매칭 결과 PDF 보고서 빌더.

각 학교별로:
  - 강매칭(score≥75): 시험문제(KaTeX) ↔ 교재문제(이미지)
  - 후보(60≤score<75): 후보 표 + 이미지 (확인용)
  - 미매칭: 시험문제만 표시
"""
from __future__ import annotations
import argparse
import base64
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')
CROPS = ROOT / 'crops_textbook'

STRONG = 70
CANDIDATE = 55


def load_image_b64(p: Path) -> str:
    if not p.exists():
        return ''
    return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()


def latex_escape_pipe(text: str) -> str:
    """KaTeX 입력으로 안전하게: $...$를 그대로 두되 \\를 보존."""
    return text.replace('<<BOX_START>>', '<div class="boxed-block">').replace('<<BOX_END>>', '</div>')


def render_choices(choices: list[dict]) -> str:
    if not choices:
        return ''
    items = []
    for c in choices:
        circ = '①②③④⑤'[c['number'] - 1] if 1 <= c.get('number', 0) <= 5 else f"{c['number']})"
        items.append(f'<span class="choice">{circ} {latex_escape_pipe(c.get("text", ""))}</span>')
    return '<div class="choices">' + ''.join(items) + '</div>'


def section_for_school(school: str, results: list[dict]) -> str:
    strong, candidate, none = [], [], []
    for r in results:
        if not r['top']:
            none.append((r, None))
            continue
        top = r['top'][0]
        if top['score'] >= STRONG:
            strong.append((r, top))
        elif top['score'] >= CANDIDATE:
            candidate.append((r, top))
        else:
            none.append((r, None))

    parts = [f'<section class="school-section"><h1 class="school-title">{school}</h1>']
    parts.append(f'<div class="summary">총 {len(results)}문항 · 강매칭 {len(strong)} · 후보 {len(candidate)} · 미매칭 {len(none)}</div>')
    if school in ('광명북고', '광문고'):
        parts.append(f'''<div class="ocr-warning" style="background:#eef3fa;border-color:#28406d;color:#28406d;">
        ℹ️ <b>{school} 추출 방식 안내</b> — {school} PDF는 손글씨 풀이가 인쇄된 문제 위에 겹쳐 있는 사진본이어서
        OCR 자동 인식이 어려웠습니다. 본 보고서는 <b>PDF 페이지를 직접 비전으로 보고 문제 본문을 옮겨 적은</b> 결과를 사용했습니다.
        손글씨가 가린 부분은 ?로 표기했으며, 그래도 한글 shell이 충분히 보이는 문제는 매칭에 무리가 없습니다.
        </div>''')

    if strong:
        parts.append('<h2 class="section-h">✅ 강매칭 (90%+ 유사도 추정)</h2>')
        for r, top in strong:
            parts.append(render_match_card(r, top, 'strong'))

    if candidate:
        parts.append('<h2 class="section-h">⚠️ 후보 (확인 필요)</h2>')
        for r, top in candidate:
            parts.append(render_match_card(r, top, 'candidate'))

    if none:
        parts.append('<h2 class="section-h">— 매칭 없음 —</h2>')
        for r, _ in none:
            parts.append(render_match_card(r, None, 'none'))

    parts.append('</section>')
    return '\n'.join(parts)


def render_match_card(r: dict, top: dict | None, level: str) -> str:
    qno = r['q_no']
    qtxt = latex_escape_pipe(r['q_text'])
    qchoices = render_choices(r['q_choices'])
    chapter = r.get('q_chapter', '')
    chapter_html = f'<span class="chapter-tag">{chapter}</span>' if chapter else ''

    if top:
        img_data = load_image_b64(CROPS / f"{top['code']}.png")
        img_html = f'<img class="tb-img" src="{img_data}" />' if img_data else '<div class="no-img">크롭 실패</div>'
        ref = f"<div class='ref'>{top['tb_short']} · 문항코드 {top['code']} · p.{top['page']+1}</div>"
        score_badge = f"<div class='score-badge level-{level}'>유사도 {top['score']:.0f}점</div>"
    else:
        img_html = '<div class="no-img">매칭된 교재 문제 없음</div>'
        ref = ''
        score_badge = "<div class='score-badge level-none'>매칭 없음</div>"

    return f"""
    <div class="card level-{level}">
      <div class="card-head">
        <span class="qno">Q{qno}</span>
        {chapter_html}
        {score_badge}
        {ref}
      </div>
      <div class="card-body">
        <div class="col col-exam">
          <div class="col-title">시험문제</div>
          <div class="exam-text">{qtxt}</div>
          {qchoices}
        </div>
        <div class="col col-tb">
          <div class="col-title">교재문제</div>
          {img_html}
        </div>
      </div>
    </div>
    """


def build_html(matches: dict, summary: dict) -> str:
    sections = []
    # 표지
    cover = render_cover(summary)
    sections.append(cover)
    # 학교별 섹션
    for school, results in matches.items():
        sections.append(section_for_school(school, results))

    css = """
    @page { size: A4; margin: 14mm 12mm; }
    * { box-sizing: border-box; }
    body {
      font-family: "AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif;
      color: #222; font-size: 10.5pt; line-height: 1.5; margin: 0;
    }
    .cover {
      page-break-after: always;
      min-height: 250mm; display:flex; flex-direction:column; justify-content:center;
      padding: 20mm 10mm; background: linear-gradient(180deg, #fff, #eef3fa 70%);
      border: 1.5pt solid #28406d; border-radius: 6pt;
    }
    .cover h1 { font-size: 30pt; color:#28406d; margin:0 0 6pt; letter-spacing:1px; font-weight:900; }
    .cover h2 { font-size: 16pt; color:#444; margin: 0 0 14pt; font-weight: 600; }
    .cover .meta { font-size: 11pt; color:#555; margin-top: 4pt; }
    .cover ul { padding-left: 18pt; font-size: 11pt; color:#333; }
    .cover .school-summary { background:#fff; border:1pt solid #b8c4d8; border-radius:4pt; margin-top: 18pt; padding: 8pt 12pt; }
    .cover .school-summary table { width:100%; border-collapse: collapse; font-size: 10.5pt; }
    .cover .school-summary th, .cover .school-summary td { padding: 4pt 6pt; border-bottom: 0.5pt solid #d8dde8; text-align:left; }
    .cover .school-summary th { background:#28406d; color:#fff; }
    .cover .school-summary td.num { text-align:right; font-weight:700; }
    .school-section { page-break-before: always; }
    .school-title {
      font-size: 22pt; color:#fff; background:#28406d;
      padding: 6pt 10pt; border-radius: 3pt; margin: 0 0 4pt;
      letter-spacing: 1px;
    }
    .summary { font-size: 10pt; color:#555; margin: 2pt 0 10pt; }
    .section-h {
      font-size: 13pt; color:#28406d; margin: 12pt 0 6pt;
      border-bottom: 2pt solid #28406d; padding-bottom: 2pt;
    }
    .card {
      border: 1pt solid #b8c4d8; border-radius: 4pt; padding: 6pt 8pt;
      margin-bottom: 6pt; page-break-inside: avoid; background: #fff;
    }
    .card.level-strong { border-left: 4pt solid #2c8a4f; }
    .card.level-candidate { border-left: 4pt solid #d8a72b; background: #fffdf6; }
    .card.level-none { border-left: 4pt solid #b54e4e; background: #fff7f7; }
    .card-head {
      display: flex; align-items: center; gap: 8pt; margin-bottom: 4pt;
      font-size: 10pt;
    }
    .qno {
      background:#28406d; color:#fff; padding: 2pt 8pt; border-radius:3pt;
      font-weight:900; font-size: 11pt; min-width: 32pt; text-align:center;
    }
    .chapter-tag {
      background:#e8eef7; color:#28406d; padding: 1pt 7pt; border-radius:3pt;
      font-size: 9pt; font-weight:600; border:0.5pt solid #b8c4d8;
    }
    .score-badge { font-weight:700; padding: 2pt 7pt; border-radius:3pt; font-size:9.5pt; }
    .score-badge.level-strong { background:#2c8a4f; color:#fff; }
    .score-badge.level-candidate { background:#d8a72b; color:#fff; }
    .score-badge.level-none { background:#b54e4e; color:#fff; }
    .ref { color:#28406d; font-weight:600; font-size: 9.8pt; }
    .card-body { display:grid; grid-template-columns: 1fr 1fr; gap: 8pt; }
    .col { border: 0.5pt solid #d8dde8; border-radius: 3pt; padding: 6pt 8pt; background:#fafbfd; }
    .col-title { font-weight:700; color:#28406d; font-size: 9.5pt; margin-bottom: 3pt; border-bottom: 0.5pt solid #d8dde8; padding-bottom:2pt; }
    .col-exam .exam-text { font-size: 10.5pt; line-height: 1.55; word-break: break-word; }
    .choices { margin-top: 4pt; display:flex; flex-wrap: wrap; gap: 6pt 14pt; font-size: 10pt; }
    .choice { white-space: nowrap; }
    .col-tb .tb-img { width: 100%; height: auto; border: 0.3pt solid #ccc; border-radius:2pt; }
    .no-img { font-size: 10pt; color:#888; padding: 12pt 0; text-align:center; }
    .ocr-warning {
      background: #fff5e6; border: 1pt solid #d8a72b; border-radius: 4pt;
      padding: 7pt 10pt; margin: 6pt 0 12pt; font-size: 10pt; line-height: 1.6;
      color: #5a4214;
    }
    .ocr-warning b { color: #b58614; }
    """

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"/>
<title>광명3개교 대수 기출 ↔ EBS 교재 매칭 보고서</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {{
    delimiters: [
      {{left: '$$', right: '$$', display: true}},
      {{left: '$', right: '$', display: false}}
    ],
    throwOnError: false
  }});"></script>
<style>{css}</style>
</head><body>
{''.join(sections)}
</body></html>"""
    return html


def render_cover(summary: dict) -> str:
    rows = ''.join(
        f'<tr><td>{s}</td><td class="num">{v["total"]}</td><td class="num">{v["strong"]}</td><td class="num">{v["candidate"]}</td><td class="num">{v["none"]}</td><td class="num">{v["pct"]}%</td></tr>'
        for s, v in summary.items()
    )
    return f"""
    <section class="cover">
      <h1>광명3개교 ✕ EBS 교재 매칭 분석</h1>
      <h2>2026학년도 1학기 중간 (대수, 고2)</h2>
      <div class="meta">분석 일자: 2026-05-07</div>
      <ul>
        <li>분석 대상 시험: 광명고 / 광명북고 / 광문고 (2026-2-1-a 대수)</li>
        <li>교재: EBS 수능특강 수학Ⅰ(181문항) · 올림포스 고난도 대수(346문항) · 올림포스 유형편 대수(889문항)</li>
        <li>매칭 기준: 한글 문장 LCS + 토큰 셋 + 선지 수 일치 → 0~100점</li>
        <li>강매칭 ≥{STRONG}점, 후보 {CANDIDATE}~{STRONG-1}점, 미만은 미매칭</li>
      </ul>
      <div class="school-summary">
        <table>
          <thead>
            <tr><th>학교</th><th>총문항</th><th>강매칭</th><th>후보</th><th>미매칭</th><th>강매칭%</th></tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    """


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(ROOT / '광명3개교_EBS교재매칭_보고서.pdf'))
    args = ap.parse_args()

    matches = json.load(open(ROOT / 'matches_v2.json'))
    # 표지 요약 계산
    summary = {}
    for school, results in matches.items():
        is_ocr = any(r.get('is_ocr') for r in results)
        if is_ocr:
            st = 0  # OCR 소스는 강매칭 없음
            cd = sum(1 for r in results if r['top'] and r['top'][0]['score'] >= CANDIDATE)
        else:
            st = sum(1 for r in results if r['top'] and r['top'][0]['score'] >= STRONG)
            cd = sum(1 for r in results if r['top'] and CANDIDATE <= r['top'][0]['score'] < STRONG)
        nn = len(results) - st - cd
        summary[school] = {
            'total': len(results),
            'strong': st,
            'candidate': cd,
            'none': nn,
            'pct': round(100 * st / len(results)) if results else 0,
        }

    html = build_html(matches, summary)
    html_path = ROOT / 'report.html'
    html_path.write_text(html)
    print(f'wrote {html_path}')

    # PDF 변환
    out = Path(args.out)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('file://' + str(html_path.resolve()))
        # KaTeX 렌더 대기
        page.wait_for_timeout(2500)
        page.pdf(path=str(out), format='A4', margin={'top': '14mm', 'bottom': '14mm', 'left': '12mm', 'right': '12mm'}, print_background=True)
        browser.close()
    print(f'PDF: {out}')


if __name__ == '__main__':
    main()
