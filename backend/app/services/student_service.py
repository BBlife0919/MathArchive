"""학생 카드 서비스 — app/pages/2_학생카드.py 의 SQL·집계 로직을 그대로 재현.

원본은 matplotlib(레이더)/pandas(시계열 groupby 평균, 막대) 로 화면에서
직접 그렸지만, 여기서는 동일한 계산 결과를 구조화된 데이터로 반환하고
프론트(recharts)가 렌더링만 담당한다.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, timedelta

from . import db_service

import db as legacy_db  # type: ignore

# app/pages/2_학생카드.py:59-69 그대로
PRISM_LETTER = {
    "계산실수": "P",
    "조건해석실패": "R",
    "개념누락": "I",
    "전략선택실패": "S",
    "시간관리": "M",
}
PRISM_ORDER = ["계산실수", "조건해석실패", "개념누락", "전략선택실패", "시간관리"]
RIS_CODES = {"개념누락", "조건해석실패", "전략선택실패"}
PM_CODES = {"계산실수", "시간관리"}

GRADE_OPTIONS = ["A", "B", "C", "D"]


def _iso(v):
    """Postgres(psycopg2)는 DATE 컬럼을 datetime.date 객체로, SQLite 는 TEXT
    문자열로 반환한다 — 두 경우 모두 ISO 문자열로 통일."""
    return v.isoformat() if hasattr(v, "isoformat") else v


def list_students() -> list:
    return db_service.query(
        "SELECT student_id, name, school, grade, class_name, note "
        "FROM students ORDER BY school, grade, name"
    )


def create_student(name: str, school: str | None, grade: int,
                   class_name: str | None) -> int:
    """app/pages/1_클리닉.py:66-84 의 create_student() 그대로 —
    Postgres(RETURNING)/SQLite(lastrowid) 분기가 필요해 execute_write() 를
    쓰지 않고 직접 처리한다."""
    conn = db_service.get_connection()
    cloud = legacy_db.is_cloud()
    sql = "INSERT INTO students (name, school, grade, class_name) VALUES (?, ?, ?, ?)"
    if cloud:
        sql += " RETURNING student_id"
    cur = conn.execute(sql, (name, school, grade, class_name))
    if cloud:
        sid = cur.fetchone()[0]
    else:
        sid = cur.lastrowid
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    return sid


def get_student(sid: int) -> dict | None:
    return _student_basic(sid)


def _student_basic(sid: int) -> dict | None:
    rows = db_service.query(
        "SELECT student_id, name, school, grade, class_name, note "
        "FROM students WHERE student_id = ?",
        (sid,),
    )
    return dict(rows[0]) if rows else None


def _clinic_count(sid: int) -> int:
    return db_service.query(
        "SELECT COUNT(*) AS n FROM clinic_entries WHERE student_id = ?", (sid,)
    )[0]["n"]


def _latest_prism(sid: int) -> dict | None:
    rows = db_service.query(
        "SELECT eval_date, score_p, score_r, score_i, score_s, score_m, note "
        "FROM prism_assessment WHERE student_id = ? "
        "ORDER BY eval_date DESC, assessment_id DESC LIMIT 1",
        (sid,),
    )
    if not rows:
        return None
    r = dict(rows[0])
    r["eval_date"] = _iso(r["eval_date"])
    return r


def _prism_history(sid: int) -> list[dict]:
    rows = db_service.query(
        "SELECT eval_date, score_p, score_r, score_i, score_s, score_m, note "
        "FROM prism_assessment WHERE student_id = ? "
        "ORDER BY eval_date DESC LIMIT 10",
        (sid,),
    )
    out = []
    for r in rows:
        d = dict(r)
        d["eval_date"] = _iso(d["eval_date"])
        out.append(d)
    return out


def _clinic_error_distribution(sid: int) -> list[dict]:
    rows = db_service.query(
        "SELECT error_code, wrong_date FROM clinic_entries WHERE student_id = ? "
        "ORDER BY wrong_date DESC",
        (sid,),
    )
    if not rows:
        return []
    counter = Counter(r["error_code"] for r in rows)
    return [
        {
            "code": code,
            "label": f"{PRISM_LETTER[code]} · {code}",
            "count": counter.get(code, 0),
            "category": "이해" if code in RIS_CODES else "수행",
        }
        for code in PRISM_ORDER
    ]


def _self_predict(sid: int) -> dict:
    rows = db_service.query(
        "SELECT log_date, title, self_predicted, self_actual, note "
        "FROM student_progress "
        "WHERE student_id = ? AND category = '자가예측' "
        "ORDER BY log_date DESC LIMIT 10",
        (sid,),
    )
    if not rows:
        return {
            "entries": [], "chart": [], "avg_gap": None,
            "over_count": 0, "under_count": 0,
        }

    entries = []
    for p in rows:
        gap = (p["self_actual"] or 0) - (p["self_predicted"] or 0)
        entries.append({
            "log_date": _iso(p["log_date"]), "title": p["title"],
            "predicted": p["self_predicted"], "actual": p["self_actual"],
            "gap": gap, "note": p["note"],
        })

    avg_gap = sum(e["gap"] for e in entries) / len(entries)
    over_count = sum(1 for e in entries if e["gap"] < 0)
    under_count = sum(1 for e in entries if e["gap"] > 0)

    # main.py:374-382 — 최신→오래된 을 오래된→최신으로 뒤집고,
    # 같은 날짜 여러 건이면 일자별 평균으로 집약 (zigzag 방지).
    by_date: dict[str, list[tuple]] = {}
    for e in reversed(entries):
        by_date.setdefault(e["log_date"], []).append((e["predicted"], e["actual"]))
    chart = []
    for d in sorted(by_date.keys()):
        pairs = by_date[d]
        preds = [p for p, _ in pairs if p is not None]
        acts = [a for _, a in pairs if a is not None]
        chart.append({
            "date": d,
            "predicted": sum(preds) / len(preds) if preds else None,
            "actual": sum(acts) / len(acts) if acts else None,
        })

    return {
        "entries": entries, "chart": chart, "avg_gap": avg_gap,
        "over_count": over_count, "under_count": under_count,
    }


def _progress_entries(sid: int) -> list[dict]:
    rows = db_service.query(
        "SELECT log_date, category, chapter, title, planned, actual, "
        "       score_raw, score_max, note "
        "FROM student_progress "
        "WHERE student_id = ? AND category IN ('진도', '숙제', '시험') "
        "ORDER BY log_date DESC, progress_id DESC LIMIT 20",
        (sid,),
    )
    out = []
    for p in rows:
        score = (
            f"{p['score_raw']}/{p['score_max']}"
            if p["score_raw"] is not None and p["score_max"] else "-"
        )
        out.append({
            "log_date": _iso(p["log_date"]), "category": p["category"],
            "chapter": p["chapter"], "title": p["title"],
            "planned": p["planned"], "actual": p["actual"],
            "score_display": score, "note": p["note"],
        })
    return out


def _quantity_grade_counts(sid: int) -> list[dict]:
    cutoff = (date.today() - timedelta(weeks=4)).isoformat()
    rows = db_service.query(
        "SELECT quantity_grade FROM student_assessment "
        "WHERE student_id = ? AND eval_type = 'quantity' AND eval_date >= ?",
        (sid, cutoff),
    )
    if not rows:
        return []
    counter = Counter(r["quantity_grade"] for r in rows if r["quantity_grade"])
    total_q = sum(counter.values())
    return [
        {
            "grade": g, "count": counter.get(g, 0),
            "pct": (counter.get(g, 0) / total_q * 100) if total_q else None,
        }
        for g in GRADE_OPTIONS
    ]


def _latest_qualitative(sid: int) -> dict | None:
    rows = db_service.query(
        "SELECT eval_date, note_completion, written_completion, "
        "       textbook_marking, second_solve_reason, note "
        "FROM student_assessment "
        "WHERE student_id = ? AND eval_type = 'qualitative' "
        "ORDER BY eval_date DESC LIMIT 1",
        (sid,),
    )
    if not rows:
        return None
    r = dict(rows[0])
    r["eval_date"] = _iso(r["eval_date"])
    return r


def _logs(sid: int) -> list[dict]:
    rows = db_service.query(
        "SELECT log_date, log_type, summary, detail "
        "FROM student_log WHERE student_id = ? "
        "ORDER BY log_date DESC, log_id DESC LIMIT 30",
        (sid,),
    )
    out = []
    for r in rows:
        d = dict(r)
        d["log_date"] = _iso(d["log_date"])
        out.append(d)
    return out


def get_dashboard(sid: int) -> dict | None:
    student = _student_basic(sid)
    if not student:
        return None

    latest_prism = _latest_prism(sid)
    avg_ris = avg_pm = None
    if latest_prism:
        avg_ris = (latest_prism["score_r"] + latest_prism["score_i"] + latest_prism["score_s"]) / 3
        avg_pm = (latest_prism["score_p"] + latest_prism["score_m"]) / 2

    sp = _self_predict(sid)

    return {
        "student": student,
        "clinic_count": _clinic_count(sid),
        "latest_prism": latest_prism,
        "avg_ris": avg_ris,
        "avg_pm": avg_pm,
        "prism_history": _prism_history(sid),
        "clinic_error_distribution": _clinic_error_distribution(sid),
        "self_predict_entries": sp["entries"],
        "self_predict_chart": sp["chart"],
        "self_predict_avg_gap": sp["avg_gap"],
        "self_predict_over_count": sp["over_count"],
        "self_predict_under_count": sp["under_count"],
        "progress_entries": _progress_entries(sid),
        "quantity_grade_counts": _quantity_grade_counts(sid),
        "latest_qualitative": _latest_qualitative(sid),
        "logs": _logs(sid),
    }


def update_student_basic(sid: int, school: str | None, grade: int,
                         class_name: str | None, note: str | None) -> None:
    db_service.execute_write(
        "UPDATE students SET school=?, grade=?, class_name=?, note=? "
        "WHERE student_id=?",
        (school, grade, class_name, note, sid),
    )


def insert_prism_eval(sid: int, eval_date: str, score_p: int, score_r: int,
                      score_i: int, score_s: int, score_m: int,
                      note: str | None) -> None:
    db_service.execute_write(
        "INSERT INTO prism_assessment "
        "(student_id, eval_date, score_p, score_r, score_i, score_s, score_m, note) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (sid, eval_date, score_p, score_r, score_i, score_s, score_m, note),
    )


def insert_self_predict(sid: int, log_date: str, title: str | None,
                        predicted: int, actual: int, note: str | None) -> None:
    db_service.execute_write(
        "INSERT INTO student_progress "
        "(student_id, log_date, category, title, self_predicted, self_actual, note) "
        "VALUES (?, ?, '자가예측', ?, ?, ?, ?)",
        (sid, log_date, title, predicted, actual, note),
    )


def insert_progress(sid: int, log_date: str, category: str, chapter: str | None,
                    title: str | None, planned: str | None, actual: str | None,
                    score_raw: int | None, score_max: int | None,
                    note: str | None) -> None:
    db_service.execute_write(
        "INSERT INTO student_progress "
        "(student_id, log_date, category, chapter, title, "
        " planned, actual, score_raw, score_max, note) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (sid, log_date, category, chapter, title, planned, actual,
         score_raw, score_max, note),
    )


def insert_quantity_assessment(sid: int, eval_date: str, grade: str,
                               note: str | None) -> None:
    db_service.execute_write(
        "INSERT INTO student_assessment "
        "(student_id, eval_date, eval_type, quantity_grade, note) "
        "VALUES (?, ?, 'quantity', ?, ?)",
        (sid, eval_date, grade, note),
    )


def insert_qualitative_assessment(sid: int, eval_date: str, note_completion: int,
                                  written_completion: int, textbook_marking: int,
                                  second_solve_reason: int, note: str | None) -> None:
    db_service.execute_write(
        "INSERT INTO student_assessment "
        "(student_id, eval_date, eval_type, note_completion, written_completion, "
        " textbook_marking, second_solve_reason, note) "
        "VALUES (?, ?, 'qualitative', ?, ?, ?, ?, ?)",
        (sid, eval_date, note_completion, written_completion,
         textbook_marking, second_solve_reason, note),
    )


def insert_log(sid: int, log_date: str, log_type: str, summary: str | None,
               detail: str | None) -> None:
    db_service.execute_write(
        "INSERT INTO student_log (student_id, log_date, log_type, summary, detail) "
        "VALUES (?, ?, ?, ?, ?)",
        (sid, log_date, log_type, summary, detail),
    )
