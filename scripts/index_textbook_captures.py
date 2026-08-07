"""무제 폴더의 교재 캡처 파일을 학교/문제번호로 인덱싱하고
각 학교 config(key_problems)에 capture_files / shared_with 를 주입한다.

파일명 패턴
- "광명15.png"             → 광명고 15
- "광문18_1.png"           → 광문고 18 (part 1)
- "광북17 운산14.png"       → 광명북고 17 + 운산고 14 (공유)
- "광명17 광문17 명문21 소하23.png"  → 4학교 공유
"""
from __future__ import annotations
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PA = ROOT / "output" / "pirate_analysis"
CAPTURE_DIR = PA / "무제 폴더"
CONFIGS = PA / "configs"

SCHOOL_CODE = {
    "광명": "광명고",
    "광북": "광명북고",
    "광문": "광문고",
    "명문": "명문고",
    "소하": "소하고",
    "운산": "운산고",
}

TOKEN_RE = re.compile(r"(광명|광북|광문|명문|소하|운산)(\d+)(?:_(\d+))?")


def parse_filename(stem: str) -> list[tuple[str, int, int | None]]:
    """파일명에서 (학교코드, 문제번호, 파트번호 or None) 리스트 추출."""
    stem = unicodedata.normalize("NFC", stem)
    found = []
    for m in TOKEN_RE.finditer(stem):
        code = m.group(1)
        qno = int(m.group(2))
        part = int(m.group(3)) if m.group(3) else None
        found.append((code, qno, part))
    return found


def build_index() -> dict:
    """index[학교short][문제번호] = [파일이름, ...]."""
    if not CAPTURE_DIR.exists():
        raise SystemExit(f"capture dir not found: {CAPTURE_DIR}")

    index: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    sharing: dict[str, list[str]] = defaultdict(list)

    files = sorted(p for p in CAPTURE_DIR.iterdir() if p.suffix.lower() == ".png")
    for p in files:
        tokens = parse_filename(p.stem)
        if not tokens:
            continue
        schools = sorted({SCHOOL_CODE[c] for c, _, _ in tokens})
        for code, qno, part in tokens:
            short = SCHOOL_CODE[code]
            index[short][qno].append(p.name)
        if len(schools) > 1:
            for s in schools:
                others = [o for o in schools if o != s]
                sharing[f"{p.name}"] = others
    return {"index": {k: dict(v) for k, v in index.items()}, "files": [p.name for p in files]}


def inject_into_configs(index: dict):
    SCHOOLS = ["광문고", "광명고", "광명북고", "명문고", "소하고", "운산고"]
    for short in SCHOOLS:
        cfg_path = CONFIGS / f"{short}.json"
        if not cfg_path.exists():
            print(f"skip: {cfg_path} not found")
            continue
        cfg = json.loads(cfg_path.read_text())
        kps = cfg.get("key_problems", [])
        s_index = index["index"].get(short, {})
        for kp in kps:
            qno = kp["q"]
            files = sorted(s_index.get(qno, []))
            kp["capture_files"] = files
            shared = set()
            for fn in files:
                stem = Path(fn).stem
                tokens = parse_filename(stem)
                for c, q, _ in tokens:
                    other_short = SCHOOL_CODE[c]
                    if other_short != short and q == qno:
                        shared.add(other_short)
            kp["shared_with"] = sorted(shared)
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"updated {cfg_path.name}: " + ", ".join(
            f"q{kp['q']}={'O' if kp['capture_files'] else 'X'}" for kp in kps
        ))


def main():
    idx = build_index()
    print(f"scanned {len(idx['files'])} files in {CAPTURE_DIR}")
    for short, qmap in idx["index"].items():
        s = ", ".join(f"{q}({len(fs)})" for q, fs in sorted(qmap.items()))
        print(f"  {short}: {s}")
    inject_into_configs(idx)


if __name__ == "__main__":
    main()
