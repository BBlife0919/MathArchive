#!/usr/bin/env python3
"""학생카드 PDF 한 장 생성 — 학부모 보고용 맛보기.

데이터 출처: students / clinic_entries / student_progress / student_assessment / student_log
출력: A4 1페이지, 학원 브랜드 + PRISM 막대 차트 + 정량/정성/자가예측/로그 표

실행:
    python scripts/render_student_card_pdf.py
    python scripts/render_student_card_pdf.py --student-name "맛보기학생" --out /tmp/card.pdf

의존: playwright (HTML→PDF), matplotlib (차트)
"""
import argparse
import base64
import io
import os
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from db import get_connection, is_cloud  # noqa: E402

PRISM_LETTER = {
    "계산실수": "P", "조건해석실패": "R", "개념누락": "I",
    "전략선택실패": "S", "시간관리": "M",
}
PRISM_ORDER = ["계산실수", "조건해석실패", "개념누락", "전략선택실패", "시간관리"]
RIS_CODES = {"개념누락", "조건해석실패", "전략선택실패"}   # 이해
PM_CODES  = {"계산실수", "시간관리"}                       # 수행


def _load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def _q(conn, sql: str, params=()):
    cur = conn.execute(sql, params)
    return cur.fetchall()


def _fetch_student_data(conn, name: str) -> dict:
    rows = _q(conn,
        "SELECT student_id, name, school, grade, class_name, note "
        "FROM students WHERE name = ? LIMIT 1",
        (name,))
    if not rows:
        return {}
    s = rows[0]
    sid = s["student_id"]

    today = date.today()
    cutoff_4w = (today - timedelta(weeks=4)).isoformat()

    clinic = _q(conn,
        "SELECT error_code, wrong_date FROM clinic_entries "
        "WHERE student_id = ? AND wrong_date >= ?",
        (sid, cutoff_4w))

    assess_q = _q(conn,
        "SELECT quantity_grade FROM student_assessment "
        "WHERE student_id = ? AND eval_type='quantity' AND eval_date >= ?",
        (sid, cutoff_4w))

    assess_l_rows = _q(conn,
        "SELECT eval_date, note_completion, written_completion, "
        "       textbook_marking, second_solve_reason, note "
        "FROM student_assessment "
        "WHERE student_id = ? AND eval_type='qualitative' "
        "ORDER BY eval_date DESC LIMIT 1",
        (sid,))

    preds = _q(conn,
        "SELECT log_date, title, self_predicted, self_actual, note "
        "FROM student_progress "
        "WHERE student_id = ? AND category='자가예측' "
        "ORDER BY log_date DESC LIMIT 3",
        (sid,))

    logs = _q(conn,
        "SELECT log_date, log_type, summary FROM student_log "
        "WHERE student_id = ? "
        "ORDER BY log_date DESC LIMIT 5",
        (sid,))

    return {
        "student":   dict(s),
        "clinic":    [dict(r) for r in clinic],
        "assess_q":  [dict(r) for r in assess_q],
        "assess_l":  dict(assess_l_rows[0]) if assess_l_rows else None,
        "preds":     [dict(r) for r in preds],
        "logs":      [dict(r) for r in logs],
    }


def _render_prism_chart_b64(clinic_rows: list) -> str:
    """matplotlib 으로 PRISM 5스펙트럼 분포 막대 → base64 PNG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    # macOS 한글 폰트
    for f in ("AppleSDGothicNeo.ttc", "AppleGothic.ttf", "AppleSDGothicNeo-Regular.otf"):
        for p in ("/System/Library/Fonts/", "/Library/Fonts/"):
            full = Path(p) / f
            if full.exists():
                font_manager.fontManager.addfont(str(full))
                plt.rcParams["font.family"] = font_manager.FontProperties(fname=str(full)).get_name()
                break

    counter = Counter(r["error_code"] for r in clinic_rows)
    labels = [f"{PRISM_LETTER[c]}\n{c}" for c in PRISM_ORDER]
    values = [counter.get(c, 0) for c in PRISM_ORDER]
    # PRISM 순서대로: P=빨강(수행), R=인디고(이해), I=인디고, S=인디고, M=빨강
    colors = ["#F97316", "#4F46E5", "#6366F1", "#8B5CF6", "#EF4444"]

    fig, ax = plt.subplots(figsize=(8, 3.2), dpi=140)
    bars = ax.bar(labels, values, color=colors, width=0.55)
    ax.set_ylabel("건수", fontsize=10)
    ax.set_title("PRISM — 최근 4주 오답 5스펙트럼 분광", fontsize=12, pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    for b, v in zip(bars, values):
        if v > 0:
            ax.text(b.get_x() + b.get_width()/2, v + 0.1, str(v),
                    ha="center", fontsize=9, fontweight="bold")

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _build_html(data: dict, chart_b64: str) -> str:
    s = data["student"]
    today_str = date.today().isoformat()
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()

    # PRISM 이해(RIS) / 수행(PM) 합계
    counter = Counter(r["error_code"] for r in data["clinic"])
    ris_total = sum(counter[c] for c in RIS_CODES)
    pm_total  = sum(counter[c] for c in PM_CODES)
    total = ris_total + pm_total
    ris_pct = f"{ris_total/total*100:.0f}%" if total else "—"
    pm_pct  = f"{pm_total/total*100:.0f}%"  if total else "—"

    # 정량 분포
    grade_counter = Counter(r["quantity_grade"] for r in data["assess_q"]
                            if r["quantity_grade"])
    quant_total = sum(grade_counter.values())
    grade_pct = lambda g: f"{grade_counter.get(g,0)}건 ({grade_counter.get(g,0)/quant_total*100:.0f}%)" if quant_total else "—"

    # 정성
    qual = data["assess_l"]
    qual_html = ""
    if qual:
        qual_html = (
            f"<table class='qual'><thead><tr>"
            f"<th>풀이노트</th><th>서술형</th><th>교재 표시</th><th>2차 풀이 이유</th></tr></thead>"
            f"<tbody><tr><td>{qual['note_completion']}/5</td>"
            f"<td>{qual['written_completion']}/5</td>"
            f"<td>{qual['textbook_marking']}/5</td>"
            f"<td>{qual['second_solve_reason']}/5</td></tr></tbody></table>"
            f"<div class='qual-date'>평가일: {qual['eval_date']}</div>"
        )
    else:
        qual_html = "<div class='muted'>정성 평가 기록 없음</div>"

    # 자가예측
    pred_rows = ""
    for p in data["preds"]:
        gap = (p["self_actual"] or 0) - (p["self_predicted"] or 0)
        sign = "+" if gap >= 0 else ""
        gap_cls = "gap-over" if gap < 0 else ("gap-under" if gap > 0 else "gap-match")
        pred_rows += (
            f"<tr><td>{p['log_date']}</td>"
            f"<td>{p['title'] or '-'}</td>"
            f"<td>{p['self_predicted']}</td>"
            f"<td>{p['self_actual']}</td>"
            f"<td class='{gap_cls}'>{sign}{gap}</td></tr>"
        )
    if not pred_rows:
        pred_rows = "<tr><td colspan='5' class='muted'>자가예측 기록 없음</td></tr>"

    # 로그
    log_rows = ""
    for l in data["logs"]:
        log_rows += (
            f"<tr><td>{l['log_date']}</td>"
            f"<td>{l['log_type']}</td>"
            f"<td>{l['summary'] or ''}</td></tr>"
        )
    if not log_rows:
        log_rows = "<tr><td colspan='3' class='muted'>관리 로그 없음</td></tr>"

    css = """
    @page { size: A4; margin: 16mm 14mm; }
    * { box-sizing: border-box; }
    body { font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
           color: #1F2937; font-size: 10pt; margin: 0; }
    .head { display: flex; justify-content: space-between; align-items: baseline;
            border-bottom: 2px solid #1F2937; padding-bottom: 6px; margin-bottom: 14px; }
    .brand { font-size: 18pt; font-weight: 800; letter-spacing: -0.4px; }
    .brand-sub { color: #6B7280; font-size: 9pt; }
    .meta { color: #6B7280; font-size: 9pt; }
    h2 { font-size: 11pt; margin: 14px 0 6px; padding-bottom: 3px;
         border-bottom: 1px solid #E5E7EB; }
    .student-card { background: #F9FAFB; border-radius: 6px; padding: 10px 14px;
                    display: flex; gap: 18px; flex-wrap: wrap; }
    .student-card div { font-size: 10pt; }
    .student-card strong { color: #4F46E5; margin-right: 4px; }
    .qm-summary { display: flex; gap: 12px; margin: 6px 0 8px; }
    .qm-summary .card { flex: 1; padding: 8px 12px; border-radius: 6px;
                        background: #EEF2FF; }
    .qm-summary .card.m { background: #FEF3C7; }
    .qm-summary .card .label { font-size: 8.5pt; color: #6B7280; }
    .qm-summary .card .val { font-size: 14pt; font-weight: 700; margin-top: 2px; }
    .qm-summary .card .pct { font-size: 9pt; color: #6B7280; }
    .chart img { width: 100%; max-height: 200px; object-fit: contain; }
    table { width: 100%; border-collapse: collapse; margin-top: 4px; }
    th, td { border: 1px solid #E5E7EB; padding: 5px 8px; font-size: 9.5pt; text-align: center; }
    th { background: #F3F4F6; font-weight: 600; }
    td.gap-over  { color: #DC2626; font-weight: 700; }
    td.gap-under { color: #16A34A; font-weight: 700; }
    td.gap-match { color: #6B7280; }
    .qual-date { font-size: 8.5pt; color: #6B7280; margin-top: 4px; }
    .quant-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
    .quant-grid .g { background: #F9FAFB; padding: 6px 8px; border-radius: 4px; text-align: center; }
    .quant-grid .g .lbl { font-size: 8.5pt; color: #6B7280; }
    .quant-grid .g .val { font-size: 11pt; font-weight: 600; margin-top: 2px; }
    .muted { color: #9CA3AF; font-size: 9pt; }
    .footer { margin-top: 14px; padding-top: 8px; border-top: 1px solid #E5E7EB;
              font-size: 8.5pt; color: #9CA3AF; text-align: center; }
    .comment-box { border: 1px dashed #9CA3AF; border-radius: 4px; padding: 10px;
                   min-height: 40px; color: #9CA3AF; font-size: 9pt; }
    """

    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><style>{css}</style></head>
<body>
  <div class="head">
    <div>
      <div class="brand">📐 MathArchive</div>
      <div class="brand-sub">학부모 주간 학습 보고서</div>
    </div>
    <div class="meta">발행 {today_str} · 주간 {week_start} ~</div>
  </div>

  <div class="student-card">
    <div><strong>이름</strong>{s['name']}</div>
    <div><strong>학교</strong>{s.get('school') or '-'}</div>
    <div><strong>학년/반</strong>{s.get('grade') or '-'}-{s.get('class_name') or '-'}</div>
  </div>

  <h2>PRISM · 최근 4주 오답 5스펙트럼 분광</h2>
  <div class="qm-summary">
    <div class="card"><div class="label">이해 RIS (Reading·Insight·Strategy)</div>
      <div class="val">{ris_total}건</div><div class="pct">{ris_pct}</div></div>
    <div class="card m"><div class="label">수행 PM (Precision·Management)</div>
      <div class="val">{pm_total}건</div><div class="pct">{pm_pct}</div></div>
  </div>
  <div class="chart"><img src="data:image/png;base64,{chart_b64}" alt="PRISM chart"/></div>

  <h2>과제 정밀평가</h2>
  <div class="quant-grid">
    <div class="g"><div class="lbl">A 등급</div><div class="val">{grade_pct('A')}</div></div>
    <div class="g"><div class="lbl">B 등급</div><div class="val">{grade_pct('B')}</div></div>
    <div class="g"><div class="lbl">C 등급</div><div class="val">{grade_pct('C')}</div></div>
    <div class="g"><div class="lbl">D 등급</div><div class="val">{grade_pct('D')}</div></div>
  </div>
  {qual_html}

  <h2>자가예측 격차 · 메타인지 추적</h2>
  <table><thead><tr>
    <th>날짜</th><th>시험</th><th>예측</th><th>실제</th><th>격차</th>
  </tr></thead><tbody>{pred_rows}</tbody></table>

  <h2>최근 관리 로그</h2>
  <table><thead><tr>
    <th>날짜</th><th>유형</th><th>요약</th>
  </tr></thead><tbody>{log_rows}</tbody></table>

  <h2>담당 강사 코멘트</h2>
  <div class="comment-box">(여기에 한 줄 추가 후 학부모께 발송)</div>

  <div class="footer">
    © MathArchive · Directed by 이영우 · 학습 데이터는 AI 로 요약 후 담당 강사가 검수·발송합니다.
  </div>
</body></html>
"""


def _render_pdf(html: str, out_path: Path) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(
            path=str(out_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--student-name", default="맛보기학생")
    ap.add_argument("--out", default="/tmp/student_card.pdf")
    ap.add_argument("--local", action="store_true")
    args = ap.parse_args()

    if args.local:
        os.environ.pop("SUPABASE_DB_URL", None)
    else:
        _load_env_file()

    conn = get_connection()
    data = _fetch_student_data(conn, args.student_name)
    if not data:
        print(f"ERROR: 학생 '{args.student_name}' 없음", file=sys.stderr)
        sys.exit(1)

    target = "Supabase Postgres" if is_cloud() else "로컬 SQLite"
    print(f"[INFO] {args.student_name} 데이터 수집 완료 ({target})")
    print(f"  - clinic {len(data['clinic'])} / assess_q {len(data['assess_q'])} / "
          f"preds {len(data['preds'])} / logs {len(data['logs'])}")

    chart_b64 = _render_prism_chart_b64(data["clinic"])
    html = _build_html(data, chart_b64)

    out = Path(args.out)
    _render_pdf(html, out)
    print(f"[OK] PDF 생성 → {out}")


if __name__ == "__main__":
    main()
