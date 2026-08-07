#!/usr/bin/env python3
"""공통수학2 · 평면좌표(도형의 방정식) 단원 — 난이도별 분책 3종 (상/중/하).

조건:
- chapter ∈ 도형의방정식 대단원 (curriculum 순서):
  평면좌표 → 직선의 방정식 → 원의 방정식 → 도형의 이동
- 학교: 아래 SCHOOLS 만 (매쏠로지 로컬 DB, 학교명 변형 포함)
- 정렬: 단원(curriculum) 오름차순 → 난이도 → qid
- 레이아웃: KERNEL POINT 표준 (KEY POINT/MEMO)

usage: python3 build_pyeongjwapyo_by_difficulty.py [상|중|하|all]
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
sys.path.insert(0, str(APP))

DB_PATH = ROOT / "db" / "mathdb.sqlite"

CHAPTERS = [
    "평면좌표",
    "직선의 방정식",
    "원의 방정식",
    "도형의 이동",
]

# 사용자 지정 학교 (학교명 변형 포함).
# 수도여고 = 수도여고 + 수도여자고 (동일 학교 축약/정식명).
# 영신고만 포함 (영신여고/영신여자고는 별개 학교라 제외).
# 성남고만 포함 (성남외고 제외). 신림고는 DB에 데이터 없음.
SCHOOLS = [
    "성남고",
    "수도여고", "수도여자고",
    "숭의여고",
    "당곡고",
    "대영고",
    "영신고",
    "영등포고",
    "영등포여고",
    "여의도고",
    "여의도여고",
    "장훈고",
    "성보고",
    "구암고",
]

DIFF_ORDER = {"하": 0, "중": 1, "상": 2, "킬": 3}

# 내지/본문 크롬을 '대수 필수유형 FINAL' 참고본과 동일 폰트로 통일.
# Cafe24 Ssurround(단원명·크롬 전반) + Paperlogy 9 Black(큰숫자·로마자).
# ── 문제 본문(.q-body)·선지(.q-choices)·KaTeX 는 제외 (폰트 불가침).
CHROME_FONT_CSS = """
.bp-head-left, .bp-head-right, .bp-head-right .roman,
.bp-page .bp-head-left, .bp-page .bp-head-right, .bp-page .bp-head-right .roman,
.bp-side-part, .bp-side-letter, .bp-side-roman, .bp-side-vertical,
.bp-page .bp-side .bp-side-part, .bp-page .bp-side .bp-side-letter,
.kp-source, .kp-checks, .cb, .kp-label, .kp-line, .kp-memo-label,
.cd-chapter-label, .cd-meta-top, .cd-major,
.cd-section-label, .cd-section-title, .cd-footer-title, .cd-footer-sub {
  font-family: 'Cafe24 Ssurround Bold', 'Cafe24Ssurround', sans-serif !important;
}
.cd-big-num, .cd-major-roman, .kp-num {
  font-family: 'Paperlogy 9 Black', sans-serif !important;
}
/* 자연스러운 줄바꿈 (폰트는 불가침, 레이아웃만):
   왼쪽정렬(자간 균일) + 한글 어절단위(keep-all) + 인라인 수식 원자화
   (연산자에서 mx+/4a 처럼 안 쪼개짐). */
.slot.book-kp .q-body {
  text-align: left !important;
  word-break: keep-all !important;
  overflow-wrap: break-word !important;
  font-family: __BODY_FONT__ !important;  /* 본문 한글 폰트 (수식은 KaTeX 그대로) */
  font-size: 10pt !important;
}
/* 수식(KaTeX)은 font-family 안 건드림 — 평가원 수식 그대로 유지 (불가침) */
.slot.book-kp .q-body .katex { white-space: nowrap !important; }
/* 배점은 통째로(안 쪼개짐), 배점/단서 우측정렬 트레일러 */
.slot.book-kp .q-body .q-pts { white-space: nowrap !important; }
.slot.book-kp .q-body .nb { white-space: nowrap !important; }
.slot.book-kp .q-body .q-trailer {
  display: block !important; text-align: right !important; margin-top: 0.5mm !important;
}
/* 보기/조건 박스 항목 내어쓰기: 마커(ㄱ./(가))는 왼쪽, 줄넘김된 글자는 텍스트에 맞춤 */
.slot.book-kp .cond-box .bogi-item {
  padding-left: 1.5em; text-indent: -1.5em; margin: 0.15em 0;
}
.slot.book-kp .cond-box .bogi-hdr { margin: 0 0 0.2em 0; }
"""

# 본문 한글 폰트 프리셋 (env PREVIEW_FONT 로 선택; 기본 나눔명조).
# 수식(KaTeX)·선지 수식은 어느 경우든 그대로.
_FONT_PRESETS = {
    "나눔명조": "'NanumMyeongjo', 'Nanum Myeongjo', '나눔명조', serif",
    "애플명조": "'AppleMyungjo', 'Apple Myungjo', serif",
    "함초롬바탕": "'HCR Batang', '함초롬바탕', 'HCR Batang LVT', 'NanumMyeongjo', serif",
    "나눔고딕": "'NanumGothic', 'Nanum Gothic', '나눔고딕', 'Pretendard', sans-serif",
}
_PREVIEW_FONT = os.environ.get("PREVIEW_FONT")
_FONT_KEY = _PREVIEW_FONT if _PREVIEW_FONT in _FONT_PRESETS else "함초롬바탕"  # 기본=평가원 함초롬바탕
CHROME_FONT_CSS = CHROME_FONT_CSS.replace("__BODY_FONT__", _FONT_PRESETS[_FONT_KEY])

# ── 본문 조판 전처리 (문자열 변환) ─────────────────────────
_MATH_RE = re.compile(r"\$[^$\n]+?\$")
_SUBQ_RE = re.compile(r"\s*(\((?:\d{1,2}|[가-힣])\))(?=\s)")   # (1)(2)/(가)(나) 소문제
_COND_RE = re.compile(r"(\(단[,\s][^()]*\))")                  # 단서조항 (단, ~)
_PTS_RE = re.compile(r"(\[[^\[\]]*점[^\[\]]*\])")              # 배점 [ …점 ]


def _stash_math(s):
    ms = []
    def f(m):
        ms.append(m.group(0)); return f"\x01{len(ms)-1}\x02"
    return _MATH_RE.sub(f, s), ms


def _restore_math(s, ms):
    for i, m in enumerate(ms):
        s = s.replace(f"\x01{i}\x02", m)
    return s


_PH_JOSA = re.compile(r"(\x01\d+\x02)([가-힣]+)")   # (수식placeholder)(조사)


def _typeset_stem(seg: str) -> str:
    seg, ms = _stash_math(seg)
    # 수식 + 바로 뒤 한글(조사/어미)을 nowrap 묶기 → "y=2x+1|과", "y=mx+n|일" 고아 방지.
    # 수식과 조사 사이 U+2060(WORD JOINER): 엔진의 `$식$+한글 → \n삽입` 정규식이
    # 매치 못하게(과잉 줄바꿈 차단) + 줄바꿈 금지. 앞에도 span'>' 가 있어 한글+식 분리도 차단.
    seg = _PH_JOSA.sub('<span class="nb">\\1⁠\\2</span>', seg)
    seg = _SUBQ_RE.sub(r"\n\n\1", seg)          # 소문제 앞 빈 줄
    seg = re.sub(r"\n{2,}", "\x00", seg)         # 문단/소문제 구분 보존
    seg = re.sub(r"[ \t]*\n[ \t]*", " ", seg)    # 나머지 하드 \n → 공백(리플로우)
    seg = seg.replace("\x00", "\n\n")
    seg = _COND_RE.sub(r'<span class="q-cond">\1</span>', seg)   # 단서 감싸기
    seg = _PTS_RE.sub(r'<span class="q-pts">\1</span>', seg)     # 배점 감싸기
    return _restore_math(seg, ms)


def typeset_body(text: str | None) -> str:
    """실제 출판물식 조판: 하드 줄바꿈 리플로우 + 소문제 빈 줄 +
    단서/배점 마킹(후처리 JS가 우측정렬). <<BOX>> 내부는 건드리지 않음."""
    if not text:
        return text or ""
    out = []
    for seg in re.split(r"(<<BOX_START>>.*?<<BOX_END>>)", text, flags=re.DOTALL):
        out.append(seg if seg.startswith("<<BOX_START>>") else _typeset_stem(seg))
    return "".join(out)


# ── 렌더 후 레이아웃 후처리 (Chromium 측정) ───────────────
TYPESET_JS = r"""
window.__typeset = function () {
  document.querySelectorAll('.slot.book-kp').forEach(function (slot) {
    // (1) 선지 다단 강등: 3열 → 2열(2/2/1) → 1열(5행)
    // KaTeX 분수(분자/막대/분모)는 line-height 의 ~2.3배 높이라 "wrap" 로 오판정되면
    // 짧은 분수 5개도 1열로 밀림. 실제 텍스트 줄바꿈만 잡도록 임계값 상향.
    var ch = slot.querySelector('.q-choices');
    if (ch && ch.classList.contains('cols3')) {
      var lh = parseFloat(getComputedStyle(ch).lineHeight) || 16, wrapped = false;
      ch.querySelectorAll('.choice').forEach(function (it) {
        if (it.offsetHeight > lh * 2.6) wrapped = true;
      });
      if (wrapped) { ch.classList.remove('cols3'); ch.classList.add('cols2'); }
    }
    if (ch && ch.classList.contains('cols2')) {
      var lh1 = parseFloat(getComputedStyle(ch).lineHeight) || 16, wrapped1 = false;
      ch.querySelectorAll('.choice').forEach(function (it) {
        if (it.offsetHeight > lh1 * 2.6) wrapped1 = true;
      });
      if (wrapped1) { ch.classList.remove('cols2'); ch.classList.add('cols1'); }
    }
    // (1b) 보기/조건 박스: ㄱㄴㄷ·(가)(나)·①② 항목을 내어쓰기(hanging indent)
    slot.querySelectorAll('.cond-box').forEach(function (box) {
      var host = box.querySelector('p') || box;
      var segs = host.innerHTML.split(/<br\s*\/?>/i);
      var marker = /^\s*(?:[ㄱ-ㅎ]\s*[.·ㆍ]|\([가-힣0-9]+\)|[①-⑳])/;
      var header = /보\s*기|조\s*건/;
      var items = [], cur = null;
      segs.forEach(function (s) {
        var plain = s.replace(/<[^>]+>/g, '').trim();
        if (!plain) return;
        if (marker.test(plain)) { cur = { m: true, html: s }; items.push(cur); }
        else if (header.test(plain)) { items.push({ m: false, html: s }); cur = null; }
        else if (cur) { cur.html += ' ' + s; }
        else { items.push({ m: false, html: s }); }
      });
      if (items.some(function (i) { return i.m; })) {
        host.innerHTML = items.map(function (i) {
          return i.m ? '<div class="bogi-item">' + i.html + '</div>'
                     : '<div class="bogi-hdr">' + i.html + '</div>';
        }).join('');
      }
    });
    // (2) 배점/단서 배치
    var body = slot.querySelector('.q-body');
    if (body) {
      var lh2 = parseFloat(getComputedStyle(body).lineHeight) || 16;
      var cond = body.querySelector('.q-cond');
      var pts = body.querySelector('.q-pts');
      if (cond || pts) {
        var lc = function (el) { return Math.round(el.offsetHeight / lh2); };
        var buildTrailer = function () {
          var w = document.createElement('div');
          w.className = 'q-trailer';
          if (cond) w.appendChild(cond);
          if (cond && pts) w.appendChild(document.createTextNode(' '));
          if (pts) w.appendChild(pts);
          return w;
        };
        // 보기/조건 박스가 있고 박스 뒤에 문제텍스트가 없으면 → 배점은 stem(박스 앞)에 속함.
        // 배점을 박스 바로 앞으로 이동(인라인)한 뒤, 아래 공통 fit-로직으로 판정.
        var box = body.querySelector('.cond-box');
        if (box) {
          var onlyAfter = true;
          for (var n = box.nextSibling; n; n = n.nextSibling) {
            if (n.nodeType === 3 && n.textContent.trim()) { onlyAfter = false; break; }
            if (n.nodeType === 1 && !/q-(cond|pts|trailer)/.test(n.className)) { onlyAfter = false; break; }
          }
          if (onlyAfter) {
            var frag = document.createDocumentFragment();
            frag.appendChild(document.createTextNode(' '));
            if (cond) frag.appendChild(cond);
            if (cond && pts) frag.appendChild(document.createTextNode(' '));
            if (pts) frag.appendChild(pts);
            body.insertBefore(frag, box);
          }
        }
        // 공통 fit-로직: 인라인이 마지막 줄에 들어가면 그대로. 넘칠 때만, 트레일러 1줄이면
        // 원래 흐름 위치(마커)에 개행+우측정렬. 2줄 이상이면 인라인 유지.
        var Lfull = lc(body), saved = [];
        [cond, pts].forEach(function (e) { if (e) { saved.push([e, e.style.display]); e.style.display = 'none'; } });
        var Lbase = lc(body);
        saved.forEach(function (d) { d[0].style.display = d[1]; });
        if (Lfull > Lbase) {
          var probe = document.createElement('div');
          probe.style.cssText = 'visibility:hidden;position:absolute;left:-9999px;width:' + body.clientWidth + 'px';
          if (cond) probe.appendChild(cond.cloneNode(true));
          if (cond && pts) probe.appendChild(document.createTextNode(' '));
          if (pts) probe.appendChild(pts.cloneNode(true));
          document.body.appendChild(probe);
          var T = lc(probe);
          document.body.removeChild(probe);
          if (T <= 1) {   // 짧으면 개행+우측정렬 — 원래 흐름 위치에 삽입(끝 X)
            var anchor = cond || pts;
            var mk = document.createComment('t');
            anchor.parentNode.insertBefore(mk, anchor);
            mk.parentNode.replaceChild(buildTrailer(), mk);
          }
        }
      }
    }
  });
};
"""


def diagonal_cover_html(diff: str) -> str:
    """사선 편집형 표지 (평면좌표 좌표모티프 + Black Han Sans)."""
    graphic = '''
    <svg class="motif" viewBox="0 0 600 600" preserveAspectRatio="xMidYMid meet">
      <defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
        <path d="M40 0H0V40" fill="none" stroke="#cdd6e8" stroke-width="1"/>
      </pattern></defs>
      <rect x="0" y="0" width="600" height="600" fill="url(#grid)"/>
      <line x1="0" y1="360" x2="600" y2="360" stroke="#9fb0d4" stroke-width="2.5"/>
      <line x1="240" y1="0" x2="240" y2="600" stroke="#9fb0d4" stroke-width="2.5"/>
      <path d="M40 540 Q240 40 440 540" fill="none" stroke="#4560a8" stroke-width="4"/>
      <line x1="60" y1="120" x2="560" y2="560" stroke="#4560a8" stroke-width="4"/>
      <circle cx="360" cy="250" r="120" fill="none" stroke="#4560a8" stroke-width="4"/>
    </svg>'''
    return f'''<!doctype html><html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Gothic+A1:wght@400;600;700;900&display=swap');
@page {{ size: A4; margin: 0; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:210mm; height:297mm; }}
.cover {{ position:relative; width:210mm; height:297mm; overflow:hidden;
  background:#f4f1ea; font-family:'Gothic A1', sans-serif; color:#1b1c22; }}
.motif {{ position:absolute; right:-95mm; bottom:-70mm; width:310mm; height:310mm;
  opacity:.18; transform:rotate(-8deg); }}
.hero {{ position:absolute; top:78mm; left:20mm;
  transform:rotate(-27deg); transform-origin:left center; }}
.kicker {{ font-family:'Gothic A1'; font-weight:700; font-size:12pt; letter-spacing:.28em;
  color:#3a4a86; margin-bottom:3mm; margin-left:2mm; }}
.title {{ font-family:'Black Han Sans', sans-serif; font-size:96pt; line-height:.92;
  color:#1b1c22; letter-spacing:-.01em; }}
.rule {{ width:66mm; height:2.4pt; background:#c8342b; margin:5mm 0 4mm 2mm; }}
.tagline {{ font-family:'Gothic A1'; font-weight:600; font-size:12.5pt; letter-spacing:.02em;
  color:#4a4d59; margin-left:2mm; max-width:120mm; }}
.bottom {{ position:absolute; right:22mm; bottom:40mm; text-align:right;
  transform:rotate(-27deg); transform-origin:right center; }}
.subject {{ font-family:'Gothic A1'; font-weight:900; font-size:30pt; color:#1b1c22; }}
.level {{ display:inline-block; margin-top:6mm;
  font-family:'Gothic A1'; font-weight:700; font-size:14pt; letter-spacing:.08em;
  color:#c8342b; border:2pt solid #c8342b; border-radius:999px; padding:2.8mm 9mm; }}
.byline {{ font-family:'Gothic A1'; font-weight:600; font-size:12pt; color:#3a3c46; margin-top:8mm; }}
.byline b {{ font-weight:900; color:#1b1c22; font-size:14pt; }}
.tick {{ position:absolute; width:15mm; height:15mm; border:2pt solid #26315e; }}
.t1 {{ top:12mm; left:12mm; border-right:none; border-bottom:none; }}
.t2 {{ bottom:12mm; right:12mm; border-left:none; border-top:none; }}
.foot {{ position:absolute; left:14mm; bottom:12mm; font-family:'Gothic A1';
  font-weight:700; font-size:8.5pt; letter-spacing:.24em; color:#3a4a86; }}
</style></head>
<body><div class="cover">
  {graphic}
  <span class="tick t1"></span><span class="tick t2"></span>
  <div class="hero">
    <div class="kicker">2학기 중간대비</div>
    <div class="title">평면좌표</div>
    <div class="rule"></div>
    <div class="tagline">공통수학2 · 도형의 방정식 내신기출</div>
  </div>
  <div class="bottom">
    <div class="subject">공통수학2</div><br>
    <span class="level">난이도 {diff}</span>
    <div class="byline">심재룡 <b>T</b></div>
  </div>
  <div class="foot">MATHOLOGY · 2026</div>
</div></body></html>'''


def fetch_rows() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cmarks = ",".join(["?"] * len(CHAPTERS))
    smarks = ",".join(["?"] * len(SCHOOLS))
    cur.execute(
        f"SELECT q.question_id, q.file_source, q.school, q.grade, "
        f"       q.year, q.semester, q.exam_type, q.subject, "
        f"       q.question_number, q.question_text, q.choices, "
        f"       q.answer, q.answer_type, q.points, q.chapter, "
        f"       q.difficulty, q.has_image, q.is_subjective, "
        f"       s.solution_text "
        f"FROM questions q "
        f"LEFT JOIN solutions s ON q.question_id = s.question_id "
        f"WHERE q.chapter IN ({cmarks}) AND q.school IN ({smarks})",
        (*CHAPTERS, *SCHOOLS),
    )
    rows = [dict(r) for r in cur.fetchall()]

    qids = [r["question_id"] for r in rows]
    if qids:
        imarks = ",".join(["?"] * len(qids))
        cur.execute(
            f"SELECT question_id, image_ref, image_path, image_type "
            f"FROM images WHERE question_id IN ({imarks})",
            tuple(qids),
        )
        img_by_q: dict = {}
        sol_by_q: dict = {}
        for ir in cur.fetchall():
            target = sol_by_q if (ir["image_type"] == "solution") else img_by_q
            target.setdefault(ir["question_id"], {})[ir["image_ref"]] = ir["image_path"]
        for r in rows:
            r["images"] = img_by_q.get(r["question_id"], {})
            if r["question_id"] in sol_by_q:
                r["images_sol"] = sol_by_q[r["question_id"]]

        comp_path = ROOT / "output" / "composite_image_qids.json"
        if comp_path.exists():
            comp = set(json.loads(comp_path.read_text()))
            for r in rows:
                if r["question_id"] in comp:
                    r["img_check"] = True

    cur.close(); conn.close()
    return rows


def build_one(diff: str, all_rows: list[dict]):
    rows = [r for r in all_rows if r.get("difficulty") == diff]

    chap_idx = {c: i for i, c in enumerate(CHAPTERS)}
    rows.sort(key=lambda r: (
        chap_idx.get(r["chapter"], 999),
        DIFF_ORDER.get(r["difficulty"], 99),
        r["question_id"],
    ))

    print(f"\n=== 난이도 '{diff}': {len(rows)}문항 ===")
    by_chap = Counter(r["chapter"] for r in rows)
    for c in CHAPTERS:
        print(f"  {c:12s} {by_chap.get(c, 0)}")
    if not rows:
        print(f"  ⚠ 난이도 '{diff}' 데이터 없음 — 스킵")
        return

    overrides = {r["question_id"]: "full" for r in rows}

    # 본문 조판 전처리 (리플로우·소문제·단서/배점 마킹)
    for r in rows:
        r["question_text"] = typeset_body(r.get("question_text"))

    from pdf_engine import generate_book_pdf
    pdf_bytes = generate_book_pdf(
        rows,
        title="평면좌표",
        subtitle="공통수학2 평면좌표",
        include_source=True,
        overrides=overrides,
        logo_path=None,                       # 이음학원 로고 제거
        kicker_mark=None,
        kicker_text=None,
        divider_meta_top=f"공통수학2 평면좌표 · 난이도 {diff}",
        divider_footer_title=f"공통수학2 평면좌표 · 난이도 {diff}",
        divider_footer_sub="심재룡 T",
        cover_main_title="2학기 중간대비",     # 표지 제목
        cover_tagline="공통수학2 평면좌표",     # 그 밑
        cover_big_word=f"난이도 {diff}",        # 그 밑 (큰 워드)
        cover_kicker="MATHOLOGY · 2026",
        cover_footer_main="MATHOLOGY · 2026",
        cover_footer_sub=f"2학기 중간대비 · 공통수학2 평면좌표 · 난이도 {diff}",
        page_running_left=f"공통수학2 평면좌표 · {diff}",
        extra_css=CHROME_FONT_CSS,
        extra_js=TYPESET_JS,
    )

    # 기본 표지(1p)를 사선 커스텀 표지로 교체 (PyMuPDF)
    import fitz
    from pdf_engine import html_to_pdf_bytes
    cover_bytes = html_to_pdf_bytes(diagonal_cover_html(diff))
    book = fitz.open(stream=pdf_bytes, filetype="pdf")
    cover = fitz.open(stream=cover_bytes, filetype="pdf")
    book.delete_page(0)                     # 기본 표지 제거
    book.insert_pdf(cover, start_at=0)      # 커스텀 표지 맨 앞 삽입
    pdf_bytes = book.tobytes()
    book.close(); cover.close()

    book_dir = Path.home() / "클로드교재"
    book_dir.mkdir(exist_ok=True)
    tag = f" [미리보기-{_FONT_KEY}]" if _PREVIEW_FONT else ""
    out_path = book_dir / f"공통수학2 평면좌표 {diff}{tag}.pdf"
    out_path.write_bytes(pdf_bytes)
    subprocess.run(["xattr", "-c", str(out_path)], check=False)
    print(f"  [OK] {out_path} ({out_path.stat().st_size/1024/1024:.1f}MB)")


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    diffs = ["상", "중", "하"] if arg == "all" else [arg]
    for d in diffs:
        assert d in ("상", "중", "하"), f"난이도는 상/중/하 — {d!r}"

    print("[1/2] 로컬 DB 조회...")
    all_rows = fetch_rows()
    print(f"  매칭 문항(전체): {len(all_rows)}")

    print("[2/2] 난이도별 빌드")
    for d in diffs:
        build_one(d, all_rows)


if __name__ == "__main__":
    main()
