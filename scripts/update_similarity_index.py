"""유사문항 벡터 인덱스를 새로 추가된 문항만 증분 갱신한다 (비용 $0).

build_similarity_index.py 는 전체 17만 문항을 매번 다시 임베딩한다(약
15~20분). 배치 하나(/파서) 적재할 때마다 늘어나는 건 보통 수십~수천 건뿐이라,
이미 인덱싱된 question_id 는 건너뛰고 새로 생긴 것만 임베딩해 기존
embeddings.npy/meta.jsonl 에 이어붙인다 — 보통 몇 초~몇 분이면 끝난다.

/파서 로 새 배치를 적재·sync 한 뒤 이어서 돌리는 걸 표준 순서로 삼는다
(feedback_batch_sync_always_together.md 와 같은 맥락 — "적재는 항상 후속
작업까지").

사용:
    python3 scripts/update_similarity_index.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_similarity_index import DB, MODEL_NAME, OUT_DIR, clean, tagset  # noqa: E402


def main() -> None:
    emb_path = OUT_DIR / "embeddings.npy"
    meta_path = OUT_DIR / "meta.jsonl"
    if not emb_path.exists() or not meta_path.exists():
        raise SystemExit(
            f"{OUT_DIR} 에 기존 인덱스가 없습니다 — 처음 한 번은 "
            "build_similarity_index.py 로 전체 생성부터 하십시오.")

    old_meta = [json.loads(line) for line in meta_path.open(encoding="utf-8")]
    old_qids = {m["qid"] for m in old_meta}
    print(f"기존 인덱스: {len(old_meta):,}건")

    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT question_id, question_text, chapter, difficulty, "
        "file_source, question_number "
        "FROM questions WHERE question_text IS NOT NULL").fetchall()
    con.close()

    new_rows = [r for r in rows if r[0] not in old_qids]
    print(f"DB 전체: {len(rows):,}건 · 새로 추가된 문항: {len(new_rows):,}건")
    if not new_rows:
        print("새로 추가된 문항이 없습니다 — 할 일 없음.")
        return

    texts = [clean(r[1]) for r in new_rows]
    new_meta = [{"qid": r[0], "chapter": r[2], "difficulty": r[3] or "?",
                 "tags": tagset(t), "file_source": r[4], "question_number": r[5]}
                for r, t in zip(new_rows, texts)]

    print("모델 로딩중...")
    t0 = time.time()
    model = SentenceTransformer(MODEL_NAME)
    print(f"  로딩 {time.time()-t0:.1f}초")

    print(f"{len(texts):,}건 임베딩중...")
    t0 = time.time()
    new_emb = model.encode(texts, show_progress_bar=True, normalize_embeddings=True,
                           batch_size=128).astype("float32")
    print(f"  임베딩 {time.time()-t0:.1f}초")

    old_emb = np.load(emb_path)
    combined_emb = np.vstack([old_emb, new_emb])
    np.save(emb_path, combined_emb)

    with meta_path.open("a", encoding="utf-8") as f:
        for m in new_meta:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    total = len(old_meta) + len(new_meta)
    (OUT_DIR / "README.txt").write_text(
        f"모델: {MODEL_NAME}\n증분갱신: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"문항수: {total:,} (이번에 +{len(new_meta):,})\n"
        "embeddings.npy[i] 와 meta.jsonl 의 i번째 줄이 1:1 대응.\n"
        "매칭 시 같은 chapter 로 먼저 필터링 후 벡터/난이도/태그 가중합으로 랭킹.\n",
        encoding="utf-8")
    print(f"갱신 완료 → 총 {total:,}건 (+{len(new_meta):,})")
    print("백엔드가 떠 있다면 재시작해야 새 인덱스를 읽습니다"
          "(similarity_service 가 프로세스 생명주기 동안 메모리에 캐싱).")


if __name__ == "__main__":
    main()
