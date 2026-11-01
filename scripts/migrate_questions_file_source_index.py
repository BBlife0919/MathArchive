#!/usr/bin/env python3
"""questions(file_source, question_number) 복합 인덱스 추가.

file_source + question_number 로 특정 문항을 찾는 조회(백필 스크립트,
sync 스크립트 등 여러 곳에서 사용)에 인덱스가 전혀 없어서 매번
174,874행 전체를 순차 스캔(Seq Scan)하고 있었다 — 운영 Postgres에서
쿼리 1건에 10초 이상 걸려, scripts/backfill_eq_parser_fixes.py 의
문항당 수 회 반복 조회가 거의 전부 statement_timeout/연결끊김으로
실패하던 근본 원인(2026-10-31 발견). 로컬 SQLite는 파일 I/O가 로컬이라
느려도 버틸 만했지만 네트워크를 거치는 운영에서는 치명적이었다.

실행:
    python scripts/migrate_questions_file_source_index.py --local
    python scripts/migrate_questions_file_source_index.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))


def _load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


DDL = (
    "CREATE INDEX IF NOT EXISTS idx_questions_file_source "
    "ON questions(file_source, question_number)"
)


def migrate(force_local: bool = False) -> None:
    if force_local:
        os.environ.pop("SUPABASE_DB_URL", None)
    else:
        _load_env_file()

    from db import get_connection, is_cloud  # noqa: E402

    cloud = is_cloud()
    conn = get_connection()
    conn.execute(DDL)
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass

    target = "Supabase Postgres" if cloud else "로컬 SQLite"
    print(f"[OK] idx_questions_file_source 인덱스 생성 완료 → {target}")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--local", action="store_true", help="강제로 SQLite(운영 DB 안 건드림)")
    args = ap.parse_args()
    migrate(force_local=args.local)


if __name__ == "__main__":
    main()
