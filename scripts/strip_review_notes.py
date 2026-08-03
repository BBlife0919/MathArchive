#!/usr/bin/env python3
"""오검/편집오검/벌점 채점메모 제거 함수 + DB 일괄 정리.

문항 본문·해설 끝(또는 인라인)에 붙은 편집자 검토 메모(<오검>, [오검내용],
편집오검 내역표, 총 벌점 …, N번 … 수정)를 잘라낸다. 리뷰 앵커를 찾은 뒤,
그 앞의 마지막 문제 종결부([N점]/구하시오) 또는 유지되는 정상 박스 끝에서
절단하므로 정상 표(마방진)·인라인 오검·리딩 오검을 모두 안전하게 처리한다.

usage:
  python3 strip_review_notes.py            # 드라이런 (통계 + 샘플만)
  python3 strip_review_notes.py --apply    # 로컬 sqlite 실제 적용 (백업 후)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "mathdb.sqlite"

# 리뷰(편집메모) 키워드: 오검/벌점주석/리뷰표 헤더/오타내역
# 2026-08-03 도형의이동 워크북 검수에서 "서술형 양식 수정" 류 스타일/포맷
# 체크리스트 표도 발견 — 오검/벌점 어휘가 전혀 없는 새 표 형식이라 키워드 추가.
_REVIEW_KW = (
    r"(?:편집|팀장)?\s*오검"
    r"|벌점\s*(?:합계|총점|사항)?\s*[:∶]?\s*[\(\[<（]?\s*(?:없|[-–−]|\d|\$)"
    r"|벌점사항|해당\s*번호|내역표|수정\s*전\s*\||수정\s*후\s*\||오타\s*및\s*오답"
    r"|서술형\s*양식|총점\s*삭제|바탕글\s*이외|배점\s*위치|스타일\s*삭제"
    r"|안\s*띄우기|한\s*줄\s*띄|오탈자\s*수정|특이사항|편집팀|편집자|<\d{4,}>"
)
# 리뷰표 헤더를 담은 <<BOX_START>>…<<BOX_END>> 만 제거.
# ── 화살표(->,→,⇨)는 정상 수학박스(보기/조건/함수/작도)에도 흔하므로 트리거 금지.
#    화살표만 있는 리뷰표는 앞의 오검/벌점/N번수정 앵커가 잡아 절단됨.
_BOX_RE = re.compile(
    r"\n*[ \t]*<<BOX_START>>(?:(?!<<BOX_END>>).)*?(?:" + _REVIEW_KW +
    r"|문항\s*번호\s*\||편집\s*오검)(?:(?!<<BOX_END>>).)*?<<BOX_END>>",
    re.DOTALL,
)
# 리뷰 앵커: 노트 영역 어딘가에 반드시 있는 강한 신호
# N번 뒤 편집 동사에 조정/변경/교체 추가 (기존 수정/오타/삭제/추가/누락만으로는
# "4번 배점위치 조정" 같은 케이스를 못 잡음).
_ANCHOR_RE = re.compile(
    _REVIEW_KW
    + r"|(?m:^[ \t]*\[?\s*(?:문제|해설|풀이|서술형)?\s*\d+\s*번?[^\n]*"
      r"(?:수정|오타|삭제|추가|누락|조정|변경|교체|->|→|⇨))"
)
# 박스 제거 후에도 남는 짧은 편집메모 잔여 조각(예: "해5. 정답을",
# "N번 OO조정" 등 — 원본 리뷰노트가 잘려서 본문 뒤에 붙은 경우) 정리용.
_DANGLING_RE = re.compile(
    r"\n*해\d+\.\s*정답을?\s*$"
    r"|\n*\d+번\s*[^\n$]{0,12}(?:조정|변경|교체)\s*$"
)
# 실제 문제의 종결부 (배점 [ …점 ] / 전각 【 …점 】 / 종결 서술어)
_TERM_RE = re.compile(
    r"\[[^\]\n]*점[^\]\n]*\]|【[^】\n]*점[^】\n]*】|（[^）\n]*점[^）\n]*）"
    r"|구하시오|구하여라|구하라|서술하시오|논술하시오|답하시오|나타내시오|"
    r"증명하시오|쓰시오|말하시오|보이시오|설명하시오|설명하여라"
)


def strip_review_notes(text: str | None) -> str:
    """오검/편집오검/벌점 편집메모 블록 제거.

    1) 리뷰 키워드 담은 <<BOX>> 표 제거 (정상 표는 유지)
    2) 첫 리뷰 앵커를 찾고, 그 앞의 '마지막 문제 종결부([N점]/구하시오)'
       또는 '유지되는 정상 박스 끝(<<BOX_END>>)' 중 더 뒤 지점에서 절단.
       → 인라인/리딩/마방진박스/마크다운표 노트 모두 안전 처리.

    NOTE(2026-08-03): "종결부 뒤 박스는 무조건 편집메모"라는 구조적 규칙을
    시도했다가 되돌림 — <보기>ㄱㄴㄷ 박스·(가)(나)(다) 빈칸·선택지 표 등 정상
    문제 구성요소가 [N점]/구하시오 뒤에 오는 경우가 매우 흔해서(예: "옳은
    것은? [4점]" 뒤에 <보기> 박스) 대량 오삭제 발생. 반드시 키워드 기반으로만
    판정할 것 — 새 리뷰표 형식 발견 시 _REVIEW_KW 에 해당 어휘를 추가할 것.
    """
    if not text:
        return text or ""
    text = _BOX_RE.sub("", text)
    a = _ANCHOR_RE.search(text)
    if not a:
        return _DANGLING_RE.sub("", text.rstrip()).rstrip()

    head = text[: a.start()]
    cut = 0
    for tm in _TERM_RE.finditer(head):       # 마지막 문제 종결부
        cut = tm.end()
    for bm in re.finditer(r"<<BOX_END>>", head):  # 유지되는 정상 박스 끝
        cut = max(cut, bm.end())
    result = text[:cut].rstrip()
    # 안전장치: 종결부/박스를 못 찾아 결과가 비었는데 앵커 앞에 실제 본문(15자↑)이
    # 있으면 통삭하지 말고 앵커 앞까지 보존 (종결어 미인식으로 인한 문항 전삭 방지).
    # 끝에 남는 마크다운/괄호 잔여(#, <, 공백)는 정리.
    if len(result.strip()) < 15 and len(head.strip()) >= 15:
        result = head.rstrip(" \t\n#<>")
    # 박스 삭제 후에도 뒤에 붙어 남는 짧은 편집메모 잔여 조각 정리
    result = _DANGLING_RE.sub("", result).rstrip()
    return result


def _run(apply: bool, cloud: bool = False):
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    stats = {"q_changed": 0, "q_emptied": 0, "s_changed": 0}
    empties = []
    samples = []
    overcut = []    # 삭제분에 오검/벌점 없음 → 과다삭제 의심
    verbcut = []    # 삭제분에 문제 종결어(구하시오 등) → 본문 삭제 의심
    undercut = []   # 유지분에 오검/벌점 잔존 → 미삭제
    kw = re.compile(r"오검|벌점")
    verb = re.compile(r"구하시오|구하여라|서술하시오|논술하시오|답하시오|나타내시오|증명하시오|쓰시오")
    left = re.compile(r"오검|벌점")

    LIKE = "(question_text LIKE '%오검%' OR question_text LIKE '%벌점%')"

    # questions
    q_updates = []
    for r in cur.execute(f"SELECT question_id, question_text FROM questions WHERE {LIKE}"):
        orig = r["question_text"]
        new = strip_review_notes(orig)
        if new != orig:
            stats["q_changed"] += 1
            q_updates.append((new, r["question_id"]))
            removed = orig[len(new):] if orig.startswith(new) else orig.replace(new, "", 1)
            if not kw.search(removed):
                overcut.append(r["question_id"])
            if verb.search(removed):
                verbcut.append(r["question_id"])
            if left.search(new):
                undercut.append(r["question_id"])
            if len(new.strip()) < 15:
                stats["q_emptied"] += 1
                empties.append(r["question_id"])
            if len(samples) < 4 and len(new.strip()) >= 15:
                samples.append((r["question_id"], orig[-260:], new[-160:]))
        elif left.search(orig):
            undercut.append(r["question_id"])

    # solutions
    s_updates = []
    for r in cur.execute("SELECT solution_id, solution_text FROM solutions "
                         "WHERE solution_text LIKE '%오검%' OR solution_text LIKE '%벌점%'"):
        orig = r["solution_text"]
        new = strip_review_notes(orig)
        if new != orig:
            stats["s_changed"] += 1
            s_updates.append((new, r["solution_id"]))

    print(f"[통계] 문항 변경 {stats['q_changed']} / 그중 본문 거의 빔(<15자) {stats['q_emptied']}")
    print(f"       해설 변경 {stats['s_changed']}")
    print(f"[검증] 과다삭제 의심(삭제분에 오검/벌점 없음): {len(overcut)}  {overcut[:15]}")
    print(f"[검증] 본문삭제 의심(삭제분에 문제종결어): {len(verbcut)}  {verbcut[:15]}")
    print(f"[검증] 미삭제(유지분에 오검/벌점 잔존): {len(undercut)}  {undercut[:15]}")
    print(f"[빈문항 후보 qid] {empties[:40]}{' …' if len(empties)>40 else ''}")
    print("\n[샘플 before(뒤260자) → after(뒤160자)]")
    for qid, before, after in samples:
        print(f"\n--- qid {qid} ---")
        print("BEFORE …", repr(before))
        print("AFTER  …", repr(after))

    if apply:
        import shutil
        bak = DB_PATH.with_suffix(f".sqlite.bak_review")
        shutil.copy2(DB_PATH, bak)
        print(f"\n[APPLY] 로컬 백업 → {bak.name}")
        cur.executemany("UPDATE questions SET question_text=? WHERE question_id=?", q_updates)
        cur.executemany("UPDATE solutions SET solution_text=? WHERE solution_id=?", s_updates)
        # 본문 유실(오검메모만) 항목 플래그
        cur.executemany(
            "UPDATE questions SET error_note=COALESCE(error_note,'')||'[본문없음:오검메모만] ' "
            "WHERE question_id=?", [(q,) for q in empties])
        conn.commit()
        print(f"  로컬 완료: 문항 {len(q_updates)} · 해설 {len(s_updates)} · 빈문항플래그 {len(empties)}")
    else:
        print("\n(드라이런 — --apply 로 로컬 적용)")
    conn.close()

    if apply and cloud:
        _apply_cloud()


def _apply_cloud():
    """Supabase(Postgres) 에 대해 클라우드 자체 텍스트로 재계산해 적용."""
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("[CLOUD] SUPABASE_DB_URL 없음 — 스킵")
        return
    import psycopg2
    print("[CLOUD] Supabase 연결·재계산…")
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()

    cur.execute("SELECT question_id, question_text FROM questions "
                "WHERE question_text LIKE '%오검%' OR question_text LIKE '%벌점%'")
    q_up, empties = [], []
    for qid, t in cur.fetchall():
        n = strip_review_notes(t)
        if n != t:
            q_up.append((n, qid))
            if len(n.strip()) < 15:
                empties.append(qid)

    cur.execute("SELECT solution_id, solution_text FROM solutions "
                "WHERE solution_text LIKE '%오검%' OR solution_text LIKE '%벌점%'")
    s_up = [(strip_review_notes(t), sid) for sid, t in cur.fetchall()
            if strip_review_notes(t) != t]

    cur2 = conn.cursor()
    cur2.executemany("UPDATE questions SET question_text=%s WHERE question_id=%s", q_up)
    cur2.executemany("UPDATE solutions SET solution_text=%s WHERE solution_id=%s", s_up)
    cur2.executemany(
        "UPDATE questions SET error_note=COALESCE(error_note,'')||'[본문없음:오검메모만] ' "
        "WHERE question_id=%s", [(q,) for q in empties])
    conn.commit()
    print(f"  클라우드 완료: 문항 {len(q_up)} · 해설 {len(s_up)} · 빈문항플래그 {len(empties)}")
    cur.close(); cur2.close(); conn.close()


if __name__ == "__main__":
    _run(apply="--apply" in sys.argv, cloud="--cloud" in sys.argv)
