"""로컬 임베딩 기반 유사문항 서비스.

scripts/build_similarity_index.py 산출물(output/similarity_index/)을 읽기만
한다 — 비용 $0, 서버에서는 무거운 임베딩 모델을 로딩하지 않는다(numpy만 사용).
LLM 유형분류(label_types.py)와는 완전히 별개 경로.

인덱스는 로컬 sqlite 기준 자연키(file_source, question_number)로 보관한다.
운영 Postgres 의 question_id 는 로컬과 다를 수 있어 db_service.
question_ids_by_natural_keys() 로 다시 찾아야 한다(write_store() 와 동일 이유).

점수 계산은 전부 numpy 로 벡터화한다 — 큰 단원(후보 수천 개)에서 순수
파이썬 반복문으로 돌리면 클릭할 때마다 체감되는 지연이 생긴다(2026-10-26
"뜨는 속도가 느리다" 피드백). 인덱스에 있는 문항(가장 흔한 경로)은
functools.lru_cache 로도 한 번 더 캐싱한다.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from threading import Lock, Thread

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
# tag_mask 를 uint8 비트마스크로 쓰므로 8개 초과 시 깨진다 — 늘릴 땐
# dtype 도 같이(uint8→uint16, _POPCOUNT 테이블도 재설계) 올릴 것.
assert len(TAGS) <= 8, "TAGS 가 8개를 넘으면 tag_mask(uint8) 비트마스크가 깨집니다"
_TAG_BIT = {name: i for i, name in enumerate(TAGS)}
_POPCOUNT8 = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def tagset(text: str) -> set[str]:
    return {name for name, pat in TAGS.items() if re.search(pat, text or "")}


def _mask_from_tags(tags) -> int:
    m = 0
    for t in tags:
        bit = _TAG_BIT.get(t)
        if bit is not None:
            m |= 1 << bit
    return m


def available() -> bool:
    return (_INDEX_DIR / "embeddings.npy").exists()


def warm_async() -> None:
    """서버 기동 시 백그라운드 스레드에서 미리 로드해둔다.

    256MB 임베딩 + 43MB 메타데이터를 파싱하는 데 ~1.2초 걸린다 — 첫 요청이
    올 때 느긋하게 로드하면 그 1.2초를 사용자가 "유사" 버튼 클릭 후 그대로
    체감한다(2026-10-26 "누르자마자 바로 뜨게" 피드백). 서버가 떠 있는 동안
    미리 끝내두면 실제 클릭은 거의 항상 캐시/벡터화 경로만 탄다."""
    if not available():
        return
    Thread(target=_load, daemon=True).start()


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

        chapter_buckets: dict[str, list[int]] = {}
        for i, m in enumerate(meta):
            chapter_buckets.setdefault(m["chapter"], []).append(i)
        by_chapter = {c: np.array(idx, dtype=np.int64)
                      for c, idx in chapter_buckets.items()}

        tag_mask = np.array([_mask_from_tags(m["tags"]) for m in meta], dtype=np.uint8)
        diffs = sorted({m["difficulty"] for m in meta})
        diff_to_code = {d: i for i, d in enumerate(diffs)}
        diff_code = np.array([diff_to_code[m["difficulty"]] for m in meta], dtype=np.int16)

        _state = {
            "emb": emb, "meta": meta, "by_key": by_key, "by_chapter": by_chapter,
            "tag_mask": tag_mask, "diff_code": diff_code, "diff_to_code": diff_to_code,
        }
        return _state


def _rank(st: dict, cand_idx: np.ndarray, vecs: np.ndarray, q_mask: int,
         q_diffc: int, limit: int) -> list[int]:
    """cand_idx 안에서 하이브리드 점수(벡터 60% + 기법태그 25% + 난이도 15%)
    상위 limit개의 cand_idx 내 위치(인덱스)를 점수 내림차순으로 반환."""
    masks = st["tag_mask"][cand_idx]
    inter = _POPCOUNT8[masks & q_mask]
    union = _POPCOUNT8[masks | q_mask]
    tag_sim = inter / np.maximum(union, 1)
    diff_match = (st["diff_code"][cand_idx] == q_diffc).astype(np.float32)

    score = 0.6 * vecs + 0.25 * tag_sim + 0.15 * diff_match
    k = min(limit, score.shape[0])
    top = np.argpartition(-score, k - 1)[:k]
    return list(top[np.argsort(-score[top])])


@lru_cache(maxsize=4096)
def _similar_by_index(qi: int, limit: int) -> tuple[tuple[str, int, float], ...]:
    """인덱스에 있는 문항(가장 흔한 경로) — 결과가 불변이라 캐싱 가능."""
    st = _load()
    chapter = st["meta"][qi]["chapter"]
    cand_idx = st["by_chapter"].get(chapter)
    if cand_idx is None or cand_idx.size == 0:
        return ()
    cand_idx = cand_idx[cand_idx != qi]
    if cand_idx.size == 0:
        return ()

    q_vec = st["emb"][qi]
    q_mask = int(st["tag_mask"][qi])
    q_diffc = int(st["diff_code"][qi])
    vecs = st["emb"][cand_idx] @ q_vec

    out = []
    for t in _rank(st, cand_idx, vecs, q_mask, q_diffc, limit):
        j = int(cand_idx[t])
        m = st["meta"][j]
        out.append((m["file_source"], m["question_number"], 0.0))
    # 점수는 UI 에 안 쓰여서 0.0 으로 채운다(아래 _rank 가 이미 정렬 끝냄).
    return tuple(out)


def _similar_fallback(chapter: str, difficulty: str | None, question_text: str,
                      limit: int) -> list[tuple[str, int, float]]:
    """인덱스에 없는 문항(새로 추가된 문항 등) — 벡터 없이 태그·난이도만.
    흔치 않은 경로라 캐싱하지 않는다."""
    st = _load()
    cand_idx = st["by_chapter"].get(chapter)
    if cand_idx is None or cand_idx.size == 0:
        return []
    q_mask = _mask_from_tags(tagset(question_text))
    q_diffc = st["diff_to_code"].get(difficulty, -1)
    vecs = np.zeros(cand_idx.shape[0], dtype=np.float32)

    out = []
    for t in _rank(st, cand_idx, vecs, q_mask, q_diffc, limit):
        j = int(cand_idx[t])
        m = st["meta"][j]
        out.append((m["file_source"], m["question_number"], 0.0))
    return out


def similar_natural_keys(
    file_source: str, question_number: int, chapter: str,
    difficulty: str | None, question_text: str, limit: int = 5,
) -> list[tuple[str, int, float]]:
    """같은 단원(chapter) 안에서 하이브리드 점수 상위 limit개의
    (file_source, question_number, score)."""
    st = _load()
    qi = st["by_key"].get((file_source, question_number))
    if qi is not None:
        return list(_similar_by_index(qi, limit))
    return _similar_fallback(chapter, difficulty, question_text, limit)
