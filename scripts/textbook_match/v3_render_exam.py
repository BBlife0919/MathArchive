"""4학교 시험문제를 KaTeX HTML로 깨끗하게 렌더링 → PNG."""
from __future__ import annotations
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match_v3')
OUT = ROOT / 'crops_exam'
OUT.mkdir(parents=True, exist_ok=True)
INP = ROOT / 'exam_input'


def html_for(qtext: str, choices: list[dict]) -> str:
    text = qtext.replace('<<BOX_START>>', '<div class="box">').replace('<<BOX_END>>', '</div>')
    ch = ''
    if choices:
        items = []
        for c in choices:
            n = c.get('number', 0)
            circ = '①②③④⑤'[n-1] if 1 <= n <= 5 else f'{n})'
            items.append(f'<span class="choice">{circ} {c.get("text","")}</span>')
        ch = '<div class="choices">' + ''.join(items) + '</div>'
    return f'''<!doctype html><html><head><meta charset="utf-8"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}], throwOnError:false}});"></script>
<style>
body {{ margin:0; padding: 20px 24px; font-family: "AppleSDGothicNeo-Regular", "Apple SD Gothic Neo", sans-serif; color:#000; font-size: 14pt; line-height: 1.55; background:#fff; width: 720px; }}
.qhdr {{ font-weight: 800; margin-bottom: 6pt; }}
.choices {{ margin-top: 6pt; display:flex; flex-wrap: wrap; gap: 4pt 18pt; }}
.choice {{ white-space: nowrap; }}
.box {{ border:1px solid #555; padding: 4px 8px; margin: 4px 0; }}
</style></head>
<body id="root">
<div class="qhdr">[문제]</div>
<div class="body">{text}</div>
{ch}
</body></html>'''


def main():
    schools = ['광명고', '광명북고', '광문고', '명문고']
    total = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={'width': 800, 'height': 1200}, device_scale_factor=2)
        page = ctx.new_page()
        for school in schools:
            d = json.load(open(INP / f'{school}.json'))
            for q in d['questions']:
                qid = f'{school}_Q{q["question_number"]:02d}'
                out = OUT / f'{qid}.png'
                # 광명3개교는 이미 있을 수 있음 - 명문고만 새로 렌더
                if out.exists() and school != '명문고':
                    continue
                html = html_for(q.get('question_text', '') or q.get('q_text_ocr', ''), q.get('choices', []))
                tmp = ROOT / f'_tmp_{qid}.html'
                tmp.write_text(html)
                page.goto('file://' + str(tmp.resolve()))
                page.wait_for_timeout(900)
                box = page.evaluate('() => { const e=document.getElementById("root"); const r=e.getBoundingClientRect(); return {x:0, y:0, width: Math.ceil(r.right + 20), height: Math.ceil(r.bottom + 20)}; }')
                page.screenshot(path=str(out), clip=box, full_page=False)
                tmp.unlink()
                total += 1
        browser.close()
    print(f'rendered {total} exam images (총 {len(list(OUT.glob("*.png")))})')


if __name__ == '__main__':
    main()
