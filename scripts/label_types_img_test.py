"""예시문항 이미지(매쓰플랫 세부유형 repProblemImageUrl) few-shot 효과 검증용.

label_types.py 는 건드리지 않는다(정본 파이프라인 보존). 이 스크립트는 같은 로직에
유형 후보마다 예시 이미지 1장을 끼워 넣어 효과만 비교하는 1회성 실험 스크립트다.

사용:
    python3 scripts/label_types_img_test.py
"""
from __future__ import annotations

import base64
import json
import mimetypes
import sys
import time
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from label_types import (  # noqa: E402
    ROOT, SYSTEM, SCHEMA, MAX_TEXT, load_unit, fetch, q_block, parse, score,
)

IMG_DIR = ROOT / "docs" / "mathflat_taxonomy" / "example_images"
OUT_DIR = ROOT / "output" / "type_labels"
MODEL = "claude-opus-5"
EFFORT = "high"

GOLD_FILES = [
    "docs/gold_labels_이차함수_mathflat.json",
    "docs/gold_labels_부등식_mathflat.json",
    "docs/gold_labels_도함수의활용_mathflat.json",
    "docs/gold_labels_확률의뜻과활용_mathflat.json",
    "docs/gold_labels_등차수열_mathflat.json",
]


def img_block(code: str) -> dict | None:
    for p in IMG_DIR.glob(f"{code}.*"):
        data = p.read_bytes()
        media_type = mimetypes.guess_type(p.name)[0] or "image/png"
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": base64.b64encode(data).decode("ascii"),
            },
        }
    return None


def build_content(unit: dict, rows: list[tuple]) -> list[dict]:
    blocks = [{"type": "text", "text": SYSTEM}]
    blocks.append({"type": "text",
                    "text": f'단원: {unit["db_chapter"]}\n유형 목록 ({len(unit["types"])}개, '
                            '일부는 실제 매쓰플랫 예시문항 이미지 첨부)'})
    n_img = 0
    for t in unit["types"]:
        img = img_block(t["code"])
        if img:
            blocks.append({"type": "text", "text": f'- {t["code"]} : {t["name"]}  [예시 ↓]'})
            blocks.append(img)
            n_img += 1
        else:
            blocks.append({"type": "text", "text": f'- {t["code"]} : {t["name"]}'})
    blocks[-1] = dict(blocks[-1])
    blocks[-1]["cache_control"] = {"type": "ephemeral"}
    blocks.append({"type": "text",
                    "text": f"이제 다음 {len(rows)}문항을 분류하십시오.\n\n" + q_block(rows)})
    print(f"  예시 이미지 {n_img}/{len(unit['types'])}개 첨부")
    return blocks


def main() -> None:
    client = anthropic.Anthropic()
    for gf in GOLD_FILES:
        gp = ROOT / gf
        g = json.loads(gp.read_text(encoding="utf-8"))
        chapter = g["chapter"]
        qids = [x["qid"] for x in g["labels"]] + [x["qid"] for x in g["moved_out"]]
        unit = load_unit(chapter)
        rows = fetch(chapter, qids)
        print(f"\n=== {chapter} ({len(rows)}문항, 유형 {len(unit['types'])}개) ===")

        content = build_content(unit, rows)
        kw = {
            "model": MODEL,
            "max_tokens": 12000,
            "output_config": {"format": {"type": "json_schema", "schema": SCHEMA},
                              "effort": EFFORT},
            "messages": [{"role": "user", "content": content}],
        }
        t0 = time.time()
        r = client.messages.create(**kw)
        pred = parse(next(b.text for b in r.content if b.type == "text"))
        print(f"  소요 {time.time()-t0:.0f}초 · 입력 {r.usage.input_tokens:,} / "
              f"출력 {r.usage.output_tokens:,} / "
              f"캐시읽기 {getattr(r.usage, 'cache_read_input_tokens', 0) or 0:,} / "
              f"캐시생성 {getattr(r.usage, 'cache_creation_input_tokens', 0) or 0:,}")

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / f"{chapter}_opus-5_gold_img.json"
        out.write_text(json.dumps(pred, ensure_ascii=False, indent=2), encoding="utf-8")
        score(pred, gp)


if __name__ == "__main__":
    main()
