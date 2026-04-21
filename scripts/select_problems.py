"""
유형별 대표 문제 선정.

규칙:
- 난이도(하/중)별로 분책
- 교과서 목차 순서로 단원 정렬: 다항식의 연산 → 항등식과 나머지정리 → 인수분해 → 복소수 → 이차방정식 → 이차함수
- 각 단원 안의 유형 순서는 TYPE_ORDER로 고정
- 유형당 최소 5문제, 최대 MAX_PER_TYPE
- "기타" 유형은 스킵
- 중복 방지: plain_text의 앞 120자를 키로 해시 중복 제거
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

INDEX_PATH = Path("output/crops/index_typed.json")
OUT_PATH = Path("output/crops/selection.json")

CHAPTER_ORDER = [
    "다항식의 연산",
    "항등식과 나머지정리",
    "인수분해",
    "복소수",
    "이차방정식",
    "이차함수",
]

TYPE_ORDER: dict[str, list[str]] = {
    "다항식의 연산": [
        "다항식의 덧셈·뺄셈",
        "곱셈공식과 곱셈",
        "다항식의 나눗셈·조립제법",
    ],
    "항등식과 나머지정리": [
        "항등식과 미정계수",
        "나머지정리·인수정리",
    ],
    "인수분해": [
        "인수분해 기본",
        "복이차식·치환 인수분해",
        "삼차·고차 인수분해",
    ],
    "복소수": [
        "복소수 상등·사칙연산",
        "켤레복소수",
        "i의 거듭제곱·규칙",
    ],
    "이차방정식": [
        "근의 공식·풀이",
        "판별식·근의 조건",
        "근과 계수의 관계",
        "이차방정식의 작성",
    ],
    "이차함수": [
        "이차함수 그래프·꼭짓점",
        "이차함수 최대·최소",
        "이차함수와 이차방정식",
        "이차함수와 직선",
    ],
}

MIN_PER_TYPE = 5
MAX_PER_TYPE = 12


def dedupe_key(r: dict) -> str:
    text = r.get("plain_text", "")[:120]
    return hashlib.md5(text.encode("utf-8")).hexdigest() if text else r["file_stem"] + str(r["seq"])


def select(difficulty: str) -> dict:
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    # 난이도/단원/유형별로 버킷팅
    buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    seen_keys: set[str] = set()
    for r in data:
        if r.get("skipped_reason") or r.get("error"):
            continue
        if r.get("difficulty") != difficulty:
            continue
        if r.get("type") == "기타":
            continue
        k = dedupe_key(r)
        if k in seen_keys:
            continue
        seen_keys.add(k)
        buckets[(r["chapter"], r["type"])].append(r)

    selection: list[dict] = []
    for chap in CHAPTER_ORDER:
        for typ in TYPE_ORDER.get(chap, []):
            pool = buckets.get((chap, typ), [])
            if len(pool) < MIN_PER_TYPE:
                # 부족하면 가능한 만큼만
                picks = pool[:MIN_PER_TYPE]
            else:
                # 골고루 뽑기: 파일 다양성 위해 file_stem 기준 round-robin
                by_file: dict[str, list[dict]] = defaultdict(list)
                for r in pool:
                    by_file[r["file_stem"]].append(r)
                file_keys = sorted(by_file.keys())
                picks: list[dict] = []
                idx = 0
                while len(picks) < MAX_PER_TYPE and file_keys:
                    key = file_keys[idx % len(file_keys)]
                    lst = by_file[key]
                    if lst:
                        picks.append(lst.pop(0))
                    else:
                        file_keys.remove(key)
                        if not file_keys:
                            break
                        continue
                    idx += 1
                # 혹시 부족하면 pool에서 더 채움
                if len(picks) < MIN_PER_TYPE:
                    remaining = [r for r in pool if r not in picks]
                    picks.extend(remaining[: MIN_PER_TYPE - len(picks)])
            for order, r in enumerate(picks, 1):
                selection.append(
                    {
                        "chapter": chap,
                        "type": typ,
                        "difficulty": difficulty,
                        "order_in_type": order,
                        "image_path": r["image_path"],
                        "file_stem": r["file_stem"],
                        "seq": r["seq"],
                    }
                )
    return {"difficulty": difficulty, "count": len(selection), "items": selection}


def main() -> None:
    result = {"하": select("하"), "중": select("중")}
    OUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    for diff in ["하", "중"]:
        print(f"\n=== {diff}난이도 선정 — 총 {result[diff]['count']}문제 ===")
        by_chap_type: dict[tuple[str, str], int] = defaultdict(int)
        for it in result[diff]["items"]:
            by_chap_type[(it["chapter"], it["type"])] += 1
        cur_chap = None
        for chap in CHAPTER_ORDER:
            for typ in TYPE_ORDER.get(chap, []):
                c = by_chap_type.get((chap, typ), 0)
                if c == 0:
                    continue
                if cur_chap != chap:
                    print(f"  ▶ {chap}")
                    cur_chap = chap
                print(f"      {typ}: {c}문제")


if __name__ == "__main__":
    main()
