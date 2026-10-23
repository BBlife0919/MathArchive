"""학교명(questions.school) 데이터 정규화 — region_taxonomy.py와 같은 원칙.

questions.school 컬럼은 자유 텍스트라 같은 학교가 여러 표기로 중복 적재돼
있다(예: "광북고"/"광북북고"/"광명북고" — 전부 광명북고를 가리키는 오타·
줄임 표기). DB 원본 값은 건드리지 않고, 이 모듈이 "원본 school 문자열 →
표준 표기"로 매핑하는 프레젠테이션 레이어 역할만 한다.
"""
from __future__ import annotations

# raw school → 표준 표기. 사용자 확인 후 정정(2026-10-24).
RAW_TO_CANONICAL: dict[str, str] = {
    "광북고": "광명북고",
    "광북북고": "광명북고",
}


def canonicalize(raw: str) -> str:
    return RAW_TO_CANONICAL.get(raw, raw)


def build_canonical_to_raw(raw_schools: set[str]) -> dict[str, list[str]]:
    canonical_to_raw: dict[str, list[str]] = {}
    for raw in raw_schools:
        canon = canonicalize(raw)
        canonical_to_raw.setdefault(canon, []).append(raw)
    return {c: sorted(r) for c, r in canonical_to_raw.items()}


def expand_canonical_schools(selected: list[str], canonical_to_raw: dict[str, list[str]]) -> list[str]:
    """프론트가 보낸 표준 표기 선택값을 검색 SQL용 원본 raw school 리스트로
    풀어낸다. canonical_to_raw 에 없는 값은 원본 그대로 1개짜리 취급."""
    out: list[str] = []
    for c in selected:
        out.extend(canonical_to_raw.get(c, [c]))
    return out
