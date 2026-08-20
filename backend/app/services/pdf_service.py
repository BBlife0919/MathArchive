"""PDF 생성 서비스 — app/pdf_engine.py 를 재작성 없이 그대로 호출한다
(계획서 "A등급" — 폰트·수식크기 회귀 위험 때문에 로직을 건드리지 않음).
"""
from __future__ import annotations

from .. import legacy_bridge  # noqa: F401

from pathlib import Path

from pdf_engine import generate_book_pdf, generate_exam_pdf, paginate  # type: ignore

from . import db_service

ASSETS_DIR = Path(__file__).resolve().parents[3] / "app" / "assets"
DEFAULT_LOGO_PATH = ASSETS_DIR / "eum_logo.png"


def _resolve_logo(include_logo: bool) -> str | None:
    return str(DEFAULT_LOGO_PATH) if include_logo and DEFAULT_LOGO_PATH.exists() else None


def build_exam_pdf(question_ids: list[int], title: str = "수학 시험지",
                   include_source: bool = True,
                   subtitle: str | None = None,
                   include_logo: bool = False,
                   overrides: dict | None = None,
                   preserve_order: bool = False) -> bytes:
    rows = db_service.fetch_questions_for_preview(question_ids, preserve_order)
    # main.py:1663 과 동일하게 dict 로 변환 후 전달
    # (raw Row 객체는 pdf_engine 내부의 `.get()` 호출과 호환 안 됨).
    questions = [dict(r) for r in rows]
    return generate_exam_pdf(
        questions,
        title=title,
        include_source=include_source,
        overrides=overrides or {},
        subtitle=subtitle,
        logo_path=_resolve_logo(include_logo),
    )


def build_layout_preview(question_ids: list[int], overrides: dict | None = None,
                         preserve_order: bool = False) -> list:
    """실시간 미리보기용 — Playwright 없이 실제 PDF와 동일한 지면 배치
    (estimate_layout/paginate)만 계산해서 [page][col][slot] 구조를 그대로
    JSON 으로 내려준다. app/pdf_engine.py 의 로직은 건드리지 않고 그대로
    재사용한다(위 build_exam_pdf 와 동일 원칙)."""
    rows = db_service.fetch_questions_for_preview(question_ids, preserve_order)
    questions = [dict(r) for r in rows]
    pages = paginate(questions, overrides or {})
    return [
        {
            "columns": [
                {
                    "slots": [
                        {"question_id": q["question_id"], "layout": layout}
                        for q, layout in col
                    ],
                }
                for col in page
            ],
        }
        for page in pages
    ]


def build_book_pdf(question_ids: list[int], title: str = "수학 교재",
                   include_source: bool = True,
                   subtitle: str | None = None,
                   include_logo: bool = False,
                   cover_style: str = "final",
                   cover_kicker: str | None = None,
                   cover_big_word: str | None = None,
                   cover_footer_main: str | None = None,
                   cover_footer_sub: str | None = None,
                   dcov_subject: str | None = None,
                   dcov_level: str | None = None,
                   kicker_mark: str | None = None,
                   kicker_text: str | None = None,
                   divider_meta_top: str | None = None,
                   divider_footer_title: str | None = None,
                   divider_footer_sub: str | None = None,
                   overrides: dict | None = None,
                   book_mode: str = "chapter",
                   flat_layout: str = "half",
                   preserve_order: bool = False) -> bytes:
    # 챕터모드는 _group_by_chapter()가 "입력 순서를 그대로 보고 인접한 같은
    # chapter만 묶는" 방식이라, 드래그한 임의 순서를 그대로 넣으면 같은
    # 단원이 흩어져 챕터 디바이더가 중복 생성될 수 있다. 순서 보존은
    # 챕터 그룹화가 없는 일반(flat)모드에서만 의미가 있고 안전하다.
    rows = db_service.fetch_questions_for_preview(
        question_ids, preserve_order and book_mode == "flat",
    )
    questions = [dict(r) for r in rows]
    return generate_book_pdf(
        questions,
        title=title,
        include_source=include_source,
        overrides=overrides or {},
        subtitle=subtitle,
        logo_path=_resolve_logo(include_logo),
        cover_style=cover_style,
        cover_kicker=cover_kicker,
        cover_big_word=cover_big_word,
        cover_footer_main=cover_footer_main,
        cover_footer_sub=cover_footer_sub,
        dcov_subject=dcov_subject,
        dcov_level=dcov_level,
        kicker_mark=kicker_mark,
        kicker_text=kicker_text,
        divider_meta_top=divider_meta_top,
        divider_footer_title=divider_footer_title,
        divider_footer_sub=divider_footer_sub,
        book_mode=book_mode,
        flat_layout=flat_layout,
    )
