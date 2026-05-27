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

import base64
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from html import escape as _html_escape
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"


@lru_cache(maxsize=4)
def _font_data_uri(ttf_name: str) -> str:
    """app/assets/fonts/ 의 ttf 를 base64 data URI 로 인코딩.

    환경 무관(macOS/Linux) 동일 폰트 렌더링 보장 — 외부 CDN 의존 0.
    PDF 생성마다 HTML 에 inline 박힘. 캐시로 매번 인코딩 안 함.
    """
    p = FONTS_DIR / ttf_name
    if not p.exists():
        return ""
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:font/truetype;base64,{b64}"


def font_face_css() -> str:
    """모든 임베드 폰트의 @font-face 선언."""
    out: list[str] = []
    nanum_brush = _font_data_uri("NanumBrushScript-Regular.ttf")
    if nanum_brush:
        out.append(
            "@font-face { font-family: 'NanumBrush'; "
            f"src: url('{nanum_brush}') format('truetype'); "
            "font-display: block; }"
        )
    return "\n".join(out)


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
/* Google Fonts 는 _HTML_WRAP 의 <link> 태그에서 head 에 직접 로드됨.
   CSS @import 는 PDF Chromium 환경에서 가끔 늦게 로드돼 fallback 발생 사고. */

.cover-page {
  page-break-after: always;
  page-break-inside: avoid;
}
.red, .red strong { color: #c0392b; }

/* with [이영우] [T] — 'NanumBrush' 는 @font-face 로 ttf 를 base64
   inline 임베드 (font_face_css). 한글+영문 동일 붓글씨 폰트로 렌더. */
.cover-instructor {
  font-size: 14pt;
}
.cover-instructor .with-text,
.cover-instructor .instructor-name,
.cover-instructor .t-mark {
  font-family: 'NanumBrush', 'Nanum Brush Script', cursive;
  font-weight: 400;
  color: #111;
}
.cover-instructor .with-text {
  font-size: 28pt;
  margin-right: 10px;
}
.cover-instructor .instructor-name,
.cover-instructor .t-mark {
  font-size: 34pt;
  letter-spacing: 2px;
}
.cover-instructor .instructor-name { margin: 0 4px; }
.cover-instructor .t-mark { margin-left: 6px; }
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
  align-items: stretch;
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

/* 우측: 위쪽 빈공간을 띄우고 표를 아래 가장자리에 맞춤 → 좌측 메타박스와
   아래선 일치 (사용자 요구). */
.inner-eum-right {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}
.inner-eum-teachers {
  width: 100%; border-collapse: collapse; font-size: 10pt;
}
.inner-eum-teachers th, .inner-eum-teachers td {
  border: 0.6pt solid #555; text-align: center;
  padding: 1.6mm 1mm;
}
.inner-eum-teachers th { background: #f3f3f3; font-weight: 700; }
.inner-eum-teachers .stamp { color: #444; }

/* 안내문 박스 — 본문 좌측 컬럼 안 첫 위치에 prepend. col 너비 100%. */
.inner-eum-instructions {
  border: 1pt solid #444;
  padding: 3mm 4mm; font-size: 10pt; line-height: 1.55;
  margin: 0 0 4mm 0;
  width: 100%;
  box-sizing: border-box;
}
.inner-eum-instructions ul { padding-left: 4mm; margin: 0; }
.inner-eum-instructions li { margin: 0.6mm 0; }
.inner-eum-instructions .red { color: #c0392b; }
"""


def render_inner_eum_first_page_header(meta: ExamMeta, n_total_pages: int) -> str:
    """내지 1번의 첫 페이지에만 들어가는 메타박스 헤더 (전체 너비)."""
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
""".strip()


def render_inner_eum_first_col_extra(meta: ExamMeta, n_total_pages: int) -> str:
    """본문 첫 페이지 좌측 컬럼 맨 위에 prepend 되는 안내문 박스.

    이 위치에 들어가야 우측 컬럼이 위에서부터 자연스럽게 채워진다.
    """
    return f"""
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
# 내지 #2 — 수능형 모의고사 (Image #190~192 100% 모사)
#   페이지별로 다른 헤더:
#     1쪽: 좌-[제N교시], 중-부제+큰제목, 우-페이지번호+[홀수형]
#     짝수쪽: 좌-페이지번호, 중-큰제목, 우-[홀수형]
#     홀수쪽: 좌-[홀수형], 중-큰제목, 우-페이지번호
#   본문 2단 사이 세로선, 1쪽 좌측 컬럼 첫 위치에 [5지선다형] 라벨.
#   매 페이지 푸터: SVG 페이지번호 박스 + 저작권 문구.
# ─────────────────────────────────────────────────────────
INNER_MOCK_CSS = r"""
/* 본문도 명조체로 강제 (수능형 양식 폰트 매칭) */
.mock-body { font-family: 'Nanum Myeongjo', 'Noto Serif KR', serif; }
.mock-body .slot { font-family: inherit; }

.mock-header {
  display: grid;
  grid-template-columns: 25% 50% 25%;
  align-items: center;
  border-bottom: 1.4pt solid #111;
  padding-bottom: 3mm;
  margin-bottom: 4mm;
  font-family: 'Nanum Myeongjo', serif;
}
.mock-header.mock-header-p1 {
  align-items: end;
}
.mock-h-left { text-align: left; }
.mock-h-center { text-align: center; }
.mock-h-right { text-align: right; }

.mock-box {
  display: inline-block;
  border: 0.8pt solid #111;
  padding: 1.4mm 4mm;
  font-size: 12pt;
  font-weight: 700;
  background: #fff;
  white-space: nowrap;
}

.mock-pagenum {
  font-size: 28pt;
  font-weight: 700;
  line-height: 1;
  display: inline-block;
}

.mock-h-sub {
  font-size: 11pt;
  margin-bottom: 1mm;
}
.mock-h-big {
  font-size: 26pt;
  font-weight: 700;
  letter-spacing: 6px;
  line-height: 1.1;
}

/* 페이지 1: 우측은 페이지번호(상) + 홀수형 박스(하) 세로 배치 */
.mock-header-p1 .mock-h-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2mm;
}

/* 5지선다형 라벨 — 1쪽 좌측 컬럼 첫 위치 prepend */
.mock-section-label {
  display: inline-block;
  border: 1pt solid #111;
  padding: 1.2mm 4mm;
  font-size: 11pt;
  font-weight: 700;
  margin: 0 0 3mm 0;
}

/* 본문 2단 사이 세로 실선 */
.page-body.mock-body .col + .col {
  border-left: 0.5pt solid #555;
  padding-left: 5mm;
}
.page-body.mock-body .col:first-child {
  padding-right: 5mm;
}

/* 매 페이지 푸터 — 페이지번호 박스(SVG) + 저작권 */
.mock-footer {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  margin-top: 4mm;
  padding-top: 1mm;
  border-top: 0;
  font-family: 'Nanum Myeongjo', serif;
}
.mock-footer-pagebox { text-align: center; }
.mock-footer-pagebox svg { display: block; margin: 0 auto; }
.mock-footer-copyright {
  grid-column: 3;
  text-align: right;
  font-size: 8.5pt;
  color: #b00;
}
"""


def render_mock_page_header(meta: ExamMeta, page_idx: int,
                             total_pages: int) -> str:
    """수능형 모의고사 각 페이지 헤더. page_idx 는 1부터."""
    title_big = _html_escape(meta.inner_title or "수학 영역")
    odd_box = '<span class="mock-box">홀수형</span>'
    pagenum = f'<span class="mock-pagenum">{page_idx}</span>'

    if page_idx == 1:
        subtitle = (
            f"{meta.school_year}학년도 대학수학능력시험 문제지"
        )
        return f"""
<header class="mock-header mock-header-p1">
  <div class="mock-h-left">
    <span class="mock-box">제 {meta.period} 교시</span>
  </div>
  <div class="mock-h-center">
    <div class="mock-h-sub">{_html_escape(subtitle)}</div>
    <div class="mock-h-big">{title_big}</div>
  </div>
  <div class="mock-h-right">
    {pagenum}
    {odd_box}
  </div>
</header>
""".strip()

    # 2쪽 이후 홀짝 패턴
    if page_idx % 2 == 0:
        # 짝수쪽: 페이지번호 좌, 홀수형 우
        return f"""
<header class="mock-header">
  <div class="mock-h-left">{pagenum}</div>
  <div class="mock-h-center">
    <div class="mock-h-big">{title_big}</div>
  </div>
  <div class="mock-h-right">{odd_box}</div>
</header>
""".strip()
    else:
        # 홀수쪽 (3, 5, 7...): 홀수형 좌, 페이지번호 우
        return f"""
<header class="mock-header">
  <div class="mock-h-left">{odd_box}</div>
  <div class="mock-h-center">
    <div class="mock-h-big">{title_big}</div>
  </div>
  <div class="mock-h-right">{pagenum}</div>
</header>
""".strip()


def render_mock_page_footer(meta: ExamMeta, page_idx: int,
                             total_pages: int) -> str:
    """수능형 모의고사 페이지 푸터 — 페이지번호 박스(SVG 빗금) + 저작권."""
    # SVG 박스: 좌측 현재 페이지, 대각선, 우측 총 페이지
    svg = (
        '<svg viewBox="0 0 90 36" width="62" height="24">'
        '<rect x="1" y="1" width="88" height="34" fill="none" '
        'stroke="#111" stroke-width="1.2"/>'
        '<line x1="32" y1="34" x2="58" y2="2" stroke="#111" stroke-width="1.2"/>'
        f'<text x="14" y="24" font-family="Nanum Myeongjo, serif" '
        f'font-size="14" font-weight="700" fill="#111">{page_idx}</text>'
        f'<text x="62" y="24" font-family="Nanum Myeongjo, serif" '
        f'font-size="14" font-weight="700" fill="#111">{total_pages}</text>'
        '</svg>'
    )
    return f"""
<div class="mock-footer">
  <div></div>
  <div class="mock-footer-pagebox">{svg}</div>
  <div class="mock-footer-copyright">
    이 문제지에 관한 저작권은 {_html_escape(meta.school_org_name or "출제기관")}에 있습니다.
  </div>
</div>
""".strip()


def render_mock_first_col_extra(meta: ExamMeta) -> str:
    """1쪽 좌측 컬럼 맨 위 prepend — [5지선다형] 라벨."""
    return '<div class="mock-section-label">5지선다형</div>'


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
        "first_col_extra": render_inner_eum_first_col_extra,
        "css": INNER_EUM_CSS,
        "needs_page_count": True,
        "body_class": "",
    },
    "수능형 모의고사 (Image #190~192)": {
        # 페이지 1 헤더는 per_page_header_fn 에서 처리 → first_header 는 비움
        "first_header": lambda meta, n=0: "",
        "first_col_extra": lambda meta, n=0: render_mock_first_col_extra(meta),
        "per_page_header_fn": render_mock_page_header,
        "per_page_footer_fn": render_mock_page_footer,
        "css": INNER_MOCK_CSS,
        "needs_page_count": False,  # first_header/col_extra 는 카운트 불필요
        "body_class": "mock-body",
    },
}


def all_design_css() -> str:
    """페이지 전체에 들어갈 디자인 CSS 모음.

    @font-face 임베드를 가장 먼저 두어 다른 폰트 family 선언 전에 등록.
    """
    return "\n".join([font_face_css(), COMMON_DESIGN_CSS]
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
