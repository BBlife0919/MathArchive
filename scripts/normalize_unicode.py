#!/usr/bin/env python3
"""DB 텍스트 컬럼 NFC 정규화 — NFD/NFC 혼재로 같은 글자가 다른 키로 분류되는
문제 해결.

근본 원인: macOS 파일시스템(HFS+/APFS) 의 한글 파일명이 NFD 로 보존돼 있어,
파서가 zip 항목명을 그대로 region/school 로 추출할 때 NFD 가 들어감. 같은
'경기김포시' 가 NFC 5 코드포인트와 NFD 12 코드포인트 두 가지로 DB 에
동시에 적재됨.

사용법:
    python3 scripts/normalize_unicode.py            # 미리보기
    python3 scripts/normalize_unicode.py --apply
"""
from __future__ import annotations

import argparse
import sqlite3
import unicodedata
from collections import Counter

# 정규화 대상 (table, [columns])
# image_path 는 R2 객체 키와 정합성 검증 필요해 이 스크립트에서는 제외.
TARGETS = [
    ("questions", [
        "file_source", "school", "region", "subject",
        "school_level", "chapter", "chapter_range",
        "exam_type", "difficulty",
    ]),
    ("solutions", []),
    ("images", ["image_ref"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/mathdb.sqlite")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    grand = 0
    for table, cols in TARGETS:
        if not cols:
            continue
        idcol = cur.execute(
            f"SELECT name FROM pragma_table_info('{table}') "
            f"WHERE pk=1"
        ).fetchone()[0]
        for col in cols:
            rows = cur.execute(
                f"SELECT {idcol}, {col} FROM {table} WHERE {col} IS NOT NULL"
            ).fetchall()
            changed = 0
            sample = []
            for rid, val in rows:
                nfc = unicodedata.normalize("NFC", val)
                if nfc != val:
                    changed += 1
                    if len(sample) < 3:
                        sample.append((rid, val, nfc))
                    if args.apply:
                        cur.execute(
                            f"UPDATE {table} SET {col}=? WHERE {idcol}=?",
                            (nfc, rid),
                        )
            if changed:
                print(f"  [{table}.{col}] {changed}건 NFC 변환")
                for rid, before, after in sample:
                    print(f"    {idcol}={rid}: len {len(before)}→{len(after)} "
                          f"({before!r:30s} → {after!r:30s})")
                grand += changed

    if args.apply:
        conn.commit()
        print(f"\n✅ 적용 완료. 총 {grand}건 갱신.")
    else:
        print(f"\n[미리보기] 총 {grand}건 변경 예정.")
    conn.close()


if __name__ == "__main__":
    main()
