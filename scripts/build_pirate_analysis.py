#!/usr/bin/env python3
"""기출 적중분석 분석지 생성기 (광문고 26년 1-1 중간 파일럿).

데이터(시험지 문항·매칭 유형·강사 코멘트)는 모두 이 파일 안에 인라인.
HTML 생성 후 Playwright로 A4 PDF 출력.
"""
from __future__ import annotations

import base64
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "output" / "pirate_analysis" / "work"
OUT_DIR = ROOT / "output" / "pirate_analysis"


# ── 입력 데이터 ──────────────────────────────────────────────
SCHOOL = "광문고등학교"
EXAM_TITLE = "2026학년도 1학기 중간고사 기출분석"
SUBJECT = "공통수학1 — 다항식의 연산 ~ 이차함수"
INSTRUCTOR = "이영우T"

# 문항별 (번호, 중단원, 배점, 난이도, 매칭 유형 번호, 매칭 유형 제목, 등급)
QUESTIONS = [
    (1,  "다항식의 연산",       3.5, "하", 1,  "다항식의 연산 - 기본",                "A"),
    (2,  "이차함수",             3.5, "하", 49, "함수와 방정식의 관계 - 실근",         "A"),
    (3,  "항등식과 나머지정리", 3.7, "하", 14, "일차식으로 나눈 나머지",              "A"),
    (4,  "인수분해(곱셈공식)",   3.7, "하", 3,  "곱셈공식의 변형 – 항 두개",           "A"),
    (5,  "항등식과 나머지정리", 3.9, "하", 12, "항등식과 미정계수법 – 수치대입법",    "A"),
    (6,  "복소수",               3.9, "하", 29, "복소수 – 음수의 제곱근",              "A"),
    (7,  "이차방정식",           4.1, "하", 40, "이차방정식의 작성 (잘못 본 근)",      "A"),
    (8,  "이차함수",             4.3, "하", 53, "이차함수의 최대·최소 - 구간내",       "A"),
    (9,  "항등식과 나머지정리", 4.3, "하", 19, "나머지정리 – 인수정리",               "A"),
    (10, "복소수",               4.3, "하", 31, "복소수의 결정",                       "A"),
    (11, "인수분해",             4.5, "중", 23, "인수분해 – 스킬, 복이차식",           "A"),
    (12, "복소수",               4.7, "중", 32, "복소수 – 조건에 따른 복소수",         "A"),
    (13, "복소수",               4.9, "중", 35, "복소수 – 거듭제곱의 합",              "A"),
    (14, "이차함수",             5.1, "중", 54, "이차함수의 최대·최소 활용",           "A"),
    (15, "이차함수",             5.1, "중", 53, "이차함수의 최대·최소 - 구간내",       "A"),
    (16, "이차방정식",           5.3, "중", 45, "근과 계수의 관계, 대입 복합",         "A"),
    (17, "항등식과 나머지정리", 5.5, "상", 15, "이차·삼차식으로 나눈 나머지",         "A"),
    (18, "이차함수",             5.7, "중", 50, "함수와 직선의 위치관계 - 판별식",     "A"),
    (19, "이차방정식 [서답형]",  8.0, "중", 41, "근과 계수의 관계",                    "A"),
    (20, "항등식·나머지 [서답형]", 12.0, "상", 17, "합성함수/치환 (복잡한 다항식)",     "A"),
]

# 주요문제 5개 (시험지 LaTeX, 매칭 카드 종류·내용)
# kind: 'note' = 핵심노트 이미지, 'text' = 교재 유형 + 강사 멘트
KEY_PROBLEMS = [
    {
        "no": 16, "score": 5.3, "diff": "중", "topic": "이차방정식",
        "exam_latex": (
            r"$x$에 대한 이차방정식 $x^2-5x+k=0$의 두 근 $\alpha,\ \beta$에 대하여 "
            r"$$\dfrac{1}{\alpha^2-2\alpha+k}+\dfrac{1}{\beta^2-2\beta+k}=\dfrac{1}{6}$$ "
            r"을 만족시키는 실수 $k$의 값은?"
        ),
        "match_kind": "note", "note_image": "3.png",
        "match_type": "유형45 — 근과 계수의 관계, 대입 복합",
        "match_caption": (
            "두 근을 대입한 식의 값을 근과 계수의 관계로 정리하는 패턴. "
            "내가 만든 핵심노트의 ‘근의 대입’ 페이지에 동일한 풀이 절차가 정리되어 있다."
        ),
    },
    {
        "no": 17, "score": 5.5, "diff": "상", "topic": "항등식·나머지정리",
        "exam_latex": (
            r"다항식 $f(x)$를 $4x^2-2x+1$로 나누었을 때의 나머지는 $2x+3$이다. "
            r"$f(x)$를 $8x^3+1$로 나누었을 때의 나머지를 $4ax^2+bx-2$라 할 때, "
            r"$f(x)$를 $2x+1$로 나누었을 때의 나머지는?"
        ),
        "match_kind": "note", "note_image": "5.png",
        "match_type": "유형15 — 이차·삼차식으로 나눈 나머지",
        "match_caption": (
            "곱셈 공식 $8x^3+1=(2x+1)(4x^2-2x+1)$을 활용해 나머지를 분해하는 표준 풀이. "
            "핵심노트 ‘나머지 분해 / 합성 인수분해’ 페이지에 그대로 들어있다."
        ),
    },
    {
        "no": 18, "score": 5.7, "diff": "중", "topic": "이차함수",
        "exam_latex": (
            r"이차함수 $y=x^2-2ax+5a-b$의 그래프가 $x$축과 만나는 두 점 사이의 거리가 4가 되게 하는 "
            r"모든 $a$의 값의 곱이 $-2$이다. 이차함수 $y=x^2-2kx+k^2-2k+8b$가 실수 $k$의 값에 관계없이 "
            r"항상 직선 $y=mx+n$에 접할 때, $b^2+m^2+n^2$의 값은? (단, $a,\ b,\ m,\ n$은 실수)"
        ),
        "match_kind": "text",
        "match_type": "유형49·50 + 유형41 + 항등식 기본개념",
        "match_caption": (
            "이차함수와 x축과의 위치관계, 근과 계수의 관계, 그리고 항등식의 기본개념이 결합된 문제로 "
            "기본기가 탄탄해야 풀린다. ① 그래프와 x축이 만나는 두 점의 거리(판별식·근과 계수), "
            "② 매개변수 $k$에 관계없이 항상 접한다 → ‘$k$에 대한 항등식’으로 환원."
        ),
    },
    {
        "no": 19, "score": 8.0, "diff": "중", "topic": "이차방정식 (서답형)",
        "exam_latex": (
            r"$x$에 대한 이차방정식 $x^2+(a^2-2a-3)x-a+1=0$의 두 실근의 절댓값이 서로 같고 "
            r"부호는 다를 때, 실수 $a$의 값을 구하고 그 과정을 서술하시오."
        ),
        "match_kind": "note", "note_image": "6.png",
        "match_type": "유형41 — 근과 계수의 관계",
        "match_caption": (
            "두 근의 절댓값이 같고 부호가 다르다 → 두 근의 합 = 0, 두 근의 곱 < 0 으로 환원되는 "
            "전형적 패턴. 핵심노트 ‘근의 부호 / 절댓값’ 페이지에 같은 조건이 정리되어 있다."
        ),
    },
    {
        "no": 20, "score": 12.0, "diff": "상", "topic": "항등식·나머지정리 (서답형)",
        "exam_latex": (
            r"최고차항의 계수가 $1$인 이차다항식 $f(x)$와 두 다항식 $P(x),\ Q(x)$가 다음 조건을 만족."
            r"<br>(가) $P(x)+Q(x),\ P(x)-Q(x)$를 $(x+1)^2$로 나눈 몫은 모두 $f(x)$, 두 나머지의 합은 $4$."
            r"<br>(나) $f(x)=f(-x+1)$"
            r"<br>$P(0)=Q(0)=2$일 때, 방정식 $f(x)+Q(x)=-x$가 오직 하나의 해를 갖는다. "
            r"이때 $Q(\sqrt{2})$의 값을 구하시오. (단, $Q(\sqrt{2})>0$)"
        ),
        "match_kind": "text",
        "match_type": "유형17 — 합성함수/치환 + 유형27 모의고사 연계",
        "match_caption": (
            "20번은 어려워 보이지만 모의고사 기출 등 여러 기본문제들의 풀이가 결합된 문제로, "
            "필수문제들을 잘 풀 줄 알아야 해결할 수 있는 문제."
        ),
    },
]

INSTRUCTOR_COMMENT = (
    "16~19번은 익숙한 패턴의 평이한 문제들. 우리 교재의 핵심유형 카드와 핵심노트만 충실히 익혔다면 무리 없이 풀린다. "
    "20번은 외형이 어려워 보이지만, 실제로는 모의고사 기출 등 여러 기본 문제의 풀이가 결합된 문제이다. "
    "필수 유형들을 잘 풀 줄 알아야만 도달할 수 있는 문제이며, 결국 ‘기본기를 정확히 다루는 학생’이 가져가는 문제."
)

STRATEGY = [
    ("교과서 + 필수 유형 문제", "이 학교는 시험 범위에서 ‘기본 유형의 정확한 풀이 능력’이 가장 큰 변수. 교과서 예제·익힘과 우리 교재 STEP1·STEP2 핵심 유형부터 흔들림 없이 잡는다."),
    ("변별력 문제 = 모의고사 기출",  "20번처럼 결합형 문제는 모의고사 기출에서 답이 나온다. 평가원·교육청 기출 변형을 주 1회 이상 풀어 ‘유형의 결합’ 자체에 익숙해질 것."),
    ("핵심노트 회독", "단순 풀이가 아닌 ‘풀이 절차의 핵심 한 줄’만 정리한 핵심노트를 시험 1주 전부터 빠르게 3회독. 이번 시험 16·17·19번이 모두 노트에 그대로 정리되어 있던 패턴."),
]


def img_to_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    ext = path.suffix.lstrip(".").lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def html_doc() -> str:
    instructor_uri = img_to_data_uri(WORK / "instructor.png")
    note_cover_uri = img_to_data_uri(WORK / "4.png")

    rows = []
    for n, topic, score, diff, ytype, ytitle, grade in QUESTIONS:
        rows.append(
            f"<tr><td class='c'>{n}</td><td>{topic}</td><td class='c'>{score}</td>"
            f"<td class='c diff-{diff}'>{diff}</td><td class='match'>유형{ytype} — {ytitle}</td>"
            f"<td class='c grade-{grade}'>{grade}</td></tr>"
        )
    table_rows = "\n".join(rows)
    total_score = sum(q[2] for q in QUESTIONS)
    hit_count = sum(1 for q in QUESTIONS if q[6] in ("A", "B"))

    key_pages = []
    for kp in KEY_PROBLEMS:
        if kp["match_kind"] == "note":
            note_uri = img_to_data_uri(WORK / kp["note_image"])
            right = (
                f"<div class='note-card'>"
                f"<div class='note-head'>핵심노트 매칭</div>"
                f"<img src='{note_uri}' class='note-img'/>"
                f"<div class='match-type'>{kp['match_type']}</div>"
                f"<div class='match-cap'>{kp['match_caption']}</div>"
                f"</div>"
            )
        else:
            right = (
                f"<div class='note-card text-card'>"
                f"<div class='note-head'>교재 매칭 / 강사 코멘트</div>"
                f"<div class='match-type'>{kp['match_type']}</div>"
                f"<div class='match-cap'>{kp['match_caption']}</div>"
                f"</div>"
            )
        key_pages.append(f"""
<section class="page key-page">
  <div class="key-head">
    <div class="key-no">시험지 {kp['no']}번</div>
    <div class="key-meta">{kp['topic']} · 배점 {kp['score']} · 난이도 {kp['diff']}</div>
  </div>
  <div class="key-body">
    <div class="exam-card">
      <div class="exam-head">시험 출제 문항</div>
      <div class="exam-latex">{kp['exam_latex']}</div>
    </div>
    {right}
  </div>
</section>
""")

    strategy_html = "\n".join(
        f"<div class='strat-row'><div class='strat-key'>{k}</div><div class='strat-val'>{v}</div></div>"
        for k, v in STRATEGY
    )

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>{SCHOOL} {EXAM_TITLE}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{{delimiters:[
    {{left:'$$',right:'$$',display:true}},
    {{left:'$',right:'$',display:false}}
  ]}});"></script>
<style>
  @page {{ size: A4; margin: 14mm 14mm 12mm 14mm; }}
  html, body {{ margin:0; padding:0; }}
  body {{ font-family: "AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif;
         color:#1d2433; font-size:10.4pt; line-height:1.55; }}
  .page {{ page-break-after: always; padding: 0; }}
  .page:last-child {{ page-break-after: auto; }}

  /* ── 표지 ── */
  .cover {{ height: 265mm; display:flex; flex-direction:column; justify-content:space-between;
            align-items:center; text-align:center; padding-top: 6mm; }}
  .cover .school {{ font-size: 18pt; color:#3a4760; letter-spacing:1px; }}
  .cover .title {{ font-size: 32pt; font-weight: 800; margin-top: 6mm; color:#0f1d3a;
                   border-top: 3px solid #0f1d3a; border-bottom: 3px solid #0f1d3a; padding: 8mm 0; }}
  .cover .subject {{ font-size: 14pt; color:#56607a; margin-top: 5mm; }}
  .cover .photo-wrap {{ flex:1; display:flex; align-items:center; justify-content:center; }}
  .cover .photo {{ width: 78mm; height: 78mm; border-radius: 50%; object-fit: cover;
                   object-position: 50% 6%;
                   box-shadow: 0 4mm 8mm rgba(15,29,58,0.18); border: 4px solid #fff;
                   outline: 2px solid #0f1d3a; }}
  .cover .name {{ font-size: 26pt; font-weight: 800; color:#0f1d3a; margin-top: 6mm; }}
  .cover .tag  {{ font-size: 11pt; color:#56607a; letter-spacing: 2px; }}

  /* ── 분석 페이지 ── */
  .sec-head {{ font-size: 16pt; font-weight: 800; color:#0f1d3a;
               border-left: 6px solid #d44a4a; padding-left: 10px; margin: 0 0 6mm 0; }}
  .hit-banner {{ background: linear-gradient(90deg,#0f1d3a 0%,#27406d 100%); color:#fff;
                 border-radius: 6px; padding: 4mm 7mm; display:flex; justify-content: space-between;
                 align-items:center; margin-bottom: 4mm; }}
  .hit-banner .big {{ font-size: 24pt; font-weight: 800; letter-spacing: 1px; }}
  .hit-banner .sub {{ font-size: 9.4pt; opacity: 0.85; max-width: 95mm; line-height:1.4; }}
  table.q {{ width:100%; border-collapse: collapse; font-size: 8.6pt; }}
  table.q th {{ background:#0f1d3a; color:#fff; padding: 3px 5px; font-weight:600; font-size: 9pt; }}
  table.q td {{ padding: 2.6px 5px; border-bottom:1px solid #e3e7ee; }}
  table.q td.c {{ text-align:center; }}
  table.q td.match {{ color:#28406d; font-weight:600; }}
  .diff-하 {{ color:#2a9d4a; font-weight:700; }}
  .diff-중 {{ color:#c98a16; font-weight:700; }}
  .diff-상 {{ color:#c0392b; font-weight:700; }}
  .grade-A {{ color:#1f7a3a; font-weight:800; }}
  .grade-B {{ color:#b87a18; font-weight:700; }}

  .panel {{ border:1px solid #d6dbe4; border-radius:6px; padding: 4mm 5mm;
            margin-top: 4mm; background:#fafbfd; }}
  .panel h3 {{ margin: 0 0 2.5mm 0; font-size: 11pt; color:#0f1d3a; }}
  .strat-row {{ display:flex; gap: 4mm; margin-bottom: 2mm; font-size: 9.4pt; }}
  .strat-key {{ flex: 0 0 36mm; font-weight:700; color:#0f1d3a; }}
  .strat-val {{ flex: 1; color:#3a4760; line-height: 1.45; }}

  .comment {{ border-left: 5px solid #d44a4a; background:#fff5f4; padding: 3mm 5mm;
              border-radius: 0 5px 5px 0; margin-top: 4mm; color:#56293a; line-height: 1.5;
              font-size: 9.6pt; }}

  /* ── 주요문제 1:1 매칭 페이지 ── */
  .key-page {{ }}
  .key-head {{ display:flex; justify-content: space-between; align-items: baseline;
               border-bottom: 3px solid #0f1d3a; padding-bottom: 3mm; margin-bottom: 6mm; }}
  .key-no   {{ font-size: 18pt; font-weight: 800; color:#0f1d3a; }}
  .key-meta {{ color:#56607a; }}
  .key-body {{ display:grid; grid-template-columns: 1fr 1fr; gap: 6mm; }}
  .exam-card, .note-card {{ border:1px solid #d6dbe4; border-radius:6px; padding: 5mm 5mm; background:#fff; }}
  .exam-head, .note-head {{ font-size: 11pt; color:#fff; background:#0f1d3a;
                            display:inline-block; padding: 1mm 3mm; border-radius: 3px;
                            margin-bottom: 3mm; font-weight: 600; }}
  .note-head {{ background:#d44a4a; }}
  .exam-latex {{ font-size: 10.6pt; line-height: 1.7; }}
  .note-img {{ width: 100%; border:1px solid #ccd2dd; border-radius: 4px;
               max-height: 130mm; object-fit: contain; }}
  .match-type {{ margin-top: 4mm; font-weight: 800; color:#28406d; }}
  .match-cap  {{ margin-top: 2mm; color:#3a4760; line-height: 1.55; font-size: 9.8pt; }}
  .text-card .match-cap {{ margin-top: 4mm; font-size: 10.4pt; }}

  /* ── 마지막 페이지 (핵심노트 안내 / CTA) ── */
  .closing {{ text-align:center; padding-top: 30mm; }}
  .closing img {{ max-width: 130mm; box-shadow: 0 6px 12px rgba(15,29,58,0.2); }}
  .closing h2 {{ margin-top: 10mm; color:#0f1d3a; font-size: 22pt; }}
  .closing p {{ color:#56607a; margin-top: 5mm; font-size: 12pt; }}
</style>
</head>
<body>

<!-- 표지 -->
<section class="page cover">
  <div>
    <div class="school">{SCHOOL}</div>
    <div class="title">{EXAM_TITLE}</div>
    <div class="subject">{SUBJECT}</div>
  </div>
  <div class="photo-wrap">
    <img class="photo" src="{instructor_uri}"/>
  </div>
  <div>
    <div class="name">{INSTRUCTOR}</div>
    <div class="tag">M A T H A R C H I V E &nbsp;·&nbsp; 기 출 적 중 분 석</div>
  </div>
</section>

<!-- 분석 페이지 -->
<section class="page">
  <div class="sec-head">시험 적중 분석</div>
  <div class="hit-banner">
    <div>
      <div class="big">적중 {hit_count}/{len(QUESTIONS)} · 100%</div>
      <div class="sub">우리 교재가 다룬 유형이 그대로 출제. 등급 A는 동형(거의 동일 풀이 절차) 매칭, 총 배점 {total_score:.1f}점 모두 커버.</div>
    </div>
  </div>
  <table class="q">
    <thead><tr><th>번호</th><th>중단원</th><th>배점</th><th>난이도</th><th>교재 매칭</th><th>등급</th></tr></thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>

  <div class="panel">
    <h3>앞으로의 시험대비 전략</h3>
    {strategy_html}
  </div>

  <div class="comment">
    <strong>강사 코멘트.</strong> {INSTRUCTOR_COMMENT}
  </div>
</section>

<!-- 주요문제 1:1 매칭 -->
{''.join(key_pages)}

<!-- 마지막: 핵심노트 안내 -->
<section class="page closing">
  <h2>모든 핵심 패턴이 이 한 권에.</h2>
  <p>이번 시험 16·17·19번은 모두 ‘이영우T 핵심노트’에 동일 패턴이 정리되어 있었습니다.</p>
  <img src="{note_cover_uri}" alt="핵심노트 표지"/>
</section>

</body>
</html>
"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html = html_doc()
    html_path = OUT_DIR / "광문고_2026_1-1중간_적중분석.html"
    pdf_path  = OUT_DIR / "광문고_2026_1-1중간_적중분석.pdf"
    html_path.write_text(html, encoding="utf-8")
    print(f"HTML: {html_path}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(html_path.as_uri(), wait_until="networkidle")
        # KaTeX render needs a tick after networkidle
        page.wait_for_timeout(400)
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "14mm", "bottom": "12mm", "left": "14mm", "right": "14mm"},
        )
        browser.close()
    print(f"PDF : {pdf_path}")


if __name__ == "__main__":
    main()
