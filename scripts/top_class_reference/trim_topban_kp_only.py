"""기존 KP+WORKBOOK 합본에서 '고난도정복' 챕터 + 뒤쪽 WORKBOOK 만 제외한
KP(유형별) 전용 축약본 생성 — 2026-08-05.

소스 HWPX가 없는 책(원의방정식)도 다뤄야 해서, 원본 문서를 다시 빌드하는 대신
이미 렌더된 합본 PDF를 페이지 단위로 잘라서 재조립하는 방식(fitz page surgery).

구조 전제(두 소스 파일 모두 확인): page0=KP 표지, page1=목차, page2~=KP 본문
(유형별 다이바이더+문제 ... 고난도정복 다이바이더+문제) → Solutions 다이바이더 →
유형별 해설 ... 고난도정복 해설 → WORKBOOK. '고난도정복'은 항상 마지막 챕터라
문제 구간에서는 정확히 한 덩어리로 잘리고, 해설 구간은 문항 순서대로 흐르므로
고난도정복 해설도 항상 전체 해설의 마지막 연속 블록 — 그 뒤(=WORKBOOK 포함)를
통째로 버리면 됨. 단, 그 경계가 페이지 중간에서 갈리는 경우(칼럼 레이아웃)가
있어 해당 1페이지만 정밀 화이트박스 처리.
"""
import os, re, base64, subprocess
import fitz
from playwright.sync_api import sync_playwright

SRC_DIR = "/Users/youngwoolee/Downloads/수업자료/탑반 교재"
CW, CH = 595.9199, 842.8800

BOOKS = [
    {
        "src": f"{SRC_DIR}/2026 KERNEL POINT_원의방정식+워크북.pdf",
        "out": f"{SRC_DIR}/2026 KERNEL POINT_원의방정식_고난도정복WORKBOOK제외.pdf",
        "chapter": "원의 방정식",
    },
    {
        "src": f"{SRC_DIR}/도형의이동_KERNEL+WORKBOOK_합본.pdf",
        "out": f"{SRC_DIR}/도형의이동_KERNEL_고난도정복WORKBOOK제외.pdf",
        "chapter": "도형의 이동",
    },
]

paper_black = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/Paperlogy-9Black.ttf"), "rb").read()).decode()
paper_eb = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/Paperlogy-8ExtraBold.ttf"), "rb").read()).decode()


def html_to_pdf(html):
    with sync_playwright() as p:
        b = p.chromium.launch(); page = b.new_page()
        page.set_content(html, wait_until="networkidle")
        page.wait_for_function("document.fonts.ready")
        out = page.pdf(format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    return out


def get_slot_nums_problem(page):
    nums = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0: continue
        for line in b["lines"]:
            for s in line["spans"]:
                t = s["text"].strip()
                if "Paperlogy-9Black" in s.get("font", "") and s["size"] < 20 \
                   and re.fullmatch(r"\d{1,3}", t):
                    nums.append(int(t))
    return nums


def find_first_solution_span(page, target):
    d = page.get_text("dict")
    for b in d["blocks"]:
        if b.get("type") != 0: continue
        for line in b["lines"]:
            for s in line["spans"]:
                if s["text"].strip() == str(target) and s["size"] > 12:
                    return s["bbox"]
    return None


for cfg in BOOKS:
    src = fitz.open(cfg["src"])
    print(f"[LOAD] {cfg['src']} — {src.page_count}p")

    # 1. 구조 탐지
    div_start = None
    for i in range(src.page_count):
        t = src[i].get_text()
        if "고난도정복" in t and "CHAPTER" in t.replace(" ", ""):
            div_start = i; break
    sol_start = None
    for i in range(src.page_count):
        if "Solutions" in src[i].get_text():
            sol_start = i; break
    assert div_start is not None and sol_start is not None, "구조 탐지 실패"

    nums_after_div = get_slot_nums_problem(src[div_start + 1])
    K = min(nums_after_div) - 1  # 마지막 유형별 문항번호
    print(f"[DETECT] 고난도정복 다이바이더={div_start+1}p, Solutions={sol_start+1}p, K(유형별 마지막 문항)={K}")

    # 2. 유형별 해설이 끝나는 경계 페이지 탐색 (K+1번 처음 등장 페이지)
    boundary_page = None
    for i in range(sol_start, src.page_count):
        t = src[i].get_text()
        if re.search(rf"(?<!\d){K+1}\s*\n?\s*번", t):
            boundary_page = i; break
    assert boundary_page is not None, "K+1번 해설 위치 탐색 실패"

    # 이 페이지에 K번(유지 대상)도 같이 있는지 확인 → 있으면 정밀 redaction 필요
    has_K_on_boundary = bool(re.search(rf"(?<!\d){K}\s*\n?\s*번", src[boundary_page].get_text()))
    print(f"[DETECT] 경계 페이지={boundary_page+1}p, 같은 페이지에 {K}번 존재={has_K_on_boundary}")

    # 3. 새 문서 조립: 표지 + (목차 placeholder) + KP 문제(고난도정복 제외) + KP 해설(고난도정복 제외)
    new_doc = fitz.open()
    new_doc.insert_pdf(src, from_page=0, to_page=0)  # 표지
    toc_placeholder_idx = new_doc.page_count
    new_doc.insert_pdf(src, from_page=0, to_page=0)  # 자리만 차지 (나중에 교체)
    problem_start_new = new_doc.page_count
    new_doc.insert_pdf(src, from_page=2, to_page=div_start - 1)  # 유형별 문제만
    sol_start_new = new_doc.page_count
    new_doc.insert_pdf(src, from_page=sol_start, to_page=boundary_page)  # 유형별 해설만 (+경계페이지)

    # 4. 경계 페이지 redaction (같은 페이지에 K/K+1 혼재 시 K+1 이후 부분만 지움)
    if has_K_on_boundary:
        bp = new_doc[new_doc.page_count - 1]
        bbox = find_first_solution_span(bp, K + 1)
        redact_rect = fitz.Rect(bbox[0] - 15, bbox[1] - 15, CW - 30, CH - 45)
        bp.draw_rect(redact_rect, color=None, fill=(1, 1, 1), overlay=True)
        print(f"[REDACT] 경계 페이지 {K+1}번 이후 영역 화이트박스 처리: {redact_rect}")

    kp_total_new = new_doc.page_count

    # 5. 문제 페이지의 기존 "정답 p.N" 오버레이 지우고 재계산
    def get_slot_nums(page):
        return get_slot_nums_problem(page)

    for pidx in range(problem_start_new, sol_start_new):
        page = new_doc[pidx]
        w = page.rect.width
        page.draw_rect(fitz.Rect(w - 92, 24, w - 20, 44), color=None, fill=(1, 1, 1), overlay=True)

    # 해설 페이지 하단 기존 "- N -" 페이지번호 지우기
    for pidx in range(sol_start_new, kp_total_new):
        page = new_doc[pidx]
        w, h = page.rect.width, page.rect.height
        page.draw_rect(fitz.Rect(w / 2 - 50, h - 34, w / 2 + 50, h - 10), color=None, fill=(1, 1, 1), overlay=True)

    COMBINED_OFFSET = 2  # 표지+목차
    sol_map = {}
    for i in range(sol_start_new, kp_total_new):
        txt = new_doc[i].get_text()
        for m in re.finditer(r"(?<![\d])(\d{1,3})\s*번\b", txt):
            n = int(m.group(1))
            if 1 <= n <= K and n not in sol_map:
                sol_map[n] = i + 1  # 절대 페이지 번호(1-idx), 이 문서 자체가 최종본이라 오프셋 불필요

    overlay_count = 0
    for pidx in range(problem_start_new, sol_start_new):
        nums = [n for n in get_slot_nums(new_doc[pidx]) if 1 <= n <= K]
        if not nums: continue
        first_num = min(nums)
        sol_pg = sol_map.get(first_num)
        if not sol_pg: continue
        page = new_doc[pidx]
        w = page.rect.width
        text = f"정답  p.{sol_pg}"
        try:
            page.insert_text((w - 86, 37), text, fontname="AppleGothic", fontsize=8, color=(0.78, 0.23, 0.17))
        except Exception:
            page.insert_text((w - 86, 37), text, fontsize=8, color=(0.78, 0.23, 0.17))
        overlay_count += 1

    for pidx in range(sol_start_new, kp_total_new):
        page = new_doc[pidx]
        w, h = page.rect.width, page.rect.height
        try:
            page.insert_text((w / 2 - 10, h - 22), f"- {pidx + 1} -", fontname="helv", fontsize=9, color=(0.3, 0.3, 0.35))
        except Exception:
            pass
    print(f"[OVERLAY] {overlay_count}개 페이지 재매핑, 해설 {len(sol_map)}개")

    # 6. 목차 재생성 (KERNEL POINT / 정답 및 해설 2줄만 — WORKBOOK 항목 제거)
    kp_first_page_final = problem_start_new + 1
    kp_sol_page_final = sol_start_new + 1
    TOC_HTML = f"""<!DOCTYPE html><html><head><style>
@font-face {{ font-family:'Paperlogy 9 Black'; src:url(data:font/ttf;base64,{paper_black}) format('truetype'); }}
@font-face {{ font-family:'Paperlogy 8 ExtraBold'; src:url(data:font/ttf;base64,{paper_eb}) format('truetype'); }}
@page {{ size:A4; margin:0; }}
body {{ margin:0; padding:60pt 55pt; width:{CW}pt; height:{CH}pt; font-family:'Paperlogy 8 ExtraBold', sans-serif; background:#f9f7f2; color:#16171b; }}
.side {{ position:absolute; left:32pt; top:60pt; bottom:60pt; width:6pt; background:#c73a2b; }}
.tag {{ font-size:9pt; color:#23315e; letter-spacing:3pt; margin-left:20pt; }}
.h1 {{ font-family:'Paperlogy 9 Black', sans-serif; font-size:52pt; letter-spacing:-1.5pt; margin:6pt 0 4pt 20pt; }}
.sub {{ font-size:10.5pt; color:#4a4d59; margin-left:20pt; letter-spacing:-0.3pt; }}
hr {{ border:0; border-top:1.5pt solid #16171b; margin:26pt 20pt 12pt; }}
ul {{ list-style:none; padding:0; margin:0 20pt; }}
li {{ display:flex; align-items:baseline; padding:11pt 0; border-bottom:0.5pt dotted #8a8f9d; }}
.name {{ font-family:'Paperlogy 9 Black', sans-serif; font-size:14pt; flex:0 0 auto; }}
.dot {{ flex:1; border-bottom:1pt dotted #b0b4c0; margin:0 8pt; height:8pt; }}
.page {{ font-family:'Paperlogy 9 Black', sans-serif; font-size:13pt; color:#c73a2b; }}
</style></head><body>
<div class="side"></div>
<div class="tag">C O N T E N T S</div>
<div class="h1">차 례</div>
<div class="sub">공통수학2 · {cfg['chapter']} · KERNEL POINT (고난도정복 제외)</div>
<hr>
<ul>
  <li><span class="name">KERNEL POINT</span><span class="dot"></span><span class="page">p. {kp_first_page_final}</span></li>
  <li><span class="name">KERNEL POINT · 정답 및 해설</span><span class="dot"></span><span class="page">p. {kp_sol_page_final}</span></li>
</ul>
</body></html>"""
    toc_pdf = fitz.open("pdf", html_to_pdf(TOC_HTML))
    new_doc.delete_page(toc_placeholder_idx)
    new_doc.insert_pdf(toc_pdf, start_at=toc_placeholder_idx)
    toc_pdf.close()

    new_doc.save(cfg["out"], deflate=True, garbage=4)
    new_doc.close(); src.close()
    subprocess.run(["xattr", "-c", cfg["out"]])
    print(f"[DONE] {cfg['out']}  총 {fitz.open(cfg['out']).page_count}p\n")
