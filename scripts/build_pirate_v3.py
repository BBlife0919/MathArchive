#!/usr/bin/env python3
"""기출 적중분석 분석지 생성기 v3 — 통합 리포트 톤 + 학교별 단일 PDF.

페이지 구성:
1. 표지 (학교명/시험명/사진/이름/로고)
2. 시험 구성 + 시험 총평 (선택)
3. 적중분석 표 + 도넛 + 시험대비전략 + 이영우T 코멘트 (Image 12)
4-7. 핵심문제 4개 (시험 vs 교재 fabricated, Image 13)
8. 핵심노트 견본 (펼쳐진 부채꼴)
9. 압도적인 적중 (closing)
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


def render_strategy(strats: list[dict]) -> str:
    return "\n".join(
        f"<div class='strat-row'>"
        f"<div class='strat-key'>{s['key']}</div>"
        f"<div class='strat-val'>{s['value']}</div>"
        f"</div>"
        for s in strats
    )


def render_key_problem(school_short: str, kp: dict, idx: int, total: int) -> str:
    fab = kp.get("fabricated_latex") or kp.get("matched_image_caption", "")
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
<section class="page note-page">
  <div class="badge">핵심노트 견본</div>
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
    strategy = cfg["strategy"]
    note_intro = cfg.get("note_intro", "이영우T 핵심노트")
    note_sub = cfg.get("note_sub", "시험 출제 핵심 패턴을 한 줄로 정리한 직강 노트")
    note_sample_images = cfg.get("note_sample_images", [
        "note_sample_1.png", "note_sample_2.png", "note_sample_3.png"
    ])

    instructor_uri = img_data_uri(asset(short, "instructor.png"))
    logo_uri = img_data_uri(asset(short, "logo.png"))

    table_rows = render_q_table(questions)
    total_score = sum(q["score"] for q in questions)
    hit_count = sum(1 for q in questions if q["grade"] in ("A", "B"))
    hit_rate = round(hit_count / len(questions) * 100)
    chart_json = chart_payload(questions)

    strategy_html = render_strategy(strategy)
    key_pages = "\n".join(
        render_key_problem(short, kp, i+1, len(key_problems))
        for i, kp in enumerate(key_problems)
    )
    note_html = render_note_fan(short, note_intro, note_sub, note_sample_images)

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
  @page {{ size: A4; margin: 14mm 14mm 12mm 14mm; }}
  html, body {{ margin:0; padding:0; }}
  body {{
    font-family: "AppleSDGothicNeo-Bold","AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif;
    color: var(--ink); font-size: 13pt; line-height: 1.55;
  }}
  .page {{ page-break-after: always; padding: 0; }}
  .page:last-child {{ page-break-after: auto; }}

  /* 표지 */
  .cover {{
    height: 270mm; display:flex; flex-direction:column;
    justify-content: space-between; align-items:center; text-align:center;
  }}
  .cover .school {{ font-size: 22pt; color:#3a4760; letter-spacing:1px; font-weight:700; }}
  .cover .title {{
    font-size: 30pt; font-weight: 900; margin-top: 5mm; color: var(--ink);
    border-top: 5px solid var(--ink); border-bottom: 5px solid var(--ink); padding: 6mm 0;
    line-height: 1.2;
  }}
  .cover .title .line1 {{ display:block; font-size: 22pt; font-weight: 700; color:#3a4760; }}
  .cover .title .line2 {{ display:block; margin-top: 2mm; }}
  .cover .subject {{ font-size: 16pt; color: var(--muted); margin-top: 4mm; }}
  .cover .photo-wrap {{ flex:1; display:flex; align-items:center; justify-content:center; padding: 3mm 0; min-height: 0; }}
  .cover .photo {{ max-width: 95mm; max-height: 125mm; width:auto; height:auto; object-fit: contain; }}
  .cover .name {{ font-size: 30pt; font-weight: 900; color: var(--ink); margin-top: 2mm; letter-spacing: 1px; }}
  .cover .logo-wrap {{ display:flex; justify-content:center; align-items:center; padding: 3mm 0; }}
  .cover .logo {{ max-height: 22mm; max-width: 70mm; }}
  .cover .logo-placeholder {{
    color:#9aa3b4; border:1.5px dashed #cdd2dc; padding: 3mm 7mm; border-radius: 4px;
    font-size: 12pt; letter-spacing: 2px;
  }}

  /* 적중분석 페이지 */
  .sec-head {{
    font-size: 22pt; font-weight: 900; color: var(--ink);
    border-left: 8px solid var(--pop); padding-left: 12px; margin: 0 0 4mm 0;
  }}
  .hit-banner {{
    background: linear-gradient(90deg, var(--ink) 0%, #27406d 100%); color:#fff;
    border-radius: 8px; padding: 4mm 7mm; display:flex;
    justify-content: space-between; align-items:center; margin-bottom: 4mm;
  }}
  .hit-banner .big {{ font-size: 19pt; font-weight: 900; letter-spacing: 1px; }}
  .hit-banner .sub {{ font-size: 10.5pt; opacity: 0.9; max-width: 115mm; line-height:1.4; margin-top: 1mm; }}
  .hit-banner .pct {{
    font-size: 38pt; font-weight: 900; color: var(--hl);
    text-shadow: 0 0 4px rgba(0,0,0,0.3);
  }}

  .charts {{ display:flex; flex-direction: column; gap: 6mm; margin: 4mm 0 4mm 0; }}
  .chart-card {{
    border:1.5px solid var(--line); border-radius:8px; padding: 4mm 6mm 4mm 6mm;
    background:#fff; height: 75mm;
    display:flex; flex-direction:row; align-items:center; gap: 8mm;
  }}
  .chart-card h4 {{ font-size: 14pt; color: var(--ink); font-weight: 800; margin: 0;
                    flex: 0 0 35mm; text-align: left; }}
  .chart-wrap {{ flex:1; position: relative; min-height: 0; height: 100%; }}
  .chart-wrap canvas {{ position:absolute; inset:0; width:100% !important; height:100% !important; }}

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

  /* 시험대비 전략 + 코멘트 페이지 */
  .strategy-page {{ }}
  .strat-block-head {{
    background: var(--ink); color: #fff; padding: 4mm 8mm;
    font-size: 16pt; font-weight: 900; letter-spacing: 2pt;
    border-radius: 4px; display: inline-block; margin-bottom: 6mm;
  }}
  .strat-row {{
    display:flex; gap: 6mm; padding: 5mm 4mm;
    border-bottom: 1.5px solid #ebeef4;
  }}
  .strat-row:last-child {{ border-bottom: none; }}
  .strat-key {{
    flex: 0 0 60mm; font-weight: 900; color: var(--ink); font-size: 15pt;
  }}
  .strat-val {{ flex: 1; color: #2d3441; line-height: 1.6; font-size: 13pt; }}

  .comment {{
    border-left: 8px solid var(--pop); background:#fff5f4; padding: 5mm 7mm;
    border-radius: 0 8px 8px 0; margin-top: 8mm; color: #2d3441; line-height: 1.65;
    font-size: 13pt;
  }}
  .comment .hdr {{
    display:block; font-weight: 900; color: var(--pop); margin-bottom:3mm;
    font-size: 17pt; letter-spacing: 1px;
  }}

  /* 핵심문제 페이지 */
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
    font-size: 13pt; line-height: 1.85; min-height: 90mm;
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

  /* 핵심노트 견본 */
  .note-page {{ text-align:center; padding-top: 3mm; }}
  .note-page .badge {{
    display:inline-block; background: var(--ink); color:#fff;
    font-size: 14pt; font-weight: 800; letter-spacing: 3pt;
    padding: 3mm 7mm; border-radius: 50mm; margin-bottom: 8mm;
  }}
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

  /* 마지막 closing */
  .closing {{
    text-align:center; padding-top: 60mm; height: 240mm;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
  }}
  .closing .h0 {{ font-size: 16pt; color: var(--muted); letter-spacing: 4pt; font-weight: 700; }}
  .closing .h1 {{
    font-size: 60pt; font-weight: 900; color: var(--ink); margin: 6mm 0;
    letter-spacing: 2px;
  }}
  .closing .h1 .pop {{ color: var(--pop); }}
  .closing .h2 {{ font-size: 22pt; color: var(--pop); font-weight: 900; margin-top: 6mm; }}
  .closing .h3 {{ font-size: 13pt; color: var(--muted); margin-top: 12mm; letter-spacing:2pt; }}
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

<!-- 적중분석 표 -->
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
    <div class="chart-card">
      <h4>중단원 분포</h4>
      <div class="chart-wrap"><canvas id="chartChapter"></canvas></div>
    </div>
    <div class="chart-card">
      <h4>난이도 분포</h4>
      <div class="chart-wrap"><canvas id="chartDiff"></canvas></div>
    </div>
  </div>
</section>

<!-- 표 -->
<section class="page">
  <div class="sec-head">문항별 매칭 표</div>
  <table class="q">
    <thead><tr><th>번호</th><th>중단원</th><th>배점</th><th>난이도</th><th>교재 매칭</th><th>등급</th></tr></thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>
</section>

<!-- 시험대비 전략 + 코멘트 -->
<section class="page strategy-page">
  <div class="strat-block-head">시험대비 전략</div>
  {strategy_html}
  <div class="comment">
    <span class="hdr">{instructor} 코멘트</span>
    {instructor_comment}
  </div>
</section>

<!-- 핵심문제 매칭 -->
{key_pages}

<!-- 핵심노트 견본 -->
{note_html}

<!-- closing -->
<section class="page closing">
  <div class="h0">2026 학년도 기출 적중 분석</div>
  <div class="h1">압도적인 <span class="pop">적중</span></div>
  <div class="h2">{instructor}와 함께</div>
  <div class="h3">M A T H A R C H I V E &nbsp;·&nbsp; {academy}</div>
</section>

<script>
window.addEventListener('load', () => {{
  const data = {chart_json};
  const palette = ['#0f1419','#27406d','#3d5e9a','#ff3a3a','#ffc83d','#1f9d5f','#caff3d'];
  const diffColors = {{ '하':'#1f9d5f', '중':'#ffc83d', '상':'#ff3a3a' }};
  const opts = (kind) => {{
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
        animation: false, cutout: '52%',
        plugins: {{
          legend: {{
            position:'right',
            labels: {{
              font: {{ size: 12, weight: '700' }},
              padding: 8, boxWidth: 16, color: '#0f1419'
            }}
          }},
          tooltip: {{ enabled: false }}
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
            margin={"top": "14mm", "bottom": "12mm", "left": "14mm", "right": "14mm"},
        )
        browser.close()
    print(f"PDF : {out_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
