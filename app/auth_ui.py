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
  --bg: #060b18;
  --bg-soft: #0c2156;
  --bg-card: rgba(28, 52, 110, 0.45);
  --accent: #5b8cff;
  --accent-strong: #9ec1ff;
  --gold: #9ec1ff;
  --gold-light: #cdddff;
  --text: #eaf0ff;
  --text-soft: #aab8e6;
  --border: rgba(110, 150, 255, 0.28);
}

/* 뒤 3D 큐브 캔버스가 비치도록 앱 배경 투명 (WebGL 실패 시 body 다크가 fallback) */
html, body { background: #060b18 !important; }
.stApp { background: transparent !important; }
#mathology-cube-bg { opacity: 0.6; }
/* 큐브 위 가독성 베일 — 폼/텍스트 영역을 살짝 어둡게 */
.cube-veil {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background:
    radial-gradient(ellipse at 50% 60%, rgba(6,11,24,.80) 0%, rgba(6,11,24,.42) 34%, transparent 66%),
    linear-gradient(180deg, rgba(6,11,24,.5) 0%, transparent 22%, transparent 68%, rgba(6,11,24,.72) 100%);
}
.block-container { position: relative; z-index: 1; }
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
.hero .eyebrow {
  display: inline-block;
  font-family: 'Pretendard', sans-serif;
  letter-spacing: 0.45em;
  font-size: 15px; font-weight: 700;
  color: var(--gold);
  border: 1px solid rgba(110, 150, 255, 0.4);
  padding: 9px 24px;
  border-radius: 999px;
  margin-bottom: 32px;
  text-transform: uppercase;
}
.hero h1 {
  font-family: 'Pretendard', 'Pretendard', sans-serif;
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
  font-family: 'Pretendard', sans-serif;
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
  font-family: 'Pretendard', sans-serif;
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
  border-color: rgba(158, 193, 255, 0.9);
  box-shadow: 0 24px 60px rgba(110, 150, 255, 0.4),
              0 0 50px rgba(110, 150, 255, 0.22);
}
.feature-circle .icon {
  font-size: 38px;
  margin-bottom: 12px;
  line-height: 1;
}
.feature-circle h3 {
  font-family: 'Pretendard', sans-serif;
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
  font-family: 'Pretendard', sans-serif;
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
  letter-spacing: 0.02em;
  margin-bottom: 12px;
  display: block;
  text-align: center;
}
.feature-circle p {
  font-family: 'Pretendard', sans-serif;
  font-size: 14px;
  line-height: 1.55;
  color: var(--text-soft);
  margin: 0;
  max-width: 84%;
  text-align: center;
}
.feature-circle.highlight {
  background:
    radial-gradient(ellipse at top, rgba(110, 150, 255, 0.30) 0%, transparent 60%),
    linear-gradient(135deg, rgba(110, 150, 255, 0.10) 0%, rgba(76, 196, 255, 0.08) 100%);
  border-color: rgba(110, 150, 255, 0.6);
  box-shadow: 0 0 60px rgba(110, 150, 255, 0.18),
              inset 0 0 40px rgba(110, 150, 255, 0.05);
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
  font-family: 'Pretendard', sans-serif;
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
# 랜딩의 _LANDING_CSS 와 색조 통일 (#0b1830 딥 블루).
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
    radial-gradient(ellipse at 90% 90%, rgba(76,196,255,0.15) 0%, transparent 55%),
    #0b1830;
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
      radial-gradient(ellipse at 90% 90%, rgba(76,196,255,0.15) 0%, transparent 55%),
      #0b1830;
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


# ── 로그인 화면 3D 큐브 배경 (랜딩 히어로와 동일 비주얼, 살짝) ─────
# entry loader 와 동일 기법: iframe(height=0) 안 module script 가
# parent.document 에 <canvas> 를 fixed 로 붙이고 Three.js 로 렌더.
# 가드로 rerun 시 중복 생성 방지. WebGL 실패해도 body 다크가 fallback.
_CUBE_BG_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><style>html,body{margin:0}</style>
<script type="importmap">
{"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js","three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"}}
</script></head><body>
<script type="module">
const doc = window.parent.document;
if (!doc.getElementById('mathology-cube-bg')) {
  const canvas = doc.createElement('canvas');
  canvas.id = 'mathology-cube-bg';
  canvas.style.cssText = 'position:fixed;inset:0;width:100vw;height:100vh;z-index:0;pointer-events:none;';
  doc.body.appendChild(canvas);
  const THREE = await import('three');
  const { RoomEnvironment } = await import('three/addons/environments/RoomEnvironment.js');
  const { EffectComposer } = await import('three/addons/postprocessing/EffectComposer.js');
  const { RenderPass } = await import('three/addons/postprocessing/RenderPass.js');
  const { UnrealBloomPass } = await import('three/addons/postprocessing/UnrealBloomPass.js');
  const W = () => window.parent.innerWidth, H = () => window.parent.innerHeight;
  const renderer = new THREE.WebGLRenderer({canvas, antialias:true});
  renderer.setPixelRatio(Math.min(window.parent.devicePixelRatio,2));
  renderer.setSize(W(), H(), false);
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#060b18');
  scene.fog = new THREE.Fog('#060b18', 14, 36);
  const camera = new THREE.PerspectiveCamera(50, W()/H(), 0.1, 100); camera.position.set(0,0,16);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.add(new THREE.AmbientLight(0x6f8bff, 0.4));
  const k = new THREE.DirectionalLight(0xffffff, 1.4); k.position.set(6,8,10); scene.add(k);
  const rl = new THREE.DirectionalLight(0x2b6fff, 1.1); rl.position.set(-8,-4,4); scene.add(rl);
  const group = new THREE.Group(); scene.add(group);
  const box = new THREE.BoxGeometry(1,1,1);
  const glass = new THREE.MeshPhysicalMaterial({color:0x9ec4ff,metalness:0,roughness:0.08,transmission:0.92,thickness:1.4,ior:1.4,clearcoat:1,clearcoatRoughness:0.1,envMapIntensity:1.3,transparent:true,opacity:0.9});
  const solid = new THREE.MeshPhysicalMaterial({color:0x3f74ff,metalness:0.1,roughness:0.35,envMapIntensity:0.9});
  const cubes = []; const COLS=7, ROWS=5;
  for(let i=0;i<COLS;i++) for(let j=0;j<ROWS;j++){
    if(Math.random()<0.4) continue;
    const m = new THREE.Mesh(box, Math.random()<0.78?glass:solid);
    m.position.set((i-(COLS-1)/2)*2.6+(Math.random()-0.5)*0.8,(j-(ROWS-1)/2)*2.6+(Math.random()-0.5)*0.8,-Math.random()*7-i*0.4);
    m.scale.setScalar(1.0+Math.random()*1.4); m.rotation.set(Math.random()*0.3,Math.random()*0.3,0);
    m.userData.f = Math.random()*Math.PI*2; m.userData.a = 0.15+Math.random()*0.25;
    group.add(m); cubes.push(m);
  }
  const glowMat = new THREE.MeshStandardMaterial({color:0xffb347,emissive:0xff9a2e,emissiveIntensity:2.0,roughness:0.4});
  const glow = new THREE.Mesh(box, glowMat); glow.position.set(3.0,0.6,2); glow.scale.setScalar(2.1); group.add(glow);
  const glowL = new THREE.PointLight(0xffae52, 16, 26, 2); glowL.position.copy(glow.position); scene.add(glowL);
  const composer = new EffectComposer(renderer); composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W(),H()), 0.7, 0.7, 0.85));
  let mx=0,my=0,tx=0,ty=0;
  window.parent.addEventListener('mousemove', e=>{ tx=(e.clientX/W()-0.5); ty=(e.clientY/H()-0.5); });
  const clock = new THREE.Clock();
  function tick(){
    requestAnimationFrame(tick);
    const t = clock.getElapsedTime();
    mx += (tx-mx)*0.05; my += (ty-my)*0.05;
    group.rotation.y = Math.sin(t*0.07)*0.16 + mx*0.4; group.rotation.x = my*0.25;
    group.position.x = -mx*1.0; group.position.y = my*0.7;
    for(const c of cubes){ c.position.y += Math.sin(t*0.6+c.userData.f)*0.016*c.userData.a; c.rotation.z += 0.0005; }
    glowMat.emissiveIntensity = 1.9 + Math.sin(t*1.4)*0.35;
    composer.render();
  }
  tick();
  window.parent.addEventListener('resize', ()=>{ camera.aspect=W()/H(); camera.updateProjectionMatrix(); renderer.setSize(W(),H(),false); composer.setSize(W(),H()); });
}
</script></body></html>
"""


def _inject_cube_background() -> None:
    """로그인 화면 뒤에 3D 큐브 배경 렌더 (parent.document 에 fixed canvas)."""
    components.html(_CUBE_BG_HTML, height=0)


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
<div class="cube-veil"></div>
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
<div class="icon">⚡</div>
<h3>Rapid Forge</h3>
<span class="sub-ko">교재 · 시험지 즉시 제작</span>
<p>단 몇 번의 클릭으로 출판 품질 PDF 빌드.</p>
</div>
<div class="feature-circle" style="--x:17%; --y:20%; --d:230px;">
<div class="icon">📚</div>
<h3>Massive Data</h3>
<span class="sub-ko">방대한 문항 데이터</span>
<p>고1~고3 전문항 130,000개.</p>
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
    _inject_cube_background()
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
