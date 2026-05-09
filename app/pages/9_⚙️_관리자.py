"""관리자 페이지 — 가입 신청 승인/거절, 사용자 관리.

`is_admin = TRUE` 인 사용자에게만 접근 허용. 비관리자가 URL 로 들어오면 차단.
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# app/ 모듈 임포트 경로 등록
APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import auth
from auth_ui import require_auth, render_user_menu_in_sidebar


st.set_page_config(page_title="관리자 — MathArchive", page_icon="⚙️", layout="wide")

require_auth()

if not auth.is_admin():
    st.error("⛔ 이 페이지는 관리자 전용입니다.")
    st.stop()

render_user_menu_in_sidebar()


# ── 헤더 ────────────────────────────────────────────────────────────────────
st.title("⚙️ 관리자")
st.caption("회원 승인 대기열, 권한 관리, 회원 목록")


# ── 승인 대기열 ─────────────────────────────────────────────────────────────
st.subheader("📋 가입 승인 대기")
pending = auth.list_pending_users()

if not pending:
    st.info("대기 중인 가입 신청이 없습니다.")
else:
    for u in pending:
        with st.container(border=True):
            cols = st.columns([3, 3, 4, 1, 1])
            cols[0].markdown(f"**{u['name']}** (`{u['username']}`)")
            cols[1].caption(u["email"])
            cols[2].caption(f"신청일: {u['created_at']}")
            if cols[3].button("승인", key=f"approve_{u['user_id']}", type="primary"):
                ok, warn = auth.approve_user(u["user_id"])
                if ok:
                    if warn:
                        st.warning(f"{u['username']} 승인됨 — {warn}")
                    else:
                        st.success(f"{u['username']} 승인 완료 (환영 메일 발송됨)")
                else:
                    st.error(f"승인 실패: {warn}")
                st.rerun()
            if cols[4].button("삭제", key=f"reject_{u['user_id']}"):
                auth.delete_user(u["user_id"])
                st.warning(f"{u['username']} 삭제됨")
                st.rerun()


# ── 전체 회원 ───────────────────────────────────────────────────────────────
st.subheader("👥 전체 회원")
all_users = auth.list_all_users()

if not all_users:
    st.info("회원이 없습니다.")
else:
    for u in all_users:
        with st.container(border=True):
            cols = st.columns([3, 3, 2, 2, 1, 1])
            cols[0].markdown(f"**{u['name']}** (`{u['username']}`)")
            cols[1].caption(u["email"])
            badges = []
            if u["approved"]:
                badges.append("✅ 승인")
            else:
                badges.append("⏳ 대기")
            if u["is_admin"]:
                badges.append("⚙️ admin")
            cols[2].markdown(" · ".join(badges))
            cols[3].caption(str(u["created_at"])[:10])

            current = auth.current_user() or {}
            is_self = current.get("user_id") == u["user_id"]

            if u["is_admin"]:
                if not is_self and cols[4].button("admin↓", key=f"unadmin_{u['user_id']}"):
                    auth.set_admin(u["user_id"], False)
                    st.rerun()
            else:
                if cols[4].button("admin↑", key=f"admin_{u['user_id']}"):
                    auth.set_admin(u["user_id"], True)
                    st.rerun()

            if u["approved"]:
                if not is_self and cols[5].button("정지", key=f"revoke_{u['user_id']}"):
                    auth.revoke_user(u["user_id"])
                    st.rerun()
            else:
                if cols[5].button("승인", key=f"approve_all_{u['user_id']}", type="primary"):
                    ok, warn = auth.approve_user(u["user_id"])
                    if ok and not warn:
                        st.success(f"{u['username']} 승인 완료 (환영 메일 발송됨)")
                    elif ok and warn:
                        st.warning(f"{u['username']} 승인됨 — {warn}")
                    else:
                        st.error(f"승인 실패: {warn}")
                    st.rerun()
