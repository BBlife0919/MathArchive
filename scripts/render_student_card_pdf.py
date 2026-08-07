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
# 랜딩 표기 (긍정형). DB error_code 는 위의 원본 유지.
PRISM_DISPLAY = {
    "계산실수": "계산정확성", "조건해석실패": "조건해석", "개념누락": "개념내재",
    "전략선택실패": "전략선택", "시간관리": "시간관리",
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

    prism_rows = _q(conn,
        "SELECT eval_date, score_p, score_r, score_i, score_s, score_m, note "
        "FROM prism_assessment WHERE student_id = ? "
        "ORDER BY eval_date DESC, assessment_id DESC LIMIT 1",
        (sid,))

    return {
        "student":   dict(s),
        "clinic":    [dict(r) for r in clinic],
        "assess_q":  [dict(r) for r in assess_q],
        "assess_l":  dict(assess_l_rows[0]) if assess_l_rows else None,
        "preds":     [dict(r) for r in preds],
        "logs":      [dict(r) for r in logs],
        "prism":     dict(prism_rows[0]) if prism_rows else None,
    }


def _setup_korean_font(plt, font_manager) -> None:
    for f in ("AppleSDGothicNeo.ttc", "AppleGothic.ttf", "AppleSDGothicNeo-Regular.otf"):
        for p in ("/System/Library/Fonts/", "/Library/Fonts/"):
            full = Path(p) / f
            if full.exists():
                font_manager.fontManager.addfont(str(full))
                plt.rcParams["font.family"] = font_manager.FontProperties(fname=str(full)).get_name()
                return


def _render_prism_radar_b64(prism_row: dict) -> str:
    """강사 PRISM 평가 → 5각형 레이더 차트 PNG (base64)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    import numpy as np

    _setup_korean_font(plt, font_manager)

    categories = ["P\n계산정확성", "R\n조건해석", "I\n개념내재",
                  "S\n전략선택", "M\n시간관리"]
    scores = [prism_row["score_p"], prism_row["score_r"], prism_row["score_i"],
              prism_row["score_s"], prism_row["score_m"]]
    values = scores + scores[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), dpi=180,
                           subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8faff")

    # 격자원
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels([])
    ax.grid(True, color="#d5deee", linewidth=0.9, alpha=0.9)
    ax.spines["polar"].set_color("#c9d3ea")
    ax.spines["polar"].set_linewidth(1.2)

    # 배경 fill (두 겹으로 은은한 그라디언트 느낌)
    ax.fill(angles, values, color="#2b6fff", alpha=0.10, zorder=2)
    ax.fill(angles, values, color="#2b6fff", alpha=0.18, zorder=3)

    # 라인 & 마커
    ax.plot(angles, values, "-", color="#2b6fff",
            linewidth=3.2, zorder=4, solid_joinstyle="round")
    ax.plot(angles, values, "o", color="#ffffff",
            markersize=12, markeredgecolor="#2b6fff",
            markeredgewidth=2.4, zorder=5)

    ax.set_thetagrids(np.degrees(angles[:-1]), categories,
                      fontsize=13, fontweight=700, color="#0a1020")

    # y축 눈금 숫자 (top axis 하나에)
    for r in [1, 2, 3, 4, 5]:
        ax.text(np.pi / 2, r + 0.13, str(r),
                fontsize=8.5, color="#8a96b3",
                ha="center", va="bottom", zorder=6)

    # 각 꼭지점 점수 뱃지
    for angle, val in zip(angles[:-1], scores):
        ax.text(angle, val + 0.35, str(val),
                fontsize=11, fontweight=800, color="#0a1020",
                ha="center", va="center", zorder=7,
                bbox=dict(boxstyle="round,pad=0.28",
                          facecolor="#ffffff", edgecolor="#2b6fff",
                          linewidth=1.3))

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", bbox_inches="tight",
                facecolor="#ffffff", pad_inches=0.15)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _render_prism_chart_b64(clinic_rows: list) -> str:
    """[폴백] clinic_entries 기반 막대 차트 (PRISM 평가 없을 때)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    _setup_korean_font(plt, font_manager)

    counter = Counter(r["error_code"] for r in clinic_rows)
    labels = [f"{PRISM_LETTER[c]}\n{PRISM_DISPLAY[c]}" for c in PRISM_ORDER]
    values = [counter.get(c, 0) for c in PRISM_ORDER]
    colors = ["#F97316", "#4F46E5", "#6366F1", "#8B5CF6", "#EF4444"]

    fig, ax = plt.subplots(figsize=(8, 3.2), dpi=140)
    bars = ax.bar(labels, values, color=colors, width=0.55)
    ax.set_ylabel("건수", fontsize=10)
    ax.set_title("PRISM — 최근 4주 오답 5스펙트럼 (정밀 누적)", fontsize=12, pad=10)
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

    # PRISM 강사 평가 (있으면) — RIS/PM 평균
    pr = data.get("prism")
    if pr:
        ris_avg = (pr["score_r"] + pr["score_i"] + pr["score_s"]) / 3
        pm_avg  = (pr["score_p"] + pr["score_m"]) / 2
        ris_label = f"이해 RIS 평균"
        pm_label  = f"수행 PM 평균"
        ris_value = f"{ris_avg:.1f}/5"
        pm_value  = f"{pm_avg:.1f}/5"
        prism_subtitle = f"강사 평가 · {pr['eval_date']}"
    else:
        # 폴백 — clinic_entries 누적 카운트
        counter = Counter(r["error_code"] for r in data["clinic"])
        ris_total = sum(counter[c] for c in RIS_CODES)
        pm_total  = sum(counter[c] for c in PM_CODES)
        total = ris_total + pm_total
        ris_label = "이해 RIS (누적)"
        pm_label  = "수행 PM (누적)"
        ris_value = f"{ris_total}건 ({ris_total/total*100:.0f}%)" if total else "—"
        pm_value  = f"{pm_total}건 ({pm_total/total*100:.0f}%)"  if total else "—"
        prism_subtitle = "클리닉 정밀 누적 (최근 4주)"

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
    @page { size: A4; margin: 14mm 14mm 12mm 14mm; }
    * { box-sizing: border-box; }
    :root {
      --ink:#0a1020; --blue:#2b6fff; --blue-soft:#e8efff;
      --paper:#f5f8ff; --text:#13203c; --muted:#5f6c87; --line:#e3e9f7;
      --pos:#10b981; --neg:#ef4444;
    }
    body { font-family: 'Pretendard', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
           color: var(--text); font-size: 10.5pt; margin: 0; letter-spacing: -0.01em;
           -webkit-font-smoothing: antialiased; }

    /* ── 헤더 ─────────────────────────────── */
    .head { display: flex; justify-content: space-between; align-items: flex-end;
            padding-bottom: 10px; margin-bottom: 14px;
            border-bottom: 1.5px solid var(--ink); }
    .brand { font-size: 20pt; font-weight: 800; letter-spacing: -0.5px; color: var(--ink);
             line-height: 1; }
    .brand-sub { color: var(--muted); font-size: 9.5pt; margin-top: 3px;
                 letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600; }
    .meta { color: var(--muted); font-size: 9pt; text-align: right; }
    .meta strong { color: var(--ink); font-weight: 700; }

    /* ── 섹션 헤딩 ─────────────────────────── */
    h2 { font-size: 12.5pt; margin: 18px 0 8px; padding: 0 0 4px 0;
         font-weight: 800; color: var(--ink); letter-spacing: -0.02em;
         border-bottom: 1px solid var(--line); }
    h2 .sub { font-weight: 500; color: var(--muted); font-size: 0.72em;
              margin-left: 6px; letter-spacing: 0; }

    /* ── 학생 카드 ─────────────────────────── */
    .student-card { background: #ffffff; border: 1px solid var(--line);
                    border-radius: 10px; padding: 12px 16px;
                    display: flex; gap: 24px; flex-wrap: wrap;
                    box-shadow: 0 1px 2px rgba(10,16,32,0.03); }
    .student-card div { font-size: 10.5pt; color: var(--text); }
    .student-card strong { color: var(--muted); margin-right: 6px; font-weight: 600;
                           font-size: 9pt; letter-spacing: 0.04em;
                           text-transform: uppercase; }
    .student-card .name { font-size: 14pt; font-weight: 800; color: var(--ink);
                          letter-spacing: -0.02em; }

    /* ── PRISM 요약 카드 ───────────────────── */
    .qm-summary { display: flex; gap: 12px; margin: 8px 0 12px; }
    .qm-summary .card { flex: 1; padding: 12px 16px; border-radius: 10px;
                        background: var(--blue-soft); border: 1px solid #cbd7ff;
                        box-shadow: 0 1px 2px rgba(10,16,32,0.03); }
    .qm-summary .card.m { background: #fff4e6; border-color: #ffd7a3; }
    .qm-summary .card .label { font-size: 8.5pt; color: var(--muted);
                               font-weight: 700; letter-spacing: 0.04em;
                               text-transform: uppercase; }
    .qm-summary .card .val { font-size: 18pt; font-weight: 800;
                             color: var(--ink); margin-top: 4px; letter-spacing: -0.02em; }

    /* ── 5각형 차트 (대형화) ─────────────── */
    .chart { text-align: center; margin: 6px 0 4px; }
    .chart img { width: 95%; max-height: 340px; object-fit: contain; }

    /* ── 정량 4카드 ──────────────────────── */
    .quant-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
    .quant-grid .g { background: #ffffff; padding: 10px 12px; border-radius: 10px;
                     text-align: center; border: 1px solid var(--line);
                     box-shadow: 0 1px 2px rgba(10,16,32,0.03); }
    .quant-grid .g .lbl { font-size: 8.5pt; color: var(--muted);
                          font-weight: 700; letter-spacing: 0.04em;
                          text-transform: uppercase; }
    .quant-grid .g .val { font-size: 12pt; font-weight: 700;
                          color: var(--ink); margin-top: 4px; }

    /* ── 표 (세련) ───────────────────────── */
    table { width: 100%; border-collapse: separate; border-spacing: 0;
            margin-top: 6px; border: 1px solid var(--line); border-radius: 10px;
            overflow: hidden; box-shadow: 0 1px 2px rgba(10,16,32,0.03); }
    th, td { padding: 8px 12px; font-size: 9.8pt; text-align: center;
             border-bottom: 1px solid var(--line); }
    th { background: #f8faff; color: var(--muted); font-weight: 700;
         font-size: 8.5pt; letter-spacing: 0.04em; text-transform: uppercase; }
    tr:last-child td { border-bottom: none; }
    tr:nth-child(even) td { background: #fafcff; }
    td.gap-over  { color: var(--neg); font-weight: 800; }
    td.gap-under { color: var(--pos); font-weight: 800; }
    td.gap-match { color: var(--muted); }
    .qual-date { font-size: 8.5pt; color: var(--muted); margin-top: 6px; text-align: right; }

    /* ── 강사 코멘트 (강조) ──────────────── */
    .comment-box { padding: 16px 20px; border-radius: 12px;
                   background: linear-gradient(135deg, #f5f8ff 0%, #e8efff 100%);
                   border: 1px solid #cbd7ff; border-left: 4px solid var(--blue);
                   color: var(--text); font-size: 12pt; line-height: 1.75;
                   letter-spacing: -0.005em; font-weight: 500;
                   box-shadow: 0 2px 6px rgba(43,111,255,0.08); }

    .muted { color: var(--muted); font-size: 9pt; }
    .footer { margin-top: 14px; padding-top: 10px; border-top: 1px solid var(--line);
              font-size: 8.5pt; color: var(--muted); text-align: center;
              letter-spacing: 0.02em; }
    """

    school_grade = (
        f"{s.get('school') or '-'} · "
        f"{s.get('grade') or '-'}학년 {s.get('class_name') or ''}"
    ).strip(" ·")

    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
<style>{css}</style></head>
<body>
  <div class="head">
    <div>
      <div class="brand">MATHOLOGY</div>
      <div class="brand-sub">Weekly Student Report</div>
    </div>
    <div class="meta">발행일 <strong>{today_str}</strong><br/>주간 {week_start} ~</div>
  </div>

  <div class="student-card">
    <div class="name">{s['name']}</div>
    <div><strong>학교</strong>{s.get('school') or '-'}</div>
    <div><strong>학년/반</strong>{s.get('grade') or '-'}학년 {s.get('class_name') or ''}</div>
  </div>

  <h2>PRISM · 5스펙트럼 진단<span class="sub">{prism_subtitle}</span></h2>
  <div class="qm-summary">
    <div class="card"><div class="label">{ris_label}</div>
      <div class="val">{ris_value}</div></div>
    <div class="card m"><div class="label">{pm_label}</div>
      <div class="val">{pm_value}</div></div>
  </div>
  <div class="chart"><img src="data:image/png;base64,{chart_b64}" alt="PRISM chart"/></div>

  <h2>과제 정밀평가<span class="sub">최근 4주 정량 + 최근 정성</span></h2>
  <div class="quant-grid">
    <div class="g"><div class="lbl">A 등급</div><div class="val">{grade_pct('A')}</div></div>
    <div class="g"><div class="lbl">B 등급</div><div class="val">{grade_pct('B')}</div></div>
    <div class="g"><div class="lbl">C 등급</div><div class="val">{grade_pct('C')}</div></div>
    <div class="g"><div class="lbl">D 등급</div><div class="val">{grade_pct('D')}</div></div>
  </div>
  {qual_html}

  <h2>자가예측 격차<span class="sub">메타인지 추적</span></h2>
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
    © MATHOLOGY · Directed by 이영우 · 학습 데이터는 AI 로 요약 후 담당 강사가 검수·발송합니다.
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

    # PRISM 평가 있으면 5각형 레이더, 없으면 막대 차트 폴백
    if data.get("prism"):
        chart_b64 = _render_prism_radar_b64(data["prism"])
    else:
        chart_b64 = _render_prism_chart_b64(data["clinic"])
    html = _build_html(data, chart_b64)

    out = Path(args.out)
    _render_pdf(html, out)
    print(f"[OK] PDF 생성 → {out}")


if __name__ == "__main__":
    main()
