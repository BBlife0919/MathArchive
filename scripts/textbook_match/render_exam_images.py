"""시험문제(LaTeX 텍스트)를 KaTeX로 깨끗한 PNG로 렌더링.

각 문제는 독립 HTML 페이지로 만들고 Playwright로 영역 캡처.
교재 PDF 크롭과 비슷한 비율(가로 긴 박스)로 만들어 CLIP 매칭이 잘 되게 함.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')
EXAM_IMG_DIR = ROOT / 'crops_exam'
EXAM_IMG_DIR.mkdir(parents=True, exist_ok=True)

SCHOOLS = [
    ('광명고', '광명고.json'),
    ('광명북고', '광명북고_pdf.json'),
    ('광문고', '광문고_pdf.json'),
]


def html_for_problem(qno: int, q_text: str, choices: list[dict]) -> str:
    text = q_text.replace('<<BOX_START>>', '<div class="box">').replace('<<BOX_END>>', '</div>')
    choices_html = ''
    if choices:
        items = []
        for c in choices:
            n = c.get('number', 0)
            circ = '①②③④⑤'[n - 1] if 1 <= n <= 5 else f'{n})'
            items.append(f'<span class="choice">{circ} {c.get("text", "")}</span>')
        choices_html = '<div class="choices">' + ' '.join(items) + '</div>'
    return f'''<!doctype html><html><head><meta charset="utf-8"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {{
    delimiters: [
      {{left:'$$',right:'$$',display:true}},
      {{left:'$',right:'$',display:false}}
    ], throwOnError: false}});"></script>
<style>
  body {{ margin:0; padding: 20px 24px; font-family: "AppleSDGothicNeo-Regular", "Apple SD Gothic Neo", "Nanum Gothic", sans-serif; color:#000; font-size:14pt; line-height:1.55; background:#fff; width: 720px; }}
  .qhdr {{ font-weight: 800; margin-bottom: 6pt; }}
  .body {{ }}
  .choices {{ margin-top: 6pt; display:flex; flex-wrap:wrap; gap: 4pt 18pt; }}
  .choice {{ white-space: nowrap; }}
  .box {{ border:1px solid #555; padding: 4px 8px; margin: 4px 0; }}
</style></head>
<body id="root">
  <div class="qhdr">[문제]</div>
  <div class="body">{text}</div>
  {choices_html}
</body></html>'''


def main():
    targets = []
    for school, fn in SCHOOLS:
        d = json.load(open(ROOT / 'parsed' / fn))
        for q in d['questions']:
            qid = f'{school}_Q{q["question_number"]:02d}'
            targets.append((qid, q['question_text'], q.get('choices', [])))
    print(f'rendering {len(targets)} exam problems')

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={'width': 800, 'height': 1200}, device_scale_factor=2)
        page = ctx.new_page()
        for qid, qtext, choices in targets:
            html = html_for_problem(0, qtext, choices)
            tmp = ROOT / f'_tmp_{qid}.html'
            tmp.write_text(html)
            page.goto('file://' + str(tmp.resolve()))
            page.wait_for_timeout(900)  # KaTeX
            # 본문 영역 자동 크기 측정
            box = page.evaluate('() => { const e=document.getElementById("root"); const r=e.getBoundingClientRect(); return {x:0, y:0, width: Math.ceil(r.right + 20), height: Math.ceil(r.bottom + 20)}; }')
            out = EXAM_IMG_DIR / f'{qid}.png'
            page.screenshot(path=str(out), clip=box, full_page=False)
            tmp.unlink()
        browser.close()
    print(f'wrote to {EXAM_IMG_DIR}')


if __name__ == '__main__':
    main()
