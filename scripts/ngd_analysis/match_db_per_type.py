"""
유형별 MathDB 대표 문제 매칭.

입력: type_taxonomy.json (+ 추가 new_types), consensus_labels.json
출력: per_type_candidates.json — 각 유형별 대표 1문항 (+ 대안 후보 3개)

전략:
1. 유형별 키워드 패턴(REGEX) 정의 (cue 기반 + 문항 본문 구조 예측)
2. MathDB의 chapter 필터 + difficulty 필터 + 키워드 포함 AND NOT 제외어
3. 문항 길이(너무 짧거나 너무 긴 것 제외) + 선택지 5개 보유 + has_image=0 선호
4. 점수 높은 순으로 정렬, 상위 1 + 대안 3
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

DB = "/Users/youngwoolee/MathDB/db/mathdb.sqlite"
NGD = Path("/Users/youngwoolee/MathDB/scripts/ngd_analysis")

# 유형별 매칭 규칙: (positive_keywords (OR), negative_keywords (NOT))
# 키워드는 정규식 허용, 주로 한국어 문장체 인식
RULES = {
    "P1": {  # 다항식 덧뺄·스칼라배
        "pos": [r"두\s*다항식.*(A|\$A\$).*(B|\$B\$)", r"(A|\$A\$)\s*[\-\+]\s*\d*(B|\$B\$)"],
        "neg": [r"나누었", r"나눗셈", r"조립제법"],
    },
    "P2": {
        "pos": [r"전개", r"\(a\s*\+\s*b\)\^?2", r"곱셈공식"],
        "neg": [r"인수분해"],
    },
    "P3": {
        "pos": [r"a\+b", r"ab", r"a\^?2\s*\+\s*b\^?2", r"(a-b)\^?2"],
        "neg": [],
    },
    "P4": {
        "pos": [r"a\^?3", r"세제곱", r"\(a[\+\-]b\)\^?3"],
        "neg": [],
    },
    "P5": {
        "pos": [r"999|101|998|\d{3,}", r"곱셈공식.*이용"],
        "neg": [],
    },
    "P6": {
        "pos": [r"나누었.*나머지", r"몫.*나머지"],
        "neg": [r"조립제법"],
    },
    "P7": {
        "pos": [r"조립제법.*과정", r"조립제법.*빈", r"조립제법"],
        "neg": [],
    },
    "P8": {
        "pos": [r"조립제법.*몫", r"x-\w.*나누"],
        "neg": [r"빈칸"],
    },
    "H1": {
        "pos": [r"항등식.*계수", r"에 대한 항등식"],
        "neg": [r"수치"],
    },
    "H2": {
        "pos": [r"대입", r"x=0.*x=1"],
        "neg": [],
    },
    "H3": {
        "pos": [r"나머지정리", r"x\s*-\s*\d+.*나누었을.*나머지", r"x\s*\+\s*\d+.*나누었을.*나머지"],
        "neg": [r"조립제법", r"로 나누었을.*로 나누었", r"\(x[\+\-].*\)\(x[\+\-].*\)로 나누"],
    },
    "H4": {
        "pos": [r"로 나누었을.*로 나누었을", r"나누었을.*나머지.*나누었을.*나머지", r"\(x[\+\-].*\)\(x[\+\-].*\)로 나누었을"],
        "neg": [],
    },
    "H5": {
        "pos": [r"인수정리", r"인수.*x-\w", r"P\(\w\)\s*=\s*0"],
        "neg": [],
    },
    "F1": {
        "pos": [r"인수분해하면", r"인수분해.*간단", r"\(.*\)\^?2.*\-.*\(.*\)\^?2", r"a\^3\s*[\+\-]\s*b\^3"],
        "neg": [r"복이차", r"고차", r"조립제법", r"x\^4", r"x\^\{4\}", r"사차", r"Q\(x\)"],
    },
    "F2": {
        "pos": [r"공통인수", r"치환.*인수분해"],
        "neg": [],
    },
    "F3": {
        "pos": [r"복이차", r"x\^?4.*x\^?2"],
        "neg": [],
    },
    "F4": {
        "pos": [r"조립제법.*인수분해", r"삼차식.*인수분해"],
        "neg": [],
    },
    "F5": {
        "pos": [r"인수분해.*이용", r"계산.*값"],
        "neg": [],
    },
    "C1": {
        "pos": [r"i\^", r"i의 거듭제곱"],
        "neg": [r"합", r"\\cdots"],
    },
    "C2": {
        "pos": [r"i\+i\^?\{?2", r"i의.*합", r"\\cdots.*i\^", r"f\(n\)\s*=\s*i", r"i\^\{?n"],
        "neg": [r"\\frac\{.*i\}\{.*i\}"],
    },
    "C3": {
        "pos": [r"분모.*실수화", r"\(.*\)\s*\/\s*\(", r"유리화"],
        "neg": [],
    },
    "C4": {
        "pos": [r"복소수.*상등", r"실수부.*허수부", r"실수\s*a.*b"],
        "neg": [],
    },
    "C5": {
        "pos": [r"켤레복소수", r"\\overline", r"z.*켤레"],
        "neg": [],
    },
    "C6": {
        "pos": [r"\\sqrt\{\s*-", r"음수.*제곱근"],
        "neg": [],
    },
    "Q1": {
        "pos": [r"이차방정식.*풀이", r"근을 구"],
        "neg": [r"판별식", r"근과 계수"],
    },
    "Q2": {
        "pos": [r"판별식", r"실근.*허근.*중근"],
        "neg": [r"범위"],
    },
    "Q3": {
        "pos": [r"판별식.*범위", r"실근.*\w의 범위"],
        "neg": [],
    },
    "Q4": {
        "pos": [r"근과 계수", r"두 근.*\\alpha.*\\beta"],
        "neg": [r"\\alpha\^?2\s*\+\s*\\beta\^?2", r"1\/\\alpha"],
    },
    "Q5": {
        "pos": [r"\\alpha\^?2\s*\+\s*\\beta\^?2", r"1\/\\alpha\s*\+\s*1\/\\beta", r"\\alpha\^?3\s*\+\s*\\beta\^?3"],
        "neg": [],
    },
    "Q6": {
        "pos": [r"두 근.*이차방정식을"],
        "neg": [],
    },
    "Q7": {
        "pos": [r"공통근"],
        "neg": [],
    },
    "Q8": {
        "pos": [r"허근", r"켤레근"],
        "neg": [],
    },
    "Q9": {
        "pos": [r"<보기>.*실근", r"<보기>.*이차방정식"],
        "neg": [],
    },
    "Y1": {
        "pos": [r"표준형", r"y=a\(x-p\)"],
        "neg": [],
    },
    "Y2": {
        "pos": [r"꼭짓점", r"축의 방정식"],
        "neg": [],
    },
    "Y3": {
        "pos": [r"꼭짓점.*최댓값", r"꼭짓점.*최솟값", r"의 최솟값은?", r"의 최댓값은?", r"이차함수.*최.*값.*얼마", r"최솟값.*구하"],
        "neg": [r"\\leq\s*x\s*\\leq", r"범위.*최", r"정의역", r"\d+\s*\\leq", r"x축.*만나", r"\(.*,.*0\)"],
    },
    "Y4": {
        "pos": [r"\\leq\s*x\s*\\leq", r"제한.*정의역", r"\d+\s*\\leq\s*x\s*\\leq\s*\d+"],
        "neg": [r"k\\leq"],
    },
    "Y5": {
        "pos": [r"k\\leq\s*x\s*\\leq\s*k\+1", r"함수.*정의역이.*k"],
        "neg": [],
    },
    "Y6": {
        "pos": [r"x축.*만나지 않", r"x축과.*교점"],
        "neg": [],
    },
    "Y7": {
        "pos": [r"이차함수.*직선", r"교점.*직선"],
        "neg": [],
    },
    "Y8": {
        "pos": [r"평행이동", r"x축의 방향으로.*y축의 방향으로"],
        "neg": [],
    },
    "Y9": {
        "pos": [r"세 점.*지나는", r"두 점.*지나.*이차함수", r"꼭짓점.*\(.*,.*\).*지나", r"이차함수.*축.*방정식.*지나"],
        "neg": [r"직선.*만나", r"x축과", r"위치", r"관계없이"],
    },
    "Y10": {
        "pos": [r"삼각형.*넓이", r"사각형.*넓이"],
        "neg": [],
    },
    "Y11": {
        "pos": [r"관계없이.*지나", r"상수.*k.*지나", r"항상 지나"],
        "neg": [],
    },
}

TYPE_TO_CHAPTER = {
    "P": "다항식의 연산",
    "H": "항등식과 나머지정리",
    "F": "인수분해",
    "C": "복소수",
    "Q": "이차방정식",
    "Y": "이차함수",
}


def score(qtext: str, rule: dict) -> int:
    s = 0
    for p in rule.get("pos", []):
        if re.search(p, qtext, re.IGNORECASE):
            s += 2
    for n in rule.get("neg", []):
        if re.search(n, qtext, re.IGNORECASE):
            s -= 3
    return s


def fetch_pool(con, chapter: str, difficulty: str) -> list[dict]:
    cur = con.execute(
        """
        SELECT question_id, question_text, choices, answer, school, year, chapter, difficulty, has_image
        FROM questions
        WHERE chapter = ? AND difficulty = ?
          AND question_text IS NOT NULL
          AND length(question_text) BETWEEN 40 AND 600
        """,
        (chapter, difficulty),
    )
    return [dict(zip([c[0] for c in cur.description], row)) for row in cur.fetchall()]


def rank_for_type(pool: list[dict], rule: dict, prefer_no_image=True) -> list[dict]:
    scored = []
    for q in pool:
        qt = q["question_text"]
        # 파서 원시 마커 노출되는 문항은 제외
        if "<<BOX_" in qt or "<<TABLE" in qt or "<<IMG" in qt:
            continue
        # 그림/표가 본질적인데 has_image=0인 경우 '그림과 같이' 포함 문항도 리스크
        if q.get("has_image") and prefer_no_image:
            # 이미지 있으면 깊은 페널티
            continue
        s = score(qt, rule)
        # 선택지 5개 + 정답 있으면 가산점
        try:
            chs = json.loads(q["choices"]) if q["choices"] else []
        except Exception:
            chs = []
        if len(chs) == 5:
            s += 2
        if q.get("answer"):
            s += 1
        # 본문 길이: 너무 짧거나(50자 미만) 너무 길면 페널티
        lt = len(qt)
        if lt < 60:
            s -= 1
        elif lt > 350:
            s -= 1
        else:
            s += 1
        # 그림/표 의존 문구 페널티
        if any(k in qt for k in ["그림과 같이", "다음은", "위의 표", "다음 표", "오른쪽 그림"]):
            s -= 2
        if s > 0:
            scored.append((s, q))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [q for _, q in scored[:4]]


def main(difficulty: str) -> None:
    consensus = json.load(open(NGD / "consensus_labels.json"))
    taxonomy = json.load(open(NGD / "type_taxonomy.json"))

    # 유형별 빈도
    from collections import Counter
    bundle = json.load(open(NGD / "label_bundle.json"))
    freq = Counter()
    for lbl in consensus:
        it = bundle[lbl["idx"]]
        if it["difficulty"] == difficulty and lbl.get("type_id", "UNKNOWN") != "UNKNOWN":
            freq[lbl["type_id"]] += 1

    # 전체 유형 dict
    type_info = {}
    for chap, types in taxonomy["types"].items():
        for t in types:
            type_info[t["id"]] = {**t, "chapter": chap}

    con = sqlite3.connect(DB)

    results = []
    for tid, cnt in freq.most_common():
        info = type_info.get(tid)
        if not info:
            continue
        chapter = info["chapter"]
        # 매칭 풀: 해당 chapter의 해당 난이도 문항
        pool = fetch_pool(con, chapter, difficulty)
        rule = RULES.get(tid, {"pos": [info.get("cue", "")], "neg": []})
        ranked = rank_for_type(pool, rule)
        if not ranked:
            # 풀이 너무 좁다면 상위 난이도도 섞어서
            pool2 = fetch_pool(con, chapter, "중" if difficulty == "하" else "하")
            ranked = rank_for_type(pool2, rule)[:2]
        results.append(
            {
                "tid": tid,
                "label": info["label"],
                "chapter": chapter,
                "cue": info.get("cue", ""),
                "ngd_count": cnt,
                "stars": 3 if cnt >= 10 else (2 if cnt >= 5 else 1),
                "candidates": ranked,
            }
        )

    out = NGD / f"per_type_candidates_{difficulty}.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    print(f"wrote {out} — {len(results)} types with candidates")


if __name__ == "__main__":
    import sys

    diff = sys.argv[1] if len(sys.argv) > 1 else "하"
    main(diff)
