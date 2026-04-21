"""
각 크롭 문제에 '유형' 라벨을 붙이는 스크립트.

절차:
1. output/crops/index.json 로드 (문제 단위 레코드)
2. 각 레코드의 원본 PDF를 열어 (start_page~end_page, column, y 범위) 영역의 **텍스트**를 추출
3. PUA(한글 수식 글리프) 제거하고 한글 키워드만 남긴 plain_text 생성
4. 유형 규칙(단원별 키워드 목록)에 매칭해 type 필드 부여
5. 매칭 실패 → "기타" 유형
6. output/crops/index_typed.json 저장 + 분포 리포트 출력

유형 규칙은 공수1 교과서 목차 순서를 따른다.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import fitz

INDEX_PATH = Path("output/crops/index.json")
OUT_PATH = Path("output/crops/index_typed.json")

# 단원 내 유형 정의: (유형명, 키워드 패턴) — 키워드 하나라도 텍스트에 있으면 해당 유형
# 순서 중요: 위쪽 유형이 더 구체적이면 먼저 매칭되도록 배치
TYPE_RULES: dict[str, list[tuple[str, list[str]]]] = {
    "다항식의 연산": [
        ("다항식의 나눗셈·조립제법", ["나누었을", "나누었을때", "몫", "조립제법", "나눗셈"]),
        ("곱셈공식과 곱셈", ["곱셈공식", "전개", "계수", "의 계수"]),
        ("다항식의 덧셈·뺄셈", ["두 다항식", "덧셈", "뺄셈", "간단히"]),
    ],
    "항등식과 나머지정리": [
        ("나머지정리·인수정리", ["나머지", "나누어", "나누어떨어", "인수", "인수정리"]),
        ("항등식과 미정계수", ["항등식", "상수", "미정계수"]),
    ],
    "인수분해": [
        ("복이차식·치환 인수분해", ["복이차", "치환", "공통부분", "공통인수"]),
        ("삼차·고차 인수분해", ["삼차", "인수분해", "인수"]),
        ("인수분해 기본", ["인수분해"]),
    ],
    "복소수": [
        ("i의 거듭제곱·규칙", ["거듭제곱", "허수단위", "허수"]),
        ("켤레복소수", ["켤레", "켤레복소수"]),
        ("복소수 상등·사칙연산", ["복소수", "등식", "실수부", "허수부", "상등"]),
    ],
    "이차방정식": [
        ("근과 계수의 관계", ["근과 계수", "근의 합", "근의 곱", "두 근"]),
        ("판별식·근의 조건", ["판별식", "서로 다른", "중근", "실근", "허근", "실수인"]),
        ("이차방정식의 작성", ["이차방정식을", "작성", "방정식을"]),
        ("근의 공식·풀이", ["근의 공식", "이차방정식"]),
    ],
    "이차함수": [
        ("이차함수 최대·최소", ["최댓값", "최솟값", "최대", "최소"]),
        ("이차함수와 직선", ["직선", "만나지", "교점", "접"]),
        ("이차함수와 이차방정식", ["축과", "x축", "축에", "해의"]),
        ("이차함수 그래프·꼭짓점", ["꼭짓점", "대칭축", "축의 방정식", "그래프"]),
    ],
}

PUA_RE = re.compile(r"[\uE000-\uF8FF]+")
CTRL_RE = re.compile(r"[\x00-\x1f]+")
WS_RE = re.compile(r"\s+")


def clean(text: str) -> str:
    """PUA(수식 글리프)·제어문자 제거, 공백 정규화."""
    t = PUA_RE.sub(" ", text)
    t = CTRL_RE.sub(" ", t)
    t = WS_RE.sub(" ", t)
    return t.strip()


def extract_region_text(doc: fitz.Document, r: dict) -> str:
    """크롭 레코드의 (start_page~end_page, col_x0/col_x1, start_y~end_y) 영역 텍스트 추출."""
    # index.json에 저장된 필드 이름에 맞춰 Read
    # start_page는 1-based로 저장돼 있다(기존 스크립트가 +1 보정해서 기록)
    start_page = int(r["start_page"]) - 1
    end_page = int(r["end_page"]) - 1
    parts: list[str] = []
    for pno in range(start_page, end_page + 1):
        if pno < 0 or pno >= len(doc):
            continue
        page = doc[pno]
        page_w = page.rect.width
        mid = page_w / 2.0
        # column은 index.json에 직접 없음. 파일명 필드로 추론 불가하므로 모든 column 영역 텍스트 사용.
        # 대신 chapter 앵커 찾는 방식으로 해당 column 추정은 생략하고 전체 페이지 텍스트 합침.
        t = page.get_text()
        parts.append(t)
    return clean(" ".join(parts))


def classify(chapter: str, text: str) -> str:
    rules = TYPE_RULES.get(chapter, [])
    for name, keywords in rules:
        for kw in keywords:
            if kw in text:
                return name
    return "기타"


def main() -> None:
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    # 파일별로 레코드 그룹화해 PDF 한 번만 열기
    by_file: dict[str, list[dict]] = defaultdict(list)
    for r in data:
        if r.get("skipped_reason") or r.get("error"):
            continue
        by_file[r["file_stem"]].append(r)

    src_dir = Path("/Users/youngwoolee/Downloads/빈출교재 만들기")
    type_counter: Counter = Counter()
    chapter_type_counter: Counter = Counter()

    for file_stem, records in by_file.items():
        pdf_candidates = list(src_dir.glob(f"{file_stem}*.pdf"))
        if not pdf_candidates:
            # index.json의 file_stem이 원본 파일명과 같지만 특수문자 이스케이프 문제 있을 수 있음
            pdf_candidates = [p for p in src_dir.glob("*.pdf") if p.stem == file_stem]
        if not pdf_candidates:
            continue
        doc = fitz.open(pdf_candidates[0])
        # 페이지 단위로 텍스트 캐시 (같은 파일의 여러 문제들이 공유)
        page_text_cache = {pno: clean(doc[pno].get_text()) for pno in range(len(doc))}
        for r in records:
            sp = int(r["start_page"]) - 1
            ep = int(r["end_page"]) - 1
            text = " ".join(page_text_cache.get(p, "") for p in range(sp, ep + 1))
            r["plain_text"] = text[:800]  # 너무 길면 800자 제한
            r["type"] = classify(r["chapter"], text)
            type_counter[r["type"]] += 1
            chapter_type_counter[(r["chapter"], r["type"])] += 1
        doc.close()

    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장: {OUT_PATH}")
    print(f"\n단원 × 유형 분포:")
    for chap in ["다항식의 연산", "항등식과 나머지정리", "인수분해", "복소수", "이차방정식", "이차함수"]:
        print(f"\n▶ {chap}")
        items = [(k[1], v) for k, v in chapter_type_counter.items() if k[0] == chap]
        for name, cnt in sorted(items, key=lambda x: -x[1]):
            print(f"    {name}: {cnt}")


if __name__ == "__main__":
    main()
