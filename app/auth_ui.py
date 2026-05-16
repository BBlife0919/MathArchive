"""인증 UI — 로그인/회원가입/찾기/재설정/대기 화면.

main.py 의 진입부에서 require_auth() 한 줄로 호출. 로그인 안 된 상태면 자동으로 폼 렌더 후 st.stop().
URL 에 ?reset_token=... 이 있으면 재설정 화면으로 분기.
"""
from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

import auth


_ASSETS_DIR = Path(__file__).parent / "assets"


def _img_data_uri(filename: str) -> str:
    """app/assets/ 안의 이미지 파일을 base64 data URI 로 인코딩."""
    p = _ASSETS_DIR / filename
    if not p.exists():
        return ""
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def _render_login_form() -> None:
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("아이디", key="login_username")
        password = st.text_input("비밀번호", type="password", key="login_password")
        submitted = st.form_submit_button("로그인", use_container_width=True, type="primary")
        if submitted:
            ok, msg = auth.login(username.strip(), password)
            if ok:
                if auth.is_approved():
                    # 새 응답에서 entry loader 가 다시 inject 되도록 가드 초기화.
                    # 그렇지 않으면 가드 때문에 두 번째 rerun 응답에서 loader 가
                    # 안 떠 로그인→메인 사이 빈 화면이 잠깐 노출됨.
                    st.session_state.pop("_entry_loader_shown", None)
                    # 현재 응답의 마지막에 entry loader + 글로벌 CSS 를 emit.
                    # 클라이언트가 rerun 응답을 받기 전 transition 동안 풀스크린
                    # 오버레이가 깔려 "Running fn()..." 같은 잔여물·디버그 토스트가
                    # 전혀 안 보임.
                    st.markdown(_AUTHED_GLOBAL_CSS, unsafe_allow_html=True)
                    st.markdown(_ENTRY_LOADER_HTML, unsafe_allow_html=True)
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


_LANDING_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800;900&family=Cormorant+Garamond:ital,wght@1,500&family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

:root {
  --bg: #0b1830;
  --bg-soft: #0c2156;
  --bg-card: rgba(28, 52, 110, 0.45);
  --accent: #4cc4ff;
  --accent-strong: #7ddcff;
  --gold: #d2af6e;
  --gold-light: #f0cd87;
  --text: #e9ecf8;
  --text-soft: #a6b2d4;
  --border: rgba(125, 220, 255, 0.22);
}

/* 본 페이지 자체 푸른 다크 */
.stApp {
  background:
    radial-gradient(ellipse at top, #163074 0%, transparent 55%),
    radial-gradient(ellipse at bottom right, rgba(76, 196, 255, 0.12) 0%, transparent 50%),
    radial-gradient(ellipse at bottom left, rgba(40, 90, 200, 0.10) 0%, transparent 55%),
    var(--bg) !important;
}
section[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 1.5rem !important; max-width: 1200px !important; }

/* 흐르는 수식 배경 */
.math-bg {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  overflow: hidden; opacity: 0.10;
}
.math-bg span {
  position: absolute;
  font-family: 'Cormorant Garamond', serif;
  font-style: italic;
  color: var(--accent);
  white-space: nowrap;
  animation: float linear infinite;
}
@keyframes float {
  from { transform: translateY(110vh); }
  to   { transform: translateY(-20vh); }
}

/* 페이드인 */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeUp 0.9s ease-out both; }
.fade-in.d1 { animation-delay: 0.10s; }
.fade-in.d2 { animation-delay: 0.25s; }
.fade-in.d3 { animation-delay: 0.40s; }
.fade-in.d4 { animation-delay: 0.55s; }

/* HERO */
.hero {
  position: relative; z-index: 1;
  padding: 70px 0 50px;
  text-align: center;
}
.hero .eyebrow {
  display: inline-block;
  font-family: 'Montserrat', sans-serif;
  letter-spacing: 0.45em;
  font-size: 15px; font-weight: 700;
  color: var(--gold);
  border: 1px solid rgba(210, 175, 110, 0.4);
  padding: 9px 24px;
  border-radius: 999px;
  margin-bottom: 32px;
  text-transform: uppercase;
}
.hero h1 {
  font-family: 'Montserrat', 'Noto Sans KR', sans-serif;
  font-weight: 900;
  font-size: clamp(36px, 5.4vw, 64px);
  line-height: 1.1;
  margin: 0 0 18px;
  letter-spacing: -0.02em;
  color: var(--text);
}
.hero h1 .grad {
  background: linear-gradient(135deg, var(--accent) 0%, var(--gold-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero .sub {
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: clamp(20px, 2.0vw, 26px);
  color: var(--text);
  letter-spacing: 0.04em;
}
.hero .sub .num {
  color: var(--gold-light);
  font-weight: 700;
  letter-spacing: 0.02em;
}

/* 섹션 헤딩 */
.section-title {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 18px;
  letter-spacing: 0.5em;
  color: var(--gold);
  text-align: center;
  margin: 64px 0 36px;
  text-transform: uppercase;
}

/* 카드 원형 산포 — 행/열 규칙 없는 nebula 레이아웃 */
.feature-scatter {
  position: relative; z-index: 1;
  width: 100%;
  height: 640px;
  margin: 0 auto 60px;
  max-width: 1020px;
}
.feature-circle {
  position: absolute;
  border-radius: 50%;
  background: var(--bg-card);
  border: 1px solid var(--border);
  backdrop-filter: blur(8px);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center;
  padding: 24px;
  box-sizing: border-box;
  transition: transform 0.35s ease, border-color 0.35s ease,
              box-shadow 0.35s ease;
  width: var(--d, 220px);
  height: var(--d, 220px);
  left: var(--x, 50%);
  top: var(--y, 50%);
  transform: translate(-50%, -50%);
  cursor: default;
}
.feature-circle:hover {
  transform: translate(-50%, -50%) scale(1.28);
  border-color: rgba(76, 196, 255, 0.85);
  box-shadow: 0 24px 60px rgba(76, 196, 255, 0.32),
              0 0 40px rgba(76, 196, 255, 0.18);
  z-index: 2;
}
.feature-circle.highlight:hover {
  transform: translate(-50%, -50%) scale(1.22);
  border-color: rgba(240, 205, 135, 0.9);
  box-shadow: 0 24px 60px rgba(210, 175, 110, 0.4),
              0 0 50px rgba(210, 175, 110, 0.22);
}
.feature-circle .icon {
  font-size: 38px;
  margin-bottom: 12px;
  line-height: 1;
}
.feature-circle h3 {
  font-family: 'Montserrat', sans-serif;
  font-weight: 800;
  font-size: 19px;
  letter-spacing: 0.12em;
  color: var(--accent-strong);
  margin: 0 0 8px;
  text-transform: uppercase;
  line-height: 1.2;
  text-align: center;
  /* 트레일링 letter-spacing 보정 — text-align:center 시 시각적 좌측 치우침 제거 */
  text-indent: 0.12em;
}
.feature-circle .sub-ko {
  font-family: 'Noto Sans KR', sans-serif;
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
  letter-spacing: 0.02em;
  margin-bottom: 12px;
  display: block;
  text-align: center;
}
.feature-circle p {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 14px;
  line-height: 1.55;
  color: var(--text-soft);
  margin: 0;
  max-width: 84%;
  text-align: center;
}
.feature-circle.highlight {
  background:
    radial-gradient(ellipse at top, rgba(210, 175, 110, 0.30) 0%, transparent 60%),
    linear-gradient(135deg, rgba(210, 175, 110, 0.10) 0%, rgba(76, 196, 255, 0.08) 100%);
  border-color: rgba(210, 175, 110, 0.6);
  box-shadow: 0 0 60px rgba(210, 175, 110, 0.18),
              inset 0 0 40px rgba(210, 175, 110, 0.05);
}
.feature-circle.highlight h3 {
  color: var(--gold-light);
  font-size: 26px;
}
.feature-circle.highlight .icon { font-size: 50px; }
.feature-circle.highlight .sub-ko { font-size: 16px; }
.feature-circle.highlight p { font-size: 15px; max-width: 86%; }
.feature-circle.highlight::after {
  content: "FEATURED";
  position: absolute;
  top: 16%;
  font-family: 'Montserrat', sans-serif;
  font-size: 9px;
  letter-spacing: 0.32em;
  color: var(--gold);
  opacity: 0.85;
}

/* 모바일: 산포 해제 → 세로 스택 */
@media (max-width: 760px) {
  .feature-scatter {
    height: auto;
    display: flex; flex-direction: column;
    align-items: center; gap: 18px;
    padding: 0 8px;
  }
  .feature-circle {
    position: relative;
    left: auto; top: auto;
    transform: none;
    width: 240px; height: 240px;
  }
  .feature-circle:hover { transform: scale(1.03); }
}

/* 프로필 섹션 — 사진 왼쪽 + 텍스트 오른쪽 (side by side) */
.profile-wrap {
  position: relative; z-index: 1;
  display: flex; align-items: center; justify-content: center;
  gap: 44px;
  padding: 40px 24px 30px;
  margin: 30px auto 10px;
  max-width: 760px;
  border-top: 1px solid rgba(210, 175, 110, 0.25);
  border-bottom: 1px solid rgba(210, 175, 110, 0.25);
  flex-wrap: wrap;
}
.profile-photo {
  height: 260px;
  width: auto;
  flex-shrink: 0;
  filter: drop-shadow(0 14px 28px rgba(0, 0, 0, 0.5));
}
.profile-text { text-align: left; }
.profile-text .directed {
  font-family: 'Cormorant Garamond', serif;
  font-style: italic;
  font-size: 16px;
  color: var(--gold);
  letter-spacing: 0.18em;
  margin-bottom: 4px;
}
.profile-text .name {
  font-family: 'Montserrat', 'Noto Sans KR', sans-serif;
  font-weight: 800;
  font-size: 30px;
  color: var(--text);
  margin: 0 0 6px;
  letter-spacing: 0.02em;
}
.profile-text .role {
  font-family: 'Montserrat', sans-serif;
  font-size: 11px;
  letter-spacing: 0.42em;
  color: var(--text-soft);
  text-transform: uppercase;
}

/* 로그인 영역 컨테이너 */
.auth-area-title {
  text-align: center;
  margin: 30px 0 16px;
}
.auth-area-title .lead {
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  letter-spacing: 0.5em;
  color: var(--gold);
  text-transform: uppercase;
}

/* 탭 — Streamlit 기본 위에 덧칠 */
.stTabs [data-baseweb="tab-list"] {
  justify-content: center;
  gap: 8px;
  border-bottom: 1px solid rgba(76, 196, 255, 0.18) !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Noto Sans KR', sans-serif !important;
  font-weight: 600 !important;
  color: var(--text-soft) !important;
}
.stTabs [aria-selected="true"] {
  color: var(--accent-strong) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
  background-color: var(--accent) !important;
}

/* 입력 필드 다크 */
.stTextInput input, .stTextArea textarea {
  background: rgba(13, 18, 48, 0.7) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
}
.stTextInput input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(76,196,255,0.18) !important;
}
.stButton button, .stFormSubmitButton button {
  background: linear-gradient(135deg, var(--accent) 0%, #2b8fd1 100%) !important;
  border: none !important;
  color: #0a1024 !important;
  font-weight: 800 !important;
  letter-spacing: 0.06em !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
.stButton button:hover, .stFormSubmitButton button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(76,196,255,0.35) !important;
}

/* 푸터 */
.footer {
  position: relative; z-index: 1;
  text-align: center;
  font-family: 'Montserrat', sans-serif;
  font-size: 10.5px;
  letter-spacing: 0.32em;
  color: var(--text-soft);
  opacity: 0.55;
  padding: 30px 0 12px;
  text-transform: uppercase;
}

@media (max-width: 700px) {
  .profile-wrap { flex-direction: column; text-align: center; gap: 24px; }
  .profile-text { text-align: center; }
  .profile-photo { height: 220px; }
  .hero { padding: 40px 0 24px; }
}

/* Streamlit 기본 디버그 토스트("Running fn()...") 영구 숨김 — 랜딩에서도 */
[data-testid="stStatusWidget"],
[data-testid="stConnectionStatus"],
[data-testid="stToast"],
.stStatusWidget {
  display: none !important;
}
</style>
"""


_MATH_BG = """
<div class="math-bg">
  <span style="left: 5%; top: 0; font-size: 64px; animation-duration: 38s; animation-delay: 0s;">∫₀^∞ e^{-x²} dx = √π/2</span>
  <span style="left: 22%; top: 0; font-size: 48px; animation-duration: 52s; animation-delay: -8s;">∑_{n=1}^∞ 1/n² = π²/6</span>
  <span style="left: 40%; top: 0; font-size: 56px; animation-duration: 46s; animation-delay: -15s;">e^{iπ} + 1 = 0</span>
  <span style="left: 58%; top: 0; font-size: 42px; animation-duration: 60s; animation-delay: -22s;">lim_{x→0} sin(x)/x = 1</span>
  <span style="left: 72%; top: 0; font-size: 52px; animation-duration: 44s; animation-delay: -5s;">d/dx[ln x] = 1/x</span>
  <span style="left: 86%; top: 0; font-size: 46px; animation-duration: 56s; animation-delay: -30s;">∇·E = ρ/ε₀</span>
  <span style="left: 12%; top: 0; font-size: 38px; animation-duration: 50s; animation-delay: -42s;">a² + b² = c²</span>
  <span style="left: 50%; top: 0; font-size: 44px; animation-duration: 48s; animation-delay: -36s;">f'(x) = lim_{h→0} (f(x+h)-f(x))/h</span>
  <span style="left: 78%; top: 0; font-size: 40px; animation-duration: 54s; animation-delay: -20s;">P(A∩B) = P(A)·P(B|A)</span>
</div>
"""


# ── 인증 통과 후 모든 페이지에 공통 적용되는 글로벌 톤 ────
# 랜딩의 _LANDING_CSS 와 색조 통일 (#0b1830 딥 블루).
# Streamlit 의 기본 "Running fn()..." 디버그 토스트도 영구 숨김.
_AUTHED_GLOBAL_CSS = """
<style>
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
  background: #0b1830 !important;
}
[data-testid="stSidebar"] > div:first-child {
  background: linear-gradient(180deg, #0e2040 0%, #0b1830 100%) !important;
}
[data-testid="stStatusWidget"],
[data-testid="stConnectionStatus"],
[data-testid="stToast"],
.stStatusWidget {
  display: none !important;
}

/* ── Entry Loader: 인증 후 첫 진입 시 1.7s 풀스크린 오버레이 */
.entry-loader {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse at 30% 20%, #163074 0%, transparent 55%),
    radial-gradient(ellipse at 90% 90%, rgba(76,196,255,0.15) 0%, transparent 55%),
    #0b1830;
  z-index: 999999;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: 'Montserrat', 'Noto Sans KR', -apple-system, sans-serif;
  color: #e9ecf8;
  pointer-events: none;
  /* animation 제거 — 시간 기반 fade-out 대신 페이지 끝의 sentinel 요소가
     DOM 에 추가될 때까지 풀스크린 유지. 모든 위젯이 서버에서 그려진 직후
     사라져 "로딩 끝 = 즉시 문항 표시" 달성. */
}
/* 페이지 끝에 #mathdb-page-loaded sentinel 이 inject 되면 entry loader fade-out */
body:has(#mathdb-page-loaded) .entry-loader {
  animation: entryFadeOut 0.45s forwards;
}
.entry-loader .brand {
  font-size: 13px;
  letter-spacing: 0.55em;
  color: #d2af6e;
  margin-bottom: 26px;
  font-weight: 700;
  border: 1px solid rgba(210,175,110,0.4);
  padding: 8px 22px;
  border-radius: 999px;
}
.entry-loader h2 {
  font-size: clamp(40px, 5.6vw, 72px);
  font-weight: 900;
  letter-spacing: -0.01em;
  background: linear-gradient(135deg, #4cc4ff 0%, #f0cd87 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 14px;
  text-align: center;
}
.entry-loader .sub {
  font-size: 12px;
  letter-spacing: 0.4em;
  color: #a6b2d4;
  margin-bottom: 36px;
  font-weight: 500;
  text-transform: uppercase;
}
.entry-loader .bar {
  width: 240px;
  height: 2px;
  background: rgba(125,220,255,0.15);
  position: relative;
  overflow: hidden;
  border-radius: 2px;
}
.entry-loader .bar::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, #4cc4ff 50%, transparent);
  animation: entryShimmer 0.95s linear infinite;
}
@keyframes entryShimmer {
  from { transform: translateX(-100%); }
  to { transform: translateX(100%); }
}
@keyframes entryFadeOut {
  to { opacity: 0; visibility: hidden; }
}
</style>
"""

_ENTRY_LOADER_HTML = """
<div class="entry-loader">
<div class="brand">MATH ARCHIVE</div>
<h2>Entering the Archive</h2>
<div class="sub">120,000+ Questions · Infinite Possibilities</div>
<div class="bar"></div>
</div>
"""


def _render_landing_hero() -> None:
    """헤로 + 카드 + 프로필 — 로그인 폼 위에 얹는 마케팅 영역.

    CSS 와 모든 HTML 청크를 단일 ``st.markdown`` 호출에 묶어 한 DOM
    노드로 mount/unmount 되게 한다. 분리하면 rerun 사이에 CSS-없는
    순간이 생겨 FOUC (Flash of Unstyled Content) 가 발생함.
    """
    profile_uri = _img_data_uri("profile_lyw.png") or _img_data_uri("profile_lyw.jpeg")
    profile_img_html = (
        f'<img src="{profile_uri}" alt="이영우" class="profile-photo" />'
        if profile_uri else ''
    )

    # NOTE: f-string 의 들여쓰기를 0칸으로 통일해야 한다. Streamlit `st.markdown`
    # 은 마크다운 파서를 거치는데, 마크다운은 "4칸 이상 들여쓰여진 줄 = 코드
    # 블록" 으로 처리한다. 보간 변수(_LANDING_CSS 등)의 내용은 0칸인데
    # f-string 리터럴이 들여쓰여 있으면 공통 leading whitespace 가 0 이 돼
    # textwrap.dedent 류의 자동 dedent 가 안 먹는다.
    st.markdown(
f"""
{_LANDING_CSS}
{_MATH_BG}
<section class="hero fade-in">
<div class="eyebrow">Mathematics · Data · Design</div>
<h1>All-in-One Mathematics Library<br>
<span class="grad">Math Archive</span>
</h1>
<p class="sub">
<span class="num">120,000+</span> Questions · Infinite Possibilities
</p>
</section>
<div class="section-title fade-in d1">Core Capabilities</div>
<div class="feature-scatter fade-in d2">
<div class="feature-circle highlight" style="--x:50%; --y:42%; --d:320px;">
<div class="icon">⚡</div>
<h3>Rapid Forge</h3>
<span class="sub-ko">교재 · 시험지 즉시 제작</span>
<p>단 몇 번의 클릭으로 출판 품질 PDF 빌드.</p>
</div>
<div class="feature-circle" style="--x:17%; --y:20%; --d:230px;">
<div class="icon">📚</div>
<h3>Massive Data</h3>
<span class="sub-ko">방대한 문항 데이터</span>
<p>고1~고3 전문항 120,000개.</p>
</div>
<div class="feature-circle" style="--x:83%; --y:22%; --d:220px;">
<div class="icon">∑</div>
<h3>LaTeX Engine</h3>
<span class="sub-ko">완벽한 수식 렌더링</span>
<p>HWP → KaTeX 무손실 변환.</p>
</div>
<div class="feature-circle" style="--x:22%; --y:82%; --d:235px;">
<div class="icon">🎯</div>
<h3>Smart Filter</h3>
<span class="sub-ko">정교한 추출 엔진</span>
<p>학교 · 단원 · 난이도 다차원 검색.</p>
</div>
<div class="feature-circle" style="--x:78%; --y:80%; --d:225px;">
<div class="icon">🩺</div>
<h3>Personal Clinic</h3>
<span class="sub-ko">학생 맞춤 클리닉</span>
<p>취약점 · 인출 · 분산 복습 · 전이.</p>
</div>
</div>
<div class="profile-wrap fade-in d3">
{profile_img_html}
<div class="profile-text">
<div class="directed">Directed by</div>
<p class="name">이영우 · Youngwoo Lee</p>
</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_auth_gate_page() -> None:
    _render_landing_hero()

    st.markdown(
        '<div class="auth-area-title fade-in d4">'
        '<div class="lead">Member Access</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # 폼은 가운데 좁게
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
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

    st.markdown(
        '<div class="footer">© Math Archive · Directed by 이영우</div>',
        unsafe_allow_html=True,
    )


def require_auth() -> None:
    """페이지 시작부에서 호출. 인증 안 됐거나 미승인이면 적절한 화면 띄우고 st.stop()."""
    # 비번 재설정 링크 분기
    token = st.query_params.get("reset_token")
    if token:
        _render_password_reset_page(token)
        st.stop()

    # 쿠키 기반 자동 로그인 복원 (30일 영속). session_state 가 비어있어도
    # 유효한 쿠키 토큰이 있으면 사용자 정보를 session_state 에 다시 채워넣는다.
    auth.restore_session_from_cookie()

    if not auth.is_logged_in():
        _render_auth_gate_page()
        st.stop()

    if not auth.is_approved():
        _render_pending_page()
        st.stop()

    # 인증 통과한 사용자: 글로벌 톤(딥 블루) + status widget 숨김 적용.
    # 모든 페이지(main / 검수 / 관리자 / 클리닉)에 자동 적용 — 일관성 확보.
    st.markdown(_AUTHED_GLOBAL_CSS, unsafe_allow_html=True)

    # 세션 첫 진입에 한해 풀스크린 entry loader 1회 표시.
    # CSS 애니메이션으로 1.7s 후 자동 fade-out, pointer-events:none 이라
    # 사용자 인터랙션 차단도 없음. 페이지 이동·rerun 마다 반복 노출 방지.
    if not st.session_state.get("_entry_loader_shown"):
        st.markdown(_ENTRY_LOADER_HTML, unsafe_allow_html=True)
        st.session_state._entry_loader_shown = True

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
