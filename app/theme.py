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

/* 전역 폰트 */
html, body, [class*="css"], .stApp,
.stMarkdown, .stMarkdown p, .stMarkdown li,
[data-testid="stAppViewContainer"] * {
    font-family: 'Pretendard Variable', 'Pretendard',
        -apple-system, 'Apple SD Gothic Neo', sans-serif !important;
}

.stApp {
    background: var(--paper) !important;
    color: var(--text) !important;
}

/* ── 헤딩 위계 ────────────────────────────── */
[data-testid="stMain"] h1 {
    font-size: 30px !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: var(--ink) !important;
    line-height: 1.25 !important;
    margin-top: 0.5rem !important;
    margin-bottom: 1.2rem !important;
}
[data-testid="stMain"] h2 {
    font-size: 22px !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
    color: var(--ink) !important;
    margin-top: 2.2rem !important;
    margin-bottom: 0.9rem !important;
}
[data-testid="stMain"] h3 {
    font-size: 16px !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
    color: var(--ink) !important;
    margin-top: 1.4rem !important;
    margin-bottom: 0.6rem !important;
}
[data-testid="stMain"] .stCaption,
[data-testid="stMain"] [data-testid="stCaptionContainer"] {
    color: var(--muted) !important;
    font-size: 13.5px !important;
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

/* ── 버튼 ─────────────────────────────────── */
.stButton button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    border: 1px solid var(--line) !important;
    background: #ffffff !important;
    color: var(--ink) !important;
    padding: 0.55rem 1rem !important;
    transition: background 0.15s, border-color 0.15s !important;
}
.stButton button:hover {
    background: #eef3ff !important;
    border-color: var(--blue-soft) !important;
    color: var(--ink) !important;
}
.stButton button[kind="primary"] {
    background: var(--ink) !important;
    color: #ffffff !important;
    border: 1px solid var(--ink) !important;
}
.stButton button[kind="primary"]:hover {
    background: var(--blue) !important;
    border-color: var(--blue) !important;
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
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: var(--ink) !important;
    font-weight: 600 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
}

/* ── Divider ──────────────────────────────── */
hr {
    border-color: var(--line) !important;
    margin: 1.5rem 0 !important;
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
    background: var(--ink) !important;
    color: #ffffff !important;
    border-color: var(--ink) !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: var(--blue) !important;
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

/* ── 여백 (breathing room) ────────────────── */
[data-testid="stMain"] .block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 1200px !important;
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
</style>
"""


def apply_theme() -> None:
    """페이지 상단에서 호출. Streamlit 컴포넌트 전역 스타일링 적용."""
    st.markdown(_THEME_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str | None = None,
                kicker: str | None = None) -> None:
    """페이지 상단 헤더 — 이모지 없이 kicker + h1 + 부제 구조.

    landing 의 chapter 헤더와 동일한 톤:
    ```
    QUESTION BANK          ← kicker (blue, 작음)
    13만 기출, 한곳에 집대성  ← h1
    설명 문장...            ← subtitle (muted)
    ```
    """
    parts = []
    if kicker:
        parts.append(
            f'<div style="color:var(--blue);font-weight:700;'
            f'letter-spacing:0.04em;font-size:13px;'
            f'margin-bottom:6px;text-transform:uppercase">{kicker}</div>'
        )
    parts.append(
        f'<h1 style="font-size:30px;font-weight:800;'
        f'letter-spacing:-0.03em;color:var(--ink);'
        f'margin:0 0 10px 0;line-height:1.25">{title}</h1>'
    )
    if subtitle:
        parts.append(
            f'<p style="color:var(--muted);font-size:15px;'
            f'line-height:1.75;margin:0 0 24px 0;max-width:680px">'
            f'{subtitle}</p>'
        )
    st.markdown("".join(parts), unsafe_allow_html=True)
