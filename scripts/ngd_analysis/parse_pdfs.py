"""
광명시 고1 1학기 중간 기출 PDF 28개 파싱.

각 문항 하단 `[중단원] X` `[난이도] Y` 라벨 기반으로 분리.
페이지를 좌/우 2단으로 crop한 뒤 개별 추출하여 순서 꼬임 방지.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pdfplumber

PDF_DIR = Path("/Users/youngwoolee/Downloads/공수1 pdf 분석")
OUT = Path("/Users/youngwoolee/MathDB/scripts/ngd_analysis/parsed.json")

CHAPTER_NORMALIZE = {
    "다항함수": "이차함수",
    "나머지정리": "항등식과 나머지정리",
    "나머지 정리": "항등식과 나머지정리",
    "항등식과 나머지 정리": "항등식과 나머지정리",
    "항등식": "항등식과 나머지정리",
    "다항식": "다항식의 연산",
}

TARGET_CHAPTERS = {
    "다항식의 연산",
    "항등식과 나머지정리",
    "인수분해",
    "복소수",
    "이차방정식",
    "이차함수",
}

# 여러 공백/줄바꿈 허용
META = re.compile(
    r"\[\s*중단원\s*\]\s*([^\n\[]+?)\s*\n\s*\[\s*난이도\s*\]\s*([상중하])"
)
Q_START = re.compile(r"(?:^|\n)\s*(\d{1,2})\s*\.\s*")


def extract_columns(pdf_path: Path) -> list[str]:
    """페이지를 좌/우 2단으로 분할 추출. 최상단 헤더 영역은 제외.

    컬럼 경계는 실제 [중단원] 라벨 x 위치(~361) 기반으로 x=355 사용.
    """
    chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            w, h = page.width, page.height
            top = 150 if page_idx == 0 else 90  # 첫 페이지만 저작권 블록 크게 잘라냄
            bottom = h - 30
            # 페이지 폭에 비례한 분할점 (A4기준 729pt → 355)
            split_x = w * 355 / 729
            left = page.crop((0, top, split_x, bottom))
            right = page.crop((split_x, top, w, bottom))
            for col in (left, right):
                t = col.extract_text(x_tolerance=1.5, y_tolerance=2) or ""
                if t.strip():
                    chunks.append(t)
    return chunks


def squeeze_spaces(text: str) -> str:
    """null 문자 제거, 이중공백 정리."""
    text = text.replace("\x00", "")
    # PUA 영역(수식 폰트 글리프)은 제거 — 타입 분류에 무의미
    text = re.sub(r"[-]", "", text)
    lines = []
    for ln in text.split("\n"):
        ln = re.sub(r" {2,}", " ", ln).strip()
        lines.append(ln)
    return "\n".join(lines)


def strip_noise(text: str) -> str:
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            continue
        if re.fullmatch(r"\d{1,3}", s):  # 페이지 번호
            continue
        if re.fullmatch(r"[NGD]", s):  # 워터마크 글자 N G D
            continue
        if "콘텐츠산업" in s or "제작연월일" in s or "제작자" in s:
            continue
        if "이 콘텐츠는" in s or "자료를 무단" in s:
            continue
        if "cafe.naver.com/ngdmath" in s:
            continue
        if "수학적실험실" in s and "공동" in s:
            continue
        if "공동작업파일" in s or "공동저작물" in s:
            continue
        if re.search(r"고등학교$|학기 중간|학기 기말|공통수학", s) and len(s) < 30:
            continue
        if re.search(r"다항식의 연산 ~", s):
            continue
        out.append(ln)
    return "\n".join(out)


def split_questions(col_text: str, source: str) -> list[dict]:
    text = strip_noise(squeeze_spaces(col_text))
    # 문항 시작점 찾기
    starts = [(m.start(), int(m.group(1))) for m in Q_START.finditer(text)]
    if not starts:
        return []

    blocks = []
    for i, (pos, n) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        body = text[pos:end]
        body = re.sub(r"^\s*\d{1,2}\s*\.\s*", "", body, count=1)
        m = META.search(body)
        if not m:
            continue
        chapter_raw = m.group(1).strip()
        chapter_raw = re.sub(r"\s+", " ", chapter_raw)
        difficulty = m.group(2)
        chapter = CHAPTER_NORMALIZE.get(chapter_raw, chapter_raw)
        question_text = body[: m.start()].strip()
        # 메타 이후 남은 꼬리는 무시
        blocks.append(
            {
                "number": n,
                "chapter_raw": chapter_raw,
                "chapter": chapter,
                "difficulty": difficulty,
                "text": question_text,
                "source": source,
            }
        )
    return blocks


def parse_all() -> list[dict]:
    all_items: list[dict] = []
    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    for p in pdfs:
        try:
            cols = extract_columns(p)
        except Exception as e:
            print(f"[FAIL] {p.name}: {e}")
            continue
        src = unicodedata.normalize("NFC", p.name)
        items = []
        for col_text in cols:
            items.extend(split_questions(col_text, src))
        all_items.extend(items)
        print(f"[OK]   {src}: {len(items)} questions")
    return all_items


def main() -> None:
    items = parse_all()
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2))
    from collections import Counter

    total = len(items)
    target = [
        it
        for it in items
        if it["chapter"] in TARGET_CHAPTERS and it["difficulty"] in {"중", "하"}
    ]
    print(f"\nTotal parsed: {total}")
    print(f"Target (6 chapters * 중/하): {len(target)}")

    by_ch_d = Counter((it["chapter"], it["difficulty"]) for it in items)
    for (ch, d), n in sorted(by_ch_d.items()):
        tag = "*" if (ch in TARGET_CHAPTERS and d in {"중", "하"}) else " "
        print(f"  {tag} {ch:>20s} / {d}: {n}")

    raws = Counter(it["chapter_raw"] for it in items)
    print("\nraw chapter names:")
    for k, v in raws.most_common():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
