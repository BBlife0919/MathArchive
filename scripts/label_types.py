"""문항에 세부유형 라벨을 붙인다 (Claude API).

- 유형표: docs/problem_types.json (DB 단원별 후보 유형)
- 확신이 없으면 code=null 로 비워둔다. 억지 배정 금지.
- 정답지(docs/gold_labels_*.json)가 있으면 정확도를 자동 산출한다.

사용:
    # 정답지 30문항으로 모델 비교 (동기 호출, 즉시 결과)
    python3 scripts/label_types.py --gold docs/gold_labels_이차함수_30.json \
        --model claude-haiku-4-5

    # 단원 전량 (배치 API, 50% 할인)
    python3 scripts/label_types.py --chapter 이차함수 --model claude-haiku-4-5 --batch
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import re
import sqlite3
import sys
import time
import unicodedata
from pathlib import Path

import anthropic
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DB = ROOT / "db" / "mathdb.sqlite"
CATALOG = ROOT / "docs" / "problem_types.json"
OUT_DIR = ROOT / "output" / "type_labels"   # 모델 원본 응답(작업 흔적)
STORE   = ROOT / "labels"                   # 정본 라벨 스토어(DB 무관, 이관 대상)
IMG_DIR = ROOT / "docs" / "mathflat_taxonomy" / "example_images"  # 유형별 예시문항(매쓰플랫)

BATCH_SIZE = 25          # 한 호출에 담는 문항 수 (프리픽스 분산)
MAX_TEXT = 900           # 문항 본문 최대 길이(문자)
EFFORT = "medium"        # 검증된 값. low 는 출력이 잘리고 글자가 깨진다(실측) — 쓰지 말 것


def norm(s: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFC", s or ""))


def load_unit(chapter: str) -> dict:
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    for u in cat["units"]:
        if norm(u["db_chapter"]) == norm(chapter):
            return u
    raise SystemExit(f"유형표에 '{chapter}' 단원이 없습니다")


SYSTEM = """당신은 한국 고등학교 수학 문제의 유형을 분류합니다.

규칙
1. 아래 유형 목록에서 **정확히 하나**를 고릅니다.
2. 기준은 '그 풀이에서 가장 결정적인 역할을 하는 수'입니다. 여러 유형의 기법이 섞인 문제(주로
   상 난이도)는 먼저 나오는 수가 아니라, 정답에 도달하는 데 가장 결정적인 기법을 기준으로
   고릅니다. 소재(도형·실생활 등)가 아니라 해법으로 판단합니다.
3. 다음 경우에는 code 를 null 로 두십시오. 억지로 배정하지 마십시오.
   - 여러 기법이 섞였어도 결정적인 기법 하나를 특정할 수 있다면 null 이 아니라 그 유형을
     고릅니다. 두 유형이 결정력에서 정말 동급이라 가릴 수 없을 때만 null 입니다.
   - 그림에만 정보가 있어 본문만으로 판정이 불가능할 때
   - 이 단원의 문제가 아닐 때 (그때는 wrong_chapter 를 true 로)
4. confidence 는 스스로의 확신도입니다. 애매하면 반드시 낮게 주십시오.
5. reason 은 **confidence 가 medium 또는 low 일 때만** 15자 이내로 씁니다.
   high 이면 반드시 빈 문자열("")로 둡니다. 출력 낭비를 막기 위함입니다.

출력은 지정된 JSON 스키마를 따릅니다."""

SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "qid": {"type": "integer"},
                    "code": {"type": ["string", "null"]},
                    "confidence": {"type": "string",
                                   "enum": ["high", "medium", "low"]},
                    "wrong_chapter": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
                "required": ["qid", "code", "confidence", "wrong_chapter", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}


def img_block(code: str) -> dict | None:
    """유형 코드의 매쓰플랫 예시문항 이미지(few-shot). 없거나 못 읽으면 None.

    파일 하나가 깨져도(권한·중간 다운로드 손상 등) 전체 배치가 죽지 않도록,
    텍스트만으로 동작하는 쪽으로 조용히 넘어간다.
    """
    for p in IMG_DIR.glob(f"{code}.*"):
        try:
            data = p.read_bytes()
        except OSError as e:
            print(f"  ! 예시 이미지 읽기 실패 {p.name}: {e}")
            return None
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


_TYPE_BLOCKS_CACHE: dict[str, list[dict]] = {}


def type_blocks(unit: dict) -> list[dict]:
    """유형 목록 + 예시문항 이미지(있는 것만). 마지막 블록에 캐시 경계를 찍는다.

    청크(BATCH_SIZE)마다 make_msg 가 호출되므로, 같은 단원이면 이미지 재인코딩·
    재전송을 피하려고 단원(db_chapter)별로 한 번만 만들어 재사용한다.
    """
    key = unit["db_chapter"]
    if key in _TYPE_BLOCKS_CACHE:
        return _TYPE_BLOCKS_CACHE[key]
    blocks = [{"type": "text",
               "text": f'단원: {unit["db_chapter"]}\n유형 목록 ({len(unit["types"])}개, '
                       '일부는 매쓰플랫 예시문항 이미지 첨부)'}]
    for t in unit["types"]:
        img = img_block(t["code"])
        line = f'- {t["code"]} : {t["name"]}' + ('  [예시 ↓]' if img else '')
        blocks.append({"type": "text", "text": line})
        if img:
            blocks.append(img)
    blocks[-1] = dict(blocks[-1])
    blocks[-1]["cache_control"] = {"type": "ephemeral"}
    _TYPE_BLOCKS_CACHE[key] = blocks
    return blocks


def q_block(rows: list[tuple]) -> str:
    out = []
    for qid, txt, choices, diff, *_ in rows:
        t = re.sub(r"\s+", " ", txt or "")[:MAX_TEXT]
        t = t.replace("<<BOX_START>>", "[조건]").replace("<<BOX_END>>", "[/조건]")
        t = re.sub(r"<<IMG:[^>]*>>", "[그림]", t)
        c = ""
        if choices:
            try:
                items = json.loads(choices)
                c = " / ".join(
                    (x.get("text", "") if isinstance(x, dict) else str(x))[:60]
                    for x in items)
            except Exception:
                pass
        out.append(f"[qid {qid}] (난이도 {diff or '?'})\n{t}"
                   + (f"\n선지: {c}" if c else ""))
    return "\n\n".join(out)


def make_msg(unit: dict, rows: list[tuple]) -> dict:
    # 유형 목록에 이미지(few-shot)가 섞이므로 system(텍스트 전용) 대신 user 메시지에
    # 다 넣고, 그 블록 끝에 캐시 경계를 찍는다. system 은 짧은 규칙만 유지.
    content = ([{"type": "text", "text": SYSTEM}]
               + type_blocks(unit)
               + [{"type": "text",
                   "text": f"이제 다음 {len(rows)}문항을 분류하십시오.\n\n" + q_block(rows)}])
    return {
        "model": None,  # 호출부에서 채움
        "max_tokens": 12000,
        "output_config": {"format": {"type": "json_schema", "schema": SCHEMA},
                          "effort": EFFORT},
        "messages": [{"role": "user", "content": content}],
    }


def fetch(chapter: str, qids: list[int] | None) -> list[tuple]:
    con = sqlite3.connect(DB)
    con.create_function("nz", 1, norm)
    if qids:
        ph = ",".join("?" * len(qids))
        rows = con.execute(
            f"SELECT question_id, question_text, choices, difficulty, "
            f"file_source, question_number "
            f"FROM questions WHERE question_id IN ({ph})", qids).fetchall()
    else:
        rows = con.execute(
            "SELECT question_id, question_text, choices, difficulty, "
            "file_source, question_number "
            "FROM questions WHERE nz(chapter)=? AND question_text IS NOT NULL "
            "ORDER BY question_id", (norm(chapter),)).fetchall()
    con.close()
    return rows


def run_batch(client, model: str, unit: dict, rows: list[tuple],
              tag: str) -> list[dict]:
    """Batch API (50% 할인). 제출 후 폴링."""
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    chunks = [rows[i:i + BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]
    reqs = []
    for i, ch in enumerate(chunks):
        kw = make_msg(unit, ch)
        kw["model"] = model
        reqs.append(Request(custom_id=f"c{i:05d}",
                            params=MessageCreateParamsNonStreaming(**kw)))
    b = client.messages.batches.create(requests=reqs)
    print(f"  배치 제출 {b.id} · 요청 {len(reqs)}건")
    (OUT_DIR / f"batch_{tag}.txt").write_text(b.id, encoding="utf-8")

    while True:
        b = client.messages.batches.retrieve(b.id)
        c = b.request_counts
        print(f"  {b.processing_status} · 완료 {c.succeeded} / 실패 {c.errored}"
              f" / 처리중 {c.processing}      ", end="\r", flush=True)
        if b.processing_status == "ended":
            break
        time.sleep(20)
    print()

    out, us = [], [0, 0, 0]
    for res in client.messages.batches.results(b.id):
        if res.result.type != "succeeded":
            print(f"  ! {res.custom_id} {res.result.type}")
            continue
        m = res.result.message
        out += parse(next(x.text for x in m.content if x.type == "text"))
        us[0] += m.usage.input_tokens
        us[1] += m.usage.output_tokens
        us[2] += getattr(m.usage, "cache_read_input_tokens", 0) or 0
    print(f"  입력 {us[0]:,} / 출력 {us[1]:,} / 캐시읽기 {us[2]:,}")
    return out


def parse(text: str) -> list[dict]:
    """잘린 응답도 최대한 살린다.

    max_tokens 에 걸리면 JSON 배열이 중간에서 끊겨 통째로 버려진다(실측:
    86요청 중 1건). 온전한 객체만 골라내면 그 요청의 대부분을 건질 수 있다.
    """
    try:
        return json.loads(text)["results"]
    except Exception:
        out = []
        for m in re.finditer(r"\{[^{}]*\}", text):
            try:
                o = json.loads(m.group())
                if "qid" in o and "code" in o:
                    out.append(o)
            except Exception:
                pass
        print(f"  ! 응답 잘림 — {len(out)}건만 회수")
        return out


def run_sync(client, model: str, unit: dict, rows: list[tuple]) -> list[dict]:
    out, usage = [], [0, 0, 0]
    chunks = [rows[i:i + BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]
    for i, ch in enumerate(chunks, 1):
        kw = make_msg(unit, ch)
        kw.pop("model")
        r = client.messages.create(model=model, **kw)
        out += parse(next(b.text for b in r.content if b.type == "text"))
        usage[0] += r.usage.input_tokens
        usage[1] += r.usage.output_tokens
        usage[2] += getattr(r.usage, "cache_read_input_tokens", 0) or 0
        print(f"  {i}/{len(chunks)} …", end="\r", flush=True)
    print(f"  호출 {len(chunks)}회 · 입력 {usage[0]:,} / 출력 {usage[1]:,}"
          f" / 캐시읽기 {usage[2]:,}")
    return out


def score(pred: list[dict], gold_path: Path) -> None:
    g = json.loads(gold_path.read_text(encoding="utf-8"))
    truth = {x["qid"]: x["code"] for x in g["labels"]}
    moved = {x["qid"] for x in g["moved_out"]}
    by = {p["qid"]: p for p in pred}

    ok = bad = skip = 0
    wrong_rows = []
    for qid, code in truth.items():
        p = by.get(qid)
        if not p:
            continue
        if p["code"] is None:
            skip += 1
        elif p["code"] == code:
            ok += 1
        else:
            bad += 1
            wrong_rows.append((qid, code, p["code"], p["confidence"]))

    # 단원이 아닌 문항을 잡아냈는지
    caught = sum(1 for qid in moved
                 if by.get(qid) and (by[qid]["wrong_chapter"] or by[qid]["code"] is None))

    n = ok + bad + skip
    print(f"\n  정답지 {n}건 중  정답 {ok} · 오답 {bad} · 비움 {skip}")
    if ok + bad:
        print(f"  판정한 것 기준 정확도 {ok/(ok+bad)*100:.1f}%")
    print(f"  단원 오배정 {len(moved)}건 중 {caught}건 걸러냄")
    if wrong_rows:
        print("\n  오답 상세")
        for qid, t, p, c in wrong_rows:
            print(f"    {qid}  정답 {t}  →  예측 {p}  ({c})")


def write_store(pred: list[dict], chapter: str, unit: dict,
                model: str, effort: str,
                rows: list[tuple] | None = None) -> Path:
    """정본 라벨 스토어(JSONL)에 기록한다.

    DB에 직접 쓰지 않는다. 적재는 scripts/apply_type_labels.py 가 이 파일을 읽어
    SQLite/Postgres 어디로든 넣는다. (범용성 원칙: 데이터와 적재를 분리)
    """
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    subj = unit["ssen_subject"]
    d = STORE / subj
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{chapter}.jsonl"
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    valid = {t["code"] for t in unit["types"]}
    # DB 무관 자연키. 운영 Postgres 는 question_id 가 로컬과 다르므로
    # (file_source, question_number) 로 매칭해야 이관이 성립한다.
    nat = {r[0]: (r[4], r[5]) for r in (rows or [])}
    n_bad = 0
    prev = {}
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line); prev[r["qid"]] = r
    with out.open("w", encoding="utf-8") as f:
        new = {}
        for p in pred:
            code = p.get("code")
            if code and code not in valid:      # 목록 밖 코드는 버린다
                code, n_bad = None, n_bad + 1
            new[p["qid"]] = {
                "qid": p["qid"],
                "file_source": nat.get(p["qid"], (None, None))[0],
                "question_number": nat.get(p["qid"], (None, None))[1],
                "chapter": chapter,
                "subject": subj,
                "code": code,
                "confidence": p.get("confidence"),
                "wrong_chapter": p.get("wrong_chapter", False),
                "reason": (p.get("reason") or "")[:60],
                "catalog_version": cat["version"],
                "model": model,
                "effort": effort,
                "labeled_at": now,
            }
        prev.update(new)
        for r in sorted(prev.values(), key=lambda x: x["qid"]):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  라벨 스토어 → {out}  (이번 {len(pred)}건 / 누적 {len(prev)}건"
          + (f", 목록 밖 코드 {n_bad}건 폐기" if n_bad else "") + ")")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter")
    ap.add_argument("--gold")
    ap.add_argument("--model", default="claude-haiku-4-5")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--offset", type=int, default=0,
                    help="앞에서 N건 건너뛰고 시작(분할 실행용)")
    ap.add_argument("--missing", action="store_true",
                    help="스토어에 아직 없는 문항만 (중단 후 이어받기)")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--batch", action="store_true", help="Batch API(50%% 할인)")
    a = ap.parse_args()
    global EFFORT
    EFFORT = a.effort

    if a.gold:
        gp = Path(a.gold)
        g = json.loads(gp.read_text(encoding="utf-8"))
        chapter = g["chapter"]
        qids = [x["qid"] for x in g["labels"]] + [x["qid"] for x in g["moved_out"]]
    else:
        chapter, qids, gp = a.chapter, None, None
    if not chapter:
        raise SystemExit("--chapter 또는 --gold 가 필요합니다")

    unit = load_unit(chapter)
    rows = fetch(chapter, qids)
    if a.missing:
        # offset 산술보다 안전하다. 응답 잘림 등으로 중간이 비어도 정확히 메운다.
        store = STORE / unit["ssen_subject"] / f"{chapter}.jsonl"
        done = set()
        if store.exists():
            done = {json.loads(x)["qid"]
                    for x in store.read_text(encoding="utf-8").splitlines() if x.strip()}
        before = len(rows)
        rows = [r for r in rows if r[0] not in done]
        print(f"  이어받기: 전체 {before:,} · 완료 {len(done):,} · 남음 {len(rows):,}")
    if a.offset:
        rows = rows[a.offset:]
    if a.limit:
        rows = rows[:a.limit]
    print(f"모델 {a.model} · 단원 {chapter} · 문항 {len(rows)}건 "
          f"· 유형 {len(unit['types'])}개")

    client = anthropic.Anthropic()
    t0 = time.time()
    tag0 = f"{chapter}_{a.model.replace(chr(99)+'laude-','')}"
    pred = (run_batch(client, a.model, unit, rows, tag0) if a.batch
            else run_sync(client, a.model, unit, rows))
    print(f"  소요 {time.time()-t0:.0f}초")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tag = a.model.replace("claude-", "")
    out = OUT_DIR / f"{chapter}_{tag}{'_gold' if gp else ''}.json"
    out.write_text(json.dumps(pred, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  저장 → {out}")

    if gp:
        score(pred, gp)
    else:
        write_store(pred, chapter, unit, a.model, a.effort, rows)


if __name__ == "__main__":
    main()
