"""클리닉 도메인 로직 — 유사문항 추출, 재도전 스케줄 계산.

UI(pages/1_🏥_클리닉.py)에서 import하여 사용.
"""
from __future__ import annotations

import json
from datetime import date, timedelta

ERROR_CODES = [
    "개념누락", "조건해석실패", "전략선택실패", "계산실수", "시간관리"
]
# 신규 코드 추가 시 app/pages/2_📋_학생카드.py 의 PRISM_LETTER / RIS_CODES / PM_CODES 동시 갱신.

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
    """D+3 / D+7 / D+14 / D+30 재도전 날짜 계산.

    D+30 은 통합비전 v3 §4-3 확장분산 — 단기 인출(D+3/7/14) 뒤
    장기 보존을 위한 추가 재도전 슬롯.
    """
    return {
        "d3":  wrong_date + timedelta(days=3),
        "d7":  wrong_date + timedelta(days=7),
        "d14": wrong_date + timedelta(days=14),
        "d30": wrong_date + timedelta(days=30),
    }


def insert_clinic_entry(
    conn,
    student_id: int,
    wrong_question_id: "int | None",
    wrong_date_iso: str,
    error_code: str,
    keyword: str,
    prescribed_qids: list[int],
    external_label: "str | None" = None,
) -> int:
    """clinic_entries 1행 INSERT, entry_id 반환.

    wrong_question_id 가 None 이면 외부 문제 (DB 미적재). external_label 에
    학교/교재/페이지/메모 자유 텍스트 저장.
    """
    # Postgres(autocommit, lastrowid 없음) vs SQLite 분기
    is_pg = hasattr(conn, "_dsn")
    sql = """
        INSERT INTO clinic_entries
            (student_id, wrong_question_id, wrong_date, error_code,
             keyword, prescribed_qids, external_label)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    if is_pg:
        sql += " RETURNING entry_id"
    cursor = conn.execute(
        sql,
        (
            student_id, wrong_question_id, wrong_date_iso,
            error_code, keyword, json.dumps(prescribed_qids),
            external_label,
        ),
    )
    if is_pg:
        entry_id = cursor.fetchone()[0]
    else:
        entry_id = cursor.lastrowid
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    return entry_id


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
               e.retry_d30_status, e.external_label,
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

        d3_due  = r[7] == 'pending' and sched["d3"]  <= today
        d7_due  = r[8] == 'pending' and sched["d7"]  <= today
        d14_due = r[9] == 'pending' and sched["d14"] <= today
        d30_due = r[10] == 'pending' and sched["d30"] <= today
        if not (d3_due or d7_due or d14_due or d30_due):
            continue

        out.append({
            "entry_id": r[0],
            "student_id": r[1],
            "wrong_question_id": r[2],
            "wrong_date": str(wrong_date_str),
            "error_code": r[4],
            "keyword": r[5],
            "prescribed_qids": json.loads(r[6]) if r[6] else [],
            "external_label":  r[11],
            "retry_d3_status":  r[7],
            "retry_d7_status":  r[8],
            "retry_d14_status": r[9],
            "retry_d30_status": r[10],
            "student_name": r[12],
        })
    return out
