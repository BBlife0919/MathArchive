"""한국어 손글씨/디자인 폰트 20종 샘플을 PDF 1장으로 모아 생성.

목적: 시험지 표지의 'with 이영우T' 자리에 어떤 폰트를 쓸지 사용자가
직관적으로 비교·선택할 수 있게 한 페이지에 모든 후보를 늘어놓는다.
"""
from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_PDF = Path.home() / "Downloads" / "font_candidates.pdf"

# (표시명, Google Fonts family URL fragment) 20종
FONTS: list[tuple[str, str]] = [
    ("Hi Melody",              "Hi+Melody"),
    ("East Sea Dokdo",         "East+Sea+Dokdo"),
    ("Single Day",             "Single+Day"),
    ("Cute Font",              "Cute+Font"),
    ("Gaegu (Bold)",           "Gaegu:wght@700"),
    ("Yeon Sung",              "Yeon+Sung"),
    ("Stylish",                "Stylish"),
    ("Black Han Sans",         "Black+Han+Sans"),
    ("Sunflower",              "Sunflower:wght@500"),
    ("Do Hyeon",               "Do+Hyeon"),
    ("Jua",                    "Jua"),
    ("Gowun Dodum",            "Gowun+Dodum"),
    ("Gowun Batang (Bold)",    "Gowun+Batang:wght@700"),
    ("Gamja Flower",           "Gamja+Flower"),
    ("Poor Story",             "Poor+Story"),
    ("Kirang Haerang",         "Kirang+Haerang"),
    ("Song Myung",             "Song+Myung"),
    ("Black And White Picture","Black+And+White+Picture"),
    ("Nanum Brush Script",     "Nanum+Brush+Script"),
    ("Diphylleia",             "Diphylleia"),
]

SAMPLE_TEXT = "with 이영우T"


def _build_html() -> str:
    families = "&".join(f"family={f[1]}" for f in FONTS)
    link = (
        f'https://fonts.googleapis.com/css2?{families}&display=swap'
    )

    rows = []
    for i, (name, family_url) in enumerate(FONTS, 1):
        # family_url 에서 표시용 이름 추출 (콜론 앞부분, '+' 를 공백으로)
        css_family = family_url.split(":")[0].replace("+", " ")
        rows.append(f"""
<div class="row">
  <div class="idx">{i:02d}.</div>
  <div class="name">{name}</div>
  <div class="sample" style="font-family: '{css_family}', cursive;">
    {SAMPLE_TEXT}
  </div>
</div>""")

    body = "\n".join(rows)

    return f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<title>폰트 후보 20종</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{link}">
<style>
@page {{ size: A4; margin: 14mm; }}
body {{
  font-family: 'Nanum Myeongjo', serif;
  color: #111;
  margin: 0; padding: 0;
}}
h1 {{
  font-size: 18pt; margin: 0 0 8mm 0;
  border-bottom: 1pt solid #888; padding-bottom: 3mm;
}}
.row {{
  display: grid;
  grid-template-columns: 10mm 50mm 1fr;
  align-items: center;
  border-bottom: 0.4pt solid #ddd;
  padding: 4mm 0;
  min-height: 18mm;
}}
.idx {{
  color: #888; font-size: 11pt;
}}
.name {{
  font-size: 10pt; color: #333;
  font-family: 'Nanum Myeongjo', serif;
}}
.sample {{
  font-size: 32pt; color: #111;
  letter-spacing: 1px;
}}
</style></head><body>
<h1>한국어 손글씨·디자인 폰트 20종 — 'with 이영우T'</h1>
{body}
</body></html>
"""


def main():
    html = _build_html()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        # 폰트 로딩 완료 대기
        try:
            page.wait_for_function(
                "document.fonts && document.fonts.ready", timeout=15000
            )
            page.evaluate("document.fonts.ready")
        except Exception:
            pass
        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        page.pdf(
            path=str(OUT_PDF),
            format="A4",
            print_background=True,
            margin={"top": "14mm", "bottom": "14mm",
                    "left": "14mm", "right": "14mm"},
        )
        browser.close()
    print(f"✅ Saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
