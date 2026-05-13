#!/usr/bin/env python3
"""학교별 적중분석 카드뉴스 PDF 생성기 (v5).

v4 대비 변경사항:
- 표지 재설계 (사진 확대, "이영우T" 강조, 우측하단 흰 로고, 제목 "완벽해부 & 1등급 처방전")
- 페이지 순서 변경:
  1) 표지 → 2) 프롤로그 → 3) 고득점 3단계전략 → 4) 총평(학교분석카드)
  → 5) 출제그리드(도넛) → 6) 분석도표(적중표) → 7) 시험대비전략(강조)
  → 8~11) 핵심문제 4개 (무제폴더 실제 교재 캡처 사용)
  → 12) "어떻게 이런 적중과 준비가 가능할까요?"
  → 13) 6,000+ 보유 (HWP 파일목록 캡처)
  → 14) 매쓰아카이브 광고 (검색화면 캡처)
  → 15) 핵심노트 광고 (부채꼴)
  → 16) 이영우T의 약속 (closing)
- 도넛: 정확한 원형 + 퍼센티지 안 + 라벨 옆 큰 글씨
- 학교카드 임팩트 강화 (색상블록, 큰 폰트, 줄배열 변형)
- 시험대비전략 키워드 강조 (highlight spans)
- 핵심문제 우측 박스에 무제폴더 실제 교재 캡처 이미지 (없으면 fabricated_latex 폴백)
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PA = ROOT / "output" / "pirate_analysis"
ASSETS = PA / "assets"
CONFIGS = PA / "configs"
CAPTURE_DIR = PA / "무제 폴더"

PA_MIDDLE = ROOT / "output" / "pirate_analysis_middle"
CONFIGS_MIDDLE = PA_MIDDLE / "configs"
CAPTURE_DIR_MIDDLE = ROOT / "raw_middle" / "스샷"
EXAM_CAPTURE_DIRS_MIDDLE = [PA_MIDDLE / "원본사진"]


def img_data_uri(path: Path) -> str:
    if not path or not path.exists():
        return ""
    ext = path.suffix.lstrip(".").lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def asset(school_short: str, name: str) -> Path:
    if not name:
        return ASSETS / "_missing_"
    p = ASSETS / school_short / name
    if p.exists():
        return p
    return ASSETS / name


CAPTURE_CLEAN_DIR = PA / "무제_clean"
EXAM_CAPTURE_DIRS = [PA / "원본사진_clean", PA / "원본사진", PA / "시험지_원본"]


def capture_path(filename: str, grade_level: str = "high") -> Path:
    """캡처 파일 경로 — 무제 폴더(고등) 또는 스샷 폴더(중등)."""
    target_nfc = unicodedata.normalize("NFC", filename)
    if grade_level == "middle":
        dirs = (CAPTURE_DIR_MIDDLE,)
    else:
        dirs = (CAPTURE_DIR, CAPTURE_CLEAN_DIR)
    for d in dirs:
        if not d.exists():
            continue
        for p in d.iterdir():
            if unicodedata.normalize("NFC", p.name) == target_nfc:
                return p
    return dirs[0] / filename


SCHOOL_CODE_REVERSE = {
    "광명고": "광명",
    "광명북고": "광북",
    "광문고": "광문",
    "명문고": "명문",
    "소하고": "소하",
    "운산고": "운산",
    "철산중": "철산",
}


def exam_capture_paths(school_short: str, qno, grade_level: str = "high") -> list[Path]:
    """원본사진/<학교약자><번호>(_파트).png 또는 <학교약자>논술N.png — 매칭 리스트."""
    code = SCHOOL_CODE_REVERSE.get(school_short)
    if not code:
        return []
    prefix = f"{code}{qno}"
    dirs = EXAM_CAPTURE_DIRS_MIDDLE if grade_level == "middle" else EXAM_CAPTURE_DIRS
    out: list[Path] = []
    for d in dirs:
        if not d.exists():
            continue
        for p in d.iterdir():
            if p.suffix.lower() != ".png":
                continue
            nfc = unicodedata.normalize("NFC", p.stem)
            if nfc == prefix or nfc.startswith(prefix + "_") or nfc.startswith(prefix + " "):
                out.append(p)
        if out:
            break  # 첫 매칭 폴더의 결과만 사용
    out.sort()
    return out


def load_consolidated(path: Path | None = None) -> dict:
    p = path if path else (CONFIGS / "광명지역_통합리포트.json")
    return json.loads(p.read_text())


# ─────────────────────────────────────────────────────────────────────────
# 강조 (시험대비전략 키워드 색상 span)
HIGHLIGHT_PATTERNS = [
    r"교과서[^\s,·]+",
    r"필수\s*유형\s*문제",
    r"교육청\s*기출",
    r"모의고사\s*기출(?:\s*변형)?",
    r"핵심노트",
    r"STEP\s*\d+",
    r"\d+\s*회독",
    r"N\s*회독",
    r"동형",
    r"\d+\s*주\s*전",
    r"우리\s*교재",
    r"기출\s*변형",
    r"풀이\s*절차",
    r"매주\s*\d+회",
    r"매일\s*\d+세트",
    r"실수\s*방지",
    r"오답노트",
    r"시간\s*분배",
    r"오답\s*복기",
    r"기계적\s*풀이",
    r"변별\s*문항",
    r"변별력\s*문제",
    r"서울\s*[·,/]\s*경기\s*학군지\s*기출",
    r"서울·경기\s*학군지\s*기출",
    r"서울\s*경기\s*학군지\s*기출",
    r"학군지\s*기출",
    r"학군지\s*심화\s*기출",
    r"전략",
    r"1등급",
    r"양치기",
    r"낯선\s*문제",
    r"응용력",
    r"실전\s*연습",
    r"실전\s*동형",
    r"시간\s*제한",
    r"즉시\s*인출",
    r"50선",
    r"패턴",
    r"구조적",
    r"정확히",
    r"빠르고\s*정확한",
]

# 한 글자 미만이면 굳이 hl 안 함. 정렬은 길이 내림차순 (긴 것 먼저)
_HL_SORTED = sorted(HIGHLIGHT_PATTERNS, key=len, reverse=True)
_HL_RE = re.compile("|".join(f"({p})" for p in _HL_SORTED))


def highlight_keywords(text: str) -> str:
    return _HL_RE.sub(lambda m: f"<mark class='hl'>{m.group(0)}</mark>", text)


# ─────────────────────────────────────────────────────────────────────────
def render_q_table(questions: list[dict]) -> str:
    rows = []
    for q in questions:
        rows.append(
            f"<tr>"
            f"<td class='c qno'>{q['q']}</td>"
            f"<td>{q['chapter']}</td>"
            f"<td class='c'>{q['score']}</td>"
            f"<td class='c'><span class='dpill diff-{q['difficulty']}'>{q['difficulty']}</span></td>"
            f"<td class='match'>유형{q['matched_yutype']} — {q['matched_title']}</td>"
            f"<td class='c'><span class='gpill grade-{q['grade']}'>{q['grade']}</span></td>"
            f"</tr>"
        )
    return "\n".join(rows)


def render_school_strategies(strats: list[dict]) -> str:
    out = []
    for i, st in enumerate(strats):
        v = highlight_keywords(st["v"])
        out.append(
            f"<div class='strat-card'>"
            f"<div class='strat-num'>0{i+1}</div>"
            f"<div class='strat-key'>{st['k']}</div>"
            f"<div class='strat-val'>{v}</div>"
            f"</div>"
        )
    return "\n".join(out)


def render_insta_cover(school_short: str, school_full: str, instructor: str,
                        logo_uri: str, instructor_uri: str) -> str:
    """매거진 포스터 스타일 표지 — 크림 배경 + 검정 프레임 + 빨강 도장."""
    photo_html = (
        f"<img class='ic2-photo' src='{instructor_uri}' alt='{instructor}'/>"
        if instructor_uri else ""
    )
    logo_html = (
        f"<img class='ic2-logo' src='{logo_uri}' alt='이음학원'/>"
        if logo_uri else ""
    )
    return f"""
<section class="page insta-cover">
  <div class="ic2-frame">
    <div class="ic2-top-bar">
      <span class="ic2-volume">No. {hash(school_short) % 100:02d} / 2026</span>
      <span class="ic2-meta">M A T H A R C H I V E &middot; 이음학원</span>
    </div>
    <div class="ic2-mid">
      <div class="ic2-pretitle">2026학년도 1학기 중간고사 · 적중분석 리포트</div>
      <div class="ic2-school">{school_short}</div>
      <div class="ic2-divider"></div>
      <div class="ic2-subject-row">
        <span class="ic2-subject">수학 내신 적중 분석</span>
        <span class="ic2-stamp">
          <span class="ic2-stamp-num">100</span>
          <span class="ic2-stamp-unit">% HIT</span>
        </span>
      </div>
    </div>
    <div class="ic2-bottom">
      <div class="ic2-photo-wrap">{photo_html}</div>
      <div class="ic2-info">
        <div class="ic2-name">이영우 <span class="ic2-name-t">T</span></div>
        <div class="ic2-role">M A T H &nbsp; I N S T R U C T O R</div>
      </div>
      <div class="ic2-logo-wrap">{logo_html}</div>
    </div>
  </div>
</section>
"""


def render_prologue(consolidated: dict) -> str:
    pr = consolidated["prologue"]
    body_lines = "<br><br>".join(highlight_keywords(b) for b in pr["body"])
    return f"""
<section class="page slide-page prologue-page">
  <div class="badge">PROLOGUE</div>
  <div class="prologue-q">"{pr['title']}"</div>
  <div class="prologue-body">{body_lines}</div>
</section>
"""


def render_solution(consolidated: dict) -> str:
    sol = consolidated["solution"]
    steps = "\n".join(
        f"<div class='sol-step'>"
        f"<div class='sol-num'>{i+1}️⃣</div>"
        f"<div class='sol-body'>"
        f"<div class='sol-key'>{st['k']}</div>"
        f"<div class='sol-val'>{highlight_keywords(st['v'])}</div>"
        f"</div></div>"
        for i, st in enumerate(sol["steps"])
    )
    return f"""
<section class="page slide-page solution-page">
  <div class="badge dark">📢 {sol['header']}</div>
  <div class="sol-title">{sol['title']}</div>
  <div class="sol-intro">{sol['intro']}</div>
  <div class="sol-steps">{steps}</div>
</section>
"""


def render_school_card(school_meta: dict) -> str:
    """총평 페이지 — 임팩트 강화 (색상블록, 큰 폰트, 줄배열 변형)."""
    name = school_meta["name"]
    tag = school_meta["tagline"]
    chars = highlight_keywords(school_meta["characteristics"])
    return f"""
<section class="page slide-page school-card-page">
  <div class="badge red">총평 · OVERALL</div>
  <div class="sc-name">{name}</div>
  <div class="sc-tag">"{tag}"</div>
  <div class="sc-chars">
    <div class="sc-chars-head">시험 특성 한눈에</div>
    <div class="sc-chars-body">{chars}</div>
  </div>
</section>
"""


def render_strategy_page(school_meta: dict, instructor: str, comment: str) -> str:
    strats_html = render_school_strategies(school_meta["strategies"])
    return f"""
<section class="page strategy-page">
  <div class="badge red">시험대비 전략</div>
  <div class="strat-title">{school_meta['name']} 맞춤 전략</div>
  <div class="strat-grid-v5">
    {strats_html}
  </div>
  <div class="comment">
    <span class="hdr">{instructor} 코멘트</span>
    {comment}
  </div>
</section>
"""


def _key_block_inner(school_short: str, kp: dict, grade_level: str) -> str:
    """시험문항+매칭 카드 inner HTML (head + body) 반환. 단독/페어 페이지 공통."""
    # 좌측 시험출제 — 우선순위: 시험지_원본/ 캡처 > DB exam_images > latex
    exam_files = exam_capture_paths(school_short, kp["q"], grade_level)
    if exam_files:
        exam_imgs = "".join(
            f"<img class='exam-img' src='{img_data_uri(p)}'/>" for p in exam_files
        )
        exam_body = f"<div class='exam-stack'>{exam_imgs}</div>"
    else:
        latex_part = f"<div class='exam-latex'>{kp['exam_latex']}</div>"
        db_imgs = []
        for rel in kp.get("exam_images", []):
            p = ROOT / rel if not Path(rel).is_absolute() else Path(rel)
            uri = img_data_uri(p)
            if uri:
                db_imgs.append(f"<img class='exam-fig-img' src='{uri}'/>")
        if db_imgs:
            exam_body = latex_part + f"<div class='exam-figs'>{''.join(db_imgs)}</div>"
        else:
            exam_body = latex_part

    capture_files = kp.get("capture_files") or []
    shared_with = kp.get("shared_with") or []
    cap_imgs = []
    for fn in capture_files:
        uri = img_data_uri(capture_path(fn, grade_level))
        if uri:
            cap_imgs.append(f"<img class='cap-img' src='{uri}'/>")
    if cap_imgs:
        match_block = f"<div class='cap-stack'>{''.join(cap_imgs)}</div>"
    else:
        fab = kp.get("fabricated_latex") or ""
        if fab:
            match_block = (
                f"<div class='match-latex'>{fab}</div>"
                f"<div class='cap-fallback'>※ 교재 페이지 캡처 추가 예정</div>"
            )
        else:
            match_block = "<div class='card-empty'>(교재 매칭 본문 없음)</div>"

    shared_pill = ""
    if shared_with:
        shared_pill = (
            "<div class='shared-pill'>"
            f"공유 적중: {', '.join(shared_with)}"
            "</div>"
        )

    comment_html = highlight_keywords(kp["comment"])

    return f"""
  <div class="key-head">
    <div class="key-no-pill">시험지 {kp['q']}번</div>
    <div class="key-meta">{kp['topic']} · 배점 {kp['score']} · 난이도 <span class='hi-{kp['difficulty']}'>{kp['difficulty']}</span></div>
  </div>
  <div class="key-body">
    <div class="exam-card">
      <div class="card-head exam-head">시험 출제 문항</div>
      {exam_body}
    </div>
    <div class="note-card">
      <div class="card-head note-head">{kp['matched_title']}</div>
      {match_block}
      <div class="match-cap">{comment_html}</div>
      {shared_pill}
    </div>
  </div>
"""


def render_key_problem(school_short: str, kp: dict, idx: int, total: int,
                       grade_level: str = "high") -> str:
    inner = _key_block_inner(school_short, kp, grade_level)
    return f"""
<section class="page key-page">
  <div class="key-counter">핵심문제 {idx} / {total}</div>
  {inner}
</section>
"""


def render_key_pair(school_short: str, kp1: dict, kp2: dict, idx: int, total: int,
                    grade_level: str = "high") -> str:
    inner1 = _key_block_inner(school_short, kp1, grade_level)
    inner2 = _key_block_inner(school_short, kp2, grade_level)
    return f"""
<section class="page key-page paired">
  <div class="key-counter">핵심문제 {idx} / {total}</div>
  <div class="key-pair-half">{inner1}</div>
  <div class="key-pair-half">{inner2}</div>
</section>
"""


def chart_payload(questions: list[dict]) -> str:
    chap_count = Counter(q["chapter"] for q in questions)
    diff_count = Counter(q["difficulty"] for q in questions)
    diff_order = ["하", "중", "상"]
    diff_labels = [d for d in diff_order if d in diff_count]
    diff_data = [diff_count[d] for d in diff_labels]
    chap_labels = list(chap_count.keys())
    chap_data = [chap_count[c] for c in chap_labels]
    return json.dumps({
        "chapter": {"labels": chap_labels, "data": chap_data},
        "difficulty": {"labels": diff_labels, "data": diff_data},
    }, ensure_ascii=False)


def render_how_page() -> str:
    """'어떻게 이런 적중과 준비가 가능할까요?' 페이지."""
    return """
<section class="page slide-page how-page">
  <div class="badge red">HOW?</div>
  <div class="how-q">"어떻게 이런 적중과 준비가<br>가능할까요?"</div>
  <div class="how-answer">
    이영우T가 직접 구축한 <mark class='hl'>6,000+ 기출 데이터베이스</mark>와<br>
    학교별 출제 패턴 분석, 그리고 <mark class='hl'>핵심노트</mark>로 정리된<br>
    풀이 절차의 결합이 만들어낸 결과입니다.
  </div>
  <ul class="how-list">
    <li><b>1.</b> <mark class='hl'>학교별 5년치 기출</mark> 누적 분석으로 출제 흐름 파악</li>
    <li><b>2.</b> <mark class='hl'>자체 교재의 핵심유형들과 최심화문제들</mark>로 모든 문제 커버</li>
    <li><b>3.</b> 직접 작성한 <mark class='hl'>핵심노트</mark>로 풀이 절차를 한 줄로 압축</li>
    <li><b>4.</b> <mark class='hl'>매쓰아카이브</mark> 검색 시스템으로 즉시 인출·연습</li>
    <li><b>5.</b> <mark class='hl'>서울·경기 주요 지역 기출</mark>들로 실전 연습</li>
  </ul>
</section>
"""


def render_student_case_page() -> str:
    """총평과 출제그리드 사이 — 70→95점 학생 사례 화두."""
    return """
<section class="page slide-page case-page">
  <div class="badge red">REAL CASE · 실제 수강생 결과</div>
  <div class="case-headline">
    <div class="case-question">"7~80점 맞던 학생이<br>겨우 <mark class='hl'>두 달</mark> 수강하고<br><span class='case-pop'>95점</span>을 받았습니다."</div>
  </div>
  <div class="case-scoreboard">
    <div class="case-before">
      <div class="case-label">BEFORE</div>
      <div class="case-score">70<span class="case-unit">점대</span></div>
    </div>
    <div class="case-arrow">▶</div>
    <div class="case-after">
      <div class="case-label">AFTER · 2개월</div>
      <div class="case-score">95<span class="case-unit">점</span></div>
      <div class="case-note">계산 실수 1개 외 전체 정답</div>
    </div>
  </div>
  <div class="case-delta">
    <span class="case-delta-num">+15~20점</span>
    <span class="case-delta-text">단 두 달 만의 점수 상승</span>
  </div>
  <div class="case-q">"<b>어떻게 이게 가능했을까?</b>"</div>
  <div class="case-tease">정답은 다음 페이지부터 차근차근 보여드립니다.</div>
</section>
"""


def render_clinic_page(c_summary: str, c_chap1: str, c_chap2: str) -> str:
    """'어떻게~' 다음 — 학생별 취약유형 클리닉 자료 페이지 (2컷 큰 레이아웃)."""
    s_html = f"<img src='{c_summary}' class='clinic-img'/>" if c_summary else ""
    chap_uri = c_chap1 or c_chap2
    a_html = f"<img src='{chap_uri}' class='clinic-img'/>" if chap_uri else ""
    return f"""
<section class="page slide-page clinic-page">
  <div class="badge red">PERSONAL CLINIC · 개인별 약점 처방전</div>
  <div class="clinic-title">교재·심화 수업에 더해<br><mark class='hl'>학생별 취약 유형 분석 → 1:1 클리닉 자료</mark> 제공</div>
  <div class="clinic-sub">전국 동일 학년과 비교한 <b>유형별 정답률 데이터</b>로
  학생 한 명 한 명의 빈틈을 잡아내고, <b>맞춤 클리닉 학습지</b>로 끝까지 메꿉니다.</div>
  <div class="clinic-grid">
    <div class="clinic-card">
      <div class="clinic-card-tag">① 학습 내역 추적</div>
      {s_html}
      <div class="clinic-card-cap">한 달 단위로 풀이량·정답률 누적 관리</div>
    </div>
    <div class="clinic-card">
      <div class="clinic-card-tag">② 단원별 유형 분석 / 취약 유형 처방</div>
      {a_html}
      <div class="clinic-card-cap">우수 유형·취약 유형을 시각화하고 클리닉 학습지로 빈틈 보강</div>
    </div>
  </div>
  <div class="clinic-bottom-line">자체 교재로 <b>출제 유형을 모두 커버</b>한 다음,
  학생별 취약점은 <b>개인 클리닉</b>으로 빈틈없이 마무리합니다.</div>
</section>
"""


def render_volume_page(consolidated: dict, hwp_uri: str) -> str:
    dv = consolidated["data_volume"]
    details = "\n".join(f"<li>{x}</li>" for x in dv["details"])
    img_html = f"<img class='volume-screenshot' src='{hwp_uri}'/>" if hwp_uri else ""
    return f"""
<section class="page slide-page data-page">
  <div class="badge yellow">{dv['header']}</div>
  <div class="data-main">{dv['main']}</div>
  <div class="data-sub">{dv['sub']}</div>
  <div class="volume-grid">
    <ul class="data-list">
      {details}
    </ul>
    {img_html}
  </div>
  <div class="data-callout">
    <span class="big-num">6,000<span class="unit">+</span></span>
    <span class="big-label">기출 문항 자체 보유</span>
  </div>
</section>
"""


def render_practice_page(p1_uri: str, p2_uri: str) -> str:
    """매쓰아카이브 다음 페이지 — 실전동형모의고사 광고 (블랙앤화이트)."""
    p1 = f"<img class='pt-img pt-img-1' src='{p1_uri}'/>" if p1_uri else ""
    p2 = f"<img class='pt-img pt-img-2' src='{p2_uri}'/>" if p2_uri else ""
    return f"""
<section class="page slide-page practice-page">
  <div class="badge dark">REAL TEST · 실전동형모의고사</div>
  <div class="pt-title">매쓰아카이브로 만든 <mark class='hl'>실전동형모의고사</mark><br><span class='pt-hl'>+ 시간제한 훈련</span></div>
  <div class="pt-sub">시험지 적중률만으로는 부족합니다. 시험장에서 <mark class='hl'>같은 난이도·같은 시간</mark>으로
  반복 연습한 학생만이 1등급을 가져갑니다.</div>
  <div class="pt-features">
    <div class="pt-feat"><span class="pt-num">①</span><span class="pt-feat-text"><b>학교별 동형</b> 시험지를 직접 제작</span></div>
    <div class="pt-feat"><span class="pt-num">②</span><span class="pt-feat-text"><b>실제 시험 시간·난이도</b> 그대로 응시</span></div>
    <div class="pt-feat"><span class="pt-num">③</span><span class="pt-feat-text"><b>오답 즉시 분석</b> → 핵심노트 보강</span></div>
  </div>
  <div class="pt-photos">
    <div class="pt-photo-card pt-photo-1">
      {p1}
      <div class="pt-photo-cap">학원 자습실 — 시험과 동일한 환경에서 실전 모의고사 응시</div>
    </div>
    <div class="pt-photo-card pt-photo-2">
      {p2}
      <div class="pt-photo-cap">매쓰아카이브 자체 제작 — 학교별 동형 모의고사 시험지</div>
    </div>
  </div>
  <div class="pt-bottom-line">시험 적중 + 실전 훈련 = <b>1등급 직행 루트</b>. 시험장이 첫 시험이 되지 않게 만듭니다.</div>
</section>
"""


def render_matharchive_page(matharchive_uri: str) -> str:
    img_html = (
        f"<img class='ma-screenshot' src='{matharchive_uri}'/>"
        if matharchive_uri
        else "<div class='ma-placeholder'>(매쓰아카이브 검색 화면)</div>"
    )
    return f"""
<section class="page slide-page matharchive-page">
  <div class="badge dark">MATHARCHIVE · 자체 검색시스템</div>
  <div class="ma-title">학교·단원·난이도별로 <mark class='hl'>즉시 인출</mark>하는<br><span class='hl-text'>매쓰아카이브 검색 시스템</span></div>
  <div class="ma-sub">필요한 학교의 기출문제를 단원·난이도별로 즉시 검색해서 시험지로 묶어내는 자체 시스템.
  현장에서 바로 학생 맞춤 문제를 뽑을 수 있다.</div>
  <div class="ma-features">
    <div class="ma-feat"><span class="ma-feat-num">①</span><b>지역·학교별</b> 필터</div>
    <div class="ma-feat"><span class="ma-feat-num">②</span><b>단원·난이도별</b> 검색</div>
    <div class="ma-feat"><span class="ma-feat-num">③</span><b>검색 결과</b> → 시험지 즉시 생성</div>
  </div>
  <div class="ma-screenshot-wrap">{img_html}</div>
  <div class="ma-bottom-line">시험지 한 장 만드는 데 <b>5분</b>이면 충분. 학교별 약점 분석에 따라 매주 다른 시험지 제공.</div>
</section>
"""


def render_note_fan(school_short: str, intro: str, sub: str, images: list[str]) -> str:
    uris = [img_data_uri(asset(school_short, n)) for n in images]
    uris = [u for u in uris if u]
    if not uris:
        return ""
    fan_positions = [
        {"left": "8%",  "rot": -14, "z": 1, "top": "10%"},
        {"left": "22%", "rot": -7,  "z": 2, "top": "5%"},
        {"left": "38%", "rot": 0,   "z": 3, "top": "2%"},
        {"left": "54%", "rot": 7,   "z": 2, "top": "5%"},
        {"left": "70%", "rot": 14,  "z": 1, "top": "10%"},
    ]
    cards = []
    for i, pos in enumerate(fan_positions):
        u = uris[i % len(uris)]
        cards.append(
            f"<img src='{u}' class='note-fan-card' "
            f"style='left:{pos['left']}; top:{pos['top']}; "
            f"transform: rotate({pos['rot']}deg); z-index:{pos['z']};'/>"
        )
    return f"""
<section class="page note-page slide-page">
  <div class="badge dark">핵심노트 견본</div>
  <div class="note-title">{intro}</div>
  <div class="note-sub">{sub}</div>
  <div class="note-fan">
    {''.join(cards)}
    <div class="note-fan-mask"></div>
  </div>
  <div class="note-sample-tag">SAMPLE PREVIEW</div>
</section>
"""


def html_doc(cfg: dict, insta: bool = False) -> str:
    school = cfg["school"]
    short = cfg["short_name"]
    title = cfg["exam_title"]
    subject = cfg["subject"]
    sub_range = cfg.get("subject_range", "")
    instructor = cfg["instructor"]
    questions = cfg["questions"]
    key_problems = cfg["key_problems"]
    instructor_comment = cfg["instructor_comment"]
    grade_level = cfg.get("grade_level", "high")
    note_intro = cfg.get("note_intro", "이영우T 핵심노트")
    note_sub = cfg.get("note_sub", "시험 출제 핵심 패턴을 한 줄로 정리한 직강 노트")
    note_sample_images = cfg.get("note_sample_images", [
        "note_sample_1.png", "note_sample_2.png", "note_sample_3.png"
    ])

    consolidated_file = cfg.get("consolidated_file")
    if consolidated_file:
        consolidated_path = Path(consolidated_file)
        if not consolidated_path.is_absolute():
            consolidated_path = ROOT / consolidated_file
        consolidated = load_consolidated(consolidated_path)
    else:
        consolidated = load_consolidated()
    school_meta = next((s for s in consolidated["schools"] if s["name"] == school), None)

    instructor_uri = img_data_uri(asset(short, "instructor.png"))
    eum_logo_uri = img_data_uri(ASSETS / "eum_logo.png")
    hwp_uri = img_data_uri(ASSETS / "hwp_volume.png")
    ma_uri = img_data_uri(ASSETS / "matharchive_search.png")
    practice1_uri = img_data_uri(ASSETS / "practice_test_1.png")
    practice2_uri = img_data_uri(ASSETS / "practice_test_2.png")

    table_rows = render_q_table(questions)
    total_score = sum(q["score"] for q in questions)
    hit_count = sum(1 for q in questions if q["grade"] in ("A", "B"))
    hit_rate = round(hit_count / len(questions) * 100)
    chart_json = chart_payload(questions)

    insta_cover_html = render_insta_cover(short, school, instructor, eum_logo_uri, instructor_uri)
    prologue_html = render_prologue(consolidated)
    solution_html = render_solution(consolidated)
    school_card_html = render_school_card(school_meta) if school_meta else ""
    strategy_page_html = (
        render_strategy_page(school_meta, instructor, instructor_comment)
        if school_meta else ""
    )
    # 페어 모드: kp.pair_with_next == True 면 다음 kp와 한 페이지에 합침
    total_key_pages = 0
    j = 0
    while j < len(key_problems):
        if key_problems[j].get("pair_with_next") and j + 1 < len(key_problems):
            j += 2
        else:
            j += 1
        total_key_pages += 1

    _key_html_parts: list[str] = []
    i = 0
    page_idx = 0
    while i < len(key_problems):
        kp = key_problems[i]
        page_idx += 1
        if kp.get("pair_with_next") and i + 1 < len(key_problems):
            _key_html_parts.append(
                render_key_pair(short, kp, key_problems[i + 1], page_idx, total_key_pages, grade_level)
            )
            i += 2
        else:
            _key_html_parts.append(
                render_key_problem(short, kp, page_idx, total_key_pages, grade_level)
            )
            i += 1
    key_pages = "\n".join(_key_html_parts)
    how_html = render_how_page()
    volume_html = render_volume_page(consolidated, hwp_uri)
    ma_html = render_matharchive_page(ma_uri)
    practice_html = render_practice_page(practice1_uri, practice2_uri)
    note_html = render_note_fan(short, note_intro, note_sub, note_sample_images)
    student_case_html = render_student_case_page() if cfg.get("show_student_case") else ""
    clinic_summary_uri = img_data_uri(ASSETS / "clinic_summary.png")
    clinic_chap1_uri = img_data_uri(ASSETS / "clinic_chapter1.png")
    clinic_chap2_uri = img_data_uri(ASSETS / "clinic_chapter2.png")
    clinic_html = (
        render_clinic_page(clinic_summary_uri, clinic_chap1_uri, clinic_chap2_uri)
        if cfg.get("show_clinic") else ""
    )

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>{school} {title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{{delimiters:[
    {{left:'$$',right:'$$',display:true}},
    {{left:'$',right:'$',display:false}}
  ]}});"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
  :root {{
    --ink: #0f1419;
    --pop: #ff3a3a;
    --gold: #ffc83d;
    --hl: #ffe14a;
    --soft: #f6f8fb;
    --line: #d6dbe4;
    --muted: #5d6678;
    --ok: #1f9d5f;
    --navy: #1a2541;
  }}
  @page {{ size: {('210mm 210mm' if insta else 'A4')}; margin: 0; }}
  html, body {{ margin:0; padding:0; }}
  body {{
    font-family: "AppleSDGothicNeo-Bold","AppleSDGothicNeo-Regular","Apple SD Gothic Neo","Nanum Gothic", sans-serif;
    color: var(--ink); font-size: {('12pt' if insta else '14pt')}; line-height: 1.6;
  }}
  .page {{ page-break-after: always; padding: {('14mm 12mm' if insta else '18mm 16mm')}; box-sizing: border-box; height: {('210mm' if insta else '297mm')}; overflow: hidden; }}
  .cover, .closing, .insta-cover, .data-page, .practice-page {{ height: {('210mm' if insta else '297mm')} !important; }}
  .page:last-child {{ page-break-after: auto; }}

  mark.hl {{
    background: linear-gradient(180deg, transparent 60%, var(--hl) 60%);
    color: var(--ink); padding: 0 1px; font-weight: 800;
  }}
  .hl-text {{ color: var(--hl); }}

  /* ── 표지 ── 매거진 포스터 (크림 배경 + 검정 프레임 + 빨강 도장) */
  .insta-cover {{
    height: 297mm; padding: 0;
    background: #f5efe0; box-sizing: border-box;
    color: #1a1a1a; display: flex; align-items: stretch;
  }}
  .ic2-frame {{
    flex: 1; margin: 8mm; border: 4mm solid #1a1a1a;
    padding: 12mm 14mm; display: flex; flex-direction: column;
    background: #f5efe0; box-sizing: border-box; position: relative;
  }}
  .ic2-top-bar {{
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 2px solid #1a1a1a; padding-bottom: 4mm;
    font-size: 10.5pt; font-weight: 800; letter-spacing: 2pt;
    color: #1a1a1a;
  }}
  .ic2-volume {{ color: #c92a2a; }}
  .ic2-mid {{
    flex: 1; display: flex; flex-direction: column; justify-content: center;
    padding: 6mm 0;
  }}
  .ic2-pretitle {{
    font-size: 11.5pt; letter-spacing: 3pt; color: #c92a2a;
    font-weight: 900; margin-bottom: 8mm;
  }}
  .ic2-school {{
    font-size: 110pt; font-weight: 900;
    line-height: 0.95; color: #1a1a1a;
    letter-spacing: -4pt;
    font-family: "Apple SD Gothic Neo", "Nanum Myeongjo", serif;
  }}
  .ic2-divider {{
    height: 3px; background: #1a1a1a; margin: 6mm 0;
    width: 50%;
  }}
  .ic2-subject-row {{
    display: flex; align-items: center;
    justify-content: space-between; gap: 6mm;
  }}
  .ic2-subject {{
    font-size: 22pt; font-weight: 900; color: #1a1a1a;
    line-height: 1.2;
  }}
  .ic2-stamp {{
    background: #c92a2a; color: #fff;
    border-radius: 50%;
    width: 38mm; height: 38mm; flex: 0 0 auto;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    transform: rotate(-12deg);
    box-shadow: 0 0 0 2mm #f5efe0, 0 0 0 calc(2mm + 2px) #c92a2a;
  }}
  .ic2-stamp-num {{ font-size: 32pt; font-weight: 900; line-height: 1; }}
  .ic2-stamp-unit {{ font-size: 11pt; font-weight: 800; letter-spacing: 1pt; margin-top: 1mm; }}
  .ic2-bottom {{
    border-top: 2px solid #1a1a1a; padding-top: 6mm;
    display: grid; grid-template-columns: 30mm 1fr auto; gap: 6mm;
    align-items: center;
  }}
  .ic2-photo-wrap {{ display: flex; }}
  .ic2-photo {{
    width: 30mm; height: 30mm; object-fit: cover;
    object-position: center top;
    border-radius: 50%; border: 3px solid #1a1a1a;
    background: #fff;
  }}
  .ic2-info {{ display: flex; flex-direction: column; }}
  .ic2-name {{
    font-size: 26pt; font-weight: 900; line-height: 1; color: #1a1a1a;
  }}
  .ic2-name-t {{ color: #c92a2a; }}
  .ic2-role {{
    font-size: 9pt; letter-spacing: 3pt; color: #555;
    margin-top: 2mm; font-weight: 700;
  }}
  .ic2-logo-wrap {{ display: flex; align-items: center; }}
  .ic2-logo {{ height: 18mm; max-width: 40mm; filter: brightness(0); }}

  /* ── 표지 (재설계: 학교명 초대형 + 사진 확대 → 썸네일 가독성 최우선) ── */
  .cover {{
    height: 297mm; padding: 0;
    position: relative;
    display:flex; flex-direction:column; justify-content:flex-start;
    background: linear-gradient(180deg, #0a3a8c 0%, #1862d4 50%, #3a8aff 100%);
    color:#fff; box-sizing: border-box;
    padding: 14mm 14mm 16mm 14mm;
    overflow: hidden;
  }}
  .cover .top-tag {{
    font-size: 10pt; color: rgba(255,255,255,0.85); letter-spacing: 6pt; font-weight: 700;
    text-align: center; margin-bottom: 4mm;
  }}
  .cover .school {{
    font-size: 110pt; font-weight: 900; color: #fff;
    letter-spacing: -3pt; text-align: center; line-height: 0.95;
    margin: 2mm 0 6mm 0;
    text-shadow: 0 6px 24px rgba(0,0,0,0.35);
  }}
  .cover .title-main {{
    font-size: 18pt; font-weight: 800; line-height: 1.3; color: #fff;
    text-align: center; margin-top: 4mm;
  }}
  .cover .title-main .accent {{ color: #ffe14a; }}
  .cover .title-sub {{
    font-size: 12pt; color: rgba(255,255,255,0.85); margin-top: 4mm;
    text-align: center; letter-spacing: 1pt;
  }}
  .cover .photo-wrap {{
    flex: 1; display: flex; align-items: center; justify-content: center;
    margin: 4mm 0;
  }}
  .cover .photo {{
    max-width: 165mm; max-height: 170mm; object-fit: contain;
    filter: drop-shadow(0 10px 28px rgba(0,0,0,0.45));
  }}
  .cover .name-block {{
    text-align: center;
  }}
  .cover .name-big {{
    font-size: 44pt; font-weight: 900; color: #fff;
    letter-spacing: 4pt; line-height: 1;
  }}
  .cover .name-big .t-mark {{ color: #ffe14a; }}
  .cover .name-role {{
    margin-top: 3mm; font-size: 11pt;
    color: rgba(255,255,255,0.75); letter-spacing: 6pt; font-weight: 600;
  }}
  .cover .logo-corner {{
    position: absolute; right: 12mm; bottom: 12mm;
    max-height: 14mm; max-width: 50mm;
    filter: brightness(0) invert(1) opacity(0.85);
  }}

  /* ── 슬라이드 공통 ── */
  .badge {{
    display:inline-block; background: var(--ink); color:#fff;
    font-size: 12pt; font-weight: 800; letter-spacing: 3pt;
    padding: 2.5mm 7mm; border-radius: 50mm; margin-bottom: 8mm;
  }}
  .badge.dark {{ background: var(--ink); color:#fff; }}
  .badge.yellow {{ background: var(--hl); color: var(--ink); }}
  .badge.red {{ background: var(--pop); color:#fff; }}

  /* ── 프롤로그 ── */
  .prologue-page {{ display:flex; flex-direction:column; justify-content:center; }}
  .prologue-q {{
    font-size: 28pt; font-weight: 900; color: var(--ink);
    line-height: 1.4; margin-bottom: 12mm;
  }}
  .prologue-body {{
    font-size: 15pt; line-height: 1.85; color: #2d3441;
  }}

  /* ── 솔루션 ── */
  .sol-title {{
    font-size: 28pt; font-weight: 900; color: var(--ink);
    margin-bottom: 4mm; letter-spacing: -0.5pt;
  }}
  .sol-intro {{
    font-size: 13pt; color: var(--muted); margin-bottom: 10mm; line-height: 1.55;
  }}
  .sol-steps {{ display:flex; flex-direction: column; gap: 6mm; }}
  .sol-step {{
    display:flex; gap: 6mm; align-items:flex-start;
    padding: 5mm 6mm; background: var(--soft); border-radius: 8px;
    border-left: 6px solid var(--pop);
  }}
  .sol-num {{ font-size: 26pt; flex: 0 0 auto; }}
  .sol-body {{ flex: 1; }}
  .sol-key {{ font-size: 16pt; font-weight: 900; color: var(--ink); margin-bottom: 2mm; }}
  .sol-val {{ font-size: 12.5pt; color: #2d3441; line-height: 1.55; }}

  /* ── 학교 분석 카드 (총평) — 임팩트 강화 ── */
  .school-card-page {{
    display:flex; flex-direction:column; justify-content:flex-start;
    background: linear-gradient(180deg, #fff 0%, #f6f8fb 100%);
  }}
  .sc-name {{
    font-size: 38pt; font-weight: 900; color: var(--ink);
    line-height: 1.1; margin-top: 4mm; margin-bottom: 6mm;
  }}
  .sc-name::after {{
    content: ""; display:block; height: 6px; width: 90mm;
    background: linear-gradient(90deg, var(--pop) 0%, var(--gold) 100%);
    margin-top: 4mm; border-radius: 3px;
  }}
  .sc-tag {{
    background: var(--ink); color: #fff;
    font-size: 17pt; font-weight: 800; line-height: 1.45;
    padding: 5mm 8mm; border-radius: 4px;
    border-left: 8px solid var(--hl);
    margin-bottom: 10mm;
  }}
  .sc-chars {{
    background: #fff; border: 2px solid var(--ink);
    border-radius: 6px; padding: 7mm 9mm;
    box-shadow: 6px 6px 0 var(--ink);
  }}
  .sc-chars-head {{
    font-size: 13pt; color: var(--pop); font-weight: 900;
    letter-spacing: 4pt; margin-bottom: 4mm;
  }}
  .sc-chars-body {{
    font-size: 13.5pt; line-height: 1.75; color: #1d2433;
  }}

  /* ── 적중분석 표 ── */
  .analysis-page {{ }}
  .sec-head {{
    font-size: 22pt; font-weight: 900; color: var(--ink);
    border-left: 8px solid var(--pop); padding-left: 12px; margin: 0 0 5mm 0;
  }}
  .hit-banner {{
    background: linear-gradient(90deg, var(--ink) 0%, #27406d 100%); color:#fff;
    border-radius: 8px; padding: 4mm 7mm; display:flex;
    justify-content: space-between; align-items:center; margin-bottom: 5mm;
  }}
  .hit-banner .big {{ font-size: 18pt; font-weight: 900; letter-spacing: 1px; }}
  .hit-banner .sub {{ font-size: 10.5pt; opacity: 0.95; max-width: 115mm; line-height:1.5; margin-top: 1.5mm; }}
  .hit-banner .sub mark.hl {{ background: var(--hl); color: var(--ink); padding: 0 2px; font-weight: 800; border-radius: 2px; }}
  .hit-banner .pct {{
    font-size: 38pt; font-weight: 900; color: var(--hl);
    text-shadow: 0 0 4px rgba(0,0,0,0.3);
  }}
  table.q {{ width:100%; border-collapse: collapse; font-size: 10.5pt; margin-top:2mm; }}
  table.q th {{ background: var(--ink); color:#fff; padding: 3px 6px; font-weight:700; font-size: 11pt; }}
  table.q td {{ padding: 2.4px 6px; border-bottom:1px solid #e3e7ee; line-height: 1.4; }}
  table.q td.c {{ text-align:center; }}
  table.q td.qno {{ font-weight: 800; color: var(--ink); }}
  table.q td.match {{ color:#28406d; font-weight:600; }}
  .dpill {{
    display:inline-block; min-width: 7mm; padding: 0.6mm 2.5mm; border-radius: 4mm;
    font-weight: 900; font-size: 10pt; color: #fff;
  }}
  .dpill.diff-하 {{ background: var(--ok); }}
  .dpill.diff-중 {{ background: var(--gold); color: var(--ink); }}
  .dpill.diff-상 {{ background: var(--pop); }}
  .gpill {{
    display:inline-block; min-width: 6mm; padding: 0.6mm 2.5mm; border-radius: 3mm;
    font-weight: 900; font-size: 10pt;
  }}
  .gpill.grade-A {{ background: var(--hl); color: var(--ink); border: 1.5px solid var(--ink); }}
  .gpill.grade-B {{ background: var(--gold); color: var(--ink); }}
  .gpill.grade-C {{ background: #e9ecf2; color: var(--muted); }}
  .gpill.grade-D {{ background: #f3f4f8; color: #9aa3b4; }}
  .hi-하 {{ color: var(--ok); font-weight: 900; }}
  .hi-중 {{ color: #c98a16; font-weight: 900; }}
  .hi-상 {{ color: var(--pop); font-weight: 900; }}

  /* ── 도넛 (정확한 원형, 퍼센트 안, 라벨 옆 큰 글씨) ── */
  .charts-page {{ display:flex; flex-direction:column; gap: 6mm; }}
  .chart-card {{
    border:1.5px solid var(--line); border-radius: 10px;
    padding: 4mm 6mm; background:#fff;
    display: grid;
    grid-template-columns: 22mm 75mm 1fr;
    align-items: center; gap: 5mm;
    height: 118mm;
    box-sizing: border-box;
  }}
  .chart-card h4 {{
    font-size: 14pt; color: var(--ink); font-weight: 900; margin: 0;
    text-align: left; line-height: 1.25;
  }}
  .chart-square {{
    width: 75mm; height: 75mm;
    position: relative; justify-self: center;
  }}
  .chart-square canvas {{
    position: absolute; inset: 0; width: 100% !important; height: 100% !important;
  }}
  .chart-legend {{
    display: flex; flex-direction: column; gap: 2mm;
    font-size: 11pt; min-width: 0;
  }}
  .chart-legend .lg-row {{
    display: grid; grid-template-columns: 5mm 1fr; gap: 3mm;
    align-items: start; line-height: 1.3;
  }}
  .chart-legend .lg-dot {{
    width: 5mm; height: 5mm; border-radius: 50%; flex: 0 0 auto;
    margin-top: 1mm;
  }}
  .chart-legend .lg-text {{ display: flex; flex-direction: column; gap: 0.5mm; }}
  .chart-legend .lg-name {{
    font-weight: 800; color: var(--ink); font-size: 11pt; word-break: keep-all;
  }}
  .chart-legend .lg-val {{
    font-weight: 900; color: var(--pop); font-size: 12pt;
  }}

  /* ── 시험대비전략 (강조 강화) ── */
  .strategy-page {{ display:flex; flex-direction:column; }}
  .strat-title {{
    font-size: 26pt; font-weight: 900; color: var(--ink);
    margin-bottom: 8mm; letter-spacing: -0.5pt;
  }}
  .strat-grid-v5 {{
    display: flex; flex-direction: column; gap: 5mm;
    margin-bottom: 8mm;
  }}
  .strat-card {{
    border-left: 6px solid var(--pop); background: var(--soft);
    padding: 5mm 8mm; border-radius: 0 8px 8px 0;
    display: grid; grid-template-columns: 14mm 1fr; gap: 4mm; align-items:start;
  }}
  .strat-num {{ font-size: 24pt; font-weight: 900; color: var(--pop); line-height: 1; }}
  .strat-key {{
    font-size: 15pt; font-weight: 900; color: var(--ink);
    margin-bottom: 2mm; grid-column: 2;
  }}
  .strat-val {{
    font-size: 12.5pt; color: #1d2433; line-height: 1.65; grid-column: 2;
  }}
  .comment {{
    border-left: 8px solid var(--pop); background:#fff5f4; padding: 5mm 7mm;
    border-radius: 0 8px 8px 0; margin-top: auto; color: #2d3441; line-height: 1.65;
    font-size: 12.5pt;
  }}
  .comment .hdr {{
    display:block; font-weight: 900; color: var(--pop); margin-bottom:3mm;
    font-size: 16pt; letter-spacing: 1px;
  }}

  /* ── 핵심문제 페이지 ── */
  .key-counter {{
    font-size: 11pt; color: var(--muted); letter-spacing: 4pt;
    font-weight: 700; margin-bottom: 3mm;
  }}
  .key-head {{
    display:flex; justify-content: space-between; align-items: center;
    border-bottom: 4px solid var(--ink); padding-bottom: 4mm; margin-bottom: 6mm;
  }}
  .key-no-pill {{
    font-size: 22pt; font-weight: 900; background: var(--ink); color: #fff;
    padding: 2mm 6mm; border-radius: 4mm; letter-spacing: 1px;
  }}
  .key-meta {{ color: var(--muted); font-size: 13pt; font-weight: 600; }}
  .key-body {{ display:grid; grid-template-columns: 1.05fr 0.95fr; gap: 5mm; }}
  .exam-card, .note-card {{
    border:1.5px solid var(--line); border-radius:8px; padding: 5mm 5mm; background:#fff;
    display:flex; flex-direction:column;
    min-width: 0;
  }}
  .card-head {{
    font-size: 13pt; color:#fff; background: var(--ink);
    display:inline-block; padding: 2mm 5mm; border-radius: 4px;
    margin-bottom: 4mm; font-weight: 800; align-self:flex-start;
  }}
  .card-head.note-head {{ background: var(--pop); }}
  .exam-latex, .match-latex {{
    font-size: 11.5pt; line-height: 1.9;
    word-break: keep-all;
  }}
  .exam-latex {{ min-height: 90mm; }}
  .match-latex {{ color: #1d2433; min-height: 60mm; }}
  .exam-stack, .cap-stack {{
    display: flex; flex-direction: column; gap: 4mm;
    align-items: center;
  }}
  .exam-stack .exam-img, .cap-stack .cap-img {{
    width: 100%; max-width: 100%; height: auto;
    border: 1px solid var(--line); border-radius: 4px;
    background: #fff;
  }}
  .exam-figs {{
    display: flex; flex-direction: column; gap: 3mm;
    margin-top: 4mm; padding-top: 3mm; border-top: 1px dashed var(--line);
    align-items: center;
  }}
  .exam-fig-img {{
    max-width: 90%; max-height: 60mm; height: auto;
    border: 1px solid var(--line); border-radius: 3px; background: #fff;
  }}
  .exam-fallback, .cap-fallback {{
    margin-top: 3mm; font-size: 9.5pt; color: var(--muted); font-style: italic;
    line-height: 1.5;
  }}
  .cond-box {{
    background: var(--soft); border: 1px solid var(--line);
    border-radius: 4px; padding: 3mm 5mm; margin: 2mm 0;
    font-size: 11.5pt; line-height: 1.7;
  }}
  .choices {{
    margin: 3mm 0 1mm 0; font-size: 11.5pt;
    color: var(--ink); line-height: 1.7;
  }}
  .exam-fallback code {{
    background: var(--soft); color: var(--ink); padding: 0.5mm 2mm;
    border-radius: 2px; font-family: monospace; font-style: normal;
  }}
  .card-empty {{
    height: 100mm; display:flex; align-items:center; justify-content:center;
    color:#9aa3b4; font-size: 11pt;
  }}
  .match-cap {{
    margin-top: 5mm; padding-top: 4mm; border-top: 1px dashed var(--line);
    color: #2d3441; line-height: 1.75; font-size: 11.5pt;
  }}
  .match-cap mark.hl {{ background: var(--hl); color: var(--ink); padding: 0 1px; font-weight: 800; }}
  .shared-pill {{
    margin-top: 3mm; display: inline-block; font-size: 10pt;
    background: var(--hl); color: var(--ink); padding: 1.5mm 4mm;
    border-radius: 3mm; font-weight: 800; letter-spacing: 0.5pt;
    align-self: flex-start;
  }}

  /* ── 핵심문제 페어 페이지 (한 페이지에 두 문제) ── */
  .key-page.paired {{ display: flex; flex-direction: column; gap: 4mm; }}
  .key-page.paired .key-pair-half {{
    flex: 1; min-height: 0;
    display: flex; flex-direction: column;
  }}
  .key-page.paired .key-head {{
    border-bottom: 2.5px solid var(--ink);
    padding-bottom: 2mm; margin-bottom: 3mm;
  }}
  .key-page.paired .key-no-pill {{ font-size: 14pt; padding: 1.2mm 4mm; }}
  .key-page.paired .key-meta {{ font-size: 10.5pt; }}
  .key-page.paired .key-body {{ gap: 3mm; flex: 1; min-height: 0; }}
  .key-page.paired .exam-card,
  .key-page.paired .note-card {{ padding: 3mm; }}
  .key-page.paired .card-head {{
    font-size: 10pt; padding: 1mm 3mm; margin-bottom: 2mm;
  }}
  .key-page.paired .exam-latex,
  .key-page.paired .match-latex {{ font-size: 9.5pt; line-height: 1.6; min-height: auto; }}
  .key-page.paired .match-cap {{
    font-size: 9.5pt; margin-top: 2.5mm; padding-top: 2mm; line-height: 1.55;
  }}
  .key-page.paired .exam-fig-img {{ max-height: 36mm; }}
  .key-page.paired .card-empty {{ height: 40mm; font-size: 9.5pt; }}

  /* ── '어떻게 이런 적중과 준비가 가능할까요' ── */
  .how-page {{ display:flex; flex-direction:column; justify-content:center; }}
  .how-q {{
    font-size: 30pt; font-weight: 900; color: var(--ink);
    line-height: 1.4; margin-bottom: 10mm;
  }}
  .how-answer {{
    font-size: 15pt; line-height: 1.85; color: #2d3441;
    border-left: 6px solid var(--pop); padding: 5mm 8mm;
    background: var(--soft); border-radius: 0 6px 6px 0;
    margin-bottom: 10mm;
  }}
  .how-list {{
    list-style: none; padding-left: 0; margin: 0;
    display: flex; flex-direction: column; gap: 4mm;
    font-size: 13pt;
  }}
  .how-list li {{
    padding: 4mm 6mm; background: #fff; border: 1.5px solid var(--line);
    border-radius: 6px;
  }}
  .how-list li b {{ color: var(--pop); margin-right: 4mm; font-size: 16pt; }}

  /* ── 학생사례 (70→95 화두) ── */
  .case-page {{
    display:flex; flex-direction:column; justify-content:center;
    background: linear-gradient(135deg, #fff8f0 0%, #fff 60%);
    padding: 18mm 16mm;
  }}
  .case-headline {{ margin-bottom: 10mm; }}
  .case-question {{
    font-size: 26pt; font-weight: 900; color: var(--ink);
    line-height: 1.4; letter-spacing: -0.3pt;
  }}
  .case-pop {{
    color: var(--pop); font-size: 38pt;
    font-weight: 900; vertical-align: -3pt;
  }}
  .case-scoreboard {{
    display: flex; align-items: center; justify-content: center;
    gap: 8mm; margin: 8mm 0 10mm;
  }}
  .case-before, .case-after {{
    flex: 1; padding: 8mm 6mm; text-align: center;
    border-radius: 8px; border: 2px solid var(--line);
    background: #fff;
  }}
  .case-after {{ border-color: var(--pop); background: #fff5f5; }}
  .case-label {{
    font-size: 9pt; letter-spacing: 2pt; color: #677;
    font-weight: 700; margin-bottom: 4mm;
  }}
  .case-after .case-label {{ color: var(--pop); }}
  .case-score {{
    font-size: 48pt; font-weight: 900; line-height: 1;
    color: var(--ink);
  }}
  .case-after .case-score {{ color: var(--pop); }}
  .case-unit {{ font-size: 18pt; font-weight: 700; margin-left: 2mm; }}
  .case-note {{
    font-size: 9pt; color: #888; margin-top: 3mm;
    font-weight: 600;
  }}
  .case-arrow {{
    font-size: 28pt; color: var(--pop); font-weight: 900;
  }}
  .case-delta {{
    text-align: center; padding: 6mm; background: var(--ink);
    color: #fff; border-radius: 6px; margin-bottom: 8mm;
  }}
  .case-delta-num {{
    font-size: 30pt; font-weight: 900; color: var(--hl);
    margin-right: 6mm; letter-spacing: -0.5pt;
  }}
  .case-delta-text {{
    font-size: 12pt; font-weight: 700; letter-spacing: 1pt;
  }}
  .case-q {{
    font-size: 22pt; font-weight: 900; text-align: center;
    margin-bottom: 5mm; color: var(--ink);
  }}
  .case-tease {{
    text-align: center; font-size: 11pt; color: #677;
    font-style: italic;
  }}

  /* ── 학생별 취약유형 클리닉 ── */
  .clinic-page {{
    display:flex; flex-direction:column;
    padding: 14mm 12mm 12mm;
  }}
  .clinic-title {{
    font-size: 22pt; font-weight: 900; color: var(--ink);
    line-height: 1.35; margin-top: 4mm; margin-bottom: 4mm;
  }}
  .clinic-sub {{
    font-size: 11pt; color: #2d3441; line-height: 1.6;
    margin-bottom: 8mm;
  }}
  .clinic-grid {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 8mm; flex: 1; min-height: 0;
  }}
  .clinic-card {{
    border: 1.5px solid var(--line); border-radius: 8px;
    background: #fff; padding: 6mm; display: flex; flex-direction: column;
    overflow: hidden; min-height: 0;
  }}
  .clinic-card-tag {{
    font-size: 11pt; font-weight: 800; color: #fff;
    background: var(--ink); padding: 3mm 5mm; border-radius: 4px;
    align-self: flex-start; margin-bottom: 5mm;
    letter-spacing: 0.3pt;
  }}
  .clinic-img {{
    width: 100%; height: auto; flex: 1; object-fit: contain;
    border-radius: 4px; min-height: 0;
  }}
  .clinic-card-cap {{
    font-size: 10.5pt; color: #444; margin-top: 5mm;
    line-height: 1.5; text-align: center; font-weight: 600;
  }}
  .clinic-bottom-line {{
    background: var(--ink); color: #fff;
    padding: 5mm 6mm; border-radius: 6px; margin-top: 6mm;
    font-size: 12pt; font-weight: 700; line-height: 1.55;
    text-align: center;
  }}
  .clinic-bottom-line b {{ color: var(--hl); }}

  /* ── 6,000+ 자료량 ── */
  .data-page {{ background: var(--ink); color:#fff; padding: 20mm 16mm; display:flex; flex-direction:column; }}
  .data-page .data-main {{
    font-size: 26pt; font-weight: 900; color: var(--hl);
    margin-top: 4mm; line-height: 1.3;
  }}
  .data-page .data-sub {{
    font-size: 14pt; color: rgba(255,255,255,0.85);
    margin-top: 4mm; letter-spacing: 1px;
  }}
  .volume-grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 8mm; align-items: start;
    margin-top: 8mm;
  }}
  .data-page .data-list {{
    margin: 0; font-size: 12.5pt; line-height: 1.9;
    list-style: none; padding-left: 0;
  }}
  .data-page .data-list li {{ padding-left: 8mm; position: relative; margin-bottom: 1mm; }}
  .data-page .data-list li::before {{
    content: "✓"; position:absolute; left:0; top:0;
    color: var(--hl); font-weight: 900; font-size: 14pt;
  }}
  .volume-screenshot {{
    width: 100%; max-height: 90mm; object-fit: contain;
    border: 2px solid rgba(255,255,255,0.2); border-radius: 4px;
    background: #fff;
  }}
  .data-page .data-callout {{
    margin-top: auto; text-align:center;
    border-top: 1.5px dashed rgba(255,255,255,0.3);
    padding-top: 6mm;
  }}
  .data-page .big-num {{
    font-size: 64pt; font-weight: 900; color: var(--hl);
    line-height: 1; letter-spacing: -2pt;
  }}
  .data-page .big-num .unit {{ font-size: 44pt; color: #fff; }}
  .data-page .big-label {{
    display:block; font-size: 15pt; color: rgba(255,255,255,0.85);
    letter-spacing: 4pt; margin-top: 3mm;
  }}

  /* ── 매쓰아카이브 광고 (블랙앤화이트 톤) ── */
  .matharchive-page {{
    display:flex; flex-direction:column;
    background: #fff;
  }}
  .ma-title {{
    font-size: 26pt; font-weight: 900; color: var(--ink);
    line-height: 1.3; margin-bottom: 4mm;
  }}
  .ma-title mark.hl {{
    background: var(--hl); color: var(--ink);
    padding: 0 2mm; border-radius: 2px;
  }}
  .ma-title .hl-text {{
    color: #fff; background: var(--ink); padding: 1mm 4mm;
    border-radius: 3px; display: inline-block; margin-top: 1mm;
  }}
  .ma-sub {{
    font-size: 13pt; color: #2d3441; line-height: 1.7;
    margin-bottom: 7mm;
  }}
  .ma-features {{
    display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm;
    margin-bottom: 7mm;
  }}
  .ma-feat {{
    background: var(--ink); color: #fff; padding: 4mm 5mm;
    border-radius: 4px; font-size: 11.5pt; font-weight: 700;
    border-bottom: 4px solid var(--ink);
    line-height: 1.4;
  }}
  .ma-feat b {{ color: var(--hl); font-weight: 900; }}
  .ma-feat-num {{ color: var(--hl); font-weight: 900; margin-right: 2mm; font-size: 14pt; }}
  .ma-screenshot-wrap {{
    border: 2px solid var(--ink); border-radius: 6px;
    padding: 3mm; background: #fff; margin-bottom: 6mm;
    box-shadow: 6px 6px 0 var(--ink);
    flex: 0 0 auto;
  }}
  .ma-screenshot {{ width: 100%; height: auto; max-height: 105mm; object-fit: contain; }}
  .ma-placeholder {{
    height: 90mm; display: flex; align-items: center; justify-content: center;
    color: var(--muted); border: 2px dashed var(--line); border-radius: 4px;
  }}
  .ma-bottom-line {{
    margin-top: auto; padding: 4mm 6mm; background: var(--ink); color: #fff;
    font-size: 13pt; font-weight: 700; line-height: 1.5;
    border-left: 6px solid var(--hl); border-radius: 0 4px 4px 0;
  }}
  .ma-bottom-line b {{ color: var(--hl); font-size: 16pt; }}

  /* ── 실전동형모의고사 광고 (블랙앤화이트 톤, 매쓰아카이브와 통일) ── */
  .practice-page {{
    display: flex; flex-direction: column;
    background: #fff;
    color: var(--ink); padding: 18mm 16mm;
  }}
  .practice-page .badge {{ background: var(--ink); color: #fff; align-self: flex-start; }}
  .pt-title {{
    font-size: 26pt; font-weight: 900; line-height: 1.3;
    margin-bottom: 4mm; color: var(--ink);
  }}
  .pt-title .pt-hl {{
    color: #fff; background: var(--ink); padding: 1mm 4mm;
    border-radius: 3px; display: inline-block; margin-top: 1mm;
  }}
  .pt-sub {{
    font-size: 13pt; line-height: 1.7; color: #2d3441;
    margin-bottom: 7mm;
  }}
  .pt-sub mark.hl {{
    background: var(--hl); color: var(--ink);
    font-weight: 900; padding: 0.5mm 2mm; border-radius: 2px;
  }}
  .pt-features {{
    display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm;
    margin-bottom: 7mm;
  }}
  .pt-feat {{
    background: var(--ink); border-bottom: 4px solid var(--ink);
    border-radius: 4px; padding: 4mm 5mm; font-size: 11.5pt; line-height: 1.4;
    display: flex; gap: 3mm; align-items: flex-start;
    color: #fff; font-weight: 700;
  }}
  .pt-feat .pt-num {{
    color: var(--hl); font-weight: 900; font-size: 14pt;
    line-height: 1; flex: 0 0 auto;
  }}
  .pt-feat .pt-feat-text {{ flex: 1; }}
  .pt-feat b {{ color: var(--hl); font-weight: 900; }}
  .pt-photos {{
    display: grid; grid-template-columns: 1.45fr 1fr; gap: 6mm;
    margin-bottom: 6mm;
  }}
  .pt-photo-card {{
    background: #fff; border: 2px solid var(--ink); border-radius: 6px; padding: 3mm;
    box-shadow: 6px 6px 0 var(--ink);
    display: flex; flex-direction: column;
  }}
  .pt-img {{
    width: 100%; height: 80mm; object-fit: cover; border-radius: 3px;
  }}
  .pt-img-2 {{ object-fit: contain; background: #f6f8fb; }}
  .pt-photo-cap {{
    margin-top: 3mm; font-size: 10.5pt; color: #2d3441;
    line-height: 1.4; font-weight: 700; text-align: center;
  }}
  .pt-bottom-line {{
    margin-top: auto; padding: 4mm 6mm; background: var(--ink); color: #fff;
    font-size: 13pt; font-weight: 700; line-height: 1.5;
    border-left: 6px solid var(--hl); border-radius: 0 4px 4px 0;
  }}
  .pt-bottom-line b {{ color: var(--hl); }}

  /* ── 핵심노트 견본 ── */
  .note-page {{ text-align:center; padding-top: 12mm; }}
  .note-page .note-title {{
    font-size: 22pt; font-weight: 900; color: var(--ink); margin-top: 2mm;
    margin-bottom: 3mm;
  }}
  .note-sub {{
    font-size: 13pt; color: var(--muted); margin-top: 0; margin-bottom: 8mm;
  }}
  .note-fan {{
    position: relative; width: 100%; height: 145mm; margin: 0 auto;
  }}
  .note-fan-card {{
    position: absolute;
    width: 60mm; height: auto; max-height: 100mm;
    border: 2px solid var(--ink); border-radius: 4px;
    box-shadow: 0 6px 14px rgba(15,29,58,0.3);
    background: #fff;
    transform-origin: 50% 80%;
  }}
  .note-fan-mask {{
    position: absolute; left: -10%; right: -10%; bottom: -2mm;
    height: 35mm;
    background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.95) 70%, rgba(255,255,255,1) 100%);
    pointer-events: none;
  }}
  .note-sample-tag {{
    margin-top: 8mm; font-size: 13pt; color: var(--pop);
    font-weight: 900; letter-spacing: 5pt;
  }}

  /* ── closing ── */
  .closing {{
    height: 297mm; padding: 0;
    display:flex; flex-direction:column; justify-content:center; align-items:center;
    background: linear-gradient(135deg, #fff 0%, var(--soft) 100%);
    text-align:center; box-sizing: border-box; padding: 40mm 16mm;
  }}
  .closing .badge {{ background: var(--pop); color:#fff; }}
  .closing .head {{
    font-size: 26pt; font-weight: 900; color: var(--ink);
    margin-top: 12mm; line-height: 1.4;
  }}
  .closing .head .hl-mark {{ color: var(--pop); }}
  .closing .sub {{ font-size: 16pt; color: #2d3441; margin-top: 10mm; line-height: 1.65; }}
  .closing .tagline {{
    margin-top: 18mm; font-size: 26pt; font-weight: 900;
    color: var(--ink); letter-spacing: 1px;
    border-top: 4px solid var(--ink); border-bottom: 4px solid var(--ink);
    padding: 6mm 0; display: inline-block;
  }}
  .closing .signature {{
    margin-top: 14mm; font-size: 13pt; color: var(--muted); letter-spacing: 4pt;
  }}
  .closing .signature .name {{
    color: var(--ink); font-size: 17pt; font-weight: 900;
  }}
</style>
</head>
<body>

<!-- 1. 표지 (메인) -->
<section class="page cover">
  <div class="top-tag">M A T H A R C H I V E</div>
  <div class="school">{school}</div>
  <div class="photo-wrap">
    <img class="photo" src="{instructor_uri}"/>
  </div>
  <div class="title-main">{title}<br><span class="accent">완벽해부 &amp; 1등급 처방전</span></div>
  <div class="name-block">
    <div class="name-big">이영우<span class="t-mark">T</span></div>
    <div class="name-role">M A T H &nbsp; I N S T R U C T O R</div>
  </div>
  {f'<img class="logo-corner" src="{eum_logo_uri}"/>' if eum_logo_uri else ''}
</section>

<!-- 2. 프롤로그 -->
{prologue_html}

<!-- 3. 고득점 3단계전략 -->
{solution_html}

<!-- 4. 총평 (학교분석카드) -->
{school_card_html}

<!-- 4.5 학생사례 (총평 ↔ 출제그리드 사이) -->
{student_case_html}

<!-- 5. 출제그리드 (도넛) -->
<section class="page charts-page">
  <div class="sec-head">출제 그리드 — 단원 · 난이도 분포</div>
  <div class="chart-card">
    <h4>중단원<br>분포</h4>
    <div class="chart-square"><canvas id="chartChapter"></canvas></div>
    <div class="chart-legend" id="legendChapter"></div>
  </div>
  <div class="chart-card">
    <h4>난이도<br>분포</h4>
    <div class="chart-square"><canvas id="chartDiff"></canvas></div>
    <div class="chart-legend" id="legendDiff"></div>
  </div>
</section>

<!-- 6. 분석도표 (적중표) -->
<section class="page analysis-page">
  <div class="sec-head">자체교재 적중 {hit_rate}%</div>
  <div class="hit-banner">
    <div>
      <div class="big">적중 {hit_count}/{len(questions)}문항 · 총배점 {total_score:.1f}점</div>
      <div class="sub"><mark class='hl'>우리 교재가 다룬 유형</mark>이 그대로 출제. 등급 A는 <mark class='hl'>동형</mark>(거의 동일 풀이 절차) 매칭.</div>
    </div>
    <div class="pct">{hit_rate}%</div>
  </div>
  <table class="q">
    <thead><tr><th>번호</th><th>중단원</th><th>배점</th><th>난이도</th><th>교재 매칭</th><th>등급</th></tr></thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>
</section>

<!-- 7. 시험대비전략 (강조) -->
{strategy_page_html}

<!-- 8~11. 핵심문제 4개 -->
{key_pages}

<!-- 12. 어떻게 이런 적중과 준비가 가능할까요? -->
{how_html}

<!-- 12.5 학생별 취약유형 클리닉 -->
{clinic_html}

<!-- 13. 6,000+ 자체 보유 -->
{volume_html}

<!-- 14. 매쓰아카이브 광고 -->
{ma_html}

<!-- 15. 실전동형모의고사 광고 -->
{practice_html}

<!-- 16. 핵심노트 견본 -->
{note_html}

<!-- 16. 이영우T의 약속 -->
<section class="page closing">
  <div class="badge">이영우T의 약속</div>
  <div class="head">"{school} 내신 족보,<br>핵심노트와 교재에 모두 담았습니다."</div>
  <div class="sub">이 교재를 믿고 반복하는 학생이 결국 1등급을 쟁취합니다.</div>
  <div class="tagline">성적으로 증명하겠습니다.</div>
  <div class="signature">수학 Instructor &nbsp;<span class="name">{instructor.replace('T','')}</span></div>
</section>

<script>
window.addEventListener('load', () => {{
  Chart.register(ChartDataLabels);
  const data = {chart_json};
  const palette = ['#0f1419','#27406d','#3d5e9a','#ff3a3a','#ffc83d','#1f9d5f','#caff3d','#a378ff'];
  const diffColors = {{ '하':'#1f9d5f', '중':'#ffc83d', '상':'#ff3a3a' }};

  const total = (kind) => data[kind].data.reduce((a,b)=>a+b, 0);

  const buildChart = (kind, canvasId, legendId) => {{
    const labels = data[kind].labels;
    const values = data[kind].data;
    const colors = (kind === 'difficulty')
      ? labels.map(l => diffColors[l] || '#888')
      : labels.map((_,i) => palette[i % palette.length]);
    const t = total(kind);
    new Chart(document.getElementById(canvasId), {{
      type: 'doughnut',
      data: {{
        labels: labels,
        datasets: [{{ data: values, backgroundColor: colors,
          borderWidth: 2, borderColor: '#fff' }}]
      }},
      options: {{
        animation: false, cutout: '52%',
        responsive: true, maintainAspectRatio: true,
        aspectRatio: 1,
        layout: {{ padding: 4 }},
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{ enabled: false }},
          datalabels: {{
            color: (ctx) => {{
              const lbl = ctx.chart.data.labels[ctx.dataIndex];
              return (lbl === '중') ? '#0f1419' : '#fff';
            }},
            font: {{ size: 16, weight: '900' }},
            formatter: (v) => Math.round(v / t * 100) + '%'
          }}
        }}
      }}
    }});
    // 외부 legend 그리기
    const legend = document.getElementById(legendId);
    if (legend) {{
      legend.innerHTML = labels.map((lbl, i) => {{
        const v = values[i];
        const pct = Math.round(v / t * 100);
        return `<div class="lg-row">
          <span class="lg-dot" style="background:${{colors[i]}}"></span>
          <span class="lg-text">
            <span class="lg-name">${{lbl}}</span>
            <span class="lg-val">${{v}}문항 · ${{pct}}%</span>
          </span>
        </div>`;
      }}).join('');
    }}
  }};

  buildChart('chapter', 'chartChapter', 'legendChapter');
  buildChart('difficulty', 'chartDiff', 'legendDiff');
  window.__chartsRendered = true;
}});
</script>

</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--insta", action="store_true", help="정사각형(인스타) 모드")
    ap.add_argument("--both", action="store_true", help="A4 + 인스타 둘 다 빌드")
    args = ap.parse_args()
    # 중등 config 우선 → 없으면 고등 config
    cfg_path = CONFIGS_MIDDLE / f"{args.config}.json"
    if not cfg_path.exists():
        cfg_path = CONFIGS / f"{args.config}.json"
    if not cfg_path.exists():
        print(f"config not found: {cfg_path}", file=sys.stderr)
        return 1
    cfg = json.loads(cfg_path.read_text())
    out_dir = PA_MIDDLE if cfg.get("grade_level") == "middle" else PA

    short = cfg["short_name"]
    title_safe = cfg["exam_title"].replace(" ", "_").replace("/", "-")
    modes: list[bool] = []
    if args.both:
        modes = [False, True]
    else:
        modes = [args.insta]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for insta in modes:
            tag = "_인스타" if insta else ""
            out_html = out_dir / f"{short}_{title_safe}_적중분석{tag}.html"
            out_pdf = out_dir / f"{short}_{title_safe}_적중분석{tag}.pdf"
            out_html.write_text(html_doc(cfg, insta=insta), encoding="utf-8")
            print(f"HTML: {out_html}")
            ctx = browser.new_context()
            page = ctx.new_page()
            page.goto(out_html.as_uri(), wait_until="networkidle")
            page.wait_for_function("window.__chartsRendered === true", timeout=10000)
            page.wait_for_timeout(900)
            pdf_kwargs = {
                "path": str(out_pdf),
                "print_background": True,
                "margin": {"top": "0", "bottom": "0", "left": "0", "right": "0"},
            }
            if insta:
                pdf_kwargs["width"] = "210mm"
                pdf_kwargs["height"] = "210mm"
            else:
                pdf_kwargs["format"] = "A4"
            page.pdf(**pdf_kwargs)
            ctx.close()
            print(f"PDF : {out_pdf}")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
