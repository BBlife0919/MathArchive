"""소하고 2026 1학년 2학기 중간(공수2) 기출분석지(홍보용) 빌더.

/기출분석 틀(build_gm_1_2a_report.py)의 CSS·헬퍼를 재사용한다.
입력 : output/pirate_analysis/sh_2026_2a/{src,assets}
출력 : output/pirate_analysis/sh_2026_2a/소하고1_2026_2학기_중간_기출분석_이영우T.{html,pdf}
색   : 파랑·흰색만(적녹색약). 매칭 이미지 원본 색은 그대로.
"""
from __future__ import annotations
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_gm_1_2a_report import CSS as BASE_CSS, uri, img  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "output" / "pirate_analysis" / "sh_2026_2a"
SRC, AS = D / "src", D / "assets"
NAME = "소하고1_2026_2학기_중간_기출분석_이영우T"

# (번호, 단원, 배점) — 소하고 2026 1-2-a 공수2 (HWPX 타이핑본 기준, 서술형1은 소문항 2+2+6=10점). 합계 100.
ITEMS = [
    (1, "원의 방정식", 3.5), (2, "도형의 이동", 3.5), (3, "도형의 이동", 3.6), (4, "평면좌표", 3.7),
    (5, "직선의 방정식", 3.8), (6, "집합", 3.8), (7, "직선의 방정식", 3.9), (8, "집합", 3.9),
    (9, "집합", 4.0), (10, "원의 방정식", 4.0), (11, "집합", 4.1), (12, "원의 방정식", 4.1),
    (13, "집합", 4.2), (14, "원의 방정식", 4.2), (15, "집합", 4.3), (16, "원의 방정식", 4.3),
    (17, "집합", 4.4), (18, "도형의 이동", 4.4), (19, "도형의 이동", 4.5), (20, "직선의 방정식", 4.5),
    (21, "원의 방정식", 4.6), (22, "도형의 이동", 4.7),
    ("서술형1", "도형의 이동", 10.0),
]
HIT = {19, 20, 21, 22, "서술형1"}               # 교재·자작문항 적중
SOURCE = set()
HARD = {19, 20, 21, 22, "서술형1"}              # 변별 (사용자 지정)


def tier(no) -> str:
    if no in HARD:
        return "변별"
    return "기본" if isinstance(no, int) and no <= 9 else "발전"


def table_rows() -> str:
    rows = []
    for no, ch, sc in ITEMS:
        hit, t = no in HIT, tier(no)
        mark = "적중" if hit else ("출처" if no in SOURCE else "적중(전형적문항)")
        rows.append(
            f"<tr class='{'hit' if hit else ''}'><td class='c no'>{no}</td><td>{ch}</td>"
            f"<td class='c'>{sc:.1f}</td><td class='c'><span class='tier t-{t}'>{t}</span></td>"
            f"<td class='c hm'>{mark}</td></tr>"
        )
    return "\n".join(rows)


# ── 글자 크기 균일화: 이미지마다 글자 높이(px)를 측정해 화면상 글자 크기가 같아지게 mm 폭을 계산 ──
import functools
import numpy as np
import scipy.ndimage as ndi
from PIL import Image

REF = {}
BOOST = {}


def _measure(path) -> float:
    """한글 음절(정사각에 가까운 연결요소)의 높이 중앙값(px)."""
    im = np.array(Image.open(path).convert("L")) < 140
    lab, _ = ndi.label(im)
    hs = []
    for sl in ndi.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if 8 <= h <= 60 and 0.75 <= w / h <= 1.3:
            hs.append(h)
    return float(np.median(hs)) if hs else 13.0


@functools.lru_cache(maxsize=None)
def glyph_px(name: str) -> tuple[float, int, int]:
    im = Image.open(SRC / REF.get(name, name))
    return _measure(SRC / REF.get(name, name)), im.width, im.height


def mm_size(name: str, T: float) -> tuple[float, float]:
    g, _, _ = glyph_px(name)
    w, h = Image.open(SRC / name).size
    k = T / g * BOOST.get(name, 1.0)
    return w * k, h * k


INNER = 194.0     # 페이지 내부 폭(mm)
BODY_H = 208.0    # 문항 머리줄·설명 띠를 뺀 본문 높이(mm)
HDR, PADC, GAP, RGAP = 9.0, 5.0, 3.0, 5.0
EXTRA = 30.0      # 설명 띠가 없는 쪽에서 더 쓸 수 있는 높이(mm)


def card_dims(kind: str, label: str, files: list[str], T: float):
    """카드 하나의 (폭 mm 목록, 폭 mm, 높이 mm). exam 카드는 그림을 가로로, 나머지는 세로로 쌓는다."""
    sz = [mm_size(f, T) for f in files]
    if kind == "exam":
        w = sum(a for a, _ in sz) + GAP * (len(sz) - 1) + PADC
        h = max(b for _, b in sz) + HDR + PADC
        if w > INNER and len(sz) > 1:          # 가로로 안 들어가면 세로로 쌓는다
            w = max(a for a, _ in sz) + PADC
            h = sum(b for _, b in sz) + GAP * (len(sz) - 1) + HDR + PADC
    else:
        w = max(a for a, _ in sz) + PADC
        h = sum(b for _, b in sz) + GAP * (len(sz) - 1) + HDR + PADC
    return [a for a, _ in sz], w, h


def flow_pages(pg: dict, T: float, mode: str = "stack"):
    """한 문항을 페이지로 배치한다. 모든 페이지에 시험 문항 카드와 교재 카드가 함께 들어간다(시험 카드는 매 쪽 반복).
    stack: 시험 카드 위 / 교재 카드 아래(폭 동일).  side: 시험 카드 왼쪽 / 교재 카드 오른쪽(글자 크기 동일, 폭은 각자).
    반환: (시험카드, 교재카드들, 시험치수, 교재치수, 카드폭(stack)/(We,Wg)(side), 페이지별 행, 초과여부)"""
    exam = ("exam", "시험 문항", pg["exam"])
    groups = [("m", lbl, fs) for lbl, fs in pg["groups"]]
    ed = card_dims("exam", exam[1], exam[2], T)
    gd = [card_dims("m", l, f, T) for _, l, f in groups]
    if mode == "side":
        We, Wg = ed[1], max(d[1] for d in gd)
        too = We + Wg + RGAP > INNER or ed[2] > BODY_H or any(d[2] > BODY_H for d in gd)
        pages, cur, used = [], [], 0.0
        for i, d in enumerate(gd):
            if cur and used + d[2] + RGAP > BODY_H + EXTRA:       # 마지막 쪽이 아니면 설명 띠 자리가 필요 없다
                pages.append(cur); cur, used = [], 0.0
            cur.append([i]); used += d[2] + RGAP
        if used > BODY_H and len(cur) > 1:                         # 마지막 쪽은 설명 띠 자리를 확보
            pages.append(cur[:-1]); cur = cur[-1:]
        pages.append(cur)
        return exam, groups, ed, gd, (We, Wg), pages, too
    W = min(INNER, max([ed[1]] + [d[1] for d in gd]))
    too = max([ed[1]] + [d[1] for d in gd]) > INNER
    cap = BODY_H - ed[2] - RGAP
    too |= any(d[2] > cap for d in gd)
    rows, i = [], 0
    while i < len(groups):
        if i + 1 < len(groups) and 2 * W + RGAP <= INNER:
            rows.append([i, i + 1]); i += 2
        else:
            rows.append([i]); i += 1
    pages, cur, used = [], [], 0.0
    for r in rows:
        h = max(gd[j][2] for j in r)
        if cur and used + h + RGAP > cap + EXTRA:
            pages.append(cur); cur, used = [], 0.0
        cur.append(r); used += h + RGAP
    if used > cap and len(cur) > 1:
        pages.append(cur[:-1]); cur = cur[-1:]
    pages.append(cur)
    return exam, groups, ed, gd, W, pages, too


def total_pages(T: float) -> int:
    return sum(len(flow_pages(pg, T)[5]) for pg in PAGES)


def card_html(c, d, W) -> str:
    kind, label, files = c
    imgs = "".join(f"<img style='width:{w:.1f}mm' src='{uri(SRC / f)}'/>" for f, w in zip(files, d[0]))
    if kind == "exam":
        return f"<div class='kcard exam' style='width:{W:.1f}mm'><div class='kh'>{label}</div><div class='kimgs'>{imgs}</div></div>"
    return f"<div class='kcard' style='width:{W:.1f}mm'><div class='kh alt'>{label}</div><div class='kimgs'>{imgs}</div></div>"


def best_T_q(pg: dict, cap: float = 4.6):
    """문항 하나에서 (시험 카드 + 교재 카드가 같은 쪽에 들어가는) 최대 글자 높이와 그때의 배치 방식."""
    best = (0.0, "stack")
    for mode in ("stack", "side"):
        lo, hi = 0.8, cap
        if not flow_pages(pg, hi, mode)[6]:
            cand = hi
        else:
            for _ in range(30):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if not flow_pages(pg, mid, mode)[6] else (lo, mid)
            cand = lo
        if cand > best[0] + 1e-6:
            best = (cand, mode)
    return best


def key_pages_html(_T=None) -> str:
    flat = []
    for pg in PAGES:
        T, mode = best_T_q(pg)
        print(f"  {pg['no']} T={T:.2f}mm {mode}")
        exam, groups, ed, gd, W, pages, _ = flow_pages(pg, T, mode)
        for pi, rows in enumerate(pages):
            flat.append((pg, exam, groups, ed, gd, W, rows, pi, len(pages), mode))
    out = []
    for n, (pg, exam, groups, ed, gd, W, rows, pi, np_, mode) in enumerate(flat, 1):
        if mode == "side":
            We, Wg = W
            left = card_html(exam, ed, We)
            right = "".join(card_html(groups[r[0]], gd[r[0]], Wg) for r in rows)
            body = f"<div class='side' style='grid-template-columns:{We:.1f}mm {Wg:.1f}mm'><div>{left}</div><div class='sidecol'>{right}</div></div>"
        else:
            body = f"<div class='krow n1'>{card_html(exam, ed, W)}</div>"
            for r in rows:
                body += f"<div class='krow n{len(r)}'>" + "".join(card_html(groups[j], gd[j], W) for j in r) + "</div>"
        band = f"<div class='kband'>{pg['cap']}</div>" if pi == np_ - 1 else ""
        meta = pg["meta"] if pi == 0 else "이어서"
        out.append(f"""
<section class="page keyp">
  <div class="khead"><span class="kno">{pg['no']}</span><span class="kmeta">{meta}</span><span class="kcount">{n} / {len(flat)}</span></div>
  <div class="kmid">{body}{band}</div>
</section>""")
    return "\n".join(out)


def best_T(max_pages: int = 99) -> float:
    """글자 높이 T를 키워 가며, 폭 초과 없이 key 페이지 수가 max_pages 이하인 최대 T."""
    lo, hi = 1.2, 4.0
    for _ in range(30):
        mid = (lo + hi) / 2
        ok = all(not flow_pages(pg, mid)[6] for pg in PAGES) and total_pages(mid) <= max_pages
        lo, hi = (mid, hi) if ok else (lo, mid)
    return lo


# 핵심 적중 페이지 정의 (사용자 제공 적중포인트 반영)
PAGES = [
    dict(no="19번", meta="배점 4.5", exam=["o19.png"], cols=1,
         groups=[("자체교재 Vol.4 · 128번", ["m19.png"])],
         cap="그림과 아이디어가 정확히 적중"),
    dict(no="20번", meta="배점 4.5", exam=["o20.png"], cols=1,
         groups=[("자체교재 Vol.2 · 204번", ["m20.png"])],
         cap="완전 적중"),
    dict(no="21번", meta="배점 4.6", exam=["o21.png"], cols=1,
         groups=[("자작문항 Vol.1", ["m21.png"])],
         cap="프린트 원본 y = x → 직선식 변형 적중<br>넓이 2배 → 3배 적중 · m<sub>1</sub> + m<sub>2</sub> 적중"),
    dict(no="22번", meta="배점 4.7", exam=["o22.png"], cols=1,
         groups=[("자작문항 Vol.2 · 22-A", ["m22.png"])],
         cap="프린트 원본 최솟값 0 → 최솟값 변형 적중<br>구하는 값의 형태까지 적중"),
    dict(no="서술형1", meta="배점 10.0 (2 + 2 + 6)", exam=["os1.png"], cols=1,
         groups=[("자체교재 Vol.3 · 72번", ["ms1a.png"]), ("자체교재 Vol.3 · 75번", ["ms1b.png"])],
         cap="기본 문제들의 결합 문제"),
]

BOOKS = [("kp_plane", "평면좌표"), ("kp_line", "직선의 방정식"), ("kp_won", "원의 방정식"), ("kp_do", "도형의 이동"),
         ("iv1", "자작문항 Vol.1"), ("iv2", "자작문항 Vol.2")]


def book_grid(kind: str) -> str:
    return "\n".join(
        f"<div class='bk'><div class='bkimg'>{img(AS / f'{k}_{kind}.png')}</div><div class='bkt'>{lbl}</div></div>"
        for k, lbl in BOOKS)


EXTRA_CSS = """
.hot{background:#1b2f6b;color:#fff;padding:24mm 20mm}
.hot-pill{display:inline-block;border:0.7mm solid #fff;border-radius:8mm;padding:2mm 7mm;font-size:14pt;font-weight:800}
.hot-h{font-size:84pt;font-weight:900;line-height:1.08;letter-spacing:-3pt;margin-top:14mm}
.hot-h span{color:#8fb4ff}
.hot-stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6mm;margin-top:20mm;border-top:0.8mm solid #fff;padding-top:9mm}
.hot-stats b{display:block;font-size:40pt;font-weight:900;line-height:1.1}
.hot-stats span{font-size:13pt;font-weight:700;color:#cfe0ff}
.hot-chips{display:flex;flex-wrap:wrap;gap:3mm;margin-top:14mm}
.hot-chips i{font-style:normal;font-weight:900;font-size:16pt;background:#fff;color:#1b2f6b;padding:2mm 6mm;border-radius:2mm}
.hot-foot{position:absolute;left:20mm;bottom:18mm;font-size:13pt;font-weight:700;color:#cfe0ff;letter-spacing:1pt}
.title{font-size:32pt}
.cv-t2{font-size:56pt}
.kmid{gap:6mm}
.keyp{padding:10mm 8mm !important}
.keyp .khead{margin-bottom:4mm}
.keyp .kno{font-size:28pt}
.kcard.exam{margin-bottom:5mm}
.kimgs.row{flex-direction:row;justify-content:center;align-items:flex-start;gap:3mm}
.kimgs img{display:block}
.kimgs{align-items:center}
.krow{display:grid;gap:5mm;align-items:start;justify-content:center;margin-bottom:5mm}
.side{display:grid;gap:5mm;justify-content:center;align-items:start}
.sidecol{display:flex;flex-direction:column;gap:5mm}
.krow.n1{grid-template-columns:auto}
.krow.n2{grid-template-columns:auto auto}
table.q td{padding:1.0mm 3mm}
table.q td.hm{font-size:10.5pt;white-space:nowrap}
table.q th:last-child{width:34mm}
.kband{line-height:1.5;background:#1b2f6b;color:#fff;border-radius:3mm;padding:5mm 7mm;font-size:19pt;font-weight:900;text-align:center;letter-spacing:-0.5pt;margin-top:4mm;border-left:0}
.bkgrid4{display:flex;flex-wrap:wrap;justify-content:center;gap:10mm 4mm;margin-top:12mm}
.bkgrid4 .bk{width:43mm}
.bkgrid4 .bkimg{height:62mm}
.bkgrid4 .bkt{font-size:14pt;line-height:1.3}
"""


def html() -> str:
    seat, logo = uri(AS / "instructor_seated.jpg"), uri(AS / "eum_logo.png")
    key_pages = key_pages_html()
    grid4 = lambda kind: book_grid(kind)
    hard_pts = sum(sc for no, _, sc in ITEMS if no in HARD)
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"/><title>소하고 1학년 2학기 중간고사 기출분석</title>
<style>{BASE_CSS}{EXTRA_CSS}</style></head><body>

<section class="page cover"><div class="cv-in">
  <div class="cv-t1">2026학년도 2학기 중간고사</div>
  <div class="cv-t2">소하고1<br>공통수학2</div>
  <div class="cv-t3">기출 분석</div>
  <img class="cv-photo" src="{seat}"/>
  <div class="cv-name">이영우<span>T</span><small>이음학원 수학</small></div>
  <img class="cv-logo" src="{logo}"/>
</div></section>

<section class="page hot">
  <div class="hot-pill">변별력 문제 5 / 5 적중</div>
  <div class="hot-h">자작문항<br><span>연전연승</span></div>
  <div class="hot-stats">
    <div><b>5문항</b><span>적중 · {hard_pts:.1f}점</span></div>
    <div><b>4 / 4</b><span>객관식 변별 적중</span></div>
    <div><b>1 / 1</b><span>서술형 변별 적중</span></div>
  </div>
  <div class="hot-chips"><i>19번</i><i>20번</i><i>21번</i><i>22번</i><i>서술형1</i></div>
  <div class="hot-foot">이영우T 자체 교재 · 자작문항</div>
</section>

<section class="page">
  <div class="title">변별 문제 외에는<br><span style="color:var(--or)">평이한 전형적 문제</span>로 구성된 시험</div>
  <div class="big3"><div><b>5문항</b><span>19 · 20 · 21 · 22 · 서술형1</span></div><div><b>{hard_pts:.1f}점</b><span>변별 문항 배점</span></div><div><b>5 / 5</b><span>변별 문항 적중</span></div></div>
  <div class="lines">
    <div>변별 문제 외에는 평이한 전형적인 문제들로 구성</div>
    <div>변별 문제가 학교 프린트에서 많이 출제</div>
    <div>전형적인 문제를 압도적으로 빠르게 풀어낼 수 있어야 합니다</div>
  </div>
</section>

<section class="page">
  <div class="title">이렇게 준비해야 합니다</div>
  <div class="st">
    <div class="s"><div><div class="sk">전형적인 문제는 압도적으로 빠르게</div><div class="sv">유형별 풀이가 숙지되어 있어야 합니다</div></div></div>
    <div class="s"><div><div class="sk">학교 프린트 문제를 철저히</div><div class="sv">기계적으로 원본 문제만 잘 풀어서는 안 됩니다</div></div></div>
    <div class="s" style="border-bottom:0.5mm solid var(--ink)"><div><div class="sk">변형된 문제로 많이 연습</div><div class="sv">원본이 바뀌어도 풀어내는 힘이 점수를 가릅니다</div></div></div>
  </div>
  <div class="quote"><small>이영우T 코멘트</small>프린트 원본 그대로 나오지 않았습니다. 직선식, 넓이의 비, 구하는 값의 형태가 바뀌어도 같은 구조로 풀어내려면 변형된 문제로 연습을 많이 해봐야 합니다.</div>
</section>

<section class="page">
  <div class="title" style="font-size:26pt">소하고 전 문항</div>
  <table class="q"><thead><tr><th>번호</th><th>단원</th><th>배점</th><th>구분</th><th>교재</th></tr></thead><tbody>{table_rows()}</tbody></table>
  <div class="tnote">파란 행 = 이영우T 교재 · 자작문항 적중</div>
</section>

{key_pages}

<section class="page wide">
  <div class="title">시험에 나오는 유형만<br>직접 집필합니다</div>
  <div class="bkgrid4">{grid4('cover')}</div>
</section>

<section class="page wide">
  <div class="bkgrid4" style="margin-top:6mm">{grid4('page')}</div>
</section>

<section class="page dark">
  <span class="only">광명 유일</span>
  <div class="big">17만 문항<br><span>내신 기출 문제은행</span></div>
  <div class="dsub">매쏠로지 · MATHOLOGY<br><b style="color:var(--navy)">강사가 직접 개발하고 직접 작업한 시스템</b></div>
  <img class="shot" src="{uri(AS/'site_hero.png')}"/>
  <div class="nums"><div><b>170,000+</b><span>내신 기출</span></div><div><b>60초</b><span>시험지 완성</span></div><div><b>100%</b><span>수식 자동 조판</span></div></div>
  <div class="url">bblife0919.github.io/MathArchive</div>
</section>

<section class="page">
  <div class="title" style="font-size:26pt">기출 · 시험지 · 오답 진단을 한 곳에서</div>
  <div style="height:8mm"></div>
  <img class="shotl" src="{uri(AS/'site_stats.png')}"/><div class="cap">17만 기출을 한곳에</div>
  <div class="two"><div><img class="shotl" src="{uri(AS/'site_exam.png')}"/><div class="cap">클릭 몇 번으로 시험지 완성</div></div>
  <div><img class="shotl" src="{uri(AS/'site_prism.png')}"/><div class="cap">오답 원인 5가지 진단</div></div></div>
</section>

<section class="page wide">
  <div class="title" style="font-size:24pt;margin-bottom:5mm">실제 사용하는 화면</div>
  <img class="shotl" src="{uri(AS/'app_1_c.jpg')}"/><div class="cap" style="margin:2mm 0 5mm">문제은행 · 필터와 검색으로 즉시 조회</div>
  <img class="shotl" src="{uri(AS/'app_2_c.jpg')}"/><div class="cap" style="margin:2mm 0 5mm">광명지역 기출 검색</div>
  <img class="shotl" src="{uri(AS/'app_3_c.jpg')}"/><div class="cap" style="margin:2mm 0 0">시험지 조립 · 실시간 미리보기</div>
</section>

<section class="page closing">
  <div class="hd">소하고 내신,<br><span>데이터와 교재</span>로<br>준비합니다.</div>
  <div class="sg">수학 Instructor &nbsp;<b>이영우</b></div>
</section>
</body></html>"""


def main() -> int:
    out_html, out_pdf = D / f"{NAME}.html", D / f"{NAME}.pdf"
    out_html.write_text(html(), encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(out_html.as_uri(), wait_until="networkidle")
        pg.wait_for_timeout(600)
        bad = pg.evaluate("""() => [...document.querySelectorAll('.page')].map((p, i) => {
          const pr = p.getBoundingClientRect(); let worst = 0;
          p.querySelectorAll('*').forEach(e => { const r = e.getBoundingClientRect(); if (r.height > 0) worst = Math.max(worst, r.bottom - pr.bottom, pr.left - r.left, r.right - pr.right); });
          return [i + 1, Math.round(worst)]; }).filter(x => x[1] > 1)""")
        print("넘침 의심 페이지:", bad or "없음")
        pg.pdf(path=str(out_pdf), print_background=True, format="A4",
               margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    print(out_pdf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
