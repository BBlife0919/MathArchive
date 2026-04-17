#!/usr/bin/env python3
"""MathDB 시험지 생성기 — Streamlit 웹앱

실행:
    streamlit run app/main.py
"""

import io
import json
import re
import sqlite3
from pathlib import Path

import streamlit as st

# ── 설정 ──────────────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parent.parent / "db" / "mathdb.sqlite"
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
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


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


def render_question_content(text: str, file_source: str = ""):
    """문제 텍스트를 Streamlit으로 렌더링한다.

    - <<IMG:imageN>> → st.image()로 실제 이미지 표시
    - <<BOX_START>>...<<BOX_END>> → 테두리 박스로 표시
    - 인라인 수식 $...$ 은 markdown이 자동 렌더링
    - \\frac → \\dfrac 변환 (display-style 분수)
    """
    # 빈 줄 정리
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 파일명 stem (이미지 매칭용)
    file_stem = Path(file_source).stem if file_source else ""

    # <<BOX_START>>...<<BOX_END>> → 테두리 박스, <<IMG:...>> → 이미지
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
                # BOX 내부는 파서가 이미 Markdown 테이블 또는 줄단위로 직렬화함.
                # 여기서 \n → \n\n 변환하면 MD 테이블이 깨지고, 들여쓰기가
                # 코드블록으로 오인되므로 각 행의 선행 공백만 제거한다.
                lines = [ln.lstrip() for ln in content.split("\n")]
                content = "\n".join(lines)
                with st.container(border=True):
                    # 셀 내 <br> 태그를 렌더링하기 위해 HTML 허용.
                    # 입력은 내부 DB(원본 HWPX 파생)라 XSS 위험 없음.
                    st.markdown(content, unsafe_allow_html=True)
            continue
        elif re.match(r"<<IMG:(image\d+)>>", part):
            ref = re.match(r"<<IMG:(image\d+)>>", part).group(1)
            _render_image(ref, file_stem)
            continue

        if in_box:
            box_content.append(part)
        else:
            stripped = part.strip()
            if stripped:
                stripped = _frac_to_dfrac(stripped)
                stripped = _ensure_line_breaks(stripped)
                st.markdown(stripped)


def _render_image(image_ref: str, file_stem: str):
    """이미지 참조를 실제 파일로 찾아서 표시한다."""
    if not file_stem:
        st.caption(f"[이미지: {image_ref}]")
        return

    # images/ 디렉토리에서 매칭되는 파일 찾기
    image_path = None
    if IMAGE_DIR.exists():
        for f in IMAGE_DIR.iterdir():
            if image_ref in f.name and file_stem in f.name:
                image_path = f
                break
        # file_stem 매칭 안 되면 image_ref만으로 시도
        if image_path is None:
            for f in IMAGE_DIR.iterdir():
                if f.stem == image_ref or image_ref in f.name:
                    image_path = f
                    break

    if image_path and image_path.exists():
        st.image(str(image_path), width=400)
    else:
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


def format_choices(choices_json: str) -> str:
    """선택지 JSON을 보기 좋게 포맷한다.
    첫 줄에 ①②③, 둘째 줄에 ④⑤가 위치하도록 선지 3개/2개로 끊어 배치."""
    try:
        choices = json.loads(choices_json)
    except (json.JSONDecodeError, TypeError):
        return ""
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
def generate_pdf(
    selected_questions: list,
    title: str = "시험지",
    include_source: bool = True,
) -> bytes:
    """선택된 문제들로 PDF를 생성한다.

    include_source: True면 문제 상단에 `[학교] YYYY년 N학기 중/기말` 출처 표시.
    """
    from fpdf import FPDF

    # 한글 폰트 후보 (macOS 로컬 + Streamlit Cloud Linux)
    font_candidates = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",        # Streamlit Cloud (fonts-nanum)
        "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",   # 대체
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",             # macOS
    ]
    font_path = next((p for p in font_candidates if Path(p).exists()), None)
    has_korean = font_path is not None

    class ExamPDF(FPDF):
        def header(self):
            if has_korean:
                self.set_font("Korean", size=14)
                safe_title = title
            else:
                self.set_font("Helvetica", "B", 14)
                # 한글 폰트 없을 때 latin-1로 인코딩 실패하는 문자 치환
                safe_title = title.encode("latin-1", errors="replace").decode("latin-1")
            self.cell(0, 10, safe_title, align="C", new_x="LMARGIN", new_y="NEXT")
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.cell(0, 10, f"{self.page_no()}/{{nb}}", align="C")

    pdf = ExamPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # 한글 폰트 등록 (한 번만)
    if has_korean:
        pdf.add_font("Korean", "", font_path, uni=True)
        pdf.set_font("Korean", size=10)
    else:
        pdf.set_font("Helvetica", size=10)

    pdf.add_page()

    for i, q in enumerate(selected_questions, 1):
        # 문제 번호 + 배점 + (선택) 출처
        points_str = f" [{q['points']}점]" if q['points'] else ""
        header = f"{i}. {points_str}"
        pdf.set_font("Korean" if has_korean else "Helvetica", size=10)
        pdf.cell(0, 7, header, new_x="LMARGIN", new_y="NEXT")
        if include_source:
            try:
                exam = EXAM_TYPE_KO.get(q.get("exam_type"), q.get("exam_type") or "")
                src_parts = [f"[{q.get('school', '?')}]"]
                if q.get("year") and q.get("semester"):
                    src_parts.append(f"{q['year']}년 {q['semester']}학기")
                if exam:
                    src_parts.append(exam)
                src_parts.append(f"{q.get('question_number', '')}번")
                src_line = " ".join(src_parts)
                pdf.set_font("Korean" if has_korean else "Helvetica", size=8)
                pdf.cell(0, 5, src_line, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Korean" if has_korean else "Helvetica", size=10)
            except Exception:
                pass

        # 문제 텍스트 (LaTeX 수식 기호는 텍스트로 표시)
        text = q["question_text"]
        # $...$ 수식 → 텍스트 표현 유지
        text = re.sub(r"<<IMG:image\d+>>", "[그림]", text)
        # 줄바꿈 정리
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        for line in text.split("\n"):
            line = line.strip()
            if not line:
                pdf.ln(3)
                continue
            try:
                pdf.multi_cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
            except Exception:
                # 인코딩 오류 시 대체 문자 사용
                safe = line.encode("latin-1", errors="replace").decode("latin-1")
                pdf.multi_cell(0, 6, safe, new_x="LMARGIN", new_y="NEXT")

        # 선택지
        choices_text = format_choices(q.get("choices", "[]"))
        if choices_text:
            pdf.multi_cell(0, 6, choices_text, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(5)

    # 정답표
    pdf.add_page()
    pdf.set_font("Korean" if has_korean else "Helvetica", size=12)
    pdf.cell(0, 10, "정답표", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Korean" if has_korean else "Helvetica", size=10)

    for i, q in enumerate(selected_questions, 1):
        answer = q["answer"]
        circle = {"1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤"}
        display = circle.get(answer, answer)
        pdf.cell(0, 7, f"{i}번: {display}", new_x="LMARGIN", new_y="NEXT")

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


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
                                    qtext, row["file_source"])
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
                                    row["file_source"])
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
            include_source = st.toggle(
                "출처 삽입 (학교·연도·학기 표시)", value=True,
                help="꺼두면 문제 번호만 표시됩니다."
            )

            col_info, col_download = st.columns([0.7, 0.3])
            with col_info:
                st.markdown(f"**{len(selected_rows)}문항** 선택됨")
                total_pts = sum(r["points"] or 0 for r in selected_rows)
                if total_pts:
                    st.caption(f"총 배점: {total_pts:.1f}점")

            with col_download:
                if mode == "exam":
                    pdf_data = generate_pdf(
                        [dict(r) for r in selected_rows],
                        title=exam_title,
                        include_source=include_source,
                    )
                    st.download_button(
                        "📥 PDF 다운로드",
                        data=pdf_data,
                        file_name="exam.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.caption("교재 PDF는 Phase 3에서 제공 예정")

            st.divider()

            # 미리보기
            show_answers = st.toggle("정답/해설 표시", value=False)

            for i, row in enumerate(selected_rows, 1):
                with st.container(border=True):
                    # 문제 헤더
                    pts = f" [{row['points']}점]" if row["points"] else ""
                    st.markdown(f"### {i}번{pts}")
                    meta_line = format_meta(row) if include_source else None
                    caption_parts = []
                    if meta_line:
                        caption_parts.append(meta_line)
                    caption_parts.append(f"`{row['chapter']}`")
                    caption_parts.append(f"난이도: {row['difficulty']}")
                    st.caption(" · ".join(caption_parts))

                    # 문제 본문 (이미지+박스+LaTeX 렌더링)
                    render_question_content(
                        row["question_text"], row.get("file_source", "")
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
                                    row.get("file_source", ""))

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
