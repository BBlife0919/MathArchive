"""
단원별 CLIP 임베딩 기반 다양성 샘플링으로 대표 문제 선정.

핵심 아이디어:
- 유형(subtopic) 자동 분류는 현재 기술 한계로 불완전 → 포기
- 대신 단원별 CLIP 임베딩 거리가 최대한 먼(=서로 다른 시각 패턴) 문제들을 샘플링
- 난이도(하/중)별 분책
- Farthest Point Sampling(FPS): 첫 점 무작위 → 이후 기존 선택 문제와의 최소 거리가 큰 것부터

출력:
- output/crops/selection_diverse.json
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

import numpy as np

EMB_CACHE = Path("output/crops/clip_embeddings.npz")
INDEX = Path("output/crops/index_typed.json")
OUT = Path("output/crops/selection_diverse.json")

CHAPTER_ORDER = [
    "다항식의 연산",
    "항등식과 나머지정리",
    "인수분해",
    "복소수",
    "이차방정식",
    "이차함수",
]

# 단원별·난이도별 목표 개수
TARGET_PER_CHAPTER = {
    "다항식의 연산": 30,
    "항등식과 나머지정리": 25,
    "인수분해": 20,
    "복소수": 30,
    "이차방정식": 30,
    "이차함수": 35,
}


def farthest_point_sampling(emb: np.ndarray, k: int, seed: int = 0) -> list[int]:
    """FPS: 서로 가장 먼 k개 인덱스 반환."""
    n = len(emb)
    if n <= k:
        return list(range(n))
    rng = random.Random(seed)
    first = rng.randrange(n)
    selected = [first]
    # 각 점의 기존 선택들과의 최소 거리
    d = np.linalg.norm(emb - emb[first], axis=1)
    for _ in range(k - 1):
        nxt = int(np.argmax(d))
        selected.append(nxt)
        new_d = np.linalg.norm(emb - emb[nxt], axis=1)
        d = np.minimum(d, new_d)
    return selected


def main() -> None:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    arr = np.load(EMB_CACHE)
    emb_all = arr["emb"]
    emb_all = emb_all / (np.linalg.norm(emb_all, axis=1, keepdims=True) + 1e-9)

    # index_typed.json의 유효 레코드 순서 = CLIP 임베딩 순서 (cluster_clip.py와 동일 로직)
    records = [r for r in data if not r.get("skipped_reason") and r.get("image_path")]
    assert len(records) == len(emb_all), f"크기 불일치 {len(records)} vs {len(emb_all)}"

    selection_by_diff: dict[str, list[dict]] = {"하": [], "중": []}

    for chap in CHAPTER_ORDER:
        target = TARGET_PER_CHAPTER[chap]
        for diff in ["하", "중"]:
            pool_idx = [i for i, r in enumerate(records) if r["chapter"] == chap and r["difficulty"] == diff]
            if not pool_idx:
                continue
            pool_emb = emb_all[pool_idx]
            # 목표 개수 절반 정도씩 (하/중 합쳐 target)
            k = min(target, len(pool_idx))
            picks = farthest_point_sampling(pool_emb, k)
            for order, local_i in enumerate(picks, 1):
                r = records[pool_idx[local_i]]
                selection_by_diff[diff].append({
                    "chapter": chap,
                    "type": chap,  # 유형은 단원 그대로
                    "difficulty": diff,
                    "order_in_chapter": order,
                    "image_path": r["image_path"],
                    "file_stem": r["file_stem"],
                    "seq": r["seq"],
                })

    OUT.write_text(json.dumps({
        "하": {"count": len(selection_by_diff["하"]), "items": selection_by_diff["하"]},
        "중": {"count": len(selection_by_diff["중"]), "items": selection_by_diff["중"]},
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    for diff in ["하", "중"]:
        items = selection_by_diff[diff]
        by_chap = defaultdict(int)
        for it in items:
            by_chap[it["chapter"]] += 1
        print(f"\n=== {diff}난이도 총 {len(items)}문제 ===")
        for chap in CHAPTER_ORDER:
            print(f"  {chap}: {by_chap[chap]}")


if __name__ == "__main__":
    main()
