"""PDF 생성 서비스 — app/pdf_engine.py 를 재작성 없이 그대로 호출한다
(계획서 "A등급" — 폰트·수식크기 회귀 위험 때문에 로직을 건드리지 않음).
"""
from __future__ import annotations

from .. import legacy_bridge  # noqa: F401

from pathlib import Path

from pdf_engine import generate_exam_pdf  # type: ignore

from . import db_service

ASSETS_DIR = Path(__file__).resolve().parents[3] / "app" / "assets"
DEFAULT_LOGO_PATH = ASSETS_DIR / "eum_logo.png"


def build_exam_pdf(question_ids: list[int], title: str = "수학 시험지",
                   include_source: bool = True,
                   subtitle: str | None = None,
                   include_logo: bool = False,
                   overrides: dict | None = None) -> bytes:
    rows = db_service.fetch_questions_for_preview(question_ids)
    # main.py:1663 과 동일하게 dict 로 변환 후 전달
    # (raw Row 객체는 pdf_engine 내부의 `.get()` 호출과 호환 안 됨).
    questions = [dict(r) for r in rows]
    logo_path = str(DEFAULT_LOGO_PATH) if include_logo and DEFAULT_LOGO_PATH.exists() else None
    return generate_exam_pdf(
        questions,
        title=title,
        include_source=include_source,
        overrides=overrides or {},
        subtitle=subtitle,
        logo_path=logo_path,
    )
