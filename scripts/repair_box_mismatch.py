#!/usr/bin/env python3
"""DB 클린업 — BOX 짝이 안 맞는 문항을 원본 HWPX 에서 재파싱해 복구.

근본 원인: 구버전 _strip_choices_from_text 가 첫 ⃝번호에서 텍스트를 잘랐는데,
선지 그리드 표(예: ① 제2사분면 / ② 제3사분면 형태) 의 ⃝번호는 표 안 셀이
어서 표 중간에서 텍스트가 잘리고 BOX_END 가 함께 사라졌다. 파서는 이미
수정됨. 이 스크립트는 영향 받은 196개 파일만 재파싱해 question_text 와
choices, has_image 필드를 갱신한다.

사용법:
    python3 scripts/repair_box_mismatch.py            # 미리보기
    python3 scripts/repair_box_mismatch.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_hwpx import parse_hwpx


def find_affected_files(cur) -> list:
    rows = cur.execute("""
        SELECT DISTINCT file_source FROM questions
        WHERE (length(question_text) - length(replace(question_text, '<<BOX_START>>', '')))
              / length('<<BOX_START>>')
           != (length(question_text) - length(replace(question_text, '<<BOX_END>>', '')))
              / length('<<BOX_END>>')
    """).fetchall()
    return [r[0] for r in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/mathdb.sqlite")
    ap.add_argument("--raw", default="raw/")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0,
                    help="처리 파일 수 제한 (디버깅)")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    file_sources = find_affected_files(cur)
    print(f"영향 파일 {len(file_sources)}개")

    if args.limit:
        file_sources = file_sources[:args.limit]

    tmp_img_dir = tempfile.mkdtemp(prefix="repair_box_")
    repaired_q = 0
    failed_files = []

    for i, fs in enumerate(file_sources, 1):
        path = Path(args.raw) / fs
        if not path.exists():
            failed_files.append((fs, "파일 없음"))
            continue
        try:
            result = parse_hwpx(str(path), image_output_dir=tmp_img_dir)
        except Exception as e:
            failed_files.append((fs, f"파싱 실패: {e}"))
            continue

        # 같은 file_source 행 중 box_mismatch 인 행만 갱신 대상으로 (다른
        # 행에 가해진 fix_nested_boxes / fix_unmapped_hwp_tokens 등 사후
        # 보정을 덮어쓰지 않기 위해)
        db_rows = cur.execute(
            "SELECT question_id, question_number, question_text FROM questions "
            "WHERE file_source=? ORDER BY question_number",
            (fs,),
        ).fetchall()
        db_map = {}
        for qid, qn, qt in db_rows:
            qt = qt or ""
            if qt.count("<<BOX_START>>") != qt.count("<<BOX_END>>"):
                db_map[qn] = qid

        # 새 파싱 결과를 question_number 로 매칭
        for q in result["questions"]:
            qn = q["question_number"]
            qid = db_map.get(qn)
            if qid is None:
                continue
            new_text = q.get("question_text") or ""
            new_choices = q.get("choices") or []
            new_has_image = 1 if q.get("has_image") else 0
            if args.apply:
                cur.execute(
                    "UPDATE questions SET question_text=?, choices=?, "
                    "has_image=? WHERE question_id=?",
                    (new_text, json.dumps(new_choices, ensure_ascii=False),
                     new_has_image, qid),
                )
            repaired_q += 1

        if i % 20 == 0:
            print(f"  {i}/{len(file_sources)}  파싱 진행")

    if args.apply:
        conn.commit()
    conn.close()

    print(f"\n복구 대상 question 수: {repaired_q}")
    if failed_files:
        print(f"실패 {len(failed_files)}건:")
        for fs, reason in failed_files[:5]:
            print(f"  - {fs[:80]}  ({reason})")
    if not args.apply:
        print("\n[미리보기] --apply 로 실제 반영.")
    else:
        print("\n✅ 적용 완료.")


if __name__ == "__main__":
    main()
