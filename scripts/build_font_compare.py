#!/usr/bin/env python3
"""한 문제를 3가지 수식 폰트로 비교 렌더 — 한 장 PDF."""
import asyncio
import sqlite3
import sys
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
conn = sqlite3.connect(ROOT / "db" / "mathdb.sqlite")
cur = conn.cursor()
cur.execute(
    "SELECT question_text FROM questions WHERE school='수원여고' "
    "AND year=2023 AND semester=2 AND exam_type='b' AND question_number=20"
)
qtext = cur.fetchone()[0]
conn.close()

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<style>
@page { size: A4; margin: 12mm; }
body {
    font-family: 'NanumGothic', 'Nanum Gothic', 'Apple SD Gothic Neo', sans-serif;
    font-size: 10pt; line-height: 1.6; color: #1f2937;
}
h1 { font-size: 14pt; margin: 0 0 6mm 0; color: #0f172a; }
.sub { font-size: 9pt; color: #64748b; margin-bottom: 8mm; }
.row {
    border: 0.3mm solid #d0d4dc; border-radius: 2mm;
    padding: 6mm 7mm; margin-bottom: 6mm;
}
.label {
    font-size: 11pt; font-weight: 800; color: #c8a96a;
    margin-bottom: 3mm;
}
.body { font-size: 10pt; }
/* ① 현재(KaTeX) */
.k1 .katex { font-size: 11pt; }
/* ② STIX Two Math */
.k2 .katex, .k2 .katex * {
    font-family: 'STIX Two Math', 'STIX', serif !important;
    font-size: 11pt;
}
/* ③ Times New Roman */
.k3 .katex, .k3 .katex * {
    font-family: 'Times New Roman', Times, serif !important;
    font-size: 11pt;
}
.note { font-size: 8pt; color: #94a3b8; margin-top: 1.5mm; }
</style>
</head><body>
<h1>수식 폰트 비교 — 수원여고 2023 고2 2학기 기말 20번</h1>
<div class="sub">한글: NanumGothic 10pt 고정 · 수식만 폰트 변경 (11pt 통일)</div>

<div class="row k1">
  <div class="label">① 현재 (KaTeX_Main)</div>
  <div class="body">__BODY__</div>
  <div class="note">현재 매쓰아카이브·교재 기본. 수학 표준 타이포.</div>
</div>

<div class="row k2">
  <div class="label">② STIX Two Math</div>
  <div class="body">__BODY__</div>
  <div class="note">과학논문 표준 수학 폰트(OFL 무료). 세리프 형태가 HWP 와 비슷.</div>
</div>

<div class="row k3">
  <div class="label">③ Times New Roman</div>
  <div class="body">__BODY__</div>
  <div class="note">교과서 클래식 세리프. 글리프 fallback 위험 일부 있음.</div>
</div>

<script>
window.addEventListener('load', function() {
    renderMathInElement(document.body, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false}
        ],
        throwOnError: false
    });
    document.body.setAttribute('data-ready', '1');
});
</script>
</body></html>"""

# question_text 의 dollar 수식은 KaTeX auto-render 가 처리. 줄넘김은 \n 그대로 → <br>.
body_html = qtext.replace("\n", "<br>")
html = HTML.replace("__BODY__", body_html)


async def make():
    out = "/Users/youngwoolee/Downloads/폰트비교.pdf"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        # KaTeX 렌더 대기
        try:
            await page.wait_for_function(
                "document.body.getAttribute('data-ready')==='1'",
                timeout=8000,
            )
        except Exception:
            pass
        await page.wait_for_timeout(800)
        await page.pdf(path=out, format="A4",
                       margin={"top":"12mm","bottom":"12mm",
                               "left":"12mm","right":"12mm"})
        await browser.close()
    print(f"saved: {out}")


asyncio.run(make())
