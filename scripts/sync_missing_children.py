#!/usr/bin/env python3
"""sync_new_to_cloud_v2 의 qid_map 누락 사고 복구.

questions 는 잘 적재됐는데 solutions/images 가 0건 INSERT 된 상태에서,
cloud questions 의 (file_source, question_number) → question_id 매핑을
다시 구성해서 SQLite 의 solutions/images 를 cloud 로 INSERT.

R2 업로드는 이미 끝났으므로 image_path 만 R2 URL 로 변환.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQLITE_DB = ROOT / "db" / "mathdb.sqlite"

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass


def _r2_url(key: str) -> str:
    return f"{os.environ['R2_PUBLIC_URL'].rstrip('/')}/{key}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    import psycopg2
    from psycopg2.extras import execute_values, DictCursor

    sconn = sqlite3.connect(str(SQLITE_DB))
    sconn.row_factory = sqlite3.Row

    pconn = psycopg2.connect(os.environ["SUPABASE_DB_URL"],
                              cursor_factory=DictCursor)
    pcur = pconn.cursor()

    # 1) cloud 의 (file_source, qnum) → pg_qid 매핑 (전체)
    print("cloud questions 매핑 로딩...", flush=True)
    pcur.execute("SELECT question_id, file_source, question_number "
                 "FROM questions")
    cloud_map: dict[tuple, int] = {}
    for r in pcur.fetchall():
        cloud_map[(r[1], r[2])] = r[0]
    print(f"  {len(cloud_map)} 항목", flush=True)

    # 2) cloud 에 이미 있는 (question_id) 집합 — solutions/images 중복 방지
    pcur.execute("SELECT DISTINCT question_id FROM solutions")
    sol_existing = {r[0] for r in pcur.fetchall()}
    pcur.execute("SELECT DISTINCT question_id FROM images")
    img_existing = {r[0] for r in pcur.fetchall()}
    print(f"cloud solutions 보유 qid: {len(sol_existing)}", flush=True)
    print(f"cloud images 보유 qid: {len(img_existing)}", flush=True)

    # 3) SQLite 의 solutions / images → cloud 매핑
    s_sol = list(sconn.execute(
        "SELECT s.*, q.file_source, q.question_number "
        "FROM solutions s JOIN questions q ON s.question_id = q.question_id"
    ))
    s_img = list(sconn.execute(
        "SELECT i.*, q.file_source, q.question_number "
        "FROM images i JOIN questions q ON i.question_id = q.question_id"
    ))

    sol_to_insert = []
    sol_skipped_already = 0
    sol_missing_qid = 0
    for r in s_sol:
        key = (r["file_source"], r["question_number"])
        pg_qid = cloud_map.get(key)
        if pg_qid is None:
            sol_missing_qid += 1
            continue
        if pg_qid in sol_existing:
            sol_skipped_already += 1
            continue
        d = dict(r)
        d["question_id"] = pg_qid
        sol_to_insert.append(d)

    img_to_insert = []
    img_skipped_already = 0
    img_missing_qid = 0
    for r in s_img:
        key = (r["file_source"], r["question_number"])
        pg_qid = cloud_map.get(key)
        if pg_qid is None:
            img_missing_qid += 1
            continue
        if pg_qid in img_existing:
            img_skipped_already += 1
            continue
        d = dict(r)
        d["question_id"] = pg_qid
        # image_path R2 URL 변환
        raw = d.get("image_path") or ""
        if raw and not raw.startswith("http"):
            d["image_path"] = _r2_url(Path(raw).name)
        img_to_insert.append(d)

    print(f"\n[solutions] 누락 INSERT 대상: {len(sol_to_insert)}, "
          f"이미존재 skip: {sol_skipped_already}, "
          f"qid 매핑실패: {sol_missing_qid}", flush=True)
    print(f"[images]    누락 INSERT 대상: {len(img_to_insert)}, "
          f"이미존재 skip: {img_skipped_already}, "
          f"qid 매핑실패: {img_missing_qid}", flush=True)

    if args.dry_run:
        print("\n[DRY-RUN] INSERT 미실행", flush=True)
        return

    # 4) INSERT
    if sol_to_insert:
        sol_cols = [c for c in sol_to_insert[0].keys()
                    if c not in ("solution_id", "file_source", "question_number")]
        values = [tuple(d.get(c) for c in sol_cols) for d in sol_to_insert]
        execute_values(
            pcur,
            f"INSERT INTO solutions ({','.join(sol_cols)}) VALUES %s",
            values, page_size=500,
        )
        pconn.commit()
        print(f"✅ solutions INSERT 완료: {len(values)}", flush=True)

    if img_to_insert:
        img_cols = [c for c in img_to_insert[0].keys()
                    if c not in ("image_id", "file_source", "question_number")]
        values = [tuple(d.get(c) for c in img_cols) for d in img_to_insert]
        execute_values(
            pcur,
            f"INSERT INTO images ({','.join(img_cols)}) VALUES %s",
            values, page_size=500,
        )
        pconn.commit()
        print(f"✅ images INSERT 완료: {len(values)}", flush=True)

    pconn.close()
    sconn.close()


if __name__ == "__main__":
    main()
