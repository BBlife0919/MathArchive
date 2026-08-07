#!/usr/bin/env python3
"""기출 적중분석 분석지 생성기 v2 (학교 단위 자동 생성).

입력: 학교 config JSON (output/pirate_analysis/configs/<학교>.json)
출력: HTML + PDF (output/pirate_analysis/<학교>_<시험>_적중분석.{html,pdf})

v2.1 개선 (카드뉴스 임팩트 강화):
- 네온 그린 뱃지 헤더 ('시험구성', '시험총평' 등)
- 큰 폰트 + 색상 강조 (포인트 컬러)
- 시험구성/시험총평 섹션 추가
- 도넛차트 가독성 개선 (큰 라벨, 구획 색)
- 핵심노트는 견본 PDF 페이지를 stack 형태로 부분 노출
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
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "svg": "image/svg+xml"}.get(ext, "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def asset(school_short: str, name: str) -> Path:
    if not name:
        return ASSETS / "_missing_"
    p = ASSETS / school_short / name
    if p.exists():
        return p
    if name.startswith("yutype_"):
        stem = name.replace("yutype_", "").rsplit(".", 1)[0]
        try:
            num = int(stem)
            padded = ASSETS / "yutype" / f"yutype_{num:02d}.png"
            if padded.exists():
                return padded
        except ValueError:
            pass
        p = ASSETS / "yutype" / name
        if p.exists():
            return p
    p = ASSETS / name
    return p


def render_questions_table(questions: list[dict]) -> str:
    rows = []
    for qd in questions:
        rows.append(
            f"<tr>"
            f"<td class='c qno'>{qd['q']}</td>"
            f"<td>{qd['chapter']}</td>"
            f"<td class='c'>{qd['score']}</td>"
            f"<td class='c diff-{qd['difficulty']}'><span class='diff-pill diff-{qd['difficulty']}'>{qd['difficulty']}</span></td>"
            f"<td class='match'>유형{qd['matched_yutype']} — {qd['matched_title']}</td>"
            f"<td class='c'><span class='grade-pill grade-{qd['grade']}'>{qd['grade']}</span></td>"
            f"</tr>"
        )
    return "\n".join(rows)


def render_chapter_table(questions: list[dict]) -> str:
    counts = Counter(q["chapter"] for q in questions)
    # 표준 챕터 순서
    order = ["다항식의 연산", "항등식과 나머지정리", "인수분해", "복소수", "이차방정식", "이차함수", "고차방정식",
             "지수", "로그", "지수함수", "로그함수", "삼각함수", "삼각함수의 그래프"]
    items = sorted(counts.items(), key=lambda x: order.index(x[0]) if x[0] in order else 99)
    rows = []
    for chap, n in items:
        rows.append(f"<tr><td>{chap}</td><td class='c bignum'>{n} 문항</td></tr>")
    return "\n".join(rows)


def render_highlights(highlights: list[dict]) -> str:
    rows = []
    for h in highlights:
        rows.append(
            f"<div class='hl-row'>"
            f"<div class='hl-icon'>+</div>"
            f"<div class='hl-body'>"
            f"<div class='hl-key'>{h['k']}</div>"
            f"<div class='hl-val'>{h['v']}</div>"
            f"</div></div>"
        )
    return "\n".join(rows)


def render_stars(stars: int, total: int = 5) -> str:
    out = []
    for i in range(total):
        cls = "star-on" if i < stars else "star-off"
        out.append(f"<span class='{cls}'>★</span>")
    return "".join(out)


def render_key_pages(school_short: str, key_problems: list[dict]) -> str:
    pages = []
    for kp in key_problems:
        exam_uri = img_data_uri(asset(school_short, kp.get("exam_image", "")))
        match_uri = img_data_uri(asset(school_short, kp.get("matched_image", "")))
        if exam_uri:
            exam_block = f"<img src='{exam_uri}' class='card-img'/>"
        elif kp.get("exam_latex"):
            exam_block = f"<div class='exam-latex'>{kp['exam_latex']}</div>"
        else:
            exam_block = "<div class='exam-empty'>(시험 발문 이미지 미제공)</div>"

        if match_uri:
            match_block = f"<img src='{match_uri}' class='card-img'/>"
        else:
            match_block = "<div class='exam-empty'>(교재 매칭 이미지 미제공)</div>"

        pages.append(f"""
<section class="page key-page">
  <div class="key-head">
    <div class="key-no-pill">시험지 {kp['q']}번</div>
    <div class="key-meta">{kp['topic']} · 배점 {kp['score']} · 난이도 <span class='hi-{kp['difficulty']}'>{kp['difficulty']}</span></div>
  </div>
  <div class="key-body">
    <div class="exam-card">
      <div class="card-head exam-head">시험 출제 문항</div>
      {exam_block}
    </div>
    <div class="note-card">
      <div class="card-head note-head">{kp['matched_title']}</div>
      {match_block}
      <div class="match-cap">{kp['comment']}</div>
    </div>
  </div>
</section>
""")
    return "\n".join(pages)


def render_note_sample_page(school_short: str, note_intro: str, note_sample_images: list[str], academy: str) -> str:
    uris = [img_data_uri(asset(school_short, n)) for n in note_sample_images]
    uris = [u for u in uris if u]
    if not uris:
        return ""
    # stacked tilted preview — first 3 pages
    layers = []
    rotations = [-6, 0, 6]
    z_indices = [1, 3, 2]
    for i, u in enumerate(uris[:3]):
        rot = rotations[i] if i < len(rotations) else 0
        z = z_indices[i] if i < len(z_indices) else 1
        layers.append(
            f"<img src='{u}' class='note-stack-img' style='transform: rotate({rot}deg); z-index:{z};'/>"
        )
    layers_html = "".join(layers)
    return f"""
<section class="page note-intro-page">
  <div class="badge-head">핵심노트 견본</div>
  <div class="note-intro-head">{note_intro}</div>
  <div class="note-intro-sub">시험 출제 핵심 패턴을 한 줄로 정리한 직강 노트 — 견본 페이지 미리보기</div>
  <div class="note-stack">
    {layers_html}
    <div class="note-stack-mask"></div>
  </div>
  <div class="note-sample-tag">SAMPLE · {academy}</div>
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
    strategy = cfg["strategy"]
    note_intro = cfg.get("note_intro", "이영우T가 직접 작성한 핵심노트")
    note_sample_images = cfg.get("note_sample_images", [])
    exam_summary = cfg.get("exam_summary", {})

    instructor_uri = img_data_uri(asset(short, "instructor.png"))
    logo_uri = img_data_uri(asset(short, "logo.png"))

    table_rows = render_questions_table(questions)
    chap_table = render_chapter_table(questions)
    total_score = sum(q["score"] for q in questions)
    hit_count = sum(1 for q in questions if q["grade"] in ("A", "B"))
    hit_rate = round(hit_count / len(questions) * 100)
    chart_json = chart_payload(questions)

    key_pages_html = render_key_pages(short, key_problems)
    note_page_html = render_note_sample_page(short, note_intro, note_sample_images, academy)

    strategy_html = "\n".join(
        f"<div class='strat-row'>"
        f"<div class='strat-key'>{s['key']}</div>"
        f"<div class='strat-val'>{s['value']}</div>"
        f"</div>"
        for s in strategy
    )

    logo_block = (
        f"<img class='logo' src='{logo_uri}' alt='{academy}'/>"
        if logo_uri
        else f"<div class='logo-placeholder'>{academy}</div>"
    )

    # 시험총평 데이터
    diff_stars = exam_summary.get("difficulty_stars", 3)
    highlights = exam_summary.get("highlights", [])
    highlights_html = render_highlights(highlights)
    structure_text = exam_summary.get("structure", f"문항 {len(questions)}개")
    ranges_text = exam_summary.get("ranges", sub_range)

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
    --neon: #caff3d;
    --ink: #111418;
    --pop: #ff3939;
    --gold: #ffc83d;
    --ok: #1f9d5f;
    --line: #d6dbe4;
    --muted: #56607a;
  }}
  @page {{ size: A4; margin: 12mm 12mm 10mm 12mm; }}
  html, body {{ margin:0; padding:0; }}
  body {{
    font-family: "AppleSDGothicNeo-Bold","AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif;
    color: var(--ink); font-size:13.5pt; line-height:1.55;
  }}
  .page {{ page-break-after: always; padding: 0; }}
  .page:last-child {{ page-break-after: auto; }}

  /* 네온 뱃지 헤더 */
  .badge-head {{
    display:inline-block; background: var(--neon); color: var(--ink);
    font-weight: 900; font-size: 22pt; padding: 4mm 8mm 3.5mm 8mm;
    border-radius: 4mm; letter-spacing: 4pt; margin-bottom: 7mm;
    border: 2.5px solid var(--ink);
    box-shadow: 0 0 0 4px var(--neon);
  }}

  /* 표지 */
  .cover {{
    height: 255mm; display:flex; flex-direction:column;
    justify-content: space-between; align-items:center; text-align:center;
  }}
  .cover .school {{ font-size: 22pt; color:#3a4760; letter-spacing:1px; font-weight:700; }}
  .cover .title {{
    font-size: 32pt; font-weight: 900; margin-top: 5mm; color: var(--ink);
    border-top: 5px solid var(--ink); border-bottom: 5px solid var(--ink); padding: 6mm 0;
    line-height: 1.2;
  }}
  .cover .title .line1 {{ display:block; font-size: 22pt; font-weight: 700; color:#3a4760; }}
  .cover .title .line2 {{ display:block; margin-top: 2mm; }}
  .cover .subject {{ font-size: 16pt; color: var(--muted); margin-top: 4mm; }}
  .cover .photo-wrap {{ flex:1; display:flex; align-items:center; justify-content:center; padding: 3mm 0; min-height: 0; }}
  .cover .photo {{ max-width: 95mm; max-height: 120mm; width:auto; height:auto; object-fit: contain; }}
  .cover .name {{ font-size: 30pt; font-weight: 900; color: var(--ink); margin-top: 2mm; letter-spacing: 1px; }}
  .cover .logo-wrap {{ display:flex; justify-content:center; align-items:center; padding: 3mm 0; }}
  .cover .logo {{ max-height: 22mm; max-width: 70mm; }}
  .cover .logo-placeholder {{
    color:#9aa3b4; border:1.5px dashed #cdd2dc; padding: 3mm 7mm; border-radius: 4px;
    font-size: 12pt; letter-spacing: 2px;
  }}

  /* ── 시험구성 ── */
  .construction-list {{ margin-top: 0; }}
  .construction-row {{ display:flex; align-items:flex-start; gap: 6mm; margin-bottom: 6mm; }}
  .check-circle {{
    flex: 0 0 auto; width: 14mm; height: 14mm; border-radius: 50%;
    border: 2.5px solid var(--ink); display:flex; align-items:center; justify-content:center;
    font-size: 18pt; font-weight: 900;
  }}
  .construction-row .lbl {{ font-size: 22pt; font-weight: 900; color: var(--ink); margin-right: 4mm; }}
  .construction-row .val {{ font-size: 17pt; color: var(--ink); padding-top: 2mm; }}

  table.chap-table {{
    width: 80%; margin: 4mm auto 0 auto; border-collapse: collapse;
    font-size: 16pt;
  }}
  table.chap-table td {{
    padding: 5mm 6mm; border:1px solid #cfd5e0; text-align:center;
  }}
  table.chap-table td:first-child {{ font-weight: 700; }}
  .bignum {{ font-weight: 900; color: var(--pop); font-size: 18pt; }}

  /* ── 시험총평 ── */
  .star-row {{
    display:flex; align-items:center; gap: 4mm; margin-bottom: 7mm;
    font-size: 22pt; font-weight: 900;
  }}
  .star-on {{ color: var(--gold); font-size: 36pt; }}
  .star-off {{ color: #d6dbe4; font-size: 36pt; }}
  .star-score {{ color: var(--muted); font-size: 18pt; margin-left: 3mm; }}
  .star-label {{ font-size: 26pt; font-weight: 900; color: var(--ink); }}

  .hl-row {{
    display:flex; align-items:flex-start; gap: 5mm; margin-bottom: 6mm;
  }}
  .hl-icon {{
    flex: 0 0 auto; width: 10mm; height: 10mm; border-radius: 50%;
    background: var(--ink); color: #fff; font-weight: 900; font-size: 16pt;
    display:flex; align-items:center; justify-content:center;
  }}
  .hl-body {{ flex: 1; }}
  .hl-key {{ font-size: 17pt; font-weight: 900; color: var(--ink); margin-bottom: 1.5mm; }}
  .hl-val {{ font-size: 13.5pt; color: #2d3441; line-height: 1.55; }}

  /* ── 적중분석 (표 + 차트) ── */
  .sec-head {{
    font-size: 20pt; font-weight: 900; color: var(--ink);
    border-left: 7px solid var(--pop); padding-left: 10px; margin: 0 0 3mm 0;
  }}
  .hit-banner {{
    background: linear-gradient(90deg, var(--ink) 0%, #27406d 100%); color:#fff;
    border-radius: 8px; padding: 3mm 7mm; display:flex;
    justify-content: space-between; align-items:center; margin-bottom: 2mm;
  }}
  .hit-banner .big {{ font-size: 17pt; font-weight: 900; letter-spacing: 1px; }}
  .hit-banner .sub {{ font-size: 10pt; opacity: 0.9; max-width: 115mm; line-height:1.35; margin-top: 0.5mm; }}
  .hit-banner .pct {{
    font-size: 34pt; font-weight: 900; color: var(--neon);
    text-shadow: 0 0 4px rgba(0,0,0,0.3);
  }}

  .charts {{ display:flex; gap: 4mm; margin: 1mm 0 1mm 0; }}
  .chart-card {{
    flex:1; border:1.5px solid var(--line); border-radius:8px; padding: 1mm 2mm 0.5mm 2mm;
    background:#fff; height: 42mm;
    display:flex; flex-direction:column;
  }}
  .chart-card h4 {{ margin: 0; font-size: 11pt; color: var(--ink); text-align:center; font-weight: 800; }}
  .chart-wrap {{ flex:1; position: relative; min-height: 0; }}
  .chart-wrap canvas {{ position:absolute; inset:0; width:100% !important; height:100% !important; }}

  table.q {{ width:100%; border-collapse: collapse; font-size: 9.6pt; margin-top:0.5mm; }}
  table.q th {{ background: var(--ink); color:#fff; padding: 2.2px 5px; font-weight:700; font-size: 10pt; }}
  table.q td {{ padding: 1.6px 5px; border-bottom:1px solid #e3e7ee; line-height: 1.35; }}
  table.q td.c {{ text-align:center; }}
  table.q td.qno {{ font-weight: 800; color: var(--ink); }}
  table.q td.match {{ color:#28406d; font-weight:600; }}
  .diff-pill {{
    display:inline-block; min-width: 7mm; padding: 0.4mm 2mm; border-radius: 4mm;
    font-weight: 900; font-size: 10pt; color: #fff;
  }}
  .diff-pill.diff-하 {{ background: var(--ok); }}
  .diff-pill.diff-중 {{ background: var(--gold); color: var(--ink); }}
  .diff-pill.diff-상 {{ background: var(--pop); }}
  .grade-pill {{
    display:inline-block; min-width: 6mm; padding: 0.4mm 1.8mm; border-radius: 3mm;
    font-weight: 900; font-size: 10pt;
  }}
  .grade-pill.grade-A {{ background: var(--neon); color: var(--ink); border:1.5px solid var(--ink); }}
  .grade-pill.grade-B {{ background: var(--gold); color: var(--ink); }}
  .grade-pill.grade-C {{ background: #e9ecf2; color: var(--muted); }}
  .grade-pill.grade-D {{ background: #f3f4f8; color: #9aa3b4; }}

  .hi-하 {{ color: var(--ok); font-weight: 900; }}
  .hi-중 {{ color: #c98a16; font-weight: 900; }}
  .hi-상 {{ color: var(--pop); font-weight: 900; }}

  /* ── 전략 + 코멘트 페이지 ── */
  .strat-row {{
    display:flex; gap: 6mm; padding: 5mm 0;
    border-bottom: 1.5px solid #ebeef4;
  }}
  .strat-row:last-child {{ border-bottom: none; }}
  .strat-key {{
    flex: 0 0 60mm; font-weight: 900; color: var(--ink); font-size: 16pt;
  }}
  .strat-val {{ flex: 1; color: #2d3441; line-height: 1.55; font-size: 13.5pt; }}
  .strat-key .strong {{ color: var(--pop); }}

  .comment {{
    border-left: 8px solid var(--pop); background:#fff5f4; padding: 5mm 7mm;
    border-radius: 0 8px 8px 0; margin-top: 8mm; color: #2d3441; line-height: 1.6;
    font-size: 14pt;
  }}
  .comment .hdr {{
    display:block; font-weight: 900; color: var(--pop); margin-bottom:3mm;
    font-size: 18pt; letter-spacing: 1px;
  }}
  .comment strong {{ color: var(--pop); }}

  /* ── 핵심문제 페이지 ── */
  .key-page {{ }}
  .key-head {{
    display:flex; justify-content: space-between; align-items: center;
    border-bottom: 4px solid var(--ink); padding-bottom: 4mm; margin-bottom: 6mm;
  }}
  .key-no-pill {{
    font-size: 22pt; font-weight: 900; background: var(--ink); color: #fff;
    padding: 2mm 6mm; border-radius: 4mm; letter-spacing: 1px;
  }}
  .key-meta {{ color: var(--muted); font-size: 14pt; font-weight: 600; }}
  .key-body {{ display:grid; grid-template-columns: 1fr 1fr; gap: 7mm; }}
  .exam-card, .note-card {{
    border:1.5px solid var(--line); border-radius:8px; padding: 5mm 5mm; background:#fff;
    display:flex; flex-direction:column;
  }}
  .card-head {{
    font-size: 13pt; color:#fff; background: var(--ink);
    display:inline-block; padding: 2mm 4mm; border-radius: 4px;
    margin-bottom: 4mm; font-weight: 800; align-self:flex-start;
  }}
  .note-head {{ background: var(--pop); }}
  .card-img {{
    width: 100%; max-height: 145mm; object-fit: contain;
    border:1px solid #ccd2dd; border-radius: 5px; padding: 1mm; background:#fff;
  }}
  .exam-empty {{
    height: 130mm; display:flex; align-items:center; justify-content:center;
    color:#9aa3b4; border:1px dashed #cdd2dc; border-radius:5px; font-size: 11pt;
  }}
  .exam-latex {{ font-size: 14pt; line-height: 1.7; }}
  .match-cap {{ margin-top: 5mm; color: #2d3441; line-height: 1.6; font-size: 12pt; }}

  /* ── 핵심노트 견본 페이지 ── */
  .note-intro-page {{ padding-top: 4mm; text-align:center; }}
  .note-intro-head {{
    font-size: 26pt; font-weight: 900; color: var(--ink); margin-bottom: 3mm;
  }}
  .note-intro-sub {{ font-size: 14pt; color: var(--muted); margin-bottom: 15mm; }}
  .note-stack {{
    position: relative; width: 100%; height: 145mm;
    display:flex; align-items:center; justify-content:center;
  }}
  .note-stack-img {{
    position: absolute; max-width: 90mm; max-height: 130mm;
    border: 2px solid var(--ink); border-radius: 4px;
    box-shadow: 0 6px 14px rgba(15,29,58,0.25);
    background:#fff;
  }}
  .note-stack-mask {{
    position: absolute; left: 0; right: 0; bottom: 0; height: 50mm;
    background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.95) 70%, rgba(255,255,255,1) 100%);
    pointer-events: none;
  }}
  .note-sample-tag {{
    margin-top: 6mm; font-size: 13pt; color: var(--pop);
    font-weight: 900; letter-spacing: 4pt;
  }}

  /* ── 마지막 closing ── */
  .closing {{
    text-align:center; height: 250mm;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
  }}
  .closing .h0 {{ font-size: 16pt; color: var(--muted); letter-spacing: 4px; font-weight: 700; }}
  .closing .h1 {{
    font-size: 60pt; font-weight: 900; color: var(--ink); margin: 6mm 0;
    letter-spacing: 2px;
  }}
  .closing .h1 .pop {{ color: var(--pop); }}
  .closing .h2 {{ font-size: 24pt; color: var(--pop); font-weight: 900; margin-top: 6mm; }}
  .closing .h3 {{ font-size: 14pt; color: var(--muted); margin-top: 12mm; letter-spacing:2px; }}
</style>
</head>
<body>

<!-- 표지 -->
<section class="page cover">
  <div>
    <div class="school">{school}</div>
    <div class="title"><span class="line1">{title}</span><span class="line2">적중분석</span></div>
    <div class="subject">{subject} · {sub_range}</div>
  </div>
  <div class="photo-wrap">
    <img class="photo" src="{instructor_uri}"/>
  </div>
  <div>
    <div class="name">{instructor}</div>
  </div>
  <div class="logo-wrap">{logo_block}</div>
</section>

<!-- 시험구성 -->
<section class="page">
  <div class="badge-head">시 험 구 성</div>
  <div class="construction-list">
    <div class="construction-row">
      <div class="check-circle">✓</div>
      <div class="lbl">시험범위</div>
      <div class="val">{ranges_text}</div>
    </div>
    <div class="construction-row">
      <div class="check-circle">✓</div>
      <div class="lbl">문항구성</div>
      <div class="val">{structure_text}</div>
    </div>
    <div class="construction-row">
      <div class="check-circle">✓</div>
      <div class="lbl">출제비율</div>
    </div>
  </div>
  <table class="chap-table">
    <tbody>
      {chap_table}
    </tbody>
  </table>
</section>

<!-- 시험총평 -->
<section class="page">
  <div class="badge-head">시 험 총 평</div>
  <div class="star-row">
    <span class="check-circle">✓</span>
    <span class="star-label">출제난이도</span>
    {render_stars(diff_stars)}
    <span class="star-score">/ 5</span>
  </div>
  {highlights_html}
</section>

<!-- 적중분석 (표 + 차트 한 페이지) -->
<section class="page">
  <div class="sec-head">자체교재 적중 {hit_rate}%</div>
  <div class="hit-banner">
    <div>
      <div class="big">적중 {hit_count}/{len(questions)}문항 · 총배점 {total_score:.1f}점</div>
      <div class="sub">우리 교재가 다룬 유형이 그대로 출제. 등급 A는 동형(거의 동일 풀이 절차) 매칭. 시험 전 범위 핵심 유형 모두 커버.</div>
    </div>
    <div class="pct">{hit_rate}%</div>
  </div>

  <div class="charts">
    <div class="chart-card"><h4>중단원 분포</h4><div class="chart-wrap"><canvas id="chartChapter"></canvas></div></div>
    <div class="chart-card"><h4>난이도 분포</h4><div class="chart-wrap"><canvas id="chartDiff"></canvas></div></div>
  </div>

  <table class="q">
    <thead><tr><th>번호</th><th>중단원</th><th>배점</th><th>난이도</th><th>교재 매칭</th><th>등급</th></tr></thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>
</section>

<!-- 시험대비 전략 + 이영우T 코멘트 -->
<section class="page">
  <div class="badge-head">시 험 대 비 전 략</div>
  <div>
    {strategy_html}
  </div>

  <div class="comment">
    <span class="hdr">{instructor} 코멘트</span>
    {instructor_comment}
  </div>
</section>

<!-- 핵심문제 매칭 -->
{key_pages_html}

<!-- 핵심노트 견본 -->
{note_page_html}

<!-- 마지막 closing -->
<section class="page closing">
  <div class="h0">2026 학년도 기출 적중 분석</div>
  <div class="h1">압도적인 <span class="pop">적중</span></div>
  <div class="h2">{instructor}와 함께</div>
  <div class="h3">M A T H A R C H I V E &nbsp;·&nbsp; {academy}</div>
</section>

<script>
window.addEventListener('load', () => {{
  const data = {chart_json};
  const palette = ['#0f1d3a','#27406d','#3d5e9a','#ff3939','#ffc83d','#1f9d5f','#caff3d'];
  const diffColors = {{ '하':'#1f9d5f', '중':'#ffc83d', '상':'#ff3939' }};

  const makeOpt = (kind) => {{
    const labels = data[kind].labels;
    const colors = (kind === 'difficulty')
      ? labels.map(l => diffColors[l] || '#888')
      : palette;
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
        animation: false,
        cutout: '50%',
        plugins: {{
          legend: {{
            position:'bottom',
            labels: {{
              font: {{ size: 11, weight: '700' }},
              padding: 6, boxWidth: 14, color: '#111418'
            }}
          }},
          tooltip: {{ enabled: false }},
          datalabels: {{
            color: '#fff', font: {{ size: 13, weight: '900' }},
            formatter: (v) => v + '문항'
          }}
        }},
        maintainAspectRatio: false,
      }},
      plugins: [ChartDataLabels]
    }};
  }};
  new Chart(document.getElementById('chartChapter'), makeOpt('chapter'));
  new Chart(document.getElementById('chartDiff'),    makeOpt('difficulty'));
  window.__chartsRendered = true;
}});
</script>

</body>
</html>
"""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("config")
    args = p.parse_args()

    cfg_path = CONFIGS / f"{args.config}.json"
    if not cfg_path.exists():
        print(f"config not found: {cfg_path}", file=sys.stderr)
        return 1
    cfg = json.loads(cfg_path.read_text())

    short = cfg["short_name"]
    title_safe = cfg["exam_title"].replace(" ", "_").replace("/", "-")
    out_html = PA / f"{short}_{title_safe}_적중분석.html"
    out_pdf  = PA / f"{short}_{title_safe}_적중분석.pdf"

    html = html_doc(cfg)
    out_html.write_text(html, encoding="utf-8")
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
            margin={"top": "12mm", "bottom": "10mm", "left": "12mm", "right": "12mm"},
        )
        browser.close()
    print(f"PDF : {out_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
