"""학교별 분석 데이터 + 통합리포트의 전략/특성을 합쳐 학교별 config 생성."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PA = ROOT / "output" / "pirate_analysis"
WORK = PA / "work"
CONFIGS = PA / "configs"

# 학교명 (긴/짧은) 매핑
SCHOOLS = {
    "광명고":   {"full": "광명고등학교",   "ranges": "다항식의 연산 ~ 이차함수"},
    "광명북고": {"full": "광명북고등학교", "ranges": "다항식의 연산 ~ 이차함수 (고차방정식 포함)"},
    "명문고":   {"full": "명문고등학교",   "ranges": "다항식의 연산 ~ 복소수와 이차방정식"},
    "소하고":   {"full": "소하고등학교",   "ranges": "다항식의 연산 ~ 이차함수의 최대·최소"},
    "운산고":   {"full": "운산고등학교",   "ranges": "다항식의 연산 ~ 이차함수의 최대·최소"},
}


def main():
    consolidated = json.loads((CONFIGS / "광명지역_통합리포트.json").read_text())
    school_strats = {s["name"]: s for s in consolidated["schools"]}

    for short, meta in SCHOOLS.items():
        data_path = WORK / f"school_data_{short}.json"
        if not data_path.exists():
            print(f"skip: {data_path} not found")
            continue
        data = json.loads(data_path.read_text())
        full_name = meta["full"]
        s_meta = school_strats.get(full_name)
        if not s_meta:
            print(f"warn: no strategy for {full_name}")
            continue

        # 시험대비전략을 v3 포맷으로 변환 (key/value)
        strategy = [
            {"key": st["k"], "value": st["v"]}
            for st in s_meta["strategies"]
        ]

        # instructor_comment: 시험특성 + 압축
        comment = (
            f"{s_meta['characteristics']} "
            f"이번 핵심문제 4개는 모두 우리 교재 STEP1·STEP2 핵심 유형으로 커버되며, "
            f"풀이 절차가 동형 또는 유사 패턴으로 정리되어 있다. "
            f"교재 N회독 + 핵심노트 3회독으로 시험장에서 즉시 인출 가능."
        )

        cfg = {
            "school": full_name,
            "short_name": short,
            "exam_title": "2026학년도 1학기 중간고사",
            "subject": "공통수학1",
            "subject_range": meta["ranges"],
            "grade": 1,
            "instructor": "이영우T",
            "academy": "이음학원",
            "questions": data["questions"],
            "key_problems": data["key_problems"],
            "instructor_comment": comment,
            "strategy": strategy,
            "note_intro": "이영우T가 직접 작성한 핵심만 모은 핵심노트",
            "note_sub": "시험 출제 핵심 패턴을 한 줄로 정리한 직강 노트",
            "note_sample_images": ["note_sample_1.png", "note_sample_2.png", "note_sample_3.png"],
        }
        out = CONFIGS / f"{short}.json"
        out.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
