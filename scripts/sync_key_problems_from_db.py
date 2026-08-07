"""DB에서 학교별 시험문제 본문 + 그림을 가져와 configs/key_problems 자동 갱신.

- exam_latex: DB question_text를 HTML 친화적으로 변환
- exam_images: images 테이블의 image_path 리스트 첨부
- 소하고 q23 (논술 10점) 자동 보강
"""
from __future__ import annotations
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIGS = ROOT / "output" / "pirate_analysis" / "configs"
DB = ROOT / "db" / "mathdb.sqlite"

SCHOOLS = ["광문고", "광명고", "광명북고", "명문고", "소하고", "운산고"]


def cleanup_question_text(text: str) -> str:
    """파서가 다음 문제와 합쳐버린 경우, 첫 [N점] + 첫 객관식/박스 종료까지만 유지."""
    # 첫 점수 표기 위치
    m = re.search(r"\[\$?\d+(?:\.\d+)?\$?\s*점\]", text)
    if not m:
        return text
    cut_pos = m.end()
    after = text[cut_pos:]
    # 점수 표기 다음의 첫 BOX_END (객관식 박스 닫힘) 까지 유지
    box_end_idx = after.find("<<BOX_END>>")
    if box_end_idx >= 0:
        # 두 번째 BOX_START 이전이어야 안전 (서답형 답안 박스 등은 보통 BOX_END 한 번)
        return text[:cut_pos + box_end_idx + len("<<BOX_END>>")]
    # 박스 없으면 점수 표기까지
    return text[:cut_pos]


CHOICE_MARKS = "①②③④⑤⑥⑦⑧⑨⑩"


def _format_box(body: str) -> str:
    """BOX_START/END 내부 — 마크다운 테이블이면 플레인 변환."""
    body = body.strip()
    # 객관식 마크 ①~⑤ 포함된 마크다운 표 패턴
    if any(m in body for m in CHOICE_MARKS) and "|" in body:
        # 셀 추출
        cells: list[str] = []
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            # 구분선 |---|---| 스킵
            if re.fullmatch(r"\|[-:|\s]+\|", line):
                continue
            for c in line.strip("|").split("|"):
                c = c.strip()
                if c:
                    cells.append(c)
        if cells:
            return "<div class='choices'>" + "&nbsp;&nbsp;&nbsp;&nbsp;".join(cells) + "</div>"
    # 일반 조건박스
    body = body.replace("\n", "<br>")
    return f"<div class='cond-box'>{body}</div>"


def qtext_to_html(text: str) -> str:
    """DB question_text → HTML inline ready string."""
    text = cleanup_question_text(text)
    # 점수 표기 [N점] 제거 (별도 표시)
    text = re.sub(r"\s*\[\$?\d+(?:\.\d+)?\$?\s*점\]\s*$", "", text)
    text = re.sub(r"<<BOX_START>>(.*?)<<BOX_END>>",
                  lambda m: _format_box(m.group(1)), text, flags=re.DOTALL)
    # 잔여 마커 정리
    text = text.replace("<<BOX_START>>", "").replace("<<BOX_END>>", "")
    # 줄바꿈 → <br>
    text = text.replace("\n", "<br>")
    # 탭 → 일반 공백
    text = text.replace("\t", " ")
    # 연속된 br 정리
    text = re.sub(r"(<br>\s*){3,}", "<br><br>", text)
    return text.strip()


def fetch(cur, school: str, qno: int):
    cur.execute(
        """
        SELECT question_id, question_text, has_image, points
        FROM questions
        WHERE school=? AND year=2026 AND semester=1 AND exam_type='a'
          AND file_source LIKE '%경기광명시%'
          AND CAST(question_number AS INTEGER) = ?
        LIMIT 1
        """,
        (school, qno),
    )
    return cur.fetchone()


def fetch_images(cur, qid: int) -> list[str]:
    cur.execute(
        "SELECT image_path FROM images WHERE question_id=? ORDER BY image_order",
        (qid,),
    )
    return [r[0] for r in cur.fetchall()]


def main():
    db = sqlite3.connect(str(DB))
    cur = db.cursor()
    for school in SCHOOLS:
        cfg_path = CONFIGS / f"{school}.json"
        if not cfg_path.exists():
            continue
        cfg = json.loads(cfg_path.read_text())

        # 1) key_problems 본문/그림 자동 갱신
        for kp in cfg.get("key_problems", []):
            row = fetch(cur, school, kp["q"])
            if not row:
                print(f"  [{school}] q{kp['q']}: DB 매칭 없음")
                continue
            qid, qtext, has_img, points = row
            kp["exam_latex"] = qtext_to_html(qtext)
            imgs = fetch_images(cur, qid)
            kp["exam_images"] = imgs
            tag = f"img×{len(imgs)}" if imgs else "no-img"
            print(f"  [{school}] q{kp['q']}: 갱신 ({tag})")

        # 2) 소하고 q23 (논술 10점) — questions 리스트에 없으면 추가
        if school == "소하고":
            qnos = {q["q"] for q in cfg["questions"]}
            if 23 not in qnos:
                row = fetch(cur, school, 23)
                if row:
                    qid, qtext, has_img, points = row
                    cfg["questions"].append({
                        "q": 23,
                        "chapter": "이차함수",  # 미정 — 사용자 보강
                        "difficulty": "상",
                        "score": 10.0,
                        "matched_yutype": 0,
                        "matched_title": "논술형 (사용자 보강 필요)",
                        "grade": "A",
                    })
                    print(f"  [소하고] q23 (논술 10점) 추가됨 — chapter/유형 사용자 보강 필요")

        cfg_path.write_text(
            json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    db.close()


if __name__ == "__main__":
    main()
