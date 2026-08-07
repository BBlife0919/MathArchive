#!/usr/bin/env python3
"""고민주 학생 데모 리포트 — 상담실장 시연용 A4 1페이지.
"""
from __future__ import annotations
_ = """

실제 DB의 학생 메타(이름/학교/학년)만 가져오고, 데이터 섹션은
합리적인 데모값으로 채워서 렌더링. DB는 건드리지 않음.

강사 코멘트도 자연스러운 문구 자동 삽입.

실행:
    python scripts/render_demo_report.py                 # /tmp/demo_report.pdf
    python scripts/render_demo_report.py --out ~/Desktop/고민주_리포트.pdf
"""
import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT))

from db import get_connection  # noqa: E402


def _load_env() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def _fetch_student_meta(name: str) -> dict | None:
    conn = get_connection()
    rows = conn.execute(
        "SELECT student_id, name, school, grade, class_name "
        "FROM students WHERE name = ? LIMIT 1",
        (name,),
    ).fetchall()
    return dict(rows[0]) if rows else None


def _build_demo_data(student: dict) -> dict:
    """DB 안 건드리고, 화면상 그럴듯한 데모 데이터 조립."""
    today = date.today()

    # PRISM 강사 평가 — 최근 4주 3회 추이 (개선되는 그림)
    prism_latest = {
        "eval_date": today.isoformat(),
        "score_p": 3,  # 계산정확성 — 중간
        "score_r": 2,  # 조건해석 — 좋음 (낮을수록 좋음)
        "score_i": 4,  # 개념내재 — 약간 두드러짐
        "score_s": 3,  # 전략선택 — 중간
        "score_m": 2,  # 시간관리 — 좋음
        "note": "인수분해 복합형 반복 후 개념 결함(I) 완화 조짐. 시간관리(M) 안정.",
    }

    # 정량 평가 — 최근 4주 A/B/C/D 분포
    assess_q = (
        [{"quantity_grade": "A"}] * 12
        + [{"quantity_grade": "B"}] * 4
        + [{"quantity_grade": "C"}] * 2
    )

    # 정성 평가 — 이번 달 1건
    assess_l = {
        "eval_date": (today - timedelta(days=5)).isoformat(),
        "note_completion": 4,
        "written_completion": 3,
        "textbook_marking": 4,
        "second_solve_reason": 3,
        "note": "풀이노트 서식 안착, 서술형 논증(∵∴) 습관 형성 중.",
    }

    # 자가예측 3건 — 실제/예측 격차 축소
    preds = [
        {"log_date": (today - timedelta(days=3)).isoformat(),
         "title": "이차함수 단원평가",
         "self_predicted": 82, "self_actual": 85,
         "note": "예측 근접 — 메타인지 개선"},
        {"log_date": (today - timedelta(days=14)).isoformat(),
         "title": "인수분해 쪽지시험",
         "self_predicted": 70, "self_actual": 78,
         "note": "예측 낮게 잡음"},
        {"log_date": (today - timedelta(days=25)).isoformat(),
         "title": "연립방정식 미니테스트",
         "self_predicted": 90, "self_actual": 74,
         "note": "예측 과다 — 시간관리 실패"},
    ]

    # 최근 관리 로그 — 보호자/출결/메모 5건
    logs = [
        {"log_date": today.isoformat(),
         "log_type": "메모",
         "summary": "인수분해 복합형 문제 자발적 재풀이 시작"},
        {"log_date": (today - timedelta(days=2)).isoformat(),
         "log_type": "보호자",
         "summary": "단원평가 85점 결과 어머니께 공유 (문자)"},
        {"log_date": (today - timedelta(days=6)).isoformat(),
         "log_type": "메모",
         "summary": "오답노트 [원인] 칸 작성 정착"},
        {"log_date": (today - timedelta(days=10)).isoformat(),
         "log_type": "출결",
         "summary": "정상 출석 (지각 0회)"},
        {"log_date": (today - timedelta(days=14)).isoformat(),
         "log_type": "보호자",
         "summary": "학습 리듬 안정화 안내 (주간 리포트)"},
    ]

    return {
        "student":  student,
        "clinic":   [],  # PRISM 평가가 있으므로 폴백 안 씀
        "prism":    prism_latest,
        "assess_q": assess_q,
        "assess_l": assess_l,
        "preds":    preds,
        "logs":     logs,
    }


DEMO_INSTRUCTOR_NOTE = (
    "고민주 학생은 최근 4주간 이해 영역(RIS)에서 눈에 띄는 개선을 보이고 있습니다. "
    "특히 오답노트에 '원인 칸'을 스스로 채우기 시작한 이후로 개념 결함(I) 관련 오답이 "
    "감소했습니다. 다음 4주는 개념내재(I)를 3점대로 안정화하는 것을 목표로 "
    "인수분해·이차함수 복합형 반복 처방을 유지하겠습니다."
)


def _inject_instructor_note(html: str, note: str) -> str:
    """render_student_card_pdf._build_html 이 만든 빈 코멘트 박스를 실제 문구로 교체."""
    placeholder = (
        "<div class=\"comment-box\">(여기에 한 줄 추가 후 학부모께 발송)</div>"
    )
    filled = f"<div class=\"comment-box\">{note}</div>"
    return html.replace(placeholder, filled)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--student-name", default="고민주")
    ap.add_argument("--out", default="/tmp/demo_report.pdf")
    ap.add_argument("--instructor-note", default=DEMO_INSTRUCTOR_NOTE)
    args = ap.parse_args()

    _load_env()

    student = _fetch_student_meta(args.student_name)
    if not student:
        print(f"ERROR: '{args.student_name}' 학생을 찾을 수 없음", file=sys.stderr)
        sys.exit(1)

    data = _build_demo_data(student)

    # 렌더 모듈 재사용
    import render_student_card_pdf as R
    chart_b64 = R._render_prism_radar_b64(data["prism"])
    html = R._build_html(data, chart_b64)
    html = _inject_instructor_note(html, args.instructor_note)

    # playwright 로 PDF 생성 (동일 옵션)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(
            path=args.out,
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()

    size_kb = Path(args.out).stat().st_size // 1024
    print(f"[OK] 데모 리포트 생성 ({size_kb} KB) → {args.out}")


if __name__ == "__main__":
    main()
