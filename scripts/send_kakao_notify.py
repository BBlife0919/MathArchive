#!/usr/bin/env python3
"""카톡 알림톡 발송 — kakao_send_queue 의 approved row 를 솔라피로 발송.

P4-B 발송 일꾼. GitHub Actions cron(금 17시)에서 호출.

PDF §7 운영 룰:
- approved 만 발송 (draft 는 건너뜀)
- instructor_note 비어있으면 발송 차단 (DB UPDATE 시점 검증 + 여기서도 한 번 더)
- 발송 성공: status='sent', sent_at, solapi_msg_id 채움
- 실패: status='failed', error_log 채움

모드 분기:
- KAKAO_MOCK=1 또는 SOLAPI_API_KEY 미설정 → mock 모드 (실제 발송 X)
- SOLAPI_API_KEY/SECRET/SENDER_KEY 모두 있으면 실제 모드

실행:
    python scripts/send_kakao_notify.py             # 자동 분기
    KAKAO_MOCK=1 python scripts/send_kakao_notify.py  # 강제 mock
    python scripts/send_kakao_notify.py --local       # 로컬 SQLite 강제
    python scripts/send_kakao_notify.py --dry-run     # 실제 모드여도 발송 X (큐만 조회)
"""
import hashlib
import hmac
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from db import get_connection, is_cloud  # noqa: E402


SOLAPI_BASE = "https://api.solapi.com"


def _load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def _is_mock_mode() -> bool:
    if os.environ.get("KAKAO_MOCK") == "1":
        return True
    # 솔라피 자격증명 하나라도 빠지면 안전상 mock
    required = ("SOLAPI_API_KEY", "SOLAPI_API_SECRET", "SOLAPI_PFID")
    return not all(os.environ.get(k) for k in required)


def _normalize_phone(raw: str) -> str:
    """솔라피는 하이픈/공백 없는 11자리 숫자 요구 — '010-1234-5678' → '01012345678'."""
    return re.sub(r"\D", "", raw or "")


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _fetch_due(conn) -> list:
    """approved + scheduled_at <= today + instructor_note 채워진 row."""
    today = datetime.now().date().isoformat()
    rows = conn.execute(
        """
        SELECT k.queue_id, k.student_id, k.target_phone, k.template_code,
               k.ai_draft, k.instructor_note, k.scheduled_at,
               s.name AS student_name
        FROM kakao_send_queue k
        JOIN students s ON k.student_id = s.student_id
        WHERE k.status = 'approved'
          AND (k.scheduled_at IS NULL OR k.scheduled_at <= ?)
          AND k.instructor_note IS NOT NULL
          AND TRIM(k.instructor_note) <> ''
        ORDER BY k.scheduled_at, k.queue_id
        """,
        (today,),
    ).fetchall()
    return rows


def _compose_body(row) -> str:
    """ai_draft 본문에 강사 1문장을 [강사 코멘트] 줄로 치환·삽입."""
    base = row["ai_draft"] or ""
    note = (row["instructor_note"] or "").strip()
    placeholder = "[강사 코멘트로 보강 예정]"
    if placeholder in base:
        return base.replace(placeholder, note)
    return f"{base}\n\n[강사 코멘트] {note}"


def _send_mock(row) -> tuple[bool, str, str]:
    """mock 발송 — 항상 성공으로 처리, MOCK_ 접두 메시지 ID 부여."""
    msg_id = f"MOCK_{row['queue_id']}_{uuid4().hex[:8]}"
    body = _compose_body(row)
    phone = _normalize_phone(row["target_phone"])
    print(f"  [MOCK] → {row['student_name']} ({phone}) "
          f"len={len(body)}자  msg_id={msg_id}")
    return True, msg_id, ""


def _send_solapi(row) -> tuple[bool, str, str]:
    """솔라피 실제 발송. requests 사용. 실패 시 (False, '', error)."""
    import requests  # 로컬에선 미설치 가능 → 실제 모드 진입 시점에만 import

    api_key    = os.environ["SOLAPI_API_KEY"]
    api_secret = os.environ["SOLAPI_API_SECRET"]
    pf_id      = os.environ["SOLAPI_PFID"]
    from_no    = _normalize_phone(os.environ.get("SOLAPI_FROM_NUMBER", ""))

    if not from_no:
        return False, "", "SOLAPI_FROM_NUMBER 미설정 (발신번호 필요)"

    salt = uuid4().hex
    timestamp = _now_iso()
    sig_target = (timestamp + salt).encode()
    sig = hmac.new(api_secret.encode(), sig_target, hashlib.sha256).hexdigest()
    auth_header = (
        f"HMAC-SHA256 apiKey={api_key}, date={timestamp}, "
        f"salt={salt}, signature={sig}"
    )

    payload = {
        "message": {
            "to":   _normalize_phone(row["target_phone"]),
            "from": from_no,
            "type": "ATA",   # 알림톡
            "kakaoOptions": {
                "pfId":         pf_id,
                "templateId":   row["template_code"],
                "disableSms":   True,   # SMS 자동 대체 OFF — 비용/의도 분리
            },
            "text": _compose_body(row),
        }
    }

    try:
        resp = requests.post(
            f"{SOLAPI_BASE}/messages/v4/send",
            headers={"Authorization": auth_header,
                     "Content-Type":  "application/json"},
            data=json.dumps(payload),
            timeout=10,
        )
    except Exception as e:
        return False, "", f"network: {type(e).__name__}: {e}"

    if not (200 <= resp.status_code < 300):
        return False, "", f"http {resp.status_code}: {resp.text[:200]}"

    try:
        data = resp.json()
        msg_id = data.get("messageId") or data.get("groupId") or ""
        return True, msg_id, ""
    except Exception as e:
        return False, "", f"parse: {e}: {resp.text[:200]}"


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--local",   action="store_true",
                    help="강제 로컬 SQLite (SUPABASE_DB_URL 무시)")
    ap.add_argument("--dry-run", action="store_true",
                    help="큐만 조회·표시. 실제 발송/DB 변경 X")
    args = ap.parse_args()

    _load_env_file()
    if args.local:
        os.environ.pop("SUPABASE_DB_URL", None)

    conn = get_connection()
    mock = _is_mock_mode()
    target = "Supabase Postgres" if is_cloud() else "로컬 SQLite"
    mode   = "MOCK" if mock else "REAL"
    print(f"[INIT] mode={mode}  db={target}  dry_run={args.dry_run}")

    due = _fetch_due(conn)
    print(f"[QUEUE] 발송 대상 {len(due)}건")
    if not due:
        return

    if args.dry_run:
        for r in due:
            print(f"  · #{r['queue_id']} {r['student_name']} "
                  f"sched={r['scheduled_at']} phone={r['target_phone']}")
        return

    sent_count = failed_count = 0
    for r in due:
        sender = _send_mock if mock else _send_solapi
        ok, msg_id, err = sender(r)
        if ok:
            conn.execute(
                "UPDATE kakao_send_queue "
                "SET status='sent', sent_at=?, solapi_msg_id=?, error_log=NULL "
                "WHERE queue_id=?",
                (_now_iso(), msg_id, r["queue_id"]),
            )
            sent_count += 1
        else:
            conn.execute(
                "UPDATE kakao_send_queue "
                "SET status='failed', error_log=? "
                "WHERE queue_id=?",
                (err[:500], r["queue_id"]),
            )
            failed_count += 1
            print(f"  [FAIL] #{r['queue_id']} {r['student_name']}: {err}")

    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception as e:
            # commit 실패는 곧 다음 cron 에서 중복 발송 위험 → 명시 로그
            print(f"[CRIT] DB commit 실패 — 다음 실행 중복 발송 가능: {e}",
                  file=sys.stderr)
    print(f"[DONE] 성공 {sent_count} / 실패 {failed_count}")


if __name__ == "__main__":
    main()
