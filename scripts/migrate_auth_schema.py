#!/usr/bin/env python3
"""scripts/auth_schema.sql 을 Supabase Postgres 에 적용.

실행:
    SUPABASE_DB_URL=postgresql://... python scripts/migrate_auth_schema.py

또는 .env 가 자동 로드되는 환경이면 그대로:
    python scripts/migrate_auth_schema.py

주의:
- Supabase Dashboard SQL Editor 에 직접 붙여넣어도 됨 (auth_schema.sql)
- 멱등 (반복 실행 안전). 단, 정책은 DROP 후 재생성하므로 잠깐 비어있는 순간 존재
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQL_PATH = ROOT / "scripts" / "auth_schema.sql"


def main():
    # .env 자동 로드 (있으면)
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip().startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL 환경변수 또는 .env 설정 필요", file=sys.stderr)
        sys.exit(1)

    sql = SQL_PATH.read_text(encoding="utf-8")

    import psycopg2
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(sql)
        print(f"[OK] {SQL_PATH.name} 적용 완료")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(2)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
