from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class ExamPdfRequest(BaseModel):
    question_ids: list[int]
    title: str = "수학 시험지"
    subtitle: Optional[str] = None
    include_source: bool = True
    include_logo: bool = False
    overrides: dict[int, str] = {}


class BookPdfRequest(BaseModel):
    question_ids: list[int]
    title: str = "수학 교재"
    subtitle: Optional[str] = None
    include_source: bool = True
    include_logo: bool = False
    cover_style: Literal["final", "diagonal"] = "final"
    cover_kicker: Optional[str] = None
    cover_big_word: Optional[str] = None
    cover_footer_main: Optional[str] = None
    cover_footer_sub: Optional[str] = None
    dcov_subject: Optional[str] = None
    dcov_level: Optional[str] = None
    kicker_mark: Optional[str] = None
    kicker_text: Optional[str] = None
    divider_meta_top: Optional[str] = None
    divider_footer_title: Optional[str] = None
    divider_footer_sub: Optional[str] = None
    overrides: dict[int, str] = {}
