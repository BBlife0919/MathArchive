#!/usr/bin/env python3
"""학생용 노트 양식 3종 PDF 생성.

산출물 (모두 A4, output/student_templates/):
  1. 풀이노트_양식.pdf       — 매일 문제 풀이 기록용 (1장에 3블록)
  2. 오답노트_양식.pdf       — 틀린 문제 + [원인] 5종 분류 (1장에 2블록)
  3. 교재표시_규칙.pdf       — 책상 옆 부착용 마킹 규칙표 (1장)

실행:
    python scripts/build_student_templates.py
의존: playwright (chromium)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "student_templates"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_STACK = (
    '"AppleSDGothicNeo-Bold","AppleSDGothicNeo-Regular",'
    '"Apple SD Gothic Neo","Nanum Gothic",sans-serif'
)


def _common_css() -> str:
    return f"""
    @page {{ size: A4; margin: 14mm 14mm 14mm 14mm; }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: {FONT_STACK};
      color: #111;
      margin: 0;
      font-size: 11pt;
      line-height: 1.45;
    }}
    .title {{
      font-size: 18pt;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin: 0 0 4px 0;
    }}
    .subtitle {{
      font-size: 10pt;
      color: #555;
      margin: 0 0 14px 0;
    }}
    .footer {{
      position: fixed;
      bottom: 6mm;
      left: 14mm;
      right: 14mm;
      font-size: 8pt;
      color: #999;
      text-align: right;
    }}
    """


def _html_solution_notebook() -> str:
    block = """
    <div class="sblock">
      <div class="row meta">
        <div class="cell"><span class="lbl">교재/페이지</span><span class="line"></span></div>
        <div class="cell narrow"><span class="lbl">문제번호</span><span class="line"></span></div>
      </div>
      <div class="work">
        <div class="work-label">풀이 (식 전개)</div>
        <div class="grid"></div>
      </div>
      <div class="answer">
        <span class="lbl">답</span><span class="line wide"></span>
      </div>
    </div>
    """
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
    {_common_css()}
    .date-bar {{
      display: flex; align-items: baseline; gap: 8px;
      margin: 4px 0 10px 0;
      padding: 6px 10px;
      border-bottom: 1.5px solid #222;
    }}
    .date-bar .lbl {{ font-weight: 800; font-size: 12pt; color: #111; }}
    .date-bar .line {{ flex: 1; border-bottom: 1.2px solid #444; height: 18px; }}
    .grid-2x2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 8px;
      height: calc(100vh - 92mm);
    }}
    .sblock {{
      border: 1.2px solid #222;
      border-radius: 6px;
      padding: 8px 10px 10px 10px;
      display: flex; flex-direction: column;
      page-break-inside: avoid;
    }}
    .row.meta {{ display: flex; gap: 8px; margin-bottom: 6px; }}
    .cell {{ display: flex; align-items: baseline; gap: 5px; flex: 1; }}
    .cell.narrow {{ flex: 0 0 38%; }}
    .lbl {{ font-weight: 700; font-size: 9pt; color: #333; white-space: nowrap; }}
    .line {{ flex: 1; border-bottom: 1px solid #555; height: 13px; }}
    .line.wide {{ min-width: 80%; }}
    .work {{ flex: 1; display: flex; flex-direction: column; }}
    .work-label {{
      font-size: 9pt; color: #444; font-weight: 700; margin-bottom: 3px;
    }}
    .grid {{
      flex: 1;
      background-image: linear-gradient(#e5e5e5 1px, transparent 1px);
      background-size: 100% 20px;
      border: 1px dashed #bbb;
      border-radius: 4px;
      min-height: 130px;
    }}
    .answer {{ margin-top: 6px; display: flex; align-items: baseline; gap: 6px; }}
    .rules {{
      margin: 0 0 8px 0;
      padding: 7px 10px;
      background: #f5f7ff;
      border-left: 3px solid #4F46E5;
      font-size: 9pt;
      color: #333;
      line-height: 1.5;
    }}
    .rules b {{ color: #4F46E5; }}
    </style></head><body>
      <div class="title">풀이노트 양식</div>
      <div class="subtitle">매일 — 모든 풀이는 이 형식으로. 답만 적지 말 것.</div>
      <div class="rules">
        <b>규칙</b> ① 식 전개를 한 줄씩 옮겨 적는다 &nbsp; ② 답은 ‘답:’ 옆에 명확히 쓴다
        &nbsp; ③ 헷갈린 부분은 ★ 표시 후 오답노트로 옮긴다
      </div>
      <div class="date-bar">
        <span class="lbl">날짜</span><span class="line"></span>
      </div>
      <div class="grid-2x2">
        {block * 4}
      </div>
      <div class="footer">MathDB · Student Template · 풀이노트 v1</div>
    </body></html>"""


def _html_wrong_notebook() -> str:
    block = """
    <div class="wblock">
      <div class="row meta">
        <div class="cell"><span class="lbl">교재/페이지</span><span class="line"></span></div>
        <div class="cell narrow"><span class="lbl">문제번호</span><span class="line"></span></div>
      </div>

      <div class="cause">
        <div class="cause-title">① 원인 (하나만 체크)</div>
        <div class="cause-row">
          <label>☐ <b>개념</b></label>
          <label>☐ <b>조건</b></label>
          <label>☐ <b>전략</b></label>
          <label>☐ <b>계산</b></label>
          <label>☐ <b>시간</b></label>
        </div>
      </div>

      <div class="resolve">
        <div class="resolve-title">② 다시 푼 풀이</div>
        <div class="grid"></div>
      </div>

      <div class="prevent">
        <span class="lbl">③ 재발방지</span>
        <span class="line wide"></span>
      </div>
    </div>
    """
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
    {_common_css()}
    .date-bar {{
      display: flex; align-items: baseline; gap: 8px;
      margin: 4px 0 8px 0;
      padding: 6px 10px;
      border-bottom: 1.5px solid #b91c1c;
    }}
    .date-bar .lbl {{ font-weight: 800; font-size: 12pt; color: #b91c1c; }}
    .date-bar .line {{ flex: 1; border-bottom: 1.2px solid #555; height: 18px; }}
    .grid-2x2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 8px;
      height: calc(100vh - 100mm);
    }}
    .wblock {{
      border: 1.4px solid #b91c1c;
      border-radius: 6px;
      padding: 7px 9px 8px 9px;
      display: flex; flex-direction: column;
      page-break-inside: avoid;
    }}
    .row.meta {{ display: flex; gap: 6px; margin-bottom: 5px; }}
    .cell {{ display: flex; align-items: baseline; gap: 4px; flex: 1; }}
    .cell.narrow {{ flex: 0 0 38%; }}
    .lbl {{ font-weight: 700; font-size: 8.5pt; color: #333; white-space: nowrap; }}
    .line {{ flex: 1; border-bottom: 1px solid #555; height: 12px; }}
    .line.wide {{ min-width: 70%; }}

    .cause {{
      background: #fff7ed;
      border: 1px solid #fdba74;
      border-radius: 4px;
      padding: 4px 7px 5px 7px;
      margin-bottom: 5px;
    }}
    .cause-title {{ font-weight: 700; color: #9a3412; font-size: 8.5pt; margin-bottom: 2px; }}
    .cause-row {{
      display: flex; flex-wrap: wrap;
      gap: 2px 8px;
      font-size: 9pt;
    }}
    .cause-row label {{ white-space: nowrap; }}
    .cause-row b {{ color: #9a3412; }}

    .resolve {{ flex: 1; display: flex; flex-direction: column; }}
    .resolve-title {{
      font-weight: 700; font-size: 8.5pt; color: #1e3a8a; margin: 0 0 2px 0;
    }}
    .grid {{
      flex: 1;
      background-image: linear-gradient(#e5e5e5 1px, transparent 1px);
      background-size: 100% 18px;
      border: 1px dashed #bbb;
      border-radius: 3px;
      min-height: 80px;
      margin-bottom: 4px;
    }}
    .prevent {{ display: flex; align-items: baseline; gap: 6px; }}

    .rules {{
      margin: 0 0 6px 0;
      padding: 7px 10px;
      background: #fef2f2;
      border-left: 3px solid #b91c1c;
      font-size: 9pt;
      color: #333;
      line-height: 1.5;
    }}
    .rules b {{ color: #b91c1c; }}
    </style></head><body>
      <div class="title" style="color:#b91c1c">오답노트 양식</div>
      <div class="subtitle">틀린 즉시 작성 — <b>원인을 모르고 다시 풀면 같은 실수가 반복</b>된다.</div>
      <div class="rules">
        <b>꼭 채울 것</b> ① 원인 5종(개념/조건/전략/계산/시간) 중 하나 체크 &nbsp;
        ② 다시 푼 풀이 &nbsp; ③ 재발방지 한 줄 — 셋 중 하나라도 비면 강사 인정 안 함.
      </div>
      <div class="date-bar">
        <span class="lbl">날짜</span><span class="line"></span>
      </div>
      <div class="grid-2x2">
        {block * 4}
      </div>
      <div class="footer">MathDB · Student Template · 오답노트 v1</div>
    </body></html>"""


def _html_marking_card() -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
    {_common_css()}
    .title {{ color: #047857; }}
    .card {{
      border: 1.4px solid #047857;
      border-radius: 8px;
      padding: 18px 22px;
      margin-top: 10px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 70px 1fr;
      row-gap: 14px;
      column-gap: 18px;
      align-items: start;
    }}
    .mark {{
      font-size: 26pt;
      font-weight: 800;
      text-align: center;
      line-height: 1;
      color: #047857;
    }}
    .mark.gray {{ color: #555; }}
    .desc {{
      font-size: 11.5pt;
    }}
    .desc b {{ display: block; margin-bottom: 2px; }}
    .desc small {{ color: #666; font-size: 9.5pt; }}
    .why {{
      margin-top: 18px;
      padding: 12px 14px;
      background: #ecfdf5;
      border-left: 3px solid #047857;
      font-size: 10.5pt;
      line-height: 1.55;
    }}
    .why b {{ color: #047857; }}
    .strip {{
      margin-top: 16px;
      padding: 8px 12px;
      border: 1px dashed #047857;
      border-radius: 5px;
      font-size: 10pt;
      color: #047857;
      text-align: center;
    }}
    </style></head><body>
      <div class="title">교재표시 규칙</div>
      <div class="subtitle">책상 옆에 붙여두고 매일 같은 기호로 표시 — 공부 흔적이 곧 시험 직전 복습 자산.</div>

      <div class="card">
        <div class="grid">
          <div class="mark">★</div>
          <div class="desc"><b>모르는 문제 — 반드시 다시 풀어야 함</b>
            <small>처음 풀이에서 답이 안 나왔거나, 풀이를 추측한 경우</small></div>

          <div class="mark">△</div>
          <div class="desc"><b>헷갈렸지만 맞춘 문제</b>
            <small>찍어서 맞췄거나, 풀이 중간에 망설였던 문제</small></div>

          <div class="mark" style="color:#f59e0b">형광</div>
          <div class="desc"><b>시험 직전 다시 볼 부분</b>
            <small>개념 정리·공식 박스·핵심 문장 — 노란 형광펜만 사용</small></div>

          <div class="mark gray">✓</div>
          <div class="desc"><b>두 번 풀어서 확실해진 문제</b>
            <small>★ 표시 후 다시 풀어서 맞춘 경우만 — 처음부터 ✓ 금지</small></div>

          <div class="mark gray">↺</div>
          <div class="desc"><b>오답노트로 옮긴 문제</b>
            <small>★ 중에서 따로 정리한 문제 — 오답노트 페이지 번호 옆에 적기</small></div>
        </div>

        <div class="why">
          <b>왜 표시해야 하는가?</b><br>
          시험 1주 전에 <b>모든 ★ 문제만</b> 다시 풀고, <b>형광 부분만</b> 다시 읽는다.
          그게 가능하려면 평소에 표시가 쌓여있어야 한다. 깨끗한 교재 = 공부하지 않은 교재.
        </div>

        <div class="strip">규칙은 단순할수록 지켜진다 — 위 5종 외에 새 기호 만들지 말 것.</div>
      </div>
      <div class="footer">MathDB · Student Template · 교재표시 규칙 v1</div>
    </body></html>"""


def _render(html: str, out_path: Path) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(
            path=str(out_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()


def main() -> None:
    targets = [
        ("풀이노트_양식.pdf",   _html_solution_notebook()),
        ("오답노트_양식.pdf",   _html_wrong_notebook()),
        ("교재표시_규칙.pdf",   _html_marking_card()),
    ]
    for name, html in targets:
        out = OUT_DIR / name
        _render(html, out)
        size_kb = out.stat().st_size // 1024
        print(f"[OK] {name}  ({size_kb} KB)  → {out}")
    print(f"\n총 {len(targets)}개 양식 생성 완료.")


if __name__ == "__main__":
    main()
