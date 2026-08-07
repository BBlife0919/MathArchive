"""PRISM 클리닉 처방전 견본 PDF (고민주 학생 데모).

app/pages/1_클리닉.py 의 로직 재현 — 오답 1건 + 인출 3문항 + PRISM 오류코드.
"""
from __future__ import annotations
import os
import sys
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
sys.path.insert(0, str(APP))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from clinic_logic import compute_retry_schedule


def pick_sample():
    """DB 에서 견본 4문항 선택 — 광명북고1 공수1 이차함수 근처."""
    conn = sqlite3.connect(ROOT / "db" / "mathdb.sqlite")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT q.question_id, q.file_source, q.school, q.question_number, "
        "       q.year, q.semester, q.exam_type, q.question_text, q.choices, "
        "       q.answer, q.answer_type, q.points, q.chapter, q.difficulty, "
        "       q.is_subjective, s.solution_text "
        "FROM questions q LEFT JOIN solutions s ON s.question_id = q.question_id "
        "WHERE q.school='광명북고' AND q.grade=1 AND q.chapter='이차함수' "
        "  AND q.difficulty IN ('중','상') "
        "  AND LENGTH(q.question_text) BETWEEN 60 AND 400 "
        "  AND q.is_subjective=0 "
        "ORDER BY q.question_id LIMIT 4"
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def main():
    rows = pick_sample()
    if len(rows) < 4:
        print(f"[warn] 견본 문항이 부족합니다 ({len(rows)}개). 광명북고 이차함수 확장 검색 시도.")
        # 완화된 조건
        conn = sqlite3.connect(ROOT / "db" / "mathdb.sqlite")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT q.question_id, q.file_source, q.school, q.question_number, "
            "       q.year, q.semester, q.exam_type, q.question_text, q.choices, "
            "       q.answer, q.answer_type, q.points, q.chapter, q.difficulty, "
            "       q.is_subjective, s.solution_text "
            "FROM questions q LEFT JOIN solutions s ON s.question_id = q.question_id "
            "WHERE q.chapter='이차함수' AND q.difficulty IN ('중','상') "
            "  AND LENGTH(q.question_text) BETWEEN 60 AND 400 "
            "  AND q.is_subjective=0 "
            "ORDER BY q.question_id LIMIT 4"
        )
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()

    # JSON 문자열화 (choices)
    import json
    for r in rows:
        ch = r.get("choices")
        if ch is not None and not isinstance(ch, str):
            r["choices"] = json.dumps(ch, ensure_ascii=False)

    student_name = "고민주"
    wrong_dt = date(2026, 7, 13)
    error_code = "I · 개념내재"   # PRISM 5스펙트럼: P·R·I·S·M
    schedule = compute_retry_schedule(wrong_dt)

    subtitle = (
        f"{student_name} · 오류코드: {error_code} · "
        f"재도전 D+3 {schedule['d3']} / D+7 {schedule['d7']} / "
        f"D+14 {schedule['d14']} / D+30 {schedule['d30']}"
    )

    from pdf_engine import generate_exam_pdf
    pdf = generate_exam_pdf(
        rows,
        title=f"처방전 — {student_name} ({wrong_dt})",
        include_source=True,
        overrides={},
        subtitle=subtitle,
    )

    out = Path(f"/Users/youngwoolee/Downloads/prescription_{student_name}_{wrong_dt}.pdf")
    out.write_bytes(pdf)
    print(f"[done] {out}  ({len(pdf)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
