#!/usr/bin/env python3
"""R2 미완료분을 병렬 업로드로 마무리 + DB URL 업데이트.

순차 업로드로 정체된 상황 대응. ThreadPoolExecutor 30 workers.
"""
from __future__ import annotations

import mimetypes
import os
import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import boto3
from botocore.config import Config

BASE = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE / "images"
SQLITE_DB = BASE / "db" / "mathdb.sqlite"

R2_BUCKET = os.environ["R2_BUCKET"]
R2_PUBLIC = os.environ["R2_PUBLIC_URL"].rstrip("/")


def make_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        config=Config(
            signature_version="s3v4",
            region_name="auto",
            connect_timeout=10,
            read_timeout=30,
            retries={"max_attempts": 3},
            max_pool_connections=50,
        ),
    )


def upload_one(s3, path: Path) -> tuple[str, bool, str]:
    key = path.name
    ct = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    try:
        s3.upload_file(str(path), R2_BUCKET, key, ExtraArgs={"ContentType": ct})
        return (key, True, "")
    except Exception as e:
        return (key, False, str(e)[:80])


def main():
    s3 = make_client()

    # 1) R2 기존 키 수집
    print("R2 기존 객체 수집 중...", file=sys.stderr)
    existing = set()
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=R2_BUCKET):
        for obj in page.get("Contents", []):
            existing.add(obj["Key"])
    print(f"  기존: {len(existing):,}", file=sys.stderr)

    # 2) 로컬 파일 수집 (R2에 없는 것만)
    local_files = [p for p in IMAGES_DIR.iterdir() if p.is_file()]
    print(f"로컬: {len(local_files):,}", file=sys.stderr)
    missing = [p for p in local_files if p.name not in existing]
    print(f"업로드 대상: {len(missing):,}", file=sys.stderr)

    # 3) 병렬 업로드
    ok = 0
    fail = 0
    errors = []
    with ThreadPoolExecutor(max_workers=30) as ex:
        futures = {ex.submit(upload_one, s3, p): p for p in missing}
        for i, fut in enumerate(as_completed(futures), 1):
            key, success, err = fut.result()
            if success:
                ok += 1
            else:
                fail += 1
                errors.append((key, err))
            if i % 200 == 0 or i == len(missing):
                print(f"  진행 {i:,}/{len(missing):,} | 성공 {ok:,} / 실패 {fail}",
                      file=sys.stderr)

    print(f"\n완료: 성공 {ok:,} / 실패 {fail}", file=sys.stderr)
    if errors[:5]:
        print("에러 샘플:", file=sys.stderr)
        for k, e in errors[:5]:
            print(f"  {k}: {e}", file=sys.stderr)

    # 4) DB URL 업데이트
    print("\nSQLite DB URL 업데이트 중...", file=sys.stderr)
    conn = sqlite3.connect(str(SQLITE_DB))
    cur = conn.cursor()
    rows = cur.execute("SELECT image_id, image_path FROM images").fetchall()
    updated = 0
    for iid, p in rows:
        if not p:
            continue
        # p가 파일 경로면 filename만 뽑음
        fname = Path(p).name
        if fname in existing or any(f.name == fname for f in missing if
                                     not any(e[0] == fname for e in errors)):
            new = f"{R2_PUBLIC}/{fname}"
            if new != p:
                cur.execute(
                    "UPDATE images SET image_path = ? WHERE image_id = ?",
                    (new, iid),
                )
                updated += 1
    conn.commit()
    conn.close()
    print(f"SQLite image_path 업데이트: {updated:,}건", file=sys.stderr)


if __name__ == "__main__":
    main()
