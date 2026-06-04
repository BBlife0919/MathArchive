#!/usr/bin/env python3
"""MathArchive — question_text 에 섞여 들어간 '편집 오검(교정) 메모' 제거.

제거 대상 (보수적 — 강한 시그널만):
  1) `<<BOX_START>>...<<BOX_END>>` 블록 중 본문에 '오검'/'내역표'/'편집오검' 포함 → 박스 통째 제거
  2) `[NNNN]오검` / `NNNNN오검` / 줄 단독 '오검' 마커부터 본문 끝까지 (교정 내역 노트)

기본 DRY-RUN: 잘려나갈 텍스트 + 남는 본문 꼬리 출력, 쓰기 없음.
`--apply` 시에만 UPDATE.
"""
from __future__ import annotations
import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

_BOX = re.compile(r"<<BOX_START>>(.*?)<<BOX_END>>", re.DOTALL)
_EDIT_BOX_SIGNAL = re.compile(r"오검|내역표|편집오검")
# 교정 노트(편집 메모) 시작 마커 — 이 줄부터 본문 끝까지 절단.
#  · [04064]오검 / 06046오검 / 줄 단독 '오검'
#  · 편집 sign-off: 특이사항 없습니다 / 내역(이) 없습니다 / 수고하셨습니다
#  · 파트 노트: 문제part / 해설part
# 마커 '위치'부터 본문 끝까지 절단.
#  · `오검` 숫자 마커: 줄 중간이어도 안전 (5자리수+오검 은 실문제에 안 나옴)
#  · sign-off 류(수고하셨습니다 등): 정상 문장 중간 오탐 방지 위해 '줄 시작'으로 한정
#  · `☞` 는 실문제에서도 쓰일 수 있어 마커에서 제외
_OGEOM_MARK = re.compile(
    r"(?:\[\s*\d{3,6}\s*\]|\d{4,6})\s*오검"          # [04064]오검 / 06046오검 / <11043오검>
    r"|^\s*오검\b"                                    # 줄 시작 '오검'
    r"|^\s*(?:특이\s*사항\s*없"                        # 줄 시작 sign-off 류만
    r"|내역\s*(?:이\s*)?없습니다"
    r"|수고\s*하셨습니다"
    r"|문제\s*part|해설\s*part"
    r"|오류\s*(?:및\s*오타\s*)?없"
    r"|오타\s*없"
    # 편집 교정 지시 문구(실문제엔 안 나옴) — 이 줄부터 끝까지 절단
    r"|콤마\s*표기\s*수정|표기\s*수정-"
    r"|배점\s*위치\s*수정|단서\s*조항\s*위치\s*수정"
    r"|틀과\s*선지\s*사이|한?\s*줄\s*띄움"
    r"|해설\s*오류\s*수정|해설오류"
    r"|정답\s*수정|오타\s*수정"
    r"|중단원\s*\S{0,14}?\s*(?:변경|로\s*변경)"
    r"|난이도\s*\S{0,6}?\s*변경"
    r"|들여쓰기)",
    re.IGNORECASE | re.MULTILINE,
)


def clean(text: str):
    """반환: (cleaned_text, removed_list[str])."""
    if not text:
        return text, []
    removed = []
    new = text

    # 1) 편집 오검 박스 제거
    def _box_sub(m):
        if _EDIT_BOX_SIGNAL.search(m.group(1)):
            removed.append(m.group(0))
            return ""
        return m.group(0)

    new = _BOX.sub(_box_sub, new)

    # 2) 편집메모 마커 '위치'부터 끝까지 절단 (앞의 진짜 본문은 보존)
    mk = _OGEOM_MARK.search(new)
    if mk:
        # 마커 바로 앞 여는 괄호/꺾쇠( [ < )까지 함께 제거
        cut = mk.start()
        while cut > 0 and new[cut - 1] in " \t[<":
            cut -= 1
        removed.append(new[cut:])
        new = new[:cut]

    # 꼬리 공백/빈 박스 정리
    new = re.sub(r"\n{3,}", "\n\n", new).rstrip()
    return new, removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=15)
    args = ap.parse_args()

    import psycopg2
    from psycopg2.extras import execute_batch
    conn = psycopg2.connect(
        os.environ["SUPABASE_DB_URL"],
        keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=5,
    )
    rcur = conn.cursor(name="read_q")
    rcur.itersize = 2000
    rcur.execute("SELECT question_id, question_text FROM questions")
    changes = []
    empties = []  # 정리 후 빈 본문 → 보존(통째 교정노트, 수동검토)
    shown = 0
    removed_chars = 0
    for qid, txt in rcur:
        t = txt or ""
        nt, removed = clean(t)
        if nt != t:
            if not nt.strip():
                empties.append(qid)
                continue
            changes.append((nt, qid))
            removed_chars += len(t) - len(nt)
            if shown < args.show:
                rem = "\n      ┄┄ ".join(r[:200].replace("\n", "⏎") for r in removed)
                print(f"\n#{qid}  (제거 {len(t)-len(nt)}자)")
                print(f"   ✂ 제거됨: {rem[:420]}")
                print(f"   ✓ 남는 본문 끝: ...{nt[-90:]!r}")
                shown += 1
    rcur.close()
    print(f"\n===== 변경 대상 {len(changes)} 행, 총 제거 {removed_chars:,}자 =====")
    if empties:
        print(f"  (보존/수동검토: 정리 후 빈 본문 {len(empties)}행 {empties})")

    if args.apply and changes:
        wcur = conn.cursor()
        B = 500
        for i in range(0, len(changes), B):
            execute_batch(wcur, "UPDATE questions SET question_text=%s WHERE question_id=%s",
                          changes[i:i + B])
            conn.commit()
            print(f"   [APPLIED] {min(i + B, len(changes))}/{len(changes)}")
        wcur.close()
    conn.close()


if __name__ == "__main__":
    main()
