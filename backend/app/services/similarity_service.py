"""로컬 임베딩 기반 유사문항 서비스.

scripts/build_similarity_index.py 산출물(output/similarity_index/)을 읽기만
한다 — 비용 $0, 서버에서는 무거운 임베딩 모델을 로딩하지 않는다(numpy만 사용).
LLM 유형분류(label_types.py)와는 완전히 별개 경로.

인덱스는 로컬 sqlite 기준 자연키(file_source, question_number)로 보관한다.
운영 Postgres 의 question_id 는 로컬과 다를 수 있어 db_service.
question_ids_by_natural_keys() 로 다시 찾아야 한다(write_store() 와 동일 이유).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from threading import Lock

import numpy as np

_INDEX_DIR = Path(__file__).resolve().parents[3] / "output" / "similarity_index"

_lock = Lock()
_state: dict | None = None

TAGS = {
    "maxmin": r"최댓값|최솟값|최대|최소",
    "intersect": r"교점|만나|만날",
    "tangent": r"접선|접할|접하",
    "discriminant": r"판별식|중근|서로\s*다른\s*두\s*점|서로\s*다른\s*두\s*실근",
    "abs": r"절댓값",
    "transform": r"평행이동|대칭이동",
    "vieta": r"근과\s*계수",
    "range_const": r"범위|부등식",
}


def tagset(text: str) -> set[str]:
    return {name for name, pat in TAGS.items() if re.search(pat, text or "")}


def available() -> bool:
    return (_INDEX_DIR / "embeddings.npy").exists()


def _load() -> dict:
    global _state
    if _state is not None:
        return _state
    with _lock:
        if _state is not None:
            return _state
        emb = np.load(_INDEX_DIR / "embeddings.npy")
        meta = [json.loads(line) for line in
                (_INDEX_DIR / "meta.jsonl").open(encoding="utf-8")]
        by_key = {(m["file_source"], m["question_number"]): i
                  for i, m in enumerate(meta)}
        by_chapter: dict[str, list[int]] = {}
        for i, m in enumerate(meta):
            by_chapter.setdefault(m["chapter"], []).append(i)
        _state = {"emb": emb, "meta": meta, "by_key": by_key,
                  "by_chapter": by_chapter}
        return _state


def similar_natural_keys(
    file_source: str, question_number: int, chapter: str,
    difficulty: str | None, question_text: str, limit: int = 5,
) -> list[tuple[str, int, float]]:
    """같은 단원(chapter) 안에서 하이브리드 점수(벡터 60% + 난이도일치 15% +
    기법태그겹침 25%) 상위 limit개의 (file_source, question_number, score).

    인덱스에 이 문항 자체가 없으면(새로 추가된 문항 등) 벡터 없이 태그·
    난이도만으로 거칠게 추천한다 — 서버에서 즉석 임베딩은 하지 않는다.
    """
    st = _load()
    cand_idx = list(st["by_chapter"].get(chapter, []))
    if not cand_idx:
        return []

    qi = st["by_key"].get((file_source, question_number))
    if qi is not None:
        cand_idx = [j for j in cand_idx if j != qi]
        q_vec = st["emb"][qi]
        q_tags = set(st["meta"][qi]["tags"])
        q_diff = st["meta"][qi]["difficulty"]
    else:
        q_vec = None
        q_tags = tagset(question_text)
        q_diff = difficulty

    if not cand_idx:
        return []

    vecs = (st["emb"][cand_idx] @ q_vec) if q_vec is not None else np.zeros(len(cand_idx))

    scored = []
    for k, j in enumerate(cand_idx):
        m = st["meta"][j]
        tj = set(m["tags"])
        union = len(q_tags | tj) or 1
        tag_sim = len(q_tags & tj) / union
        diff_match = 1.0 if m["difficulty"] == q_diff else 0.0
        score = 0.6 * float(vecs[k]) + 0.25 * tag_sim + 0.15 * diff_match
        scored.append((j, score))
    scored.sort(key=lambda x: -x[1])

    return [(st["meta"][j]["file_source"], st["meta"][j]["question_number"], sc)
            for j, sc in scored[:limit]]
