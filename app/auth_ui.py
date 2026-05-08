"""인증 UI — 로그인/회원가입/찾기/재설정/대기 화면.

main.py 의 진입부에서 require_auth() 한 줄로 호출. 로그인 안 된 상태면 자동으로 폼 렌더 후 st.stop().
URL 에 ?reset_token=... 이 있으면 재설정 화면으로 분기.
"""
from __future__ import annotations

import streamlit as st

import auth


def _render_login_form() -> None:
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("아이디", key="login_username")
        password = st.text_input("비밀번호", type="password", key="login_password")
        submitted = st.form_submit_button("로그인", use_container_width=True, type="primary")
        if submitted:
            ok, msg = auth.login(username.strip(), password)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


def _render_signup_form() -> None:
    with st.form("signup_form", clear_on_submit=False):
        name = st.text_input("이름", key="signup_name")
        username = st.text_input("아이디 (영문/숫자/언더스코어 3~20자)", key="signup_username")
        email = st.text_input("이메일 (아이디·비번 찾기 시 사용)", key="signup_email")
        password = st.text_input("비밀번호 (8자 이상)", type="password", key="signup_password")
        password2 = st.text_input("비밀번호 확인", type="password", key="signup_password2")
        submitted = st.form_submit_button("가입 신청", use_container_width=True, type="primary")
        if submitted:
            if password != password2:
                st.error("비밀번호가 일치하지 않습니다.")
                return
            ok, msg = auth.signup(name.strip(), username.strip(), password, email.strip())
            if ok:
                st.success(msg)
                st.info("관리자 승인 후 로그인 탭에서 접속하세요.")
            else:
                st.error(msg)


def _render_forgot_form() -> None:
    st.caption("가입 시 등록한 이메일을 입력하시면 아이디 안내 + 비밀번호 재설정 링크를 보내드립니다.")
    with st.form("forgot_form", clear_on_submit=False):
        email = st.text_input("이메일", key="forgot_email")
        submitted = st.form_submit_button("발송", use_container_width=True, type="primary")
        if submitted:
            ok, msg = auth.request_password_reset(email.strip())
            if ok:
                st.success(msg)
            else:
                st.error(msg)


def _render_password_reset_page(token: str) -> None:
    st.title("🔐 비밀번호 재설정")

    # 재설정 성공 후 화면 — form 밖이라 일반 버튼 사용 가능
    if st.session_state.get("reset_success"):
        st.success("비밀번호가 변경되었습니다. 새 비번으로 로그인하세요.")
        if st.button("로그인 페이지로 이동", use_container_width=True, type="primary"):
            st.session_state.pop("reset_success", None)
            st.query_params.clear()
            st.rerun()
        return

    with st.form("reset_form"):
        new_pw = st.text_input("새 비밀번호 (8자 이상)", type="password", key="reset_pw")
        new_pw2 = st.text_input("새 비밀번호 확인", type="password", key="reset_pw2")
        submitted = st.form_submit_button("재설정", use_container_width=True, type="primary")

    if submitted:
        if new_pw != new_pw2:
            st.error("비밀번호가 일치하지 않습니다.")
            return
        ok, msg = auth.consume_reset_token(token, new_pw)
        if ok:
            st.session_state["reset_success"] = True
            st.rerun()
        else:
            st.error(msg)


def _render_pending_page() -> None:
    u = auth.current_user() or {}
    st.title("⏳ 승인 대기 중")
    st.info(
        f"**{u.get('name', '')}** 님, 가입은 완료됐지만 아직 관리자 승인을 기다리고 있어요. "
        "승인되면 메일 또는 별도 안내를 드릴 예정입니다."
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("승인 상태 새로고침", use_container_width=True):
            auth.refresh_profile()
            st.rerun()
    with col2:
        if st.button("로그아웃", use_container_width=True):
            auth.logout()
            st.rerun()


def _render_auth_gate_page() -> None:
    st.title("🔐 MathArchive")
    st.caption("회원제 문제은행 — 로그인 후 이용 가능합니다.")
    tab_login, tab_signup, tab_forgot = st.tabs([
        "로그인",
        "회원가입",
        "아이디 / 비밀번호 찾기",
    ])
    with tab_login:
        _render_login_form()
    with tab_signup:
        _render_signup_form()
    with tab_forgot:
        _render_forgot_form()


def require_auth() -> None:
    """페이지 시작부에서 호출. 인증 안 됐거나 미승인이면 적절한 화면 띄우고 st.stop()."""
    # 비번 재설정 링크 분기
    token = st.query_params.get("reset_token")
    if token:
        _render_password_reset_page(token)
        st.stop()

    if not auth.is_logged_in():
        _render_auth_gate_page()
        st.stop()

    if not auth.is_approved():
        _render_pending_page()
        st.stop()

    # 비관리자에겐 사이드바의 ⚙️ 관리자 페이지 링크 숨김
    # (페이지 가드는 페이지 내부에서 별도로 차단되지만 링크 자체를 안 보여주는 게 UX 깔끔)
    if not auth.is_admin():
        st.markdown(
            """
            <style>
            [data-testid="stSidebarNav"] li:has(a[href*="관리자"]),
            [data-testid="stSidebarNav"] li:has(a[href*="%EA%B4%80%EB%A6%AC%EC%9E%90"]),
            [data-testid="stSidebarNav"] a[href*="관리자"],
            [data-testid="stSidebarNav"] a[href*="%EA%B4%80%EB%A6%AC%EC%9E%90"] {
                display: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


def render_user_menu_in_sidebar() -> None:
    """로그인 상태일 때 사이드바 하단에 사용자 정보 + 로그아웃 표시."""
    u = auth.current_user()
    if not u:
        return
    st.sidebar.markdown("---")
    st.sidebar.caption(f"👤 **{u['name']}** ({u['username']})")
    if u.get("is_admin"):
        st.sidebar.caption("⚙️ 관리자")
    if st.sidebar.button("로그아웃", use_container_width=True, key="sidebar_logout"):
        auth.logout()
        st.rerun()
