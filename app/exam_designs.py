"""시험지 표지·내지 디자인 모듈.

사용자가 표지/내지 디자인을 선택할 수 있게 하고, ExamMeta 에 담긴 입력값으로
각 디자인의 HTML 을 생성한다. pdf_engine 에서 본문(2단 paginate)과 결합해
최종 PDF 로 굳힌다.

디자인 추가 절차:
1. `COVER_DESIGNS` / `INNER_DESIGNS` 에 신규 키 + render 함수 등록
2. `render_<name>(meta, body_html, n_pages)` 형태의 새 함수 정의
3. UI 의 selectbox 옵션은 자동으로 갱신됨 (main.py 에서 dict 키 사용)
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from html import escape as _html_escape
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


# ─────────────────────────────────────────────────────────
# 메타데이터
# ─────────────────────────────────────────────────────────
@dataclass
class ExamMeta:
    """사용자가 시험지 만들기 폼에 입력하는 모든 값."""
    school_year: int = 2026          # xx학년도
    semester: int = 1                # x학기
    session: int = 1                 # x차 지필평가 / x회고사
    grade: int = 1                   # x학년
    subject: str = "공통수학1"        # 과목명
    exam_date: date | None = None    # 시행일
    exam_hour: int = 17              # 시행 시각(시)
    period: int = 1                  # 내지의 x교시
    code_number: str = "02"          # 내지 메타박스 코드번호
    n_choice: int = 0                # 선택형 문항 수
    n_essay: int = 0                 # 논술형(서답형) 문항 수
    school_name_short: str = "이음"   # → "이음고등학교"
    school_org_name: str = "이음학원"  # 표지 하단 학원명
    school_motto: str = "생각을 잇고 성장을 이루다."
    instructor_name: str = "이영우"   # → "with 이영우T"
    logo_path: str | None = None
    inner_title: str = "수학영역"      # 모의고사 스타일 내지 제목

    # ─ 파생 ─
    @property
    def school_full_name(self) -> str:
        return f"{self.school_name_short}고등학교"

    @property
    def instructor_full_html(self) -> str:
        name = _html_escape(self.instructor_name)
        # with · 이름 · T 각각 다른 폰트/크기로 — 원본 NanumBrush 느낌 재현.
        return (
            f'<span class="with-text">with</span>'
            f'<span class="instructor-name">{name}</span>'
            f'<span class="t-mark">T</span>'
        )

    def date_korean_full(self) -> str:
        """`2026년 4월 12일(일요일) 17시` 형식 — 표지용."""
        if not self.exam_date:
            return ""
        wd = "월화수목금토일"[self.exam_date.weekday()]
        return (f"{self.exam_date.year}년 {self.exam_date.month}월 "
                f"{self.exam_date.day}일({wd}요일) {self.exam_hour}시")

    def date_short_with_period(self) -> str:
        """`2026년 4월 12일 (일) 1교시` 형식 — 내지용."""
        if not self.exam_date:
            return ""
        wd = "월화수목금토일"[self.exam_date.weekday()]
        return (f"{self.exam_date.year}년 {self.exam_date.month}월 "
                f"{self.exam_date.day}일 ({wd}) {self.period}교시")

    def exam_session_title(self) -> str:
        """`2026학년도 1학기 1회고사` — 내지 헤더."""
        return (f"{self.school_year}학년도 {self.semester}학기 "
                f"{self.session}회고사")

    def cover_main_title(self) -> str:
        """`2026학년도 1학기 1차 지필평가 문제지` — 표지 최상단."""
        return (f"{self.school_year}학년도 {self.semester}학기 "
                f"{self.session}차 지필평가 문제지")


# ─────────────────────────────────────────────────────────
# 공통 CSS — 디자인 공유 + 디자인별 prefix
# 폰트 매칭:
#   본문 명조 (Haansoft-Batang) → Nanum Myeongjo (가장 가까운 무료 웹폰트)
#   손글씨 (NanumBrush)         → Nanum Pen Script (한글+영문 손글씨)
# ─────────────────────────────────────────────────────────
COMMON_DESIGN_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&family=Nanum+Pen+Script&family=Gaegu:wght@400;700&display=swap');

.cover-page {
  page-break-after: always;
  page-break-inside: avoid;
}
.red, .red strong { color: #c0392b; }
.cover-instructor .instructor-name {
  /* 나눔손글씨 붓 대용. 굵은 손글씨 느낌은 Nanum Pen 보다 Gaegu 700 이 가까움 */
  font-family: 'Nanum Pen Script', 'Gaegu', cursive;
  font-weight: 700;
  font-size: 26pt;
  margin: 0 4px;
  letter-spacing: 1px;
}
.cover-instructor .with-text {
  font-family: 'Nanum Pen Script', cursive;
  font-size: 20pt;
  margin-right: 6px;
}
.cover-instructor .t-mark {
  font-family: 'Nanum Pen Script', cursive;
  font-size: 16pt;
  margin-left: 2px;
}
"""

# ─────────────────────────────────────────────────────────
# 표지 #1 — 이음고 스타일 (Image #176)
# ─────────────────────────────────────────────────────────
COVER_EUM_CSS = r"""
/* A4 = 297mm. margin top/bottom 각 10mm → 본문 영역 277mm.
   모든 요소를 한 페이지에 담기 위해 vertical margin 을 컴팩트하게 조정. */
.cover-page {
  width: 100%;
  height: 277mm;          /* 본문 영역 전체 사용 */
  padding: 8mm 14mm 8mm 14mm;
  text-align: center;
  font-family: 'Nanum Myeongjo', 'Noto Serif KR', serif;
  color: #111;
  display: flex; flex-direction: column;
  box-sizing: border-box;
}
.cover-page .cover-main-title {
  font-size: 17pt; font-weight: 700;
  text-decoration: underline;
  margin-bottom: 8mm;
}
.cover-page .cover-grade {
  font-size: 20pt; font-weight: 700; margin-bottom: 4mm;
}
.cover-page .cover-subject {
  font-size: 42pt; font-weight: 800; letter-spacing: 4px;
  margin-bottom: 10mm;
}
.cover-page .cover-datetime-box {
  width: 60%; margin: 0 auto 10mm auto;
  border: 1px solid #222; border-radius: 2px; overflow: hidden;
}
.cover-page .cover-datetime-header {
  background: #d8d8d8; padding: 3mm 0; font-size: 12pt; font-weight: 700;
  border-bottom: 1px solid #222;
}
.cover-page .cover-datetime-body {
  padding: 5mm 0; font-size: 14pt;
}
.cover-page .cover-instructions {
  width: 88%; margin: 0 auto 8mm auto;
  border: 1px solid #222; padding: 5mm 6mm 3mm 6mm;
  text-align: left; font-size: 10.5pt; line-height: 1.6;
}
.cover-page .cover-instructions ul {
  list-style: none; padding: 0; margin: 0 0 3mm 0;
}
.cover-page .cover-instructions li {
  text-indent: -6mm; padding-left: 6mm; margin-bottom: 0.5mm;
}
.cover-page .cover-instructions li::before {
  content: "○ "; font-weight: 700;
}
.cover-page .cover-counts {
  text-align: center; font-weight: 700; margin-top: 2mm;
}
.cover-page .cover-warning {
  width: 88%; margin: 0 auto 10mm auto;
  border: 1px solid #222; padding: 3mm 0;
  font-weight: 700; font-size: 11.5pt;
}
.cover-page .cover-school-name {
  font-size: 17pt; font-weight: 700; margin-bottom: 8mm;
}
.cover-page .cover-footer {
  display: flex; align-items: center; justify-content: center;
  gap: 16mm; margin-top: auto;
}
.cover-page .cover-logo {
  display: flex; flex-direction: column; align-items: center;
}
.cover-page .cover-logo img {
  height: 20mm; margin-bottom: 1mm;
  /* 흰 배경 제거 / 어두운 배경 호환 위해 background 투명 가정 */
}
.cover-page .cover-instructor {
  font-size: 14pt; display: flex; align-items: baseline;
  white-space: nowrap;
}
"""


def _logo_img_html(logo_path: str | None) -> str:
    """디자인 모듈 안에서 쓰는 간단 logo embed.

    pdf_engine._logo_data_uri 를 import 안 하기 위해 같은 동작 재구현 —
    순환 의존 방지.
    """
    if not logo_path:
        return ""
    p = Path(logo_path)
    if not p.exists():
        return ""
    import base64
    import mimetypes
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f'<img src="data:{mime};base64,{b64}" alt="logo">'


def render_cover_eum(meta: ExamMeta) -> str:
    """1번 표지 (Image #176) HTML 생성. 페이지 하나의 <section> 반환."""
    logo_html = _logo_img_html(meta.logo_path)
    return f"""
<section class="cover-page">
  <div class="cover-main-title">{_html_escape(meta.cover_main_title())}</div>
  <div class="cover-grade">{meta.grade}학년</div>
  <div class="cover-subject">{_html_escape(meta.subject)}</div>
  <div class="cover-datetime-box">
    <div class="cover-datetime-header">시행일시</div>
    <div class="cover-datetime-body">{_html_escape(meta.date_korean_full())}</div>
  </div>
  <div class="cover-instructions">
    <ul>
      <li>답안지에 필요한 기록사항(학년, 반, 번호, 성명, 과목명 등)을 정확히 기입하세요.</li>
      <li>문항에 따라 배점이 다르니, 각 물음의 끝에 표시된 배점을 참고하세요.</li>
      <li>선택형 문항을 읽고 알맞은 답을 골라 답안지(OMR카드)의 해당란에 컴퓨터용 수성펜으로 바르게 표시(●)하세요.</li>
      <li>논술형 문항의 정답은 반드시 검정색 볼펜으로 답안지에 작성하세요.</li>
    </ul>
    <div class="cover-counts">
      [선택형 문제는 ({meta.n_choice})문항, 논술형 문제는 ({meta.n_essay})문항입니다.]
    </div>
  </div>
  <div class="cover-warning">※시험이 시작될 때까지 표지를 넘기지 마십시오.</div>
  <div class="cover-school-name">{_html_escape(meta.school_full_name)}</div>
  <div class="cover-footer">
    <div class="cover-logo">
      {logo_html}
    </div>
    <div class="cover-instructor">{meta.instructor_full_html}</div>
  </div>
</section>
""".strip()


# ─────────────────────────────────────────────────────────
# 내지 #1 — 이음고 스타일 (Image #177)
#   첫 페이지 헤더에만 메타박스 + 안내문이 들어가고,
#   본문은 2단 paginate.
# ─────────────────────────────────────────────────────────
INNER_EUM_CSS = r"""
.inner-eum-header {
  display: grid;
  grid-template-columns: 1.2fr 1.2fr;
  gap: 2mm;
  border-bottom: 1.6pt solid #111;
  padding-bottom: 2mm;
  margin-bottom: 3mm;
}
.inner-eum-left { display: flex; flex-direction: column; gap: 2mm; }
.inner-eum-title {
  text-align: center; font-size: 16pt; font-weight: 700;
  border-bottom: 0.6pt solid #888;
  padding-bottom: 1.2mm;
}
.inner-eum-date {
  text-align: center; font-size: 11pt;
  padding-bottom: 1.4mm;
  border-bottom: 0.6pt solid #888;
}
.inner-eum-meta {
  width: 100%; border-collapse: collapse; font-size: 10.5pt;
}
.inner-eum-meta td {
  border: 0.6pt solid #555;
  padding: 1.2mm 2mm; text-align: center;
}
.inner-eum-meta td.red { color: #c0392b; font-weight: 700; }
.inner-eum-teachers {
  width: 100%; border-collapse: collapse; font-size: 10pt;
}
.inner-eum-teachers th, .inner-eum-teachers td {
  border: 0.6pt solid #555; text-align: center;
  padding: 1.6mm 1mm;
}
.inner-eum-teachers th { background: #f3f3f3; font-weight: 700; }
.inner-eum-teachers .stamp { color: #444; }
.inner-eum-instructions {
  border: 1pt solid #444;
  padding: 3mm 4mm; font-size: 10pt; line-height: 1.55;
  margin-bottom: 4mm;
}
.inner-eum-instructions ul { padding-left: 4mm; margin: 0; }
.inner-eum-instructions li { margin: 0.6mm 0; }
.inner-eum-instructions .red { color: #c0392b; }
"""


def render_inner_eum_first_page_header(meta: ExamMeta, n_total_pages: int) -> str:
    """내지 1번의 첫 페이지에만 들어가는 메타박스+안내문 헤더 HTML."""
    return f"""
<header class="inner-eum-header">
  <div class="inner-eum-left">
    <div class="inner-eum-title">{_html_escape(meta.exam_session_title())}</div>
    <div class="inner-eum-date">{_html_escape(meta.date_short_with_period())}</div>
    <table class="inner-eum-meta">
      <tr>
        <td rowspan="2" style="width:18%;">과목</td>
        <td style="width:22%;">교과명</td>
        <td class="red" style="width:18%;">수학</td>
        <td rowspan="2" style="width:18%;">대상학년</td>
        <td rowspan="2">제 {meta.grade}학년</td>
      </tr>
      <tr>
        <td>코드번호</td>
        <td class="red">{_html_escape(str(meta.code_number))}</td>
      </tr>
    </table>
  </div>
  <div class="inner-eum-right">
    <table class="inner-eum-teachers">
      <tr>
        <th style="width:30%;">공동출제 교사</th>
        <th>계</th><th>부장</th><th>교감</th><th>교장</th>
      </tr>
      <tr><td class="stamp">(인)</td><td></td><td></td><td></td><td></td></tr>
      <tr><td class="stamp">(인)</td><td></td><td></td><td></td><td></td></tr>
    </table>
  </div>
</header>
<div class="inner-eum-instructions">
  <ul>
    <li>답안지에 학년, 반, 번호를 정확하게 기입하시오.</li>
    <li>문제지는 총 <span class="red">{n_total_pages}쪽</span>,
        선택형 <span class="red">{meta.n_choice}문항</span>,
        서답형 <span class="red">{meta.n_essay}문항</span></li>
    <li>선택형 문항의 답은 OMR카드에 컴퓨터용 사인펜으로 정확히 마킹하시오.</li>
    <li class="red">서답형 답은 검은색 펜으로 서답형 답안지에 작성하시오.</li>
    <li>답안지에 불필요한 표시나 낙서는 절대로 하지 마시오.</li>
  </ul>
</div>
""".strip()


# ─────────────────────────────────────────────────────────
# 내지 #2 — 모의고사 스타일 (Image #178)
#   사용자 입력: inner_title (예: "수학영역")
#   페이지마다 좌우 반복 헤더 + 자동 페이지번호.
# ─────────────────────────────────────────────────────────
INNER_MOCK_CSS = r"""
.inner-mock-banner {
  text-align: center;
  margin-bottom: 4mm;
}
.inner-mock-banner .period-badge {
  display: inline-block;
  border: 1pt solid #111;
  padding: 1mm 4mm;
  font-size: 12pt; font-weight: 700;
  float: left;
}
.inner-mock-banner .big-title {
  font-size: 26pt; font-weight: 800;
  letter-spacing: 6px;
}
.inner-mock-running {
  font-size: 13pt; color: #aaa; letter-spacing: 6px;
  text-align: center; margin-bottom: 2mm;
}
"""


def render_inner_mock_first_page_header(meta: ExamMeta) -> str:
    """내지 2번의 첫 페이지 큰 제목 헤더. 사용자 입력은 inner_title 하나."""
    return f"""
<div class="inner-mock-banner">
  <span class="period-badge">제{meta.period}교시</span>
  <div class="big-title">{_html_escape(meta.inner_title)}</div>
</div>
""".strip()


# ─────────────────────────────────────────────────────────
# 디자인 레지스트리
# ─────────────────────────────────────────────────────────
COVER_DESIGNS: dict = {
    "이음고 표지 (Image #176)": {
        "render": render_cover_eum,
        "css": COVER_EUM_CSS,
    },
}

INNER_DESIGNS: dict = {
    "이음고 내지 (Image #177)": {
        "first_header": render_inner_eum_first_page_header,
        "css": INNER_EUM_CSS,
        "needs_page_count": True,
    },
    "모의고사 스타일 (Image #178)": {
        "first_header": lambda meta, n=0: render_inner_mock_first_page_header(meta),
        "css": INNER_MOCK_CSS,
        "needs_page_count": False,
    },
}


def all_design_css() -> str:
    """페이지 전체에 들어갈 디자인 CSS 모음 (모든 디자인 분 + 공통)."""
    return "\n".join([COMMON_DESIGN_CSS]
                     + [d["css"] for d in COVER_DESIGNS.values()]
                     + [d["css"] for d in INNER_DESIGNS.values()])


def list_logos() -> list[tuple[str, str]]:
    """assets 폴더의 로고 후보 (표시명, 절대경로) 반환."""
    if not ASSETS_DIR.exists():
        return []
    out: list[tuple[str, str]] = []
    for p in sorted(ASSETS_DIR.iterdir()):
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg"}:
            # 썸네일 같은 OG 이미지는 표지용으로 부적합 → 제외
            if p.name.startswith("og_"):
                continue
            out.append((p.name, str(p)))
    return out
