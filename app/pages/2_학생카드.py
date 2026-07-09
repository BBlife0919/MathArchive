"""학생 카드 v1 — 한 명의 학생 = 한 장의 운영 페이지.

구성 (대치동 노하우 + 클리닉 통합 기반):
1. 기본정보 (이름·학교·학년·반·메모)
2. PRISM — 오답 5스펙트럼 분광 (이해 RIS / 수행 PM)
3. 자가예측 격차 (예측 vs 실제 — 메타인지 추적)
4. 학습 로그 (진도/숙제/시험 통합 입력)
5. 과제 정밀평가 (PDF §5-2: 정량 매일 A/B/C/D + 정성 월 2회 4항목)
6. 관리 로그 (보호자/출결/메모 통합 입력)

DB:
- students (tenant_id 추가됨)
- student_progress (진도/숙제/시험/자가예측)
- student_log (보호자/출결/메모)
- student_assessment (과제 정밀평가 — 정량/정성)
- clinic_entries (PRISM 원천)
"""
from __future__ import annotations

import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import get_connection as _get_db_connection  # noqa: E402

st.set_page_config(page_title="학생 카드 — MATHOLOGY", page_icon="", layout="wide")

from theme import apply_theme
apply_theme()

from auth_ui import require_auth, render_user_menu_in_sidebar  # noqa: E402
require_auth()
render_user_menu_in_sidebar()

st.title("학생 카드")
st.caption("한 명 = 한 장. 진도·PRISM·자가예측·보호자 연락이 한 화면에 누적됩니다.")


# ── PRISM — 오답 5스펙트럼 분광 ─────────────────────────
# 랜딩 표기는 긍정형 (계산정확성 등). DB error_code 값은 그대로 유지.
# P: Precision   계산실수 → 계산정확성   (수행 — 양·절차로 사라짐)
# R: Reading     조건해석실패 → 조건해석 (이해 — 가르침으로 사라짐)
# I: Inclusion   개념누락 → 개념내재     (이해)  (2026-07-01 Insight→Inclusion)
# S: Strategy    전략선택실패 → 전략선택 (이해)
# M: Management  시간관리                (수행)
PRISM_LETTER = {
    "계산실수":       "P",
    "조건해석실패":   "R",
    "개념누락":       "I",
    "전략선택실패":   "S",
    "시간관리":       "M",
}
PRISM_ORDER = ["계산실수", "조건해석실패", "개념누락", "전략선택실패", "시간관리"]
# 두 갈래 (이해 RIS / 수행 PM)
RIS_CODES = {"개념누락", "조건해석실패", "전략선택실패"}   # 이해
PM_CODES  = {"계산실수", "시간관리"}                       # 수행

LOG_TYPES = ["보호자", "출결", "메모"]
PROGRESS_CATEGORIES = ["진도", "숙제", "시험", "자가예측"]


# ── DB ────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return _get_db_connection()


def q(sql: str, params=()):
    return get_conn().execute(sql, params).fetchall()


def exec_commit(sql: str, params=()) -> int:
    cur = get_conn().execute(sql, params)
    try:
        get_conn().commit()
    except Exception:
        pass
    return cur.lastrowid if hasattr(cur, "lastrowid") else 0


# ── 학생 선택 ───────────────────────────────────────────
def list_students():
    return q(
        "SELECT student_id, name, school, grade, class_name, note "
        "FROM students ORDER BY school, grade, name"
    )


students = list_students()

with st.sidebar:
    st.header("학생")
    if not students:
        st.warning("등록된 학생이 없습니다. 클리닉 페이지에서 먼저 등록하세요.")
        st.stop()

    student_options = {
        f"[{r['school'] or '?'}] {r['name']} ({r['grade'] or '?'}학년)": r["student_id"]
        for r in students
    }
    sel_label = st.selectbox("학생 선택", list(student_options.keys()))
    sid = student_options[sel_label]

    st.divider()
    st.caption(
        "PRISM 5스펙트럼:\n"
        "- **P** 계산정확성 (Precision)\n"
        "- **R** 조건해석 (Reading)\n"
        "- **I** 개념내재 (Inclusion)\n"
        "- **S** 전략선택 (Strategy)\n"
        "- **M** 시간관리 (Management)\n"
        "→ 이해(RIS) vs 수행(PM)"
    )

    st.divider()
    with st.expander("학생용 양식 다운로드", expanded=False):
        st.caption("매번 같은 양식을 인쇄해서 학생에게 나눠주세요.")
        tpl_dir = Path(__file__).resolve().parent.parent.parent / "output" / "student_templates"
        for fname, label in [
            ("풀이노트_양식.pdf", "📘 풀이노트"),
            ("오답노트_양식.pdf", "📕 오답노트"),
            ("교재표시_규칙.pdf", "📗 교재표시 규칙"),
        ]:
            fpath = tpl_dir / fname
            if fpath.exists():
                st.download_button(
                    label=label,
                    data=fpath.read_bytes(),
                    file_name=fname,
                    mime="application/pdf",
                    key=f"dl_{fname}",
                    use_container_width=True,
                )
            else:
                st.caption(f"{fname} 미생성 — `python scripts/build_student_templates.py` 실행 필요")

student = next(s for s in students if s["student_id"] == sid)


# ── 섹션 1: 기본정보 ─────────────────────────────────
st.subheader("1. 기본정보")
c1, c2, c3, c4 = st.columns([0.25, 0.25, 0.2, 0.3])
c1.metric("이름", student["name"])
c2.metric("학교", student["school"] or "-")
c3.metric("학년·반", f"{student['grade'] or '?'}학년 {student['class_name'] or ''}".strip())
clinic_count = q(
    "SELECT COUNT(*) AS n FROM clinic_entries WHERE student_id = ?", (sid,)
)[0]["n"]
c4.metric("누적 오답", f"{clinic_count}건")

with st.expander("기본정보 수정"):
    with st.form("edit_student"):
        new_school = st.text_input("학교", value=student["school"] or "")
        new_grade = st.number_input("학년", 1, 6, value=int(student["grade"] or 1))
        new_class = st.text_input("반", value=student["class_name"] or "")
        new_note = st.text_area("메모", value=student["note"] or "", height=80)
        if st.form_submit_button("저장"):
            exec_commit(
                "UPDATE students SET school=?, grade=?, class_name=?, note=? "
                "WHERE student_id=?",
                (new_school.strip() or None, int(new_grade),
                 new_class.strip() or None, new_note.strip() or None, sid),
            )
            st.success("저장됨. 새로고침합니다.")
            st.rerun()

st.divider()


# ── 섹션 2: PRISM 강사 임상 평가 ──────────────────────
st.subheader("2. PRISM — 강사 임상 평가")
st.caption(
    "매주 30초. 숙제 검사 + 평소 인상으로 5영역 결함도를 1~5점 입력. "
    "1=거의 없음 · 3=보통 · 5=매우 두드러짐"
)

# ── 입력 폼 ──
with st.expander("이번 주 PRISM 평가 입력", expanded=False):
    with st.form("prism_eval_form"):
        eval_dt = st.date_input("평가일", value=date.today(), key="prism_eval_dt")
        pc1, pc2, pc3, pc4, pc5 = st.columns(5)
        sp = pc1.slider("**P** 계산정확성", 1, 5, 3, key="prism_sp",
                        help="부호·이항·분수 등 기계적 실수 (Precision)")
        sr = pc2.slider("**R** 조건해석", 1, 5, 3, key="prism_sr",
                        help="문제 조건·범위 놓침 (Reading)")
        si = pc3.slider("**I** 개념내재", 1, 5, 3, key="prism_si",
                        help="공식·정의 내재화 부족 (Inclusion)")
        ss = pc4.slider("**S** 전략선택", 1, 5, 3, key="prism_ss",
                        help="접근법 선택 실패 (Strategy)")
        sm = pc5.slider("**M** 시간관리", 1, 5, 3, key="prism_sm",
                        help="시간 부족·서술형 누락 (Management)")
        pnote = st.text_area("강사 메모 (선택)", height=60, key="prism_note",
                             placeholder="예: 이번 주 단원평가에서 부등호 방향 헷갈리는 패턴 반복")
        if st.form_submit_button("💾 평가 저장"):
            exec_commit(
                """INSERT INTO prism_assessment
                   (student_id, eval_date, score_p, score_r, score_i, score_s, score_m, note)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (sid, eval_dt.isoformat(),
                 int(sp), int(sr), int(si), int(ss), int(sm),
                 pnote.strip() or None),
            )
            st.success("저장됨")
            st.rerun()

# ── 최신 평가 + 5각형 레이더 ──
latest_prism = q(
    "SELECT eval_date, score_p, score_r, score_i, score_s, score_m, note "
    "FROM prism_assessment WHERE student_id = ? "
    "ORDER BY eval_date DESC, assessment_id DESC LIMIT 1",
    (sid,),
)

if not latest_prism:
    st.info("아직 PRISM 평가 없음. 위 폼에서 첫 평가를 입력하세요.")
else:
    lp = latest_prism[0]
    scores = [lp["score_p"], lp["score_r"], lp["score_i"], lp["score_s"], lp["score_m"]]
    avg_ris = (lp["score_r"] + lp["score_i"] + lp["score_s"]) / 3
    avg_pm  = (lp["score_p"] + lp["score_m"]) / 2

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("이해 RIS 평균", f"{avg_ris:.1f}/5",
               help="Reading + Insight + Strategy")
    mc2.metric("수행 PM 평균",  f"{avg_pm:.1f}/5",
               help="Precision + Management")
    mc3.metric("최근 평가일", str(lp["eval_date"]))

    # 5각형 레이더 차트
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    import numpy as np

    # 한글 폰트
    for f in ("AppleSDGothicNeo.ttc", "AppleGothic.ttf"):
        for p in ("/System/Library/Fonts/", "/Library/Fonts/"):
            full = Path(p) / f
            if full.exists():
                font_manager.fontManager.addfont(str(full))
                plt.rcParams["font.family"] = font_manager.FontProperties(fname=str(full)).get_name()
                break

    categories = ["P 계산정확성", "R 조건해석", "I 개념내재", "S 전략선택", "M 시간관리"]
    values = scores + scores[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color="#4F46E5", alpha=0.25)
    ax.plot(angles, values, "o-", color="#4F46E5", linewidth=2)
    ax.set_thetagrids(np.degrees(angles[:-1]), categories, fontsize=10)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=8)
    ax.set_rlabel_position(0)
    ax.grid(True, alpha=0.5)
    ax.set_title(f"PRISM 5각형 — {lp['eval_date']}", fontsize=12, pad=20)

    rad1, rad2 = st.columns([0.5, 0.5])
    with rad1:
        st.pyplot(fig, use_container_width=True)
    with rad2:
        st.markdown("**점수표**")
        st.markdown(
            f"- **P** 계산정확성: {lp['score_p']}/5\n"
            f"- **R** 조건해석: {lp['score_r']}/5\n"
            f"- **I** 개념내재: {lp['score_i']}/5\n"
            f"- **S** 전략선택: {lp['score_s']}/5\n"
            f"- **M** 시간관리: {lp['score_m']}/5"
        )
        if lp["note"]:
            st.caption(f"{lp['note']}")
    plt.close(fig)

# ── 이력 ──
history = q(
    "SELECT eval_date, score_p, score_r, score_i, score_s, score_m, note "
    "FROM prism_assessment WHERE student_id = ? "
    "ORDER BY eval_date DESC LIMIT 10",
    (sid,),
)
if len(history) > 1:
    with st.expander(f"📈 최근 평가 이력 ({len(history)}건)"):
        hist_df = pd.DataFrame([
            {"날짜": h["eval_date"],
             "P": h["score_p"], "R": h["score_r"], "I": h["score_i"],
             "S": h["score_s"], "M": h["score_m"],
             "메모": (h["note"] or "")[:40]}
            for h in history
        ])
        st.dataframe(hist_df, use_container_width=True, hide_index=True)

# ── 참고: 클리닉 정밀 기록 누적 (보조) ──
clinic_entries_all = q(
    "SELECT error_code, wrong_date FROM clinic_entries WHERE student_id = ? "
    "ORDER BY wrong_date DESC",
    (sid,),
)
if clinic_entries_all:
    with st.expander(f"📂 참고 — 클리닉 정밀 기록 누적 ({len(clinic_entries_all)}건)"):
        st.caption("클리닉 페이지에서 입력한 오답 1건씩의 누적 분포 (참고용).")
        counter = Counter(e["error_code"] for e in clinic_entries_all)
        df = pd.DataFrame(
            [{"PRISM": f"{PRISM_LETTER[code]} · {code}",
              "건수": counter.get(code, 0),
              "구분": "이해" if code in RIS_CODES else "수행"}
             for code in PRISM_ORDER]
        )
        st.bar_chart(df.set_index("PRISM")["건수"], height=180)

st.divider()


# ── 섹션 3: 자가예측 격차 ────────────────────────────
st.subheader("3. 자가예측 격차 — 메타인지 추적")
st.caption("시험 전 자가예측 점수와 실제 점수의 차이. 격차가 크면 자기평가 능력이 약합니다.")

with st.expander("자가예측 기록 추가", expanded=False):
    with st.form("add_self_predict"):
        sp_date = st.date_input("시험일", value=date.today(), key="sp_date")
        sp_title = st.text_input("시험명", placeholder="예: 인수분해 단원평가")
        spc1, spc2 = st.columns(2)
        sp_pred = spc1.number_input("자가예측 점수", 0, 100, 80)
        sp_actual = spc2.number_input("실제 점수", 0, 100, 70)
        sp_note = st.text_input("메모", placeholder="예: 시간관리 실패로 -10")
        if st.form_submit_button("저장"):
            exec_commit(
                """INSERT INTO student_progress
                   (student_id, log_date, category, title,
                    self_predicted, self_actual, note)
                   VALUES (?, ?, '자가예측', ?, ?, ?, ?)""",
                (sid, sp_date.isoformat(), sp_title.strip() or None,
                 int(sp_pred), int(sp_actual), sp_note.strip() or None),
            )
            st.success("저장됨")
            st.rerun()

predicts = q(
    "SELECT log_date, title, self_predicted, self_actual, note "
    "FROM student_progress "
    "WHERE student_id = ? AND category = '자가예측' "
    "ORDER BY log_date DESC LIMIT 10",
    (sid,),
)
if predicts:
    rows = []
    for p in predicts:
        gap = (p["self_actual"] or 0) - (p["self_predicted"] or 0)
        rows.append({
            "날짜": p["log_date"],
            "시험": p["title"] or "-",
            "예측": p["self_predicted"],
            "실제": p["self_actual"],
            "격차": gap,
            "메모": p["note"] or "",
        })

    # 시간 순 line chart (PDF §5 "자가예측 격차 시각화", §6 메타인지 카드)
    df_pred = pd.DataFrame(rows)
    df_chart = (
        df_pred[["날짜", "예측", "실제"]]
        .iloc[::-1]                       # 최신→오래된 → 오래된→최신 (시간 축)
        .set_index("날짜")
    )
    # 같은 날 2건 이상 입력된 경우 일일 평균으로 집약 — zigzag 방지
    df_chart = df_chart.groupby(df_chart.index).mean()
    st.line_chart(df_chart, height=240)

    # 평균 격차 metric
    avg_gap = df_pred["격차"].mean()
    over_count  = int((df_pred["격차"] < 0).sum())   # 예측 > 실제 (과신)
    under_count = int((df_pred["격차"] > 0).sum())   # 예측 < 실제 (과소)
    gc1, gc2, gc3 = st.columns(3)
    gc1.metric("평균 격차", f"{avg_gap:+.1f}점")
    gc2.metric("과신 (예측>실제)", f"{over_count}건")
    gc3.metric("과소 (예측<실제)", f"{under_count}건")

    st.dataframe(df_pred, use_container_width=True, hide_index=True)
else:
    st.info("아직 자가예측 기록이 없습니다.")

st.divider()


# ── 섹션 4: 학습 로그 (진도/숙제/시험) ─────────────────
st.subheader("4. 학습 로그 — 진도·숙제·시험")
st.caption("Walk-Run-Fly 트랙 운영을 위해 계획(planned) vs 실제(actual)를 함께 기록합니다.")

with st.expander("학습 로그 추가", expanded=False):
    with st.form("add_progress"):
        lp_date = st.date_input("일자", value=date.today(), key="lp_date")
        lp_cat = st.selectbox("카테고리", ["진도", "숙제", "시험"])
        lp_chapter = st.text_input("단원/주제", placeholder="예: 인수분해")
        lp_title = st.text_input("제목", placeholder="예: 유형 1~10")
        lpc1, lpc2 = st.columns(2)
        lp_planned = lpc1.text_input("계획 (planned)", placeholder="예: 1h / 10문")
        lp_actual = lpc2.text_input("실제 (actual)", placeholder="예: 1.2h / 8문, 2개 보류")
        lps1, lps2 = st.columns(2)
        lp_raw = lps1.number_input("점수 (raw)", 0, 1000, 0)
        lp_max = lps2.number_input("만점 (max)", 0, 1000, 0)
        lp_note = st.text_area("메모", height=60)
        if st.form_submit_button("저장"):
            exec_commit(
                """INSERT INTO student_progress
                   (student_id, log_date, category, chapter, title,
                    planned, actual, score_raw, score_max, note)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sid, lp_date.isoformat(), lp_cat,
                 lp_chapter.strip() or None, lp_title.strip() or None,
                 lp_planned.strip() or None, lp_actual.strip() or None,
                 int(lp_raw) or None, int(lp_max) or None,
                 lp_note.strip() or None),
            )
            st.success("저장됨")
            st.rerun()

progs = q(
    "SELECT log_date, category, chapter, title, planned, actual, "
    "       score_raw, score_max, note "
    "FROM student_progress "
    "WHERE student_id = ? AND category IN ('진도', '숙제', '시험') "
    "ORDER BY log_date DESC, progress_id DESC LIMIT 20",
    (sid,),
)
if progs:
    rows = []
    for p in progs:
        score = (f"{p['score_raw']}/{p['score_max']}"
                 if p["score_raw"] is not None and p["score_max"] else "-")
        rows.append({
            "날짜": p["log_date"],
            "구분": p["category"],
            "단원": p["chapter"] or "-",
            "제목": p["title"] or "-",
            "계획": p["planned"] or "-",
            "실제": p["actual"] or "-",
            "점수": score,
            "메모": p["note"] or "",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("아직 학습 로그가 없습니다.")

st.divider()


# ── 섹션 5: 과제 정밀평가 (PDF §5-2) ───────────────────
st.subheader("5. 과제 정밀평가")
st.caption(
    "정량(매일 A/B/C/D)은 처방 갱신 신호, "
    "정성(월 2회 4항목)은 자기학습 자세 추적."
)

with st.expander("📘 평가 가이드 (각 항목 의미 + 운영법)", expanded=False):
    st.markdown(
        """
**정량 (매일, A~D)** — 그날 숙제 했나
- **A** 100% 완료 + 풀이 흔적 깔끔
- **B** 완료했지만 일부 미흡 (답만 적힌 문제 있음)
- **C** 절반만 풀었거나 풀이 부실
- **D** 거의 안 함
→ 3일 연속 C/D 면 보호자 알림. A 80% 이상이면 숙제량 ↑

---

**정성 (월 2회, 1~5점)** — 공부 습관이 잡혔나

**① 풀이노트 완성도**
노트에 풀이 과정을 남겼는가? (답만 적혀있으면 1점)
→ 양식: `[날짜][단원][문제번호] → 식 전개 → 답`

**② 서술형 완성도**
서술형 문제에서 **"왜냐하면 ~이므로 ~이다"** 식 논증을 글로 적었는가?
→ ∵(왜냐하면) ∴(따라서) 기호 의무화

**③ 교재표시 습관**
교재에 본인 마킹이 있는가? (새 책처럼 깨끗 = 공부 안 한 것)
→ 마킹 규칙: ★ 모르는 문제 / △ 헷갈렸지만 맞춤 / 형광 시험 전 다시볼 곳 / ✓ 확실해진 문제

**④ 2차 풀이 후 틀린 이유 작성**
틀린 문제 다시 풀 때, **처음 왜 틀렸는지 원인**을 적었는가?
→ 원인 카테고리 5개로 한정: 개념 / 조건 / 전략 / 계산 / 시간
→ 이게 가장 중요. 원인 인식 없이 다시 풀면 같은 실수 반복.
        """
    )

GRADE_OPTIONS = ["A", "B", "C", "D"]

with st.expander("정량 평가 (매일)", expanded=False):
    with st.form("add_assess_quant"):
        aq_date = st.date_input("평가일", value=date.today(), key="aq_date")
        aq_grade = st.radio(
            "과제 완성도",
            GRADE_OPTIONS,
            horizontal=True,
            key="aq_grade",
            help="A=100%완료+깔끔 / B=완료했지만 일부 미흡 / "
                 "C=절반 풀이 부실 / D=거의 안 함",
        )
        aq_note = st.text_input("메모 (선택)", placeholder="예: 풀이 빈약, 시간 부족", key="aq_note")
        if st.form_submit_button("저장"):
            exec_commit(
                """INSERT INTO student_assessment
                   (student_id, eval_date, eval_type, quantity_grade, note)
                   VALUES (?, ?, 'quantity', ?, ?)""",
                (sid, aq_date.isoformat(), aq_grade,
                 aq_note.strip() or None),
            )
            st.success("저장됨")
            st.rerun()

with st.expander("정성 평가 (월 2회 · 4항목)", expanded=False):
    with st.form("add_assess_qual"):
        al_date = st.date_input("평가일", value=date.today(), key="al_date")
        sl1 = st.slider(
            "풀이노트 완성도", 1, 5, 3, key="sl_note",
            help="답만 적힘=1 / 단계별 식 전개+답 구분=5",
        )
        sl2 = st.slider(
            "서술형 완성도", 1, 5, 3, key="sl_written",
            help="식만 나열=1 / ∵(왜냐하면) ∴(따라서) 논증 완성=5",
        )
        sl3 = st.slider(
            "교재 표시 습관", 1, 5, 3, key="sl_textbook",
            help="새 책처럼 깨끗=1 / 본인 마킹(★△형광✓) 시스템 작동=5",
        )
        sl4 = st.slider(
            "2차 풀이 후 틀린 이유 작성", 1, 5, 3, key="sl_second",
            help="그냥 다시 풀기만=1 / 원인 5종(개념/조건/전략/계산/시간) 명시=5",
        )
        al_note = st.text_input("메모 (선택)", key="al_note")
        if st.form_submit_button("저장"):
            exec_commit(
                """INSERT INTO student_assessment
                   (student_id, eval_date, eval_type,
                    note_completion, written_completion,
                    textbook_marking, second_solve_reason, note)
                   VALUES (?, ?, 'qualitative', ?, ?, ?, ?, ?)""",
                (sid, al_date.isoformat(),
                 int(sl1), int(sl2), int(sl3), int(sl4),
                 al_note.strip() or None),
            )
            st.success("저장됨")
            st.rerun()

# 최근 4주 정량 분포
quant_cutoff = (date.today() - timedelta(weeks=4)).isoformat()
quants = q(
    "SELECT quantity_grade FROM student_assessment "
    "WHERE student_id = ? AND eval_type = 'quantity' AND eval_date >= ?",
    (sid, quant_cutoff),
)
if quants:
    grade_counter = Counter(r["quantity_grade"] for r in quants if r["quantity_grade"])
    total_q = sum(grade_counter.values())
    gq1, gq2, gq3, gq4 = st.columns(4)
    for col, g in zip([gq1, gq2, gq3, gq4], GRADE_OPTIONS):
        cnt = grade_counter.get(g, 0)
        pct = f"{cnt / total_q * 100:.0f}%" if total_q else "-"
        col.metric(f"{g} 등급", f"{cnt}건", pct)
else:
    st.info("최근 4주 정량 평가 기록 없음.")

# 최근 정성 1건
latest_qual = q(
    "SELECT eval_date, note_completion, written_completion, "
    "       textbook_marking, second_solve_reason, note "
    "FROM student_assessment "
    "WHERE student_id = ? AND eval_type = 'qualitative' "
    "ORDER BY eval_date DESC LIMIT 1",
    (sid,),
)
if latest_qual:
    lq = latest_qual[0]
    st.markdown(f"**최근 정성 평가 ({lq['eval_date']})**")
    pq1, pq2, pq3, pq4 = st.columns(4)
    pq1.metric("풀이노트",       f"{lq['note_completion']}/5")
    pq2.metric("서술형",         f"{lq['written_completion']}/5")
    pq3.metric("교재 표시",       f"{lq['textbook_marking']}/5")
    pq4.metric("2차 풀이 이유",   f"{lq['second_solve_reason']}/5")
    if lq["note"]:
        st.caption(f"{lq['note']}")

st.divider()


# ── 섹션 6: 관리 로그 (보호자/출결/메모) ─────────────
st.subheader("6. 관리 로그 — 보호자·출결·메모")
st.caption("학부모 신뢰의 핵심. 모든 연락/결석/특이사항을 1줄씩 누적합니다.")

with st.expander("관리 로그 추가", expanded=False):
    with st.form("add_log"):
        ml_date = st.date_input("일자", value=date.today(), key="ml_date")
        ml_type = st.selectbox("유형", LOG_TYPES)
        ml_summary = st.text_input("요약 (1줄)",
                                   placeholder="예: 어머니께 단원평가 결과 공유 / 결석 / 집중도 저하")
        ml_detail = st.text_area("상세", height=80)
        if st.form_submit_button("저장"):
            exec_commit(
                """INSERT INTO student_log
                   (student_id, log_date, log_type, summary, detail)
                   VALUES (?, ?, ?, ?, ?)""",
                (sid, ml_date.isoformat(), ml_type,
                 ml_summary.strip() or None, ml_detail.strip() or None),
            )
            st.success("저장됨")
            st.rerun()

logs = q(
    "SELECT log_date, log_type, summary, detail "
    "FROM student_log WHERE student_id = ? "
    "ORDER BY log_date DESC, log_id DESC LIMIT 30",
    (sid,),
)
if logs:
    tabs = st.tabs(["전체"] + LOG_TYPES)
    for tab_idx, tab_name in enumerate(["전체"] + LOG_TYPES):
        with tabs[tab_idx]:
            filtered = (logs if tab_name == "전체"
                        else [r for r in logs if r["log_type"] == tab_name])
            if not filtered:
                st.caption("기록 없음")
                continue
            for r in filtered:
                with st.container(border=True):
                    st.caption(f"📅 {r['log_date']} · **{r['log_type']}**")
                    st.write(r["summary"] or "(요약 없음)")
                    if r["detail"]:
                        with st.expander("상세"):
                            st.write(r["detail"])
else:
    st.info("아직 관리 로그가 없습니다.")
