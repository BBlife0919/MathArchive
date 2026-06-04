#!/usr/bin/env python3
"""수식 `$...$` 안 한글 → `\\text{}` 래핑 (하이브리드: 명확=자동, 애매=검토목록).

분류:
  CLEAR    : 한글 run 이 구분자( ( ) , 공백 { } \\ / 양끝 )로 깔끔히 떨어짐 + run ≤ 2
             → KaTeX(after) 통과 시 자동 적용 후보
  AMBIG    : 한글이 수식기호에 바짝 붙음(예: r인) / run 3개+ / after 실패
             → 자동 적용 안 함, 검토 목록

--dry-run(기본): 카운트 + 샘플 + 검토목록 파일.  --apply: 백업 후 CLEAR 만 UPDATE.
"""
from __future__ import annotations
import re

_MATH = re.compile(r"(?<!\\)\$(.*?)(?<!\\)\$", re.DOTALL)
# 이미 \text/\mathrm/\mbox 로 감싼 블록
_TEXTBLOCK = re.compile(r"\\(?:text|mathrm|mbox|operatorname)\s*\{[^{}]*\}")
_HANGUL = re.compile(r"[가-힣]")
# 한글 run: 한글(내부 공백 허용)
_HANGUL_RUN = re.compile(r"[가-힣]+(?:\s+[가-힣]+)*")
# run 양옆 '안전한 구분자'
_SAFE = set(" ()[]{},\\/$\n\t")


def _wrap_segment(seg: str):
    """\\text 블록 바깥의 한 조각에서 한글 run 래핑. (new_seg, runs, all_clear)."""
    out = []
    last = 0
    runs = 0
    all_clear = True
    for m in _HANGUL_RUN.finditer(seg):
        runs += 1
        s, e = m.start(), m.end()
        left = seg[s - 1] if s > 0 else " "
        right = seg[e] if e < len(seg) else " "
        if left not in _SAFE or right not in _SAFE:
            all_clear = False  # 수식기호에 바짝 붙음
        out.append(seg[last:s])
        out.append(r"\text{" + m.group(0) + "}")
        last = e
    out.append(seg[last:])
    return "".join(out), runs, all_clear


def wrap_math_inner(inner: str):
    """$...$ 내부 처리. (new_inner, total_runs, clear_bool)."""
    pieces = []
    last = 0
    total_runs = 0
    clear = True
    for tb in _TEXTBLOCK.finditer(inner):
        seg = inner[last:tb.start()]
        nw, r, c = _wrap_segment(seg)
        pieces.append(nw)
        total_runs += r
        clear = clear and c
        pieces.append(tb.group(0))  # 기존 \text 블록 보존
        last = tb.end()
    seg = inner[last:]
    nw, r, c = _wrap_segment(seg)
    pieces.append(nw)
    total_runs += r
    clear = clear and c
    return "".join(pieces), total_runs, clear


def transform(text: str):
    """반환: (new_text, changed_spans[(before,after)], clear_bool)."""
    if not text or "$" not in text:
        return text, [], True
    changed = []
    clear = True

    def _sub(m):
        nonlocal clear
        inner = m.group(1)
        if not _HANGUL.search(inner):
            return m.group(0)
        # 이미 모든 한글이 \text 안이면 변화 없음
        new_inner, runs, c = wrap_math_inner(inner)
        if new_inner == inner:
            return m.group(0)
        if runs > 2:
            c = False
        changed.append(("$" + inner + "$", "$" + new_inner + "$"))
        clear = clear and c
        return "$" + new_inner + "$"

    new_text = _MATH.sub(_sub, text)
    return new_text, changed, clear


def katex_validate(spans: list[str]) -> dict:
    """inner LaTeX 리스트 → {span: ok(bool)}. KaTeX throwOnError 로 검증."""
    import json as _json
    from playwright.sync_api import sync_playwright
    html = (
        "<!doctype html><meta charset=utf-8>"
        "<script src='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js'></script>"
    )
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content(html)
        pg.wait_for_function("window.katex !== undefined", timeout=15000)
        res = {}
        B = 1000
        for i in range(0, len(spans), B):
            chunk = spans[i:i + B]
            ok = pg.evaluate(
                "(arr)=>arr.map(s=>{try{katex.renderToString(s,{throwOnError:true});return true}"
                "catch(e){return false}})",
                chunk,
            )
            for s, o in zip(chunk, ok):
                res[s] = o
        b.close()
    return res


def main():
    import argparse
    import json
    import os
    from pathlib import Path
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=10)
    args = ap.parse_args()

    ROOT = Path(__file__).resolve().parent.parent
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    import psycopg2
    from psycopg2.extras import execute_batch
    conn = psycopg2.connect(
        os.environ["SUPABASE_DB_URL"],
        keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=5,
    )

    cands = []  # {table,id,col,before,after,clear,after_spans[]}
    for table, idcol, txtcol in [
        ("questions", "question_id", "question_text"),
        ("solutions", "solution_id", "solution_text"),
    ]:
        rcur = conn.cursor(name=f"r_{table}")
        rcur.itersize = 2000
        rcur.execute(f"SELECT {idcol}, {txtcol} FROM {table}")
        for _id, txt in rcur:
            t = txt or ""
            nt, changed, clear = transform(t)
            if nt != t:
                cands.append({
                    "table": table, "col": txtcol, "id": _id,
                    "before": t, "after": nt, "clear": clear,
                    "after_spans": [a[1][1:-1] for a in changed],  # inner (strip $)
                })
        rcur.close()
    print(f"변경 후보(한글 수식 포함): {len(cands)} 행")

    # KaTeX 검증 — 변경된 after span 전체
    uniq = sorted({s for c in cands for s in c["after_spans"]})
    print(f"KaTeX 검증 대상 고유 span: {len(uniq)} ...")
    valid = katex_validate(uniq)

    auto, review = [], []
    for c in cands:
        after_ok = all(valid.get(s, False) for s in c["after_spans"])
        if c["clear"] and after_ok:
            auto.append(c)
        else:
            review.append(c)

    print(f"\n===== 자동적용(CLEAR+KaTeX통과): {len(auto)}  /  검토목록(AMBIG/실패): {len(review)} =====")
    print("\n[자동적용 샘플]")
    for c in auto[:args.show]:
        print(f"  #{c['id']}({c['table']}): {c['before'][:80]!r}\n            → {c['after'][:80]!r}")
    print("\n[검토목록 샘플]")
    for c in review[:args.show]:
        print(f"  #{c['id']}({c['table']}): {c['before'][:90]!r}")

    # 검토목록 파일
    rev_path = ROOT / "output" / "hangul_math_review.json"
    rev_path.parent.mkdir(exist_ok=True)
    rev_path.write_text(json.dumps(
        [{"table": c["table"], "id": c["id"], "before": c["before"], "after": c["after"]}
         for c in review], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n검토목록 저장: {rev_path}")

    if args.apply and auto:
        # 백업
        bak = ROOT / "output" / "hangul_math_backup.json"
        bak.write_text(json.dumps(
            [{"table": c["table"], "id": c["id"], "before": c["before"]} for c in auto],
            ensure_ascii=False), encoding="utf-8")
        print(f"백업 저장: {bak}")
        wcur = conn.cursor()
        by_tbl = {}
        for c in auto:
            by_tbl.setdefault((c["table"], c["col"], "question_id" if c["table"] == "questions" else "solution_id"), []).append((c["after"], c["id"]))
        for (tbl, col, idc), rows in by_tbl.items():
            for i in range(0, len(rows), 500):
                execute_batch(wcur, f"UPDATE {tbl} SET {col}=%s WHERE {idc}=%s", rows[i:i + 500])
                conn.commit()
                print(f"  [APPLIED {tbl}] {min(i + 500, len(rows))}/{len(rows)}")
        wcur.close()
    conn.close()


if __name__ == "__main__":
    main()
