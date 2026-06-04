"""직접 인증 모듈 — psycopg2 + bcrypt + Resend.

Supabase Auth REST 가 egress 한도로 차단돼 있어 우회. 인증 흐름:
- 회원가입: users 테이블에 INSERT (approved=False, password_hash=bcrypt)
- 로그인: 아이디/비번 검증 → Streamlit session_state + 영속 쿠키 토큰 발급
- 자동 로그인: 페이지 로드 시 쿠키 토큰 검증 → session_state 복원
- 비번 재설정: 토큰 생성 → 이메일로 링크 발송 → 사용자가 링크 따라와서 신규 비번 설정
- 아이디 안내: 비번 재설정 메일에 username 동봉 (단일 흐름으로 통합)

영속 로그인: HMAC-서명 stateless 토큰을 쿠키에 저장. DB 테이블 불필요.
서명 시크릿은 SESSION_SECRET 환경변수/secret 에서 읽고, 없으면 SMTP 시크릿
파생값으로 폴백 (배포 환경 secret 누락 시에도 동작).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import streamlit as st

from db import get_connection as _get_db_connection


# ── 환경 설정 ──────────────────────────────────────────────────────────────
def _get_secret(key: str, default: str | None = None) -> str | None:
    v = os.environ.get(key)
    if v:
        return v
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return default


def _conn():
    return _get_db_connection()


# ── 검증 ─────────────────────────────────────────────────────────────────────
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_username(u: str) -> str | None:
    if not u:
        return "아이디를 입력하세요."
    if not USERNAME_RE.match(u):
        return "아이디는 영문/숫자/언더스코어 3~20자."
    return None


def validate_email(e: str) -> str | None:
    if not e:
        return "이메일을 입력하세요."
    if not EMAIL_RE.match(e):
        return "이메일 형식이 올바르지 않습니다."
    return None


def validate_password(p: str) -> str | None:
    if not p:
        return "비밀번호를 입력하세요."
    if len(p) < 8:
        return "비밀번호는 최소 8자."
    return None


# ── 비번 해시 ────────────────────────────────────────────────────────────────
def _hash_password(p: str) -> str:
    import bcrypt
    return bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _check_password(p: str, hashed: str) -> bool:
    import bcrypt
    try:
        return bcrypt.checkpw(p.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── 회원가입 ────────────────────────────────────────────────────────────────
def signup(name: str, username: str, password: str, email: str) -> tuple[bool, str]:
    """가입 신청. 성공 시 (True, msg), 실패 시 (False, err)."""
    if not name.strip():
        return False, "이름을 입력하세요."
    for err in (validate_username(username), validate_email(email), validate_password(password)):
        if err:
            return False, err

    pw_hash = _hash_password(password)

    conn = _conn()
    try:
        cur = conn.execute(
            "SELECT 1 FROM users WHERE username = ? OR email = ?",
            (username, email),
        )
        if cur.fetchone():
            return False, "이미 사용 중인 아이디 또는 이메일입니다."
        conn.execute(
            "INSERT INTO users (username, name, email, password_hash, approved, is_admin) "
            "VALUES (?, ?, ?, ?, FALSE, FALSE)",
            (username, name.strip(), email, pw_hash),
        )
    except Exception as e:
        return False, f"가입 실패: {e}"

    # 관리자 알림 메일 (실패해도 가입 자체는 성공으로 처리)
    try:
        _send_admin_signup_notice(
            new_name=name.strip(),
            new_username=username,
            new_email=email,
        )
    except Exception as e:
        # 메일 실패는 사용자한테 노출하지 않음. 로그만.
        import sys
        print(f"[WARN] admin signup notice 실패: {e}", file=sys.stderr)

    return True, "가입 신청이 접수되었습니다. 관리자 승인 후 로그인할 수 있어요."


def _send_admin_signup_notice(new_name: str, new_username: str, new_email: str) -> None:
    """새 회원가입 발생 시 관리자(ADMIN_EMAIL) 에게 알림."""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.utils import formataddr

    gmail_user = _get_secret("GMAIL_USER")
    gmail_pw = _get_secret("GMAIL_APP_PASSWORD")
    from_name = _get_secret("SMTP_FROM_NAME", "MathArchive")
    admin_email = _get_secret("ADMIN_EMAIL", "ywl0919@naver.com")
    base_url = (_get_secret("APP_BASE_URL", "http://localhost:8501") or "").rstrip("/")

    if not gmail_user or not gmail_pw:
        raise RuntimeError("GMAIL_USER / GMAIL_APP_PASSWORD 미설정")
    if not admin_email:
        raise RuntimeError("ADMIN_EMAIL 미설정")

    gmail_pw = gmail_pw.replace(" ", "")
    admin_url = f"{base_url}/관리자"

    html = f"""\
    <div style="font-family: sans-serif; line-height: 1.6;">
      <h2>🔔 새 회원가입 신청</h2>
      <table style="border-collapse:collapse;margin:12px 0;">
        <tr><td style="padding:6px 12px;color:#666;">이름</td><td style="padding:6px 12px;"><b>{new_name}</b></td></tr>
        <tr><td style="padding:6px 12px;color:#666;">아이디</td><td style="padding:6px 12px;"><b>{new_username}</b></td></tr>
        <tr><td style="padding:6px 12px;color:#666;">이메일</td><td style="padding:6px 12px;"><b>{new_email}</b></td></tr>
      </table>
      <p>승인하려면 관리자 페이지로 이동:</p>
      <p><a href="{admin_url}" style="background:#4f46e5;color:white;padding:10px 18px;
            text-decoration:none;border-radius:6px;display:inline-block">
        관리자 페이지 열기
      </a></p>
    </div>
    """
    text = (
        f"🔔 새 회원가입 신청\n\n"
        f"이름: {new_name}\n"
        f"아이디: {new_username}\n"
        f"이메일: {new_email}\n\n"
        f"승인: {admin_url}"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[MathArchive] 새 가입 신청 — {new_name} ({new_username})"
    msg["From"]    = formataddr((from_name, gmail_user))
    msg["To"]      = admin_email
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html",  "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
        smtp.login(gmail_user, gmail_pw)
        smtp.sendmail(gmail_user, [admin_email], msg.as_string())


# ── 영속 로그인: HMAC-서명 stateless 토큰 ─────────────────────────────────
SESSION_COOKIE_NAME = "matharchive_session"
SESSION_TTL_DAYS = 30


def _session_secret() -> str:
    """HMAC 서명 시크릿. 명시 secret 없으면 SMTP 시크릿 파생값으로 폴백.
    배포 환경 비밀이 누락된 채로도 인증이 멎지 않게 한다.
    """
    s = _get_secret("SESSION_SECRET")
    if s:
        return s
    # 폴백: SMTP 시크릿이라도 있으면 그것 기반 파생 (배포 환경 일관)
    smtp_pw = _get_secret("GMAIL_APP_PASSWORD") or ""
    return hashlib.sha256(f"matharchive::{smtp_pw}".encode()).hexdigest()


def _b64u_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64u_decode(s: str) -> bytes:
    padded = s + "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(padded)


def _encode_session_token(user_id: int) -> str:
    """stateless 세션 토큰: payload.signature 형식."""
    payload = {
        "uid": int(user_id),
        "exp": int(time.time()) + SESSION_TTL_DAYS * 86400,
    }
    payload_b64 = _b64u_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(
        _session_secret().encode(),
        payload_b64.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload_b64}.{sig}"


def _decode_session_token(token: str) -> int | None:
    """토큰이 유효하면 user_id 반환, 아니면 None."""
    try:
        payload_b64, sig = token.split(".", 1)
    except ValueError:
        return None
    expected = hmac.new(
        _session_secret().encode(),
        payload_b64.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return None
    try:
        payload = json.loads(_b64u_decode(payload_b64))
    except Exception:
        return None
    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    uid = payload.get("uid")
    return int(uid) if uid else None


def _cookie_manager():
    """CookieManager 싱글턴. lazy import 로 라이브러리 미설치 환경에서도 안전."""
    if "_auth_cookie_mgr" in st.session_state:
        return st.session_state["_auth_cookie_mgr"]
    try:
        import extra_streamlit_components as stx
        mgr = stx.CookieManager(key="auth_persistent_cookies")
    except Exception:
        mgr = None
    st.session_state["_auth_cookie_mgr"] = mgr
    return mgr


def _issue_session_cookie(user_id: int) -> None:
    """로그인 성공 시 쿠키에 세션 토큰 저장.

    CookieManager.set 기본 same_site='strict' 가 streamlit component
    iframe 환경에서 새로고침 시 cookie 송신을 차단하는 사고 — 'lax' 로
    완화. secure=True 로 HTTPS 전용 (streamlit cloud) 명시.
    expires_at 은 UTC timezone-aware 로 박아 브라우저 해석 모호성 제거.
    """
    mgr = _cookie_manager()
    if mgr is None:
        return
    token = _encode_session_token(user_id)
    try:
        mgr.set(
            SESSION_COOKIE_NAME, token,
            expires_at=datetime.now(timezone.utc)
                       + timedelta(days=SESSION_TTL_DAYS),
            same_site="lax",
            secure=True,
        )
    except Exception:
        # 첫 페이지 마운트 직후엔 set 가 실패할 수 있음. 다음 rerun 에 재시도해도 무방.
        pass


def refresh_session_cookie() -> None:
    """이미 로그인된 사용자의 cookie 만료시각을 주기적으로 갱신.

    매 페이지 진입마다 호출하면 CookieManager iframe 응답 대기로
    페이지 hang 사고. 12시간에 1회만 실제 set 실행 → sliding session
    효과는 유지하면서 페이지 렌더 영향 없음.
    """
    user = st.session_state.get("auth_user")
    if not user:
        return
    last = st.session_state.get("_last_cookie_refresh_ts", 0)
    now = time.time()
    if now - last < 12 * 3600:  # 12시간 미만이면 skip
        return
    _issue_session_cookie(user.get("user_id"))
    st.session_state["_last_cookie_refresh_ts"] = now


def _clear_session_cookie() -> None:
    mgr = _cookie_manager()
    if mgr is None:
        return
    try:
        mgr.delete(SESSION_COOKIE_NAME)
    except Exception:
        pass


def restore_session_from_cookie() -> None:
    """페이지 로드 시 쿠키에서 자동 로그인 복원. 이미 로그인됐으면 no-op.

    extra-streamlit-components 의 CookieManager 는 iframe 컴포넌트로 마운트
    되며 쿠키를 비동기로 받아옴. 새로고침/새 탭 등 fresh mount 시점엔 첫
    몇 번의 mgr.get() 이 None 을 반환. retry 횟수 부족하면 cookie 가 진짜
    있어도 로그인 풀림 → 5회까지 누적 ~3.7초 대기.
    """
    if st.session_state.get("auth_user"):
        st.session_state.pop("_cookie_restore_attempts", None)
        return
    mgr = _cookie_manager()
    if mgr is None:
        return
    try:
        token = mgr.get(SESSION_COOKIE_NAME)
    except Exception:
        token = None
    if not token:
        attempts = st.session_state.get("_cookie_restore_attempts", 0)
        # 누적 sleep: 0.3+0.5+0.7+1.0+1.2 = 3.7s. iframe 마운트가 streamlit cloud
        # 환경에서 1~2s 걸리는 케이스도 커버. 그래도 None 이면 실제 미로그인.
        delays = [0.3, 0.5, 0.7, 1.0, 1.2]
        if attempts < len(delays):
            st.session_state["_cookie_restore_attempts"] = attempts + 1
            time.sleep(delays[attempts])
            st.rerun()
        return
    user_id = _decode_session_token(token)
    if not user_id:
        return
    try:
        conn = _conn()
        cur = conn.execute(
            "SELECT user_id, username, name, email, approved, is_admin "
            "FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = cur.fetchone()
    except Exception:
        return
    if not row:
        return
    st.session_state["auth_user"] = {
        "user_id":  row["user_id"],
        "username": row["username"],
        "name":     row["name"],
        "email":    row["email"],
        "approved": bool(row["approved"]),
        "is_admin": bool(row["is_admin"]),
    }
    st.session_state.pop("_cookie_restore_attempts", None)


# ── 로그인 ────────────────────────────────────────────────────────────────
def login(username: str, password: str) -> tuple[bool, str]:
    for err in (validate_username(username), validate_password(password)):
        if err:
            return False, err

    conn = _conn()
    try:
        cur = conn.execute(
            "SELECT user_id, username, name, email, password_hash, approved, is_admin "
            "FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
    except Exception as e:
        return False, f"로그인 실패: {e}"

    if not row:
        return False, "아이디 또는 비밀번호가 올바르지 않습니다."

    if not _check_password(password, row["password_hash"]):
        return False, "아이디 또는 비밀번호가 올바르지 않습니다."

    st.session_state["auth_user"] = {
        "user_id":  row["user_id"],
        "username": row["username"],
        "name":     row["name"],
        "email":    row["email"],
        "approved": bool(row["approved"]),
        "is_admin": bool(row["is_admin"]),
    }

    # 영속 쿠키 발급 (30일 자동 로그인)
    _issue_session_cookie(row["user_id"])

    if not row["approved"]:
        return True, "로그인은 됐지만 아직 관리자 승인 대기 중입니다."
    return True, f"환영합니다, {row['name']}님."


def logout() -> None:
    _clear_session_cookie()
    for k in list(st.session_state.keys()):
        if k.startswith("auth_"):
            del st.session_state[k]


# ── 비번 재설정 + 아이디 안내 통합 ──────────────────────────────────────────
TOKEN_TTL_HOURS = 1


def request_password_reset(email: str) -> tuple[bool, str]:
    """이메일 입력 → 등록된 사용자라면 재설정 링크 + 아이디 안내 메일 발송.

    보안상 이메일 등록 여부와 무관하게 동일 메시지 반환 (열거 공격 방지).
    """
    err = validate_email(email)
    if err:
        return False, err

    conn = _conn()
    cur = conn.execute(
        "SELECT user_id, username, name FROM users WHERE email = ?",
        (email,),
    )
    row = cur.fetchone()

    if row:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS)
        try:
            conn.execute(
                "INSERT INTO password_reset_tokens (token, user_id, expires_at) "
                "VALUES (?, ?, ?)",
                (token, row["user_id"], expires_at),
            )
        except Exception as e:
            return False, f"토큰 저장 실패: {e}"

        try:
            _send_reset_email(
                to_email=email,
                name=row["name"],
                username=row["username"],
                token=token,
            )
        except Exception as e:
            return False, f"메일 발송 실패: {e}"

    return True, "등록된 이메일이라면 안내 메일을 발송했습니다. 메일함을 확인하세요."


def _send_reset_email(to_email: str, name: str, username: str, token: str) -> None:
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.utils import formataddr

    gmail_user = _get_secret("GMAIL_USER")
    gmail_pw = _get_secret("GMAIL_APP_PASSWORD")
    from_name = _get_secret("SMTP_FROM_NAME", "MathArchive")
    base_url = (_get_secret("APP_BASE_URL", "http://localhost:8501") or "").rstrip("/")
    if not gmail_user or not gmail_pw:
        raise RuntimeError("GMAIL_USER / GMAIL_APP_PASSWORD 미설정")

    # 앱 비밀번호는 공백 포함해서 발급되기도 — 자동 정리
    gmail_pw = gmail_pw.replace(" ", "")

    reset_url = f"{base_url}/?reset_token={token}"
    html = f"""\
    <div style="font-family: sans-serif; line-height: 1.6;">
      <h2>MathArchive 계정 안내</h2>
      <p>{name} 님,</p>
      <p>등록하신 아이디는 <b>{username}</b> 입니다.</p>
      <p>비밀번호를 재설정하려면 아래 링크를 클릭하세요 (1시간 안 유효):</p>
      <p><a href="{reset_url}" style="background:#4f46e5;color:white;padding:10px 18px;
            text-decoration:none;border-radius:6px;display:inline-block">
        비밀번호 재설정
      </a></p>
      <p style="color:#666;font-size:12px;">
        본인이 요청한 적이 없다면 이 메일을 무시하세요.
      </p>
    </div>
    """
    text = (
        f"{name} 님,\n\n"
        f"등록하신 아이디: {username}\n\n"
        f"비밀번호 재설정 링크 (1시간 안 유효):\n{reset_url}\n\n"
        "본인이 요청한 적이 없다면 이 메일을 무시하세요."
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "[MathArchive] 아이디 안내 및 비밀번호 재설정"
    msg["From"]    = formataddr((from_name, gmail_user))
    msg["To"]      = to_email
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html",  "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
        smtp.login(gmail_user, gmail_pw)
        smtp.sendmail(gmail_user, [to_email], msg.as_string())


def consume_reset_token(token: str, new_password: str) -> tuple[bool, str]:
    """재설정 링크 클릭 후 신규 비번으로 교체."""
    err = validate_password(new_password)
    if err:
        return False, err
    if not token:
        return False, "토큰이 없습니다."

    conn = _conn()
    cur = conn.execute(
        "SELECT user_id, expires_at, used FROM password_reset_tokens WHERE token = ?",
        (token,),
    )
    row = cur.fetchone()
    if not row:
        return False, "유효하지 않은 토큰입니다."
    if row["used"]:
        return False, "이미 사용된 토큰입니다. 재설정을 다시 요청하세요."

    expires_at = row["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        return False, "만료된 토큰입니다. 재설정을 다시 요청하세요."

    pw_hash = _hash_password(new_password)
    try:
        conn.execute("UPDATE users SET password_hash = ? WHERE user_id = ?",
                     (pw_hash, row["user_id"]))
        conn.execute("UPDATE password_reset_tokens SET used = TRUE WHERE token = ?",
                     (token,))
    except Exception as e:
        return False, f"비밀번호 변경 실패: {e}"

    return True, "비밀번호가 변경되었습니다. 새 비번으로 로그인하세요."


# ── 관리자: 승인 큐 ─────────────────────────────────────────────────────────
def list_pending_users() -> list[dict[str, Any]]:
    conn = _conn()
    cur = conn.execute(
        "SELECT user_id, username, name, email, created_at "
        "FROM users WHERE NOT approved ORDER BY created_at"
    )
    return [dict(r) for r in cur.fetchall()]


def list_all_users() -> list[dict[str, Any]]:
    conn = _conn()
    cur = conn.execute(
        "SELECT user_id, username, name, email, approved, is_admin, created_at "
        "FROM users ORDER BY created_at DESC"
    )
    return [dict(r) for r in cur.fetchall()]


def approve_user(user_id: int) -> tuple[bool, str | None]:
    """승인 처리 + 첫 승인 시 환영 메일 발송.

    이미 승인된 사용자엔 메일 재발송 안 함 (idempotent).
    메일 발송 실패해도 승인 처리 자체는 성공으로 간주, 경고만 반환.
    """
    conn = _conn()
    cur = conn.execute(
        "SELECT name, email, username, approved FROM users WHERE user_id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    if not row:
        return False, "사용자를 찾을 수 없습니다."

    was_approved = bool(row["approved"])
    conn.execute("UPDATE users SET approved = TRUE WHERE user_id = ?", (user_id,))

    if was_approved:
        return True, None  # 이미 승인 → 메일 안 보냄

    try:
        _send_approval_email(
            to_email=row["email"],
            name=row["name"],
            username=row["username"],
        )
    except Exception as e:
        return True, f"승인은 됐지만 메일 발송 실패: {e}"

    return True, None


def _send_approval_email(to_email: str, name: str, username: str) -> None:
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.utils import formataddr

    gmail_user = _get_secret("GMAIL_USER")
    gmail_pw = _get_secret("GMAIL_APP_PASSWORD")
    from_name = _get_secret("SMTP_FROM_NAME", "MathArchive")
    base_url = (_get_secret("APP_BASE_URL", "http://localhost:8501") or "").rstrip("/")
    if not gmail_user or not gmail_pw:
        raise RuntimeError("GMAIL_USER / GMAIL_APP_PASSWORD 미설정")
    gmail_pw = gmail_pw.replace(" ", "")

    html = f"""\
    <div style="font-family: sans-serif; line-height: 1.6;">
      <h2>🎉 MathArchive 가입 승인 완료</h2>
      <p>{name} 님,</p>
      <p>가입 신청이 승인되었습니다. 이제 아이디 <b>{username}</b> 로 로그인해서 이용하실 수 있어요.</p>
      <p><a href="{base_url}" style="background:#4f46e5;color:white;padding:10px 18px;
            text-decoration:none;border-radius:6px;display:inline-block">
        MathArchive 들어가기
      </a></p>
      <p style="color:#666;font-size:12px;">
        문의 사항이 있으면 답장으로 회신주세요.
      </p>
    </div>
    """
    text = (
        f"{name} 님,\n\n"
        f"MathArchive 가입 신청이 승인되었습니다.\n"
        f"아이디 {username} 로 로그인해서 이용하세요.\n\n"
        f"링크: {base_url}\n"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "[MathArchive] 가입 승인 완료 — 이제 로그인하실 수 있어요"
    msg["From"]    = formataddr((from_name, gmail_user))
    msg["To"]      = to_email
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html",  "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
        smtp.login(gmail_user, gmail_pw)
        smtp.sendmail(gmail_user, [to_email], msg.as_string())


def revoke_user(user_id: int) -> None:
    _conn().execute("UPDATE users SET approved = FALSE WHERE user_id = ?", (user_id,))


def delete_user(user_id: int) -> None:
    _conn().execute("DELETE FROM users WHERE user_id = ?", (user_id,))


def set_admin(user_id: int, is_admin: bool) -> None:
    _conn().execute("UPDATE users SET is_admin = ? WHERE user_id = ?", (is_admin, user_id))


# ── 세션 헬퍼 ───────────────────────────────────────────────────────────────
def current_user() -> dict[str, Any] | None:
    return st.session_state.get("auth_user")


def is_logged_in() -> bool:
    return current_user() is not None


def is_approved() -> bool:
    u = current_user()
    return bool(u and u.get("approved"))


def is_admin() -> bool:
    u = current_user()
    return bool(u and u.get("is_admin"))


def refresh_profile() -> None:
    """승인 토글 등 변경 사항 재조회."""
    u = current_user()
    if not u:
        return
    conn = _conn()
    cur = conn.execute(
        "SELECT name, email, approved, is_admin FROM users WHERE user_id = ?",
        (u["user_id"],),
    )
    row = cur.fetchone()
    if row:
        u["name"]     = row["name"]
        u["email"]    = row["email"]
        u["approved"] = bool(row["approved"])
        u["is_admin"] = bool(row["is_admin"])
        st.session_state["auth_user"] = u
