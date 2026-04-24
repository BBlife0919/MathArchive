"""
A, B 두 라벨링 결과를 합쳐 consensus_labels.json 생성.

정책:
- 두 라벨이 같으면 그대로 사용
- 다르면 confidence 높은 쪽 채택 (high > medium > low)
- 둘 다 같은 confidence면 A 우선
- 둘 중 하나가 UNKNOWN이면 다른 쪽 채택
"""

import json
from collections import Counter
from pathlib import Path

NGD = Path("/Users/youngwoolee/MathDB/scripts/ngd_analysis")
CONF_RANK = {"high": 3, "medium": 2, "low": 1, None: 0}


def main() -> None:
    a = json.load(open(NGD / "labels_A.json"))
    b = json.load(open(NGD / "labels_B.json"))
    a_map = {l["idx"]: l for l in a["labels"]}
    b_map = {l["idx"]: l for l in b["labels"]}

    bundle = json.load(open(NGD / "label_bundle.json"))
    consensus = []
    agree = 0
    disagree = 0
    details = []
    for it in bundle:
        i = it["idx"]
        la = a_map.get(i, {})
        lb = b_map.get(i, {})
        ta, tb = la.get("type_id"), lb.get("type_id")
        ca, cb = la.get("confidence"), lb.get("confidence")

        if ta == tb:
            chosen = ta
            conf = ca if CONF_RANK[ca] >= CONF_RANK[cb] else cb
            agree += 1
        else:
            disagree += 1
            # UNKNOWN 처리
            if ta == "UNKNOWN" and tb != "UNKNOWN":
                chosen = tb
                conf = cb
            elif tb == "UNKNOWN" and ta != "UNKNOWN":
                chosen = ta
                conf = ca
            else:
                # confidence 비교
                if CONF_RANK[ca] > CONF_RANK[cb]:
                    chosen, conf = ta, ca
                elif CONF_RANK[cb] > CONF_RANK[ca]:
                    chosen, conf = tb, cb
                else:
                    chosen, conf = ta, ca  # 타이브레이커: A 우선
            details.append(
                {
                    "idx": i,
                    "chapter": it["chapter"],
                    "difficulty": it["difficulty"],
                    "A": ta, "B": tb,
                    "chosen": chosen,
                    "prose": it["prose"][:120],
                }
            )

        consensus.append({"idx": i, "type_id": chosen, "confidence": conf, "A": ta, "B": tb})

    (NGD / "consensus_labels.json").write_text(
        json.dumps(consensus, ensure_ascii=False, indent=2)
    )
    (NGD / "disagreements.json").write_text(
        json.dumps(details, ensure_ascii=False, indent=2)
    )

    print(f"agree: {agree} / 325 ({agree*100//325}%)")
    print(f"disagree: {disagree} / 325 ({disagree*100//325}%)")

    # 유형별 카운트 (중/하 별도)
    print("\n=== 중 난이도 유형 분포 ===")
    c_m = Counter()
    for lbl in consensus:
        it = bundle[lbl["idx"]]
        if it["difficulty"] == "중":
            c_m[lbl["type_id"]] += 1
    for tid, n in c_m.most_common():
        print(f"  {tid}: {n}")
    print(f"  [중 소계] {sum(c_m.values())}")

    print("\n=== 하 난이도 유형 분포 ===")
    c_h = Counter()
    for lbl in consensus:
        it = bundle[lbl["idx"]]
        if it["difficulty"] == "하":
            c_h[lbl["type_id"]] += 1
    for tid, n in c_h.most_common():
        print(f"  {tid}: {n}")
    print(f"  [하 소계] {sum(c_h.values())}")


if __name__ == "__main__":
    main()
