"""매쏠로지 통합 테마 — landing 페이지 디자인 토큰을 Streamlit 에 이식.

각 페이지 상단에서 `apply_theme()` 한 번 호출하면 아래 스타일 모두 적용.
- Pretendard 폰트 (웹폰트 CDN)
- landing 팔레트 (--ink/--blue/--paper/--text/--muted/--line)
- 라이트 input/버튼/select (다크 강제 해제)
- 헤딩 폰트 위계 (32/22/16) + 자간 -.02em
- 안내 박스·구분선 톤다운
- 사이드바 라이트 화
"""
from __future__ import annotations

import streamlit as st


_THEME_CSS = """
<style>
/* Pretendard 웹폰트 */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css');

:root {
    --ink: #0a1020;
    --blue: #2b6fff;
    --blue-soft: #9ec1ff;
    --paper: #f5f8ff;
    --text: #13203c;
    --muted: #5f6c87;
    --line: #e3e9f7;
}

/* 전역 폰트 — KaTeX 수식은 자체 폰트 유지 (문제/선지 폰트 절대 건드리지 말 것)
   나머지 모든 UI 요소를 Pretendard Variable 로 통일 */
html, body, .stApp,
.stMarkdown, .stMarkdown p, .stMarkdown li,
h1, h2, h3, h4, h5, h6, p, span, div, li, a, label,
.stButton, .stButton button,
.stDownloadButton, .stDownloadButton button,
.stFormSubmitButton, .stFormSubmitButton button,
.stTextInput, .stNumberInput, .stTextArea, .stDateInput, .stTimeInput,
.stSelectbox, .stMultiSelect, .stRadio, .stCheckbox,
.stTabs, [data-baseweb="tab"], [data-baseweb="tab-list"],
[data-testid="stExpander"], [data-testid="stExpander"] *,
[data-testid="stWidgetLabel"],
[data-testid="stCaptionContainer"],
[data-testid="stAlert"], [data-testid="stAlert"] *,
[data-testid="stMetric"], [data-testid="stMetric"] *,
[data-testid="stSidebar"], [data-testid="stSidebar"] * {
    font-family: 'Pretendard Variable', 'Pretendard',
        -apple-system, 'Apple SD Gothic Neo', sans-serif !important;
}

/* KaTeX 는 자체 폰트 (KaTeX_Main/_Math/_AMS) 로 복구 — 사용자 명시 요청 */
.katex, .katex *,
.katex-html, .katex-html *,
.katex-display, .katex-display * {
    font-family: KaTeX_Main, KaTeX_Math, KaTeX_Size1,
        KaTeX_Size2, KaTeX_Size3, KaTeX_Size4, KaTeX_AMS,
        KaTeX_Caligraphic, KaTeX_Fraktur, KaTeX_SansSerif,
        KaTeX_Script, KaTeX_Typewriter, 'Times New Roman', serif !important;
}

.stApp {
    background: var(--paper) !important;
    color: var(--text) !important;
}

/* ── 헤딩 위계 (컴팩트) ─────────────────────── */
[data-testid="stMain"] h1 {
    font-size: 26px !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: var(--ink) !important;
    line-height: 1.25 !important;
    margin-top: 0.25rem !important;
    margin-bottom: 0.6rem !important;
}
[data-testid="stMain"] h2 {
    font-size: 18px !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: var(--ink) !important;
    margin-top: 1.6rem !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stMain"] h3 {
    font-size: 14.5px !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
    color: var(--ink) !important;
    margin-top: 1.0rem !important;
    margin-bottom: 0.4rem !important;
}
[data-testid="stMain"] .stCaption,
[data-testid="stMain"] [data-testid="stCaptionContainer"] {
    color: var(--muted) !important;
    font-size: 12.5px !important;
    line-height: 1.55 !important;
}

/* ── 입력 컴포넌트 라이트화 (다크 강제 해제) ─ */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stDateInput input,
.stTimeInput input,
[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
    background: #ffffff !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    font-size: 14.5px !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus,
.stDateInput input:focus,
[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] > div:focus-within {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(43, 111, 255, 0.12) !important;
    outline: none !important;
}

/* multiselect chip */
[data-baseweb="tag"] {
    background: rgba(43, 111, 255, 0.08) !important;
    color: var(--blue) !important;
    border: none !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
}

/* ── 버튼 (파랑 X, 검정/화이트 톤) ────────── */
/* Streamlit 버전에 따라 kind attribute 대소문자·이름 다름 → 여러 selector */
.stButton button,
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    letter-spacing: -0.01em !important;
    border: 1px solid var(--line) !important;
    background: #ffffff !important;
    color: var(--ink) !important;
    padding: 0.4rem 0.85rem !important;
    transition: background 0.15s, border-color 0.15s !important;
}
.stButton button:hover,
.stButton > button:hover {
    background: #f1f4fb !important;
    border-color: #c9d3ea !important;
    color: var(--ink) !important;
}
/* Primary — 검정 톤 (파랑 X) */
.stButton button[kind="primary"],
.stButton button[data-testid="baseButton-primary"],
button[kind="primary"],
button[data-testid="baseButton-primary"] {
    background: var(--ink) !important;
    color: #ffffff !important;
    border: 1px solid var(--ink) !important;
}
.stButton button[kind="primary"]:hover,
.stButton button[data-testid="baseButton-primary"]:hover,
button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
    background: #1a2544 !important;
    border-color: #1a2544 !important;
    color: #ffffff !important;
}

/* Download 버튼도 같은 스타일 */
.stDownloadButton button {
    border-radius: 10px !important;
    background: var(--ink) !important;
    color: #ffffff !important;
    border: 1px solid var(--ink) !important;
    font-weight: 600 !important;
}

/* ── 안내 박스 (info/success/warning/error) 톤다운 ── */
[data-testid="stAlert"] {
    background: #ffffff !important;
    border: 1px solid var(--line) !important;
    border-left: 3px solid var(--blue-soft) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    padding: 14px 18px !important;
}
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
    color: var(--text) !important;
}
/* success — 은은한 초록 */
[data-testid="stAlert"][kind="success"],
.stAlert.stSuccess {
    border-left-color: #10b981 !important;
}
/* warning — 은은한 주황 */
[data-testid="stAlert"][kind="warning"],
.stAlert.stWarning {
    border-left-color: #f59e0b !important;
}
/* error — 은은한 빨강 */
[data-testid="stAlert"][kind="error"],
.stAlert.stError {
    border-left-color: #ef4444 !important;
}

/* ── Expander / Container border ─────────── */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 2px rgba(10, 16, 32, 0.03) !important;
}
[data-testid="stExpander"] summary {
    color: var(--ink) !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    padding: 8px 12px !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    padding: 4px 12px 12px 12px !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
}

/* ── Metric 카드 (컴팩트) ───────────────────── */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    box-shadow: 0 1px 2px rgba(10, 16, 32, 0.03) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: var(--muted) !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}
[data-testid="stMetricValue"] {
    font-size: 20px !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: var(--ink) !important;
    line-height: 1.2 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 11.5px !important;
    color: var(--muted) !important;
}

/* ── Divider ──────────────────────────────── */
hr {
    border-color: var(--line) !important;
    margin: 1.0rem 0 !important;
}

/* ── Tab ──────────────────────────────────── */
[data-baseweb="tab-list"] {
    border-bottom: 1px solid var(--line) !important;
    gap: 4px !important;
}
[data-baseweb="tab"] {
    color: var(--muted) !important;
    font-weight: 600 !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: var(--ink) !important;
    border-bottom-color: var(--blue) !important;
}

/* ── 사이드바 ─────────────────────────────── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text) !important;
}
[data-testid="stSidebar"] .stButton button {
    background: #ffffff !important;
    color: var(--ink) !important;
    border: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #f1f4fb !important;
    color: var(--ink) !important;
    border-color: #c9d3ea !important;
}
/* 사이드바 primary — 검정 (해제 버튼 등 secondary 는 위 흰색) */
[data-testid="stSidebar"] .stButton button[kind="primary"],
[data-testid="stSidebar"] button[kind="primary"] {
    background: var(--ink) !important;
    color: #ffffff !important;
    border: 1px solid var(--ink) !important;
}
[data-testid="stSidebar"] .stButton button[kind="primary"]:hover,
[data-testid="stSidebar"] button[kind="primary"]:hover {
    background: #1a2544 !important;
    color: #ffffff !important;
}

/* ── Radio ────────────────────────────────── */
[data-testid="stRadio"] label {
    color: var(--text) !important;
    font-weight: 500 !important;
}

/* ── Slider ───────────────────────────────── */
[data-testid="stSlider"] [role="slider"] {
    background: var(--blue) !important;
}

/* ── Code block (스타일 정리) ─────────────── */
code, pre {
    background: #eef2f8 !important;
    color: var(--ink) !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}

/* ── 여백 (breathing room, 컴팩트) ────────── */
[data-testid="stMain"] .block-container {
    padding-top: 1.6rem !important;
    padding-bottom: 3rem !important;
    max-width: 1180px !important;
}

/* ── 안내 박스 크기 축소 ───────────────────── */
[data-testid="stAlert"] {
    padding: 10px 14px !important;
    font-size: 13.5px !important;
}

/* Streamlit 기본 라벨 */
[data-testid="stWidgetLabel"] {
    color: var(--muted) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: -0.005em !important;
}

/* Status widget 등 잔여 다크 요소 제거 */
[data-testid="stStatusWidget"],
[data-testid="stConnectionStatus"],
[data-testid="stToolbar"] {
    background: transparent !important;
}

/* 로그인 페이지 등에서 뒤에 붙은 3D 큐브 배경 강제 hide */
#mathology-cube-bg,
canvas#scene,
.cube-veil,
.math-bg {
    display: none !important;
}

/* stApp 배경 라이트 강제 (다크 gradient override) */
.stApp,
[data-testid="stAppViewContainer"] {
    background: var(--paper) !important;
    background-image: none !important;
}

/* ── 문제 카드 컴팩트 (3열 대응) ─────────────── */
/* 사용자 요청: 한글 10pt, 숫자/수식 11pt */
[data-testid="stVerticalBlockBorderWrapper"] {
    padding: 10px 12px !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 2px rgba(10, 16, 32, 0.04) !important;
}
[data-testid="stVerticalBlockBorderWrapper"] .stMarkdown,
[data-testid="stVerticalBlockBorderWrapper"] .stMarkdown p,
[data-testid="stVerticalBlockBorderWrapper"] .stMarkdown li {
    font-size: 10pt !important;      /* 한글 */
    line-height: 1.5 !important;
}
/* 카드 안 KaTeX 수식만 11pt */
[data-testid="stVerticalBlockBorderWrapper"] .katex {
    font-size: 11pt !important;
}
[data-testid="stVerticalBlockBorderWrapper"] .stCaption,
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"] {
    font-size: 10pt !important;
}
[data-testid="stVerticalBlockBorderWrapper"] .stButton button {
    padding: 0.2rem 0.35rem !important;
    font-size: 12px !important;
    white-space: nowrap !important;
    min-width: 0 !important;
    height: 28px !important;
    line-height: 1 !important;
}

/* 카드 안 expander (정답 · 해설 보기) 크기 축소 */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stExpander"] {
    box-shadow: none !important;
    margin-top: 6px !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stExpander"] summary {
    padding: 5px 10px !important;
    font-size: 10.5pt !important;
    font-weight: 600 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stExpander"]
[data-testid="stExpanderDetails"] {
    padding: 6px 10px 8px 10px !important;
}

/* ── 사이드바 nav 아이콘 (얇은 line SVG · 로그인페이지 톤 통일) ── */
/* 파일명에서 이모지 제거 후 CSS ::before 로 SVG 삽입.
   순서: 매쏠로지(home) / 클리닉 / 학생카드 / 카톡승인큐 / 검수 / 관리자 */
[data-testid="stSidebarNav"] ul li a::before,
[data-testid="stSidebarNavItems"] li a::before {
    content: '';
    display: inline-block;
    width: 17px; height: 17px;
    margin-right: 10px;
    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
    vertical-align: -3px;
    opacity: 0.85;
}
/* 1) 매쏠로지 (home) */
[data-testid="stSidebarNav"] ul li:nth-child(1) a::before,
[data-testid="stSidebarNavItems"] li:nth-child(1) a::before {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230a1020' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'><path d='M3 12L12 3l9 9'/><path d='M5 10v11h5v-6h4v6h5V10'/></svg>");
}
/* 2) 클리닉 (heart-pulse) */
[data-testid="stSidebarNav"] ul li:nth-child(2) a::before,
[data-testid="stSidebarNavItems"] li:nth-child(2) a::before {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230a1020' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'><path d='M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z'/><path d='M3.5 12h4l2-4 4 8 2-4h4'/></svg>");
}
/* 3) 학생카드 (id-card) */
[data-testid="stSidebarNav"] ul li:nth-child(3) a::before,
[data-testid="stSidebarNavItems"] li:nth-child(3) a::before {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230a1020' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'><rect x='2' y='4' width='20' height='16' rx='2'/><circle cx='9' cy='11' r='2.5'/><path d='M14 10h5M14 14h5M4.5 17c.7-2 2.7-3 4.5-3s3.8 1 4.5 3'/></svg>");
}
/* 4) 카톡승인큐 (envelope) */
[data-testid="stSidebarNav"] ul li:nth-child(4) a::before,
[data-testid="stSidebarNavItems"] li:nth-child(4) a::before {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230a1020' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'><rect x='2' y='4' width='20' height='16' rx='2'/><path d='M22 7l-10 7L2 7'/></svg>");
}
/* 5) 검수 (magnifier) */
[data-testid="stSidebarNav"] ul li:nth-child(5) a::before,
[data-testid="stSidebarNavItems"] li:nth-child(5) a::before {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230a1020' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='7'/><path d='M21 21l-4.3-4.3'/></svg>");
}
/* 6) 관리자 (settings gear) */
[data-testid="stSidebarNav"] ul li:nth-child(6) a::before,
[data-testid="stSidebarNavItems"] li:nth-child(6) a::before {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230a1020' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='3'/><path d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z'/></svg>");
}
</style>
"""


def apply_theme() -> None:
    """페이지 상단에서 호출. Streamlit 컴포넌트 전역 스타일링 적용."""
    st.markdown(_THEME_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str | None = None,
                kicker: str | None = None) -> None:
    """페이지 상단 헤더 — 파스텔 pill kicker + h1 + subtitle (프로토타입 톤).

    ```
    ● QUESTION BANK    ← kicker pill (파스텔 blue 배경, 파란 텍스트)
    큰 헤딩...          ← h1 (800, -0.03em)
    설명 문장...        ← subtitle (muted, 1.7 line-height)
    ```
    """
    parts = []
    if kicker:
        parts.append(
            f'<div style="display:inline-flex;align-items:center;gap:6px;'
            f'background:rgba(43,111,255,0.10);color:var(--accent,#2b6fff);'
            f'font-weight:700;font-size:11.5px;letter-spacing:0.14em;'
            f'padding:5px 12px;border-radius:999px;margin-bottom:14px;'
            f'text-transform:uppercase">'
            f'<span style="width:5px;height:5px;border-radius:50%;'
            f'background:var(--accent,#2b6fff)"></span>{kicker}</div>'
        )
    parts.append(
        f'<h1 style="font-size:30px;font-weight:800;'
        f'letter-spacing:-0.03em;color:var(--ink);'
        f'margin:0 0 10px 0;line-height:1.2">{title}</h1>'
    )
    if subtitle:
        parts.append(
            f'<p style="color:var(--muted);font-size:14.5px;'
            f'line-height:1.7;margin:0 0 24px 0;max-width:720px">'
            f'{subtitle}</p>'
        )
    st.markdown("".join(parts), unsafe_allow_html=True)


def numbered_section(n: int, title: str, subtitle: str | None = None) -> None:
    """번호 원 배지 + 섹션 제목 + subtitle (프로토타입 톤).

    ```
    [1] 수집 — 강사 화면
        채점 끝나고 반당 5분. 개인별 입력 없음.
    ```
    """
    sub_html = (
        f'<div style="color:var(--muted,#5f6c87);font-size:13px;'
        f'margin-top:2px;line-height:1.55">{subtitle}</div>'
        if subtitle else ''
    )
    st.markdown(
        f'<div style="display:flex;align-items:flex-start;gap:12px;'
        f'margin:36px 0 16px 0">'
        f'<div style="flex-shrink:0;width:26px;height:26px;'
        f'border-radius:50%;background:rgba(43,111,255,0.10);'
        f'color:var(--accent,#2b6fff);font-weight:800;font-size:13px;'
        f'display:flex;align-items:center;justify-content:center;'
        f'letter-spacing:-0.02em">{n}</div>'
        f'<div><div style="font-weight:800;font-size:17px;'
        f'letter-spacing:-0.02em;color:var(--ink,#0a1020);'
        f'line-height:1.3">{title}</div>{sub_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def kicker_pill(text: str, color: str = "#2b6fff") -> str:
    """작은 라이트 pill (필터 태그 등). HTML 문자열 반환.

    ```
    반 월금반 · 교재 자체교재 · 범위 p.22~27
    ```
    """
    return (
        f'<span style="display:inline-block;background:rgba(43,111,255,0.08);'
        f'color:{color};font-weight:600;font-size:12px;'
        f'padding:3px 10px;border-radius:999px;margin-right:6px;'
        f'letter-spacing:-0.01em">{text}</span>'
    )
