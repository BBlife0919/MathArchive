#!/usr/bin/env python3
"""카카오톡/페이스북/트위터 공유 시 보이는 1200×630 OG 썸네일을 빌드.

Playwright 로 HTML 한 페이지를 렌더링해서 PNG 로 캡처.
랜딩 페이지의 톤(딥 블루 + 골드 + 누끼 PNG)을 그대로 사용.

실행:
    python3 scripts/build_og_thumbnail.py
    → app/assets/og_thumbnail.png 생성
"""
from __future__ import annotations

import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "app" / "assets"
OUT = ASSETS / "og_thumbnail.png"


def _data_uri(p: Path) -> str:
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def _build_html() -> str:
    profile_uri = _data_uri(ASSETS / "profile_lyw.png")

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800;900&family=Cormorant+Garamond:ital,wght@1,500&family=Noto+Sans+KR:wght@500;700;900&display=swap');
html, body {{ margin: 0; padding: 0; }}
body {{
  width: 1200px; height: 630px;
  background:
    radial-gradient(ellipse at 30% 20%, #163074 0%, transparent 55%),
    radial-gradient(ellipse at 90% 90%, rgba(76,196,255,0.15) 0%, transparent 55%),
    radial-gradient(ellipse at 10% 90%, rgba(40,90,200,0.12) 0%, transparent 60%),
    #061535;
  position: relative;
  overflow: hidden;
  font-family: 'Montserrat', 'Noto Sans KR', sans-serif;
  color: #e9ecf8;
}}
/* 흐르는 수식 배경 */
.math-bg span {{
  position: absolute;
  font-family: 'Cormorant Garamond', serif;
  font-style: italic;
  color: #4cc4ff;
  opacity: 0.12;
  white-space: nowrap;
}}

/* 좌측 텍스트 블록 */
.left {{
  position: absolute;
  left: 70px; top: 50%; transform: translateY(-50%);
  width: 720px;
  z-index: 2;
}}
.eyebrow {{
  display: inline-block;
  font-size: 16px; font-weight: 700;
  letter-spacing: 0.5em;
  color: #d2af6e;
  border: 1px solid rgba(210, 175, 110, 0.45);
  padding: 9px 24px;
  border-radius: 999px;
  margin-bottom: 30px;
  text-transform: uppercase;
}}
h1 {{
  font-weight: 900;
  font-size: 92px;
  line-height: 1.0;
  letter-spacing: -0.02em;
  margin: 0 0 22px;
}}
h1 .grad {{
  background: linear-gradient(135deg, #4cc4ff 0%, #f0cd87 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}
.sub {{
  font-size: 34px;
  font-weight: 600;
  color: #c4ceea;
  letter-spacing: 0.04em;
  margin-bottom: 48px;
}}
.sub .num {{ color: #f0cd87; font-weight: 800; }}
.directed {{
  font-family: 'Cormorant Garamond', serif;
  font-style: italic;
  font-size: 22px;
  color: #d2af6e;
  letter-spacing: 0.22em;
  margin-bottom: 8px;
}}
.name {{
  font-weight: 800;
  font-size: 48px;
  margin: 0;
  letter-spacing: 0.02em;
}}

/* 우측 누끼 사진 */
.right {{
  position: absolute;
  right: -20px; bottom: 0;
  height: 600px;
  z-index: 1;
  filter: drop-shadow(0 18px 36px rgba(0,0,0,0.55));
}}

/* 골드 코너 액센트 */
.corner-tl, .corner-br {{
  position: absolute;
  width: 60px; height: 60px;
  border-color: #d2af6e;
}}
.corner-tl {{ top: 36px; left: 36px;
  border-top: 2px solid; border-left: 2px solid; }}
.corner-br {{ bottom: 36px; right: 36px;
  border-bottom: 2px solid; border-right: 2px solid; }}
</style></head>
<body>
  <div class="math-bg">
    <span style="left: 5%; top: 8%; font-size: 36px;">e^{{i\\pi}} + 1 = 0</span>
    <span style="left: 40%; top: 88%; font-size: 32px;">∫₀^∞ e^{{-x²}} dx</span>
    <span style="left: 55%; top: 12%; font-size: 28px;">∑ 1/n²</span>
    <span style="left: 8%; top: 75%; font-size: 30px;">f'(x)</span>
  </div>

  <div class="corner-tl"></div>
  <div class="corner-br"></div>

  <div class="left">
    <div class="eyebrow">Mathematics · Data · Design</div>
    <h1>Math <span class="grad">Archive</span></h1>
    <div class="sub"><span class="num">120,000+</span> Questions · Infinite Possibilities</div>
    <div class="directed">Directed by</div>
    <h2 class="name">이영우 · Youngwoo Lee</h2>
  </div>

  <img class="right" src="{profile_uri}" />
</body></html>
"""


def main():
    html = _build_html()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        page.set_content(html, wait_until="networkidle")
        # 폰트가 로드될 시간 확보
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT), full_page=False,
                        clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        browser.close()

    size = OUT.stat().st_size
    print(f"✅ {OUT.relative_to(ROOT)} 생성 ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
