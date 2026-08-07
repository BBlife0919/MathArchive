#!/usr/bin/env python3
"""학교별 적중분석 카드뉴스 PDF 생성기 (v4).

페이지 구성:
1. 표지 (다크 그라데이션 + 사진 + 학교명)
2. 프롤로그 ("우리 아이는 왜 유독 수학을...")
3. 솔루션 (이영우T 고득점 3단계 절대 전략)
4. 자료 소개 멘트
5. 압도적인 자료량 (6,000+)
6. 학교 분석 카드 (학교명 + tagline + 시험 특성 + 대비 전략)
7. 적중분석 표 + hit banner
8. 도넛차트 (위아래 정렬, 큰 사이즈, 퍼센티지)
9. 시험대비 전략 + 이영우T 코멘트 (살 붙음)
10-13. 핵심문제 4개 (시험 vs 교재 fabricated)
14. 핵심노트 견본 (펼쳐진 부채꼴)
15. closing
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from collections import Counter
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


def asset(school_short: str, name: str) -> Path:
    if not name:
        return ASSETS / "_missing_"
    p = ASSETS / school_short / name
    if p.exists():
        return p
    p = ASSETS / name
    return p


def load_consolidated() -> dict:
    return json.loads((CONFIGS / "광명지역_통합리포트.json").read_text())


def render_q_table(questions: list[dict]) -> str:
    rows = []
    for q in questions:
        rows.append(
            f"<tr>"
            f"<td class='c qno'>{q['q']}</td>"
            f"<td>{q['chapter']}</td>"
            f"<td class='c'>{q['score']}</td>"
            f"<td class='c'><span class='dpill diff-{q['difficulty']}'>{q['difficulty']}</span></td>"
            f"<td class='match'>유형{q['matched_yutype']} — {q['matched_title']}</td>"
            f"<td class='c'><span class='gpill grade-{q['grade']}'>{q['grade']}</span></td>"
            f"</tr>"
        )
    return "\n".join(rows)


def render_school_strategies(strats: list[dict]) -> str:
    return "\n".join(
        f"<div class='strat-card'>"
        f"<div class='strat-num'>0{i+1}</div>"
        f"<div class='strat-key'>{st['k']}</div>"
        f"<div class='strat-val'>{st['v']}</div>"
        f"</div>"
        for i, st in enumerate(strats)
    )


def render_principles_solution(consolidated: dict) -> str:
    """프롤로그 + 솔루션(3단계) 슬라이드 2장."""
    pr = consolidated["prologue"]
    sol = consolidated["solution"]
    body_lines = "<br><br>".join(pr["body"])

    steps = "\n".join(
        f"<div class='sol-step'>"
        f"<div class='sol-num'>{i+1}️⃣</div>"
        f"<div class='sol-body'>"
        f"<div class='sol-key'>{st['k']}</div>"
        f"<div class='sol-val'>{st['v']}</div>"
        f"</div></div>"
        for i, st in enumerate(sol["steps"])
    )

    return f"""
<section class="page slide-page prologue-page">
  <div class="badge">PROLOGUE</div>
  <div class="prologue-q">"{pr['title']}"</div>
  <div class="prologue-body">{body_lines}</div>
</section>

<section class="page slide-page solution-page">
  <div class="badge dark">📢 {sol['header']}</div>
  <div class="sol-title">{sol['title']}</div>
  <div class="sol-intro">{sol['intro']}</div>
  <div class="sol-steps">{steps}</div>
</section>
"""


def render_data_pages(consolidated: dict) -> str:
    di = consolidated["data_intro"]
    dv = consolidated["data_volume"]
    details = "\n".join(f"<li>{x}</li>" for x in dv["details"])
    return f"""
<section class="page slide-page intro-page">
  <div class="intro-title">{di['title']}</div>
  <div class="intro-sub">{di['sub']}</div>
</section>

<section class="page slide-page data-page">
  <div class="badge yellow">{dv['header']}</div>
  <div class="data-main">{dv['main']}</div>
  <div class="data-sub">{dv['sub']}</div>
  <ul class="data-list">
    {details}
  </ul>
  <div class="data-callout">
    <span class="big-num">6,000<span class="unit">+</span></span>
    <span class="big-label">기출 문항 자체 보유</span>
  </div>
</section>
"""


def render_school_slide(school_meta: dict) -> str:
    strats = render_school_strategies(school_meta["strategies"])
    return f"""
<section class="page slide-page school-slide">
  <div class="school-name">{school_meta['name']}</div>
  <div class="school-tagline">"{school_meta['tagline']}"</div>
  <div class="char-block">
    <div class="char-head">시험 특성</div>
    <div class="char-body">{school_meta['characteristics']}</div>
  </div>
  <div class="strat-block">
    <div class="strat-head">대비 전략</div>
    <div class="strat-grid">
      {strats}
    </div>
  </div>
</section>
"""


def render_key_problem(school_short: str, kp: dict, idx: int, total: int) -> str:
    fab = kp.get("fabricated_latex") or ""
    if not fab:
        match_block = "<div class='card-empty'>(교재 매칭 본문 없음)</div>"
    else:
        match_block = f"<div class='match-latex'>{fab}</div>"
    return f"""
<section class="page key-page">
  <div class="key-counter">핵심문제 {idx} / {total}</div>
  <div class="key-head">
    <div class="key-no-pill">시험지 {kp['q']}번</div>
    <div class="key-meta">{kp['topic']} · 배점 {kp['score']} · 난이도 <span class='hi-{kp['difficulty']}'>{kp['difficulty']}</span></div>
  </div>
  <div class="key-body">
    <div class="exam-card">
      <div class="card-head exam-head">시험 출제 문항</div>
      <div class="exam-latex">{kp['exam_latex']}</div>
    </div>
    <div class="note-card">
      <div class="card-head note-head">{kp['matched_title']}</div>
      {match_block}
      <div class="match-cap">{kp['comment']}</div>
    </div>
  </div>
</section>
"""


def chart_payload(questions: list[dict]) -> str:
    chap_count = Counter(q["chapter"] for q in questions)
    diff_count = Counter(q["difficulty"] for q in questions)
    diff_order = ["하", "중", "상"]
    diff_labels = [d for d in diff_order if d in diff_count]
    diff_data = [diff_count[d] for d in diff_labels]
    chap_labels = list(chap_count.keys())
    chap_data = [chap_count[c] for c in chap_labels]
    return json.dumps({
        "chapter": {"labels": chap_labels, "data": chap_data},
        "difficulty": {"labels": diff_labels, "data": diff_data},
    }, ensure_ascii=False)


def render_note_fan(school_short: str, intro: str, sub: str, images: list[str]) -> str:
    uris = [img_data_uri(asset(school_short, n)) for n in images]
    uris = [u for u in uris if u]
    if not uris:
        return ""
    fan_positions = [
        {"left": "8%",  "rot": -14, "z": 1, "top": "10%"},
        {"left": "22%", "rot": -7,  "z": 2, "top": "5%"},
        {"left": "38%", "rot": 0,   "z": 3, "top": "2%"},
        {"left": "54%", "rot": 7,   "z": 2, "top": "5%"},
        {"left": "70%", "rot": 14,  "z": 1, "top": "10%"},
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
<section class="page note-page slide-page">
  <div class="badge dark">핵심노트 견본</div>
  <div class="note-title">{intro}</div>
  <div class="note-sub">{sub}</div>
  <div class="note-fan">
    {''.join(cards)}
    <div class="note-fan-mask"></div>
  </div>
  <div class="note-sample-tag">SAMPLE PREVIEW</div>
</section>
"""


def html_doc(cfg: dict) -> str:
    school = cfg["school"]
    short = cfg["short_name"]
    title = cfg["exam_title"]
    subject = cfg["subject"]
    sub_range = cfg.get("subject_range", "")
    instructor = cfg["instructor"]
    academy = cfg.get("academy", "")
    questions = cfg["questions"]
    key_problems = cfg["key_problems"]
    instructor_comment = cfg["instructor_comment"]
    note_intro = cfg.get("note_intro", "이영우T 핵심노트")
    note_sub = cfg.get("note_sub", "시험 출제 핵심 패턴을 한 줄로 정리한 직강 노트")
    note_sample_images = cfg.get("note_sample_images", [
        "note_sample_1.png", "note_sample_2.png", "note_sample_3.png"
    ])

    consolidated = load_consolidated()
    school_meta = next((s for s in consolidated["schools"] if s["name"] == school), None)
    strategy_html = render_school_strategies(school_meta["strategies"]) if school_meta else ""

    instructor_uri = img_data_uri(asset(short, "instructor.png"))
    logo_uri = img_data_uri(asset(short, "logo.png"))

    table_rows = render_q_table(questions)
    total_score = sum(q["score"] for q in questions)
    hit_count = sum(1 for q in questions if q["grade"] in ("A", "B"))
    hit_rate = round(hit_count / len(questions) * 100)
    chart_json = chart_payload(questions)

    key_pages = "\n".join(
        render_key_problem(short, kp, i+1, len(key_problems))
        for i, kp in enumerate(key_problems)
    )
    note_html = render_note_fan(short, note_intro, note_sub, note_sample_images)
    pr_sol_html = render_principles_solution(consolidated)
    data_html = render_data_pages(consolidated)
    school_slide_html = render_school_slide(school_meta) if school_meta else ""

    logo_block = (
        f"<img class='logo' src='{logo_uri}' alt='{academy}'/>"
        if logo_uri
        else f"<div class='logo-placeholder'>{academy}</div>"
    )

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>{school} {title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{{delimiters:[
    {{left:'$$',right:'$$',display:true}},
    {{left:'$',right:'$',display:false}}
  ]}});"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
  :root {{
    --ink: #0f1419;
    --pop: #ff3a3a;
    --gold: #ffc83d;
    --hl: #ffe14a;
    --soft: #f6f8fb;
    --line: #d6dbe4;
    --muted: #5d6678;
    --ok: #1f9d5f;
  }}
  @page {{ size: A4; margin: 0; }}
  html, body {{ margin:0; padding:0; }}
  body {{
    font-family: "AppleSDGothicNeo-Bold","AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif;
    color: var(--ink); font-size: 14pt; line-height: 1.6;
  }}
  .page {{ page-break-after: always; padding: 18mm 16mm; box-sizing: border-box; height: 297mm; }}
  .page:last-child {{ page-break-after: auto; }}

  /* ── 표지 (다크 그라데이션) ── */
  .cover {{
    height: 297mm; padding: 0;
    display:flex; flex-direction:column; justify-content:space-between;
    background: linear-gradient(180deg, #0f1419 0%, #1a2541 60%, #2b3a64 100%);
    color:#fff; text-align:center; box-sizing: border-box; padding: 22mm 18mm 22mm 18mm;
  }}
  .cover .top-tag {{
    font-size: 13pt; color: var(--hl); letter-spacing: 6pt; font-weight: 700;
  }}
  .cover .title-block {{ margin-top: 8mm; }}
  .cover .school {{
    font-size: 24pt; font-weight: 800; color: var(--hl);
    letter-spacing: 2pt; margin-bottom: 5mm;
  }}
  .cover .title-main {{
    font-size: 30pt; font-weight: 900; line-height: 1.3; color: #fff;
  }}
  .cover .title-sub {{
    font-size: 14pt; color: rgba(255,255,255,0.85); margin-top: 6mm; line-height: 1.5;
  }}
  .cover .photo-wrap {{
    flex:1; display:flex; align-items:center; justify-content:center;
    margin: 4mm 0;
  }}
  .cover .photo {{
    max-width: 90mm; max-height: 110mm; object-fit: contain;
    filter: drop-shadow(0 6px 18px rgba(0,0,0,0.4));
  }}
  .cover .footer-mark {{
    font-size: 13pt; color: rgba(255,255,255,0.85); letter-spacing: 4pt;
  }}
  .cover .footer-mark .name {{ color: var(--hl); font-weight: 800; }}
  .cover .logo-wrap {{ margin-top: 5mm; }}
  .cover .logo {{ max-height: 18mm; max-width: 60mm; }}
  .cover .logo-placeholder {{
    color: rgba(255,255,255,0.5); border:1px dashed rgba(255,255,255,0.3);
    padding: 2mm 6mm; border-radius: 3px; font-size: 11pt; letter-spacing: 2pt;
    display:inline-block;
  }}

  /* ── 슬라이드 공통 ── */
  .slide-page {{ }}
  .badge {{
    display:inline-block; background: var(--ink); color:#fff;
    font-size: 13pt; font-weight: 800; letter-spacing: 3pt;
    padding: 3mm 8mm; border-radius: 50mm; margin-bottom: 9mm;
  }}
  .badge.dark {{ background: var(--ink); color:#fff; }}
  .badge.yellow {{ background: var(--hl); color: var(--ink); }}
  .badge.red {{ background: var(--pop); color:#fff; }}

  /* ── 프롤로그 ── */
  .prologue-page {{ display:flex; flex-direction:column; justify-content:center; }}
  .prologue-q {{
    font-size: 30pt; font-weight: 900; color: var(--ink);
    line-height: 1.4; margin-bottom: 12mm;
  }}
  .prologue-body {{
    font-size: 16pt; line-height: 1.85; color: #2d3441;
  }}

  /* ── 솔루션 (3단계) ── */
  .solution-page {{ }}
  .sol-title {{
    font-size: 30pt; font-weight: 900; color: var(--ink);
    margin-bottom: 4mm; letter-spacing: -0.5pt;
  }}
  .sol-intro {{
    font-size: 14pt; color: var(--muted); margin-bottom: 12mm; line-height: 1.55;
  }}
  .sol-steps {{ display:flex; flex-direction: column; gap: 8mm; }}
  .sol-step {{
    display:flex; gap: 7mm; align-items:flex-start;
    padding: 5mm 6mm; background: var(--soft); border-radius: 8px;
    border-left: 6px solid var(--pop);
  }}
  .sol-num {{ font-size: 28pt; flex: 0 0 auto; }}
  .sol-body {{ flex: 1; }}
  .sol-key {{ font-size: 17pt; font-weight: 900; color: var(--ink); margin-bottom: 2mm; }}
  .sol-val {{ font-size: 13pt; color: #2d3441; line-height: 1.6; }}

  /* ── 자료 소개 ── */
  .intro-page {{
    display:flex; flex-direction: column; justify-content:center; align-items:center;
    text-align: center;
  }}
  .intro-title {{
    font-size: 34pt; font-weight: 900; color: var(--ink);
    line-height: 1.4; margin-bottom: 10mm;
  }}
  .intro-sub {{
    font-size: 16pt; color: var(--muted); line-height: 1.6;
    border-top: 1.5px solid var(--line); border-bottom: 1.5px solid var(--line);
    padding: 6mm 0;
  }}

  /* ── 압도적 자료량 ── */
  .data-page {{ background: var(--ink); color:#fff; padding: 22mm 18mm; }}
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
  .data-page .data-list li {{ padding-left: 10mm; position: relative; }}
  .data-page .data-list li::before {{
    content: "✓"; position:absolute; left:0; top:0;
    color: var(--hl); font-weight: 900; font-size: 16pt;
  }}
  .data-page .data-callout {{
    margin-top: 10mm; text-align:center;
    border-top: 1.5px dashed rgba(255,255,255,0.3);
    padding-top: 8mm;
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

  /* ── 학교 분석 슬라이드 ── */
  .school-slide {{ display:flex; flex-direction:column; gap: 5mm; }}
  .school-name {{
    font-size: 32pt; font-weight: 900; color: var(--ink);
    border-bottom: 4px solid var(--pop); padding-bottom: 3mm;
    display: inline-block;
  }}
  .school-tagline {{
    font-size: 17pt; color: var(--ink); font-weight: 700;
    background: var(--hl); display: inline-block;
    padding: 3mm 7mm; border-radius: 4px; margin-top: 3mm;
    line-height: 1.3;
  }}
  .char-block {{ margin-top: 5mm; }}
  .char-head, .strat-head {{
    font-size: 16pt; font-weight: 900; color: var(--pop);
    border-left: 6px solid var(--pop); padding-left: 8mm;
    margin-bottom: 4mm;
  }}
  .char-body {{ font-size: 13pt; color: #2d3441; line-height: 1.65; padding-left: 4mm; }}
  .strat-block {{ margin-top: 5mm; flex: 1; }}
  .strat-grid {{ display: grid; grid-template-columns: 1fr; gap: 3mm; }}
  .strat-card {{
    border-left: 4px solid var(--ink); background: var(--soft);
    padding: 3.5mm 7mm; border-radius: 0 6px 6px 0;
    display: grid; grid-template-columns: 12mm 1fr; gap: 4mm; align-items:start;
  }}
  .strat-num {{ font-size: 20pt; font-weight: 900; color: var(--pop); line-height: 1; }}
  .strat-key {{ font-size: 14pt; font-weight: 900; color: var(--ink); margin-bottom: 1mm; grid-column: 2; }}
  .strat-val {{ font-size: 12pt; color: #2d3441; line-height: 1.5; grid-column: 2; }}

  /* ── 적중분석 표 + 도넛 ── */
  .analysis-page {{ }}
  .sec-head {{
    font-size: 22pt; font-weight: 900; color: var(--ink);
    border-left: 8px solid var(--pop); padding-left: 12px; margin: 0 0 5mm 0;
  }}
  .hit-banner {{
    background: linear-gradient(90deg, var(--ink) 0%, #27406d 100%); color:#fff;
    border-radius: 8px; padding: 4mm 7mm; display:flex;
    justify-content: space-between; align-items:center; margin-bottom: 5mm;
  }}
  .hit-banner .big {{ font-size: 18pt; font-weight: 900; letter-spacing: 1px; }}
  .hit-banner .sub {{ font-size: 10.5pt; opacity: 0.9; max-width: 115mm; line-height:1.4; margin-top: 1mm; }}
  .hit-banner .pct {{
    font-size: 38pt; font-weight: 900; color: var(--hl);
    text-shadow: 0 0 4px rgba(0,0,0,0.3);
  }}

  table.q {{ width:100%; border-collapse: collapse; font-size: 10.5pt; margin-top:2mm; }}
  table.q th {{ background: var(--ink); color:#fff; padding: 3px 6px; font-weight:700; font-size: 11pt; }}
  table.q td {{ padding: 2.4px 6px; border-bottom:1px solid #e3e7ee; line-height: 1.4; }}
  table.q td.c {{ text-align:center; }}
  table.q td.qno {{ font-weight: 800; color: var(--ink); }}
  table.q td.match {{ color:#28406d; font-weight:600; }}
  .dpill {{
    display:inline-block; min-width: 7mm; padding: 0.6mm 2.5mm; border-radius: 4mm;
    font-weight: 900; font-size: 10pt; color: #fff;
  }}
  .dpill.diff-하 {{ background: var(--ok); }}
  .dpill.diff-중 {{ background: var(--gold); color: var(--ink); }}
  .dpill.diff-상 {{ background: var(--pop); }}
  .gpill {{
    display:inline-block; min-width: 6mm; padding: 0.6mm 2.5mm; border-radius: 3mm;
    font-weight: 900; font-size: 10pt;
  }}
  .gpill.grade-A {{ background: var(--hl); color: var(--ink); border: 1.5px solid var(--ink); }}
  .gpill.grade-B {{ background: var(--gold); color: var(--ink); }}
  .gpill.grade-C {{ background: #e9ecf2; color: var(--muted); }}
  .gpill.grade-D {{ background: #f3f4f8; color: #9aa3b4; }}
  .hi-하 {{ color: var(--ok); font-weight: 900; }}
  .hi-중 {{ color: #c98a16; font-weight: 900; }}
  .hi-상 {{ color: var(--pop); font-weight: 900; }}

  /* ── 도넛 페이지 (위아래 정렬, 큰 사이즈, 퍼센티지) ── */
  .charts-page {{ display:flex; flex-direction:column; gap: 8mm; }}
  .chart-card {{
    border:1.5px solid var(--line); border-radius: 10px;
    padding: 4mm 8mm 6mm 8mm; background:#fff;
    display: grid; grid-template-columns: 50mm 1fr;
    align-items: center; gap: 8mm;
    height: 110mm;
  }}
  .chart-card h4 {{
    font-size: 18pt; color: var(--ink); font-weight: 900; margin: 0;
    text-align: left;
  }}
  .chart-wrap {{ position: relative; height: 100%; }}
  .chart-wrap canvas {{ position:absolute; inset:0; width:100% !important; height:100% !important; }}

  /* ── 전략 + 코멘트 페이지 ── */
  .strategy-page {{ }}
  .strat-page-head {{
    background: var(--ink); color: #fff; padding: 4mm 8mm;
    font-size: 16pt; font-weight: 900; letter-spacing: 2pt;
    border-radius: 4px; display: inline-block; margin-bottom: 6mm;
  }}
  .strat-row {{
    display:flex; gap: 6mm; padding: 5mm 4mm;
    border-bottom: 1.5px solid #ebeef4;
  }}
  .strat-row:last-child {{ border-bottom: none; }}
  .strat-row-key {{
    flex: 0 0 60mm; font-weight: 900; color: var(--ink); font-size: 15pt;
  }}
  .strat-row-val {{ flex: 1; color: #2d3441; line-height: 1.6; font-size: 12.5pt; }}
  .comment {{
    border-left: 8px solid var(--pop); background:#fff5f4; padding: 5mm 7mm;
    border-radius: 0 8px 8px 0; margin-top: 8mm; color: #2d3441; line-height: 1.65;
    font-size: 13pt;
  }}
  .comment .hdr {{
    display:block; font-weight: 900; color: var(--pop); margin-bottom:3mm;
    font-size: 17pt; letter-spacing: 1px;
  }}

  /* ── 핵심문제 페이지 ── */
  .key-page {{ }}
  .key-counter {{
    font-size: 11pt; color: var(--muted); letter-spacing: 4pt;
    font-weight: 700; margin-bottom: 3mm;
  }}
  .key-head {{
    display:flex; justify-content: space-between; align-items: center;
    border-bottom: 4px solid var(--ink); padding-bottom: 4mm; margin-bottom: 6mm;
  }}
  .key-no-pill {{
    font-size: 22pt; font-weight: 900; background: var(--ink); color: #fff;
    padding: 2mm 6mm; border-radius: 4mm; letter-spacing: 1px;
  }}
  .key-meta {{ color: var(--muted); font-size: 13pt; font-weight: 600; }}
  .key-body {{ display:grid; grid-template-columns: 1fr 1fr; gap: 7mm; }}
  .exam-card, .note-card {{
    border:1.5px solid var(--line); border-radius:8px; padding: 5mm 6mm; background:#fff;
    display:flex; flex-direction:column;
  }}
  .card-head {{
    font-size: 13pt; color:#fff; background: var(--ink);
    display:inline-block; padding: 2mm 5mm; border-radius: 4px;
    margin-bottom: 4mm; font-weight: 800; align-self:flex-start;
  }}
  .card-head.note-head {{ background: var(--pop); }}
  .exam-latex, .match-latex {{
    font-size: 12.5pt; line-height: 1.85; min-height: 90mm;
  }}
  .match-latex {{ color: #1d2433; }}
  .card-empty {{
    height: 100mm; display:flex; align-items:center; justify-content:center;
    color:#9aa3b4; font-size: 11pt;
  }}
  .match-cap {{
    margin-top: 5mm; padding-top: 4mm; border-top: 1px dashed var(--line);
    color: #2d3441; line-height: 1.6; font-size: 11.5pt;
  }}

  /* ── 핵심노트 견본 ── */
  .note-page {{ text-align:center; padding-top: 12mm; }}
  .note-page .note-title {{
    font-size: 24pt; font-weight: 900; color: var(--ink); margin-top: 2mm;
    margin-bottom: 3mm;
  }}
  .note-sub {{
    font-size: 13pt; color: var(--muted); margin-top: 0; margin-bottom: 8mm;
  }}
  .note-fan {{
    position: relative; width: 100%; height: 145mm; margin: 0 auto;
  }}
  .note-fan-card {{
    position: absolute;
    width: 60mm; height: auto; max-height: 100mm;
    border: 2px solid var(--ink); border-radius: 4px;
    box-shadow: 0 6px 14px rgba(15,29,58,0.3);
    background: #fff;
    transform-origin: 50% 80%;
  }}
  .note-fan-mask {{
    position: absolute; left: -10%; right: -10%; bottom: -2mm;
    height: 35mm;
    background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.95) 70%, rgba(255,255,255,1) 100%);
    pointer-events: none;
  }}
  .note-sample-tag {{
    margin-top: 8mm; font-size: 13pt; color: var(--pop);
    font-weight: 900; letter-spacing: 5pt;
  }}

  /* closing */
  .closing {{
    height: 297mm; padding: 0;
    display:flex; flex-direction:column; justify-content:center; align-items:center;
    background: linear-gradient(135deg, #fff 0%, var(--soft) 100%);
    text-align:center; box-sizing: border-box; padding: 40mm 16mm;
  }}
  .closing .badge {{ background: var(--pop); color:#fff; }}
  .closing .head {{
    font-size: 26pt; font-weight: 900; color: var(--ink);
    margin-top: 12mm; line-height: 1.4;
  }}
  .closing .head .hl {{ color: var(--pop); }}
  .closing .sub {{ font-size: 16pt; color: #2d3441; margin-top: 10mm; line-height: 1.65; }}
  .closing .tagline {{
    margin-top: 18mm; font-size: 26pt; font-weight: 900;
    color: var(--ink); letter-spacing: 1px;
    border-top: 4px solid var(--ink); border-bottom: 4px solid var(--ink);
    padding: 6mm 0; display: inline-block;
  }}
  .closing .signature {{
    margin-top: 14mm; font-size: 13pt; color: var(--muted); letter-spacing: 4pt;
  }}
  .closing .signature .name {{
    color: var(--ink); font-size: 17pt; font-weight: 900;
  }}
</style>
</head>
<body>

<!-- 표지 -->
<section class="page cover">
  <div class="top-tag">M A T H A R C H I V E</div>
  <div class="title-block">
    <div class="school">{school}</div>
    <div class="title-main">{title}<br>적중분석</div>
    <div class="title-sub">{subject} · {sub_range}</div>
  </div>
  <div class="photo-wrap">
    <img class="photo" src="{instructor_uri}"/>
  </div>
  <div>
    <div class="footer-mark"><span class="name">{instructor}</span> &nbsp;·&nbsp; {academy}</div>
    <div class="logo-wrap">{logo_block}</div>
  </div>
</section>

<!-- 프롤로그 + 솔루션 -->
{pr_sol_html}

<!-- 자료 소개 + 압도적 자료량 -->
{data_html}

<!-- 학교 분석 카드 -->
{school_slide_html}

<!-- 적중분석 표 -->
<section class="page analysis-page">
  <div class="sec-head">자체교재 적중 {hit_rate}%</div>
  <div class="hit-banner">
    <div>
      <div class="big">적중 {hit_count}/{len(questions)}문항 · 총배점 {total_score:.1f}점</div>
      <div class="sub">우리 교재가 다룬 유형이 그대로 출제. 등급 A는 동형(거의 동일 풀이 절차) 매칭.</div>
    </div>
    <div class="pct">{hit_rate}%</div>
  </div>
  <table class="q">
    <thead><tr><th>번호</th><th>중단원</th><th>배점</th><th>난이도</th><th>교재 매칭</th><th>등급</th></tr></thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>
</section>

<!-- 도넛차트 -->
<section class="page charts-page">
  <div class="sec-head">출제 분포</div>
  <div class="chart-card">
    <h4>중단원<br>분포</h4>
    <div class="chart-wrap"><canvas id="chartChapter"></canvas></div>
  </div>
  <div class="chart-card">
    <h4>난이도<br>분포</h4>
    <div class="chart-wrap"><canvas id="chartDiff"></canvas></div>
  </div>
</section>

<!-- 시험대비전략 + 코멘트 -->
<section class="page strategy-page">
  <div class="strat-page-head">시험대비 전략</div>
  <div class="strat-grid" style="display:flex;flex-direction:column;gap:4mm;">
    {strategy_html}
  </div>
  <div class="comment">
    <span class="hdr">{instructor} 코멘트</span>
    {instructor_comment}
  </div>
</section>

<!-- 핵심문제 -->
{key_pages}

<!-- 핵심노트 견본 -->
{note_html}

<!-- closing -->
<section class="page closing">
  <div class="badge">이영우T의 약속</div>
  <div class="head">"{school} 내신 족보,<br>핵심노트와 교재에 모두 담았습니다."</div>
  <div class="sub">이 교재를 믿고 반복하는 학생이 결국 1등급을 쟁취합니다.</div>
  <div class="tagline">성적으로 증명하겠습니다.</div>
  <div class="signature">수학 Instructor &nbsp;<span class="name">{instructor.replace('T','')}</span></div>
</section>

<script>
window.addEventListener('load', () => {{
  Chart.register(ChartDataLabels);
  const data = {chart_json};
  const palette = ['#0f1419','#27406d','#3d5e9a','#ff3a3a','#ffc83d','#1f9d5f','#caff3d','#a378ff'];
  const diffColors = {{ '하':'#1f9d5f', '중':'#ffc83d', '상':'#ff3a3a' }};

  const total = (kind) => data[kind].data.reduce((a,b)=>a+b, 0);

  const opts = (kind) => {{
    const labels = data[kind].labels;
    const colors = (kind === 'difficulty')
      ? labels.map(l => diffColors[l] || '#888')
      : palette;
    const t = total(kind);
    return {{
      type: 'doughnut',
      data: {{
        labels: labels,
        datasets: [{{
          data: data[kind].data,
          backgroundColor: colors,
          borderWidth: 2, borderColor: '#fff'
        }}]
      }},
      options: {{
        animation: false, cutout: '50%',
        layout: {{ padding: 4 }},
        plugins: {{
          legend: {{
            position:'right',
            labels: {{
              font: {{ size: 13, weight: '700' }},
              padding: 8, boxWidth: 18, color: '#0f1419',
              usePointStyle: false
            }}
          }},
          tooltip: {{ enabled: false }},
          datalabels: {{
            color: (ctx) => {{
              const lbl = ctx.chart.data.labels[ctx.dataIndex];
              return (lbl === '중') ? '#0f1419' : '#fff';
            }},
            font: {{ size: 13, weight: '900' }},
            formatter: (v, ctx) => {{
              const pct = Math.round(v / t * 100);
              return pct + '%';
            }}
          }}
        }},
        maintainAspectRatio: false,
      }}
    }};
  }};
  new Chart(document.getElementById('chartChapter'), opts('chapter'));
  new Chart(document.getElementById('chartDiff'),    opts('difficulty'));
  window.__chartsRendered = true;
}});
</script>

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

    short = cfg["short_name"]
    title_safe = cfg["exam_title"].replace(" ", "_").replace("/", "-")
    out_html = PA / f"{short}_{title_safe}_적중분석.html"
    out_pdf  = PA / f"{short}_{title_safe}_적중분석.pdf"
    out_html.write_text(html_doc(cfg), encoding="utf-8")
    print(f"HTML: {out_html}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(out_html.as_uri(), wait_until="networkidle")
        page.wait_for_function("window.__chartsRendered === true", timeout=10000)
        page.wait_for_timeout(700)
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
