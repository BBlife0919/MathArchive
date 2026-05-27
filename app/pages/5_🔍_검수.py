"""검수 페이지 — DB 품질 자동 진단 + 1클릭 처리.

이 페이지에서 모든 처리 가능. 사용자는 메시지 보낼 필요 없음.
- 누락 토큰 → 토큰별 dropdown으로 매핑/제거/무시 → 적용 버튼
- 구조 오류 → 자동 복구 버튼
- 신고함 → 처리완료 / 재파싱 버튼
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from db import get_connection as _get_db_connection

SCRIPTS_DIR = APP_DIR.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# ─────────────────────────────────────────────────────────
# HWP 토큰 → LaTeX 사전 (사용자가 매번 검색 안 해도 되게)
# ─────────────────────────────────────────────────────────
# action: 'map' (LaTeX 치환) / 'remove' (스타일 토글, 제거)
HWP_TOKEN_REFERENCE = {
    # 분수/근호
    "over": ("map", r"\frac"),
    "OVER": ("map", r"\frac"),
    "sqrt": ("map", r"\sqrt"),
    "root": ("map", r"\sqrt"),
    # 위/아래 데코
    "bar": ("map", r"\overline"),
    "BAR": ("map", r"\overline"),
    "hat": ("map", r"\hat"),
    "dot": ("map", r"\dot"),
    "tilde": ("map", r"\tilde"),
    "vec": ("map", r"\vec"),
    "under": ("map", r"\underline"),
    "UNDER": ("map", r"\underline"),
    "underbrace": ("map", r"\underbrace"),
    "UNDERBRACE": ("map", r"\underbrace"),
    "overbrace": ("map", r"\overbrace"),
    "OVERBRACE": ("map", r"\overbrace"),
    # 비교 연산자
    "leq": ("map", r"\leq"), "LEQ": ("map", r"\leq"),
    "LE": ("map", r"\leq"),
    "geq": ("map", r"\geq"), "GEQ": ("map", r"\geq"),
    "GE": ("map", r"\geq"),
    "neq": ("map", r"\neq"), "NEQ": ("map", r"\neq"),
    "NE": ("map", r"\neq"),
    "approx": ("map", r"\approx"), "APPROX": ("map", r"\approx"),
    "equiv": ("map", r"\equiv"), "EQUIV": ("map", r"\equiv"),
    "sim": ("map", r"\sim"), "SIM": ("map", r"\sim"),
    # 연산
    "pm": ("map", r"\pm"), "PM": ("map", r"\pm"),
    "mp": ("map", r"\mp"), "MP": ("map", r"\mp"),
    "times": ("map", r"\times"), "TIMES": ("map", r"\times"),
    "cdot": ("map", r"\cdot"), "CDOT": ("map", r"\cdot"),
    "div": ("map", r"\div"), "DIV": ("map", r"\div"),
    "divide": ("map", r"\div"), "DIVIDE": ("map", r"\div"),
    # 집합/원소
    "in": ("map", r"\in"), "IN": ("map", r"\in"),
    "notin": ("map", r"\notin"), "NOTIN": ("map", r"\notin"),
    "subset": ("map", r"\subset"), "SUBSET": ("map", r"\subset"),
    "supset": ("map", r"\supset"), "SUPSET": ("map", r"\supset"),
    "cup": ("map", r"\cup"), "CUP": ("map", r"\cup"),
    "cap": ("map", r"\cap"), "CAP": ("map", r"\cap"),
    "SMALLINTER": ("map", r"\cap"),
    "SMALLUNION": ("map", r"\cup"),
    "emptyset": ("map", r"\emptyset"),
    # 도형
    "circ": ("map", r"\circ"), "CIRC": ("map", r"\circ"),
    "triangle": ("map", r"\triangle"),
    "angle": ("map", r"\angle"), "ANGLE": ("map", r"\angle"),
    "perp": ("map", r"\perp"), "PERP": ("map", r"\perp"),
    "parallel": ("map", r"\parallel"),
    "bigcirc": ("map", r"\bigcirc"), "BIGCIRC": ("map", r"\bigcirc"),
    "Box": ("map", r"\square"),
    # 양화사·총합
    "forall": ("map", r"\forall"), "FORALL": ("map", r"\forall"),
    "exists": ("map", r"\exists"), "EXISTS": ("map", r"\exists"),
    "sum": ("map", r"\sum"), "SUM": ("map", r"\sum"),
    "prod": ("map", r"\prod"), "PROD": ("map", r"\prod"),
    "int": ("map", r"\int"), "INT": ("map", r"\int"),
    "partial": ("map", r"\partial"),
    "nabla": ("map", r"\nabla"),
    # 점선
    "cdots": ("map", r"\cdots"), "CDOTS": ("map", r"\cdots"),
    "ldots": ("map", r"\ldots"), "LDOTS": ("map", r"\ldots"),
    "vdots": ("map", r"\vdots"),
    "ddots": ("map", r"\ddots"),
    # 화살표
    "rarrow": ("map", r"\rightarrow"),
    "RARROW": ("map", r"\rightarrow"),
    "larrow": ("map", r"\leftarrow"),
    "LARROW": ("map", r"\leftarrow"),
    "lrarrow": ("map", r"\leftrightarrow"),
    "LRARROW": ("map", r"\leftrightarrow"),
    "RIGHTARROW": ("map", r"\rightarrow"),
    "LEFTARROW": ("map", r"\leftarrow"),
    # 추론 기호
    "therefore": ("map", r"\therefore"),
    "THEREFORE": ("map", r"\therefore"),
    "because": ("map", r"\because"),
    "BECAUSE": ("map", r"\because"),
    # 무한
    "infty": ("map", r"\infty"), "INFTY": ("map", r"\infty"),
    # HWP 스타일 토글 (의미 없음, 제거)
    "bold": ("remove", ""),
    "BOLD": ("remove", ""),
    "IT": ("remove", ""),
    "it": ("remove", ""),
    "RM": ("remove", ""),
    "rm": ("remove", ""),
    "ITALIC": ("remove", ""),
    # 화살표 추가
    "uparrow": ("map", r"\uparrow"),
    "UPARROW": ("map", r"\uparrow"),
    "downarrow": ("map", r"\downarrow"),
    "DOWNARROW": ("map", r"\downarrow"),
    "updownarrow": ("map", r"\updownarrow"),
    "Uparrow": ("map", r"\Uparrow"),
    "Downarrow": ("map", r"\Downarrow"),
    # 집합 부정/포함
    "NSUBSET": ("map", r"\not\subset"),
    "nsubset": ("map", r"\not\subset"),
    "NSUPSET": ("map", r"\not\supset"),
    "SUPERSET": ("map", r"\supset"),
    "superset": ("map", r"\supset"),
    "SUBSETEQ": ("map", r"\subseteq"),
    "subseteq": ("map", r"\subseteq"),
    "SUPSETEQ": ("map", r"\supseteq"),
    "supseteq": ("map", r"\supseteq"),
    # HWP 벡터 표기 — `dyad{AD}` 는 `AD` 위에 → 화살표 그리는 의미
    # 텐서곱(\otimes) 아님!
    "dyad": ("map", r"\overrightarrow"),
    "DYAD": ("map", r"\overrightarrow"),
    # 2026-05 대규모 적재 후 새로 발견된 토큰
    "ANG": ("map", r"\angle"),
    "TRIANG": ("map", r"\triangle"),
    "SMALLPROD": ("map", r"\prod"),
    "smallprod": ("map", r"\prod"),
    "ARROW": ("map", r"\rightarrow"),
    "arrow": ("map", r"\rightarrow"),
    "SEARROW": ("map", r"\searrow"),
    "searrow": ("map", r"\searrow"),
    "NEARROW": ("map", r"\nearrow"),
    "SWARROW": ("map", r"\swarrow"),
    "NWARROW": ("map", r"\nwarrow"),
    "big": ("remove", ""),
    "BIG": ("remove", ""),
    "Big": ("remove", ""),
}


# ─────────────────────────────────────────────────────────
# 패턴 인식기 — `inA`, `primeB`, `alphax` 등 부착 케이스
# ─────────────────────────────────────────────────────────
_GREEK_LOWER = ("alpha", "beta", "gamma", "delta", "epsilon", "zeta",
                "eta", "theta", "iota", "kappa", "lambda", "mu",
                "nu", "xi", "omicron", "pi", "rho", "sigma", "tau",
                "upsilon", "phi", "chi", "psi", "omega")
_GREEK_PAT = "|".join(_GREEK_LOWER)

# 그리스 문자 단독 토큰 → LaTeX 매핑 (안전 휴리스틱 #2)
# 대문자 시작은 LaTeX 에 \Gamma 형태로 존재하는 것만 매핑, 나머지는
# 소문자 LaTeX(=라틴 알파벳과 형태가 같은 경우)으로 fallback.
_GREEK_UPPERCASE_LATEX = {
    "gamma": "Gamma", "delta": "Delta", "theta": "Theta",
    "lambda": "Lambda", "xi": "Xi", "pi": "Pi", "sigma": "Sigma",
    "upsilon": "Upsilon", "phi": "Phi", "psi": "Psi", "omega": "Omega",
}
for _greek in _GREEK_LOWER:
    HWP_TOKEN_REFERENCE.setdefault(_greek, ("map", f"\\{_greek}"))
    HWP_TOKEN_REFERENCE.setdefault(_greek.upper(), ("map", f"\\{_greek}"))
    _cap_latex = _GREEK_UPPERCASE_LATEX.get(_greek, _greek)
    HWP_TOKEN_REFERENCE.setdefault(_greek.capitalize(), ("map", f"\\{_cap_latex}"))
_SET_OPS = ("in", "IN", "notin", "NOTIN", "subset", "SUBSET",
            "supset", "SUPSET", "cup", "CUP", "cap", "CAP",
            "smallinter", "SMALLINTER", "smallunion", "SMALLUNION")
_SET_OPS_MAP = {
    "in": "in", "IN": "in", "notin": "notin", "NOTIN": "notin",
    "subset": "subset", "SUBSET": "subset",
    "supset": "supset", "SUPSET": "supset",
    "cup": "cup", "CUP": "cup", "cap": "cap", "CAP": "cap",
    "smallinter": "cap", "SMALLINTER": "cap",
    "smallunion": "cup", "SMALLUNION": "cup",
}

_TRIG_LOG = ("sin", "cos", "tan", "cot", "sec", "csc",
             "sinh", "cosh", "tanh", "log", "ln", "lim", "exp")
_TRIG_LOG_PAT = "|".join(_TRIG_LOG)

HWP_TOKEN_PATTERNS = [
    # 집합연산 + 대문자 변수: inA, smallinterB, etc.
    (re.compile(rf"^({'|'.join(_SET_OPS)})([A-Z])$"),
     lambda m: ("map", f"\\{_SET_OPS_MAP[m.group(1)]} {m.group(2)}")),
    # prime + 대문자: primeB → B'
    (re.compile(r"^[Pp]rime([A-Z])$"),
     lambda m: ("map", f"{m.group(1)}'")),
    # 삼각/로그 함수 + 그리스 (costheta, sinalpha 등) — 함수+그리스
    (re.compile(rf"^({_TRIG_LOG_PAT})({_GREEK_PAT})$"),
     lambda m: ("map", f"\\{m.group(1)}\\{m.group(2)}")),
    # 삼각/로그 함수 + 변수 (sinx, cosx, lnx, loga 등)
    (re.compile(rf"^({_TRIG_LOG_PAT})([a-zA-Z])$"),
     lambda m: ("map", f"\\{m.group(1)} {m.group(2)}")),
    # 그리스 + 영문자: alphax, pix → \alpha x, \pi x
    (re.compile(rf"^({_GREEK_PAT})([a-zA-Z])$"),
     lambda m: ("map", f"\\{m.group(1)} {m.group(2)}")),
    # IT/RM/bold + 변수: ITa → a (토글 제거)
    (re.compile(r"^(IT|RM|it|rm|bold|BOLD|big|BIG)([a-zA-Z]+)$"),
     lambda m: ("map", m.group(2))),
]


def lookup_token(token: str):
    """토큰의 권장 처리 방식. (action, latex) 반환.

    action: 'map' / 'remove' / 'ignore' / None
    """
    if token in HWP_TOKEN_REFERENCE:
        return HWP_TOKEN_REFERENCE[token]
    for pat, fn in HWP_TOKEN_PATTERNS:
        m = pat.match(token)
        if m:
            return fn(m)
    return (None, "")


st.set_page_config(page_title="검수 — MathArchive", page_icon="🔍", layout="wide")

# Auth optional
try:
    import auth
    from auth_ui import require_auth, render_user_menu_in_sidebar
    require_auth()
    if not auth.is_admin():
        st.error("⛔ 이 페이지는 관리자 전용입니다.")
        st.stop()
    render_user_menu_in_sidebar()
except ImportError:
    pass


# ─────────────────────────────────────────────────────────
# 캐시: 지난 실행 결과 저장
# ─────────────────────────────────────────────────────────
HISTORY_DIR = APP_DIR.parent / "output" / "audit_history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _load_last_run() -> dict:
    files = sorted(HISTORY_DIR.glob("audit_*.json"), reverse=True)
    if not files:
        return {}
    try:
        return json.loads(files[0].read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_run(data: dict):
    fname = HISTORY_DIR / f"audit_{datetime.now():%Y%m%d_%H%M%S}.json"
    fname.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                     encoding="utf-8")


# ─────────────────────────────────────────────────────────
# 검사 로직
# ─────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def run_bare_word_detection(min_len: int = 3) -> list:
    from detect_bare_math_words import (
        extract_bare_words, KNOWN_TOKENS, COMMON_VARS,
    )
    conn = _get_db_connection()
    qrows = conn.execute("SELECT question_text FROM questions").fetchall()
    srows = conn.execute("SELECT solution_text FROM solutions").fetchall()

    total = Counter()
    for r in qrows:
        total.update(extract_bare_words(r[0] or "", min_len))
    for r in srows:
        total.update(extract_bare_words(r[0] or "", min_len))

    # 사용자 매핑 토큰도 화이트리스트
    user_tokens = set()
    try:
        rows = conn.execute(
            "SELECT token FROM user_token_mappings"
        ).fetchall()
        user_tokens = {r[0] for r in rows}
    except Exception:
        pass

    for w in list(total.keys()):
        if w in KNOWN_TOKENS or w.lower() in KNOWN_TOKENS \
                or w.upper() in KNOWN_TOKENS:
            del total[w]
        elif w in COMMON_VARS:
            del total[w]
        elif w in user_tokens:
            del total[w]

    # 모든 토큰 반환 — 처리 후 "감춰져 있던 51번째 이후가 또 떠오르는" 사고
    # 방지를 위한 사용자 요구. 위젯 마운트 비용은 있지만 한 번에 끝낼 수 있음.
    return total.most_common()


@st.cache_data(ttl=1800)
def run_structural_scan() -> dict:
    conn = _get_db_connection()
    rows = conn.execute(
        "SELECT question_id, question_text FROM questions"
    ).fetchall()

    box_mismatch_ids = []
    code_block_ids = []

    for qid, txt in rows:
        if not txt:
            continue
        if txt.count("<<BOX_START>>") != txt.count("<<BOX_END>>"):
            box_mismatch_ids.append(qid)
        body = re.sub(r"<<BOX_START>>.*?<<BOX_END>>", "", txt, flags=re.S)
        if re.search(r"(?:^|\n)(?:\t|    )\s*\$", body):
            code_block_ids.append(qid)

    return {
        "box_mismatch": len(box_mismatch_ids),
        "box_mismatch_ids": box_mismatch_ids,
        "code_block": len(code_block_ids),
        "code_block_ids": code_block_ids,
        "total_questions": len(rows),
    }


def _exec_write(conn, sql, params=()):
    conn.execute(sql, params)
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────
# 자동 처리 함수들
# ─────────────────────────────────────────────────────────
def _strip_leading_tabs_outside_box(text: str) -> str:
    """BOX 외부 줄들의 leading tab/4-space 제거. BOX 내부는 보존
    (markdown 표는 들여쓰기 의미 없음, BOX 표는 자체 구조 보존)."""
    if not text:
        return text
    parts = re.split(r"(<<BOX_START>>.*?<<BOX_END>>)", text, flags=re.S)
    out = []
    for part in parts:
        if part.startswith("<<BOX_START>>"):
            out.append(part)
        else:
            # 줄별 leading tab/4-space 제거
            part = "\n".join(
                re.sub(r"^[\t ]+", "", ln) for ln in part.split("\n")
            )
            out.append(part)
    return "".join(out)


def _batch_update(conn, table: str, idcol: str, txtcol: str,
                  updates: list) -> int:
    """배치 UPDATE — Postgres 는 execute_values, SQLite 는 executemany.

    개별 UPDATE 1,000회 = 100~200초. 배치 = 1~5초.
    """
    if not updates:
        return 0
    # Postgres _PgConnection 래퍼 감지
    if hasattr(conn, "_conn") and hasattr(conn._conn, "cursor"):
        from psycopg2.extras import execute_values
        cur = conn._conn.cursor()
        execute_values(
            cur,
            f"UPDATE {table} SET {txtcol} = data.t "
            f"FROM (VALUES %s) AS data(id, t) "
            f"WHERE {table}.{idcol} = data.id",
            updates,
            template="(%s, %s)",
            page_size=500,
        )
        try:
            conn._conn.commit()
        except Exception:
            pass
    else:
        # SQLite — executemany 는 raw connection 에 있음
        raw = getattr(conn, "_conn", conn)
        raw.executemany(
            f"UPDATE {table} SET {txtcol}=? WHERE {idcol}=?",
            [(t, qid) for qid, t in updates],
        )
        try:
            raw.commit()
        except Exception:
            pass
    return len(updates)


def auto_fix_structural() -> dict:
    """BOX 짝/중첩/shadow + 누락 토큰 + 탭 들여쓰기 일괄 처리.

    배치 UPDATE 사용 — 90k 행을 ~10초 내 처리.
    """
    from fix_nested_boxes import fix_text as fix_nested
    from fix_unmapped_hwp_tokens import fix_text as fix_tokens

    conn = _get_db_connection()

    q_updates = []
    rows = conn.execute(
        "SELECT question_id, question_text FROM questions"
    ).fetchall()
    for r in rows:
        qid, txt = r[0], r[1]
        if not txt:
            continue
        new = fix_nested(txt)
        new = fix_tokens(new)
        new = _strip_leading_tabs_outside_box(new)
        if new != txt:
            q_updates.append((qid, new))

    s_updates = []
    rows = conn.execute(
        "SELECT solution_id, solution_text FROM solutions"
    ).fetchall()
    for r in rows:
        sid, txt = r[0], r[1]
        if not txt:
            continue
        new = fix_nested(txt)
        new = fix_tokens(new)
        new = _strip_leading_tabs_outside_box(new)
        if new != txt:
            s_updates.append((sid, new))

    n_q = _batch_update(conn, "questions", "question_id", "question_text",
                        q_updates)
    n_s = _batch_update(conn, "solutions", "solution_id", "solution_text",
                        s_updates)

    return {"questions_fixed": n_q, "solutions_fixed": n_s}


def apply_user_mapping(token: str, action: str, latex: str = "") -> dict:
    """사용자가 정의한 토큰 매핑을 DB 전체에 적용 + 매핑 저장."""
    conn = _get_db_connection()
    # 매핑 저장 (UPSERT 호환 패턴)
    try:
        conn.execute("DELETE FROM user_token_mappings WHERE token=?", (token,))
    except Exception:
        pass
    _exec_write(
        conn,
        "INSERT INTO user_token_mappings (token, action, latex) "
        "VALUES (?, ?, ?)",
        (token, action, latex),
    )

    # 적용
    if action == "ignore":
        return {"affected": 0, "note": "무시 처리 — DB 변경 없음"}

    pat = re.compile(rf"(?<![A-Za-z\\]){re.escape(token)}(?![A-Za-z])")
    repl = latex if action == "map" else ""

    # re.sub 의 replacement 인자는 \1, \g<> 같은 escape 를 해석한다.
    # \circ 같은 LaTeX 명령은 \c 가 invalid escape 로 잡혀 PatternError.
    # lambda 로 우회하면 literal 그대로 치환됨.
    def _do_sub(text):
        return pat.sub(lambda m: repl, text)

    n = 0
    for table, idcol, txtcol in [
        ("questions", "question_id", "question_text"),
        ("solutions", "solution_id", "solution_text"),
    ]:
        rows = conn.execute(
            f"SELECT {idcol}, {txtcol} FROM {table} "
            f"WHERE {txtcol} LIKE ?", (f"%{token}%",)
        ).fetchall()
        updates = []
        for r in rows:
            rid, txt = r[0], r[1]
            if not txt:
                continue
            new = _do_sub(txt)
            if new != txt:
                updates.append((rid, new))
        n += _batch_update(conn, table, idcol, txtcol, updates)
    return {"affected": n, "note": f"{action} 적용 완료"}


# ─────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────
st.title("🔍 검수")
st.caption("이 페이지에서 모든 처리 가능. 클릭 한 번이면 끝.")


def _show_result_banner(title: str, body: str, kind: str = "success"):
    """다음 rerun 에서 dialog 로 띄울 결과 메시지 저장."""
    st.session_state["audit_dialog"] = {
        "title": title, "body": body, "kind": kind,
    }


@st.dialog("처리 결과")
def _audit_result_dialog(title: str, body: str, kind: str):
    if kind == "success":
        st.success(f"### ✅ {title}")
    elif kind == "warning":
        st.warning(f"### ⚠️ {title}")
    else:
        st.info(f"### ℹ️ {title}")
    st.markdown(body)
    if st.button("확인", use_container_width=True, type="primary",
                 key="audit_dialog_close"):
        st.session_state.pop("audit_dialog", None)
        st.rerun()


# 직전 액션 결과가 있으면 페이지 진입 시 다이얼로그 자동 표시
if "audit_dialog" in st.session_state:
    _d = st.session_state["audit_dialog"]
    _audit_result_dialog(_d["title"], _d["body"], _d["kind"])

last = _load_last_run()
last_words = {w: n for w, n in (last.get("bare_words") or [])}


# ─────────────────────────────────────────────────────────
# 세션 캐시 — dropdown 변경 시 재스캔 방지
# ─────────────────────────────────────────────────────────
def _force_rescan():
    """다음 렌더에서 강제 재스캔.

    session_state 만 비우면 @st.cache_data(ttl=1800) 가 살아있어서
    옛 결과가 그대로 다시 채워짐 → 처리 후에도 화면이 안 바뀌는 사고.
    두 레이어 모두 클리어해야 함.
    """
    st.session_state.pop("audit_bare_words", None)
    st.session_state.pop("audit_struct", None)
    try:
        run_bare_word_detection.clear()
        run_structural_scan.clear()
    except Exception:
        pass


if "audit_bare_words" not in st.session_state:
    with st.spinner("⏳ DB 전체 스캔 중... (첫 진입 시 1~2분)"):
        st.session_state.audit_bare_words = run_bare_word_detection()

if "audit_struct" not in st.session_state:
    with st.spinner("⏳ 구조 무결성 검사 중..."):
        st.session_state.audit_struct = run_structural_scan()

bare_words_cached = st.session_state.audit_bare_words
struct_cached = st.session_state.audit_struct

# ─── 구조 무결성 ─────────────────────────────────────────
st.subheader("🏗 구조 무결성")
struct = struct_cached

c1, c2, c3, c4 = st.columns(4)
c1.metric("전체 문항", f"{struct['total_questions']:,}")
c2.metric("BOX 짝 어긋남", struct["box_mismatch"])
c3.metric("코드블록 오인", struct["code_block"])

with c4:
    if st.button("🔧 자동 복구",
                 disabled=struct["box_mismatch"] == 0
                          and struct["code_block"] == 0,
                 use_container_width=True):
        with st.spinner("처리 중... (5~15초)"):
            res = auto_fix_structural()
        _show_result_banner(
            "자동 복구 완료",
            f"- 문제 텍스트: **{res['questions_fixed']}건** 갱신\n"
            f"- 해설 텍스트: **{res['solutions_fixed']}건** 갱신\n\n"
            f"다음 단계: **🧠 알려진 토큰 자동 매핑** 버튼을 누르세요.",
        )
        _force_rescan()
        st.rerun()

st.divider()

# ─── 누락 토큰 ─────────────────────────────────────────
st.subheader("🔤 누락 HWP 토큰")
hdr_cols = st.columns([6, 1])
hdr_cols[0].caption("수식 안에서 백슬래시 없이 등장하는 단어. "
                    "각 행에서 처리 방식을 선택하고 [적용]을 누르세요.")
if hdr_cols[1].button("🔄 다시 스캔", use_container_width=True):
    _force_rescan()
    st.rerun()

bare_words = bare_words_cached

# 신규 표시
new_count = sum(1 for w, _ in bare_words if w not in last_words)
if new_count:
    st.warning(f"⚠️ 지난 실행 이후 새로 등장한 토큰 {new_count}개")

# 토큰별 처리 UI
ACTION_LABELS = {
    "선택": "선택...",
    "ignore": "무시 (도형 라벨/변수 등)",
    "map": "→ LaTeX로 매핑",
    "remove": "삭제 (스타일 토글 등)",
}

# 누락 토큰 _전체_ 표시 — "한 방에 다 처리" 사용자 요구.
# 위젯 mount 비용이 토큰 수에 비례하지만, 한 번 처리하고 끝낼 수 있어
# 슬라이더로 자르지 않는다.
visible_tokens = bare_words
if visible_tokens:
    st.info(f"📋 현재 누락 토큰 **{len(visible_tokens)}개** — 한 번에 처리하세요")

# 도형 라벨 자동 인식: 영문자 2~6글자 묶음 (대문자 또는 소문자만)
def _is_geometry_label(token: str) -> bool:
    if not (2 <= len(token) <= 6):
        return False
    # 대문자만 (ABP, EFGH, OPQ 등) — 100% 도형
    if re.fullmatch(r"[A-Z]{2,6}", token):
        return True
    # 소문자 변수 묶음 (xyz, abc, abi 등) — 자음모음 패턴 영어 단어 제외
    if re.fullmatch(r"[a-z]{2,6}", token):
        # 영어 단어 의심 (모음 비율로 판단): 모음 1개 이상 + 자음 1개 이상
        # 인 짧은 단어는 LaTeX 명령일 수 있어 제외
        vowels = sum(1 for c in token if c in "aeiou")
        if vowels >= 1 and vowels <= len(token) - 1 and len(token) >= 4:
            return False  # 영어 단어 가능성 — 사람 검토 필요
        return True  # xyz, ab, abc 같은 변수 묶음
    return False


# ─── 일괄 처리 툴바 ────────────────────────────────────
# 통합: 사전·패턴·도형 라벨·그리스 약어를 한 번에 처리.
# 페이지네이션과 무관하게 항상 _전체_ bare_words 를 대상으로 적용.
toolbar = st.columns([4, 3])

if toolbar[0].button("🚀 한 방 처리 (사전+패턴+도형+그리스, 전체)",
                     use_container_width=True, type="primary"):
    with st.spinner("자동 처리 중..."):
        n_mapped = 0
        n_removed = 0
        n_ignored = 0
        n_affected_total = 0
        mapped_examples: list[str] = []
        ignored_examples: list[str] = []
        for token, _ in bare_words:
            action, latex = lookup_token(token)
            # 추천 없을 때 도형 라벨이면 ignore
            if action is None and _is_geometry_label(token):
                action, latex = "ignore", ""
            if action is None:
                continue
            res = apply_user_mapping(token, action, latex or "")
            n_affected_total += res.get("affected", 0)
            if action == "map":
                n_mapped += 1
                if len(mapped_examples) < 5:
                    mapped_examples.append(f"`{token}` → `{latex}`")
            elif action == "remove":
                n_removed += 1
            else:
                n_ignored += 1
                if len(ignored_examples) < 5:
                    ignored_examples.append(f"`{token}`")
    total_done = n_mapped + n_removed + n_ignored
    remaining = max(0, len(bare_words) - total_done)
    if total_done == 0:
        _show_result_banner(
            "처리할 토큰 없음",
            "사전/패턴/도형 라벨/그리스 약어로 매칭되는 토큰이 없습니다. "
            "남은 미상 토큰은 표에서 dropdown 으로 수동 처리해주세요.",
            kind="info",
        )
        st.toast("ℹ️ 자동 처리 대상 없음")
    else:
        body = (
            f"- 매핑: **{n_mapped}개 토큰**\n"
            f"- 삭제: **{n_removed}개 토큰**\n"
            f"- 무시 (도형 라벨): **{n_ignored}개 토큰**\n"
            f"- DB 문항 변경: **{n_affected_total}건**\n"
            f"- 남은 미상 토큰: **{remaining}개**\n\n"
        )
        if mapped_examples:
            body += "**매핑 예시:** " + ", ".join(mapped_examples) + "\n\n"
        if ignored_examples:
            body += "**무시 예시:** " + ", ".join(ignored_examples) + "\n\n"
        body += (
            "다음 단계: 표에 남은 미상 토큰은 dropdown 으로 수동 처리 → "
            "**[✅ 미상 dropdown 일괄 적용]** → **[📌 베이스라인 저장]**."
        )
        _show_result_banner("한 방 처리 완료", body)
        st.toast(f"✅ {total_done}개 처리 · {remaining}개 남음")
    _force_rescan()
    st.rerun()

# 미상 dropdown 일괄 적용 — 사용자가 수동으로 선택한 처리만
if toolbar[1].button("✅ 미상 dropdown 일괄 적용",
                     use_container_width=True):
    n_done = 0
    n_affected = 0
    with st.spinner("선택 처리 적용 중..."):
        for token, _ in visible_tokens:
            action = st.session_state.get(f"act_{token}", "선택")
            if action == "선택":
                continue
            latex = st.session_state.get(f"latex_{token}", "").strip()
            if action == "map" and not latex:
                continue
            res = apply_user_mapping(token, action, latex)
            n_done += 1
            n_affected += res.get("affected", 0)
    if n_done == 0:
        _show_result_banner(
            "처리할 항목 없음",
            "dropdown 에서 처리 방식을 선택한 토큰이 없습니다.",
            kind="warning",
        )
        st.toast("⚠️ 선택된 처리가 없습니다")
    else:
        remaining = max(0, len(bare_words) - n_done)
        _show_result_banner(
            "미상 dropdown 일괄 적용 완료",
            f"- 처리 토큰: **{n_done}개**\n"
            f"- DB 변경: **{n_affected}건**\n"
            f"- 남은 미상 토큰: **{remaining}개**\n\n"
            "다음 단계: **📌 베이스라인 저장**.",
        )
        st.toast(f"✅ {n_done}개 처리 · {remaining}개 남음")
        _force_rescan()
    st.rerun()

st.caption(
    "💡 **권장 순서**: ① **[🚀 한 방 처리]** → ② 남은 미상 토큰은 표에서 "
    "dropdown 처리 → ③ **[✅ 미상 dropdown 일괄 적용]** → ④ **[📌 베이스라인 저장]**"
)

with st.expander("❓ 미상 토큰이란? · 처리 가이드"):
    st.markdown(
        """
**미상 토큰** = 사전(SYMBOL_MAP)에도 없고 패턴 인식기(영문 변수 묶음·도형 라벨 등)에도 매칭 안 된 토큰. 즉 자동으로 판단 못 한 것.

**처리 방법**:
- **수식 토큰** (수학 기호로 보이면) → 처리 방식: `→ LaTeX 로 매핑` 선택 + LaTeX 칸에 입력 (예: `\\prec`, `\\succeq`, `\\rightarrow`)
- **변수/도형 라벨** (영문자 묶음) → 처리 방식: `무시` — 검색·렌더링에 영향 없게
- **의미 없는 표시 글자** (HWP 스타일 토글 등) → 처리 방식: `삭제` — 본문에서 제거
- **모르겠으면** → 그냥 두기. 다음에 사전이 업데이트되면 자동 매핑됨

**팁**: 미상이 너무 많으면 [📌 베이스라인 저장] 후 그대로 두세요. 다음 검수 때 "새로 등장한 토큰" 만 강조됩니다.
        """
    )

st.markdown("---")

# ─── 페이지네이션 ─────────────────────────────────────
# 토큰이 많아도 스크롤이 길게 늘어지지 않게 한 페이지에 일부만 표시.
# 일괄 처리 버튼은 항상 _전체_ visible_tokens 를 대상으로 동작하므로
# 페이지네이션은 표시·미상 dropdown 수동 입력 보존용.
TOKENS_PER_PAGE = 20
total_tokens = len(visible_tokens)
total_pages = max(1, (total_tokens + TOKENS_PER_PAGE - 1) // TOKENS_PER_PAGE)
if "audit_page" not in st.session_state:
    st.session_state.audit_page = 0
if st.session_state.audit_page >= total_pages:
    st.session_state.audit_page = 0
cur_page = st.session_state.audit_page
start = cur_page * TOKENS_PER_PAGE
end = min(start + TOKENS_PER_PAGE, total_tokens)
page_tokens = visible_tokens[start:end]


def _render_token_pagination(prefix: str):
    """페이지 네비게이션 — 문항 페이지와 동일 패턴."""
    if total_pages <= 1:
        return
    if total_pages <= 7:
        page_nums = list(range(total_pages))
    else:
        pages = {0, total_pages - 1}
        for p in range(max(0, cur_page - 2),
                       min(total_pages - 1, cur_page + 2) + 1):
            pages.add(p)
        sorted_pages = sorted(pages)
        page_nums = []
        for i, p in enumerate(sorted_pages):
            if i > 0 and p - sorted_pages[i - 1] > 1:
                page_nums.append(None)
            page_nums.append(p)
    col_specs = [1] + [1] * len(page_nums) + [1]
    cols = st.columns(col_specs)
    with cols[0]:
        if st.button("◀", disabled=cur_page == 0,
                     key=f"audit_prev_{prefix}", use_container_width=True):
            st.session_state.audit_page -= 1
            st.rerun()
    for i, p in enumerate(page_nums):
        with cols[i + 1]:
            if p is None:
                st.markdown(
                    "<div style='text-align:center;padding:8px 0;"
                    "color:#a6b2d4;'>…</div>",
                    unsafe_allow_html=True,
                )
            elif p == cur_page:
                st.markdown(
                    f"<div style='text-align:center;padding:6px 0;"
                    f"border:1px solid #f0cd87;border-radius:6px;"
                    f"color:#f0cd87;font-weight:700;'>{p + 1}</div>",
                    unsafe_allow_html=True,
                )
            else:
                if st.button(str(p + 1),
                             key=f"audit_page_{prefix}_{p}",
                             use_container_width=True):
                    st.session_state.audit_page = p
                    st.rerun()
    with cols[-1]:
        if st.button("▶", disabled=cur_page >= total_pages - 1,
                     key=f"audit_next_{prefix}", use_container_width=True):
            st.session_state.audit_page += 1
            st.rerun()


st.caption(
    f"전체 {total_tokens}개 중 {start + 1 if total_tokens else 0}–{end}번 표시 "
    f"(페이지 {cur_page + 1}/{total_pages})"
)
_render_token_pagination("top")

# 헤더 — 체크박스 컬럼 제거. 한 방 처리 버튼이 추천을 자동 적용함.
hdr = st.columns([2, 1.5, 2.5, 2.8])
hdr[0].markdown("**토큰**")
hdr[1].markdown("**추천**")
hdr[2].markdown("**처리 방식 (미상 토큰만)**")
hdr[3].markdown("**LaTeX (매핑 시만)**")

for token, count in page_tokens:
    is_new = token not in last_words
    badge = " 🆕" if is_new else ""
    cols = st.columns([2, 1.5, 2.5, 2.8])
    cols[0].markdown(f"`{token}` ({count}건){badge}")

    # 추천 표시 (사전 + 패턴 인식기 모두 사용)
    rec_action, rec_latex = lookup_token(token)
    is_geo = _is_geometry_label(token)
    if rec_action == "map":
        cols[1].markdown(f"📘 `{rec_latex}`")
    elif rec_action == "remove":
        cols[1].markdown("🗑 제거")
    elif rec_action == "ignore":
        cols[1].markdown("🚫 무시")
    elif is_geo:
        cols[1].markdown("🔤 변수")
    else:
        cols[1].markdown("❓ 미상")

    has_rec = rec_action is not None or is_geo
    if has_rec:
        # 추천 있는 행: 한 방 처리 버튼이 자동 적용 → UI 단순화
        cols[2].caption("🚀 [한 방 처리]로 자동 적용")
        cols[3].caption("—")
    else:
        # 미상 행: dropdown + LaTeX 로 수동 처리
        cols[2].selectbox(
            "처리",
            options=list(ACTION_LABELS.keys()),
            format_func=lambda k: ACTION_LABELS[k],
            key=f"act_{token}",
            label_visibility="collapsed",
        )
        if st.session_state.get(f"act_{token}") == "map":
            cols[3].text_input(
                "LaTeX",
                value="",
                placeholder=r"예: \prec",
                key=f"latex_{token}",
                label_visibility="collapsed",
            )
        else:
            cols[3].caption("—")

_render_token_pagination("bot")
st.divider()

# ─── 결과 저장 ─────────────────────────────────────────
if st.button("📌 이번 결과 저장 (베이스라인 갱신)"):
    _save_run({
        "timestamp": datetime.now().isoformat(),
        "bare_words": bare_words,
        "box_mismatch": struct["box_mismatch"],
        "code_block": struct["code_block"],
    })
    _show_result_banner(
        "베이스라인 저장 완료",
        "처리된 토큰은 화이트리스트에 반영돼 새로고침 후 사라집니다. "
        "남은 토큰만 표시됩니다.",
    )
    # 캐시 비우고 재스캔 → 처리된 토큰은 user_tokens 화이트리스트로
    # 자동 제외되어 남은 토큰만 표에 보임.
    _force_rescan()
    st.rerun()

st.divider()

# ─── 신고함 ─────────────────────────────────────────
st.subheader("🚩 신고함")
st.caption("검색·시험지에서 사용자가 직접 신고한 문항.")

conn = _get_db_connection()
flagged_rows = conn.execute(
    "SELECT f.flag_id, f.question_id, f.flagged_at, f.reason, "
    "       q.school, q.year, q.semester, q.exam_type, q.question_number, "
    "       q.chapter, q.question_text "
    "FROM flagged_problems f "
    "JOIN questions q ON f.question_id = q.question_id "
    "WHERE f.resolved = 0 "
    "ORDER BY f.flagged_at DESC"
).fetchall()

st.metric("미해결 신고", len(flagged_rows))

if not flagged_rows:
    st.info("신고된 문항 없음.")
else:
    for r in flagged_rows[:20]:
        with st.container(border=True):
            cols = st.columns([4, 1, 1])
            EXAM = {"a": "중간", "b": "기말"}
            label = (
                f"**[{r['school']}]** {r['year']}년 {r['semester']}학기 "
                f"{EXAM.get(r['exam_type'], '')} {r['question_number']}번 · "
                f"`{r['chapter']}` · qid={r['question_id']}"
            )
            cols[0].markdown(label)
            cols[0].caption(f"신고일: {r['flagged_at']}")
            cols[0].code((r['question_text'] or "")[:200], language="markdown")
            if cols[1].button("자동 복구",
                              key=f"fix_one_{r['flag_id']}"):
                # 단건 자동 복구 (구조 + 토큰 + 사용자 매핑)
                from fix_nested_boxes import fix_text as fix_nested
                from fix_unmapped_hwp_tokens import fix_text as fix_tokens
                new = fix_tokens(fix_nested(r['question_text']))
                _exec_write(
                    conn,
                    "UPDATE questions SET question_text=? "
                    "WHERE question_id=?",
                    (new, r['question_id']),
                )
                st.toast("자동 복구 시도 완료. 결과 확인 후 처리완료.")
                st.rerun()
            if cols[2].button("처리완료",
                              key=f"resolve_{r['flag_id']}"):
                _exec_write(
                    conn,
                    "UPDATE flagged_problems SET resolved=1 "
                    "WHERE flag_id=?",
                    (r['flag_id'],),
                )
                st.rerun()

st.divider()

with st.expander("ℹ️ 사용법"):
    st.markdown("""
**구조 무결성**: 숫자 0이 아니면 [🔧 자동 복구] 클릭. 끝.

**누락 토큰**: 각 토큰을 보고 dropdown 선택:
- **무시**: 도형 라벨이나 변수면 (`ABP`, `xyz`, `EFGH` 등). 다음부터 안 뜸.
- **매핑**: LaTeX 명령어면 (`prec` → `\\prec` 처럼 텍스트 입력 후 적용).
- **삭제**: HWP 스타일 토글이면 (`bold`, `IT` 등 의미 없는 것).

**신고함**: 자동 복구 한 번 누르고 결과 확인. OK면 처리완료.

**저장**: 모든 처리 끝낸 후 베이스라인 갱신.
""")
