"""클리닉 도메인 로직 — 유사문항 추출, 재도전 스케줄 계산.

UI(pages/1_🏥_클리닉.py)에서 import하여 사용.
"""
from __future__ import annotations

import json
from datetime import date, timedelta

ERROR_CODES = [
    "개념누락", "조건해석실패", "전략선택실패", "계산실수", "시간관리"
]

DIFF_NEXT = {"하": "중", "중": "상", "상": "킬"}


def find_similar_questions(conn, wrong_qid: int) -> list[int]:
    """오답 문제와 같은 chapter에서 인출 3문항 추출.

    구성: 동일 difficulty 2 (유사) + 한 단계 상 1 (변형).
    한 단계 상이 부족하면 동일 difficulty에서 보충.
    """
    row = conn.execute(
        "SELECT chapter, difficulty FROM questions WHERE question_id = ?",
        (wrong_qid,),
    ).fetchone()
    if not row:
        return []
    chapter, diff = row[0], row[1]

    similar = conn.execute(
        """
        SELECT question_id FROM questions
        WHERE chapter = ? AND difficulty = ? AND question_id != ?
        ORDER BY RANDOM() LIMIT 2
        """,
        (chapter, diff, wrong_qid),
    ).fetchall()

    next_diff = DIFF_NEXT.get(diff, diff)
    variant = conn.execute(
        """
        SELECT question_id FROM questions
        WHERE chapter = ? AND difficulty = ? AND question_id != ?
        ORDER BY RANDOM() LIMIT 1
        """,
        (chapter, next_diff, wrong_qid),
    ).fetchall()

    picks = [r[0] for r in similar] + [r[0] for r in variant]

    # 3개 미달 시 동일 chapter 아무 난이도에서 보충
    if len(picks) < 3:
        existing = set(picks) | {wrong_qid}
        placeholders = ",".join("?" * len(existing))
        backup = conn.execute(
            f"""
            SELECT question_id FROM questions
            WHERE chapter = ? AND question_id NOT IN ({placeholders})
            ORDER BY RANDOM() LIMIT ?
            """,
            (chapter, *existing, 3 - len(picks)),
        ).fetchall()
        picks.extend(r[0] for r in backup)

    return picks[:3]


def compute_retry_schedule(wrong_date: date) -> dict:
    """D+3 / D+7 / D+14 재도전 날짜 계산."""
    return {
        "d3": wrong_date + timedelta(days=3),
        "d7": wrong_date + timedelta(days=7),
        "d14": wrong_date + timedelta(days=14),
    }


def insert_clinic_entry(
    conn,
    student_id: int,
    wrong_question_id: int,
    wrong_date_iso: str,
    error_code: str,
    keyword: str,
    prescribed_qids: list[int],
) -> int:
    """clinic_entries 1행 INSERT, entry_id 반환."""
    cursor = conn.execute(
        """
        INSERT INTO clinic_entries
            (student_id, wrong_question_id, wrong_date, error_code, keyword, prescribed_qids)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            student_id, wrong_question_id, wrong_date_iso,
            error_code, keyword, json.dumps(prescribed_qids),
        ),
    )
    conn.commit()
    return cursor.lastrowid


def list_pending_retries(conn, student_id: "int | None" = None) -> list:
    """오늘 기준 재도전 도래 항목 (D+3/7/14 중 pending인 것).

    학생별 워밍업 퀴즈에 자동 삽입할 수 있는 풀.

    DB 호환: 날짜 연산을 Python 측에서 수행 (SQLite/Postgres 모두 호환).
    """
    where_student = "WHERE e.student_id = ?" if student_id is not None else ""
    params = (student_id,) if student_id is not None else ()
    rows = conn.execute(
        f"""
        SELECT e.entry_id, e.student_id, e.wrong_question_id, e.wrong_date,
               e.error_code, e.keyword, e.prescribed_qids,
               e.retry_d3_status, e.retry_d7_status, e.retry_d14_status,
               s.name as student_name
        FROM clinic_entries e
        JOIN students s ON e.student_id = s.student_id
        {where_student}
        ORDER BY e.wrong_date DESC
        """,
        params,
    ).fetchall()

    today = date.today()
    out = []
    for r in rows:
        wrong_date_str = r[3]
        try:
            wd = date.fromisoformat(str(wrong_date_str)[:10])
        except (TypeError, ValueError):
            continue
        sched = compute_retry_schedule(wd)

        d3_due = r[7] == 'pending' and sched["d3"] <= today
        d7_due = r[8] == 'pending' and sched["d7"] <= today
        d14_due = r[9] == 'pending' and sched["d14"] <= today
        if not (d3_due or d7_due or d14_due):
            continue

        out.append({
            "entry_id": r[0],
            "student_id": r[1],
            "wrong_question_id": r[2],
            "wrong_date": str(wrong_date_str),
            "error_code": r[4],
            "keyword": r[5],
            "prescribed_qids": json.loads(r[6]) if r[6] else [],
            "retry_d3_status": r[7],
            "retry_d7_status": r[8],
            "retry_d14_status": r[9],
            "student_name": r[10],
        })
    return out
