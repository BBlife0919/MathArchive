#!/usr/bin/env python3
"""6학교 통합 리포트 생성기 (카드뉴스 슬라이드).

입력: output/pirate_analysis/configs/<리포트>.json
출력: output/pirate_analysis/<리포트>.{html,pdf}

페이지 구성:
1. 메인 카드 (타이틀)
2. 이영우T의 1등급 절대 원칙
3~8. 학교별 슬라이드 (6장)
9. 압도적인 자료량
10. 핵심노트 견본 (펼쳐진 느낌)
11. 마무리 카드 (이영우T의 약속)
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PA = ROOT / "output" / "pirate_analysis"
ASSETS = PA / "assets"
CONFIGS = PA / "configs"


def img_data_uri(path: Path) -> str:
    if not path or not path.exists():
        return ""
    ext = path.suffix.lstrip(".").lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def asset(name: str) -> Path:
    return ASSETS / name


def render_principles_slide(p: dict) -> str:
    items = "\n".join(
        f"<div class='princ-row'>"
        f"<div class='princ-num'>{i+1}</div>"
        f"<div class='princ-body'>"
        f"<div class='princ-key'>{it['k']}</div>"
        f"<div class='princ-val'>{it['v']}</div>"
        f"</div></div>"
        for i, it in enumerate(p["items"])
    )
    return f"""
<section class="page slide-page principles-page">
  <div class="badge">📢 {p['header']}</div>
  <div class="princ-list">
    {items}
  </div>
</section>
"""


def render_school_slide(s: dict, idx: int, total: int) -> str:
    strats = "\n".join(
        f"<div class='strat-card'>"
        f"<div class='strat-num'>0{i+1}</div>"
        f"<div class='strat-key'>{st['k']}</div>"
        f"<div class='strat-val'>{st['v']}</div>"
        f"</div>"
        for i, st in enumerate(s["strategies"])
    )
    return f"""
<section class="page slide-page school-slide">
  <div class="slide-counter">SLIDE {idx} / {total}</div>
  <div class="school-name">{s['name']}</div>
  <div class="school-tagline">"{s['tagline']}"</div>
  <div class="char-block">
    <div class="char-head">시험 특성</div>
    <div class="char-body">{s['characteristics']}</div>
  </div>
  <div class="strat-block">
    <div class="strat-head">대비 전략</div>
    <div class="strat-grid">
      {strats}
    </div>
  </div>
</section>
"""


def render_data_volume(d: dict) -> str:
    details = "\n".join(f"<li>{x}</li>" for x in d["details"])
    return f"""
<section class="page slide-page data-page">
  <div class="badge">{d['header']}</div>
  <div class="data-main">{d['main']}</div>
  <div class="data-sub">{d['sub']}</div>
  <ul class="data-list">
    {details}
  </ul>
  <div class="data-callout">
    <span class="big-num">6,000<span class="unit">+</span></span>
    <span class="big-label">기출 문항 자체 보유</span>
  </div>
</section>
"""


def render_note_sample(intro: str, sub: str, images: list[str]) -> str:
    uris = [img_data_uri(asset(n)) for n in images]
    uris = [u for u in uris if u]
    if not uris:
        return ""
    # 5장 펼쳐진 느낌(부채꼴): 같은 3장을 회전 변형으로 5위치에 배치
    fan_positions = [
        {"left": "8%",  "rot": -14, "z": 1, "top": "12%"},
        {"left": "22%", "rot": -7,  "z": 2, "top": "6%"},
        {"left": "38%", "rot": 0,   "z": 3, "top": "2%"},
        {"left": "54%", "rot": 7,   "z": 2, "top": "6%"},
        {"left": "70%", "rot": 14,  "z": 1, "top": "12%"},
    ]
    cards = []
    for i, pos in enumerate(fan_positions):
        u = uris[i % len(uris)]
        cards.append(
            f"<img src='{u}' class='note-fan-card' "
            f"style='left:{pos['left']}; top:{pos['top']}; "
            f"transform: rotate({pos['rot']}deg); z-index:{pos['z']};'/>"
        )
    return f"""
<section class="page slide-page note-page">
  <div class="badge">핵심노트 견본</div>
  <div class="note-head">{intro}</div>
  <div class="note-sub">{sub}</div>
  <div class="note-fan">
    {''.join(cards)}
    <div class="note-fan-mask"></div>
  </div>
  <div class="note-sample-tag">SAMPLE PREVIEW</div>
</section>
"""


def html_doc(cfg: dict) -> str:
    schools = cfg["schools"]
    total = len(schools)
    school_slides = "\n".join(
        render_school_slide(s, i+1, total) for i, s in enumerate(schools)
    )
    instructor = cfg.get("instructor", "이영우T")
    academy = cfg.get("academy", "")
    note_html = render_note_sample(
        cfg.get("note_intro", "이영우T 핵심노트"),
        cfg.get("note_sub", ""),
        cfg.get("note_sample_images", []),
    )
    cl = cfg.get("closing", {})

    title_main_html = cfg['title_main'].replace('치트키', '<span class="hl">치트키</span>')
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>{cfg.get('title_main','')}</title>
<style>
  :root {{
    --ink: #0f1419;
    --pop: #ff3a3a;
    --gold: #ffc83d;
    --hl: #ffe14a;
    --soft: #f6f8fb;
    --line: #d6dbe4;
    --muted: #5d6678;
  }}
  @page {{ size: A4; margin: 0; }}
  html, body {{ margin:0; padding:0; }}
  body {{
    font-family: "AppleSDGothicNeo-Bold","AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif;
    color: var(--ink); font-size: 14pt; line-height: 1.55;
  }}
  .page {{ page-break-after: always; padding: 18mm 16mm; box-sizing: border-box; height: 297mm; }}
  .page:last-child {{ page-break-after: auto; }}

  /* ── 메인 카드 ── */
  .main-card {{
    height: 297mm; padding: 0;
    display:flex; flex-direction:column; justify-content:space-between;
    background: linear-gradient(180deg, #0f1419 0%, #1a2541 60%, #2b3a64 100%);
    color:#fff; text-align:center; box-sizing: border-box; padding: 40mm 18mm 30mm 18mm;
  }}
  .main-card .top-tag {{
    font-size: 13pt; color: var(--hl); letter-spacing: 6pt;
    margin-bottom: 18mm; font-weight: 700;
  }}
  .main-card .title-main {{
    font-size: 32pt; font-weight: 900; line-height: 1.35;
    color: #fff; padding: 0 4mm;
  }}
  .main-card .title-main .hl {{ color: var(--hl); }}
  .main-card .title-sub {{
    font-size: 16pt; color: rgba(255,255,255,0.85);
    margin-top: 14mm; line-height: 1.5;
  }}
  .main-card .footer-mark {{
    font-size: 13pt; color: rgba(255,255,255,0.6);
    letter-spacing: 4pt; margin-top: auto;
  }}

  /* ── 1등급 절대 원칙 슬라이드 ── */
  .badge {{
    display:inline-block; background: var(--ink); color:#fff;
    font-size: 14pt; font-weight: 800; letter-spacing: 3pt;
    padding: 3mm 8mm; border-radius: 50mm; margin-bottom: 9mm;
  }}
  .principles-page .princ-list {{ margin-top: 6mm; }}
  .princ-row {{ display:flex; gap: 8mm; margin-bottom: 14mm; align-items:flex-start; }}
  .princ-num {{
    flex: 0 0 auto; width: 18mm; height: 18mm; border-radius: 50%;
    background: var(--pop); color:#fff; font-weight: 900; font-size: 22pt;
    display:flex; align-items:center; justify-content:center;
  }}
  .princ-body {{ flex: 1; }}
  .princ-key {{ font-size: 22pt; font-weight: 900; color: var(--ink); margin-bottom: 3mm; }}
  .princ-val {{ font-size: 14pt; color:#2d3441; line-height: 1.65; }}

  /* ── 학교 슬라이드 ── */
  .school-slide {{
    display:flex; flex-direction:column; gap: 6mm;
  }}
  .slide-counter {{
    font-size: 11pt; color: var(--muted); letter-spacing: 4pt;
    font-weight: 700; margin-bottom: 4mm;
  }}
  .school-name {{
    font-size: 32pt; font-weight: 900; color: var(--ink);
    border-bottom: 4px solid var(--pop); padding-bottom: 3mm;
    display: inline-block;
  }}
  .school-tagline {{
    font-size: 18pt; color: var(--ink); font-weight: 700;
    background: var(--hl); display: inline-block;
    padding: 3mm 7mm; border-radius: 4px; margin-top: 4mm;
    line-height: 1.3;
  }}
  .char-block {{ margin-top: 8mm; }}
  .char-head, .strat-head {{
    font-size: 16pt; font-weight: 900; color: var(--pop);
    border-left: 6px solid var(--pop); padding-left: 8mm;
    margin-bottom: 4mm;
  }}
  .char-body {{ font-size: 14pt; color: #2d3441; line-height: 1.65; padding-left: 4mm; }}
  .strat-block {{ margin-top: 8mm; flex: 1; }}
  .strat-grid {{ display: grid; grid-template-columns: 1fr; gap: 4mm; }}
  .strat-card {{
    border-left: 4px solid var(--ink); background: var(--soft);
    padding: 4mm 7mm; border-radius: 0 6px 6px 0;
    display: grid; grid-template-columns: 12mm 1fr; gap: 4mm; align-items:start;
  }}
  .strat-num {{
    font-size: 22pt; font-weight: 900; color: var(--pop); line-height: 1;
  }}
  .strat-key {{ font-size: 15pt; font-weight: 900; color: var(--ink); margin-bottom: 1.5mm; grid-column: 2; }}
  .strat-val {{ font-size: 12.5pt; color: #2d3441; line-height: 1.55; grid-column: 2; }}

  /* ── 압도적인 자료량 ── */
  .data-page {{ background: var(--ink); color:#fff; padding: 20mm 16mm; }}
  .data-page .badge {{
    background: var(--hl); color: var(--ink);
  }}
  .data-page .data-main {{
    font-size: 28pt; font-weight: 900; color: var(--hl);
    margin-top: 4mm; line-height: 1.3;
  }}
  .data-page .data-sub {{
    font-size: 16pt; color: rgba(255,255,255,0.85);
    margin-top: 4mm; letter-spacing: 1px;
  }}
  .data-page .data-list {{
    margin-top: 12mm; font-size: 14pt; line-height: 2;
    list-style: none; padding-left: 0;
  }}
  .data-page .data-list li {{
    padding-left: 10mm; position: relative;
  }}
  .data-page .data-list li::before {{
    content: "✓"; position:absolute; left:0; top:0;
    color: var(--hl); font-weight: 900; font-size: 16pt;
  }}
  .data-page .data-callout {{
    margin-top: 12mm; text-align:center;
    border-top: 1.5px dashed rgba(255,255,255,0.3);
    padding-top: 10mm;
  }}
  .data-page .big-num {{
    font-size: 80pt; font-weight: 900; color: var(--hl);
    line-height: 1; letter-spacing: -2pt;
  }}
  .data-page .big-num .unit {{ font-size: 56pt; color: #fff; }}
  .data-page .big-label {{
    display:block; font-size: 18pt; color: rgba(255,255,255,0.85);
    letter-spacing: 4pt; margin-top: 4mm;
  }}

  /* ── 핵심노트 펼쳐진 ── */
  .note-page {{ text-align:center; }}
  .note-head {{
    font-size: 26pt; font-weight: 900; color: var(--ink); margin-top: 4mm;
  }}
  .note-sub {{
    font-size: 14pt; color: var(--muted); margin-top: 3mm; margin-bottom: 8mm;
  }}
  .note-fan {{
    position: relative; width: 100%; height: 160mm; margin: 0 auto;
  }}
  .note-fan-card {{
    position: absolute;
    width: 65mm; height: auto; max-height: 105mm;
    border: 2px solid var(--ink); border-radius: 4px;
    box-shadow: 0 6px 14px rgba(15,29,58,0.3);
    background: #fff;
    transform-origin: 50% 80%;
  }}
  .note-fan-mask {{
    position: absolute; left: -10%; right: -10%; bottom: -2mm;
    height: 50mm;
    background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.95) 70%, rgba(255,255,255,1) 100%);
    pointer-events: none;
  }}
  .note-sample-tag {{
    margin-top: 6mm; font-size: 14pt; color: var(--pop);
    font-weight: 900; letter-spacing: 5pt;
  }}

  /* ── 마무리 카드 ── */
  .closing-card {{
    height: 297mm; padding: 0;
    display:flex; flex-direction:column; justify-content:center; align-items:center;
    background: linear-gradient(135deg, #fff 0%, var(--soft) 100%);
    text-align:center; box-sizing: border-box; padding: 40mm 16mm;
  }}
  .closing-card .badge {{ background: var(--pop); color:#fff; }}
  .closing-card .head {{
    font-size: 26pt; font-weight: 900; color: var(--ink);
    margin-top: 12mm; line-height: 1.4;
  }}
  .closing-card .head .hl {{ color: var(--pop); }}
  .closing-card .sub {{
    font-size: 16pt; color: #2d3441; margin-top: 10mm;
    line-height: 1.65;
  }}
  .closing-card .tagline {{
    margin-top: 18mm; font-size: 28pt; font-weight: 900;
    color: var(--ink); letter-spacing: 1px;
    border-top: 4px solid var(--ink); border-bottom: 4px solid var(--ink);
    padding: 6mm 0; display: inline-block;
  }}
  .closing-card .signature {{
    margin-top: 14mm; font-size: 13pt; color: var(--muted);
    letter-spacing: 4pt;
  }}
  .closing-card .signature .name {{
    color: var(--ink); font-size: 17pt; font-weight: 900;
  }}
</style>
</head>
<body>

<!-- 메인 카드 -->
<section class="page main-card">
  <div class="top-tag">M A T H A R C H I V E</div>
  <div>
    <div class="title-main">{title_main_html}</div>
    <div class="title-sub">{cfg['title_sub']}</div>
  </div>
  <div class="footer-mark">{instructor} · {academy}</div>
</section>

<!-- 1등급 절대 원칙 -->
{render_principles_slide(cfg['principles'])}

<!-- 학교별 슬라이드 -->
{school_slides}

<!-- 압도적인 자료량 -->
{render_data_volume(cfg['data_volume'])}

<!-- 핵심노트 견본 -->
{note_html}

<!-- 마무리 카드 -->
<section class="page closing-card">
  <div class="badge">{cl.get('headline','이영우T의 약속')}</div>
  <div class="head">"{cl.get('main','')}"</div>
  <div class="sub">{cl.get('sub','')}</div>
  <div class="tagline">{cl.get('tagline','성적으로 증명하겠습니다.')}</div>
  <div class="signature">수학 Instructor &nbsp;<span class="name">{instructor.replace('T','')}</span></div>
</section>

</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    args = ap.parse_args()
    cfg_path = CONFIGS / f"{args.config}.json"
    if not cfg_path.exists():
        print(f"config not found: {cfg_path}", file=sys.stderr)
        return 1
    cfg = json.loads(cfg_path.read_text())
    out_html = PA / f"{args.config}.html"
    out_pdf  = PA / f"{args.config}.pdf"
    out_html.write_text(html_doc(cfg), encoding="utf-8")
    print(f"HTML: {out_html}")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(out_html.as_uri(), wait_until="networkidle")
        page.wait_for_timeout(500)
        page.pdf(
            path=str(out_pdf),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()
    print(f"PDF : {out_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
