from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ExamPdfRequest(BaseModel):
    question_ids: list[int]
    title: str = "수학 시험지"
    subtitle: Optional[str] = None
    include_source: bool = True
    include_logo: bool = False
    overrides: dict[int, str] = {}
