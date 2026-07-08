"""인증 UI — 로그인/회원가입/찾기/재설정/대기 화면.

main.py 의 진입부에서 require_auth() 한 줄로 호출. 로그인 안 된 상태면 자동으로 폼 렌더 후 st.stop().
URL 에 ?reset_token=... 이 있으면 재설정 화면으로 분기.
"""
from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

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
                    # JS 오버레이는 parent.document 에 직접 부착되므로 rerun
                    # 후에도 살아남음. 가드는 require_auth 에서 활용.
                    st.session_state.pop("_entry_loader_shown", None)
                    st.markdown(_AUTHED_GLOBAL_CSS, unsafe_allow_html=True)
                    _inject_js_entry_loader()
                # switch_page 대신 단순 rerun. transition broken DOM 회피.
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
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

:root {
  /* 소개페이지(landing) 팔레트와 통일 — 2026-07 라이트 톤 */
  --bg: #f5f8ff;
  --bg-soft: #ffffff;
  --bg-card: #ffffff;
  --accent: #2b6fff;
  --accent-strong: #1a4fd4;
  --gold: #2b6fff;
  --gold-light: #9ec1ff;
  --text: #0a1020;
  --text-soft: #5f6c87;
  --border: #e3e9f7;
  --ink: #0a1020;
  --muted: #5f6c87;
}

/* 소개페이지와 동일한 페이퍼 배경 */
.stApp {
  background: var(--bg) !important;
}
html, body { background: var(--bg) !important; }
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, .block-container { background: transparent !important; }
/* 사이드바 영역 전부 숨김 — 와일드카드 + 명시 셀렉터 보강 */
/* 로그인 페이지에선 사이드바 컨테이너만 숨김 — 자식은 자동 비표시 */
section[data-testid="stSidebar"],
aside[data-testid="stSidebar"],
div[data-testid="stSidebar"],
[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 1.5rem !important; max-width: 1200px !important; }

/* 흐르는 수식 배경 */
.math-bg {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  overflow: hidden; opacity: 0.10;
}
.math-bg span {
  position: absolute;
  font-family: 'Pretendard', serif;
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
/* eyebrow — 파란 pill (소개페이지 톤) */
.hero .eyebrow {
  display: inline-block;
  font-family: 'Pretendard Variable', 'Pretendard', sans-serif;
  letter-spacing: 0.45em;
  font-size: 13px; font-weight: 700;
  color: var(--accent);
  border: 1px solid var(--border);
  background: #ffffff;
  padding: 9px 26px;
  border-radius: 999px;
  margin-bottom: 34px;
  text-transform: uppercase;
}
/* h1 — 소개페이지의 거대 헤딩 톤 (800 weight, -0.02em 자간, ink 색) */
.hero h1 {
  font-family: 'Pretendard Variable', 'Pretendard', sans-serif;
  font-weight: 800;
  font-size: clamp(38px, 5.4vw, 64px);
  line-height: 1.15;
  margin: 0 0 22px;
  letter-spacing: -0.03em;
  color: var(--ink) !important;
}
.hero h1 .grad {
  color: var(--accent) !important;
  -webkit-text-fill-color: var(--accent);
}
.hero .sub {
  font-family: 'Pretendard Variable', 'Pretendard', sans-serif;
  font-weight: 700;
  font-size: clamp(22px, 2.0vw, 28px);
  color: var(--ink);
  letter-spacing: -0.01em;
}
.hero .sub .num {
  color: var(--accent);
  font-weight: 800;
}

/* 섹션 헤딩 — 소개페이지의 kicker 톤 */
.section-title {
  font-family: 'Pretendard Variable', 'Pretendard', sans-serif;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.5em;
  color: var(--accent);
  text-align: center;
  margin: 72px 0 40px;
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
/* feature-circle — 라이트 흰 카드, 얇은 border, 소프트 shadow (소개페이지 톤) */
.feature-circle {
  position: absolute;
  border-radius: 50%;
  background: #ffffff;
  border: 1px solid var(--border);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center;
  padding: 26px;
  box-sizing: border-box;
  transition: transform 0.35s ease, border-color 0.35s ease,
              box-shadow 0.35s ease;
  width: var(--d, 220px);
  height: var(--d, 220px);
  left: var(--x, 50%);
  top: var(--y, 50%);
  transform: translate(-50%, -50%);
  cursor: default;
  box-shadow: 0 4px 20px rgba(43, 111, 255, 0.06),
              0 1px 3px rgba(10, 16, 32, 0.04);
}
.feature-circle:hover {
  transform: translate(-50%, -50%) scale(1.06);
  border-color: var(--accent);
  box-shadow: 0 12px 40px rgba(43, 111, 255, 0.16),
              0 2px 8px rgba(10, 16, 32, 0.06);
  z-index: 2;
}
.feature-circle .icon {
  width: 38px; height: 38px;
  margin-bottom: 14px;
  color: var(--accent);
  display: flex; align-items: center; justify-content: center;
}
.feature-circle .icon svg {
  width: 100%; height: 100%;
  display: block;
}
.feature-circle h3 {
  font-family: 'Pretendard Variable', 'Pretendard', sans-serif;
  font-weight: 800;
  font-size: 12px;
  letter-spacing: 0.32em;
  color: var(--accent) !important;
  text-shadow: none;
  margin: 0 0 10px;
  text-transform: uppercase;
  line-height: 1.2;
  text-align: center;
  text-indent: 0.32em;
}
.feature-circle .sub-ko {
  font-family: 'Pretendard Variable', 'Pretendard', sans-serif;
  font-weight: 800;
  font-size: 15px;
  color: var(--ink);
  letter-spacing: -0.02em;
  margin-bottom: 10px;
  display: block;
  text-align: center;
}
.feature-circle p {
  font-family: 'Pretendard Variable', 'Pretendard', sans-serif;
  font-size: 13px;
  line-height: 1.6;
  color: var(--muted);
  margin: 0;
  max-width: 88%;
  text-align: center;
  font-weight: 500;
}

/* highlight — 중앙 대형 카드: 파란 그라디언트 배경 + 흰 텍스트 (image #40 톤) */
.feature-circle.highlight {
  background: linear-gradient(135deg, var(--accent) 0%, #4d85ff 100%);
  border: none;
  box-shadow: 0 20px 50px rgba(43, 111, 255, 0.28),
              0 4px 12px rgba(43, 111, 255, 0.15);
}
.feature-circle.highlight:hover {
  transform: translate(-50%, -50%) scale(1.04);
  box-shadow: 0 24px 60px rgba(43, 111, 255, 0.35),
              0 6px 16px rgba(43, 111, 255, 0.2);
}
.feature-circle.highlight .icon {
  color: #ffffff;
  width: 52px; height: 52px;
}
.feature-circle.highlight h3 {
  color: rgba(255, 255, 255, 0.85) !important;
  font-size: 12px;
  letter-spacing: 0.4em;
  text-indent: 0.4em;
}
.feature-circle.highlight .sub-ko {
  color: #ffffff !important;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 14px;
}
.feature-circle.highlight p {
  color: rgba(255, 255, 255, 0.88) !important;
  font-size: 14px;
  max-width: 82%;
  font-weight: 500;
}
.feature-circle.highlight::after {
  content: "FEATURED";
  position: absolute;
  top: 18%;
  font-family: 'Pretendard Variable', 'Pretendard', sans-serif;
  font-size: 9px;
  letter-spacing: 0.4em;
  color: rgba(255, 255, 255, 0.75);
  font-weight: 700;
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
  border-top: 1px solid rgba(110, 150, 255, 0.25);
  border-bottom: 1px solid rgba(110, 150, 255, 0.25);
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
  font-family: 'Pretendard', serif;
  font-style: italic;
  font-size: 16px;
  color: var(--gold);
  letter-spacing: 0.18em;
  margin-bottom: 4px;
}
.profile-text .name {
  font-family: 'Pretendard', 'Pretendard', sans-serif;
  font-weight: 800;
  font-size: 30px;
  color: var(--text);
  margin: 0 0 6px;
  letter-spacing: 0.02em;
}
.profile-text .role {
  font-family: 'Pretendard', sans-serif;
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
  font-family: 'Pretendard', sans-serif;
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
  font-family: 'Pretendard', sans-serif !important;
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
  font-family: 'Pretendard', sans-serif;
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
# 랜딩의 _LANDING_CSS 와 색조 통일 (#060b18 딥 블루).
# Streamlit 의 기본 "Running fn()..." 디버그 토스트도 영구 숨김.
_AUTHED_GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

:root{
  --m-ink:#0a1020; --m-blue:#2b6fff; --m-blue-d:#1c54e0; --m-blue-soft:#9ec1ff;
  --m-text:#16223c; --m-muted:#5c6a86; --m-line:#e4e9f5; --m-paper:#f6f8fe;
}

/* ── 전역 폰트: Pretendard (랜딩과 통일) */
html, body, .stApp, .stApp *:not(.katex):not(.katex *){
  font-family:'Pretendard',-apple-system,'Apple SD Gothic Neo','Pretendard',sans-serif;
}
/* 머티리얼 아이콘 폰트 보존 — 전역 폰트 override 로 아이콘 ligature 깨짐 방지 */
[data-testid="stIconMaterial"],
.material-icons, .material-icons-outlined, .material-icons-round, .material-icons-sharp,
[class*="material-symbols"]{
  font-family:'Material Symbols Rounded','Material Symbols Outlined',
    'Material Symbols Sharp','Material Icons' !important;
}

/* ── 라이트 톤 (가독성 우선) */
.stApp, [data-testid="stAppViewContainer"]{ background:var(--m-paper) !important; }
[data-testid="stHeader"]{ background:transparent !important; }
[data-testid="stMain"]{ color:var(--m-text); }

/* 사이드바 라이트 */
[data-testid="stSidebar"] > div:first-child{
  background:#ffffff !important; border-right:1px solid var(--m-line) !important;
}

/* 제목 */
[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3{
  color:var(--m-ink) !important; font-weight:800 !important; letter-spacing:-.01em;
}

/* 본문 가독성 */
[data-testid="stMain"] p,[data-testid="stMain"] li{ color:var(--m-text); line-height:1.7; }

/* 버튼 — 블루 프라이머리 */
.stButton button,.stFormSubmitButton button,.stDownloadButton button{
  border-radius:10px !important; font-weight:700 !important;
  border:1px solid var(--m-line) !important;
  transition:transform .15s, box-shadow .15s !important;
}
.stButton button[kind="primary"],.stFormSubmitButton button,.stDownloadButton button{
  background:var(--m-blue) !important; color:#fff !important; border:none !important;
  box-shadow:0 8px 22px -10px rgba(43,111,255,.6) !important;
}
.stButton button[kind="primary"]:hover,.stFormSubmitButton button:hover,
.stDownloadButton button:hover{
  transform:translateY(-1px); box-shadow:0 12px 28px -10px rgba(43,111,255,.78) !important;
}

/* 입력 */
.stTextInput input,.stTextArea textarea,.stNumberInput input{
  border-radius:10px !important; border:1px solid var(--m-line) !important;
}
.stTextInput input:focus,.stTextArea textarea:focus,.stNumberInput input:focus{
  border-color:var(--m-blue) !important; box-shadow:0 0 0 3px rgba(43,111,255,.15) !important;
}

/* 탭 */
.stTabs [aria-selected="true"]{ color:var(--m-blue) !important; font-weight:700 !important; }
.stTabs [data-baseweb="tab-highlight"]{ background:var(--m-blue) !important; }

/* 확장/지표/표 카드화 */
[data-testid="stExpander"]{ border:1px solid var(--m-line) !important; border-radius:12px !important; background:#fff !important; }
[data-testid="stMetric"]{ background:#fff; border:1px solid var(--m-line); border-radius:12px; padding:14px 16px; }
[data-testid="stDataFrame"]{ border-radius:12px !important; overflow:hidden; }

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
    radial-gradient(ellipse at 90% 90%, rgba(91,140,255,0.16) 0%, transparent 55%),
    #060b18;
  z-index: 999999;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: 'Pretendard', 'Pretendard', -apple-system, sans-serif;
  color: #e9ecf8;
  /* 기본 60s 보이고 1s fade out — 페이지 마지막에 도착하는
     "entry loader dismiss" CSS 가 더 빠른 fade-out 으로 덮어씀.
     즉 60s 는 안전망(컨텐츠가 그때까지 안 그려져도 결국 사라짐),
     실제로는 main 페이지 모든 위젯 그려진 직후 즉시 fade-out. */
  animation: entryFadeOut 1s 60s forwards;
  pointer-events: none;
}
.entry-loader .brand {
  font-size: 18px;
  letter-spacing: 0.5em;
  color: #9ec1ff;
  margin-bottom: 28px;
  font-weight: 700;
  border: 1px solid rgba(158,193,255,0.5);
  padding: 10px 28px;
  border-radius: 999px;
}
.entry-loader h2 {
  font-size: clamp(40px, 5.6vw, 72px);
  font-weight: 800;
  letter-spacing: -0.01em;
  background: linear-gradient(135deg, #5b8cff 0%, #9ec1ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 14px;
  text-align: center;
}
.entry-loader .sub {
  font-size: 20px;
  letter-spacing: 0.3em;
  color: #a6b2d4;
  margin-bottom: 40px;
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
  background: linear-gradient(90deg, transparent, #5b8cff 50%, transparent);
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
<div class="brand">MATHOLOGY</div>
<h2>Entering MATHOLOGY</h2>
<div class="sub">130,000+ Questions · Infinite Possibilities</div>
<div class="bar"></div>
</div>
"""


# ── JavaScript 기반 entry loader (컨텐츠 로드 끝 = 즉시 dismiss) ─────
# iframe 안 script 가 parent.document 에 직접 오버레이 inject 하고,
# MutationObserver 로 main.py 끝의 <div id="mathdb-ready"> sentinel
# 등장을 감시. 발견 즉시 fade-out. 안전망 30s timeout 으로 무한 로딩 0%.
_JS_ENTRY_LOADER = """
<script>
(function() {
  const doc = window.parent.document;
  if (doc.getElementById('mathdb-entry-loader')) return;

  const overlay = doc.createElement('div');
  overlay.id = 'mathdb-entry-loader';
  overlay.style.cssText = `
    position: fixed; inset: 0; z-index: 2147483647;
    background:
      radial-gradient(ellipse at 30% 20%, #163074 0%, transparent 55%),
      radial-gradient(ellipse at 90% 90%, rgba(91,140,255,0.16) 0%, transparent 55%),
      #060b18;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    font-family: 'Pretendard', 'Pretendard', -apple-system, sans-serif;
    color: #e9ecf8;
    transition: opacity 0.5s ease-out;
    pointer-events: none;
  `;
  overlay.innerHTML = `
    <div style="font-size:18px; letter-spacing:0.5em; color:#9ec1ff;
                margin-bottom:28px; font-weight:700;
                border:1px solid rgba(158,193,255,0.5);
                padding:10px 28px; border-radius:999px;">MATHOLOGY</div>
    <h2 style="font-size:clamp(40px,5.6vw,72px); font-weight:800;
               letter-spacing:-0.01em;
               background:linear-gradient(135deg,#5b8cff 0%,#9ec1ff 100%);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;
               background-clip:text; margin:0 0 14px; text-align:center;">
      Entering MATHOLOGY
    </h2>
    <div style="font-size:20px; letter-spacing:0.3em; color:#a6b2d4;
                margin-bottom:40px; font-weight:500; text-transform:uppercase;">
      130,000+ Questions · Infinite Possibilities
    </div>
    <div style="width:240px; height:2px; background:rgba(125,220,255,0.15);
                position:relative; overflow:hidden; border-radius:2px;">
      <div id="mathdb-shimmer" style="position:absolute; inset:0;
                  background:linear-gradient(90deg,transparent,#5b8cff 50%,transparent);"></div>
    </div>
    <style>
      @keyframes mathdb-shimmer-anim {
        from { transform: translateX(-100%); } to { transform: translateX(100%); }
      }
      #mathdb-shimmer { animation: mathdb-shimmer-anim 0.95s linear infinite; }
    </style>
  `;
  doc.body.appendChild(overlay);

  function dismiss() {
    overlay.style.opacity = '0';
    setTimeout(() => {
      if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
    }, 500);
  }

  // 이미 ready sentinel 있으면 즉시 dismiss
  if (doc.getElementById('mathdb-ready')) {
    dismiss();
    return;
  }

  const observer = new MutationObserver(() => {
    if (doc.getElementById('mathdb-ready')) {
      dismiss();
      observer.disconnect();
      clearTimeout(safetyTimer);
    }
  });
  observer.observe(doc.body, { childList: true, subtree: true });

  // 안전망: 30s 후 강제 dismiss — sentinel 어떤 이유로 못 와도 결국 사라짐
  const safetyTimer = setTimeout(() => {
    dismiss();
    observer.disconnect();
  }, 30000);
})();
</script>
"""


def _inject_js_entry_loader() -> None:
    """JavaScript 기반 풀스크린 entry loader 표시. main 페이지 sentinel
    이 DOM 에 나타날 때까지 유지. CSS animation 기반보다 안전 (컨텐츠
    로드 끝 = 즉시 dismiss). iframe height=0 이라 시각적 영향 없음."""
    components.html(_JS_ENTRY_LOADER, height=0)


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
<span class="grad">MATHOLOGY</span>
</h1>
<p class="sub">
<span class="num">130,000+</span> Questions · Infinite Possibilities
</p>
</section>
<div class="section-title fade-in d1">Core Capabilities</div>
<div class="feature-scatter fade-in d2">
<div class="feature-circle highlight" style="--x:50%; --y:42%; --d:320px;">
<div class="icon">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
</div>
<h3>Rapid Forge</h3>
<span class="sub-ko">교재 · 시험지 즉시 제작</span>
<p>단 몇 번의 클릭으로 출판 품질 PDF 빌드.</p>
</div>
<div class="feature-circle" style="--x:17%; --y:20%; --d:230px;">
<div class="icon">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
</div>
<h3>Massive Data</h3>
<span class="sub-ko">방대한 문항 데이터</span>
<p>고1~고3 전문항 130,000개.</p>
</div>
<div class="feature-circle" style="--x:83%; --y:22%; --d:220px;">
<div class="icon">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 4H4l7 8-7 8h16"/></svg>
</div>
<h3>LaTeX Engine</h3>
<span class="sub-ko">완벽한 수식 렌더링</span>
<p>HWP → KaTeX 무손실 변환.</p>
</div>
<div class="feature-circle" style="--x:22%; --y:82%; --d:235px;">
<div class="icon">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 3H2l8 9v5l4 2v-7l8-9z"/></svg>
</div>
<h3>Smart Filter</h3>
<span class="sub-ko">정교한 추출 엔진</span>
<p>학교 · 단원 · 난이도 다차원 검색.</p>
</div>
<div class="feature-circle" style="--x:78%; --y:80%; --d:225px;">
<div class="icon">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v5a4 4 0 0 0 4 4v0a4 4 0 0 0 4-4V3"/><path d="M7 12v3a5 5 0 0 0 5 5v0a5 5 0 0 0 5-5v-3"/><circle cx="17" cy="9" r="2"/></svg>
</div>
<h3>PRISM Clinic</h3>
<span class="sub-ko">오답 5스펙트럼 진단</span>
<p>계산정확성·조건해석·개념내재·전략선택·시간관리.</p>
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
        '<div class="footer">© MATHOLOGY · Directed by YOUNGWOO LEE</div>',
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

    # NOTE: refresh_session_cookie 는 호출 시 mgr.set() 비동기 응답 대기로
    # 페이지 hang 사고 발생 → 호출 제거. cookie expires_at=30일 명시로 충분.

    # 인증 통과한 사용자: 글로벌 톤(딥 블루) + status widget 숨김 적용.
    # 모든 페이지(main / 검수 / 관리자 / 클리닉)에 자동 적용 — 일관성 확보.
    st.markdown(_AUTHED_GLOBAL_CSS, unsafe_allow_html=True)

    # main.py 가 set_page_config 직후 사이드바를 영구 숨김 처리했으므로,
    # 인증 통과 시점에 명시적으로 다시 보임. display: none !important 를
    # display: flex !important 로 덮어쓰기.
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        section[data-testid="stSidebar"],
        aside[data-testid="stSidebar"] { display: flex !important; }
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarContent"] { display: block !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 세션 첫 진입에 한해 JS 풀스크린 entry loader 1회 표시.
    # MutationObserver 가 main.py 끝의 <div id="mathdb-ready"> sentinel
    # 감지 시 즉시 fade-out. 안전망 30s. 사용자 인터랙션 차단 없음.
    if not st.session_state.get("_entry_loader_shown"):
        _inject_js_entry_loader()
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
