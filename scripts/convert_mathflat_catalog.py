"""docs/problem_types_mathflat_draft.json(초안) -> docs/problem_types.json(정본 경로).

label_types.py 는 CATALOG = docs/problem_types.json 을 하드코딩해서 읽는다.
초안 스키마(new_subject/db_chapter/types)를 그 스크립트가 기대하는 필드명
(ssen_subject 라는 옛 키 이름을 그대로 재사용 — write_store() 가 이 키로
labels/<subject>/ 폴더를 나누기 때문)에 맞춰 그대로 복사한다. 내용 변경 없음.

사용:
    python3 scripts/convert_mathflat_catalog.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "problem_types_mathflat_draft.json"
DST = ROOT / "docs" / "problem_types.json"


def main() -> None:
    draft = json.loads(SRC.read_text(encoding="utf-8"))
    units = []
    for u in draft["units"]:
        units.append({
            "ssen_subject": u["new_subject"],  # label_types.py 가 쓰는 키 이름 그대로 재사용
            "db_chapter": u["db_chapter"],
            "db_subjects": u["db_subjects"],
            "db_question_count": u["db_question_count"],
            "mathflat_sosub": u["mathflat_sosub"],
            "types": [{"code": t["code"], "name": t["name"]} for t in u["types"]],
        })
    out = {"version": draft["version"], "note": draft["note"], "units": units}
    DST.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"단원 {len(units)}개 -> {DST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
