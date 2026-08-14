"""검수(데이터 무결성) 서비스 — app/pages/5_검수.py 의 스캔·자동복구 로직 그대로.

HWP_TOKEN_REFERENCE/HWP_TOKEN_PATTERNS/lookup_token()/_is_geometry_label()은
원본과 100% 동일 로직. scripts/ 의 순수 함수(extract_bare_words, fix_text류)를
그대로 재사용한다.
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

from . import db_service

_ROOT_DIR = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _ROOT_DIR / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

HISTORY_DIR = _ROOT_DIR / "output" / "audit_history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────
# HWP 토큰 → LaTeX 사전 (app/pages/5_검수.py 그대로)
# ─────────────────────────────────────────────────────────
HWP_TOKEN_REFERENCE = {
    "over": ("map", r"\frac"),
    "OVER": ("map", r"\frac"),
    "sqrt": ("map", r"\sqrt"),
    "root": ("map", r"\sqrt"),
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
    "leq": ("map", r"\leq"), "LEQ": ("map", r"\leq"),
    "LE": ("map", r"\leq"),
    "geq": ("map", r"\geq"), "GEQ": ("map", r"\geq"),
    "GE": ("map", r"\geq"),
    "neq": ("map", r"\neq"), "NEQ": ("map", r"\neq"),
    "NE": ("map", r"\neq"),
    "approx": ("map", r"\approx"), "APPROX": ("map", r"\approx"),
    "equiv": ("map", r"\equiv"), "EQUIV": ("map", r"\equiv"),
    "sim": ("map", r"\sim"), "SIM": ("map", r"\sim"),
    "pm": ("map", r"\pm"), "PM": ("map", r"\pm"),
    "mp": ("map", r"\mp"), "MP": ("map", r"\mp"),
    "times": ("map", r"\times"), "TIMES": ("map", r"\times"),
    "cdot": ("map", r"\cdot"), "CDOT": ("map", r"\cdot"),
    "div": ("map", r"\div"), "DIV": ("map", r"\div"),
    "divide": ("map", r"\div"), "DIVIDE": ("map", r"\div"),
    "in": ("map", r"\in"), "IN": ("map", r"\in"),
    "notin": ("map", r"\notin"), "NOTIN": ("map", r"\notin"),
    "subset": ("map", r"\subset"), "SUBSET": ("map", r"\subset"),
    "supset": ("map", r"\supset"), "SUPSET": ("map", r"\supset"),
    "cup": ("map", r"\cup"), "CUP": ("map", r"\cup"),
    "cap": ("map", r"\cap"), "CAP": ("map", r"\cap"),
    "SMALLINTER": ("map", r"\cap"),
    "SMALLUNION": ("map", r"\cup"),
    "emptyset": ("map", r"\emptyset"),
    "circ": ("map", r"\circ"), "CIRC": ("map", r"\circ"),
    "triangle": ("map", r"\triangle"),
    "angle": ("map", r"\angle"), "ANGLE": ("map", r"\angle"),
    "perp": ("map", r"\perp"), "PERP": ("map", r"\perp"),
    "parallel": ("map", r"\parallel"),
    "bigcirc": ("map", r"\bigcirc"), "BIGCIRC": ("map", r"\bigcirc"),
    "Box": ("map", r"\square"),
    "forall": ("map", r"\forall"), "FORALL": ("map", r"\forall"),
    "exists": ("map", r"\exists"), "EXISTS": ("map", r"\exists"),
    "sum": ("map", r"\sum"), "SUM": ("map", r"\sum"),
    "prod": ("map", r"\prod"), "PROD": ("map", r"\prod"),
    "int": ("map", r"\int"), "INT": ("map", r"\int"),
    "partial": ("map", r"\partial"),
    "nabla": ("map", r"\nabla"),
    "cdots": ("map", r"\cdots"), "CDOTS": ("map", r"\cdots"),
    "ldots": ("map", r"\ldots"), "LDOTS": ("map", r"\ldots"),
    "vdots": ("map", r"\vdots"),
    "ddots": ("map", r"\ddots"),
    "rarrow": ("map", r"\rightarrow"),
    "RARROW": ("map", r"\rightarrow"),
    "larrow": ("map", r"\leftarrow"),
    "LARROW": ("map", r"\leftarrow"),
    "lrarrow": ("map", r"\leftrightarrow"),
    "LRARROW": ("map", r"\leftrightarrow"),
    "RIGHTARROW": ("map", r"\rightarrow"),
    "LEFTARROW": ("map", r"\leftarrow"),
    "therefore": ("map", r"\therefore"),
    "THEREFORE": ("map", r"\therefore"),
    "because": ("map", r"\because"),
    "BECAUSE": ("map", r"\because"),
    "infty": ("map", r"\infty"), "INFTY": ("map", r"\infty"),
    "bold": ("remove", ""),
    "BOLD": ("remove", ""),
    "IT": ("remove", ""),
    "it": ("remove", ""),
    "RM": ("remove", ""),
    "rm": ("remove", ""),
    "ITALIC": ("remove", ""),
    "uparrow": ("map", r"\uparrow"),
    "UPARROW": ("map", r"\uparrow"),
    "downarrow": ("map", r"\downarrow"),
    "DOWNARROW": ("map", r"\downarrow"),
    "updownarrow": ("map", r"\updownarrow"),
    "Uparrow": ("map", r"\Uparrow"),
    "Downarrow": ("map", r"\Downarrow"),
    "NSUBSET": ("map", r"\not\subset"),
    "nsubset": ("map", r"\not\subset"),
    "NSUPSET": ("map", r"\not\supset"),
    "SUPERSET": ("map", r"\supset"),
    "superset": ("map", r"\supset"),
    "SUBSETEQ": ("map", r"\subseteq"),
    "subseteq": ("map", r"\subseteq"),
    "SUPSETEQ": ("map", r"\supseteq"),
    "supseteq": ("map", r"\supseteq"),
    "dyad": ("map", r"\overrightarrow"),
    "DYAD": ("map", r"\overrightarrow"),
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

_GREEK_LOWER = ("alpha", "beta", "gamma", "delta", "epsilon", "zeta",
                "eta", "theta", "iota", "kappa", "lambda", "mu",
                "nu", "xi", "omicron", "pi", "rho", "sigma", "tau",
                "upsilon", "phi", "chi", "psi", "omega")
_GREEK_PAT = "|".join(_GREEK_LOWER)

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
    (re.compile(rf"^({'|'.join(_SET_OPS)})([A-Z])$"),
     lambda m: ("map", f"\\{_SET_OPS_MAP[m.group(1)]} {m.group(2)}")),
    (re.compile(r"^[Pp]rime([A-Z])$"),
     lambda m: ("map", f"{m.group(1)}'")),
    (re.compile(rf"^({_TRIG_LOG_PAT})({_GREEK_PAT})$"),
     lambda m: ("map", f"\\{m.group(1)}\\{m.group(2)}")),
    (re.compile(rf"^({_TRIG_LOG_PAT})([a-zA-Z])$"),
     lambda m: ("map", f"\\{m.group(1)} {m.group(2)}")),
    (re.compile(rf"^({_GREEK_PAT})([a-zA-Z])$"),
     lambda m: ("map", f"\\{m.group(1)} {m.group(2)}")),
    (re.compile(r"^(IT|RM|it|rm|bold|BOLD|big|BIG)([a-zA-Z]+)$"),
     lambda m: ("map", m.group(2))),
]


def lookup_token(token: str):
    if token in HWP_TOKEN_REFERENCE:
        return HWP_TOKEN_REFERENCE[token]
    for pat, fn in HWP_TOKEN_PATTERNS:
        m = pat.match(token)
        if m:
            return fn(m)
    return (None, "")


def is_geometry_label(token: str) -> bool:
    if not (2 <= len(token) <= 6):
        return False
    if re.fullmatch(r"[A-Z]{2,6}", token):
        return True
    if re.fullmatch(r"[a-z]{2,6}", token):
        vowels = sum(1 for c in token if c in "aeiou")
        if 1 <= vowels <= len(token) - 1 and len(token) >= 4:
            return False
        return True
    return False


# ─────────────────────────────────────────────────────────
# 히스토리 (베이스라인)
# ─────────────────────────────────────────────────────────
def load_last_run() -> dict:
    files = sorted(HISTORY_DIR.glob("audit_*.json"), reverse=True)
    if not files:
        return {}
    try:
        return json.loads(files[0].read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_run(bare_words: list, box_mismatch: int, code_block: int) -> None:
    fname = HISTORY_DIR / f"audit_{datetime.now():%Y%m%d_%H%M%S}.json"
    fname.write_text(
        json.dumps(
            {
                "timestamp": datetime.now().isoformat(),
                "bare_words": bare_words,
                "box_mismatch": box_mismatch,
                "code_block": code_block,
            },
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )


# ─────────────────────────────────────────────────────────
# 스캔 (TTL 캐시 — main.py:283/322 의 @st.cache_data(ttl=1800) 와 동등)
# ─────────────────────────────────────────────────────────
_SCAN_TTL = 1800
_bare_words_cache: tuple[float, list] | None = None
_struct_cache: tuple[float, dict] | None = None


def _run_bare_word_detection(min_len: int = 3) -> list:
    from detect_bare_math_words import extract_bare_words, KNOWN_TOKENS, COMMON_VARS

    conn = db_service.get_dedicated_connection()
    try:
        qrows = conn.execute("SELECT question_text FROM questions").fetchall()
        srows = conn.execute("SELECT solution_text FROM solutions").fetchall()

        total = Counter()
        for r in qrows:
            total.update(extract_bare_words(r[0] or "", min_len))
        for r in srows:
            total.update(extract_bare_words(r[0] or "", min_len))

        user_tokens = set()
        try:
            rows = conn.execute("SELECT token FROM user_token_mappings").fetchall()
            user_tokens = {r[0] for r in rows}
        except Exception:
            pass
    finally:
        db_service.close_dedicated_connection(conn)

    for w in list(total.keys()):
        if w in KNOWN_TOKENS or w.lower() in KNOWN_TOKENS or w.upper() in KNOWN_TOKENS:
            del total[w]
        elif w in COMMON_VARS:
            del total[w]
        elif w in user_tokens:
            del total[w]

    return total.most_common()


def _run_structural_scan() -> dict:
    conn = db_service.get_dedicated_connection()
    try:
        rows = conn.execute("SELECT question_id, question_text FROM questions").fetchall()
    finally:
        db_service.close_dedicated_connection(conn)

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
        "code_block": len(code_block_ids),
        "total_questions": len(rows),
    }


def get_scan(force: bool = False) -> dict:
    global _bare_words_cache, _struct_cache
    now = time.time()

    if force or _bare_words_cache is None or now - _bare_words_cache[0] >= _SCAN_TTL:
        _bare_words_cache = (now, _run_bare_word_detection())
    if force or _struct_cache is None or now - _struct_cache[0] >= _SCAN_TTL:
        _struct_cache = (now, _run_structural_scan())

    bare_words = _bare_words_cache[1]
    struct = _struct_cache[1]
    last = load_last_run()
    last_words = {w: n for w, n in (last.get("bare_words") or [])}
    new_count = sum(1 for w, _ in bare_words if w not in last_words)

    return {
        "bare_words": [
            {
                "token": w, "count": n, "is_new": w not in last_words,
                "recommend_action": lookup_token(w)[0],
                "recommend_latex": lookup_token(w)[1],
                "is_geometry_label": is_geometry_label(w),
            }
            for w, n in bare_words
        ],
        "new_count": new_count,
        "struct": struct,
        "has_baseline": bool(last),
    }


def save_baseline() -> None:
    """현재 캐시된 스캔 결과를 베이스라인으로 저장."""
    if _bare_words_cache is None or _struct_cache is None:
        get_scan()
    bare_words = _bare_words_cache[1]
    struct = _struct_cache[1]
    save_run(bare_words, struct["box_mismatch"], struct["code_block"])


def force_rescan() -> None:
    global _bare_words_cache, _struct_cache
    _bare_words_cache = None
    _struct_cache = None


# ─────────────────────────────────────────────────────────
# 자동 처리
# ─────────────────────────────────────────────────────────
def _exec_write(conn, sql, params=()):
    conn.execute(sql, params)
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass


def _strip_leading_tabs_outside_box(text: str) -> str:
    if not text:
        return text
    parts = re.split(r"(<<BOX_START>>.*?<<BOX_END>>)", text, flags=re.S)
    out = []
    for part in parts:
        if part.startswith("<<BOX_START>>"):
            out.append(part)
        else:
            part = "\n".join(re.sub(r"^[\t ]+", "", ln) for ln in part.split("\n"))
            out.append(part)
    return "".join(out)


def _batch_update(conn, table: str, idcol: str, txtcol: str,
                  updates: list, *, jsonb: bool = False) -> int:
    if not updates:
        return 0
    if hasattr(conn, "_conn") and hasattr(conn._conn, "cursor"):
        from psycopg2.extras import execute_values
        cur = conn._conn.cursor()
        cast = "::jsonb" if jsonb else ""
        execute_values(
            cur,
            f"UPDATE {table} SET {txtcol} = data.t{cast} "
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


def _choices_to_list(raw):
    if raw is None:
        return None
    if isinstance(raw, (list, dict)):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def _apply_to_choices(raw, text_fixer):
    choices = _choices_to_list(raw)
    if not choices:
        return None, False
    changed = False
    new_list = []
    for c in choices:
        if not isinstance(c, dict):
            new_list.append(c)
            continue
        txt = c.get("text") or ""
        new_txt = text_fixer(txt)
        if new_txt != txt:
            changed = True
        new_c = dict(c)
        new_c["text"] = new_txt
        new_list.append(new_c)
    if not changed:
        return None, False
    return json.dumps(new_list, ensure_ascii=False), True


def _fix_one_question(conn, qid: int, q_text: str, choices_raw,
                      fix_nested, fix_tokens) -> tuple[bool, bool]:
    q_changed = False
    if q_text:
        new_q = fix_tokens(fix_nested(q_text))
        if new_q != q_text:
            _exec_write(
                conn, "UPDATE questions SET question_text=? WHERE question_id=?",
                (new_q, qid),
            )
            q_changed = True
    new_choices, ch_changed = _apply_to_choices(
        choices_raw, lambda t: fix_tokens(fix_nested(t))
    )
    if ch_changed:
        if hasattr(conn, "_conn") and hasattr(conn._conn, "cursor"):
            cur = conn._conn.cursor()
            cur.execute(
                "UPDATE questions SET choices=%s::jsonb WHERE question_id=%s",
                (new_choices, qid),
            )
            try:
                conn._conn.commit()
            except Exception:
                pass
        else:
            _exec_write(
                conn, "UPDATE questions SET choices=? WHERE question_id=?",
                (new_choices, qid),
            )
    return q_changed, ch_changed


def auto_fix_structural() -> dict:
    from fix_nested_boxes import fix_text as fix_nested
    from fix_unmapped_hwp_tokens import fix_text as fix_tokens

    conn = db_service.get_dedicated_connection()
    try:
        q_updates = []
        ch_updates = []
        rows = conn.execute(
            "SELECT question_id, question_text, choices FROM questions"
        ).fetchall()
        for r in rows:
            qid, txt, ch_raw = r[0], r[1], r[2]
            if txt:
                new = fix_nested(txt)
                new = fix_tokens(new)
                new = _strip_leading_tabs_outside_box(new)
                if new != txt:
                    q_updates.append((qid, new))
            new_ch, ch_changed = _apply_to_choices(
                ch_raw, lambda t: fix_tokens(fix_nested(t))
            )
            if ch_changed:
                ch_updates.append((qid, new_ch))

        s_updates = []
        rows = conn.execute("SELECT solution_id, solution_text FROM solutions").fetchall()
        for r in rows:
            sid, txt = r[0], r[1]
            if not txt:
                continue
            new = fix_nested(txt)
            new = fix_tokens(new)
            new = _strip_leading_tabs_outside_box(new)
            if new != txt:
                s_updates.append((sid, new))

        n_q = _batch_update(conn, "questions", "question_id", "question_text", q_updates)
        n_s = _batch_update(conn, "solutions", "solution_id", "solution_text", s_updates)
        n_ch = _batch_update(conn, "questions", "question_id", "choices", ch_updates, jsonb=True)
    finally:
        db_service.close_dedicated_connection(conn)

    return {"questions_fixed": n_q, "solutions_fixed": n_s, "choices_fixed": n_ch}


def _apply_mappings_bulk(tokens_actions: dict) -> dict:
    """여러 토큰을 한 번의 테이블 스캔으로 일괄 치환.

    토큰마다 apply_user_mapping()을 반복 호출하면 토큰 수 × (questions+solutions+choices)
    LIKE 전체 스캔이 되어, 원격 Postgres 에서는 토큰 수십~수백 개만 되어도 수 분~수십 분이
    걸려 사실상 요청이 응답하지 않는 것처럼 보인다 (로컬 SQLite 기준 토큰당 약 1초).
    전체 로우를 테이블당 딱 한 번만 읽어, 모든 토큰을 하나의 정규식으로 동시에 치환한다
    (auto_fix_structural()과 동일한 단일 스캔 패턴).
    tokens_actions: {token: (action, latex)}
    """
    conn = db_service.get_dedicated_connection()
    try:
        all_tokens = list(tokens_actions.keys())
        if all_tokens:
            placeholders = ",".join("?" * len(all_tokens))
            try:
                conn.execute(
                    f"DELETE FROM user_token_mappings WHERE token IN ({placeholders})",
                    tuple(all_tokens),
                )
            except Exception:
                pass
            values_sql = ",".join(["(?, ?, ?)"] * len(all_tokens))
            params = []
            for t in all_tokens:
                action, latex = tokens_actions[t]
                params += [t, action, latex if action == "map" else ""]
            _exec_write(
                conn,
                f"INSERT INTO user_token_mappings (token, action, latex) VALUES {values_sql}",
                tuple(params),
            )

        to_sub = {
            t: (a, latex if a == "map" else "")
            for t, (a, latex) in tokens_actions.items() if a in ("map", "remove")
        }
        if not to_sub:
            return {"affected_total": 0}

        alternation = "|".join(re.escape(t) for t in sorted(to_sub, key=len, reverse=True))
        pattern = re.compile(rf"(?<![A-Za-z\\])({alternation})(?![A-Za-z])")

        def _sub(text: str) -> str:
            return pattern.sub(lambda m: to_sub[m.group(1)][1], text)

        q_rows = conn.execute("SELECT question_id, question_text FROM questions").fetchall()
        q_updates = [
            (qid, _sub(txt)) for qid, txt in q_rows if txt and pattern.search(txt)
        ]
        n_q = _batch_update(conn, "questions", "question_id", "question_text", q_updates)

        s_rows = conn.execute("SELECT solution_id, solution_text FROM solutions").fetchall()
        s_updates = [
            (sid, _sub(txt)) for sid, txt in s_rows if txt and pattern.search(txt)
        ]
        n_s = _batch_update(conn, "solutions", "solution_id", "solution_text", s_updates)

        ch_rows = conn.execute("SELECT question_id, choices FROM questions").fetchall()
        ch_updates = []
        for qid, raw in ch_rows:
            new_ch, changed = _apply_to_choices(raw, _sub)
            if changed:
                ch_updates.append((qid, new_ch))
        n_ch = _batch_update(conn, "questions", "question_id", "choices", ch_updates, jsonb=True)

        return {"affected_total": n_q + n_s + n_ch}
    finally:
        db_service.close_dedicated_connection(conn)


def _current_bare_words() -> list:
    """캐시된 bare_words 목록 (스캔을 다시 돌리지 않고 최근 스캔 결과 재사용)."""
    if _bare_words_cache is None:
        get_scan()
    return _bare_words_cache[1]


def bulk_auto() -> dict:
    """"한 방 처리" — 사전+패턴+도형+그리스로 추천 있는 토큰 전부 자동 적용."""
    bare_words = _current_bare_words()
    tokens_actions: dict = {}
    for token, _ in bare_words:
        action, latex = lookup_token(token)
        if action is None and is_geometry_label(token):
            action, latex = "ignore", ""
        if action is None:
            continue
        tokens_actions[token] = (action, latex or "")

    result = _apply_mappings_bulk(tokens_actions)

    n_mapped = n_removed = n_ignored = 0
    mapped_examples: list[str] = []
    ignored_examples: list[str] = []
    for token, (action, latex) in tokens_actions.items():
        if action == "map":
            n_mapped += 1
            if len(mapped_examples) < 5:
                mapped_examples.append(f"{token} → {latex}")
        elif action == "remove":
            n_removed += 1
        else:
            n_ignored += 1
            if len(ignored_examples) < 5:
                ignored_examples.append(token)

    total_done = n_mapped + n_removed + n_ignored
    remaining = max(0, len(bare_words) - total_done)
    return {
        "mapped": n_mapped, "removed": n_removed, "ignored": n_ignored,
        "affected_total": result["affected_total"], "remaining": remaining,
        "mapped_examples": mapped_examples, "ignored_examples": ignored_examples,
    }


def bulk_manual(items: list[dict]) -> dict:
    """미상 dropdown 일괄 적용 — action이 '선택'이 아니고 (map 이면 latex 필수)인 항목만."""
    bare_words = _current_bare_words()
    tokens_actions: dict = {}
    for it in items:
        action = it.get("action")
        if not action or action == "선택":
            continue
        latex = (it.get("latex") or "").strip()
        if action == "map" and not latex:
            continue
        tokens_actions[it["token"]] = (action, latex)

    result = _apply_mappings_bulk(tokens_actions)
    n_done = len(tokens_actions)
    remaining = max(0, len(bare_words) - n_done)
    return {"done": n_done, "affected": result["affected_total"], "remaining": remaining}


def ignore_tokens_bulk(tokens: list[str]) -> int:
    """남은 미상 토큰 전체를 한 번에 ignore 처리 (배치 SQL 1회)."""
    if not tokens:
        return 0
    conn = db_service.get_connection()
    placeholders = ",".join("?" * len(tokens))
    try:
        conn.execute(
            f"DELETE FROM user_token_mappings WHERE token IN ({placeholders})",
            tuple(tokens),
        )
    except Exception:
        pass
    values_sql = ",".join(["(?, ?, ?)"] * len(tokens))
    params = []
    for t in tokens:
        params += [t, "ignore", ""]
    _exec_write(
        conn,
        f"INSERT INTO user_token_mappings (token, action, latex) VALUES {values_sql}",
        tuple(params),
    )
    return len(tokens)


# ─────────────────────────────────────────────────────────
# 신고함
# ─────────────────────────────────────────────────────────
def _iso(v):
    return v.isoformat() if hasattr(v, "isoformat") else v


def list_flagged() -> list[dict]:
    conn = db_service.get_connection()
    rows = conn.execute(
        "SELECT f.flag_id, f.question_id, f.flagged_at, f.reason, "
        "       q.school, q.year, q.semester, q.exam_type, q.question_number, "
        "       q.chapter, q.question_text "
        "FROM flagged_problems f "
        "JOIN questions q ON f.question_id = q.question_id "
        "WHERE f.resolved = 0 "
        "ORDER BY f.flagged_at DESC"
    ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["flagged_at"] = _iso(d["flagged_at"])
        out.append(d)
    return out


def fix_flagged_one(flag_id: int) -> None:
    from fix_nested_boxes import fix_text as fix_nested
    from fix_unmapped_hwp_tokens import fix_text as fix_tokens

    conn = db_service.get_connection()
    row = conn.execute(
        "SELECT f.question_id, q.question_text, q.choices "
        "FROM flagged_problems f JOIN questions q ON f.question_id = q.question_id "
        "WHERE f.flag_id = ?",
        (flag_id,),
    ).fetchone()
    if not row:
        return
    _fix_one_question(
        conn, row["question_id"], row["question_text"] or "", row["choices"],
        fix_nested, fix_tokens,
    )


def resolve_flagged(flag_id: int) -> None:
    conn = db_service.get_connection()
    _exec_write(conn, "UPDATE flagged_problems SET resolved=1 WHERE flag_id=?", (flag_id,))


def fix_all_flagged() -> dict:
    from fix_nested_boxes import fix_text as fix_nested
    from fix_unmapped_hwp_tokens import fix_text as fix_tokens

    conn = db_service.get_connection()
    rows = conn.execute(
        "SELECT f.flag_id, f.question_id, q.question_text, q.choices "
        "FROM flagged_problems f JOIN questions q ON f.question_id = q.question_id "
        "WHERE f.resolved = 0"
    ).fetchall()
    n_fixed = 0
    n_failed = 0
    for r in rows:
        try:
            _fix_one_question(
                conn, r["question_id"], r["question_text"] or "", r["choices"],
                fix_nested, fix_tokens,
            )
            _exec_write(
                conn, "UPDATE flagged_problems SET resolved=1 WHERE flag_id=?",
                (r["flag_id"],),
            )
            n_fixed += 1
        except Exception:
            n_failed += 1
    return {"fixed": n_fixed, "failed": n_failed}
