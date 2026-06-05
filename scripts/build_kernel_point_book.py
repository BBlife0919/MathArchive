#!/usr/bin/env python3
"""KERNEL POINT — 광명 고2 대수 1학기 기말 내신기출 PDF 빌더.

조건:
- region='경기광명시', grade=2
- chapter ∈ 6개 (curriculum 순서):
  삼각함수와 그래프 → 사인법칙과 코사인법칙 → 등차수열 → 등비수열
  → 수열의 합 → 수학적 귀납법
- 정렬: 단원(curriculum) 오름차순 → 난이도(하<중<상<킬) 오름차순
- 레이아웃: 2단, 단당 1문제 (페이지당 2문제, 모든 문항 full)
- 해설: 맨 뒤 챕터별 쭉
- 챕터 디바이더: 화이트+블루 디자인 (자동 I/II + SECTION 번호)

데이터 소스: cloud Postgres (chapter 정규화 완료된 상태).
출력: /Users/youngwoolee/Downloads/대수_1학기기말_필수유형FINAL.pdf
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
sys.path.insert(0, str(APP))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

CHAPTERS = [
    "삼각함수와 그래프",
    "사인법칙과 코사인법칙",
    "등차수열",
    "등비수열",
    "수열의 합",
    "수학적 귀납법",
]
DIFF_ORDER = {"하": 0, "중": 1, "상": 2, "킬": 3}


def fetch_rows():
    import psycopg2
    from psycopg2.extras import DictCursor
    dsn = os.environ["SUPABASE_DB_URL"]
    conn = psycopg2.connect(dsn, cursor_factory=DictCursor)
    cur = conn.cursor()
    marks = ",".join(["%s"] * len(CHAPTERS))
    cur.execute(
        f"SELECT q.question_id, q.file_source, q.school, q.region, q.grade, "
        f"       q.year, q.semester, q.exam_type, q.subject, "
        f"       q.question_number, q.question_text, q.choices, "
        f"       q.answer, q.answer_type, q.points, q.chapter, "
        f"       q.difficulty, q.has_image, q.is_subjective, "
        f"       s.solution_text "
        f"FROM questions q "
        f"LEFT JOIN solutions s ON q.question_id = s.question_id "
        f"WHERE q.region = %s AND q.grade = %s "
        f"  AND q.chapter IN ({marks})",
        ("경기광명시", 2, *CHAPTERS),
    )
    rows = [dict(r) for r in cur.fetchall()]

    # 문항별 이미지 (image_ref → image_path[R2 URL]) 부착 → 본문 <img> 임베드용
    qids = [r["question_id"] for r in rows]
    if qids:
        imarks = ",".join(["%s"] * len(qids))
        cur.execute(
            f"SELECT question_id, image_ref, image_path, image_type "
            f"FROM images WHERE question_id IN ({imarks})",
            tuple(qids),
        )
        img_by_q: dict = {}
        sol_by_q: dict = {}
        for ir in cur.fetchall():
            target = sol_by_q if (ir["image_type"] == "solution") else img_by_q
            target.setdefault(ir["question_id"], {})[ir["image_ref"]] = ir["image_path"]
        for r in rows:
            r["images"] = img_by_q.get(r["question_id"], {})
            if r["question_id"] in sol_by_q:
                r["images_sol"] = sol_by_q[r["question_id"]]

        # 합성 이미지 의심 문항 → '그림 확인 필요' 배지 플래그
        import json as _json
        comp_path = ROOT / "output" / "composite_image_qids.json"
        if comp_path.exists():
            comp = set(_json.loads(comp_path.read_text()))
            for r in rows:
                if r["question_id"] in comp:
                    r["img_check"] = True

    cur.close()
    conn.close()
    return rows


def main():
    print("[1/4] cloud DB 조회...")
    rows = fetch_rows()
    print(f"  매칭 문항(전체): {len(rows)}")
    # 난이도 '상' 행 제외 (사용자 지시)
    rows = [r for r in rows if r.get("difficulty") != "상"]
    print(f"  난이도 '상' 제외 후: {len(rows)}")

    # 정렬: chapter (CHAPTERS 순서) → 난이도 → question_id
    chap_idx = {c: i for i, c in enumerate(CHAPTERS)}
    rows.sort(key=lambda r: (
        chap_idx.get(r["chapter"], 999),
        DIFF_ORDER.get(r["difficulty"], 99),
        r["question_id"],
    ))

    # cloud choices 는 jsonb 라 list 로 자동 디코딩됨. pdf_engine 의
    # format_choices 는 list/JSON 문자열 둘 다 처리하지만 일관성 위해 dump.
    import json
    for r in rows:
        ch = r.get("choices")
        if ch is not None and not isinstance(ch, str):
            r["choices"] = json.dumps(ch, ensure_ascii=False)

    # 분포 출력
    print("[2/4] 분포:")
    from collections import Counter
    by_chap = Counter(r["chapter"] for r in rows)
    for c in CHAPTERS:
        print(f"  {c:25s} {by_chap.get(c, 0)}")

    # overrides: 모든 문항 full (2단 1문제씩)
    overrides = {r["question_id"]: "full" for r in rows}

    # 로고
    logo_path = APP / "assets" / "eum_logo.png"

    print("[3/4] PDF 생성...")
    from pdf_engine import generate_book_pdf
    pdf_bytes = generate_book_pdf(
        rows,
        title="KERNEL POINT",
        subtitle="대수 1학기 기말 내신기출",
        include_source=True,
        overrides=overrides,
        logo_path=str(logo_path) if logo_path.exists() else None,
        kicker_mark=None,
        kicker_text=None,
        divider_meta_top="대수 1학기 기말 · KERNEL POINT",
        divider_footer_title="대수 1학기 기말 · 내신기출 KERNEL POINT",
        divider_footer_sub="이영우 T",
        cover_main_title="KERNEL POINT",
        cover_tagline="대수 1학기 기말 내신기출",
        cover_big_word="FINAL",
        cover_kicker="MATH WORKBOOK · 2026",
        cover_footer_main="Algebra Final Workbook · 2026",
        cover_footer_sub="필수유형으로 끝내는 기말 마무리",
        page_running_left="KERNEL POINT",
    )

    # 벡터 원본 보관 (텍스트 선택용)
    vec_path = ROOT / "output" / "daesu_kernel_point_vector.pdf"
    vec_path.parent.mkdir(exist_ok=True)
    vec_path.write_bytes(pdf_bytes)

    # Downloads 에는 '뷰어 안전' 래스터화본 — Chromium 의 Type3 폰트 과부하로
    # Acrobat/Preview 가 렌더 못 하는 문제 회피 (각 페이지 이미지화). 빈 페이지도 제거.
    import fitz
    src = fitz.open(stream=pdf_bytes, filetype="pdf")
    out = fitz.open()
    mat = fitz.Matrix(180 / 72, 180 / 72)
    for pg in src:
        if len(pg.get_text().strip()) < 3 and not pg.get_images() and len(pg.get_drawings()) < 3:
            continue  # 빈 페이지 건너뜀
        pix = pg.get_pixmap(matrix=mat, alpha=False)
        npg = out.new_page(width=pg.rect.width, height=pg.rect.height)
        npg.insert_image(pg.rect, stream=pix.tobytes("jpeg", jpg_quality=82))
    out_path = Path("/Users/youngwoolee/Downloads/대수 1학기 기말 KERNEL POINT.pdf")
    out.save(str(out_path), garbage=4, deflate=True)
    out.close(); src.close()

    # Ghostscript 재증류 — PyMuPDF 가 만든 PDF 구조를 Acrobat 이 열 때 자동 '복구'를
    # 시도하며 저장 시 error 117(읽기 오류)을 내는 문제 회피. gs 가 완전히 새 구조로
    # 다시 쓰면 Acrobat/Preview 모두 깔끔히 열림. (180dpi 유지, gs 없으면 PyMuPDF 본 유지)
    _gs_redistill(out_path)
    print(f"[4/4] 저장: {out_path} (래스터/뷰어안전, {out_path.stat().st_size/1024/1024:.0f}MB) "
          f"+ 벡터본 {vec_path}")


def _gs_redistill(path: Path) -> None:
    """Acrobat 호환을 위해 Ghostscript 로 PDF 재증류 (실패 시 원본 유지)."""
    import shutil
    import subprocess
    gs = shutil.which("gs")
    if not gs:
        print("  (gs 없음 → PyMuPDF 본 유지)")
        return
    tmp = path.with_suffix(".gs.pdf")
    cmd = [
        gs, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.6",
        "-dPDFSETTINGS=/printer", "-dNOPAUSE", "-dBATCH", "-dQUIET",
        "-dAutoRotatePages=/None", "-dDetectDuplicateImages=true",
        "-dColorImageDownsampleType=/Bicubic", "-dColorImageResolution=180",
        f"-sOutputFile={tmp}", str(path),
    ]
    try:
        r = subprocess.run(cmd, timeout=300)
        if r.returncode == 0 and tmp.exists() and tmp.stat().st_size > 0:
            shutil.move(str(tmp), str(path))
            print("  (gs 재증류 완료 — Acrobat 호환)")
        else:
            tmp.unlink(missing_ok=True)
            print("  (gs 실패 → PyMuPDF 본 유지)")
    except Exception as e:  # noqa: BLE001
        tmp.unlink(missing_ok=True)
        print(f"  (gs 예외 {e} → PyMuPDF 본 유지)")


if __name__ == "__main__":
    main()
