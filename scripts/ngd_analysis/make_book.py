"""
유형 후보 → 교재 페이지 데이터 변환 → HTML/PDF.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from build_study_book import build as build_book, CHAPTER_ORDER

NGD = Path("/Users/youngwoolee/MathDB/scripts/ngd_analysis")
DB = "/Users/youngwoolee/MathDB/db/mathdb.sqlite"

# 각 유형의 체크포인트 (풀이 루틴 1~2줄)
CHECKPOINTS = {
    "P1": "두 다항식 A, B가 주어지면 동류항끼리 차수별로 정렬해서 덧뺄셈. 계수 앞의 음수 실수 처리만 주의하면 끝.",
    "P2": "곱셈공식은 외우는 게 아니라 '괄호 두 번 풀어서 동류항 묶기'. (a+b)², (a+b)(a-b), (a+b+c)² 세 개만 연습하면 80% 커버.",
    "P3": "a+b와 ab가 주어지면 a²+b²=(a+b)²-2ab 대입만. 곱셈공식의 '꺼꾸로 뒤집기'가 핵심.",
    "P4": "a³+b³=(a+b)(a²-ab+b²), (a+b)³=a³+3a²b+3ab²+b³. 세제곱은 전개보다 '공식 꺼내 쓰기'가 빠름.",
    "P5": "큰 수 계산은 100, 1000 같은 '정돈된 수'로 치환. 998×1002는 (1000-2)(1000+2)=1000²-4.",
    "P6": "다항식의 나눗셈은 '자연수 나눗셈과 같다'는 것만 기억. 몫·나머지는 나눗셈 원리 P = QD + R.",
    "P7": "조립제법 빈칸 문제는 가로 한 줄씩 계산. '내려오는 값 × 나누는 수 → 다음 칸 더하기' 리듬만 지키면 빈칸은 저절로.",
    "P8": "x-α로 나눈 몫·나머지는 조립제법이 제일 빠름. α로 한 줄 내려보내는 연습만.",
    "H1": "양변을 x의 거듭제곱 순서로 정리해 계수끼리 비교. 'x에 대한 항등식' 보이면 반사적으로 '계수 비교' 생각.",
    "H2": "양변 동일하게 되는 등식이면 x=0, 1, -1 등 '쉬운 수' 대입으로 연립. 계수비교보다 때론 더 빠름.",
    "H3": "P(x)를 x-α로 나눈 나머지는 P(α). 1차식 나누기는 무조건 '대입' 반사.",
    "H4": "P(x)를 (x-a)(x-b)로 나눈 나머지는 1차식 cx+d. P(a), P(b) 두 값을 아면 c, d 연립으로 구함.",
    "H5": "P(α)=0이면 x-α가 P(x)의 인수. 거꾸로 인수분해 전 α 후보부터 대입해서 0 찾기.",
    "F1": "공식 5개만 외우자: a²-b², a³±b³, (a±b)², (a±b)³, 완전세제곱. 나머지는 이 변형.",
    "F2": "같은 식 덩어리가 보이면 문자로 치환 (x²-2x = t). 치환 후 기본 인수분해 적용.",
    "F3": "x⁴+ax²+b → x²=t 치환. 치환 후 이차식 인수분해. 안되면 'x⁴+a = (x²+c)²-(dx)²' 꼴 의심.",
    "F4": "삼차식 이상은 인수정리로 1차 인수 찾은 뒤 조립제법. 정수근 후보는 상수항의 약수/최고차 계수 약수.",
    "F5": "숫자 계산은 먼저 '공통 문자'로 치환해 인수분해 꼴을 만든 뒤 수치 대입.",
    "C1": "i²=-1, i³=-i, i⁴=1. i^n은 n을 4로 나눈 나머지만 보면 즉결.",
    "C2": "i+i²+i³+i⁴=0. 4개씩 묶으면 0. 나머지만 계산.",
    "C3": "분모에 i 있으면 분자·분모에 켤레 곱해서 실수화. 결과는 a+bi 꼴로 정리.",
    "C4": "a+bi = c+di ⇔ a=c, b=d. 복소수 상등 문제는 결국 '두 실수 방정식 연립'.",
    "C5": "z=a+bi의 켤레는 ā=a-bi. z+ā=2a, z·ā=a²+b². 켤레 연산 3개만 외우면 대부분 풀림.",
    "C6": "a<0이면 √a = i√|a|. 음수의 제곱근 계산은 i 밖으로 빼낸 다음 실수 계산.",
    "Q1": "ax²+bx+c=0은 인수분해 먼저 시도, 안되면 근의 공식. 'ax²+bx+c=(x-α)(x-β)' 꼴 인식.",
    "Q2": "D=b²-4ac. D>0 서로 다른 두 실근 / D=0 중근 / D<0 두 허근. 이 세 줄만 반사.",
    "Q3": "판별식의 값이 아닌 '부호 조건'이 핵심. D>0, D=0, D<0 각각에 대한 k의 범위를 부등식/등식으로.",
    "Q4": "α+β = -b/a, αβ = c/a. 식이 어려워 보여도 결국 α+β와 αβ만 알면 됨.",
    "Q5": "α²+β² = (α+β)²-2αβ, 1/α+1/β = (α+β)/(αβ). 대칭식은 '기본량 두 개'로 환원.",
    "Q6": "α+β=s, αβ=p 이면 x²-sx+p=0. 두 근으로부터 이차식 만드는 공식.",
    "Q7": "두 방정식 공통근을 γ라 하고 두 식에 대입 → γ에 대한 연립 → γ의 값 구하고 원방정식 대입.",
    "Q8": "실계수 이차방정식의 허근은 반드시 켤레 쌍. α=p+qi면 ā=p-qi도 근.",
    "Q9": "각 이차방정식의 판별식 D로 실근 여부 판정. 보기 하나하나 D 계산.",
    "Y1": "y=ax²+bx+c의 x²와 x항을 묶어 완전제곱 만들기. y=a(x-p)²+q 꼴로 바꾸면 꼭짓점 (p, q).",
    "Y2": "표준형 y=a(x-p)²+q의 꼭짓점은 (p, q), 축은 x=p.",
    "Y3": "a>0: 꼭짓점에서 최솟값 / a<0: 꼭짓점에서 최댓값. 전체 실수 범위면 꼭짓점만 보면 끝.",
    "Y4": "제한된 정의역에서는 꼭짓점이 구간 안에 있는지 먼저 확인. 밖이면 양 끝점만 비교.",
    "Y5": "변수 k가 정의역에 있으면 k에 따라 케이스 분기. 꼭짓점 위치와 구간 위치 관계로 3~4경우.",
    "Y6": "판별식으로 x축과의 교점 개수 판정. 만나지 않음 ↔ D<0.",
    "Y7": "이차함수와 직선 연립 → 이차방정식 → 판별식 조건으로 교점 개수·위치.",
    "Y8": "y=f(x)를 x축 방향 p, y축 방향 q 평행이동 → y-q=f(x-p).",
    "Y9": "조건 3개면 꼭짓점 형태나 일반형에 미지수 대입해서 연립.",
    "Y10": "도형 한 변을 x로 놓고 넓이 S(x)를 x의 이차식으로 표현 → 제한된 정의역에서 최댓값.",
    "Y11": "식 정리하여 k로 묶기. k의 계수=0, k 빼고 남은 부분=0 → x, y 값 도출.",
}


def select_top_types(candidates: list[dict], limit: int = 25) -> list[dict]:
    """빈도 내림차순 + chapter별 최소 2개 보장."""
    # chapter별 그룹
    by_chap: dict[str, list] = {}
    for t in candidates:
        by_chap.setdefault(t["chapter"], []).append(t)
    for ch in by_chap:
        by_chap[ch].sort(key=lambda x: x["ngd_count"], reverse=True)

    # 각 chapter에서 상위 N개 강제 포함 (min 2)
    selected = []
    seen = set()
    min_per_chap = 2
    for ch in CHAPTER_ORDER:
        for t in by_chap.get(ch, [])[:min_per_chap]:
            selected.append(t)
            seen.add(t["tid"])

    # 나머지 슬롯은 전체 빈도순
    remaining = [t for t in sorted(candidates, key=lambda x: x["ngd_count"], reverse=True) if t["tid"] not in seen]
    while len(selected) < limit and remaining:
        selected.append(remaining.pop(0))

    # chapter 순서로 정렬 (교재 내 배치 순서)
    ch_order = {c: i for i, c in enumerate(CHAPTER_ORDER)}
    selected.sort(key=lambda t: (ch_order.get(t["chapter"], 99), -t["ngd_count"]))
    return selected


def build_type_page(type_entry: dict) -> dict | None:
    if not type_entry["candidates"]:
        return None
    c = type_entry["candidates"][0]
    choices = []
    if c.get("choices"):
        try:
            choices = json.loads(c["choices"])
        except Exception:
            choices = []
    src_short = f"{c.get('school','')} {c.get('year','')}".strip()
    return {
        "tid": type_entry["tid"],
        "label": type_entry["label"],
        "chapter": type_entry["chapter"],
        "cue": type_entry["cue"],
        "checkpoint": CHECKPOINTS.get(type_entry["tid"], type_entry["cue"]),
        "count": type_entry["ngd_count"],
        "stars": type_entry["stars"],
        "question_text": c["question_text"],
        "choices": choices,
        "answer": c.get("answer", ""),
        "source_short": src_short,
    }


def main(difficulty: str) -> None:
    candidates = json.load(open(NGD / f"per_type_candidates_{difficulty}.json"))
    top = select_top_types(candidates, limit=25)
    pages = [p for p in (build_type_page(t) for t in top) if p]
    print(f"{difficulty} 난이도: {len(pages)}개 유형 페이지 생성")
    build_book(difficulty, pages)


if __name__ == "__main__":
    import sys

    diff = sys.argv[1] if len(sys.argv) > 1 else "하"
    main(diff)
