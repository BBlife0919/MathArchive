"""전체 문항 벡터 유사도 인덱스 생성 (유사문항 추천용, 비용 $0 — 전부 로컬 연산).

DB question_text 를 로컬 임베딩 모델(sentence-transformers)로 벡터화하고,
난이도·기법 키워드 태그를 같이 뽑아서 저장한다. 매칭 시(쿼리 타임)
"같은 단원" 하드필터 + 벡터유사도/난이도일치/태그겹침 가중합 점수로 랭킹한다
(scripts/label_types.py 의 LLM 유형분류와는 완전히 별개 경로 — 둘 다 유지하며
비교·보완 가능).

산출물(DB 무관, 이관 가능한 파일 — 범용성 원칙):
    output/similarity_index/embeddings.npy   (N x 384 float32)
    output/similarity_index/meta.jsonl        (qid, chapter, difficulty, tags)

사용:
    python3 scripts/build_similarity_index.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "mathdb.sqlite"
OUT_DIR = ROOT / "output" / "similarity_index"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

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


def clean(text: str) -> str:
    t = re.sub(r"<<IMG:[^>]*>>", " ", text or "")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def tagset(text: str) -> list[str]:
    return sorted(name for name, pat in TAGS.items() if re.search(pat, text))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT question_id, question_text, chapter, difficulty, "
        "file_source, question_number "
        "FROM questions WHERE question_text IS NOT NULL").fetchall()
    con.close()
    print(f"대상 문항수: {len(rows):,}")

    texts = [clean(r[1]) for r in rows]
    # file_source+question_number(자연키) — 운영 Postgres 는 question_id 가
    # 로컬과 다를 수 있어(이관 드리프트, label_types.py write_store() 와 동일
    # 이유) backend/app/services/similarity_service.py 가 이 자연키로 매칭한다.
    meta = [{"qid": r[0], "chapter": r[2], "difficulty": r[3] or "?",
             "tags": tagset(t), "file_source": r[4], "question_number": r[5]}
            for r, t in zip(rows, texts)]

    print("모델 로딩중...")
    t0 = time.time()
    model = SentenceTransformer(MODEL_NAME)
    print(f"  로딩 {time.time()-t0:.1f}초")

    print("임베딩 생성중...")
    t0 = time.time()
    emb = model.encode(texts, show_progress_bar=True, normalize_embeddings=True,
                       batch_size=128)
    print(f"  임베딩 {len(texts):,}건 {time.time()-t0:.1f}초, 차원 {emb.shape}")

    np.save(OUT_DIR / "embeddings.npy", emb.astype("float32"))
    with (OUT_DIR / "meta.jsonl").open("w", encoding="utf-8") as f:
        for m in meta:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    (OUT_DIR / "README.txt").write_text(
        f"모델: {MODEL_NAME}\n생성: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"문항수: {len(rows):,}\n"
        "embeddings.npy[i] 와 meta.jsonl 의 i번째 줄이 1:1 대응.\n"
        "매칭 시 같은 chapter 로 먼저 필터링 후 벡터/난이도/태그 가중합으로 랭킹.\n",
        encoding="utf-8")
    print(f"저장 완료 → {OUT_DIR}")


if __name__ == "__main__":
    main()
