#!/usr/bin/env python3
"""MathDB 시험지 생성기 — Streamlit 웹앱

실행:
    streamlit run app/main.py
"""
from __future__ import annotations

import io
import json
import random
import re
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

import streamlit as st

from db import get_connection as _get_db_connection, is_cloud
import curriculum as _curr

PAGE_TITLE = "MathArchive by 이영우"
DIFF_ORDER = {"하": 0, "중": 1, "상": 2, "킬": 3}
DIFF_VALID = ["하", "중", "상", "킬"]
EXAM_TYPE_KO = {"a": "중간", "b": "기말"}


# ── 메타 포맷팅 ─────────────────────────────────────────────
EXAM_TYPE_SHORT = {"a": "중", "b": "기"}


def format_meta(row, *, short=False) -> str:
    """문제 row에서 출처 메타데이터를 사람이 읽을 수 있는 문자열로.

    short=False: `[가림고] 2025년 1학기 중간 · 26번`
    short=True : `[가림고 25.1중] 26번` (2열 그리드용 컴팩트)
    """
    school = row["school"] or "?"
    qn = row["question_number"]
    try:
        year = row["year"]
        sem = row["semester"]
        exam = row["exam_type"] or ""
    except (KeyError, IndexError):
        year = sem = exam = None

    if short:
        # `[가락고 25.1중]` 형태 — 학교+시험 출처를 한 묶음으로
        head = school
        if year:
            head += f" {str(year)[-2:]}"  # 2025 → 25
        if sem and exam:
            head += f".{sem}{EXAM_TYPE_SHORT.get(exam, exam)}"
        return f"[{head}] {qn}번"

    exam_ko = EXAM_TYPE_KO.get(exam, exam or "")
    parts = [f"[{school}]"]
    if year and sem:
        parts.append(f"{year}년 {sem}학기")
    if exam_ko:
        parts.append(exam_ko)
    parts.append(f"{qn}번")
    return " ".join(parts)


# ── DB 연결 ───────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return _get_db_connection()


def query(sql, params=()):
    return get_connection().execute(sql, params).fetchall()


def execute_write(sql, params=()):
    """INSERT/UPDATE/DELETE 실행. SQLite/Postgres 양쪽 호환."""
    conn = get_connection()
    conn.execute(sql, params)
    # SQLite 는 명시 commit 필요, Postgres 는 autocommit 이라 무해
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass


# ── 신고 시스템 ──────────────────────────────────────────────
# 페이지 단위 prefetch 캐시 (현 rerun 안에서 N+1 차단)
_PAGE_FLAGGED_SET: set[int] = set()
_PAGE_FLAGGED_PRIMED: bool = False


def _prefetch_flagged(question_ids: list[int]) -> None:
    """페이지 문항 전체의 신고 상태를 1회 IN 쿼리로 일괄 조회."""
    global _PAGE_FLAGGED_PRIMED, _PAGE_FLAGGED_SET
    if not question_ids:
        _PAGE_FLAGGED_SET = set()
        _PAGE_FLAGGED_PRIMED = True
        return
    placeholders = ",".join("?" * len(question_ids))
    rows = query(
        f"SELECT question_id FROM flagged_problems "
        f"WHERE resolved=0 AND question_id IN ({placeholders})",
        list(question_ids),
    )
    _PAGE_FLAGGED_SET = {r["question_id"] for r in rows}
    _PAGE_FLAGGED_PRIMED = True


def is_flagged(qid: int) -> bool:
    """문항이 현재 미해결 신고 상태인지.

    페이지 prefetch 캐시가 prime 돼 있으면 거기서 조회 (N+1 차단).
    """
    if _PAGE_FLAGGED_PRIMED:
        return qid in _PAGE_FLAGGED_SET
    rows = query(
        "SELECT 1 FROM flagged_problems "
        "WHERE question_id=? AND resolved=0 LIMIT 1",
        (qid,),
    )
    return bool(rows)


def flag_problem(qid: int, reason: str = ""):
    execute_write(
        "INSERT INTO flagged_problems (question_id, reason, flagged_by) "
        "VALUES (?, ?, ?)",
        (qid, reason, "user"),
    )


def unflag_problem(qid: int):
    execute_write(
        "UPDATE flagged_problems SET resolved=1 "
        "WHERE question_id=? AND resolved=0",
        (qid,),
    )


# ── 필터 옵션 로드 ───────────────────────────────────────────
@st.cache_data(ttl=600)
def load_filter_options():
    schools = [r[0] for r in query("SELECT DISTINCT school FROM questions ORDER BY school")]
    chapters = [r[0] for r in query("SELECT DISTINCT chapter FROM questions ORDER BY chapter")]
    # 난이도는 정상 4종(하/중/상/킬)만 표시 — HWPX 작성자가 난이도 칸에
    # 단원명·메모 등 잘못 입력한 잡티(다항함수/문제오류/특/즁/히 등) 차단.
    difficulties = DIFF_VALID
    regions = [r[0] for r in query("SELECT DISTINCT region FROM questions ORDER BY region")]
    return schools, chapters, difficulties, regions


# ── 문제 검색 ────────────────────────────────────────────────
def _build_search_where(schools, chapters, difficulties, regions,
                        is_subjective=None, keyword=""):
    """필터 조건을 (where_clause, params) 튜플로 반환."""
    conditions = []
    params = []

    if schools:
        placeholders = ",".join("?" * len(schools))
        conditions.append(f"q.school IN ({placeholders})")
        params.extend(schools)
    if chapters:
        placeholders = ",".join("?" * len(chapters))
        conditions.append(f"q.chapter IN ({placeholders})")
        params.extend(chapters)
    if difficulties:
        placeholders = ",".join("?" * len(difficulties))
        conditions.append(f"q.difficulty IN ({placeholders})")
        params.extend(difficulties)
    if regions:
        placeholders = ",".join("?" * len(regions))
        conditions.append(f"q.region IN ({placeholders})")
        params.extend(regions)
    if is_subjective is not None:
        conditions.append("q.is_subjective = ?")
        params.append(1 if is_subjective else 0)
    if keyword:
        conditions.append("q.question_text LIKE ?")
        params.append(f"%{keyword}%")

    where = " AND ".join(conditions) if conditions else "1=1"
    return where, params


@st.cache_data(ttl=300)
def search_question_ids(schools, chapters, difficulties, regions,
                        is_subjective=None, keyword=""):
    """필터 매칭 문항의 ID + 미니테스트용 최소 메타만 반환 (가벼움).

    페이지네이션·총 카운트·미니테스트 풀 추출에 사용.
    캐시 키는 인자 전체이므로 list 는 호출 측에서 tuple 변환 후 전달.
    """
    where, params = _build_search_where(
        list(schools), list(chapters), list(difficulties), list(regions),
        is_subjective, keyword,
    )
    sql = f"""
        SELECT q.question_id, q.difficulty
        FROM questions q
        WHERE {where}
        ORDER BY q.school, q.year DESC, q.semester, q.exam_type,
                 q.question_number
    """
    return [dict(r) for r in query(sql, params)]


def fetch_questions_page(question_ids):
    """주어진 ID 목록의 전체 데이터(해설 포함) 반환.

    페이지 표시용 — 30개 정도만 전달되므로 안전.
    원본 ID 순서를 보존해서 반환.
    """
    if not question_ids:
        return []
    placeholders = ",".join("?" * len(question_ids))
    sql = f"""
        SELECT q.question_id, q.file_source, q.school, q.region,
               q.year, q.semester, q.exam_type,
               q.question_number, q.question_text, q.choices,
               q.answer, q.answer_type, q.points, q.chapter,
               q.difficulty, q.has_image, q.is_subjective, q.error_note,
               s.solution_text
        FROM questions q
        LEFT JOIN solutions s ON q.question_id = s.question_id
        WHERE q.question_id IN ({placeholders})
    """
    rows = query(sql, list(question_ids))
    by_id = {r["question_id"]: r for r in rows}
    return [by_id[qid] for qid in question_ids if qid in by_id]


# ── 이미지 경로 ──────────────────────────────────────────────
IMAGE_DIR = Path(__file__).resolve().parent.parent / "images"


@st.cache_data(ttl=600)
def _image_map_for_question(question_id: int) -> dict:
    """question_id → {image_ref: image_path/URL} 사전.

    Postgres(R2) 환경에서는 모든 image_path 가 R2 URL,
    로컬 환경에서는 파일경로(또는 R2 URL) 혼재 가능.
    """
    if question_id is None:
        return {}
    rows = query(
        "SELECT image_ref, image_path FROM images WHERE question_id = ?",
        (question_id,),
    )
    return {r["image_ref"]: r["image_path"] for r in rows if r["image_ref"]}


def _prefetch_image_maps(question_ids: list[int]) -> None:
    """페이지에 표시할 문항 ID 들의 이미지 맵을 1회 IN 쿼리로 일괄 fetch한 뒤
    개별 `_image_map_for_question` 캐시에 prime한다.

    Why: 페이지당 30문항 × per-question 쿼리 = 30 round-trip 을
    1 round-trip 으로 줄임. Streamlit Cloud→Supabase 왕복 비용이 큼.
    """
    if not question_ids:
        return
    # 캐시 키가 인자(question_id)로 잡혀 있어 cache_data API 로는 직접
    # 다른 키에 값을 채워 넣을 수 없다 → 함수 시그니처를 우회: 미리 한 번에
    # 받아서 별도 함수로 캐시 prime.
    placeholders = ",".join("?" * len(question_ids))
    rows = query(
        f"SELECT question_id, image_ref, image_path FROM images "
        f"WHERE question_id IN ({placeholders})",
        list(question_ids),
    )
    grouped: dict[int, dict] = {qid: {} for qid in question_ids}
    for r in rows:
        if r["image_ref"]:
            grouped[r["question_id"]][r["image_ref"]] = r["image_path"]
    # 캐시 prime: cache_data 데코레이터는 동일 인자로 호출 시 캐시 히트하므로,
    # 여기서 _image_map_for_question.clear() 한 뒤 각 ID에 대해 결과를 미리
    # 채워 넣어도 어차피 prime API 가 없음. 그래서 모듈 전역 dict 로 따로 캐시.
    for qid, m in grouped.items():
        _PAGE_IMG_CACHE[qid] = m


# 페이지 단위로 배치 prefetch 된 이미지 맵을 담는 모듈 전역 캐시.
# Streamlit cache_data 와 별개로 동일 rerun 안에서 N+1 을 막는 용도.
_PAGE_IMG_CACHE: dict[int, dict] = {}


def _get_image_map(question_id: int | None) -> dict:
    """페이지 prefetch 캐시 우선, 없으면 per-question 쿼리 fallback."""
    if question_id is None:
        return {}
    if question_id in _PAGE_IMG_CACHE:
        return _PAGE_IMG_CACHE[question_id]
    return _image_map_for_question(question_id)


# ── LaTeX 렌더링 헬퍼 ────────────────────────────────────────
def _frac_to_dfrac(text: str) -> str:
    r"""$...$안의 \frac → \dfrac 변환 (display-style로 분수 크기 키움)."""
    def _replace_in_math(m):
        inner = m.group(1)
        inner = inner.replace(r"\frac", r"\dfrac")
        return "$" + inner + "$"
    return re.sub(r"\$([^$]+)\$", _replace_in_math, text)


_BOX_TITLE_PAT = re.compile(
    r"^<\s*(보\s*기|조\s*건|참\s*고|예\s*시|단\s*서)\s*>$"
)
_BOX_ITEM_PREFIX = re.compile(
    r"^\s*(?:[ㄱ-ㅎ]\.|\([가-힣]\)|\(?[①②③④⑤⑥⑦⑧⑨]\)?)"
)


def _flatten_grid_box(content: str) -> str:
    """`<보기>` / `<조건>` 박스가 markdown 격자 표로 들어왔을 때
    셀들을 flatten 해서 깔끔한 세로 나열로 변환.

    HWP 원본은 단순 테두리 사각형 + 내용 나열인데 표 구조로 파싱돼
    Streamlit 에서 격자 표로 렌더되면 못생김. 이를 원본 모양에 가깝게.
    """
    lines = content.split("\n")
    if not any("|---" in ln for ln in lines):
        return content  # 표 아님, 원본 그대로

    # 셀 추출
    cells = []
    for ln in lines:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        if re.search(r"\|\s*-+\s*\|", s):
            continue  # 구분자 행 스킵
        parts = [c.strip() for c in s.strip("|").split("|")]
        cells.extend(parts)
    cells = [c for c in cells if c.strip()]
    if not cells:
        return content

    # 헤더(`<보기>`) 와 항목 분리
    title = None
    items = []
    for c in cells:
        if _BOX_TITLE_PAT.match(c):
            title = c
        else:
            items.append(c)

    # 항목 prefix(`ㄱ.`, `(가)`, `①`) 가 있거나 헤더가 있으면 박스로 인정.
    has_prefix = any(_BOX_ITEM_PREFIX.match(it) for it in items)
    if title is None and not has_prefix:
        return content  # 일반 수치 표는 그대로

    out = []
    if title:
        out.append(f"<div style='text-align:center; font-weight:bold; "
                   f"margin-bottom:0.5em;'>{title}</div>")
    out.extend(items)
    return "\n\n".join(out)


def _ensure_line_breaks(text: str) -> str:
    """단일 \\n을 markdown 줄바꿈(\\n\\n)으로 변환하여 원본 줄넘김 보존.

    또한 줄별 leading tab/4-space 를 제거한다. HWP 원본에서 정렬용으로
    탭이 들어오는 경우가 많은데, 마크다운에서 줄이 탭/4-space 로 시작하면
    자동으로 code block 으로 렌더돼 수식이 raw LaTeX 으로 표시되는 사고 발생.
    """
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 줄별 leading tab/4-space 제거 (마크다운 code block 오인 차단)
    text = "\n".join(re.sub(r"^[\t ]+", "", ln) for ln in text.split("\n"))
    # 단일 \n → \n\n (markdown paragraph break)
    text = re.sub(r"(?<!\n)\n(?!\n)", "\n\n", text)
    return text


def render_question_content(text: str, file_source: str = "",
                            question_id: int | None = None):
    """문제 텍스트를 Streamlit으로 렌더링한다.

    - <<IMG:imageN>> → st.image()로 실제 이미지 표시 (DB image_path → R2 URL or 로컬)
    - <<BOX_START>>...<<BOX_END>> → 테두리 박스로 표시
    - 인라인 수식 $...$ 은 markdown이 자동 렌더링
    - \\frac → \\dfrac 변환 (display-style 분수)
    """
    text = re.sub(r"\n{3,}", "\n\n", text)

    file_stem = Path(file_source).stem if file_source else ""
    img_map = _get_image_map(question_id) if question_id else {}

    parts = re.split(r"(<<BOX_START>>|<<BOX_END>>|<<IMG:image\d+>>)", text)

    in_box = False
    box_content = []

    for part in parts:
        if part == "<<BOX_START>>":
            in_box = True
            box_content = []
            continue
        elif part == "<<BOX_END>>":
            in_box = False
            content = "".join(box_content).strip()
            if content:
                content = _frac_to_dfrac(content)
                lines = [ln.lstrip() for ln in content.split("\n")]
                content = "\n".join(lines)
                # `<보기>`/`<조건>` 격자 표 → 단순 세로 나열로 변환
                content = _flatten_grid_box(content)
                with st.container(border=True):
                    st.markdown(content, unsafe_allow_html=True)
            continue
        elif re.match(r"<<IMG:(image\d+)>>", part):
            ref = re.match(r"<<IMG:(image\d+)>>", part).group(1)
            _render_image(ref, file_stem, img_map)
            continue

        if in_box:
            box_content.append(part)
        else:
            stripped = part.strip()
            if stripped:
                stripped = _frac_to_dfrac(stripped)
                stripped = _ensure_line_breaks(stripped)
                st.markdown(stripped)


def _safe_image_url(url: str) -> str:
    """R2 URL의 한글·대괄호·공백을 퍼센트 인코딩한다.

    Why: image_path에 인코딩 안 된 특수문자가 들어있으면 Streamlit이
    URL로 인식하지 못하고 로컬 파일로 fallback해서 MediaFileStorageError가 난다.
    """
    parts = urlsplit(url)
    if not parts.scheme:
        return url
    return urlunsplit((
        parts.scheme,
        parts.netloc,
        quote(parts.path, safe="/%"),
        quote(parts.query, safe="=&%"),
        parts.fragment,
    ))


def _render_image(image_ref: str, file_stem: str, img_map: dict | None = None):
    """이미지 표시. DB의 image_path 우선(R2 URL), 없으면 로컬 폴더 폴백."""
    src = (img_map or {}).get(image_ref)
    if src and src.startswith("http"):
        # st.image()는 URL도 서버측 캐싱을 거치며 깨질 수 있어 HTML img로 직접 렌더.
        safe = _safe_image_url(src)
        st.markdown(
            f'<img src="{safe}" width="400" style="display:block;margin:8px 0;">',
            unsafe_allow_html=True,
        )
        return
    if src:
        # 비-URL src: 클라우드엔 로컬 파일이 없으므로 존재 확인 후에만 렌더.
        p = Path(src)
        if p.exists():
            st.image(str(p), width=400)
            return

    # 로컬 폴백 (개발 환경 / 마이그레이션 전 DB)
    if file_stem and IMAGE_DIR.exists():
        for f in IMAGE_DIR.iterdir():
            if image_ref in f.name and file_stem in f.name:
                st.image(str(f), width=400)
                return
        for f in IMAGE_DIR.iterdir():
            if f.stem == image_ref or image_ref in f.name:
                st.image(str(f), width=400)
                return

    st.caption(f"[이미지: {image_ref}]")


def render_question_text(text: str) -> str:
    """문제 텍스트를 Streamlit markdown용 문자열로 변환한다 (하위 호환).

    render_question_content()를 사용하는 것이 권장되지만,
    단순 문자열 변환이 필요한 곳에서 사용.
    """
    text = re.sub(r"<<IMG:image\d+>>", "🖼️", text)
    text = re.sub(r"<<BOX_START>>", "", text)
    text = re.sub(r"<<BOX_END>>", "", text)
    text = _frac_to_dfrac(text)
    text = _ensure_line_breaks(text)
    return text


def format_choices(choices_json) -> str:
    """선택지 JSON을 보기 좋게 포맷한다.
    첫 줄에 ①②③, 둘째 줄에 ④⑤가 위치하도록 선지 3개/2개로 끊어 배치.

    Postgres JSONB 는 이미 list/dict로 디코드되므로 문자열/객체 모두 허용."""
    if not choices_json:
        return ""
    if isinstance(choices_json, str):
        try:
            choices = json.loads(choices_json)
        except (json.JSONDecodeError, TypeError):
            return ""
    else:
        choices = choices_json
    if not choices:
        return ""
    circle = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤"}
    # 번호 순 보장
    choices = sorted(choices, key=lambda c: c.get("number", 0))
    parts = []
    for c in choices:
        num = c.get("number", 0)
        txt = c.get("text", "")
        txt = _frac_to_dfrac(txt)
        parts.append(f"{circle.get(num, str(num))} {txt}")
    # 첫 줄 3개 + 둘째 줄 나머지 (Markdown 단락 분리 \n\n)
    if len(parts) > 3:
        return "    ".join(parts[:3]) + "\n\n" + "    ".join(parts[3:])
    return "    ".join(parts)


# ── PDF 생성 ──────────────────────────────────────────────────
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
DEFAULT_LOGO_PATH = ASSETS_DIR / "eum_logo.png"


def generate_pdf(
    selected_questions: list,
    title: str = "시험지",
    include_source: bool = True,
    overrides: dict | None = None,
    subtitle: str | None = None,
    logo_path: str | None = None,
    include_difficulty: bool = False,
) -> bytes:
    """Playwright + KaTeX 기반 2단 PDF. 길이 짧은 문제는 단의 절반씩 2문제,
    긴 문제/상 난이도는 단 하나를 통째로 차지.

    overrides: {question_id: 'half'|'full'} 수동 지정.
    include_difficulty=True: 교재 모드. 출처에 난이도 prefix `[상]`.
    """
    from pdf_engine import generate_exam_pdf
    return generate_exam_pdf(
        selected_questions,
        title=title,
        include_source=include_source,
        overrides=overrides or {},
        subtitle=subtitle,
        logo_path=logo_path,
        include_difficulty=include_difficulty,
    )


# ── 메인 앱 ──────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="📐",
        layout="wide",
    )

    # Streamlit 기본 디버그 토스트 + 사이드바(자동 multi-page menu 포함) 즉시
    # 숨김. require_auth 통과 _전_ 사이드바가 노출되면 #169 같은 broken DOM
    # 발생. 인증 통과 후 require_auth 안에서 사이드바 다시 보임 처리.
    st.markdown(
        """
        <style>
        [data-testid="stStatusWidget"],
        [data-testid="stConnectionStatus"],
        [data-testid="stToast"],
        .stStatusWidget { display: none !important; }

        /* 인증 전 사이드바·자동 nav 숨김 (전체 영역) */
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid*="stSidebar"],
        section[data-testid="stSidebar"],
        aside[data-testid="stSidebar"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # OG / 트위터 카드 메타 (카톡·페이스북·트위터 공유 시 썸네일·제목 제어)
    # Streamlit 은 head 직접 수정을 지원하지 않아 body 에 주입.
    # KakaoTalk 등 일부 스크래퍼는 문서 전체에서 og 태그를 탐지.
    _OG_IMAGE = (
        "https://raw.githubusercontent.com/BBlife0919/MathArchive/"
        "main/app/assets/og_thumbnail.png?v=2"
    )
    st.markdown(
        f"""
        <meta property="og:title" content="Math Archive · Directed by 이영우" />
        <meta property="og:description" content="120,000+ Questions · Infinite Possibilities" />
        <meta property="og:image" content="{_OG_IMAGE}" />
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="630" />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://matharchive.streamlit.app" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Math Archive · Directed by 이영우" />
        <meta name="twitter:description" content="120,000+ Questions · Infinite Possibilities" />
        <meta name="twitter:image" content="{_OG_IMAGE}" />
        """,
        unsafe_allow_html=True,
    )

    # 인증 게이트 — 로그인/승인 안 됐으면 여기서 멈추고 로그인 화면 렌더
    # (인증 통과 시 require_auth 가 글로벌 톤 CSS + entry loader 도 inject)
    from auth_ui import require_auth, render_user_menu_in_sidebar
    require_auth()

    st.title("📐 MathArchive by 이영우")

    # 세션 상태 초기화
    if "selected_ids" not in st.session_state:
        st.session_state.selected_ids = set()

    schools, chapters, difficulties, regions = load_filter_options()

    # ── 사이드바: 필터 ────────────────────────────────────────
    with st.sidebar:
        st.header("🔍 문제 필터")

        sel_regions = st.multiselect("지역", regions)
        sel_schools = st.multiselect("학교", schools)

        # ── 계층형 단원 필터: 과목 → 대단원 → 중단원 ─────────
        st.markdown("**단원**")
        sel_subjects = st.multiselect(
            "과목", _curr.subjects(),
            key="sel_subjects",
            help="예: 공수1, 공수2, 대수, 미적1, 확통, 기하 등",
        )
        majors_pool = _curr.major_chapters(sel_subjects) \
            if sel_subjects else []
        sel_majors = st.multiselect(
            "대단원",
            majors_pool,
            key="sel_majors",
            disabled=not sel_subjects,
            help="과목을 먼저 선택하면 활성화",
        ) if majors_pool else []
        minors_pool = _curr.minor_chapters(sel_subjects, sel_majors) \
            if sel_majors else (
                _curr.all_minor_chapters_in_subjects(sel_subjects)
                if sel_subjects else []
            )
        sel_minors = st.multiselect(
            "중단원",
            minors_pool,
            key="sel_minors",
            disabled=not minors_pool,
            help="비워두면 위 단계의 모든 중단원 검색",
        ) if minors_pool else []

        # 최종 SQL 필터에 들어갈 중단원 리스트
        sel_chapters = _curr.expand_to_minors(
            sel_subjects, sel_majors, sel_minors
        )

        sel_difficulties = st.multiselect("난이도", difficulties)

        question_type = st.radio(
            "문제 유형", ["전체", "선택형", "서답형"],
            horizontal=True
        )
        is_subjective = None
        if question_type == "선택형":
            is_subjective = False
        elif question_type == "서답형":
            is_subjective = True

        keyword = st.text_input("키워드 검색", placeholder="문제 텍스트 검색...")

        st.divider()
        st.subheader(f"📋 시험지 ({len(st.session_state.selected_ids)}문항)")

        if st.button("🗑️ 시험지 초기화", use_container_width=True):
            st.session_state.selected_ids = set()
            st.session_state.mini_test_active = False
            st.rerun()

    render_user_menu_in_sidebar()

    # ── 문제 검색 결과 ────────────────────────────────────────
    # 1단계: 가벼운 ID+난이도만 (전체 매칭) — 카운트·미니테스트 풀용
    all_meta = search_question_ids(
        tuple(sel_schools), tuple(sel_chapters),
        tuple(sel_difficulties), tuple(sel_regions),
        is_subjective, keyword
    )

    # 탭 구성
    tab_list, tab_preview = st.tabs(["📝 문제 목록", "📄 시험지 미리보기"])

    # ── 탭 1: 문제 목록 ──────────────────────────────────────
    with tab_list:
        total = len(all_meta)

        # 미니테스트 프리셋 — 워밍업/총복습용 15분 컷
        with st.expander("🎯 미니테스트 자동 생성 (15분 컷, 6~8문항)"):
            st.caption(
                "현재 필터(단원/난이도/학교 등) 안에서 난이도 비중에 맞춰 랜덤 추출합니다. "
                "워밍업 인출 퀴즈·총복습 미니 모의에 활용."
            )
            mp1, mp2 = st.columns(2)
            with mp1:
                mini_count = st.slider("문항 수", 6, 8, 7, key="mini_count")
            with mp2:
                mini_easy_pct = st.slider(
                    "쉬운 문제 비중 (%)", 0, 100, 40, step=10, key="mini_easy_pct",
                    help="‘하’ 난이도 비중. 나머지는 ‘중’ 위주로 뽑습니다.",
                )
            if st.button("🎲 미니테스트 자동 생성",
                         use_container_width=True, type="primary"):
                if not all_meta:
                    st.warning("필터 조건에 맞는 문제가 없습니다. 사이드바를 확인하세요.")
                else:
                    easy_n = round(mini_count * mini_easy_pct / 100)
                    rest_n = mini_count - easy_n
                    easy_pool = [r["question_id"] for r in all_meta if r["difficulty"] == "하"]
                    rest_pool = [r["question_id"] for r in all_meta if r["difficulty"] in ("중", "상")]
                    picks = []
                    if easy_pool:
                        picks.extend(random.sample(easy_pool, min(easy_n, len(easy_pool))))
                    if rest_pool:
                        need = mini_count - len(picks)
                        picks.extend(random.sample(rest_pool, min(need, len(rest_pool))))
                    # 모자라면 전체 풀에서 보충
                    if len(picks) < mini_count:
                        all_pool = [r["question_id"] for r in all_meta
                                    if r["question_id"] not in picks]
                        need = mini_count - len(picks)
                        if all_pool:
                            picks.extend(random.sample(all_pool, min(need, len(all_pool))))
                    if picks:
                        st.session_state.selected_ids = set(picks)
                        st.session_state.mini_test_active = True
                        st.success(
                            f"{len(picks)}문항 자동 선택됨 → '시험지 미리보기' 탭에서 PDF 생성"
                        )
                        st.rerun()
                    else:
                        st.warning("선택 가능한 문제가 부족합니다.")

        PAGE_SIZE = 30

        # 페이지네이션 상태
        if "page_num" not in st.session_state:
            st.session_state.page_num = 0
        # 결과가 줄어들면 현재 페이지가 범위 밖일 수 있음 → 리셋
        max_page = max(0, (total - 1) // PAGE_SIZE) if total else 0
        if st.session_state.page_num > max_page:
            st.session_state.page_num = 0

        start = st.session_state.page_num * PAGE_SIZE
        end = min(start + PAGE_SIZE, total)
        # 2단계: 현재 페이지에 해당하는 ID 들만 전체 데이터 fetch (해설 포함)
        page_ids = [r["question_id"] for r in all_meta[start:end]]
        page_results = fetch_questions_page(page_ids)
        # 이미지 맵·신고 상태를 1회 IN 쿼리로 일괄 prefetch (N+1 차단)
        _prefetch_image_maps(page_ids)
        _prefetch_flagged(page_ids)

        st.caption(
            f"검색 결과: {total}문항 · {start + 1 if total else 0}–{end}번 표시"
        )

        # ── 페이지 윈도우 & 네비게이션 헬퍼 ────────────────────
        def _page_window(current: int, last: int):
            """첫·마지막 페이지 + 현재±2 표시. 사이가 멀면 None('…') 삽입.
            예) last=4048, current=10 → [0, None, 8, 9, 10, 11, 12, None, 4048]"""
            if last <= 6:
                return list(range(last + 1))
            pages = {0, last}
            for p in range(max(0, current - 2), min(last, current + 2) + 1):
                pages.add(p)
            sorted_pages = sorted(pages)
            result = []
            for i, p in enumerate(sorted_pages):
                if i > 0 and p - sorted_pages[i - 1] > 1:
                    result.append(None)
                result.append(p)
            return result

        def _render_pagination(prefix: str):
            """페이지 네비게이션. prefix: 'top'/'bot' (버튼 key 충돌 방지용)."""
            if total <= PAGE_SIZE:
                return
            current = st.session_state.page_num
            pages = _page_window(current, max_page)
            col_specs = [1] + [1] * len(pages) + [1]
            cols = st.columns(col_specs)
            with cols[0]:
                if st.button("◀", disabled=current == 0,
                             key=f"prev_{prefix}",
                             use_container_width=True):
                    st.session_state.page_num -= 1
                    st.rerun()
            for i, p in enumerate(pages):
                with cols[i + 1]:
                    if p is None:
                        st.markdown(
                            "<div style='text-align:center;padding:8px 0;"
                            "color:#a6b2d4;'>…</div>",
                            unsafe_allow_html=True,
                        )
                    elif p == current:
                        st.markdown(
                            f"<div style='text-align:center;padding:6px 0;"
                            f"border:1px solid #f0cd87;border-radius:6px;"
                            f"color:#f0cd87;font-weight:700;'>{p + 1}</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        if st.button(str(p + 1),
                                     key=f"page_{prefix}_{p}",
                                     use_container_width=True):
                            st.session_state.page_num = p
                            st.rerun()
            with cols[-1]:
                if st.button("▶", disabled=current >= max_page,
                             key=f"next_{prefix}",
                             use_container_width=True):
                    st.session_state.page_num += 1
                    st.rerun()

        if not all_meta:
            st.info("필터 조건에 맞는 문제가 없습니다. 사이드바에서 조건을 조정해주세요.")
        else:
            # 상단 페이지 네비게이션
            _render_pagination("top")

            def _render_problem_card(row):
                """문제 카드 1개 렌더 — 2열 그리드용 헬퍼."""
                qid = row["question_id"]
                is_selected = qid in st.session_state.selected_ids

                with st.container(border=True):
                    # 헤더 정보 + 액션 버튼 (한 줄)
                    diff_emoji = {"하": "🟢", "중": "🟡",
                                  "상": "🔴", "킬": "💀"}.get(
                        row["difficulty"], "⚪"
                    )
                    points_str = f"{row['points']}점" if row["points"] else ""
                    subj_badge = " `서술형`" if row["is_subjective"] else ""
                    err_badge = " ⚠️오류" if row["error_note"] else ""

                    meta_line = (
                        f"**{format_meta(row, short=True)}** · "
                        f"{diff_emoji} · `{row['chapter']}` · "
                        f"{points_str}{subj_badge}{err_badge}"
                    )
                    head_cols = st.columns([3, 1, 1])
                    head_cols[0].markdown(meta_line)
                    # 신고 버튼
                    flagged = is_flagged(qid)
                    flag_icon = "🚩" if not flagged else "🚩✓"
                    if head_cols[1].button(
                        flag_icon, key=f"flag_{qid}",
                        use_container_width=True,
                        help="신고됨 토글" if flagged else "오류 신고",
                    ):
                        if flagged:
                            unflag_problem(qid)
                        else:
                            flag_problem(qid)
                        st.rerun()
                    # 추가/제거 버튼
                    if is_selected:
                        if head_cols[2].button(
                            "❌", key=f"rm_{qid}",
                            use_container_width=True, help="선택 제거",
                        ):
                            st.session_state.selected_ids.discard(qid)
                            st.session_state.mini_test_active = False
                            st.rerun()
                    else:
                        if head_cols[2].button(
                            "➕", key=f"add_{qid}",
                            use_container_width=True, help="시험지에 추가",
                            type="primary",
                        ):
                            st.session_state.selected_ids.add(qid)
                            st.session_state.mini_test_active = False
                            st.rerun()

                    # 문제 텍스트
                    qtext = row["question_text"]
                    has_rich = "<<IMG:" in qtext or "<<BOX_START>>" in qtext
                    if has_rich or len(qtext) > 400:
                        with st.expander("문제 보기",
                                         expanded=not has_rich):
                            render_question_content(
                                qtext, row["file_source"], qid)
                    else:
                        text = render_question_text(qtext)
                        st.markdown(text)

                    # 선택지
                    choices_str = format_choices(row["choices"])
                    if choices_str:
                        st.caption(choices_str)

                    # 정답/해설
                    circle = {"1": "①", "2": "②", "3": "③",
                              "4": "④", "5": "⑤"}
                    ans = row["answer"]
                    display_ans = circle.get(ans, ans)
                    with st.expander(f"정답: {display_ans} · 해설 보기"):
                        if row["solution_text"]:
                            render_question_content(
                                row["solution_text"],
                                row["file_source"], qid)
                        else:
                            st.caption("해설 없음")

                    if is_selected:
                        st.caption("✅ 선택됨")

            # 2열 그리드 — 한 줄에 문제 2개씩 (한 화면에 ~6문제)
            page_list = list(page_results)
            for i in range(0, len(page_list), 2):
                grid_cols = st.columns(2, gap="small")
                with grid_cols[0]:
                    _render_problem_card(page_list[i])
                if i + 1 < len(page_list):
                    with grid_cols[1]:
                        _render_problem_card(page_list[i + 1])

            # 하단 페이지 네비게이션 (스크롤 후에도 이동 가능)
            st.markdown("---")
            _render_pagination("bot")

    # ── 탭 2: 시험지 미리보기 ────────────────────────────────
    with tab_preview:
        selected_ids = st.session_state.selected_ids

        if not selected_ids:
            st.info("문제 목록에서 ➕ 버튼으로 문제를 추가해주세요.")
        else:
            # 선택된 문제 조회
            placeholders = ",".join("?" * len(selected_ids))
            selected_rows = query(f"""
                SELECT q.question_id, q.file_source, q.school, q.question_number,
                       q.year, q.semester, q.exam_type,
                       q.question_text, q.choices, q.answer, q.answer_type,
                       q.points, q.chapter, q.difficulty, q.is_subjective,
                       s.solution_text
                FROM questions q
                LEFT JOIN solutions s ON q.question_id = s.question_id
                WHERE q.question_id IN ({placeholders})
                ORDER BY q.difficulty, q.chapter
            """, list(selected_ids))

            # 생성 모드 선택 (시험지 or 교재) — 두 버튼이 각각 "제작 단계" 진입 트리거
            mode = st.session_state.get("build_mode")  # "exam" | "book" | None

            if mode is None:
                st.markdown(f"**{len(selected_rows)}문항** 선택됨")
                total_pts = sum(r["points"] or 0 for r in selected_rows)
                if total_pts:
                    st.caption(f"총 배점: {total_pts:.1f}점")
                st.divider()
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("📝 시험지 만들기", use_container_width=True,
                                 type="primary"):
                        st.session_state.build_mode = "exam"
                        st.rerun()
                with b2:
                    if st.button("📚 교재 생성", use_container_width=True,
                                 help="준비 중 — Phase 3에서 지원 예정"):
                        st.session_state.build_mode = "book"
                        st.rerun()
                st.stop()

            # 뒤로가기
            if st.button("⬅ 선택으로 돌아가기", key="back_to_select"):
                st.session_state.build_mode = None
                st.session_state.mini_test_active = False
                st.rerun()

            mini_active = st.session_state.get("mini_test_active", False)
            if mini_active and mode == "exam":
                default_title = "미니테스트 (15분)"
            else:
                default_title = "수학 시험지" if mode == "exam" else "수학 교재"
            exam_title = st.text_input("제목", value=default_title)

            head_c1, head_c2 = st.columns(2)
            with head_c1:
                show_subtitle = st.toggle("부제 표시", value=False,
                                          help="제목 아래에 작은 글씨로 표시됩니다.")
                subtitle_text = ""
                if show_subtitle:
                    subtitle_text = st.text_input(
                        "부제", value="", placeholder="예: 2026학년도 1학기 중간대비",
                        label_visibility="collapsed",
                    )
            with head_c2:
                show_logo = st.toggle("로고 표시", value=False,
                                      help="우측 상단에 로고 이미지 표시.")
                logo_override = None
                if show_logo:
                    uploaded_logo = st.file_uploader(
                        "로고 업로드 (기본: 이음학원 로고)", type=["png", "jpg", "jpeg"],
                        label_visibility="collapsed",
                    )
                    if uploaded_logo is not None:
                        tmp = Path("/tmp") / f"logo_upload_{uploaded_logo.name}"
                        tmp.write_bytes(uploaded_logo.getvalue())
                        logo_override = str(tmp)

            include_source = st.toggle(
                "출처 삽입 (학교·연도·학기 표시)", value=True,
                help="꺼두면 문제 번호만 표시됩니다."
            )

            # 교재 모드 전용: 제목 위 kicker (디자인 요소)
            kicker_mark = None
            kicker_text = None
            if mode == "book":
                show_kicker = st.toggle(
                    "상단 라벨 표시", value=True,
                    help="제목 위에 작은 포인트 텍스트 (예: '#01 MATH ARCHIVE')"
                )
                if show_kicker:
                    kc1, kc2 = st.columns([0.35, 0.65])
                    with kc1:
                        kicker_mark = st.text_input(
                            "포인트 (주황)", value="#01",
                            placeholder="예: #01, VOL.1, 2026",
                        )
                    with kc2:
                        kicker_text = st.text_input(
                            "브랜드", value="MATH ARCHIVE",
                            placeholder="예: MATH ARCHIVE, EUM ACADEMY",
                        )
                    kicker_mark = kicker_mark.strip() or None
                    kicker_text = kicker_text.strip() or None

            effective_subtitle = subtitle_text.strip() if show_subtitle else None
            effective_logo = (
                logo_override if show_logo and logo_override
                else (str(DEFAULT_LOGO_PATH) if show_logo and DEFAULT_LOGO_PATH.exists() else None)
            )

            col_info, col_download = st.columns([0.7, 0.3])
            with col_info:
                st.markdown(f"**{len(selected_rows)}문항** 선택됨")
                total_pts = sum(r["points"] or 0 for r in selected_rows)
                if total_pts:
                    st.caption(f"총 배점: {total_pts:.1f}점")

            # 레이아웃 override (수동 1단/2단 전환)
            if "layout_overrides" not in st.session_state:
                st.session_state.layout_overrides = {}
            overrides = st.session_state.layout_overrides

            with col_download:
                try:
                    if mode == "exam":
                        from pdf_engine import generate_exam_pdf
                        pdf_data = generate_exam_pdf(
                            [dict(r) for r in selected_rows],
                            title=exam_title,
                            include_source=include_source,
                            overrides=overrides,
                            subtitle=effective_subtitle,
                            logo_path=effective_logo,
                        )
                        fname = "exam.pdf"
                    else:  # book
                        from pdf_engine import generate_book_pdf
                        pdf_data = generate_book_pdf(
                            [dict(r) for r in selected_rows],
                            title=exam_title,
                            include_source=include_source,
                            overrides=overrides,
                            subtitle=effective_subtitle,
                            logo_path=effective_logo,
                            kicker_mark=kicker_mark,
                            kicker_text=kicker_text,
                        )
                        fname = "book.pdf"
                    st.download_button(
                        "📥 PDF 다운로드",
                        data=pdf_data,
                        file_name=fname,
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"PDF 생성 실패: {type(e).__name__}")
                    st.caption(str(e)[:200])

            st.divider()

            # 미리보기
            show_answers = st.toggle("정답/해설 표시", value=False)

            from pdf_engine import estimate_layout

            for i, row in enumerate(selected_rows, 1):
                qid = row["question_id"]
                # 자동 판정 + 수동 override
                auto_layout = estimate_layout(dict(row))
                current = overrides.get(qid, auto_layout)

                with st.container(border=True):
                    h_col1, h_col2 = st.columns([0.75, 0.25])
                    with h_col1:
                        pts = f" [{row['points']}점]" if row["points"] else ""
                        st.markdown(f"### {i}번{pts}")
                        meta_line = format_meta(row) if include_source else None
                        caption_parts = []
                        if meta_line:
                            caption_parts.append(meta_line)
                        caption_parts.append(f"`{row['chapter']}`")
                        caption_parts.append(f"난이도: {row['difficulty']}")
                        st.caption(" · ".join(caption_parts))
                    with h_col2:
                        layout_label = "📄 단 전체" if current == "full" else "📐 반 단"
                        help_txt = (
                            "이 문제가 단의 절반(2문제 공존) vs 단 하나 통째로(1문제 전용)"
                        )
                        new_layout = st.selectbox(
                            "배치",
                            options=["half", "full"],
                            format_func=lambda x: "반 단 (2문제/단)" if x == "half" else "단 전체 (1문제/단)",
                            index=0 if current == "half" else 1,
                            key=f"layout_{qid}",
                            help=help_txt,
                            label_visibility="collapsed",
                        )
                        if new_layout != auto_layout:
                            overrides[qid] = new_layout
                        elif qid in overrides:
                            del overrides[qid]
                        if new_layout != current:
                            st.rerun()

                    # 문제 본문 (이미지+박스+LaTeX 렌더링)
                    render_question_content(
                        row["question_text"], row.get("file_source", ""),
                        row["question_id"],
                    )

                    # 선택지
                    choices_str = format_choices(row["choices"])
                    if choices_str:
                        st.markdown(choices_str)

                    # 정답/해설
                    if show_answers:
                        circle = {"1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤"}
                        ans = row["answer"]
                        display_ans = circle.get(ans, ans)
                        st.success(f"**정답:** {display_ans}")

                        if row["solution_text"]:
                            with st.expander("해설 보기"):
                                render_question_content(
                                    row["solution_text"],
                                    row.get("file_source", ""),
                                    row["question_id"])

                    # 제거 버튼
                    if st.button(f"❌ {i}번 제거", key=f"prev_rm_{row['question_id']}"):
                        st.session_state.selected_ids.discard(row["question_id"])
                        st.rerun()

            # 정답표
            if show_answers:
                st.divider()
                st.markdown("### 정답표")
                circle = {"1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤"}
                answers = []
                for i, row in enumerate(selected_rows, 1):
                    ans = row["answer"]
                    answers.append(f"{i}번: {circle.get(ans, ans)}")
                st.code("  ".join(answers))

    # ── Entry loader dismiss sentinel ──────────────────────
    # main() 의 모든 위젯이 그려진 _직후_ 이 sentinel <div> 가 DOM 에 inject.
    # auth_ui 의 JS entry loader 가 MutationObserver 로 이 element 등장을
    # 감지하면 즉시 fade-out. → "문항 로드 끝 = 즉시 문항 페이지" 보장.
    st.markdown(
        '<div id="mathdb-ready" style="display:none"></div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
