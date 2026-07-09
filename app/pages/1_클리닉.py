"""수학 클리닉 페이지 — 오답 1건 → 처방전 1장 PDF 자동 생성.

워크플로우:
1. 학생 선택(또는 신규 등록)
2. 오답 question_id + 오류코드 + 키워드 입력
3. '처방전 생성' 클릭 → 유사문항 3개 자동 추출 → DB 저장 → PDF 다운로드
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import streamlit as st

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import get_connection as _get_db_connection, is_cloud
from clinic_logic import (
    ERROR_CODES,
    ERROR_CODE_DISPLAY,
    find_similar_questions,
    compute_retry_schedule,
    insert_clinic_entry,
    list_pending_retries,
)

st.set_page_config(page_title="클리닉 — MATHOLOGY", page_icon="", layout="wide")

from theme import apply_theme
apply_theme()

from auth_ui import require_auth, render_user_menu_in_sidebar
require_auth()
render_user_menu_in_sidebar()

st.title("수학 클리닉")
st.caption(
    "오답 1건 → 즉시 인출 3문항 + D+3/7/14/30 재도전 처방전. "
    "스테이플러 묶음에 끼워넣어 점수 엔진을 가동하세요."
)


# ── DB 연결 ────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return _get_db_connection()


def query(sql, params=()):
    return get_conn().execute(sql, params).fetchall()


# ── 학생 관리 ─────────────────────────────────────────────
def list_students():
    return query(
        "SELECT student_id, name, school, grade, class_name "
        "FROM students ORDER BY school, grade, name"
    )


def create_student(name: str, school: str, grade: int, class_name: str) -> int:
    cloud = is_cloud()
    sql = "INSERT INTO students (name, school, grade, class_name) VALUES (?, ?, ?, ?)"
    if cloud:
        sql += " RETURNING student_id"
    cur = get_conn().execute(
        sql,
        (name.strip(), school.strip() or None, grade or None, class_name.strip() or None),
    )
    if cloud:
        sid = cur.fetchone()[0]
    else:
        sid = cur.lastrowid
    if hasattr(get_conn(), "commit"):
        try:
            get_conn().commit()
        except Exception:
            pass
    return sid


# ── 사이드바: 학생 선택/등록 ────────────────────────────
with st.sidebar:
    st.header("👤 학생")
    students = list_students()

    if students:
        student_options = {
            f"[{r['school'] or '?'}] {r['name']} ({r['grade'] or '?'}학년)": r["student_id"]
            for r in students
        }
        sel_label = st.selectbox("학생 선택", list(student_options.keys()))
        selected_student_id = student_options[sel_label]
    else:
        st.info("등록된 학생이 없습니다. 아래 폼에서 추가하세요.")
        selected_student_id = None

    with st.expander("신규 학생 등록"):
        with st.form("new_student"):
            new_name = st.text_input("이름")
            new_school = st.text_input("학교", placeholder="예: 광명북중")
            new_grade = st.number_input("학년", 1, 6, 1)
            new_class = st.text_input("반", placeholder="예: 3-2")
            if st.form_submit_button("등록"):
                if not new_name.strip():
                    st.error("이름 필수")
                else:
                    sid = create_student(new_name, new_school, int(new_grade), new_class)
                    st.success(f"등록 완료 (id={sid}). 다시 로드합니다.")
                    st.rerun()

# ── 메인: 오답 입력 폼 ───────────────────────────────────
if selected_student_id is None:
    st.warning("좌측 사이드바에서 학생을 등록/선택하세요.")
    st.stop()

st.subheader("오답 입력 → 처방전 생성")

# 문제 출처 모드 선택
source_mode = st.radio(
    "문제 출처",
    ["DB 검색 (MATHOLOGY 적재 문제)", "외부 문제 (학교 내신지·시판 교재)"],
    horizontal=True,
    key="src_mode",
    help="DB 검색은 인출 3문항 자동 추출 + 처방전 PDF 가능. 외부 문제는 클리닉 기록만 저장.",
)
is_db_mode = source_mode.startswith("")

qrow = None
wrong_qid = None
external_label = None

if is_db_mode:
    c1, c2 = st.columns([0.45, 0.55])
    with c1:
        kw = st.text_input(
            "검색어 (학교명·단원·키워드)",
            placeholder="예: 광명북 / 이차함수 / 인수분해",
            key="search_kw",
        )
        results = []
        if kw.strip():
            like = f"%{kw.strip()}%"
            results = query(
                "SELECT question_id, school, year, semester, exam_type, question_number, "
                "chapter, difficulty, question_text "
                "FROM questions "
                "WHERE school LIKE ? OR chapter LIKE ? OR question_text LIKE ? "
                "ORDER BY question_id DESC LIMIT 20",
                (like, like, like),
            )
        if kw.strip() and not results:
            st.error("검색 결과 없음 — 다른 키워드를 시도하거나 '외부 문제' 모드를 사용하세요.")
        elif results:
            options = {
                f"[{r['school']}] {r['question_number']}번 · {r['chapter']} · {r['difficulty']}  (id={r['question_id']})": r
                for r in results
            }
            picked = st.radio(
                f"검색 결과 ({len(results)}건)",
                options=list(options.keys()),
                key="search_pick",
            )
            qrow = options[picked]
            wrong_qid = qrow["question_id"]

        error_code = st.selectbox(
            "PRISM 오류코드", ERROR_CODES,
            format_func=lambda c: ERROR_CODE_DISPLAY.get(c, c),
            help="P 계산정확성 · R 조건해석 · I 개념내재 · S 전략선택 · M 시간관리",
        )
        keyword = st.text_input(
            "키워드 (학생 작성)", placeholder="예: 인수정리 적용 후 조립제법 단계 빼먹음"
        )
        wrong_dt = st.date_input("오답 발생일", value=date.today())

    with c2:
        if qrow:
            st.markdown("**선택한 오답 미리보기**")
            with st.container(border=True):
                st.markdown(qrow["question_text"][:600] + ("…" if len(qrow["question_text"]) > 600 else ""))
else:
    # 외부 문제 모드
    external_label = st.text_input(
        "외부 문제 라벨",
        placeholder="예: 광명북중 1학기 기말 12번 · 시판 ‘쎈’ p.84 17번",
        key="ext_label",
        help="DB에 없는 문제. 어디서 나온 문제인지 학생이 식별 가능하게 적기.",
    )
    error_code = st.selectbox(
        "PRISM 오류코드", ERROR_CODES,
        format_func=lambda c: ERROR_CODE_DISPLAY.get(c, c),
        help="P 계산정확성 · R 조건해석 · I 개념내재 · S 전략선택 · M 시간관리",
    )
    keyword = st.text_input(
        "키워드 (학생 작성)", placeholder="예: 부등호 방향 헷갈림"
    )
    wrong_dt = st.date_input("오답 발생일", value=date.today())
    st.info("외부 문제는 클리닉 기록만 저장됩니다 (인출 3문항·처방전 PDF 미생성).")

st.divider()

# ── 처방전 생성 ──────────────────────────────────────────
can_submit = (is_db_mode and qrow is not None) or (not is_db_mode and external_label and external_label.strip())
btn_label = "🩺 처방전 생성" if is_db_mode else "💾 클리닉 기록 저장"

if st.button(btn_label, type="primary", use_container_width=True, disabled=not can_submit):
    conn = get_conn()
    similar_qids: list = []
    schedule = compute_retry_schedule(wrong_dt)

    if is_db_mode:
        similar_qids = find_similar_questions(conn, int(wrong_qid))
        if len(similar_qids) < 3:
            st.error(
                f"인출 문항이 {len(similar_qids)}개만 추출됨 — "
                f"같은 단원의 풀이 가능 문제가 부족합니다. "
                f"처방전 생성을 중단합니다. (chapter: {qrow['chapter']})"
            )
            st.caption(
                "해결책: 같은 chapter에 더 많은 문제를 DB에 추가하거나, "
                "다른 오답 문제로 시도해보세요."
            )
            st.stop()

    entry_id = insert_clinic_entry(
        conn,
        student_id=selected_student_id,
        wrong_question_id=int(wrong_qid) if is_db_mode else None,
        wrong_date_iso=wrong_dt.isoformat(),
        error_code=error_code,
        keyword=keyword,
        prescribed_qids=similar_qids,
        external_label=(external_label.strip() if not is_db_mode else None),
    )
    st.success(f"클리닉 엔트리 저장됨 (entry_id={entry_id})")
    if not is_db_mode:
        st.caption(f"외부 문제 — {external_label}")
        st.markdown("**📅 재도전 스케줄**")
        st.markdown(
            f"- D+3 ({schedule['d3']})  ☐\n"
            f"- D+7 ({schedule['d7']})  ☐\n"
            f"- D+14 ({schedule['d14']})  ☐\n"
            f"- D+30 ({schedule['d30']})  ☐"
        )
        st.stop()

    # ── 이하는 DB 모드 전용 (처방전 PDF + 인출 3문항) ──
    # 처방전용 4문항 (오답 + 인출 3) PDF 생성
    all_qids = [int(wrong_qid)] + similar_qids
    placeholders = ",".join("?" * len(all_qids))
    rx_rows = query(
        f"""
        SELECT q.question_id, q.file_source, q.school, q.question_number,
               q.year, q.semester, q.exam_type,
               q.question_text, q.choices, q.answer, q.answer_type,
               q.points, q.chapter, q.difficulty, q.is_subjective,
               s.solution_text
        FROM questions q
        LEFT JOIN solutions s ON q.question_id = s.question_id
        WHERE q.question_id IN ({placeholders})
        ORDER BY CASE q.question_id
            {' '.join(f'WHEN {q} THEN {i}' for i, q in enumerate(all_qids))}
        END
        """,
        all_qids,
    )

    student_name = next(s["name"] for s in students if s["student_id"] == selected_student_id)
    rx_subtitle = (
        f"{student_name} · 오류코드: {error_code} · "
        f"재도전: D+3 {schedule['d3']} / D+7 {schedule['d7']} / "
        f"D+14 {schedule['d14']} / D+30 {schedule['d30']}"
    )

    try:
        from pdf_engine import generate_exam_pdf
        pdf_data = generate_exam_pdf(
            [dict(r) for r in rx_rows],
            title=f"처방전 — {student_name} ({wrong_dt})",
            include_source=True,
            overrides={},
            subtitle=rx_subtitle,
        )
        st.download_button(
            "처방전 PDF 다운로드",
            data=pdf_data,
            file_name=f"prescription_{student_name}_{wrong_dt}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"PDF 생성 실패: {type(e).__name__}: {e}")

    st.markdown("**인출 3문항 (자동 추출)**")
    for qid in similar_qids:
        meta = query(
            "SELECT school, question_number, difficulty FROM questions WHERE question_id = ?",
            (qid,),
        )[0]
        st.caption(
            f"· id={qid} · [{meta['school']}] {meta['question_number']}번 · 난이도 {meta['difficulty']}"
        )

    st.markdown("**📅 재도전 스케줄**")
    st.markdown(
        f"- D+3 ({schedule['d3']})  ☐\n"
        f"- D+7 ({schedule['d7']})  ☐\n"
        f"- D+14 ({schedule['d14']})  ☐\n"
        f"- D+30 ({schedule['d30']})  ☐"
    )

# ── 하단: 미해결 재도전 ─────────────────────────────────
st.divider()
st.subheader("⏰ 오늘 도래한 재도전 (학생 전체)")
pendings = list_pending_retries(get_conn())
if pendings:
    for p in pendings[:20]:
        flags = []
        if p["retry_d3_status"] == "pending":
            flags.append("D+3")
        if p["retry_d7_status"] == "pending":
            flags.append("D+7")
        if p["retry_d14_status"] == "pending":
            flags.append("D+14")
        if p["retry_d30_status"] == "pending":
            flags.append("D+30")
        qref = (f"q={p['wrong_question_id']}"
                if p.get("wrong_question_id")
                else f"외부 · {p.get('external_label') or '-'}")
        st.caption(
            f"· {p['student_name']} · 오답 {qref} ({p['wrong_date']}) "
            f"· 오류 {p['error_code']} · 미완료: {', '.join(flags)}"
        )
else:
    st.info("도래한 재도전이 없습니다.")
