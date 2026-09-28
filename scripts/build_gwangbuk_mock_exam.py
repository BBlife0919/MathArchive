#!/usr/bin/env python3
"""광명북고 2026-2학기 중간 실전동형테스트 3회분 빌드.

구성 (세트당 24문항: 객관식 21 + 서술형 3, 배점합 100점):
  - 원본 프린트(2026년 2학기 중간 광명북고 프린트대비자료.pdf) 28문항을
    9~10개씩 변형해 3세트에 분배 (gwangbuk_mock_transformed.py, 전량 사용).
  - 나머지는 매쏠로지 로컬 DB 공수2 1-2-a 하/중 표본(241개교 중 20개교 샘플)에서
    선별한 필러 문항 (gwangbuk_mock_filler_ids.json / _content.json).
  - 정렬: 객관식(하→중→상) 먼저, 주관식(하→중→상) 뒤.
  - 출력: 문제 PDF + 정답/해설 PDF 를 합본해 1개 파일로 저장.

usage: python3 build_gwangbuk_mock_exam.py [세트번호 | all]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
sys.path.insert(0, str(APP))
sys.path.insert(0, str(ROOT / "scripts"))

from gwangbuk_mock_transformed import TRANSFORMED, SET_ORIG_NUMS  # noqa: E402

DIFF_RANK = {"하": 0, "중": 1, "상": 2, "킬": 3}

FILLER_IDS = json.loads((ROOT / "scripts" / "gwangbuk_mock_filler_ids.json").read_text())
FILLER_CONTENT = json.loads((ROOT / "scripts" / "gwangbuk_mock_filler_content.json").read_text())

_qid_counter = [900000]


def _next_qid() -> int:
    _qid_counter[0] += 1
    return _qid_counter[0]


def _insert_points_marker(text: str, points) -> str:
    if not points:
        return text
    marker = f" [{int(points) if float(points) == int(points) else points}점]"
    if "[" in text and "점]" in text:
        return text  # 이미 배점 표기가 있음 (필러 DB 문항)
    # 박스가 텍스트의 맨 끝이면(=<보기>가 질문에 딸린 부속물) 질문 문장 직후·박스 직전에 배점을
    # 삽입. 박스 뒤에 실제 질문("구하시오"/"값은?" 등)이 더 이어지면 맨 끝에 배점을 붙인다.
    if "<<BOX_START>>" in text:
        if text.rstrip().endswith("<<BOX_END>>"):
            i = text.index("<<BOX_START>>")
            return text[:i].rstrip() + marker + text[i:]
        return text.rstrip() + marker
    return text.rstrip() + marker


def _row_from_transformed(orig_num: int) -> dict:
    d = TRANSFORMED[orig_num]
    text = d["question_text"].replace("<br>", "\n")
    text = _insert_points_marker(text, d["points"])
    text = "[프린트]\n" + text  # 변형문제 출처 표시 (문항 위에)
    return dict(
        question_id=_next_qid(),
        file_source=f"이영우T_프린트_변형_원본{orig_num}",
        school=None, grade=1, year=2026, semester=2, exam_type="a",
        subject="공수2",
        question_number=0,
        question_text=text,
        choices=d["choices"],
        answer=d["answer"],
        answer_type="choice" if d["choices"] else "short",
        is_subjective=0 if d["choices"] else 1,
        points=d["points"],
        chapter=d["chapter"],
        difficulty=d["difficulty"],
        has_image=0,
        images={},
        solution_text=d["solution_text"],
        images_sol={},
    )


def _row_from_filler(qid: int) -> dict:
    r = dict(FILLER_CONTENT[str(qid)])
    r["question_id"] = _next_qid()
    r["choices"] = r.get("choices")  # JSON string, format_choices handles it
    r["images"] = {}
    r["images_sol"] = {}
    r["file_source"] = f"공수2_1-2-a_{r.get('school')}"
    r["grade"] = 1
    r["year"] = None
    r["semester"] = 2
    r["exam_type"] = "a"
    r["subject"] = "공수2"
    return r


def build_set(set_no: int) -> list[dict]:
    trans_rows = [_row_from_transformed(n) for n in SET_ORIG_NUMS[set_no]]
    filler_rows = [_row_from_filler(qid) for qid in FILLER_IDS[str(set_no)]]
    all_rows = trans_rows + filler_rows

    def is_subj(r):
        return bool(r.get("is_subjective"))

    obj = sorted([r for r in all_rows if not is_subj(r)],
                 key=lambda r: DIFF_RANK.get(r.get("difficulty"), 1))
    subj = sorted([r for r in all_rows if is_subj(r)],
                  key=lambda r: DIFF_RANK.get(r.get("difficulty"), 1))
    # 서술형은 객관식 번호(1~21)를 이어받지 않고 "서술형1/2/3"로 독립 라벨링
    # (2026-09-28 사용자 요청) — 문제지/빠른정답/해설 세 군데 다 이 라벨로 통일.
    for j, r in enumerate(subj, 1):
        r["display_label"] = f"서술형{j}"
    ordered = obj + subj
    for i, r in enumerate(ordered, 1):
        r["question_number"] = i
    return ordered


def render_answer_key_html(questions: list[dict]) -> str:
    import pdf_engine as pe
    qa = pe._render_quick_answer_table(questions, cols=4)
    sol = pe._render_solution_items(questions, include_source=False)
    body = (
        '<section class="page qa-page">'
        '<h2 class="section-title">빠른 정답</h2>' + qa + '</section>'
        '<section class="page sol-page">'
        '<h2 class="section-title">정답 및 해설</h2>' + sol + '</section>'
    )
    return pe._HTML_WRAP.format(
        title="정답 및 해설", css=pe._CSS, body=body,
        body_class="", postprocess_script=pe._PREVIEW_POSTPROCESS_JS,
    )


def build_one(set_no: int):
    import fitz
    import pdf_engine as pe

    questions = build_set(set_no)
    n_obj = sum(1 for r in questions if not r.get("is_subjective"))
    n_subj = len(questions) - n_obj
    print(f"[세트 {set_no}] 총 {len(questions)}문항 (객관식 {n_obj} + 주관식 {n_subj})")
    from collections import Counter
    print("  단원:", dict(Counter(r["chapter"] for r in questions)))
    print("  난이도:", dict(Counter(r["difficulty"] for r in questions)))

    exam_pdf = pe.generate_exam_pdf(
        questions,
        title=f"실전동형테스트 {set_no}회",
        subtitle="공통수학2 · 평면좌표~도형의 이동 · 광명북고 대비",
        include_source=False,
    )
    key_html = render_answer_key_html(questions)
    key_pdf = pe.html_to_pdf_bytes(key_html)

    book = fitz.open(stream=exam_pdf, filetype="pdf")
    key = fitz.open(stream=key_pdf, filetype="pdf")
    book.insert_pdf(key)
    out_bytes = book.tobytes()
    book.close(); key.close()

    out_dir = Path.home() / "클로드교재"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"광명북고 실전동형테스트 {set_no}회.pdf"
    out_path.write_bytes(out_bytes)
    subprocess.run(["xattr", "-c", str(out_path)], check=False)
    print(f"  [OK] {out_path} ({out_path.stat().st_size/1024/1024:.2f}MB)")


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    sets = [1, 2, 3] if arg == "all" else [int(arg)]
    for s in sets:
        build_one(s)


if __name__ == "__main__":
    main()
