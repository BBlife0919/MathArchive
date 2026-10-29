#!/usr/bin/env python3
"""2026-10-29 파서 수정 4건(분수 over 분자/분모, 적분·합 음수 첨자, 해설
π≤ 깨짐=pile→matrix 백필, 워터마크 이미지 해시 필터) 백필 스크립트.

question_id는 절대 바꾸지 않는다(clinic_entries 등 다른 테이블이 FK로
참조하므로 INSERT/DELETE가 아니라 file_source+question_number로 기존 행을
찾아 question_text/choices/solution_text만 UPDATE). images 테이블은
워터마크 재필터링으로 image_ref 집합이 바뀌므로 해당 question_id 분만
삭제 후 재삽입한다.

실행:
    python scripts/backfill_eq_parser_fixes.py --local   # 로컬 SQLite만
    python scripts/backfill_eq_parser_fixes.py           # .env 보고 자동판단(운영)
    python scripts/backfill_eq_parser_fixes.py --dry-run # DB 안 건드리고 변경 건수만 집계
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "app"))


def _load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--local", action="store_true", help="강제로 SQLite(운영 DB 안 건드림)")
    ap.add_argument("--dry-run", action="store_true", help="DB 쓰기 없이 변경 건수만 집계")
    ap.add_argument("--limit", type=int, default=None, help="파일 수 제한(테스트용)")
    args = ap.parse_args()

    if args.local:
        os.environ.pop("SUPABASE_DB_URL", None)
    else:
        _load_env_file()

    from db import get_connection, is_cloud  # noqa: E402
    import parse_hwpx  # noqa: E402

    conn = get_connection()
    cloud = is_cloud()
    print(f"대상 DB: {'Supabase Postgres' if cloud else '로컬 SQLite'}"
          + (" (dry-run)" if args.dry_run else ""))

    # 1) 이번에 수정한 패턴들이 실제로 걸리는 "영향받는 file_source" 전체를
    #    모은다 — 파일 단위로 통째로 재파싱해서, 바뀐 question만 UPDATE.
    affected: set[str] = set()
    rows = conn.execute(
        "SELECT DISTINCT file_source FROM questions "
        "WHERE question_text LIKE ? OR question_text LIKE ? OR choices LIKE ?",
        ("%\\leq{%", "%\\leq {%", "%\\leq{%"),
    ).fetchall()
    affected.update(r[0] for r in rows)

    rows = conn.execute(
        "SELECT DISTINCT q.file_source FROM questions q "
        "JOIN solutions s ON s.question_id=q.question_id "
        "WHERE s.solution_text LIKE ? OR s.solution_text LIKE ?",
        ("%\\leq{%", "%\\leq {%"),
    ).fetchall()
    affected.update(r[0] for r in rows)

    import re
    neg_sup_pat = re.compile(r"[\^_]-[0-9]")
    for r in conn.execute(
        "SELECT DISTINCT file_source, question_text FROM questions "
        "WHERE question_text LIKE '%_-%' OR question_text LIKE '%^-%'"
    ).fetchall():
        if r[1] and neg_sup_pat.search(r[1]):
            affected.add(r[0])
    for r in conn.execute(
        "SELECT q.file_source, s.solution_text FROM questions q "
        "JOIN solutions s ON s.question_id=q.question_id "
        "WHERE s.solution_text LIKE '%_-%' OR s.solution_text LIKE '%^-%'"
    ).fetchall():
        if r[1] and neg_sup_pat.search(r[1]):
            affected.add(r[0])

    print(f"텍스트 신호로 찾은 영향 파일: {len(affected)}건")

    # 분수 over 버그는 이미 변환된 DB 텍스트에서 역으로 찾기 어려우므로
    # (원본 "over" 키워드가 안 남아있음) raw/ 안에 있는, "over"를 실제로
    # 포함하는 모든 파일을 추가한다 — 가장 포괄적이고 안전한 방법.
    raw_dir = ROOT / "raw"
    import zipfile
    over_kw = re.compile(r"(?<![A-Za-z])over(?!line|right|left)(?![A-Za-z])")
    all_files = sorted(raw_dir.glob("*.hwpx"))
    if args.limit:
        all_files = all_files[: args.limit]
    print(f"raw/ 전체 파일: {len(all_files)}건 — 'over' 포함 여부 스캔 중...")
    n_scanned = 0
    for fp in all_files:
        n_scanned += 1
        if n_scanned % 2000 == 0:
            print(f"  ...{n_scanned}개 스캔")
        try:
            z = zipfile.ZipFile(fp)
            xml = z.read("Contents/section0.xml").decode("utf-8")
        except Exception:
            continue
        if over_kw.search(xml):
            affected.add(unicodedata.normalize("NFC", fp.name))

    if args.limit:
        affected = set(sorted(affected)[: args.limit])
    print(f"최종 재처리 대상 파일: {len(affected)}건", flush=True)

    # 2) 파일별로 재파싱 → file_source+question_number 로 기존 question_id
    #    찾아서 UPDATE (question_id는 유지).
    n_files_done = 0
    n_q_updated = 0
    n_sol_updated = 0
    n_img_resynced = 0
    n_missing = 0

    name_to_path = {}
    for fp in raw_dir.glob("*.hwpx"):
        name_to_path[unicodedata.normalize("NFC", fp.name)] = fp

    for file_source in sorted(affected):
        fp = name_to_path.get(file_source)
        if fp is None:
            n_missing += 1
            continue
        n_files_done += 1
        if n_files_done % 50 == 0:
            print(f"  ...재파싱 {n_files_done}/{len(affected)} "
                  f"(questions UPDATE {n_q_updated}, solutions UPDATE {n_sol_updated})",
                  flush=True)
        try:
            result = parse_hwpx.parse_hwpx(str(fp))
        except Exception as e:
            print(f"  [파싱 실패] {file_source}: {e}")
            continue

        for q in result["questions"]:
            row = conn.execute(
                "SELECT question_id, question_text, choices FROM questions "
                "WHERE file_source=? AND question_number=?",
                (file_source, q["question_number"]),
            ).fetchone()
            if row is None:
                continue
            qid, old_text, old_choices = row[0], row[1], row[2]
            new_text = q["question_text"]
            new_choices = json.dumps(q["choices"], ensure_ascii=False)
            if old_text != new_text or old_choices != new_choices:
                n_q_updated += 1
                if not args.dry_run:
                    conn.execute(
                        "UPDATE questions SET question_text=?, question_latex=?, "
                        "choices=?, has_image=? WHERE question_id=?",
                        (new_text, new_text, new_choices,
                         1 if q["has_image"] else 0, qid),
                    )

            if q["solution_text"]:
                srow = conn.execute(
                    "SELECT solution_id, solution_text FROM solutions "
                    "WHERE question_id=?", (qid,),
                ).fetchone()
                if srow is not None:
                    if srow[1] != q["solution_text"]:
                        n_sol_updated += 1
                        if not args.dry_run:
                            conn.execute(
                                "UPDATE solutions SET solution_text=?, solution_latex=? "
                                "WHERE solution_id=?",
                                (q["solution_text"], q["solution_text"], srow[0]),
                            )

            # 이미지 재동기화(워터마크 제외 반영) — 기존 행 지우고 다시 삽입.
            existing_refs = [r[0] for r in conn.execute(
                "SELECT image_ref FROM images WHERE question_id=? ORDER BY image_order",
                (qid,),
            ).fetchall()]
            new_refs = q.get("image_refs", [])
            if existing_refs != new_refs:
                n_img_resynced += 1
                if not args.dry_run:
                    conn.execute("DELETE FROM images WHERE question_id=?", (qid,))
                    for order, ref in enumerate(new_refs, 1):
                        image_path = ""
                        for p in q.get("image_paths", []):
                            if ref in p:
                                image_path = p
                                break
                        conn.execute(
                            "INSERT INTO images (question_id, image_ref, image_path, "
                            "image_order, image_type) VALUES (?, ?, ?, ?, ?)",
                            (qid, ref, image_path, order, "question"),
                        )

        if not args.dry_run and hasattr(conn, "commit"):
            try:
                conn.commit()
            except Exception:
                pass

    print(f"\n[완료] 재파싱 파일: {n_files_done} (raw 없음: {n_missing})")
    print(f"questions 업데이트: {n_q_updated}")
    print(f"solutions 업데이트: {n_sol_updated}")
    print(f"images 재동기화: {n_img_resynced}")


if __name__ == "__main__":
    main()
