"""학생 카드 v1 — 한 명의 학생 = 한 장의 운영 페이지.

구성 (대치동 노하우 + 클리닉 통합 기반):
1. 기본정보 (이름·학교·학년·반·메모)
2. Q-M Chart (clinic_entries 집계: Q=이해/방법, M=실수/시간)
3. 자가예측 격차 (예측 vs 실제 — 메타인지 추적)
4. 학습 로그 (진도/숙제/시험 통합 입력)
5. 관리 로그 (보호자/출결/메모 통합 입력)

DB:
- students (tenant_id 추가됨)
- student_progress (진도/숙제/시험/자가예측)
- student_log (보호자/출결/메모)
- clinic_entries (Q-M Chart 원천)
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

st.set_page_config(page_title="📋 학생 카드", page_icon="📋", layout="wide")

from auth_ui import require_auth, render_user_menu_in_sidebar  # noqa: E402
require_auth()
render_user_menu_in_sidebar()

st.title("📋 학생 카드")
st.caption("한 명 = 한 장. 진도·Q-M·자가예측·보호자 연락이 한 화면에 누적됩니다.")


# ── 오류코드 → Q/M 매핑 ────────────────────────────────
# Q (Question, 이해/방법 부재): 32% — 시간 들여 가르쳐야 사라짐
# M (Mistake, 실수/시간): 68% — 양과 절차로 사라짐
Q_CODES = {"개념누락", "조건해석실패", "전략선택실패"}
M_CODES = {"계산실수", "시간관리"}

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
    st.header("👤 학생")
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
        "Q-M Chart 매핑:\n"
        "- Q = 개념누락 / 조건해석실패 / 전략선택실패\n"
        "- M = 계산실수 / 시간관리"
    )

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


# ── 섹션 2: Q-M Chart ────────────────────────────────
st.subheader("2. Q-M Chart — 오답 원인 분포")
st.caption(
    "Q(이해/방법 부재)는 가르침으로, M(실수/시간)은 양과 절차로 사라집니다. "
    "비율이 한쪽으로 치우치면 처방 전략을 바꿔야 합니다."
)

entries_all = q(
    "SELECT error_code, wrong_date FROM clinic_entries WHERE student_id = ? "
    "ORDER BY wrong_date DESC",
    (sid,),
)

# 시간 윈도우 토글 (PDF §6 "2~4주 단위 오류 분포")
qm_window = st.radio(
    "집계 기간",
    options=["전체", "최근 4주", "최근 2주"],
    horizontal=True,
    key="qm_window",
)
if qm_window == "최근 4주":
    cutoff = (date.today() - timedelta(weeks=4)).isoformat()
    entries = [e for e in entries_all if (e["wrong_date"] or "") >= cutoff]
elif qm_window == "최근 2주":
    cutoff = (date.today() - timedelta(weeks=2)).isoformat()
    entries = [e for e in entries_all if (e["wrong_date"] or "") >= cutoff]
else:
    entries = entries_all

if not entries:
    if entries_all:
        st.info(f"선택한 기간({qm_window})에 오답이 없습니다.")
    else:
        st.info("아직 클리닉 오답 기록이 없습니다. 클리닉 페이지에서 처방전을 1건 생성하세요.")
else:
    counter = Counter(e["error_code"] for e in entries)
    q_total = sum(counter[c] for c in Q_CODES)
    m_total = sum(counter[c] for c in M_CODES)
    total = q_total + m_total

    cc1, cc2, cc3 = st.columns(3)
    cc1.metric("Q (이해/방법)", f"{q_total}건",
               f"{q_total/total*100:.0f}%" if total else "-")
    cc2.metric("M (실수/시간)", f"{m_total}건",
               f"{m_total/total*100:.0f}%" if total else "-")
    cc3.metric("총 오답", f"{total}건")

    df = pd.DataFrame(
        [{"오류코드": code, "건수": counter.get(code, 0),
          "구분": "Q" if code in Q_CODES else "M"}
         for code in list(Q_CODES) + list(M_CODES)]
    )
    st.bar_chart(df.set_index("오류코드")["건수"], height=220)

    with st.expander("선택 기간 내 최근 10건"):
        for e in entries[:10]:
            tag = "Q" if e["error_code"] in Q_CODES else "M"
            st.caption(f"· [{tag}] {e['wrong_date']} · {e['error_code']}")

st.divider()


# ── 섹션 3: 자가예측 격차 ────────────────────────────
st.subheader("3. 자가예측 격차 — 메타인지 추적")
st.caption("시험 전 자가예측 점수와 실제 점수의 차이. 격차가 크면 자기평가 능력이 약합니다.")

with st.expander("➕ 자가예측 기록 추가", expanded=False):
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

with st.expander("➕ 학습 로그 추가", expanded=False):
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


# ── 섹션 5: 관리 로그 (보호자/출결/메모) ─────────────
st.subheader("5. 관리 로그 — 보호자·출결·메모")
st.caption("학부모 신뢰의 핵심. 모든 연락/결석/특이사항을 1줄씩 누적합니다.")

with st.expander("➕ 관리 로그 추가", expanded=False):
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
