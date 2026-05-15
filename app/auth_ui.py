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


_LANDING_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800;900&family=Cormorant+Garamond:ital,wght@1,500&family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

:root {
  --bg: #07091a;
  --bg-soft: #0d1230;
  --bg-card: rgba(20, 28, 60, 0.55);
  --accent: #4cc4ff;
  --accent-strong: #5fd3ff;
  --gold: #d2af6e;
  --gold-light: #f0cd87;
  --text: #e9ecf8;
  --text-soft: #9aa3c4;
  --border: rgba(76, 196, 255, 0.18);
}

/* 본 페이지 자체 다크화 */
.stApp {
  background:
    radial-gradient(ellipse at top, #131a3f 0%, transparent 55%),
    radial-gradient(ellipse at bottom right, rgba(76,196,255,0.08) 0%, transparent 50%),
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
  font-size: 11px; font-weight: 700;
  color: var(--gold);
  border: 1px solid rgba(210, 175, 110, 0.4);
  padding: 6px 18px;
  border-radius: 999px;
  margin-bottom: 28px;
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
  font-weight: 500;
  font-size: clamp(15px, 1.6vw, 19px);
  color: var(--text-soft);
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
  font-size: 12px;
  letter-spacing: 0.5em;
  color: var(--gold);
  text-align: center;
  margin: 60px 0 28px;
  text-transform: uppercase;
}

/* 카드 그리드 */
.feature-grid {
  position: relative; z-index: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
  margin-bottom: 60px;
}
.feature-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 28px 22px;
  backdrop-filter: blur(8px);
  transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}
.feature-card:hover {
  transform: translateY(-4px);
  border-color: rgba(76, 196, 255, 0.55);
  box-shadow: 0 10px 30px rgba(76, 196, 255, 0.12);
}
.feature-card .icon {
  font-size: 26px;
  margin-bottom: 14px;
  display: inline-block;
}
.feature-card h3 {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 16px;
  letter-spacing: 0.06em;
  color: var(--accent-strong);
  margin: 0 0 8px;
  text-transform: uppercase;
}
.feature-card h3 .sub-ko {
  display: block;
  font-family: 'Noto Sans KR', sans-serif;
  font-weight: 500;
  font-size: 12px;
  color: var(--text-soft);
  letter-spacing: 0.02em;
  text-transform: none;
  margin-top: 4px;
}
.feature-card p {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 13px;
  line-height: 1.65;
  color: var(--text-soft);
  margin: 0;
}
.feature-card.highlight {
  background: linear-gradient(135deg, rgba(210, 175, 110, 0.12) 0%, rgba(76, 196, 255, 0.10) 100%);
  border-color: rgba(210, 175, 110, 0.45);
}
.feature-card.highlight h3 { color: var(--gold-light); }

/* 프로필 섹션 */
.profile-wrap {
  position: relative; z-index: 1;
  display: flex; align-items: center; justify-content: center;
  gap: 38px;
  padding: 40px 24px 30px;
  margin: 30px auto 10px;
  max-width: 720px;
  border-top: 1px solid rgba(210, 175, 110, 0.25);
  border-bottom: 1px solid rgba(210, 175, 110, 0.25);
  flex-wrap: wrap;
}
.profile-photo {
  width: 130px; height: 130px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--gold);
  box-shadow: 0 0 0 6px rgba(210, 175, 110, 0.08),
              0 12px 28px rgba(0,0,0,0.45);
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
  .profile-wrap { flex-direction: column; text-align: center; gap: 20px; }
  .profile-text { text-align: center; }
  .hero { padding: 40px 0 24px; }
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


def _render_landing_hero() -> None:
    """헤로 + 카드 + 프로필 — 로그인 폼 위에 얹는 마케팅 영역."""
    profile_uri = _img_data_uri("profile_lyw.jpeg")

    st.markdown(_LANDING_CSS, unsafe_allow_html=True)
    st.markdown(_MATH_BG, unsafe_allow_html=True)

    # HERO
    st.markdown(
        """
        <section class="hero fade-in">
          <div class="eyebrow">Mathematics · Data · Design</div>
          <h1>All-in-One Mathematics Library<br>
            <span class="grad">Math Archive</span>
          </h1>
          <p class="sub">
            <span class="num">120,000</span> Questions · Infinite Possibilities
          </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # FEATURES
    st.markdown(
        '<div class="section-title fade-in d1">Core Capabilities</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="feature-grid fade-in d2">
          <div class="feature-card">
            <div class="icon">📚</div>
            <h3>Massive Data<span class="sub-ko">방대한 문항 데이터</span></h3>
            <p>NGD 공동작업 고1~고3 전문항 120,000개 + 상세 해설을 단일 DB로 정제 수록.</p>
          </div>
          <div class="feature-card">
            <div class="icon">∑</div>
            <h3>LaTeX Engine<span class="sub-ko">완벽한 수식 렌더링</span></h3>
            <p>HWP 수식편집기를 KaTeX 로 무손실 변환. 가독성과 출판 품질을 동시에.</p>
          </div>
          <div class="feature-card">
            <div class="icon">🎯</div>
            <h3>Smart Filter<span class="sub-ko">정교한 추출 엔진</span></h3>
            <p>학교 · 단원 · 난이도 · 유형 · 키워드를 계층 결합한 다차원 검색.</p>
          </div>
          <div class="feature-card highlight">
            <div class="icon">⚡</div>
            <h3>Rapid Forge<span class="sub-ko">교재 · 시험지 즉시 제작</span></h3>
            <p>단 몇 번의 클릭으로 학원 브랜드의 교재와 모의고사를 출판 품질 PDF 로 빌드.</p>
          </div>
          <div class="feature-card">
            <div class="icon">🩺</div>
            <h3>Personal Clinic<span class="sub-ko">학생 맞춤 클리닉</span></h3>
            <p>취약점 진단 · 인출 · 분산 복습 · 전이 점수까지, 1인 1엔진 학습 관리.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # PROFILE
    profile_img_html = (
        f'<img src="{profile_uri}" alt="이영우" class="profile-photo" />'
        if profile_uri
        else '<div class="profile-photo" style="background:#1a2050;"></div>'
    )
    st.markdown(
        f"""
        <div class="profile-wrap fade-in d3">
          {profile_img_html}
          <div class="profile-text">
            <div class="directed">Directed by</div>
            <p class="name">이영우 · Youngwoo Lee</p>
            <div class="role">High School Math Specialist</div>
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
