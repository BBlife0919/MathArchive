"""DB row → QuestionCard 스키마 변환. main.py 의 카드 렌더 로직(1094-1194줄)과
동일한 필드 구성을 재사용한다."""
from __future__ import annotations

from .. import legacy_bridge  # noqa: F401
from ..schemas.questions import QuestionCard
from . import content_parser
from . import db_service

import main as legacy_main  # type: ignore

_ANSWER_CIRCLE = {"1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤"}


def build_question_card(row, img_map: dict | None = None) -> QuestionCard:
    qtext = row["question_text"] or ""
    solution_text = row["solution_text"] if "solution_text" in row.keys() else None

    content_segments = content_parser.parse_question_content(
        qtext, row["file_source"] or "", img_map or {},
    )
    solution_segments = (
        content_parser.parse_question_content(
            solution_text, row["file_source"] or "", img_map or {},
        )
        if solution_text else []
    )

    answer = row["answer"]
    return QuestionCard(
        question_id=row["question_id"],
        meta_short=legacy_main.format_meta(row, short=True),
        meta_full=legacy_main.format_meta(row, short=False),
        school=row["school"],
        chapter=row["chapter"],
        difficulty=row["difficulty"],
        points=row["points"],
        is_subjective=bool(row["is_subjective"]),
        error_note=row["error_note"] if "error_note" in row.keys() else None,
        content_segments=content_segments,
        choices_text=legacy_main.format_choices(row["choices"]),
        answer=answer,
        answer_display=_ANSWER_CIRCLE.get(answer, answer),
        solution_segments=solution_segments,
    )


def build_question_cards(rows) -> list[QuestionCard]:
    ids = [r["question_id"] for r in rows]
    img_maps = db_service.image_maps_for(ids)
    return [build_question_card(r, img_maps.get(r["question_id"])) for r in rows]
