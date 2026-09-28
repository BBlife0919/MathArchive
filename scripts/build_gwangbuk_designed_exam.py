#!/usr/bin/env python3
"""광명북고 실전동형테스트 — '이음고 표지/내지' 디자인(app/exam_designs.py)으로 조립.

사용자가 준 두 참고 PDF(동형모고 표지.pdf / 고1 실전 동형모고 1회.pdf)는 이미
app/exam_designs.py 의 render_cover_eum + render_inner_eum_* 함수가 만드는
바로 그 디자인이다. 그 인프라를 그대로 재사용해 문제를 그 안에 배치한다.

usage: python3 build_gwangbuk_designed_exam.py [세트번호 | all]
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
sys.path.insert(0, str(APP))
sys.path.insert(0, str(ROOT / "scripts"))

import build_gwangbuk_mock_exam as bge  # noqa: E402
import pdf_engine as pe  # noqa: E402
import exam_designs as ed  # noqa: E402
from exam_designs import ExamMeta  # noqa: E402

# JIS B4(257mm x 364mm) — 참고 PDF(고1 실전 동형모고 1회.pdf, 729x1032pt)와 동일 규격.
# 문제 본문 폰트(한글 10pt / 수식 11pt)는 app/pdf_engine.py 기본값 그대로 유지.
B4_CSS = r"""
@page { size: 257mm 364mm; margin: 10mm 10mm; }
.page { min-height: 344mm; }
"""

# ── 표지: 사용자가 준 원본 PDF(동형모고 표지.pdf)를 그대로 패치해서 사용 ──────
# (exam_designs.py 로 코드 재생성한 표지보다 원본 그대로가 더 낫다는 피드백 반영.
#  상단 "2026학년도 2학기 1차 지필평가 문제지"는 회차와 무관하게 항상 고정,
#  "공통수학2" 옆 큰 글씨만 회차(1회/2회/3회)에 따라 바뀐다.)
COVER_SRC = Path.home() / "Downloads" / "동형모고 표지.pdf"
_FONT_SUBSET_DIR = Path("/tmp/gwangbuk_font_subset")


def _ensure_subset_fonts() -> tuple[str, str]:
    """표지에 넣는 두 짧은 문자열만 담은 서브셋 폰트를 만들어 캐시.

    HANBatang(B) 원본은 전체 한글 음절을 담아 28~30MB 라, 그대로 embed하면
    PDF가 수십MB 로 불어난다. 실제 쓰는 글자만 추려 ~10KB 로 줄인다.
    """
    _FONT_SUBSET_DIR.mkdir(exist_ok=True)
    b_out = _FONT_SUBSET_DIR / "HANBatangB_sub.ttf"
    r_out = _FONT_SUBSET_DIR / "HANBatang_sub.ttf"
    if b_out.exists() and r_out.exists():
        return str(b_out), str(r_out)
    from fontTools import subset
    from fontTools.ttLib import TTFont
    chars = set("".join([
        "1회", "2회", "3회",
        "[선택형 문제는 (0123456789)문항, 논술형 문제는 ()문항입니다.]",
    ]))
    text = "".join(sorted(chars))
    for src, out in [
        (str(Path.home() / "Library/Fonts/HANBatangB.ttf"), b_out),
        (str(Path.home() / "Library/Fonts/HANBatang.ttf"), r_out),
    ]:
        font = TTFont(src)
        subsetter = subset.Subsetter()
        subsetter.populate(text=text)
        subsetter.subset(font)
        font.save(str(out))
    return str(b_out), str(r_out)


BATANG_B, BATANG = _ensure_subset_fonts()


def _redact(page, rect, pad=1.0):
    r = fitz.Rect(rect)
    r.x0 -= pad; r.y0 -= pad; r.x1 += pad; r.y1 += pad
    page.add_redact_annot(r, fill=(1, 1, 1))


def build_cover_b4(set_no: int, n_obj: int, n_subj: int) -> bytes:
    """원본 표지(A4)를 패치한 뒤 B4 페이지에 맞게 스케일링해서 반환.

    원본 소스(동형모고 표지.pdf)가 삭제된 경우(2026-09-28 확인), 이번 재배치는
    회차별 선택형/논술형 문항수가 이전과 동일(21+3)해 표지 내용이 바뀔 이유가
    없으므로, 기존에 이미 만들어둔 출력 PDF의 표지 페이지를 그대로 재사용한다.
    """
    if not COVER_SRC.exists():
        existing = Path.home() / "클로드교재" / f"광명북고 실전동형테스트 {set_no}회.pdf"
        if existing.exists():
            old = fitz.open(str(existing))
            out = fitz.open()
            out.insert_pdf(old, from_page=0, to_page=0)
            old.close()
            return out.tobytes()
        raise FileNotFoundError(
            f"{COVER_SRC} 없음 + 재사용할 기존 출력물도 없음 — 표지 원본을 다시 받아야 함"
        )
    doc = fitz.open(str(COVER_SRC))
    page = doc[0]

    rect = fitz.Rect(153.1, 460.7, 451.0, 471.7)
    _redact(page, rect)
    page.apply_redactions()

    page.insert_font(fontname="batang-b", fontfile=BATANG_B)
    page.insert_font(fontname="batang", fontfile=BATANG)

    # "N회" 큰 글씨로 "공통수학2" 옆에 추가 (상단 "1차 지필평가"는 건드리지 않음 — 고정)
    page.insert_text((398, 200), f"{set_no}회", fontsize=34, fontname="batang-b",
                      color=(0, 0, 0))
    new_line = f"[선택형 문제는 ({n_obj:2d})문항, 논술형 문제는 ({n_subj:2d})문항입니다.]"
    page.insert_text((rect.x0, rect.y1 - 2.5), new_line, fontsize=11.04,
                      fontname="batang", color=(0, 0, 0))

    a4_bytes = doc.tobytes()
    doc.close()

    # A4(595x842pt) 내용을 B4(729.12x1032pt) 페이지에 꽉 차게 스케일링해서 삽입
    # (두 규격 모두 세로:가로 = √2:1 비율이라 왜곡 없이 그대로 확대된다.)
    b4 = fitz.open()
    b4_page = b4.new_page(width=729.12, height=1032)
    src = fitz.open(stream=a4_bytes, filetype="pdf")
    b4_page.show_pdf_page(b4_page.rect, src, 0)
    out_bytes = b4.tobytes()
    src.close(); b4.close()
    return out_bytes


@dataclass
class BlankDateMeta(ExamMeta):
    """실제 시행일이 미정이라 원본 참고 PDF처럼 '일/시'를 빈칸으로 표시."""

    def date_korean_full(self) -> str:
        return "2026년 10월 일 시"

    def date_short_with_period(self) -> str:
        return f"2026년 10월 일 (일) {self.period}교시"


def build_one(set_no: int):
    questions = bge.build_set(set_no)
    n_obj = sum(1 for r in questions if not r.get("is_subjective"))
    n_subj = len(questions) - n_obj

    meta = BlankDateMeta(
        school_year=2026, semester=2, session=set_no, grade=1,
        subject=f"공통수학2 {set_no}회", exam_date=date(2026, 10, 1), exam_hour=17, period=1,
        code_number="02", n_choice=n_obj, n_essay=n_subj,
        school_name_short="이음", school_org_name="이음학원",
        instructor_name="이영우",
    )

    # 표지는 원본 PDF 그대로 패치(고정 "1차" 문구 유지) + B4 스케일링
    cover_pdf = build_cover_b4(set_no, n_obj, n_subj)

    # 내지(안내+문제)는 exam_designs.py 인프라 재사용, 표지는 빈 값으로 건너뜀
    exam_html = pe.build_designed_exam_html(
        questions, meta,
        cover_design="",
        inner_design="이음고 내지 (Image #177)",
        include_source=False,
    )
    exam_html = exam_html.replace("</body>", f"<style>{B4_CSS}</style></body>")
    exam_pdf = pe.html_to_pdf_bytes(exam_html)

    key_html = bge.render_answer_key_html(questions)
    key_html = key_html.replace("</body>", f"<style>{B4_CSS}</style></body>")
    key_pdf = pe.html_to_pdf_bytes(key_html)

    out = fitz.open(stream=cover_pdf, filetype="pdf")
    out.insert_pdf(fitz.open(stream=exam_pdf, filetype="pdf"))
    out.insert_pdf(fitz.open(stream=key_pdf, filetype="pdf"))

    out_dir = Path.home() / "클로드교재"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"광명북고 실전동형테스트 {set_no}회.pdf"
    out.save(str(out_path), garbage=4, deflate=True, clean=True)
    out.close()
    subprocess.run(["xattr", "-c", str(out_path)], check=False)
    print(f"[OK] 세트{set_no}: 선택형{n_obj}·논술형{n_subj} -> {out_path} "
          f"({out_path.stat().st_size/1024/1024:.2f}MB)")


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    sets = [1, 2, 3] if arg == "all" else [int(arg)]
    for s in sets:
        build_one(s)


if __name__ == "__main__":
    main()
