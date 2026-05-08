#!/usr/bin/env python3
"""사용자를 관리자로 승격 + 자동 승인.

용례:
    python scripts/make_admin.py <username>
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# .env 자동 로드
env = ROOT / ".env"
if env.exists():
    for line in env.read_text().splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def main():
    if len(sys.argv) < 2:
        print("사용법: python scripts/make_admin.py <username>", file=sys.stderr)
        sys.exit(1)
    username = sys.argv[1]

    import psycopg2
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL 미설정", file=sys.stderr)
        sys.exit(2)

    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET is_admin = TRUE, approved = TRUE WHERE username = %s "
        "RETURNING user_id, username, name, email",
        (username,),
    )
    row = cur.fetchone()
    if not row:
        print(f"ERROR: 사용자 '{username}' 를 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(3)
    print(f"[OK] {row[1]} ({row[2]}, {row[3]}) → admin + approved")


if __name__ == "__main__":
    main()
