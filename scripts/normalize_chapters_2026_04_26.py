#!/usr/bin/env python3
"""중단원명 일괄 정규화 (2026-04-26 사용자 지시).

매핑 표는 사용자가 직접 검수해 확정한 결과. 표기 변형을 캐논(canonical) 명칭
으로 통합하고, 특정 문항(백석고/남녕고/범박고/덕문여고)은 개별 재분류.

사용법:
    python3 scripts/normalize_chapters_2026_04_26.py            # 미리보기
    python3 scripts/normalize_chapters_2026_04_26.py --apply
"""
from __future__ import annotations

import argparse
import sqlite3
from collections import Counter

# 표기 변형 → 캐논 명칭 (단순 1:1 치환)
CHAPTER_MAP = {
    # 경우의 수
    "경우의 상": "경우의 수",
    "경우의수": "경우의 수",
    # 고차방정식
    "고차 방정식": "고차방정식",
    "고차방장석": "고차방정식",
    "고차방장식": "고차방정식",
    "삼차방정식": "고차방정식",
    # 항등식과 나머지정리
    "나머지 정리 (시험 범위 외)": "항등식과 나머지정리",
    "나머지 정리와 인수분해": "항등식과 나머지정리",
    "항등식과 나마지정리": "항등식과 나머지정리",
    "항등식과 나머니 정리": "항등식과 나머지정리",
    "항등식과 나머지": "항등식과 나머지정리",
    "항등식과 나머지정리.": "항등식과 나머지정리",
    # 이차함수
    "다함함수": "이차함수",
    "이차방정식과 이차함수": "이차함수",
    # 다항식의 연산
    "다항식": "다항식의 연산",
    "다항식 연산": "다항식의 연산",
    "다항식과 연산": "다항식의 연산",
    "다항식의": "다항식의 연산",
    "다항식의 계산": "다항식의 연산",
    "다항식의 계수": "다항식의 연산",
    "다항식의 곱셈": "다항식의 연산",
    "다항식의 연산\\": "다항식의 연산",
    "다항식의 전개": "다항식의 연산",
    "다항식의연산": "다항식의 연산",
    "다항식이 연산": "다항식의 연산",
    # 도형의 이동
    "도형의이동": "도형의 이동",
    "도형이 이동": "도형의 이동",
    # 등비수열
    "등비수옇": "등비수열",
    # 명제
    "명제의 증명": "명제",
    # 무리식과 무리함수
    "무리수와 무리함수": "무리식과 무리함수",
    "무리식과 무맇마수": "무리식과 무리함수",
    "무리식와 무리함수": "무리식과 무리함수",
    "무리함수": "무리식과 무리함수",
    "무식과 무리함수": "무리식과 무리함수",
    "유리함수, 무리함수": "무리식과 무리함수",
    "유리함수,무리함수": "무리식과 무리함수",
    # 복소수
    "복수수": "복소수",
    "볶소수": "복소수",
    "이복소수": "복소수",
    # 부등식
    "부": "부등식",
    "연립부등식": "부등식",
    # 조합
    "순열, 조합": "조합",
    "순열,조합": "조합",
    "순열~조합": "조합",
    "순열과 조합": "조합",
    "조함": "조합",
    # 여러가지 방정식
    "여러 가지 방정식": "여러가지 방정식",
    "여러가지방정식": "여러가지 방정식",
    # 연립방정식
    "연립": "연립방정식",
    "연립방징식": "연립방정식",
    # 원의 방정식
    "원의 반지름": "원의 방정식",
    "원의방정식": "원의 방정식",
    "원이 방정식": "원의 방정식",
    # 유리식과 유리함수
    "유리식과 무리함수": "유리식과 유리함수",
    "유리식과 유리합수": "유리식과 유리함수",
    "유리함수": "유리식과 유리함수",
    # '유리식과 유리함수, 무리식과 무리함수' 는 덕문여고 2024 2기말 18번 만
    # '무리식과 무리함수', 나머지는 '유리식과 유리함수' 로 (개별 처리 후 일괄)
    # 인수분해
    "인수분히": "인수분해",
    # 이차방정식
    "이치방정식": "이차방정식",
    # 절대부등식
    "절대 부등식": "절대부등식",
    # 평면좌표
    "점과 좌표": "평면좌표",
    "퍙면좌표": "평면좌표",
    "펑면좌표": "평면좌표",
    "폄면좌표": "평면좌표",
    "평면죄표": "평면좌표",
    "평며좌표": "평면좌표",
    "평면 좌표": "평면좌표",
    # 직선의 방정식
    "직선의  방정식": "직선의 방정식",
    "직선의방정식": "직선의 방정식",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/mathdb.sqlite")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    # ----------------------------------------------------------------
    # 1) 개별 문항 분류 수정 (먼저 처리: 일괄 매핑 전에 손봐야 함)
    # ----------------------------------------------------------------
    individual_updates = []

    # 백석고 2025 1학기 중간 8번 → 인수분해
    rows = cur.execute(
        "SELECT question_id, chapter FROM questions "
        "WHERE school='백석고' AND year=2025 AND semester=1 "
        "AND exam_type='a' AND question_number=8"
    ).fetchall()
    for qid, ch in rows:
        individual_updates.append((qid, ch, "인수분해", "백석고 2025-1중 8번"))

    # 범박고 2025 1학기 중간 7번 → 이차방정식
    rows = cur.execute(
        "SELECT question_id, chapter FROM questions "
        "WHERE school='범박고' AND year=2025 AND semester=1 "
        "AND exam_type='a' AND question_number=7"
    ).fetchall()
    for qid, ch in rows:
        individual_updates.append((qid, ch, "이차방정식", "범박고 2025-1중 7번"))

    # 덕문여고 2024 2학기 기말 18번: '유리식과 유리함수, 무리식과 무리함수'
    # → 무리식과 무리함수
    rows = cur.execute(
        "SELECT question_id, chapter FROM questions "
        "WHERE school='덕문여고' AND year=2024 AND semester=2 "
        "AND exam_type='b' AND question_number=18"
    ).fetchall()
    for qid, ch in rows:
        individual_updates.append((qid, ch, "무리식과 무리함수",
                                   "덕문여고 2024-2기 18번"))

    # 남녕고 2025 1학기 중간 26번: 중복 두 문제 → 하나로 + 고차방정식
    namnyeong_q26 = cur.execute(
        "SELECT question_id, chapter FROM questions "
        "WHERE school='남녕고' AND year=2025 AND semester=1 "
        "AND exam_type='a' AND question_number=26 "
        "ORDER BY question_id"
    ).fetchall()
    delete_qid = None
    if len(namnyeong_q26) >= 2:
        # 첫 번째만 살리고 나머지 삭제, 분류는 고차방정식
        keep_qid = namnyeong_q26[0][0]
        delete_qid = [r[0] for r in namnyeong_q26[1:]]
        individual_updates.append((keep_qid, namnyeong_q26[0][1],
                                   "고차방정식", "남녕고 2025-1중 26번 (유지)"))
    elif len(namnyeong_q26) == 1:
        individual_updates.append((namnyeong_q26[0][0], namnyeong_q26[0][1],
                                   "고차방정식", "남녕고 2025-1중 26번"))

    print("=== 개별 문항 분류 수정 ===")
    for qid, before, after, label in individual_updates:
        print(f"  qid={qid}: '{before}' → '{after}' ({label})")
    if delete_qid:
        print(f"\n  남녕고 2025-1중 26번 중복 삭제 대상 qid: {delete_qid}")
    print()

    # ----------------------------------------------------------------
    # 2) '유리식과 유리함수, 무리식과 무리함수' 잔여분 → 유리식과 유리함수
    #    (덕문여고 2024-2기 18번은 위에서 이미 무리식과 무리함수 로 처리)
    # ----------------------------------------------------------------
    leftover_combo = cur.execute(
        "SELECT question_id FROM questions "
        "WHERE chapter IN ('유리식과 유리함수, 무리식과 무리함수', "
        "                  '유리식과 유리함수. 무리식과 무리함수') "
        "AND NOT (school='덕문여고' AND year=2024 AND semester=2 "
        "         AND exam_type='b' AND question_number=18)"
    ).fetchall()
    print(f"=== 'A, B' 형 단원명 → 유리식과 유리함수: {len(leftover_combo)}건 ===")

    # ----------------------------------------------------------------
    # 3) 일괄 매핑 적용 — 영향 카운트 미리 계산
    # ----------------------------------------------------------------
    print("\n=== 일괄 매핑 (변형 → 캐논) 영향 ===")
    impact = Counter()
    for variant, canonical in CHAPTER_MAP.items():
        n = cur.execute(
            "SELECT COUNT(*) FROM questions WHERE chapter=?",
            (variant,),
        ).fetchone()[0]
        if n:
            impact[(variant, canonical)] = n
            print(f"  {variant!r:40s} → {canonical!r:25s}  {n}건")

    total_map = sum(impact.values())
    print(f"\n  총 매핑 영향: {total_map}건 + 개별 {len(individual_updates)}건"
          f" + 콤보 잔여 {len(leftover_combo)}건"
          f" + 중복 삭제 {len(delete_qid or [])}건")

    if not args.apply:
        print("\n[미리보기] --apply 로 실제 반영.")
        conn.close()
        return

    # ----------------------------------------------------------------
    # 4) 실제 반영
    # ----------------------------------------------------------------
    # 개별 문항 먼저
    for qid, _before, after, _label in individual_updates:
        cur.execute("UPDATE questions SET chapter=? WHERE question_id=?",
                    (after, qid))

    # 남녕고 26번 중복 삭제 (solutions/images도 cascade)
    if delete_qid:
        for qid in delete_qid:
            cur.execute("DELETE FROM images WHERE question_id=?", (qid,))
            cur.execute("DELETE FROM solutions WHERE question_id=?", (qid,))
            cur.execute("DELETE FROM questions WHERE question_id=?", (qid,))

    # 'A, B' 콤보 잔여
    cur.execute(
        "UPDATE questions SET chapter='유리식과 유리함수' "
        "WHERE chapter IN ('유리식과 유리함수, 무리식과 무리함수', "
        "                  '유리식과 유리함수. 무리식과 무리함수')"
    )

    # 일괄 매핑
    for variant, canonical in CHAPTER_MAP.items():
        cur.execute("UPDATE questions SET chapter=? WHERE chapter=?",
                    (canonical, variant))

    conn.commit()
    print(f"\n✅ 적용 완료.")
    conn.close()


if __name__ == "__main__":
    main()
