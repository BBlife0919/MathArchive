"""반(class) 관리 서비스 — student_service.py 와 동일한 db_service 패턴.

scripts/migrate_class_test_management.py 가 만든 classes 테이블 +
students.class_id 를 다룬다. class_name(자유텍스트) 은 하위호환으로 남겨두되,
새 UI는 전부 class_id 기준으로 조회한다.
"""
from __future__ import annotations

from . import db_service

import db as legacy_db  # type: ignore


def list_classes() -> list[dict]:
    rows = db_service.query(
        "SELECT c.class_id, c.name, c.teacher, "
        "(SELECT COUNT(*) FROM students s "
        " WHERE s.class_id = c.class_id AND s.is_active=1) "
        "AS student_count "
        "FROM classes c ORDER BY c.name"
    )
    return [dict(r) for r in rows]


def create_class(name: str, teacher: str | None) -> int:
    """student_service.create_student() 와 동일한 Postgres(RETURNING)/
    SQLite(lastrowid) 분기 — execute_write() 로는 PK를 못 돌려받아서 직접 처리."""
    conn = db_service.get_connection()
    cloud = legacy_db.is_cloud()
    sql = "INSERT INTO classes (name, teacher) VALUES (?, ?)"
    if cloud:
        sql += " RETURNING class_id"
    cur = conn.execute(sql, (name, teacher))
    class_id = cur.fetchone()[0] if cloud else cur.lastrowid
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    return class_id


def update_class(class_id: int, name: str | None, teacher: str | None) -> None:
    sets, params = [], []
    if name is not None:
        sets.append("name=?")
        params.append(name)
    if teacher is not None:
        sets.append("teacher=?")
        params.append(teacher)
    if not sets:
        return
    params.append(class_id)
    db_service.execute_write(
        f"UPDATE classes SET {', '.join(sets)} WHERE class_id=?", tuple(params))


def delete_class(class_id: int) -> None:
    # 반을 지워도 학생·테스트는 남는다 — 미배정으로 돌아갈 뿐.
    # tests.class_id 도 같이 NULL 처리 안 하면: SQLite는 FK를 강제 안 해서
    # 조용히 고아 테스트가 되어 list_tests_for_student 의 JOIN 조건을 영영
    # 못 만족해 안 보이게 되고, Postgres는 FK violation으로 500이 난다
    # (/근본 2차 교차검수에서 지적받아 추가, 2026-10-27).
    db_service.execute_write(
        "UPDATE tests SET class_id=NULL WHERE class_id=?", (class_id,))
    db_service.execute_write(
        "UPDATE students SET class_id=NULL WHERE class_id=?", (class_id,))
    db_service.execute_write(
        "DELETE FROM classes WHERE class_id=?", (class_id,))


def assign_students(class_id: int, student_ids: list[int]) -> None:
    if not student_ids:
        return
    placeholders = ",".join("?" * len(student_ids))
    db_service.execute_write(
        f"UPDATE students SET class_id=? WHERE student_id IN ({placeholders})",
        tuple([class_id] + student_ids))


def list_students_in_class(class_id: int | None) -> list[dict]:
    """class_id=None 이면 미배정 학생."""
    if class_id is None:
        rows = db_service.query(
            "SELECT student_id, name, school, grade FROM students "
            "WHERE class_id IS NULL AND is_active=1 ORDER BY name")
    else:
        rows = db_service.query(
            "SELECT student_id, name, school, grade FROM students "
            "WHERE class_id=? AND is_active=1 ORDER BY name", (class_id,))
    return [dict(r) for r in rows]
