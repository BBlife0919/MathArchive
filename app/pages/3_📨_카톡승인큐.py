"""카톡 승인 큐 — 주간 학부모 보고 발송 관리 (P4 카톡 자동화 v1).

PDF §7-3 운영 룰:
1. AI 가 학생별 데이터(PRISM·자가예측·학습 로그)를 요약해 draft 생성
2. 강사가 학생별 1문장(instructor_note) 직접 추가 → 승인
3. cron(GitHub Actions, 금 17시) 이 approved row 만 발송
4. instructor_note 미입력 시 발송 차단 (코드 레벨)

DB: kakao_send_queue (status: draft → approved → sent / failed)
"""
from __future__ import annotations

import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import get_connection as _get_db_connection  # noqa: E402

st.set_page_config(page_title="📨 승인 큐 — MATHOLOGY", page_icon="📨", layout="wide")

from auth_ui import require_auth, render_user_menu_in_sidebar  # noqa: E402
import auth  # noqa: E402
require_auth()
render_user_menu_in_sidebar()

# 관리자만 접근 (강사 본인이 학부모에게 직접 발송 책임)
if not auth.is_admin():
    st.error("관리자 전용 페이지입니다.")
    st.stop()

st.title("📨 카톡 승인 큐")
st.caption(
    "AI 가 학생별 데이터로 draft 를 만들고, 강사가 1문장 추가 후 승인하면 "
    "금요일 17시 cron 이 솔라피로 발송합니다. (PDF §7-3 하이브리드 강제)"
)

RIS_CODES = {"개념누락", "조건해석실패", "전략선택실패"}   # PRISM 이해
PM_CODES  = {"계산실수", "시간관리"}                       # PRISM 수행


@st.cache_resource
def get_conn():
    return _get_db_connection()


def q(sql: str, params=()):
    return get_conn().execute(sql, params).fetchall()


def exec_commit(sql: str, params=()) -> int:
    conn = get_conn()
    cur = conn.execute(sql, params)
    conn.commit()
    return cur.lastrowid


# ── AI draft 생성 로직 (학생카드 데이터 요약) ─────────────
def build_ai_draft(student_id: int, student_name: str) -> str:
    """학생카드의 PRISM + 자가예측 + 학습 로그 → PDF §7-4 템플릿 문장.

    솔라피 알림톡 템플릿이 심사 완료되면 본문은 템플릿 변수 치환으로 가지만,
    지금은 자유 텍스트 draft 로 만들어 강사가 검수/편집할 수 있게 한다.
    """
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # PRISM 강사 평가 (우선) → 없으면 clinic_entries 누적
    prism_rows = q(
        "SELECT eval_date, score_p, score_r, score_i, score_s, score_m "
        "FROM prism_assessment WHERE student_id = ? "
        "ORDER BY eval_date DESC, assessment_id DESC LIMIT 1",
        (student_id,),
    )
    if prism_rows:
        pr = prism_rows[0]
        ris_avg = (pr["score_r"] + pr["score_i"] + pr["score_s"]) / 3
        pm_avg  = (pr["score_p"] + pr["score_m"]) / 2
        prism_line = (
            f"· PRISM 강사 평가 ({pr['eval_date']}): "
            f"이해 RIS {ris_avg:.1f}/5 · 수행 PM {pm_avg:.1f}/5\n"
        )
    else:
        cutoff = (today - timedelta(weeks=4)).isoformat()
        entries = q(
            "SELECT error_code FROM clinic_entries "
            "WHERE student_id = ? AND wrong_date >= ?",
            (student_id, cutoff),
        )
        counter = Counter(e["error_code"] for e in entries)
        ris_total = sum(counter[c] for c in RIS_CODES)
        pm_total  = sum(counter[c] for c in PM_CODES)
        prism_line = (
            f"· PRISM (최근 4주 누적): 이해 RIS {ris_total}건 / 수행 PM {pm_total}건\n"
        )

    # 직전 자가예측
    pred = q(
        "SELECT self_predicted, self_actual FROM student_progress "
        "WHERE student_id = ? AND category = '자가예측' "
        "ORDER BY log_date DESC LIMIT 1",
        (student_id,),
    )
    gap_line = ""
    if pred:
        gap = (pred[0]["self_actual"] or 0) - (pred[0]["self_predicted"] or 0)
        sign = "+" if gap >= 0 else ""
        gap_line = f"· 자가예측 격차: {sign}{gap}점\n"

    # 최근 7일 학습 로그 건수
    seven_ago = (today - timedelta(days=7)).isoformat()
    logs = q(
        "SELECT category FROM student_progress "
        "WHERE student_id = ? AND log_date >= ? AND category != '자가예측'",
        (student_id, seven_ago),
    )
    log_summary = Counter(l["category"] for l in logs)

    return (
        f"[EUM] {student_name} 학부모님께 안녕하세요. "
        f"{week_start.isoformat()} 주 학습 보고드립니다.\n"
        f"· 이번 주 학습 로그: "
        f"{log_summary.get('진도', 0)}진도·{log_summary.get('숙제', 0)}숙제·"
        f"{log_summary.get('시험', 0)}시험\n"
        + prism_line
        + gap_line +
        "· 다음 주 과제: [강사 코멘트로 보강 예정]\n"
        "※ 학습 데이터는 AI 로 요약 후 담당 강사가 검수·발송합니다."
    )


# ── 신규 draft 생성 폼 ────────────────────────────────────
st.subheader("1. 신규 draft 생성")
students = q("SELECT student_id, name FROM students ORDER BY name")
if not students:
    st.info("등록된 학생이 없습니다. 학생카드 페이지에서 먼저 등록하세요.")
else:
    with st.form("new_draft"):
        sc1, sc2, sc3 = st.columns([2, 2, 1])
        sel_sid = sc1.selectbox(
            "학생",
            options=[s["student_id"] for s in students],
            format_func=lambda i: next(s["name"] for s in students if s["student_id"] == i),
        )
        sel_phone = sc2.text_input("학부모 카톡 전화번호", placeholder="01012345678")
        sel_template = sc3.text_input("템플릿 코드", value="WEEKLY_REPORT_V1")
        sel_scheduled = st.date_input(
            "발송 예정일", value=date.today() + timedelta(days=(4 - date.today().weekday()) % 7)
        )
        if st.form_submit_button("AI draft 생성 + 큐 적재"):
            if not sel_phone.strip():
                st.error("학부모 전화번호 입력 필수")
            else:
                sel_name = next(s["name"] for s in students if s["student_id"] == sel_sid)
                draft = build_ai_draft(sel_sid, sel_name)
                exec_commit(
                    """INSERT INTO kakao_send_queue
                       (student_id, target_phone, template_code, ai_draft,
                        status, scheduled_at)
                       VALUES (?, ?, ?, ?, 'draft', ?)""",
                    (sel_sid, sel_phone.strip(), sel_template.strip(),
                     draft, sel_scheduled.isoformat()),
                )
                st.success(f"{sel_name} draft 생성됨")
                st.rerun()

st.divider()


# ── 승인 대기 (draft) ────────────────────────────────────
st.subheader("2. 승인 대기 (draft) — 강사 1문장 필수")
drafts = q(
    """SELECT k.queue_id, k.student_id, k.target_phone, k.ai_draft,
              k.instructor_note, k.scheduled_at, s.name AS student_name
       FROM kakao_send_queue k
       JOIN students s ON k.student_id = s.student_id
       WHERE k.status = 'draft'
       ORDER BY k.scheduled_at, k.queue_id""",
)
if not drafts:
    st.info("승인 대기 항목이 없습니다.")
else:
    for d in drafts:
        with st.expander(
            f"📩 {d['student_name']} · 예정 {d['scheduled_at']} · → {d['target_phone']}",
            expanded=False,
        ):
            st.markdown("**AI draft 본문**")
            st.code(d["ai_draft"] or "(비어있음)", language=None)

            note = st.text_area(
                "강사 1문장 (instructor_note) — **미입력 시 승인 불가**",
                value=d["instructor_note"] or "",
                key=f"note_{d['queue_id']}",
                placeholder="예: OO이가 이번 주 인수분해 복합형에서 큰 진전 보였습니다.",
                height=80,
            )
            bc1, bc2, _ = st.columns([1, 1, 4])
            if bc1.button("✅ 승인", key=f"approve_{d['queue_id']}", type="primary"):
                if not note.strip():
                    st.error("강사 코멘트가 비어있어 승인할 수 없습니다 (PDF §7-3 룰).")
                else:
                    exec_commit(
                        "UPDATE kakao_send_queue "
                        "SET instructor_note = ?, status = 'approved' "
                        "WHERE queue_id = ?",
                        (note.strip(), d["queue_id"]),
                    )
                    st.success("승인됨")
                    st.rerun()

            # 삭제는 confirm checkbox 활성 시에만 노출 — 실수 클릭 방지
            confirm_del = bc2.checkbox(
                "삭제 확인",
                key=f"confirm_del_{d['queue_id']}",
            )
            if confirm_del:
                if st.button(
                    "🗑 삭제 실행", key=f"del_{d['queue_id']}",
                ):
                    exec_commit(
                        "DELETE FROM kakao_send_queue WHERE queue_id = ?",
                        (d["queue_id"],),
                    )
                    st.rerun()

st.divider()


# ── 승인됨 (approved) ────────────────────────────────────
st.subheader("3. 승인됨 (approved) — 발송 대기")
approved = q(
    """SELECT k.queue_id, k.scheduled_at, k.target_phone, k.instructor_note,
              s.name AS student_name
       FROM kakao_send_queue k
       JOIN students s ON k.student_id = s.student_id
       WHERE k.status = 'approved'
       ORDER BY k.scheduled_at""",
)
if approved:
    df_app = pd.DataFrame([{
        "예정일": a["scheduled_at"],
        "학생": a["student_name"],
        "전화번호": a["target_phone"],
        "강사 코멘트": (a["instructor_note"] or "")[:40],
        "queue_id": a["queue_id"],
    } for a in approved])
    st.dataframe(df_app, use_container_width=True, hide_index=True)

    qid_revert = st.selectbox(
        "승인 취소할 queue_id",
        options=[None] + [a["queue_id"] for a in approved],
        format_func=lambda x: "선택 안 함" if x is None else f"#{x}",
    )
    if qid_revert and st.button("↩ draft 로 되돌리기"):
        exec_commit(
            "UPDATE kakao_send_queue SET status = 'draft' WHERE queue_id = ?",
            (qid_revert,),
        )
        st.rerun()
else:
    st.info("승인된 항목이 없습니다.")

st.divider()


# ── 발송 결과 로그 ───────────────────────────────────────
st.subheader("4. 발송 결과 (최근 20건)")
logs = q(
    """SELECT k.queue_id, k.status, k.sent_at, k.target_phone,
              k.solapi_msg_id, k.error_log, s.name AS student_name
       FROM kakao_send_queue k
       JOIN students s ON k.student_id = s.student_id
       WHERE k.status IN ('sent', 'failed')
       ORDER BY COALESCE(k.sent_at, k.created_at) DESC
       LIMIT 20""",
)
if logs:
    df_log = pd.DataFrame([{
        "queue_id": l["queue_id"],
        "상태": "✅ 발송" if l["status"] == "sent" else "❌ 실패",
        "학생": l["student_name"],
        "전화번호": l["target_phone"],
        "발송 시각": l["sent_at"] or "-",
        "솔라피 MSG ID": l["solapi_msg_id"] or "-",
        "에러": (l["error_log"] or "")[:50],
    } for l in logs])
    st.dataframe(df_log, use_container_width=True, hide_index=True)
else:
    st.info("발송 기록이 없습니다.")
