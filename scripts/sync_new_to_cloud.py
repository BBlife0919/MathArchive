#!/usr/bin/env python3
"""SQLite 에 새로 적재된 file_source 의 questions/solutions/images 를
Supabase Postgres 로 증분 동기화 + 이미지는 R2 로 업로드.

전체 재이관(migrate_to_supabase.py 의 DROP+재이관) 과 달리 신규 행만 추가.

사용:
    python3 scripts/sync_new_to_cloud.py --dry-run
    python3 scripts/sync_new_to_cloud.py
"""
from __future__ import annotations

import argparse
import json
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


def _open_pg():
    import psycopg2
    from psycopg2.extras import DictCursor
    dsn = os.environ["SUPABASE_DB_URL"]
    conn = psycopg2.connect(dsn, cursor_factory=DictCursor)
    conn.autocommit = False
    return conn


def _upload_new_images(dry_run: bool) -> dict:
    """images/ 디렉토리의 신규 파일을 R2 로 업로드.

    반환: local_path/relative_path → public R2 URL 매핑.
    이미 R2 에 있는 파일은 매핑만 채우고 업로드 skip.
    """
    import sys as _s
    _s.path.insert(0, str(ROOT / "scripts"))
    from migrate_images_to_r2 import upload_all
    return upload_all(dry_run=dry_run)


def _resolve_image_path(raw_path: str, url_map: dict) -> str:
    """SQLite 의 image_path 를 R2 URL 로 변환.

    raw_path 형태가 절대경로/상대경로/이미 URL 다양함. URL 이면 그대로,
    파일경로면 url_map 에서 찾음.
    """
    if not raw_path:
        return raw_path
    if raw_path.startswith("http://") or raw_path.startswith("https://"):
        return raw_path
    # 절대경로
    if raw_path in url_map:
        return url_map[raw_path]
    # 상대경로
    rel = f"images/{Path(raw_path).name}"
    if rel in url_map:
        return url_map[rel]
    # 매핑 못 찾음 → 원본 보존 (cloud 에서 깨질 위험 있음)
    return raw_path


def sync(dry_run: bool):
    sconn = sqlite3.connect(str(SQLITE_DB))
    sconn.row_factory = sqlite3.Row

    pconn = _open_pg()
    pcur = pconn.cursor()

    # 1) 신규 file_source 집합
    pcur.execute("SELECT DISTINCT file_source FROM questions")
    cloud_fs = {r[0] for r in pcur.fetchall()}
    local_fs = {r[0] for r in sconn.execute(
        "SELECT DISTINCT file_source FROM questions"
    )}
    new_fs = sorted(local_fs - cloud_fs)
    print(f"클라우드 file_source: {len(cloud_fs)}")
    print(f"로컬 file_source: {len(local_fs)}")
    print(f"신규 sync 대상: {len(new_fs)}")
    if not new_fs:
        print("→ 동기화할 신규 파일 없음")
        pconn.close()
        sconn.close()
        return

    # 2) R2 업로드 (URL map 확보)
    print("\n[R2] 이미지 업로드...")
    url_map = _upload_new_images(dry_run=dry_run)

    # 3) 신규 questions 추출 + Postgres INSERT
    placeholders = ",".join("?" * len(new_fs))
    s_rows = list(sconn.execute(
        f"SELECT * FROM questions WHERE file_source IN ({placeholders})",
        new_fs,
    ))
    print(f"\n[questions] {len(s_rows)} 행")

    # Postgres INSERT — question_id 는 SERIAL 새 할당, RETURNING 으로 매핑
    from psycopg2.extras import execute_values, Json
    insert_cols = [c for c in s_rows[0].keys() if c != "question_id"]
    placeholders_pg = ",".join(["%s"] * len(insert_cols))

    qid_map: dict[int, int] = {}  # sqlite_qid → pg_qid

    if dry_run:
        print(f"  [DRY-RUN] questions 신규 {len(s_rows)} 행 INSERT 예정")
    else:
        values = []
        sqlite_qids_ordered = []
        for r in s_rows:
            d = dict(r)
            ch = d.get("choices")
            if ch and isinstance(ch, str):
                try:
                    d["choices"] = Json(json.loads(ch))
                except Exception:
                    d["choices"] = None
            elif ch is None:
                d["choices"] = None
            values.append(tuple(d.get(c) for c in insert_cols))
            sqlite_qids_ordered.append(r["question_id"])
        sql = (
            f"INSERT INTO questions ({','.join(insert_cols)}) "
            f"VALUES %s RETURNING question_id"
        )
        execute_values(pcur, sql, values, template=None, page_size=500,
                        fetch=True)
        returned = pcur.fetchall()
        # RETURNING 순서는 INSERT 순서와 동일 (Postgres 보장)
        for s_qid, row in zip(sqlite_qids_ordered, returned):
            qid_map[s_qid] = row[0]
        pconn.commit()
        print(f"  questions INSERT 완료: {len(qid_map)} 행")

    # 4) 신규 solutions
    s_sol = list(sconn.execute(
        f"SELECT * FROM solutions WHERE question_id IN ("
        f"SELECT question_id FROM questions WHERE file_source IN ({placeholders})"
        f")",
        new_fs,
    ))
    print(f"[solutions] {len(s_sol)} 행")
    if not dry_run and s_sol:
        sol_cols = [c for c in s_sol[0].keys() if c != "solution_id"]
        sol_values = []
        for r in s_sol:
            d = dict(r)
            pg_qid = qid_map.get(d["question_id"])
            if pg_qid is None:
                continue
            d["question_id"] = pg_qid
            sol_values.append(tuple(d.get(c) for c in sol_cols))
        execute_values(
            pcur,
            f"INSERT INTO solutions ({','.join(sol_cols)}) VALUES %s",
            sol_values, page_size=500,
        )
        pconn.commit()
        print(f"  solutions INSERT 완료: {len(sol_values)} 행")
    elif dry_run:
        print(f"  [DRY-RUN] solutions 신규 {len(s_sol)} 행 INSERT 예정")

    # 5) 신규 images
    s_img = list(sconn.execute(
        f"SELECT * FROM images WHERE question_id IN ("
        f"SELECT question_id FROM questions WHERE file_source IN ({placeholders})"
        f")",
        new_fs,
    ))
    print(f"[images] {len(s_img)} 행")
    if not dry_run and s_img:
        img_cols = [c for c in s_img[0].keys() if c != "image_id"]
        img_values = []
        for r in s_img:
            d = dict(r)
            pg_qid = qid_map.get(d["question_id"])
            if pg_qid is None:
                continue
            d["question_id"] = pg_qid
            # image_path → R2 URL 변환
            d["image_path"] = _resolve_image_path(d.get("image_path") or "",
                                                  url_map)
            img_values.append(tuple(d.get(c) for c in img_cols))
        execute_values(
            pcur,
            f"INSERT INTO images ({','.join(img_cols)}) VALUES %s",
            img_values, page_size=500,
        )
        pconn.commit()
        print(f"  images INSERT 완료: {len(img_values)} 행")
    elif dry_run:
        print(f"  [DRY-RUN] images 신규 {len(s_img)} 행 INSERT 예정")

    pconn.close()
    sconn.close()
    print("\n✅ 증분 동기화 완료" if not dry_run else "\n[DRY-RUN] 완료")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sync(args.dry_run)


if __name__ == "__main__":
    main()
