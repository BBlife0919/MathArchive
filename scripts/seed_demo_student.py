#!/usr/bin/env python3
"""학생카드 맛보기용 가짜 학생 + 풍부한 데이터 시드.

사용처: 데모/스크린샷/PDF 인쇄용 — 모든 섹션에 데이터 보이도록 한 학생 가득 채움.

학생: 맛보기학생 / 광명북중 3-1
데이터: clinic_entries 9, student_progress 8, student_assessment 14, student_log 5

삭제는 --purge 옵션 (이름 매칭 후 cascade).

실행:
    python scripts/seed_demo_student.py            # 자동 분기 (cloud or sqlite)
    python scripts/seed_demo_student.py --local    # 강제 SQLite
    python scripts/seed_demo_student.py --purge    # 맛보기학생 + 데이터 일괄 삭제
"""
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from db import get_connection, is_cloud  # noqa: E402

DEMO_NAME = "맛보기학생"


def _load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def _today_minus(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def _placeholder(cloud: bool) -> str:
    """SQLite=?, Postgres=%s 명시 분기 (모듈명 기반 자동 추론은 _PgConnection
    이 db 모듈 안이라 'psycopg' 미포함 → 잘못 추론되는 사고)."""
    return "%s" if cloud else "?"


def _seed(conn, ph: str, cloud: bool) -> int:
    # 1) student
    cur = conn.execute(
        f"INSERT INTO students (name, school, grade, class_name, note) "
        f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph})"
        + (" RETURNING student_id" if cloud else ""),
        (DEMO_NAME, "광명북중", 3, "1반",
         "시연용 가짜 데이터 — --purge 로 일괄 삭제 가능"),
    )
    if cloud:
        sid = cur.fetchone()[0]
    else:
        sid = cur.lastrowid

    # 2) clinic_entries (Q 4 + M 5)
    # wrong_question_id 는 questions FK (Postgres 강제). 실제 존재하는 question_id 동적 조회.
    qrow = conn.execute(
        "SELECT question_id FROM questions ORDER BY question_id LIMIT 1"
    ).fetchone()
    if qrow is None:
        raise RuntimeError(
            "questions 테이블이 비어있어 데모 clinic 시드 불가. "
            "먼저 build_db.py 로 적어도 1개 이상 적재 필요."
        )
    demo_qid = qrow[0]
    clinic_rows = [
        (demo_qid, _today_minus(2),  "개념누락",     "인수분해 공식"),
        (demo_qid, _today_minus(5),  "개념누락",     "이차함수 정의"),
        (demo_qid, _today_minus(12), "조건해석실패", "범위 조건"),
        (demo_qid, _today_minus(18), "전략선택실패", "대입 vs 가감"),
        (demo_qid, _today_minus(1),  "계산실수",     "부호 누락"),
        (demo_qid, _today_minus(7),  "계산실수",     "이항 실수"),
        (demo_qid, _today_minus(10), "계산실수",     "분수 통분"),
        (demo_qid, _today_minus(15), "시간관리",     "마지막 3문항"),
        (demo_qid, _today_minus(22), "시간관리",     "서술형 시간"),
    ]
    for qid, dt, code, kw in clinic_rows:
        conn.execute(
            f"INSERT INTO clinic_entries "
            f"(student_id, wrong_question_id, wrong_date, error_code, keyword, prescribed_qids) "
            f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
            (sid, qid, dt, code, kw, "[]"),
        )

    # 3) student_progress — 자가예측 3 + 학습 로그 5
    progress_pred = [
        (_today_minus(21), "자가예측", "인수분해 단원평가", 85, 72, "시간관리 실패 -10"),
        (_today_minus(14), "자가예측", "이차함수 쪽지시험", 70, 75, "예상보다 잘 봄"),
        (_today_minus(3),  "자가예측", "연립방정식 미니",   80, 78, ""),
    ]
    for dt, cat, title, pred, actual, note in progress_pred:
        conn.execute(
            f"INSERT INTO student_progress "
            f"(student_id, log_date, category, title, self_predicted, self_actual, note) "
            f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
            (sid, dt, cat, title, pred, actual, note),
        )

    progress_log = [
        (_today_minus(1),  "진도", "이차함수", "유형 1~5",      "1h / 10문", "1.2h / 10문",   None, None, ""),
        (_today_minus(2),  "숙제", "이차함수", "워크북 p.42",   "1h",        "1h / 8문",      None, None, "2문항 보류"),
        (_today_minus(7),  "시험", "인수분해", "단원평가",      "40분",      "40분",            72,  100, ""),
        (_today_minus(8),  "진도", "이차함수", "유형 6~10",     "1h / 10문", "1h / 10문",     None, None, ""),
        (_today_minus(12), "숙제", "인수분해", "복합형 6문",    "30분",      "50분 / 5문",    None, None, "한 문제 못 풀음"),
    ]
    for dt, cat, ch, title, pl, ac, sr, sm, note in progress_log:
        conn.execute(
            f"INSERT INTO student_progress "
            f"(student_id, log_date, category, chapter, title, planned, actual, score_raw, score_max, note) "
            f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
            (sid, dt, cat, ch, title, pl, ac, sr, sm, note),
        )

    # 4) student_assessment — 정량 12 + 정성 2
    quant_rows = [
        (_today_minus(1),  "A"), (_today_minus(2),  "B"), (_today_minus(3),  "A"),
        (_today_minus(4),  "B"), (_today_minus(7),  "A"), (_today_minus(8),  "C"),
        (_today_minus(9),  "B"), (_today_minus(14), "A"), (_today_minus(15), "B"),
        (_today_minus(16), "B"), (_today_minus(21), "C"), (_today_minus(22), "D"),
    ]
    for dt, grade in quant_rows:
        conn.execute(
            f"INSERT INTO student_assessment "
            f"(student_id, eval_date, eval_type, quantity_grade) "
            f"VALUES ({ph}, {ph}, 'quantity', {ph})",
            (sid, dt, grade),
        )

    qual_rows = [
        (_today_minus(2),  4, 4, 5, 3, "풀이노트 깔끔, 2차 풀이 이유 작성 부족"),
        (_today_minus(16), 3, 3, 4, 2, "서술형 부족, 교재 표시는 늘어남"),
    ]
    for dt, n, w, t, s, note in qual_rows:
        conn.execute(
            f"INSERT INTO student_assessment "
            f"(student_id, eval_date, eval_type, "
            f" note_completion, written_completion, textbook_marking, second_solve_reason, note) "
            f"VALUES ({ph}, {ph}, 'qualitative', {ph}, {ph}, {ph}, {ph}, {ph})",
            (sid, dt, n, w, t, s, note),
        )

    # 5) student_log
    log_rows = [
        (_today_minus(1),  "보호자", "단원평가 결과 공유",   "어머니께 점수 72점 + 시간관리 보강 안내"),
        (_today_minus(10), "보호자", "주간 보고 카톡",       "주간 학습량 + PRISM 비율 공유"),
        (_today_minus(5),  "출결",   "결석 1회",             "병원 진료, 다음 주 보충"),
        (_today_minus(3),  "메모",   "집중도 회복",          "오답노트 작성 후 적극성 증가"),
        (_today_minus(8),  "메모",   "Q→M 전이 신호",        "개념 누락 ↓, 계산실수 ↑"),
    ]
    for dt, ltype, summary, detail in log_rows:
        conn.execute(
            f"INSERT INTO student_log "
            f"(student_id, log_date, log_type, summary, detail) "
            f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph})",
            (sid, dt, ltype, summary, detail),
        )

    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    return sid


def _purge(conn, ph: str) -> int:
    """맛보기학생 + 모든 의존 데이터 삭제. 삭제된 학생 수 반환."""
    rows = conn.execute(
        f"SELECT student_id FROM students WHERE name = {ph}",
        (DEMO_NAME,),
    ).fetchall()
    if not rows:
        return 0
    sids = [r[0] for r in rows]
    placeholders = ",".join([ph] * len(sids))
    for tbl in ("clinic_entries", "student_progress",
                "student_assessment", "student_log"):
        conn.execute(
            f"DELETE FROM {tbl} WHERE student_id IN ({placeholders})",
            tuple(sids),
        )
    conn.execute(
        f"DELETE FROM students WHERE student_id IN ({placeholders})",
        tuple(sids),
    )
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    return len(sids)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--local", action="store_true",
                    help="강제로 로컬 SQLite (SUPABASE_DB_URL 무시)")
    ap.add_argument("--purge", action="store_true",
                    help="맛보기학생 + 데이터 일괄 삭제")
    args = ap.parse_args()

    if args.local:
        os.environ.pop("SUPABASE_DB_URL", None)
    else:
        _load_env_file()

    conn = get_connection()
    cloud = is_cloud()
    ph = _placeholder(cloud)
    target = "Supabase Postgres" if cloud else "로컬 SQLite"

    if args.purge:
        n = _purge(conn, ph)
        print(f"[OK] {DEMO_NAME} {n}명 + 의존 데이터 삭제 ({target})")
        return

    sid = _seed(conn, ph, cloud)
    print(f"[OK] {DEMO_NAME} 신규 student_id={sid} + "
          f"9 clinic / 8 progress / 14 assess / 5 log ({target})")


if __name__ == "__main__":
    main()
