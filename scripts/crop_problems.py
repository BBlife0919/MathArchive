"""
PDF에서 문제 단위로 영역을 크롭해 PNG로 저장.

앵커 규칙:
- 각 문제는 `[중단원] XXX` → `[난이도] X` 순서로 끝난다.
- 문제 시작 = (같은 파일 내) 이전 `[난이도]` 블록의 y1 다음 픽셀, 없으면 현재 페이지 상단.
- 페이지 걸침 케이스: 문제 본문이 전 페이지에서 시작해 현재 페이지에서 끝날 수 있음 → 두 조각을 세로로 이어 붙여 한 장의 PNG로 저장.

필터/정규화:
- 포함 단원: 다항식의 연산, 항등식과 나머지정리, 인수분해, 복소수, 이차방정식, 이차함수
- 정규화:
  - "나머지정리", "항등식과 나머니정리", "항등식과 나머지정리" → "항등식과 나머지정리"
  - "다항함수" → "이차함수"
- 그 외(고차방정식, 연립방정식, 부등식, 행렬 등)는 전부 스킵.

출력:
- 크롭 PNG: <out_dir>/<원본파일stem>__<seq>_<정규화단원>_<난이도>.png
- 인덱스 JSON: <out_dir>/index.json (파일, 단원, 난이도, 경로 기록)
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import fitz

INCLUDE_CHAPTERS = {
    "다항식의 연산",
    "항등식과 나머지정리",
    "인수분해",
    "복소수",
    "이차방정식",
    "이차함수",
}


def _canon(s: str) -> str:
    """\x01 같은 한글 PDF 제어문자와 공백을 전부 제거한 canonical 표기."""
    return re.sub(r"\s+", "", s.replace("\x01", ""))


# canonical(공백/제어문자 제거) 키 → 정규화된 단원명
CHAPTER_ALIASES_CANON: dict[str, str] = {
    _canon("다항식의 연산"): "다항식의 연산",
    _canon("다항식의연산"): "다항식의 연산",
    _canon("항등식과 나머지정리"): "항등식과 나머지정리",
    _canon("항등식과 나머지 정리"): "항등식과 나머지정리",
    _canon("항등식과 나머니정리"): "항등식과 나머지정리",
    _canon("항등식과나머니정리"): "항등식과 나머지정리",
    _canon("나머지정리"): "항등식과 나머지정리",
    _canon("나머지 정리"): "항등식과 나머지정리",
    _canon("항등식"): "항등식과 나머지정리",
    _canon("인수분해"): "인수분해",
    _canon("복소수"): "복소수",
    _canon("이차방정식"): "이차방정식",
    _canon("이차함수"): "이차함수",
    _canon("다항함수"): "이차함수",
}

DIFFICULTY_WHITELIST = {"하", "중"}  # 상/킬은 제외
DIFFICULTY_CANON = {_canon(d): d for d in DIFFICULTY_WHITELIST}

RENDER_DPI = 200
SIDE_MARGIN_PT = 40.0
HEADER_SKIP_PT = 95.0  # 이 y 이하는 페이지 헤더(학교명/단원 라벨)로 간주하고 스킵
TOP_MARGIN_PT = 100.0  # 본문 블록을 찾지 못했을 때의 폴백
BOTTOM_MARGIN_PT = 50.0

# 2단 레이아웃 경계 (A4 세로형 595pt 기준)
COL_GAP_PT = 10.0  # 단과 단 사이 여유
# 왼쪽 단: x ~ [LEFT_X0, LEFT_X1], 오른쪽 단: x ~ [RIGHT_X0, RIGHT_X1]


@dataclass
class Anchor:
    page_idx: int
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    column: int = 0  # 0=left, 1=right


@dataclass
class Problem:
    seq: int
    chapter_raw: str
    chapter: str
    difficulty: str
    column: int
    start_page: int
    start_y: float
    end_page: int
    end_y: float
    col_x0: float
    col_x1: float
    file_stem: str
    skipped_reason: str = ""


def normalize_chapter(raw: str) -> str:
    key = _canon(raw)
    if key in CHAPTER_ALIASES_CANON:
        return CHAPTER_ALIASES_CANON[key]
    # 디폴트: 공백/제어문자만 정돈해서 반환
    return re.sub(r"\s+", " ", raw.replace("\x01", " ")).strip()


def normalize_difficulty(raw: str) -> str:
    key = _canon(raw)
    return DIFFICULTY_CANON.get(key, raw.replace("\x01", "").strip())


def collect_anchors(doc: fitz.Document) -> tuple[list[Anchor], list[Anchor], float]:
    """페이지 순회하며 [중단원]/[난이도] 앵커 수집. 페이지 중앙 x 기준으로 column 판정."""
    chapter_anchors: list[Anchor] = []
    diff_anchors: list[Anchor] = []
    page_width = doc[0].rect.width if len(doc) else 595.0
    mid_x = page_width / 2.0
    for pno, page in enumerate(doc):
        for b in page.get_text("blocks"):
            x0, y0, x1, y1, text, bno, btype = b
            if btype != 0:
                continue
            t = text.strip()
            col = 0 if (x0 + x1) / 2 < mid_x else 1
            if t.startswith("[중단원]"):
                chapter_anchors.append(Anchor(pno, x0, y0, x1, y1, t, col))
            elif t.startswith("[난이도]"):
                diff_anchors.append(Anchor(pno, x0, y0, x1, y1, t, col))
    return chapter_anchors, diff_anchors, page_width


def find_content_start_y(page: fitz.Page, col: int, mid_x: float) -> float:
    """해당 페이지·column에서 헤더 영역(y≤HEADER_SKIP_PT)을 스킵하고 본문 첫 텍스트 블록의 y0를 반환."""
    best: float | None = None
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, text, bno, btype = b
        if btype != 0:
            continue
        if not text.strip():
            continue
        if y1 <= HEADER_SKIP_PT:
            continue
        # 양쪽 단에 걸친 블록(가로 배너 등)은 헤더 취급
        if x0 < mid_x - 20 and x1 > mid_x + 20:
            continue
        c = 0 if (x0 + x1) / 2 < mid_x else 1
        if c != col:
            continue
        if best is None or y0 < best:
            best = y0
    return (best - 4.0) if best is not None else TOP_MARGIN_PT


def pair_anchors(chapters: list[Anchor], diffs: list[Anchor]) -> list[tuple[Anchor, Anchor]]:
    """[중단원] 바로 뒤 같은 column에서 등장하는 [난이도]와 짝짓기."""
    pairs: list[tuple[Anchor, Anchor]] = []
    used = [False] * len(diffs)
    for ca in chapters:
        best_idx = -1
        best_key = None
        for i, da in enumerate(diffs):
            if used[i]:
                continue
            if da.column != ca.column:
                continue
            if (da.page_idx, da.y0) < (ca.page_idx, ca.y1):
                continue
            key = (da.page_idx - ca.page_idx, da.y0 - ca.y1 if da.page_idx == ca.page_idx else da.y0)
            if best_key is None or key < best_key:
                best_key = key
                best_idx = i
        if best_idx >= 0:
            used[best_idx] = True
            pairs.append((ca, diffs[best_idx]))
    return pairs


def extract_problems(doc: fitz.Document, file_stem: str) -> list[Problem]:
    chapter_anchors, diff_anchors, page_width = collect_anchors(doc)
    pairs = pair_anchors(chapter_anchors, diff_anchors)
    # column 및 페이지/y 순서로 정렬
    pairs.sort(key=lambda p: (p[1].page_idx, p[1].column, p[1].y1))

    # column별 x 경계: 페이지 본문 텍스트 블록 전체에서 mid_x 기준 좌/우로 분류해 실제 폭 추정.
    mid = page_width / 2.0
    col_bounds: dict[int, tuple[float, float]] = {0: (9999.0, -1.0), 1: (9999.0, -1.0)}
    for page in doc:
        for b in page.get_text("blocks"):
            x0, y0, x1, y1, text, bno, btype = b
            if btype != 0 or not text.strip():
                continue
            # 블록이 양쪽 단에 걸치면 버림(드물지만 방어)
            if x0 < mid - 20 and x1 > mid + 20:
                continue
            c = 0 if (x0 + x1) / 2 < mid else 1
            lo, hi = col_bounds[c]
            col_bounds[c] = (min(lo, x0), max(hi, x1))
    if col_bounds[0][1] < 0:
        col_bounds[0] = (30.0, mid - COL_GAP_PT / 2)
    if col_bounds[1][1] < 0:
        col_bounds[1] = (mid + COL_GAP_PT / 2, page_width - 30.0)
    # 단 사이 간섭 방지: 서로의 bound가 mid를 넘지 않게 clamp
    col_bounds[0] = (col_bounds[0][0], min(col_bounds[0][1], mid - COL_GAP_PT / 2))
    col_bounds[1] = (max(col_bounds[1][0], mid + COL_GAP_PT / 2), col_bounds[1][1])

    problems: list[Problem] = []
    # 각 페이지·column의 본문 시작 y 캐시
    start_cache: dict[tuple[int, int], float] = {}

    def page_start(pno: int, col: int) -> float:
        key = (pno, col)
        if key not in start_cache:
            start_cache[key] = find_content_start_y(doc[pno], col, mid)
        return start_cache[key]

    # column별 prev_end 추적 (첫 페이지도 본문 첫 블록 y부터 시작)
    prev_end: dict[int, tuple[int, float]] = {
        0: (0, page_start(0, 0)),
        1: (0, page_start(0, 1)),
    }
    for seq, (ca, da) in enumerate(pairs, start=1):
        chapter_raw = ca.text.replace("[중단원]", "").replace("\x01", " ").strip()
        chapter = normalize_chapter(ca.text.replace("[중단원]", ""))
        diff = normalize_difficulty(da.text.replace("[난이도]", ""))
        col = da.column

        # 새 페이지로 넘어가면 본문 첫 텍스트 블록 y로 리셋(헤더 영역 스킵)
        pe_page, pe_y = prev_end[col]
        if pe_page != da.page_idx:
            pe_page = da.page_idx
            pe_y = page_start(da.page_idx, col)

        end_page = da.page_idx
        end_y = da.y1 + 6.0
        cx0, cx1 = col_bounds[col]

        p = Problem(
            seq=seq,
            chapter_raw=chapter_raw,
            chapter=chapter,
            difficulty=diff,
            column=col,
            start_page=pe_page,
            start_y=pe_y,
            end_page=end_page,
            end_y=end_y,
            col_x0=max(cx0 - 15, 0),
            col_x1=min(cx1 + 15, page_width),
            file_stem=file_stem,
        )
        if chapter not in INCLUDE_CHAPTERS:
            p.skipped_reason = f"chapter_filtered:{chapter_raw}"
        elif diff not in DIFFICULTY_WHITELIST:
            p.skipped_reason = f"bad_difficulty:{diff}"
        problems.append(p)

        prev_end[col] = (end_page, end_y)

    return problems


def render_crop(doc: fitz.Document, p: Problem, out_path: Path) -> None:
    """해당 단(column) 영역만 크롭해 PNG 저장. 페이지 걸침 시 세로 결합."""
    tiles = []
    zoom = RENDER_DPI / 72.0
    mat = fitz.Matrix(zoom, zoom)
    for pno in range(p.start_page, p.end_page + 1):
        page = doc[pno]
        page_rect = page.rect
        top = p.start_y if pno == p.start_page else 0.0
        bottom = p.end_y if pno == p.end_page else page_rect.height
        if bottom - top < 10:
            continue
        clip = fitz.Rect(
            max(p.col_x0, 0),
            max(top - 4, 0),
            min(p.col_x1, page_rect.width),
            min(bottom + 4, page_rect.height),
        )
        pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)
        tiles.append(pix)

    if not tiles:
        return
    if len(tiles) == 1:
        tiles[0].save(str(out_path))
        return

    width = max(t.width for t in tiles)
    height = sum(t.height for t in tiles)
    combined = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, width, height), False)
    combined.clear_with(255)
    y_cursor = 0
    for t in tiles:
        x_off = (width - t.width) // 2
        combined.copy(t, fitz.IRect(x_off, y_cursor, x_off + t.width, y_cursor + t.height))
        y_cursor += t.height
    combined.save(str(out_path))


def safe_slug(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]+", "_", text).strip("_")


def process_file(pdf_path: Path, out_dir: Path) -> list[dict]:
    doc = fitz.open(pdf_path)
    file_stem = pdf_path.stem
    problems = extract_problems(doc, file_stem)
    records: list[dict] = []
    for p in problems:
        record = {
            "file_stem": file_stem,
            "seq": p.seq,
            "chapter_raw": p.chapter_raw,
            "chapter": p.chapter,
            "difficulty": p.difficulty,
            "start_page": p.start_page + 1,
            "end_page": p.end_page + 1,
            "skipped_reason": p.skipped_reason,
            "image_path": "",
        }
        if not p.skipped_reason:
            slug = f"{safe_slug(file_stem)[:60]}__{p.seq:02d}_{safe_slug(p.chapter)}_{safe_slug(p.difficulty)}.png"
            out_path = out_dir / slug
            try:
                render_crop(doc, p, out_path)
                record["image_path"] = str(out_path)
            except Exception as e:  # noqa: BLE001
                record["skipped_reason"] = f"render_error:{e}"
        records.append(record)
    doc.close()
    return records


def main() -> None:
    src_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    all_records: list[dict] = []
    pdfs = sorted(src_dir.glob("*.pdf"))
    print(f"처리 대상 PDF: {len(pdfs)}개")
    for i, pdf in enumerate(pdfs, 1):
        try:
            recs = process_file(pdf, out_dir)
            kept = sum(1 for r in recs if not r["skipped_reason"])
            print(f"  [{i}/{len(pdfs)}] {pdf.name} → 문항 {len(recs)}개 중 채택 {kept}개")
            all_records.extend(recs)
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}/{len(pdfs)}] {pdf.name} 실패: {e}")
            all_records.append({"file_stem": pdf.stem, "error": str(e)})

    index_path = out_dir / "index.json"
    index_path.write_text(json.dumps(all_records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n인덱스 저장: {index_path}")

    # 요약 리포트
    by_chapter: dict[str, int] = {}
    by_diff: dict[str, int] = {}
    skipped = 0
    kept = 0
    for r in all_records:
        if r.get("error") or r.get("skipped_reason"):
            skipped += 1
            continue
        kept += 1
        by_chapter[r["chapter"]] = by_chapter.get(r["chapter"], 0) + 1
        by_diff[r["difficulty"]] = by_diff.get(r["difficulty"], 0) + 1
    print(f"\n총 추출 문항: {len(all_records)}개 / 채택 {kept} / 스킵 {skipped}")
    print("채택 단원 분포:")
    for k, v in sorted(by_chapter.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print("채택 난이도 분포:")
    for k, v in sorted(by_diff.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
