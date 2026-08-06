"""카톡 승인 큐 서비스 — app/pages/3_카톡승인큐.py 의 SQL·AI draft 로직 그대로.

실제 발송(Solapi)은 이 서비스가 관여하지 않는다 — scripts/send_kakao_notify.py
(cron)가 approved 행만 읽어서 발송하는 별개 배치 프로세스.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, timedelta

from . import db_service, student_service

RIS_CODES = student_service.RIS_CODES
PM_CODES = student_service.PM_CODES


def _iso(v):
    return v.isoformat() if hasattr(v, "isoformat") else v


def list_students_for_draft() -> list[dict]:
    return [dict(r) for r in db_service.query(
        "SELECT student_id, name FROM students ORDER BY name"
    )]


def build_ai_draft(student_id: int, student_name: str) -> str:
    """app/pages/3_카톡승인큐.py:71-141 그대로."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    prism_rows = db_service.query(
        "SELECT eval_date, score_p, score_r, score_i, score_s, score_m "
        "FROM prism_assessment WHERE student_id = ? "
        "ORDER BY eval_date DESC, assessment_id DESC LIMIT 1",
        (student_id,),
    )
    if prism_rows:
        pr = prism_rows[0]
        ris_avg = (pr["score_r"] + pr["score_i"] + pr["score_s"]) / 3
        pm_avg = (pr["score_p"] + pr["score_m"]) / 2
        prism_line = (
            f"· PRISM 강사 평가 ({_iso(pr['eval_date'])}): "
            f"이해 RIS {ris_avg:.1f}/5 · 수행 PM {pm_avg:.1f}/5\n"
        )
    else:
        cutoff = (today - timedelta(weeks=4)).isoformat()
        entries = db_service.query(
            "SELECT error_code FROM clinic_entries "
            "WHERE student_id = ? AND wrong_date >= ?",
            (student_id, cutoff),
        )
        counter = Counter(e["error_code"] for e in entries)
        ris_total = sum(counter[c] for c in RIS_CODES)
        pm_total = sum(counter[c] for c in PM_CODES)
        prism_line = (
            f"· PRISM (최근 4주 누적): 이해 RIS {ris_total}건 / 수행 PM {pm_total}건\n"
        )

    pred = db_service.query(
        "SELECT self_predicted, self_actual FROM student_progress "
        "WHERE student_id = ? AND category = '자가예측' "
        "ORDER BY log_date DESC LIMIT 1",
        (student_id,),
    )
    gap_line = ""
    if pred:
        gap = (pred[0]["self_actual"] or 0) - (pred[0]["self_predicted"] or 0)
        sign = "+" if gap >= 0 else ""
        gap_line = f"· 자가예측 격차: {sign}{gap}점\n"

    seven_ago = (today - timedelta(days=7)).isoformat()
    logs = db_service.query(
        "SELECT category FROM student_progress "
        "WHERE student_id = ? AND log_date >= ? AND category != '자가예측'",
        (student_id, seven_ago),
    )
    log_summary = Counter(l["category"] for l in logs)

    return (
        f"[EUM] {student_name} 학부모님께 안녕하세요. "
        f"{week_start.isoformat()} 주 학습 보고드립니다.\n"
        f"· 이번 주 학습 로그: "
        f"{log_summary.get('진도', 0)}진도·{log_summary.get('숙제', 0)}숙제·"
        f"{log_summary.get('시험', 0)}시험\n"
        + prism_line
        + gap_line +
        "· 다음 주 과제: [강사 코멘트로 보강 예정]\n"
        "※ 학습 데이터는 AI 로 요약 후 담당 강사가 검수·발송합니다."
    )


def create_draft(student_id: int, target_phone: str, template_code: str,
                 scheduled_at: str) -> int:
    student = student_service.get_student(student_id)
    student_name = student["name"] if student else "?"
    draft = build_ai_draft(student_id, student_name)
    return db_service.execute_write(
        "INSERT INTO kakao_send_queue "
        "(student_id, target_phone, template_code, ai_draft, status, scheduled_at) "
        "VALUES (?, ?, ?, ?, 'draft', ?)",
        (student_id, target_phone, template_code, draft, scheduled_at),
    )


def list_drafts() -> list[dict]:
    rows = db_service.query(
        "SELECT k.queue_id, k.student_id, k.target_phone, k.ai_draft, "
        "       k.instructor_note, k.scheduled_at, s.name AS student_name "
        "FROM kakao_send_queue k "
        "JOIN students s ON k.student_id = s.student_id "
        "WHERE k.status = 'draft' "
        "ORDER BY k.scheduled_at, k.queue_id",
    )
    out = []
    for r in rows:
        d = dict(r)
        d["scheduled_at"] = _iso(d["scheduled_at"])
        out.append(d)
    return out


class EmptyInstructorNote(Exception):
    pass


def approve_draft(queue_id: int, instructor_note: str) -> None:
    """app/pages/3_카톡승인큐.py:211-220 — 강사 코멘트 미입력 시 승인 차단
    (원본은 프론트 폼에서만 체크하는데, 여기서는 API 레벨에서도 강제해
    "코드 레벨 강제 룰"이라는 원본 의도를 API 우회로부터도 지킨다)."""
    if not instructor_note.strip():
        raise EmptyInstructorNote()
    db_service.execute_write(
        "UPDATE kakao_send_queue SET instructor_note = ?, status = 'approved' "
        "WHERE queue_id = ?",
        (instructor_note.strip(), queue_id),
    )


def delete_draft(queue_id: int) -> None:
    db_service.execute_write(
        "DELETE FROM kakao_send_queue WHERE queue_id = ?", (queue_id,),
    )


def list_approved() -> list[dict]:
    rows = db_service.query(
        "SELECT k.queue_id, k.scheduled_at, k.target_phone, k.instructor_note, "
        "       s.name AS student_name "
        "FROM kakao_send_queue k "
        "JOIN students s ON k.student_id = s.student_id "
        "WHERE k.status = 'approved' "
        "ORDER BY k.scheduled_at",
    )
    out = []
    for r in rows:
        d = dict(r)
        d["scheduled_at"] = _iso(d["scheduled_at"])
        out.append(d)
    return out


def revert_to_draft(queue_id: int) -> None:
    db_service.execute_write(
        "UPDATE kakao_send_queue SET status = 'draft' WHERE queue_id = ?",
        (queue_id,),
    )


def list_send_logs() -> list[dict]:
    rows = db_service.query(
        "SELECT k.queue_id, k.status, k.sent_at, k.target_phone, "
        "       k.solapi_msg_id, k.error_log, s.name AS student_name "
        "FROM kakao_send_queue k "
        "JOIN students s ON k.student_id = s.student_id "
        "WHERE k.status IN ('sent', 'failed') "
        "ORDER BY COALESCE(k.sent_at, k.created_at) DESC "
        "LIMIT 20",
    )
    out = []
    for r in rows:
        d = dict(r)
        d["sent_at"] = _iso(d["sent_at"])
        out.append(d)
    return out
