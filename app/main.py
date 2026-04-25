#!/usr/bin/env python3
"""MathDB 시험지 생성기 — Streamlit 웹앱

실행:
    streamlit run app/main.py
"""

import io
import json
import re
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

import streamlit as st

from db import get_connection as _get_db_connection, is_cloud

PAGE_TITLE = "MathArchive by 이영우"
DIFF_ORDER = {"하": 0, "중": 1, "상": 2, "킬": 3}
EXAM_TYPE_KO = {"a": "중간", "b": "기말"}


# ── 메타 포맷팅 ─────────────────────────────────────────────
def format_meta(row, *, short=False) -> str:
    """문제 row에서 출처 메타데이터를 사람이 읽을 수 있는 문자열로.

    short=False: `[가림고] 2025년 1학기 중간 · 26번`
    short=True : `[가림고] 26번` (스페이스 절약용)
    """
    school = row["school"] or "?"
    qn = row["question_number"]
    if short:
        return f"[{school}] {qn}번"
    try:
        year = row["year"]
        sem = row["semester"]
        exam = EXAM_TYPE_KO.get(row["exam_type"], row["exam_type"] or "")
    except (KeyError, IndexError):
        year = sem = exam = None
    parts = [f"[{school}]"]
    if year and sem:
        parts.append(f"{year}년 {sem}학기")
    if exam:
        parts.append(exam)
    parts.append(f"{qn}번")
    return " ".join(parts)


# ── DB 연결 ───────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return _get_db_connection()


def query(sql, params=()):
    return get_connection().execute(sql, params).fetchall()


# ── 필터 옵션 로드 ───────────────────────────────────────────
@st.cache_data(ttl=600)
def load_filter_options():
    schools = [r[0] for r in query("SELECT DISTINCT school FROM questions ORDER BY school")]
    chapters = [r[0] for r in query("SELECT DISTINCT chapter FROM questions ORDER BY chapter")]
    difficulties = [r[0] for r in query(
        "SELECT DISTINCT difficulty FROM questions ORDER BY difficulty"
    )]
    # 난이도 순서 정렬
    difficulties.sort(key=lambda x: DIFF_ORDER.get(x, 99))
    regions = [r[0] for r in query("SELECT DISTINCT region FROM questions ORDER BY region")]
    return schools, chapters, difficulties, regions


# ── 문제 검색 ────────────────────────────────────────────────
def search_questions(schools, chapters, difficulties, regions,
                     is_subjective=None, keyword=""):
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

    sql = f"""
        SELECT q.question_id, q.file_source, q.school, q.region,
               q.year, q.semester, q.exam_type,
               q.question_number, q.question_text, q.choices,
               q.answer, q.answer_type, q.points, q.chapter,
               q.difficulty, q.has_image, q.is_subjective, q.error_note,
               s.solution_text
        FROM questions q
        LEFT JOIN solutions s ON q.question_id = s.question_id
        WHERE {where}
        ORDER BY q.school, q.question_number
    """
    return query(sql, params)


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


# ── LaTeX 렌더링 헬퍼 ────────────────────────────────────────
def _frac_to_dfrac(text: str) -> str:
    r"""$...$안의 \frac → \dfrac 변환 (display-style로 분수 크기 키움)."""
    def _replace_in_math(m):
        inner = m.group(1)
        inner = inner.replace(r"\frac", r"\dfrac")
        return "$" + inner + "$"
    return re.sub(r"\$([^$]+)\$", _replace_in_math, text)


def _ensure_line_breaks(text: str) -> str:
    """단일 \\n을 markdown 줄바꿈(\\n\\n)으로 변환하여 원본 줄넘김 보존."""
    # 이미 \n\n인 것은 건드리지 않음
    text = re.sub(r"\n{3,}", "\n\n", text)
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
    img_map = _image_map_for_question(question_id) if question_id else {}

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
    if src:
        display_src = _safe_image_url(src) if src.startswith("http") else src
        st.image(display_src, width=400)
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
        sel_chapters = st.multiselect("단원", chapters)
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
            st.rerun()

    # ── 문제 검색 결과 ────────────────────────────────────────
    results = search_questions(
        sel_schools, sel_chapters, sel_difficulties, sel_regions,
        is_subjective, keyword
    )

    # 탭 구성
    tab_list, tab_preview = st.tabs(["📝 문제 목록", "📄 시험지 미리보기"])

    # ── 탭 1: 문제 목록 ──────────────────────────────────────
    with tab_list:
        total = len(results)
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
        page_results = results[start:end]

        st.caption(
            f"검색 결과: {total}문항 · {start + 1 if total else 0}–{end}번 표시"
        )

        if not results:
            st.info("필터 조건에 맞는 문제가 없습니다. 사이드바에서 조건을 조정해주세요.")
        else:
            # 페이지 네비게이션 (상단)
            if total > PAGE_SIZE:
                nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
                with nav_col1:
                    if st.button("◀ 이전", disabled=st.session_state.page_num == 0,
                                 key="prev_top", use_container_width=True):
                        st.session_state.page_num -= 1
                        st.rerun()
                with nav_col2:
                    st.markdown(
                        f"<div style='text-align:center;padding-top:6px;'>"
                        f"페이지 {st.session_state.page_num + 1} / {max_page + 1}"
                        f"</div>", unsafe_allow_html=True)
                with nav_col3:
                    if st.button("다음 ▶", disabled=st.session_state.page_num >= max_page,
                                 key="next_top", use_container_width=True):
                        st.session_state.page_num += 1
                        st.rerun()

            for row in page_results:
                qid = row["question_id"]
                is_selected = qid in st.session_state.selected_ids

                with st.container(border=True):
                    col1, col2 = st.columns([0.85, 0.15])

                    with col1:
                        # 헤더 정보
                        diff_emoji = {"하": "🟢", "중": "🟡", "상": "🔴", "킬": "💀"}.get(
                            row["difficulty"], "⚪"
                        )
                        points_str = f"{row['points']}점" if row["points"] else ""
                        subj_badge = " `서술형`" if row["is_subjective"] else ""
                        err_badge = " ⚠️오류" if row["error_note"] else ""

                        st.markdown(
                            f"**{format_meta(row)}** · "
                            f"{diff_emoji} {row['difficulty']} · "
                            f"`{row['chapter']}` · {points_str}"
                            f"{subj_badge}{err_badge}"
                        )

                        # 문제 텍스트 (목록에서는 이미지/박스 포함 풀 렌더링)
                        qtext = row["question_text"]
                        has_rich = "<<IMG:" in qtext or "<<BOX_START>>" in qtext
                        if has_rich or len(qtext) > 400:
                            with st.expander("문제 보기", expanded=not has_rich):
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
                        circle = {"1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤"}
                        ans = row["answer"]
                        display_ans = circle.get(ans, ans)
                        with st.expander(f"정답: {display_ans} · 해설 보기"):
                            if row["solution_text"]:
                                render_question_content(
                                    row["solution_text"],
                                    row["file_source"], qid)
                            else:
                                st.caption("해설 없음")

                    with col2:
                        if is_selected:
                            if st.button("❌ 제거", key=f"rm_{qid}",
                                         use_container_width=True):
                                st.session_state.selected_ids.discard(qid)
                                st.rerun()
                        else:
                            if st.button("➕ 추가", key=f"add_{qid}",
                                         use_container_width=True):
                                st.session_state.selected_ids.add(qid)
                                st.rerun()

                        if is_selected:
                            st.caption("✅ 선택됨")

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
                st.rerun()

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


if __name__ == "__main__":
    main()
