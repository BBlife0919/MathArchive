"""
CLIP 이미지 임베딩 기반 클러스터링.

크롭 PNG 9,547개를 CLIP으로 임베딩 → 단원별 HDBSCAN 클러스터링.
텍스트 기반은 한글만으로 변별력이 부족했음(수식이 PUA 공백).
CLIP는 이미지 전체 패턴을 보므로 수식 레이아웃·그래프 유무·선지 구조도 반영.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import hdbscan
import numpy as np
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer

IN_PATH = Path("output/crops/index_typed.json")
OUT_PATH = Path("output/crops/index_clip.json")
EMB_CACHE = Path("output/crops/clip_embeddings.npz")

SINGLE_TYPE_CHAPTERS = {"다항식의 연산"}
CHAPTER_ORDER = [
    "다항식의 연산",
    "항등식과 나머지정리",
    "인수분해",
    "복소수",
    "이차방정식",
    "이차함수",
]


def device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def encode_images(paths: list[Path], model: SentenceTransformer, batch: int = 32) -> np.ndarray:
    imgs = []
    embs = []
    for i in range(0, len(paths), batch):
        chunk = []
        for p in paths[i : i + batch]:
            try:
                chunk.append(Image.open(p).convert("RGB"))
            except Exception:
                chunk.append(Image.new("RGB", (224, 224), "white"))
        e = model.encode(chunk, batch_size=batch, show_progress_bar=False, convert_to_numpy=True)
        embs.append(e)
        if (i // batch) % 10 == 0:
            print(f"  {i+len(chunk)}/{len(paths)} 인코딩 완료")
    return np.concatenate(embs, axis=0)


def simple_keyword_name(cluster_id: int, chap: str) -> str:
    return f"{chap} · 유형{cluster_id+1}"


def main() -> None:
    data = json.loads(IN_PATH.read_text(encoding="utf-8"))
    records = [r for r in data if not r.get("skipped_reason") and r.get("image_path")]
    print(f"유효 레코드: {len(records)}")

    dev = device()
    print(f"device: {dev}")
    model = SentenceTransformer("clip-ViT-B-32", device=dev)

    # 경로 리스트화 + 순서 고정
    paths = [Path(r["image_path"]) for r in records]

    # 캐시
    if EMB_CACHE.exists():
        print("캐시 로드")
        arr = np.load(EMB_CACHE)
        emb = arr["emb"]
        if len(emb) != len(records):
            print("  캐시 크기 불일치 → 재계산")
            emb = encode_images(paths, model)
            np.savez(EMB_CACHE, emb=emb)
    else:
        print("임베딩 계산 시작...")
        emb = encode_images(paths, model)
        np.savez(EMB_CACHE, emb=emb)
        print(f"캐시 저장: {EMB_CACHE}")

    # L2 정규화 → 코사인 ≈ 유클리드
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9)

    # 단원별 클러스터링
    for chap in CHAPTER_ORDER:
        idxs = [i for i, r in enumerate(records) if r["chapter"] == chap]
        if not idxs:
            continue
        if chap in SINGLE_TYPE_CHAPTERS:
            for i in idxs:
                records[i]["type"] = chap
                records[i]["cluster_id"] = -1
            print(f"▶ {chap}: 단일 유형 {len(idxs)}")
            continue

        sub_emb = emb[idxs]
        n = len(idxs)
        mcs = max(15, n // 40)
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=mcs,
            min_samples=5,
            metric="euclidean",
            cluster_selection_method="leaf",
        )
        labels = clusterer.fit_predict(sub_emb)
        n_clusters = len([u for u in set(labels) if u != -1])
        noise = int(np.sum(labels == -1))
        print(f"▶ {chap}: n={n} mcs={mcs} 클러스터={n_clusters} 노이즈={noise}")
        for idx, lab in zip(idxs, labels):
            if lab == -1:
                records[idx]["type"] = f"{chap} · 기타"
            else:
                records[idx]["type"] = simple_keyword_name(int(lab), chap)
            records[idx]["cluster_id"] = int(lab)

    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n저장: {OUT_PATH}")

    # 요약
    print("\n=== 단원 × 유형 분포 ===")
    cnt: Counter = Counter()
    for r in data:
        if r.get("type"):
            cnt[(r["chapter"], r["type"])] += 1
    for chap in CHAPTER_ORDER:
        items = [(t, c) for (ch, t), c in cnt.items() if ch == chap]
        print(f"\n▶ {chap}")
        for t, c in sorted(items, key=lambda x: -x[1]):
            print(f"    {t}: {c}")


if __name__ == "__main__":
    main()
