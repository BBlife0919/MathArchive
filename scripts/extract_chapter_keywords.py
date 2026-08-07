#!/usr/bin/env python3
"""단원별 차별 키워드/구문 추출.

각 단원의 문항 텍스트에서 (1) 그 단원에 자주 나오면서 (2) 다른 단원에는
잘 안 나오는 한국어 구문을 찾는다. TF-IDF 의 단순 변형 — chapter score:

    score(token, chapter) = freq_in_chapter × log(n_chapters / n_chapters_with_token)

수식 ($...$) 과 일반 stopword 는 제거. 한국어 어절·2~3 어절 묶음을 본다.
"""
from __future__ import annotations

import argparse
import math
import re
import sqlite3
from collections import Counter, defaultdict

CHAPTERS = [
    "다항식의 연산",
    "항등식과 나머지정리",
    "인수분해",
    "복소수",
    "이차방정식",
    "이차함수",
]

# 일반 한국어/시험문항 stopword
STOP = {
    "이", "그", "저", "것", "수", "때", "값", "값은", "값을", "값의", "옳은",
    "다음", "있는", "있다", "있을", "이다", "이고", "이라", "이라고",
    "구하시오", "구하면", "구할", "구하라", "옳게", "구한", "구하기",
    "또는", "그리고", "에서", "에게", "에서의", "이며", "라고", "라하자",
    "관하여", "대하여", "대한", "대해", "위하여", "위해", "그러나", "또한",
    "각각", "모두", "모든", "어떤", "임의의", "한", "두", "세", "네",
    "할", "할때", "구해보자", "한다", "라", "하자", "하면", "한다고",
    "옳지", "않은", "맞는", "틀린", "포함하는", "고른", "들어갈",
    "관계없이", "대하여",
    "보기", "조건", "참고", "단", "예", "예를", "들어",
    "중에서", "중에", "중", "사이",
    "다음을", "다음과", "다음의", "물음에", "답하시오",
    "이때", "그때", "이를",
    "여기서", "여기",
    "먼저", "동시", "주어진", "주어졌을",
    "표현하면", "정리하면", "나타내면",
    "선분", "점", "그림", "그림과", "그림에서",
    "ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ", "ㅇ",
    # 단위·점수
    "점", "점이다", "점에서", "점이",
    # 흔한 동사/형용사 변형
    "구하는", "갖는", "가지는", "가질", "가지고", "갖도록", "갖는다",
    "되는", "되도록", "되고", "되어", "된다", "되었을",
    "만나는", "만난다", "만나도록",
    "나타낸", "나타낸다",
    "성립", "성립할", "성립하는", "성립한다",
    "오는", "오도록",
}


def clean_text(s: str) -> str:
    """수식/마커/특수문자 제거, 어절 단위 한국어만 남김."""
    if not s:
        return ""
    s = re.sub(r"\$[^$]*\$", " ", s)
    s = re.sub(r"<<[^>]+>>", " ", s)
    s = re.sub(r"\|[-]+\|", " ", s)
    s = re.sub(r"\|", " ", s)
    s = re.sub(r"[<>\[\]{}()①②③④⑤⑥⑦⑧⑨]", " ", s)
    s = re.sub(r"\d+\.\d+", " ", s)  # 점수
    s = re.sub(r"[a-zA-Z\d]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def tokens(s: str) -> list:
    """1~3 어절 묶음을 토큰으로. 길이 ≥ 2 한글만."""
    words = [w for w in s.split() if len(w) >= 2 and re.search(r"[가-힣]", w)]
    out = []
    for w in words:
        if w not in STOP and len(w) <= 8:
            out.append(w)
    # 2-gram, 3-gram
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i:i + n])
            if any(w in STOP for w in words[i:i + n]):
                continue
            if any(len(w) < 2 for w in words[i:i + n]):
                continue
            if len(phrase) > 25:
                continue
            out.append(phrase)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/mathdb.sqlite")
    ap.add_argument("--top", type=int, default=40,
                    help="단원당 상위 N개 키워드")
    ap.add_argument("--min-freq", type=int, default=10,
                    help="단원 내 최소 등장 횟수")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    # 단원별 토큰 수집
    chapter_tokens: dict[str, Counter] = defaultdict(Counter)
    chapter_total: dict[str, int] = defaultdict(int)
    for ch in CHAPTERS:
        rows = cur.execute(
            "SELECT question_text FROM questions WHERE chapter=?",
            (ch,),
        ).fetchall()
        for (txt,) in rows:
            cleaned = clean_text(txt or "")
            for t in tokens(cleaned):
                chapter_tokens[ch][t] += 1
            chapter_total[ch] += 1
        print(f"  [{ch}] 문항 {chapter_total[ch]}, 고유토큰 {len(chapter_tokens[ch])}")

    # 토큰별 등장 단원 수
    n_chapters_with: Counter = Counter()
    for ch, cnt in chapter_tokens.items():
        for t in cnt:
            n_chapters_with[t] += 1

    n_total = len(CHAPTERS)

    # 단원별 차별 점수
    print("\n" + "=" * 80)
    for ch in CHAPTERS:
        cnt = chapter_tokens[ch]
        scored = []
        for t, f in cnt.items():
            if f < args.min_freq:
                continue
            n_chap = n_chapters_with[t]
            # IDF: 적은 단원에 등장할수록 가중
            idf = math.log((n_total + 1) / (n_chap + 0.5))
            # 정규화 빈도 (해당 단원 문항 수 대비)
            tf = f / max(chapter_total[ch], 1)
            score = tf * idf * 1000
            scored.append((score, t, f, n_chap))
        scored.sort(reverse=True)

        print(f"\n## {ch}")
        print(f"{'점수':>5} {'빈도':>5} {'단원수':>4}  키워드")
        for s, t, f, nc in scored[:args.top]:
            print(f"{s:5.1f} {f:5d} {nc:4d}/{n_total}  {t}")


if __name__ == "__main__":
    main()
