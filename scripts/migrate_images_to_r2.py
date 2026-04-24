#!/usr/bin/env python3
"""images/ → Cloudflare R2 이관 + DB `image_path` URL 업데이트.

선행 조건:
- .env 설정
- pip install boto3 python-dotenv
"""
from __future__ import annotations

import os
import sys
import sqlite3
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

import boto3
from botocore.config import Config

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / "images"
SQLITE_DB = BASE_DIR / "db" / "mathdb.sqlite"

R2_ACCESS_KEY = os.environ.get("R2_ACCESS_KEY_ID")
R2_SECRET_KEY = os.environ.get("R2_SECRET_ACCESS_KEY")
R2_ENDPOINT = os.environ.get("R2_ENDPOINT")
R2_BUCKET = os.environ.get("R2_BUCKET")
R2_PUBLIC = os.environ.get("R2_PUBLIC_URL")


def make_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        config=Config(signature_version="s3v4", region_name="auto"),
    )


def upload_all(dry_run: bool = False) -> dict:
    """images/ 모든 파일을 R2로 업로드. 이미 존재하는 것은 skip."""
    if not all([R2_ACCESS_KEY, R2_SECRET_KEY, R2_ENDPOINT, R2_BUCKET, R2_PUBLIC]):
        print("ERROR: R2 환경변수 누락", file=sys.stderr)
        sys.exit(2)
    if not IMAGES_DIR.exists():
        print(f"ERROR: {IMAGES_DIR} 없음", file=sys.stderr)
        sys.exit(2)

    s3 = make_client()

    # 기존 버킷 객체 목록 (skip 판정용)
    existing = set()
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=R2_BUCKET):
        for obj in page.get("Contents", []):
            existing.add(obj["Key"])
    print(f"기존 R2 객체: {len(existing):,}")

    files = sorted(IMAGES_DIR.iterdir())
    total = len(files)
    print(f"업로드 대상: {total:,}")

    url_map: dict[str, str] = {}  # local_path → public url
    uploaded = 0
    skipped = 0
    for i, p in enumerate(files, 1):
        if not p.is_file():
            continue
        # 키 = 파일명 그대로
        key = p.name
        public_url = f"{R2_PUBLIC.rstrip('/')}/{key}"
        url_map[str(p)] = public_url
        url_map[f"images/{key}"] = public_url

        if key in existing:
            skipped += 1
            continue

        if dry_run:
            uploaded += 1
            continue

        # content-type 추론
        import mimetypes
        ct = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        try:
            s3.upload_file(
                Filename=str(p),
                Bucket=R2_BUCKET,
                Key=key,
                ExtraArgs={"ContentType": ct},
            )
            uploaded += 1
        except Exception as e:
            print(f"  ERROR {key}: {e}", file=sys.stderr)
            continue

        if i % 200 == 0:
            print(f"  [{i:,}/{total:,}] 업로드 {uploaded:,} / 스킵 {skipped:,}")

    print(f"\n업로드 완료: {uploaded:,} / 스킵 {skipped:,} / 총 {total:,}")
    return url_map


def update_db(url_map: dict, target: str = "sqlite") -> None:
    """DB의 image_path를 공개 URL로 업데이트.

    target = 'sqlite' 또는 'postgres'
    """
    if target == "sqlite":
        conn = sqlite3.connect(str(SQLITE_DB))
        cur = conn.cursor()
        rows = cur.execute("SELECT image_id, image_path FROM images").fetchall()
        updated = 0
        for iid, p in rows:
            if not p:
                continue
            new = url_map.get(p)
            if not new:
                # 상대 경로일 수 있음 — images/ prefix 추가해서 재시도
                new = url_map.get(f"images/{Path(p).name}")
            if new and new != p:
                cur.execute(
                    "UPDATE images SET image_path = ? WHERE image_id = ?",
                    (new, iid),
                )
                updated += 1
        conn.commit()
        conn.close()
        print(f"SQLite images.image_path 업데이트: {updated:,}건")
    elif target == "postgres":
        try:
            from dotenv import load_dotenv
            load_dotenv(BASE_DIR / ".env")
        except ImportError:
            pass
        import psycopg2
        pg_url = os.environ.get("SUPABASE_DB_URL")
        if not pg_url or "[YOUR-PASSWORD]" in pg_url:
            print("SKIP postgres 업데이트 — SUPABASE_DB_URL 미설정", file=sys.stderr)
            return
        conn = psycopg2.connect(pg_url)
        cur = conn.cursor()
        cur.execute("SELECT image_id, image_path FROM images")
        rows = cur.fetchall()
        updated = 0
        for iid, p in rows:
            if not p:
                continue
            new = url_map.get(p)
            if not new:
                new = url_map.get(f"images/{Path(p).name}")
            if new and new != p:
                cur.execute(
                    "UPDATE images SET image_path = %s WHERE image_id = %s",
                    (new, iid),
                )
                updated += 1
        conn.commit()
        cur.close()
        conn.close()
        print(f"Postgres images.image_path 업데이트: {updated:,}건")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--target", default="both",
                    choices=["sqlite", "postgres", "both"])
    ap.add_argument("--upload-only", action="store_true")
    args = ap.parse_args()

    url_map = upload_all(dry_run=args.dry_run)
    if args.dry_run or args.upload_only:
        return

    if args.target in ("sqlite", "both"):
        update_db(url_map, target="sqlite")
    if args.target in ("postgres", "both"):
        update_db(url_map, target="postgres")


if __name__ == "__main__":
    main()
