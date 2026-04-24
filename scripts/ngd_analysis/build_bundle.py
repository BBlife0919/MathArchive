"""라벨링 에이전트에게 넘길 문항 번들 생성."""

import json
import sqlite3

PARSED = "/Users/youngwoolee/MathDB/scripts/ngd_analysis/parsed.json"
OUT = "/Users/youngwoolee/MathDB/scripts/ngd_analysis/label_bundle.json"
DB = "/Users/youngwoolee/MathDB/db/mathdb.sqlite"

TARGETS = {"다항식의 연산", "항등식과 나머지정리", "인수분해", "복소수", "이차방정식", "이차함수"}


def main() -> None:
    items = json.load(open(PARSED))
    flt = [it for it in items if it["chapter"] in TARGETS and it["difficulty"] in {"중", "하"}]

    con = sqlite3.connect(DB)
    bundle = []
    for idx, it in enumerate(flt):
        src_hwpx = it["source"].replace(".pdf", ".hwpx")
        row = con.execute(
            "SELECT question_text, choices FROM questions WHERE file_source=? AND question_number=?",
            (src_hwpx, it["number"]),
        ).fetchone()
        db_text = None
        db_choices = None
        if row:
            db_text, db_choices = row
        # PDF prose 정리 — 빈줄/반복공백 제거
        prose = " ".join(it["text"].split())
        if len(prose) > 400:
            prose = prose[:400] + "..."
        payload = {
            "idx": idx,
            "chapter": it["chapter"],
            "difficulty": it["difficulty"],
            "number": it["number"],
            "source": it["source"],
            "prose": prose,
            "db_text": (db_text[:500] if db_text else None),
        }
        bundle.append(payload)

    with open(OUT, "w") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)
    print(f"wrote {len(bundle)} items to {OUT}")


if __name__ == "__main__":
    main()
