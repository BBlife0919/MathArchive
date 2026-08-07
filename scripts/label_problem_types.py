#!/usr/bin/env python3
"""LLM 기반 문항 유형 자동 라벨링.

공수1 6단원 47유형 체계에 따라 Claude API 로 각 문항의 유형을 1~2개 부여.
prompt caching 으로 유형 정의 부분 비용 절감.

사용법:
    # 환경변수 ANTHROPIC_API_KEY 필요
    python3 scripts/label_problem_types.py --sample 50          # 시범 50건
    python3 scripts/label_problem_types.py --chapter 다항식의\\ 연산  # 단원 한정
    python3 scripts/label_problem_types.py --apply              # 전체 적용
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

# ─────────────────────────────────────────────────────────
# 47 유형 체계 (공수1 6단원)
# ─────────────────────────────────────────────────────────
TYPE_SYSTEM = {
    "다항식의 연산": [
        ("1.1", "다항식 사칙연산", "두 다항식 A, B 의 A+B/A-B/AB 직접 계산"),
        ("1.2", "다항식 나눗셈", "다항식을 다항식으로 나눈 몫·나머지 (조립제법 포함)"),
        ("1.3", "곱셈공식 — 식의 값", "a+b, ab 주어졌을 때 a^2+b^2, a^3+b^3 등"),
        ("1.4", "곱셈공식 — 전개식의 계수", "(x+a)^n 등 전개식에서 특정 항의 계수"),
        ("1.5", "항등식 — 계수 비교", "x 에 관계없이 성립하는 등식 → 계수 비교"),
        ("1.6", "내림차순/오름차순 정리", "다변수 다항식을 한 문자에 대해 정리"),
        ("1.7", "다항식 활용 — 도형", "직육면체·삼각형·반원 등 도형의 넓이/부피 식"),
        ("1.8", "다항식 활용 — 실생활", "기계 처리량·가격 등 일상 모델링"),
    ],
    "항등식과 나머지정리": [
        ("2.1", "항등식 — 계수 비교/대입", "f(x) 항등식 → a, b, c 결정"),
        ("2.2", "나머지정리 — 일차식 1개", "f(x) 를 (x-k) 로 나눈 나머지 = f(k)"),
        ("2.3", "나머지정리 — 이차식으로 나눔", "두 일차식 나머지에서 이차식 나머지 결정"),
        ("2.4", "인수정리 — 나누어떨어짐 조건", "f(α)=0 으로 미지수 결정"),
        ("2.5", "조립제법 활용", "조립제법 빈칸 채우기, 몫·나머지 결정"),
        ("2.6", "조건부 종합형", "(가)/(나)/(다) 다중 조건으로 다항식 결정"),
        ("2.7", "두 다항식 동시 만족", "f(x), g(x) 두 다항식 양쪽 조건"),
    ],
    "인수분해": [
        ("3.1", "공식 직접 적용", "a^2-b^2, a^3±b^3, 완전제곱 등 공식 그대로"),
        ("3.2", "공통인수/치환", "묶기 또는 X = x^2+x 등 치환"),
        ("3.3", "복이차식", "x^4 + ax^2 + b 형태"),
        ("3.4", "인수정리 + 조립제법", "f(α)=0 찾고 인수분해"),
        ("3.5", "두 일차식 곱 조건", "두 일차식 곱으로 인수분해되도록 미지수 조건"),
        ("3.6", "인수분해 활용 — 큰 수 계산", "99^3+1 같은 수치 계산"),
        ("3.7", "인수분해 활용 — 도형/삼각형", "변 길이 관계로 삼각형 판정"),
    ],
    "복소수": [
        ("4.1", "복소수 사칙연산", "(a+bi) 사칙연산"),
        ("4.2", "켤레복소수 성질", "z+z̄, zz̄ 등"),
        ("4.3", "i 의 거듭제곱 주기성", "i^n 주기 4 활용한 합/곱"),
        ("4.4", "음수의 제곱근", "√(-a)·√(-b) 부호 처리"),
        ("4.5", "실수/허수 조건", "z 가 실수 ↔ 허수부=0"),
        ("4.6", "복소수 등식 a+bi=c+di", "실수부·허수부 비교"),
        ("4.7", "1의 거듭제곱근 ω", "x^3=1 한 허근 활용"),
    ],
    "이차방정식": [
        ("5.1", "근과 계수의 관계", "두 근의 합·곱 → 식의 값"),
        ("5.2", "새로운 이차방정식 만들기", "α, β 로 새 두 근 → 새 방정식"),
        ("5.3", "판별식 — 실근/허근/중근 조건", "D>0, D=0, D<0"),
        ("5.4", "항상 중근 조건", "실수 k 값에 관계없이 중근"),
        ("5.5", "한 근이 주어진 경우", "α=1+i 등 한 근으로 미지수 결정"),
        ("5.6", "켤레근 정리", "허수계수 → 켤레근"),
        ("5.7", "근의 부호 조건", "두 근이 양수/음수/혼합 부호"),
        ("5.8", "활용 — 잘못 본 문제 등", "학생 A/B 가 일부 잘못 봄 시나리오"),
    ],
    "이차함수": [
        ("6.1", "구간 최대·최소 (꼭짓점 구간 내)", "α≤x≤β 에서 최대·최소"),
        ("6.2", "구간 최대·최소 (변수 포함)", "구간이 변수 a 에 의존"),
        ("6.3", "그래프와 x축 교점", "두 교점/접/안 만남 조건"),
        ("6.4", "그래프와 직선 교점/접점", "접하는 조건, 두 점에서 만남"),
        ("6.5", "이차함수 결정", "세 점/꼭짓점+한 점/절편 조건"),
        ("6.6", "두 이차함수 관계", "f(x)≤g(x), 교점 등"),
        ("6.7", "그래프 대칭축/평행이동", "축 x=k 활용"),
        ("6.8", "절댓값/합성 그래프", "y=|f(x)|, f(f(x))"),
        ("6.9", "활용 — 실생활 최적화", "가격·판매량, 텐트, 울타리"),
        ("6.10", "활용 — 도형 넓이/부피 최대", "직사각형·사다리꼴 넓이 최대"),
    ],
}

# 단원명 → 유형 ID 집합
CHAPTER_TYPE_IDS = {
    ch: {tid for tid, _, _ in lst} for ch, lst in TYPE_SYSTEM.items()
}

SUPPORTED_CHAPTERS = list(TYPE_SYSTEM.keys())


def build_system_prompt() -> str:
    """유형 정의 시스템 프롬프트 — prompt cache 대상."""
    lines = [
        "너는 한국 고등학교 수학 (공통수학1) 문항 유형 분류 전문가다.",
        "각 문항을 아래 단원·유형 체계 중 가장 적절한 유형 1개에 배정한다.",
        "정확히 일치하는 유형이 없으면 가장 가까운 유형을 고르고 confidence 를 0.5 미만으로 한다.",
        "두 유형이 동시에 해당되면 더 핵심적인(풀이 시작점이 되는) 유형 하나만 고른다.",
        "",
        "=== 유형 체계 ===",
    ]
    for ch, types in TYPE_SYSTEM.items():
        lines.append(f"\n[{ch}]")
        for tid, name, desc in types:
            lines.append(f"  {tid} {name} — {desc}")
    lines.append("")
    lines.append("=== 응답 형식 ===")
    lines.append("JSON 한 줄: {\"type_id\": \"X.Y\", \"type_name\": \"...\", \"confidence\": 0.0~1.0, \"reason\": \"한 줄 사유\"}")
    return "\n".join(lines)


def clean_text_for_llm(text: str) -> str:
    """LLM 입력용 정리: BOX 마커 제거, 너무 긴 텍스트 컷."""
    if not text:
        return ""
    text = re.sub(r"<<BOX_START>>|<<BOX_END>>", "", text)
    text = re.sub(r"<<IMG:[^>]+>>", "[그림]", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:1500]  # 토큰 절약: 1500자 컷


def label_one(client, system_prompt, chapter, qtext) -> dict:
    """문항 1개 라벨링. 반환: {type_id, type_name, confidence, reason}."""
    user = (
        f"단원: {chapter}\n"
        f"문항:\n{clean_text_for_llm(qtext)}\n\n"
        f"위 문항의 유형을 위 체계에서 1개 선택해 JSON 한 줄로 응답."
    )
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        system=[{
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user}],
    )
    raw = resp.content[0].text.strip()
    # JSON 추출 (코드블록 등 잘라내기)
    m = re.search(r"\{[^{}]*\}", raw, re.S)
    if not m:
        return {"type_id": None, "confidence": 0.0,
                "reason": f"파싱 실패: {raw[:80]}", "raw": raw}
    try:
        parsed = json.loads(m.group(0))
        # type_id 가 단원에 속하는지 검증
        if parsed.get("type_id") not in CHAPTER_TYPE_IDS.get(chapter, set()):
            parsed["confidence"] = min(parsed.get("confidence", 0.5), 0.3)
            parsed["reason"] = f"단원 불일치: {parsed.get('reason', '')}"
        return parsed
    except json.JSONDecodeError as e:
        return {"type_id": None, "confidence": 0.0,
                "reason": f"JSON 파싱 실패: {e}", "raw": raw}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/mathdb.sqlite")
    ap.add_argument("--sample", type=int, default=0,
                    help="처음 N건만 (시범용)")
    ap.add_argument("--chapter", help="특정 단원만")
    ap.add_argument("--apply", action="store_true", help="DB 에 반영")
    ap.add_argument("--show", type=int, default=10, help="처음 N건 결과 출력")
    ap.add_argument("--skip-existing", action="store_true",
                    help="이미 라벨된 문항 skip")
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY 환경변수 미설정.", file=sys.stderr)
        sys.exit(2)

    try:
        from anthropic import Anthropic
    except ImportError:
        print("ERROR: pip install anthropic 필요", file=sys.stderr)
        sys.exit(2)

    client = Anthropic(api_key=api_key)
    system_prompt = build_system_prompt()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    chapters = [args.chapter] if args.chapter else SUPPORTED_CHAPTERS
    where = "chapter IN ({})".format(
        ",".join("?" for _ in chapters)
    )
    if args.skip_existing:
        where += " AND problem_type IS NULL"
    sql = f"SELECT question_id, chapter, question_text FROM questions WHERE {where} ORDER BY question_id"
    if args.sample:
        sql += f" LIMIT {args.sample}"

    rows = cur.execute(sql, chapters).fetchall()
    print(f"라벨링 대상: {len(rows)}건")

    results = []
    t0 = time.time()
    for i, row in enumerate(rows, 1):
        try:
            r = label_one(client, system_prompt, row["chapter"], row["question_text"])
        except Exception as e:
            r = {"type_id": None, "confidence": 0.0, "reason": f"API 오류: {e}"}
        r["question_id"] = row["question_id"]
        r["chapter"] = row["chapter"]
        results.append(r)

        if i <= args.show:
            tid = r.get("type_id") or "—"
            conf = r.get("confidence", 0.0)
            reason = (r.get("reason") or "")[:60]
            print(f"  qid={row['question_id']:5d} [{row['chapter'][:8]}] "
                  f"{tid:5s} conf={conf:.2f}  {reason}")

        if args.apply and r.get("type_id"):
            cur.execute(
                "UPDATE questions SET problem_type=?, "
                "problem_type_confidence=?, problem_type_source=? "
                "WHERE question_id=?",
                (r["type_id"], r.get("confidence", 0.0),
                 "claude-haiku-4-5", row["question_id"]),
            )

        # 매 50건마다 commit + 상태
        if i % 50 == 0:
            if args.apply:
                conn.commit()
            elapsed = time.time() - t0
            print(f"  {i}/{len(rows)}  ({elapsed:.0f}s)")

    if args.apply:
        conn.commit()

    # 통계
    succ = sum(1 for r in results if r.get("type_id"))
    avg_conf = sum(r.get("confidence", 0.0) for r in results) / max(len(results), 1)
    print(f"\n=== 라벨링 결과 ===")
    print(f"  성공: {succ}/{len(results)}")
    print(f"  평균 confidence: {avg_conf:.2f}")
    print(f"  소요시간: {time.time() - t0:.0f}초")
    if not args.apply:
        print("  --apply 로 DB 에 반영")

    conn.close()


if __name__ == "__main__":
    main()
