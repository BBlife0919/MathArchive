"""자동 수정 — 룰 기반 토큰 변환 추천 + 클릭 한 번 적용.

각 행마다 변환 후보를 미리 계산해서 보여주고, 사용자는 ✓ 한 번만 누르면
로컬 SQLite + 클라우드 Postgres 양쪽에 즉시 반영.
"""
from __future__ import annotations

import os
import re
import sqlite3
import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

try:
    from dotenv import load_dotenv
    load_dotenv(APP_DIR.parent / ".env")
except ImportError:
    pass

st.set_page_config(page_title="자동수정 — MathArchive",
                   page_icon="🪄", layout="wide")

# Auth
try:
    import auth
    from auth_ui import require_auth, render_user_menu_in_sidebar
    require_auth()
    if not auth.is_admin():
        st.error("⛔ 관리자 전용입니다.")
        st.stop()
    render_user_menu_in_sidebar()
except ImportError:
    pass


# ── 변환 룰 (검증된 안전 패턴) ─────────────────────────────
# 각 룰: (정규식, 치환, 설명)
RULES: list[tuple[re.Pattern, str, str]] = [
    # lim/INF/-> (수식 컨텍스트)
    (re.compile(r"(?<![A-Za-z\\])lim(?![A-Za-z])"), r"\\lim",
     "lim → \\lim"),
    (re.compile(r"(?<![A-Za-z\\])INF(?![A-Za-z])"), r"\\infty",
     "INF → \\infty"),
    (re.compile(r"(?<![A-Za-z\\])inf(?![A-Za-z])"), r"\\infty",
     "inf → \\infty"),
    (re.compile(r"\\in\s+F\b"), r"\\infty",
     "\\in F → \\infty (잘못 변환된 케이스)"),
    (re.compile(r"(?<![<=-])->"), r"\\to",
     "-> → \\to"),
    # sup 지수
    (re.compile(r"\bsup\s+(\d+)\b"), r"^{\1}",
     "sup N → ^{N}"),
    # int from to 적분
    (re.compile(r"\bint\s+from\s+(\S+)\s+to\s+(\S+)"),
     r"\\int_{\1}^{\2}", "int from A to B → \\int_A^B"),
    # vec 벡터
    (re.compile(r"\\mathrm\{vec\}\s+([A-Za-z]+)"), r"\\vec{\1}",
     "\\mathrm{vec} → \\vec{}"),
    (re.compile(r"(?<![A-Za-z\\])vec\s*(\d+)"), r"\\vec{\1}",
     "vec N → \\vec{N}"),
    (re.compile(r"(?<![A-Za-z\\])vec\s+([A-Za-z]+)"), r"\\vec{\1}",
     "vec X → \\vec{X}"),
    (re.compile(r"(?<![A-Za-z\\])vec([A-Za-z])"), r"\\vec{\1}",
     "vecX → \\vec{X}"),
    # bar overline
    (re.compile(r"(?<![A-Za-z\\])bar\{([^{}]*)\}"), r"\\overline{\1}",
     "bar{X} → \\overline{X}"),
    # dot 순환소수
    (re.compile(r"(?<![A-Za-z\\])dot\s+(\d+)"), r"\\dot{\1}",
     "dot N → \\dot{N}"),
    # notin
    (re.compile(r"(?<![A-Za-z\\])notin(?![A-Za-z])"), r"\\notin",
     "notin → \\notin"),
    (re.compile(r"(?<![A-Za-z\\])NOTIN(?![A-Za-z])"), r"\\notin",
     "NOTIN → \\notin"),
]


def apply_rules(text: str) -> tuple[str, list[str]]:
    """텍스트에 모든 룰 순차 적용. (결과, 적용된 룰 설명 목록) 반환."""
    if not text:
        return text, []
    new = text
    applied = []
    for pat, repl, desc in RULES:
        before = new
        new = pat.sub(repl, new)
        if new != before:
            applied.append(desc)
    return new, applied


# ── DB 연결 ────────────────────────────────────────────────
@st.cache_resource
def _sqlite():
    p = APP_DIR.parent / "db" / "mathdb.sqlite"
    return sqlite3.connect(str(p), check_same_thread=False)


def _pg_connect():
    import psycopg2
    return psycopg2.connect(os.environ["SUPABASE_DB_URL"])


# ── 후보 행 검색 (룰이 변경하는 행만) ──────────────────────
@st.cache_data(ttl=300)
def find_candidates(limit: int = 200) -> list[dict]:
    """questions + solutions 의 모든 행을 스캔해서 룰 적용 시 변경되는 행만 반환.

    각 행: {table, pk, col, qid(meta), before, after, applied_rules, meta_label}
    """
    conn = _sqlite()
    cur = conn.cursor()
    result = []

    # questions
    cur.execute(
        "SELECT q.question_id, q.school, q.year, q.grade, q.semester, "
        "       q.exam_type, q.question_number, q.question_text "
        "FROM questions q"
    )
    for qid, school, year, grade, sem, exam, qnum, text in cur.fetchall():
        if not text:
            continue
        new, applied = apply_rules(text)
        if new == text:
            continue
        meta = (
            f"{school or '?'} {year or '?'}-{grade or '?'}-{sem or '?'}-"
            f"{exam or '?'} {qnum}번"
        )
        result.append({
            "table": "questions", "pk": "question_id", "col": "question_text",
            "pk_value": qid, "qid_meta": qid, "meta_label": meta,
            "before": text, "after": new, "applied": applied,
        })
        if len(result) >= limit:
            return result

    # solutions
    cur.execute(
        "SELECT s.solution_id, s.question_id, q.school, q.year, q.grade, "
        "       q.semester, q.exam_type, q.question_number, s.solution_text "
        "FROM solutions s JOIN questions q ON s.question_id = q.question_id"
    )
    for sid, qid, school, year, grade, sem, exam, qnum, text in cur.fetchall():
        if not text:
            continue
        new, applied = apply_rules(text)
        if new == text:
            continue
        meta = (
            f"[해설] {school or '?'} {year or '?'}-{grade or '?'}-"
            f"{sem or '?'}-{exam or '?'} {qnum}번"
        )
        result.append({
            "table": "solutions", "pk": "solution_id", "col": "solution_text",
            "pk_value": sid, "qid_meta": qid, "meta_label": meta,
            "before": text, "after": new, "applied": applied,
        })
        if len(result) >= limit:
            return result
    return result


# ── 양쪽 DB UPDATE ─────────────────────────────────────────
def apply_to_dbs(table: str, pk: str, col: str,
                 pk_value: int, new_text: str) -> tuple[bool, str]:
    """로컬 SQLite + 클라우드 Postgres 동기 UPDATE.

    Postgres pk 는 별도 매핑 필요 — questions 는 (file_source, qnum) 기준,
    solutions 는 cloud question_id 기준. 단순화: 같은 텍스트 행이 다중일 수
    있어 cloud 에서는 (table, 매칭 텍스트) 로 UPDATE. 실패 시 로컬만 반영.
    """
    # 로컬 먼저
    sl = _sqlite()
    cur = sl.cursor()
    cur.execute(f"SELECT {col} FROM {table} WHERE {pk}=?", (pk_value,))
    row = cur.fetchone()
    if not row:
        return False, "로컬에서 행을 찾을 수 없음"
    old_text = row[0]
    cur.execute(
        f"UPDATE {table} SET {col}=? WHERE {pk}=?",
        (new_text, pk_value),
    )
    sl.commit()

    # 클라우드 — 동일 (table, col, old_text) 매칭 행 UPDATE
    try:
        pg = _pg_connect()
        pcur = pg.cursor()
        pcur.execute(
            f"UPDATE {table} SET {col} = %s WHERE {col} = %s",
            (new_text, old_text),
        )
        n = pcur.rowcount
        pg.commit()
        pg.close()
        return True, f"로컬 + 클라우드 ({n}행) 반영 완료"
    except Exception as e:
        return True, f"로컬만 반영. 클라우드 에러: {type(e).__name__}"


# ── 상태 ────────────────────────────────────────────────────
if "auto_fix_skipped" not in st.session_state:
    st.session_state["auto_fix_skipped"] = set()


# ── UI ──────────────────────────────────────────────────────
st.title("🪄 자동 수정 — 룰 기반 추천")
st.caption(
    "안전한 변환 룰을 자동 적용한 결과를 미리보기로 표시. "
    "✓ 적용 한 번에 로컬 + 클라우드 동기 반영."
)

with st.expander("🔧 적용 룰 목록", expanded=False):
    for _, _, desc in RULES:
        st.markdown(f"- {desc}")

col_a, col_b = st.columns([0.7, 0.3])
with col_a:
    page_limit = st.slider(
        "한 번에 표시할 행 수", 10, 100, 30, step=10,
    )
with col_b:
    if st.button("🔄 후보 새로 검색", use_container_width=True):
        st.cache_data.clear()
        st.session_state["auto_fix_skipped"] = set()
        st.rerun()

cands = find_candidates(limit=500)
visible = [
    c for c in cands
    if (c["table"], c["pk_value"]) not in st.session_state["auto_fix_skipped"]
]
total = len(cands)
shown = min(page_limit, len(visible))

st.markdown(
    f"**총 {total}건** (적용 가능). 이 페이지에 **{shown}건** 표시. "
    f"패스 누적 {len(st.session_state['auto_fix_skipped'])}건."
)

if total == 0:
    st.success("🎉 자동 변환 후보 0건. 모든 안전 룰이 이미 적용됨.")
    st.stop()

st.divider()

for c in visible[:shown]:
    key_base = f"{c['table']}_{c['pk_value']}"
    with st.container(border=True):
        head_c1, head_c2 = st.columns([0.7, 0.3])
        with head_c1:
            st.markdown(f"**{c['meta_label']}**")
            st.caption("적용 룰: " + " · ".join(c["applied"]))
        with head_c2:
            apply_btn = st.button(
                "✓ 적용", key=f"apply_{key_base}",
                type="primary", use_container_width=True,
            )
            skip_btn = st.button(
                "✗ 패스", key=f"skip_{key_base}",
                use_container_width=True,
            )

        st.markdown("**변환 전:**")
        st.markdown(c["before"][:800] +
                    ("..." if len(c["before"]) > 800 else ""))
        st.markdown("**변환 후:**")
        st.markdown(c["after"][:800] +
                    ("..." if len(c["after"]) > 800 else ""))

        if apply_btn:
            ok, msg = apply_to_dbs(
                c["table"], c["pk"], c["col"], c["pk_value"], c["after"],
            )
            if ok:
                st.success(msg)
                st.session_state["auto_fix_skipped"].add(
                    (c["table"], c["pk_value"]),
                )
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(msg)
        if skip_btn:
            st.session_state["auto_fix_skipped"].add(
                (c["table"], c["pk_value"]),
            )
            st.rerun()
