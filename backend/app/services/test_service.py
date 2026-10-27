"""TEST 관리(출제·채점) 서비스.

scripts/migrate_class_test_management.py 가 만든 tests/test_results/
test_answers 를 다룬다. 채점에서 오답이 나오면 기존 클리닉 인프라
(app/clinic_logic.compute_retry_schedule/insert_clinic_entry — D+3/7/14/30
재도전 추적)를 그대로 타되, 유사문항 추천만 오늘 만든 임베딩 기반
similarity_service 로 바꾼다(클리닉의 chapter+difficulty+RANDOM() 보다
품질이 높음).
"""
from __future__ import annotations

import json
from datetime import date, datetime

from . import db_service, question_builder, similarity_service

import clinic_logic  # type: ignore
import db as legacy_db  # type: ignore

# 클리닉의 ERROR_CODES(PRISM 5분류, 강사가 직접 진단)는 의도된 고정 taxonomy라
# 손대지 않는다 — 자동 채점 오답은 "왜" 틀렸는지 진단하지 않았으므로 그 중
# 하나로 끼워맞추지 않고, DB에 CHECK 제약이 없는 걸 확인하고 전용 라벨을 쓴다.
AUTO_GRADE_ERROR_LABEL = "테스트채점(미분류)"


def create_test(title: str, class_id: int | None, question_ids: list[int],
                chapter_label: str | None, created_by: int | None) -> int:
    conn = db_service.get_connection()
    cloud = legacy_db.is_cloud()
    sql = ("INSERT INTO tests (title, class_id, question_ids, chapter_label, "
           "created_by) VALUES (?, ?, ?, ?, ?)")
    if cloud:
        sql += " RETURNING test_id"
    cur = conn.execute(
        sql, (title, class_id, json.dumps(question_ids), chapter_label, created_by))
    test_id = cur.fetchone()[0] if cloud else cur.lastrowid
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    return test_id


def list_tests_for_student(student_id: int) -> list[dict]:
    """이 학생의 반에 배정된 테스트 전체 + 본인 채점 상태(LEFT JOIN)."""
    rows = db_service.query(
        "SELECT t.test_id, t.title, t.chapter_label, t.question_ids, "
        "t.created_at, r.result_id, r.score, r.total, r.graded_at "
        "FROM tests t "
        "JOIN students s ON s.class_id = t.class_id "
        "LEFT JOIN test_results r "
        "  ON r.test_id = t.test_id AND r.student_id = s.student_id "
        "WHERE s.student_id = ? "
        "ORDER BY t.created_at DESC",
        (student_id,),
    )
    out = []
    for r in rows:
        d = dict(r)
        d["question_count"] = len(json.loads(d.pop("question_ids")))
        # Postgres는 TIMESTAMP 컬럼을 datetime 객체로 돌려주고(SQLite는
        # TEXT라 이미 문자열) — 스키마(Optional[str])와 안 맞아 pydantic
        # 검증에서 500이 났다(2026-10-27 실사용 중 발견). 둘 다 문자열로
        # 통일.
        for key in ("created_at", "graded_at"):
            if d.get(key) is not None and not isinstance(d[key], str):
                d[key] = d[key].isoformat()
        out.append(d)
    return out


def get_test_detail(test_id: int, student_id: int | None = None) -> dict | None:
    rows = db_service.query(
        "SELECT test_id, title, chapter_label, question_ids FROM tests "
        "WHERE test_id=?", (test_id,))
    if not rows:
        return None
    t = dict(rows[0])
    qids = json.loads(t["question_ids"])
    q_rows = db_service.fetch_questions_for_preview(qids, preserve_order=True)
    items = question_builder.build_question_cards(q_rows)

    existing: dict[int, bool] = {}
    if student_id is not None:
        res = db_service.query(
            "SELECT result_id FROM test_results WHERE test_id=? AND student_id=?",
            (test_id, student_id))
        if res:
            ans = db_service.query(
                "SELECT question_id, is_correct FROM test_answers "
                "WHERE result_id=?", (res[0]["result_id"],))
            existing = {a["question_id"]: bool(a["is_correct"]) for a in ans}

    return {
        "test_id": t["test_id"], "title": t["title"],
        "chapter_label": t["chapter_label"], "items": items,
        "existing_answers": existing,
    }


def _similar_question_ids(question_id: int, limit: int = 3) -> list[int]:
    """오답 문항의 유사문항 id — similarity_service(오늘 만든 임베딩 인덱스)
    재사용. 인덱스가 없거나 후보를 못 찾으면 조용히 빈 리스트(채점 자체를
    막지 않는다 — best-effort 보강일 뿐)."""
    if not similarity_service.available():
        return []
    base = db_service.fetch_questions_page([question_id])
    if not base:
        return []
    b = base[0]
    cands = similarity_service.similar_natural_keys(
        b["file_source"], b["question_number"], b["chapter"], b["difficulty"],
        b["question_text"], limit=limit,
    )
    if not cands:
        return []
    rows = db_service.fetch_questions_by_natural_keys(
        [(fs, qn) for fs, qn, _ in cands], preserve_order=True)
    seen: set[int] = set()
    out: list[int] = []
    for r in rows:
        cid = r["question_id"]
        if cid == question_id or cid in seen:
            continue
        seen.add(cid)
        out.append(cid)
    return out


def grade_test(test_id: int, student_id: int, answers: list[dict]) -> dict:
    """answers: [{question_id, is_correct}, ...]. test_results/test_answers
    upsert 후, 오답마다 clinic_entries 에 자동 처방(재도전 추적 포함)."""
    conn = db_service.get_connection()
    score = sum(1 for a in answers if a["is_correct"])
    total = len(answers)
    now = datetime.now().isoformat(timespec="seconds")

    existing = db_service.query(
        "SELECT result_id FROM test_results WHERE test_id=? AND student_id=?",
        (test_id, student_id))
    if existing:
        result_id = existing[0]["result_id"]
        db_service.execute_write(
            "UPDATE test_results SET score=?, total=?, graded_at=? "
            "WHERE result_id=?", (score, total, now, result_id))
        # 재채점(이미 있던 답안) 지우고 새로 기록 — 쌓이지 않게.
        db_service.execute_write(
            "DELETE FROM test_answers WHERE result_id=?", (result_id,))
    else:
        cloud = legacy_db.is_cloud()
        sql = ("INSERT INTO test_results (test_id, student_id, score, total, "
               "graded_at) VALUES (?, ?, ?, ?, ?)")
        if cloud:
            sql += " RETURNING result_id"
        cur = conn.execute(sql, (test_id, student_id, score, total, now))
        result_id = cur.fetchone()[0] if cloud else cur.lastrowid
        if hasattr(conn, "commit"):
            try:
                conn.commit()
            except Exception:
                pass

    for a in answers:
        # is_correct 컬럼이 SQLite는 INTEGER, Postgres는 BOOLEAN이라(마이그레이션
        # DDL 차이) 0/1 정수를 그대로 넣으면 Postgres가 DatatypeMismatch로
        # 거부한다(2026-10-27 실사용 중 발견) — 파이썬 bool 로 넘기면 양쪽
        # 드라이버가 알아서 맞는 타입으로 바인딩한다.
        db_service.execute_write(
            "INSERT INTO test_answers (result_id, question_id, is_correct) "
            "VALUES (?, ?, ?)",
            (result_id, a["question_id"], bool(a["is_correct"])))

    # 재채점(오타 정정 등)으로 grade_test 가 여러 번 불려도 clinic_entries 가
    # 안 맞는 상태로 남지 않게 — 이 테스트의 전체 문항에 대해 이 학생의
    # 자동채점 처방 기록을 먼저 전부 지우고, 현재 오답만 다시 넣는다
    # (삭제 후 재생성 = 멱등). 단순 "오늘 중복 체크"만으로는 (1)오답→정답
    # 으로 바뀐 문항의 옛 처방이 안 지워지고 (2)재채점이 다른 날짜에
    # 일어나면 중복 처방이 생기는 문제가 있었다(/근본 2차 교차검수에서
    # 지적받아 전면 수정, 2026-10-27).
    all_qids = [a["question_id"] for a in answers]
    if all_qids:
        placeholders = ",".join("?" * len(all_qids))
        db_service.execute_write(
            f"DELETE FROM clinic_entries WHERE student_id=? AND error_code=? "
            f"AND wrong_question_id IN ({placeholders})",
            tuple([student_id, AUTO_GRADE_ERROR_LABEL] + all_qids))

    wrong_ids = [a["question_id"] for a in answers if not a["is_correct"]]
    prescribed: list[int] = []
    today_iso = date.today().isoformat()
    for wqid in wrong_ids:
        similar = _similar_question_ids(wqid)
        prescribed.extend(similar)
        try:
            clinic_logic.insert_clinic_entry(
                conn, student_id=student_id, wrong_question_id=wqid,
                wrong_date_iso=today_iso,
                error_code=AUTO_GRADE_ERROR_LABEL, keyword="",
                prescribed_qids=similar,
            )
        except Exception:
            # 처방 기록 실패가 채점 저장 자체를 막으면 안 된다 — 채점은
            # 이미 위에서 커밋됐다.
            pass

    # 중복 제거(여러 오답이 같은 유사문항을 추천할 수 있음), 순서 보존.
    seen: set[int] = set()
    prescribed_dedup = []
    for qid in prescribed:
        if qid not in seen:
            seen.add(qid)
            prescribed_dedup.append(qid)

    return {
        "result_id": result_id, "score": score, "total": total,
        "wrong_question_ids": wrong_ids,
        "prescribed_question_ids": prescribed_dedup,
    }
