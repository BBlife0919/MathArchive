"""KP v2 마무리: 표지 교체 → 정답 마커 오버레이 → 목차 → WORKBOOK 합본."""
import fitz, base64, os, re, subprocess, io
from playwright.sync_api import sync_playwright
from PIL import Image as PIL

CW, CH = 595.9199, 842.8800
KP_SRC = "/tmp/dohyeong_kernel_v2.pdf"
WB_SRC = "/tmp/dohyeong_workbook.pdf"
OUT = "/Users/youngwoolee/Downloads/수업자료/탑반 교재/도형의이동_KERNEL+WORKBOOK_합본.pdf"

paper_black = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/Paperlogy-9Black.ttf"),"rb").read()).decode()
paper_eb = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/Paperlogy-8ExtraBold.ttf"),"rb").read()).decode()

# ─── 1. KP 표지 교체 (평면좌표 합본 구조: KERNEL POINT 대형 대각선 제목)
COVER_HTML = f"""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap" rel="stylesheet">
<style>
@font-face {{ font-family:'Paperlogy 9 Black'; src:url(data:font/ttf;base64,{paper_black}) format('truetype'); }}
@font-face {{ font-family:'Paperlogy 8 ExtraBold'; src:url(data:font/ttf;base64,{paper_eb}) format('truetype'); }}
@page {{ size: A4; margin: 0; }} * {{ box-sizing: border-box; }}
body {{ margin:0; padding:0; width:{CW}pt; height:{CH}pt; position:relative; background:#f4f1ea; overflow:hidden; font-family:'Paperlogy 8 ExtraBold', sans-serif; }}
.bg-svg {{ position:absolute; inset:0; width:100%; height:100%; opacity:0.35; }}
.corner {{ position:absolute; width:42pt; height:42pt; border:1.2pt solid #23315e; }}
.corner.tl {{ top:32pt; left:32pt; border-right:0; border-bottom:0; }}
.corner.br {{ bottom:32pt; right:32pt; border-left:0; border-top:0; }}
.sidebar {{ position:absolute; right:0; top:32pt; width:8pt; height:300pt; background:#16171b; }}
.title-block {{ position:absolute; left:30pt; top:310pt; transform:rotate(-45deg); transform-origin:left top; }}
.title-block .kicker {{ font-size:10pt; color:#23315e; letter-spacing:2pt; margin-bottom:8pt; }}
.title-block .title {{ font-family:'Black Han Sans', sans-serif; font-size:66pt; color:#16171b; letter-spacing:-3pt; line-height:0.95; }}
.title-block .rule {{ width:260pt; height:2pt; background:#c73a2b; margin-top:6pt; }}
.title-block .sub {{ margin-top:10pt; font-size:12.5pt; color:#4a4d59; letter-spacing:-0.3pt; }}
.brand {{ position:absolute; right:55pt; bottom:130pt; font-family:'Paperlogy 9 Black', sans-serif; font-size:34pt; color:#16171b; letter-spacing:-1pt; text-align:right; }}
.author {{ position:absolute; right:55pt; bottom:82pt; font-size:14pt; color:#16171b; text-align:right; }}
.author .t {{ font-family:'Paperlogy 9 Black', sans-serif; font-size:15pt; }}
.mathology {{ position:absolute; left:40pt; bottom:40pt; font-size:8.5pt; color:#23315e; letter-spacing:3pt; }}
</style></head><body>
<svg class="bg-svg" viewBox="0 0 595 842" preserveAspectRatio="none">
  <g stroke="#a8adba" stroke-width="1.2" fill="none">
    <circle cx="380" cy="620" r="140"/><line x1="60" y1="720" x2="560" y2="380"/>
    <line x1="0" y1="500" x2="595" y2="500"/><line x1="330" y1="0" x2="330" y2="842"/>
    <path d="M 30 780 Q 300 400 560 780"/><path d="M 50 550 C 200 500, 350 700, 550 620"/>
  </g></svg>
<div class="corner tl"></div><div class="corner br"></div><div class="sidebar"></div>
<div class="title-block">
  <div class="kicker">2 학 기  중 간 대 비</div>
  <div class="title">KERNEL<br>POINT</div>
  <div class="rule"></div>
  <div class="sub">공통수학2_도형의 이동</div>
</div>
<div class="brand">공통수학2</div>
<div class="author">이영우 <span class="t">T</span></div>
<div class="mathology">M A T H O L O G Y  ·  2 0 2 6</div>
</body></html>"""

def html_to_pdf(html):
    with sync_playwright() as p:
        b = p.chromium.launch(); page = b.new_page()
        page.set_content(html, wait_until="networkidle")
        page.wait_for_function("document.fonts.ready")
        out = page.pdf(format="A4", print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"})
        b.close()
    return out

# ── 2. KP 원본 표지 교체
kp = fitz.open(KP_SRC)
kp.delete_page(0)
cover_pdf = fitz.open("pdf", html_to_pdf(COVER_HTML))
kp.insert_pdf(cover_pdf, start_at=0); cover_pdf.close()

# ── 3. KP 페이지 분석: 문제/해설 페이지 매핑 (합본 오프셋 미리 반영)
# 합본 배치: 표지(1) + 목차(2) + KP 표지(3) + KP 본문/해설(4~) + WB
COMBINED_OFFSET = 2  # 표지+목차 = 2p 추가

def get_slot_nums_problem(page):
    nums = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0: continue
        for line in b["lines"]:
            for s in line["spans"]:
                t = s["text"].strip()
                if "Paperlogy-9Black" in s.get("font","") and s["size"] < 20 \
                   and re.fullmatch(r"\d{1,3}", t):
                    nums.append(int(t))
    return nums

sol_start = None
for i in range(kp.page_count):
    if "Solutions" in kp[i].get_text():
        sol_start = i; break

sol_map = {}
if sol_start is not None:
    for i in range(sol_start, kp.page_count):
        txt = kp[i].get_text()
        for m in re.finditer(r"(?<![\d])(\d{1,3})\s*번\b", txt):
            n = int(m.group(1))
            if 1 <= n <= 200 and n not in sol_map:
                sol_map[n] = i + 1 + COMBINED_OFFSET

overlay_count = 0
for pidx in range(kp.page_count):
    if sol_start is not None and pidx >= sol_start: break
    nums = get_slot_nums_problem(kp[pidx])
    slot_nums = [n for n in nums if 1 <= n <= 200]
    if not slot_nums: continue
    first_num = min(slot_nums)
    sol_pg = sol_map.get(first_num)
    if not sol_pg: continue
    page = kp[pidx]
    w, h = page.rect.width, page.rect.height
    text = f"정답  p.{sol_pg}"
    rect = fitz.Rect(w - 90, 26, w - 22, 42)
    page.draw_rect(rect, color=None, fill=(1,1,1), overlay=True)
    try:
        page.insert_text((w - 86, 37), text, fontname="AppleGothic",
                          fontsize=8, color=(0.78, 0.23, 0.17))
    except Exception:
        page.insert_text((w - 86, 37), text, fontsize=8, color=(0.78, 0.23, 0.17))
    overlay_count += 1

if sol_start is not None:
    for pidx in range(sol_start, kp.page_count):
        page = kp[pidx]
        w, h = page.rect.width, page.rect.height
        combined_pg = pidx + 1 + COMBINED_OFFSET
        try:
            page.insert_text((w/2 - 10, h - 22), f"- {combined_pg} -",
                              fontname="helv", fontsize=9, color=(0.3,0.3,0.35))
        except Exception:
            pass
print(f"[OVERLAY] {overlay_count}개 페이지, 해설매핑 {len(sol_map)}개")

# ── 5. 목차 페이지 (표지 다음)
wb_doc = fitz.open(WB_SRC)
wb_sol_kp = 1
for i in range(wb_doc.page_count):
    if "Solutions" in wb_doc[i].get_text() or "정답 및 해설" in wb_doc[i].get_text():
        wb_sol_kp = i + 1; break
wb_total = wb_doc.page_count
kp_total = kp.page_count

kp_first_page_final = 3
kp_sol_page_final = (sol_start + 1) + COMBINED_OFFSET if sol_start is not None else kp_first_page_final
wb_cover_final = COMBINED_OFFSET + kp_total + 1
wb_sol_page_final = wb_cover_final + wb_sol_kp - 1

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
<div class="sub">공통수학2 · 도형의 이동 · KERNEL POINT + WORKBOOK</div>
<hr>
<ul>
  <li><span class="name">KERNEL POINT</span><span class="dot"></span><span class="page">p. {kp_first_page_final}</span></li>
  <li><span class="name">KERNEL POINT · 정답 및 해설</span><span class="dot"></span><span class="page">p. {kp_sol_page_final}</span></li>
  <li><span class="name">WORKBOOK</span><span class="dot"></span><span class="page">p. {wb_cover_final}</span></li>
  <li><span class="name">WORKBOOK · 정답 및 해설</span><span class="dot"></span><span class="page">p. {wb_sol_page_final}</span></li>
</ul>
</body></html>"""

toc_pdf = fitz.open("pdf", html_to_pdf(TOC_HTML))

# ── 6. 합본: KP 표지 + 목차 + KP 본문 (표지 뒤) + WB 전체
final = fitz.open()
final.insert_pdf(kp, from_page=0, to_page=0)
final.insert_pdf(toc_pdf)
final.insert_pdf(kp, from_page=1, to_page=kp.page_count-1)
final.insert_pdf(wb_doc)

final.save(OUT, deflate=True, garbage=4)
final.close(); kp.close(); wb_doc.close(); toc_pdf.close()

subprocess.run(["xattr","-c", OUT])
subprocess.run(["killall","Preview"], stderr=subprocess.DEVNULL)
subprocess.run(["open", OUT])
print(f"[OK] {OUT}")
print(f"    KP 페이지수: {kp_total}, WB: {wb_total}, 해설 매핑: {len(sol_map)}개")
