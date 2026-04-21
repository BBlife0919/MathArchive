"""
ko-SBERT 임베딩 + HDBSCAN 클러스터링으로 유형 후보 자동 추출.

정책:
- "다항식의 연산"은 소분류 없이 단일 유형으로 묶는다(사용자 지시).
- 나머지 5개 단원은 단원 내부에서 HDBSCAN으로 클러스터 → 유형 후보.
- 각 클러스터에 Kiwi 기반 대표 키워드로 자동 라벨 생성.
- 노이즈(-1) 클러스터는 "기타"로 둠.

입력: output/crops/index_typed.json (plain_text 필드 포함)
출력: output/crops/index_clustered.json (type 필드 갱신)
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import hdbscan
import numpy as np
from kiwipiepy import Kiwi
from sentence_transformers import SentenceTransformer

IN_PATH = Path("output/crops/index_typed.json")
OUT_PATH = Path("output/crops/index_clustered.json")

SINGLE_TYPE_CHAPTERS = {"다항식의 연산"}
CHAPTER_ORDER = [
    "다항식의 연산",
    "항등식과 나머지정리",
    "인수분해",
    "복소수",
    "이차방정식",
    "이차함수",
]

# 클러스터링 파라미터: 표본 크기에 비례해 조정
def min_cluster_size(n: int) -> int:
    return max(10, n // 60)


STOPWORDS = {
    "문제", "다음", "값", "구하", "구하시오", "것", "때", "대하여", "이다", "있다", "같다",
    "위한", "모든", "실수", "정수", "자연수", "경우", "합", "곱", "차", "몫",
    "표시", "제작", "제작연월일", "콘텐츠", "콘텐츠산업", "진흥법", "시행령", "수학적실험실",
    "네이버", "카페", "일", "년", "월", "점", "학기", "중간", "기말", "고등학교", "공통수학",
    "보호됩니다", "배포", "무단", "복제", "법적", "책임", "오프라인", "온라인", "유포",
    "자료", "저작물", "이음", "이영우",
}

PUA_RE = re.compile(r"[\uE000-\uF8FF]+")
DIGIT_RE = re.compile(r"\d+")


def extract_keywords(kiwi: Kiwi, texts: list[str], topk: int = 3) -> list[str]:
    """Kiwi로 명사만 뽑아 빈도 상위 topk 반환."""
    cnt: Counter = Counter()
    for t in texts:
        t = PUA_RE.sub(" ", t)
        t = DIGIT_RE.sub(" ", t)
        try:
            tokens = kiwi.tokenize(t[:400])
        except Exception:
            continue
        for tk in tokens:
            if tk.tag in ("NNG", "NNP") and len(tk.form) >= 2:
                if tk.form in STOPWORDS:
                    continue
                cnt[tk.form] += 1
    return [w for w, _ in cnt.most_common(topk)]


def main() -> None:
    data = json.loads(IN_PATH.read_text(encoding="utf-8"))
    print(f"로드: {len(data)}개 레코드")

    # 유효 레코드만
    records = [r for r in data if not r.get("skipped_reason") and not r.get("error") and r.get("plain_text")]
    print(f"유효(plain_text 있음): {len(records)}개")

    # 단원별 버킷
    by_chapter: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_chapter[r["chapter"]].append(r)

    print("단원별 수:")
    for chap in CHAPTER_ORDER:
        print(f"  {chap}: {len(by_chapter[chap])}")

    # 임베딩 모델 (공통)
    model = SentenceTransformer("jhgan/ko-sroberta-multitask")
    kiwi = Kiwi()

    # 각 문제의 임베딩 입력 텍스트 구성: PUA 제거 + 앞 500자
    def build_input(r: dict) -> str:
        t = PUA_RE.sub(" ", r.get("plain_text", ""))
        t = re.sub(r"\s+", " ", t).strip()
        return t[:500]

    for chap in CHAPTER_ORDER:
        chap_records = by_chapter[chap]
        if not chap_records:
            continue
        if chap in SINGLE_TYPE_CHAPTERS:
            for r in chap_records:
                r["type"] = chap  # 통째로 하나의 유형
            print(f"\n▶ {chap}: 단일 유형({len(chap_records)}문항)으로 통합")
            continue

        inputs = [build_input(r) for r in chap_records]
        print(f"\n▶ {chap}: 임베딩 {len(inputs)}개 계산 중...")
        emb = model.encode(inputs, batch_size=64, show_progress_bar=False, convert_to_numpy=True)

        # HDBSCAN 클러스터링 (코사인 → 각도 거리로 변환을 피하기 위해 L2 정규화 후 euclidean 사용)
        norms = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9
        emb_n = emb / norms
        mcs = min_cluster_size(len(inputs))
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=mcs,
            min_samples=3,
            metric="euclidean",
            cluster_selection_method="leaf",
        )
        labels = clusterer.fit_predict(emb_n)
        unique = sorted(set(labels))
        print(f"  min_cluster_size={mcs}, 클러스터 수: {len([u for u in unique if u != -1])} (+노이즈 {list(labels).count(-1)})")

        # 클러스터별 키워드 추출해 라벨 만들기
        label_names: dict[int, str] = {}
        for cid in unique:
            texts_in = [inputs[i] for i, l in enumerate(labels) if l == cid]
            if cid == -1:
                label_names[cid] = f"{chap} · 기타"
                continue
            kws = extract_keywords(kiwi, texts_in, topk=3)
            name = " · ".join(kws) if kws else f"유형{cid}"
            label_names[cid] = f"{chap} · {name}"

        # 레코드에 라벨 부여
        for r, l in zip(chap_records, labels):
            r["type"] = label_names[l]
            r["cluster_id"] = int(l)

    # 저장
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n저장: {OUT_PATH}")

    # 요약: 단원 × 유형 분포
    print("\n=== 단원 × 유형 분포 ===")
    type_counter: Counter = Counter()
    for r in data:
        if r.get("type"):
            type_counter[(r["chapter"], r["type"])] += 1
    for chap in CHAPTER_ORDER:
        print(f"\n▶ {chap}")
        items = [(t, c) for (ch, t), c in type_counter.items() if ch == chap]
        for name, cnt in sorted(items, key=lambda x: -x[1]):
            print(f"    {name}: {cnt}")


if __name__ == "__main__":
    main()
