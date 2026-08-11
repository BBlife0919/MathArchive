#!/usr/bin/env python3
"""sync_new_to_cloud.py 의 R2 listing 우회 버전.

이전 버전은 boto3 list_objects_v2 페이지네이션 단계에서 silent hang/crash 발생.
이 버전은 listing 을 건너뛰고 신규 file_source 에 연관된 이미지만 head_object
로 개별 존재 확인 → 없으면 PUT. 작업량을 신규 file_source 범위로 한정.

사용:
    python3 scripts/sync_new_to_cloud_v2.py --dry-run
    python3 scripts/sync_new_to_cloud_v2.py
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQLITE_DB = ROOT / "db" / "mathdb.sqlite"
IMAGES_DIR = ROOT / "images"

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass


def _make_r2():
    import boto3
    from botocore.config import Config
    return boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        config=Config(signature_version="s3v4", region_name="auto"),
    )


def _r2_url(key: str) -> str:
    return f"{os.environ['R2_PUBLIC_URL'].rstrip('/')}/{key}"


def _open_pg():
    import psycopg2
    from psycopg2.extras import DictCursor
    return psycopg2.connect(os.environ["SUPABASE_DB_URL"],
                            cursor_factory=DictCursor)


def _image_keys_for_new(sconn, new_fs: list[str]) -> dict[int, list[str]]:
    """{question_id → [image_path 리스트]} for 신규 file_source.

    image_path 는 SQLite 에 저장된 raw 값 (절대경로/상대경로).
    """
    if not new_fs:
        return {}
    placeholders = ",".join("?" * len(new_fs))
    rows = sconn.execute(
        f"SELECT i.question_id, i.image_path "
        f"FROM images i "
        f"JOIN questions q ON i.question_id = q.question_id "
        f"WHERE q.file_source IN ({placeholders})",
        new_fs,
    ).fetchall()
    out: dict[int, list[str]] = {}
    for r in rows:
        out.setdefault(r[0], []).append(r[1])
    return out


def _upload_one(s3, bucket: str, local_path: Path, key: str) -> bool:
    """없으면 업로드. 이미 있으면 skip. 반환: 실제 업로드 여부."""
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return False
    except Exception:
        pass
    ct = mimetypes.guess_type(str(local_path))[0] or "application/octet-stream"
    s3.upload_file(str(local_path), bucket, key,
                    ExtraArgs={"ContentType": ct})
    return True


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
    print(f"클라우드: {len(cloud_fs)}, 로컬: {len(local_fs)}, 신규: {len(new_fs)}",
          flush=True)
    if not new_fs:
        print("→ 동기화할 신규 없음", flush=True)
        return

    # 2) 신규 file_source 에 속한 images.image_path 들만 R2 업로드
    img_map = _image_keys_for_new(sconn, new_fs)
    all_paths: set[str] = set()
    for paths in img_map.values():
        for p in paths:
            if p:
                all_paths.add(p)
    print(f"[R2] 처리 대상 이미지: {len(all_paths)}건", flush=True)

    url_map: dict[str, str] = {}  # 원본 image_path → R2 public URL
    bucket = os.environ["R2_BUCKET"]

    if dry_run:
        for p in all_paths:
            name = Path(p).name
            url_map[p] = _r2_url(name)
        print(f"  [DRY-RUN] 업로드 예정 (head_object 안 함)", flush=True)
    else:
        s3 = _make_r2()
        uploaded = skipped = missing = 0
        for i, raw_p in enumerate(sorted(all_paths), 1):
            name = Path(raw_p).name
            key = name
            # 로컬 파일 위치 — raw_p 가 절대/상대/URL 다양
            if raw_p.startswith("http"):
                url_map[raw_p] = raw_p
                continue
            local = Path(raw_p)
            if not local.exists():
                local = IMAGES_DIR / name
            if not local.exists():
                missing += 1
                continue
            try:
                did = _upload_one(s3, bucket, local, key)
            except Exception as e:
                print(f"  ERROR {key}: {e}", flush=True)
                continue
            url_map[raw_p] = _r2_url(key)
            if did:
                uploaded += 1
            else:
                skipped += 1
            if i % 50 == 0:
                print(f"  [{i}/{len(all_paths)}] up={uploaded} skip={skipped} "
                      f"miss={missing}", flush=True)
        print(f"  R2 완료: 업로드={uploaded}, skip={skipped}, miss={missing}",
              flush=True)

    # 3) Postgres 에 questions / solutions / images INSERT
    from psycopg2.extras import execute_values, Json
    placeholders = ",".join("?" * len(new_fs))
    s_rows = list(sconn.execute(
        f"SELECT * FROM questions WHERE file_source IN ({placeholders})",
        new_fs,
    ))
    print(f"[questions] {len(s_rows)}", flush=True)
    insert_cols = [c for c in s_rows[0].keys() if c != "question_id"]
    qid_map: dict[int, int] = {}

    if dry_run:
        print(f"  [DRY-RUN] {len(s_rows)} INSERT 예정", flush=True)
    else:
        values = []
        sqlite_qids = []
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
            sqlite_qids.append(r["question_id"])
        returned = execute_values(
            pcur,
            f"INSERT INTO questions ({','.join(insert_cols)}) "
            f"VALUES %s RETURNING question_id",
            values, page_size=500, fetch=True,
        )
        # execute_values(fetch=True) 는 결과를 반환값으로 주고 커서 결과셋은
        # 이미 소비한 상태라, 별도 pcur.fetchall() 을 또 호출하면 빈 리스트가
        # 나와서 qid_map 이 통째로 비는 버그가 있었음(2026-08-11 발견 — 314개
        # 파일 6751문항이 해설·이미지 연결 없이 들어간 사고로 발견함).
        for sq, pg_row in zip(sqlite_qids, returned):
            qid_map[sq] = pg_row[0]
        pconn.commit()
        print(f"  questions INSERT 완료: {len(qid_map)}", flush=True)

    # solutions
    s_sol = list(sconn.execute(
        f"SELECT * FROM solutions WHERE question_id IN ("
        f"  SELECT question_id FROM questions WHERE file_source IN ({placeholders}))",
        new_fs,
    ))
    print(f"[solutions] {len(s_sol)}", flush=True)
    if dry_run:
        print(f"  [DRY-RUN] {len(s_sol)} INSERT 예정", flush=True)
    elif s_sol:
        sol_cols = [c for c in s_sol[0].keys() if c != "solution_id"]
        sol_values = []
        for r in s_sol:
            d = dict(r)
            pgid = qid_map.get(d["question_id"])
            if pgid is None:
                continue
            d["question_id"] = pgid
            sol_values.append(tuple(d.get(c) for c in sol_cols))
        execute_values(
            pcur,
            f"INSERT INTO solutions ({','.join(sol_cols)}) VALUES %s",
            sol_values, page_size=500,
        )
        pconn.commit()
        print(f"  solutions INSERT 완료: {len(sol_values)}", flush=True)

    # images
    s_img = list(sconn.execute(
        f"SELECT * FROM images WHERE question_id IN ("
        f"  SELECT question_id FROM questions WHERE file_source IN ({placeholders}))",
        new_fs,
    ))
    print(f"[images] {len(s_img)}", flush=True)
    if dry_run:
        print(f"  [DRY-RUN] {len(s_img)} INSERT 예정", flush=True)
    elif s_img:
        img_cols = [c for c in s_img[0].keys() if c != "image_id"]
        img_values = []
        for r in s_img:
            d = dict(r)
            pgid = qid_map.get(d["question_id"])
            if pgid is None:
                continue
            d["question_id"] = pgid
            raw = d.get("image_path") or ""
            d["image_path"] = url_map.get(raw, raw)
            img_values.append(tuple(d.get(c) for c in img_cols))
        execute_values(
            pcur,
            f"INSERT INTO images ({','.join(img_cols)}) VALUES %s",
            img_values, page_size=500,
        )
        pconn.commit()
        print(f"  images INSERT 완료: {len(img_values)}", flush=True)

    pconn.close()
    sconn.close()
    print("\n✅ 동기화 완료" if not dry_run else "\n[DRY-RUN] 완료",
          flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sync(args.dry_run)


if __name__ == "__main__":
    main()
