"""TOP반 추가자료(평면좌표+직선의방정식) 빌드 — KP 스타일 단일 합본, WORKBOOK 없음.

표지만 예외: 하얀 배경 + 심플 타이틀("TOP반 추가자료" / "평면좌표 · 직선의방정식").
나머지 렌더 규칙(폰트·수식·이미지 이관·정답 마커 등)은 project_top_class_textbook.md 그대로.
"""
import sys, os, zipfile, json, base64, re
from collections import Counter
sys.path.insert(0, "/Users/youngwoolee/MathDB/app")
sys.path.insert(0, "/Users/youngwoolee/MathDB/scripts")
from dotenv import load_dotenv; load_dotenv("/Users/youngwoolee/MathDB/.env")
import xml.etree.ElementTree as ET
import importlib
from parse_hwpx import _extract_questions_from_xml
import pdf_engine; importlib.reload(pdf_engine)
import build_pyeongjwapyo_by_difficulty as tpl; importlib.reload(tpl)
from pdf_engine import generate_book_pdf
from PIL import Image as PIL
import fitz

SRC_DIR = "/Users/youngwoolee/Downloads/수업자료/탑반 교재"
FILES = [
    (f"{SRC_DIR}/탑반 평좌 추가자료.hwpx", "평면좌표", "pyj"),
    (f"{SRC_DIR}/탑반 직방 추가자료.hwpx", "직선의 방정식", "jbs"),
]
OUT = f"{SRC_DIR}/TOP반_추가자료_평면좌표+직선의방정식.pdf"

IMG_MARKER = re.compile(r"<<IMG:(image\d+)>>")

rows = []
qidx = 0
for path, chapter_name, tag in FILES:
    z = zipfile.ZipFile(path)
    # 이 스크립트는 section0.xml 하나만 읽음 — "추가자료" 원본 HWPX가 파일당
    # 단원 하나·section 하나 구조라 확인 후 단순화한 것. 여러 section을 가진
    # HWPX(유형별로 나뉜 본편 교재 등)에는 build_dohyeong_v2.py처럼
    # section0~3 순회 로직이 필요함 — 그대로 재사용하면 뒷부분 유실.
    xml_str = z.read("Contents/section0.xml").decode("utf-8", errors="ignore")
    root = ET.fromstring(xml_str)
    qs = _extract_questions_from_xml(root, watermark_images=set(), debug=False)
    for q in qs:
        q["chapter"] = chapter_name
    print(f"[PARSE:{tag}] {chapter_name} {len(qs)}문제")

    # ── 선택지 번호 결번 보정
    gap_fixed = 0
    for q in qs:
        choices = q.get("choices") or []
        if not choices:
            continue
        nums = sorted(c.get("number") for c in choices)
        have = {c.get("number") for c in choices}
        missing = set(range(nums[0], nums[-1] + 1)) - have
        if missing:
            for m in missing:
                choices.append({"number": m, "text": ""})
            choices.sort(key=lambda c: c.get("number"))
            gap_fixed += 1
    if gap_fixed:
        print(f"[CHOICE-GAP:{tag}] 결번 보정: {gap_fixed}문제")

    # ── 그림형 통합 선택지 감지 (같은 이미지가 선택지 3개+ 반복 → 본문 1회로 이관)
    combined_img_fixed = 0
    for q in qs:
        choices = q.get("choices") or []
        if not choices:
            continue
        ref_count = Counter()
        for c in choices:
            for ref in set(IMG_MARKER.findall(c.get("text", "") or "")):
                ref_count[ref] += 1
        combined_ref = next((ref for ref, cnt in ref_count.items() if cnt >= 3), None)
        if not combined_ref:
            continue
        for c in choices:
            c["text"] = IMG_MARKER.sub("", c.get("text", "") or "").strip()
        q["question_text"] = (q.get("question_text", "") or "") + f"<<IMG:{combined_ref}>>"
        combined_img_fixed += 1
    if combined_img_fixed:
        print(f"[COMBINED-IMG:{tag}] 통합 그림 선택지 보정: {combined_img_fixed}문제")

    # ── BinData 이미지 전량 추출 (파일별 독립 디렉터리 — image1.png 등 이름 충돌 방지)
    SRC_IMG = f"/tmp/topban_extra_bin_{tag}"
    os.makedirs(SRC_IMG, exist_ok=True)
    for n in z.namelist():
        if n.startswith("BinData/") and not n.endswith("/"):
            with z.open(n) as f:
                open(f"{SRC_IMG}/{os.path.basename(n)}", "wb").write(f.read())
    z.close()

    SMALL_DIR = f"/tmp/topban_extra_small_{tag}"
    os.makedirs(SMALL_DIR, exist_ok=True)

    referenced = set()
    for q in qs:
        for src in (q.get("question_text", ""), q.get("solution_text", "")):
            referenced.update(IMG_MARKER.findall(src or ""))
        for c in (q.get("choices") or []):
            referenced.update(IMG_MARKER.findall(c.get("text", "") or ""))

    ref_count2 = Counter()
    for q in qs:
        seen = set()
        for src in (q.get("question_text", ""), q.get("solution_text", "")):
            seen.update(IMG_MARKER.findall(src or ""))
        for c in (q.get("choices") or []):
            seen.update(IMG_MARKER.findall(c.get("text", "") or ""))
        for n in seen:
            ref_count2[n] += 1
    BADGES = set(n for n, c in ref_count2.items() if c >= 2)  # 2문제+ 반복 = 배지(다른풀이 등)
    for name in referenced:
        p = f"{SRC_IMG}/{name}.bmp"
        if not os.path.exists(p):
            for ext in (".png", ".jpg", ".jpeg"):
                if os.path.exists(f"{SRC_IMG}/{name}{ext}"):
                    p = f"{SRC_IMG}/{name}{ext}"; break
            else:
                continue
        try:
            img = PIL.open(p); w, h = img.size
            if h > 0 and (w / h > 2.0) and h < 200:
                BADGES.add(name)
            elif w < 150 and h < 150:
                BADGES.add(name)
        except Exception:
            pass

    IMG_URL = {}
    for name in referenced:
        if name in BADGES:
            continue
        src = None
        for ext in (".bmp", ".png", ".jpg", ".jpeg"):
            cand = f"{SRC_IMG}/{name}{ext}"
            if os.path.exists(cand):
                src = cand; break
        if not src:
            continue
        dst = f"{SMALL_DIR}/{name}.jpg"
        if not os.path.exists(dst):
            try:
                img = PIL.open(src).convert("RGB")
                if img.width > 800:
                    r = 800 / img.width
                    img = img.resize((800, int(img.height * r)))
                img.save(dst, "JPEG", quality=85)
            except Exception as e:
                print(f"[WARN:{tag}] {name}: {e}"); continue
        with open(dst, "rb") as f:
            IMG_URL[name] = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"

    print(f"[IMG:{tag}] 참조={len(referenced)} 배지={len(BADGES)} 이관={len(IMG_URL)}")

    for q in qs:
        qidx += 1
        qt = q.get("question_text", "") or ""
        st = q.get("solution_text", "") or ""
        for k in BADGES:
            qt = qt.replace(f"<<IMG:{k}>>", "")
            st = st.replace(f"<<IMG:{k}>>", "")
        used = set(IMG_MARKER.findall(qt) + IMG_MARKER.findall(st))
        for c in (q.get("choices") or []):
            used.update(IMG_MARKER.findall(c.get("text", "") or ""))
        q_imgs = {name: IMG_URL[name] for name in used if name in IMG_URL}
        new_choices = []
        for c in (q.get("choices") or []):
            t = c.get("text", "") or ""
            for k in BADGES:
                t = t.replace(f"<<IMG:{k}>>", "")
            new_choices.append({**c, "text": t})
        rows.append({
            "question_id": qidx,
            "question_text": tpl.typeset_body(qt),
            "solution_text": st,
            "answer": q.get("answer", ""),
            "choices": json.dumps(new_choices, ensure_ascii=False),
            "chapter": chapter_name,
            "difficulty": "", "school": "", "year": None,
            "semester": "", "exam_type": "",
            "question_number": qidx,
            "has_image": bool(q_imgs),
            "images": q_imgs,
        })

print(f"[BUILD] 총 {len(rows)}문제")

# ── 크롬 폰트 CSS (탑반 표준) + 표지 전용 심플 오버라이드
paper_black = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/Paperlogy-9Black.ttf"), "rb").read()).decode()
paper_eb = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/Paperlogy-8ExtraBold.ttf"), "rb").read()).decode()
hcr = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/HANBatang.ttf"), "rb").read()).decode()
CROME_CSS = f"""
@font-face {{ font-family: 'Paperlogy 9 Black'; src: url(data:font/ttf;base64,{paper_black}) format('truetype'); }}
@font-face {{ font-family: 'Paperlogy 8 ExtraBold'; src: url(data:font/ttf;base64,{paper_eb}) format('truetype'); }}
@font-face {{ font-family: 'HCR Batang'; src: url(data:font/ttf;base64,{hcr}) format('truetype'); }}
.bp-head-left, .bp-head-right, .bp-head-right .roman,
.bp-side-part, .bp-side-letter, .bp-side-roman, .bp-side-vertical,
.kp-source, .kp-checks, .cb, .kp-label, .kp-line, .kp-memo-label,
.cd-chapter-label, .cd-meta-top,
.cd-section-label, .cd-footer-title, .cd-footer-sub {{ font-family: 'Paperlogy 8 ExtraBold', sans-serif !important; }}
.cd-big-num, .cd-major-roman, .kp-num, .cd-major, .cd-section-title {{ font-family: 'Paperlogy 9 Black', sans-serif !important; }}
.slot.book-kp .q-body {{ text-align:left !important; word-break:keep-all !important; overflow-wrap:break-word !important;
  font-family: 'HCR Batang', serif !important; font-size: 10pt !important; line-height: 1.55 !important; }}
.slot.book-kp .q-choices .choice {{ font-family: 'HCR Batang', serif !important; font-size: 10pt !important; }}
.slot.book-kp .katex, .katex {{ font-size: 11pt !important; }}
.q-body .katex {{ white-space: nowrap; }}
/* 표지만 심플 하얀배경 + 타이틀만 (킥커·빅워드·강사박스·푸터·코너브라켓 전부 제거) */
.book-cover .bc-tl, .book-cover .bc-tr, .book-cover .bc-bl, .book-cover .bc-br,
.book-cover .bc-kicker, .book-cover .bc-kicker-rule,
.book-cover .bc-title-big, .book-cover .bc-big-rule,
.book-cover .bc-instructor, .book-cover .bc-footer {{ display: none !important; }}
.book-cover {{ background:#ffffff !important; display:flex !important; flex-direction:column !important;
  align-items:center !important; justify-content:center !important; }}
.book-cover .bc-title-main {{ margin-top:0 !important; font-size:46pt !important; }}
.book-cover .bc-title-mid {{ margin-top:14mm !important; font-size:19pt !important; letter-spacing:1.5pt !important; color:#334155 !important; }}
"""

overrides = {r["question_id"]: "full" for r in rows}
pdf_bytes = generate_book_pdf(
    rows, title="TOP반 추가자료", subtitle="평면좌표 · 직선의방정식",
    include_source=False, overrides=overrides, logo_path=None,
    kicker_mark=None, kicker_text=None,
    divider_meta_top="공통수학2 · 도형의 방정식 · TOP반 추가자료",
    divider_footer_title="공통수학2 · TOP반 추가자료",
    divider_footer_sub="이영우 T",
    cover_style="final",
    cover_main_title="TOP반 추가자료",
    cover_tagline="평면좌표 · 직선의방정식",
    cover_kicker="", cover_big_word="",
    cover_footer_main="", cover_footer_sub="",
    page_running_left="공통수학2 · TOP반 추가자료",
    extra_css=CROME_CSS, extra_js=tpl.TYPESET_JS,
    running_numbering=True,
)
TMP_PDF = "/tmp/topban_extra_raw.pdf"
open(TMP_PDF, "wb").write(pdf_bytes)
print(f"[OK] 원본 PDF: {len(rows)}문제 → {TMP_PDF}")

# ── 정답 갈피(정답 p.N) + 해설 페이지 번호 오버레이 (표지가 이미 이 PDF 안에 있으므로 오프셋 0)
doc = fitz.open(TMP_PDF)

sol_start = None
for i in range(doc.page_count):
    if "Solutions" in doc[i].get_text():
        sol_start = i; break

def get_slot_nums_problem(page):
    nums = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for line in b["lines"]:
            for s in line["spans"]:
                t = s["text"].strip()
                if "Paperlogy-9Black" in s.get("font", "") and s["size"] < 20 \
                   and re.fullmatch(r"\d{1,3}", t):
                    nums.append(int(t))
    return nums

sol_map = {}
if sol_start is not None:
    for i in range(sol_start, doc.page_count):
        txt = doc[i].get_text()
        for m in re.finditer(r"(?<![\d])(\d{1,3})\s*번\b", txt):
            n = int(m.group(1))
            if 1 <= n <= 200 and n not in sol_map:
                sol_map[n] = i + 1

overlay_count = 0
for pidx in range(doc.page_count):
    if sol_start is not None and pidx >= sol_start:
        break
    nums = get_slot_nums_problem(doc[pidx])
    slot_nums = [n for n in nums if 1 <= n <= 200]
    if not slot_nums:
        continue
    first_num = min(slot_nums)
    sol_pg = sol_map.get(first_num)
    if not sol_pg:
        continue
    page = doc[pidx]
    w, h = page.rect.width, page.rect.height
    text = f"정답  p.{sol_pg}"
    rect = fitz.Rect(w - 90, 26, w - 22, 42)
    page.draw_rect(rect, color=None, fill=(1, 1, 1), overlay=True)
    try:
        page.insert_text((w - 86, 37), text, fontname="AppleGothic", fontsize=8, color=(0.78, 0.23, 0.17))
    except Exception:
        page.insert_text((w - 86, 37), text, fontsize=8, color=(0.78, 0.23, 0.17))
    overlay_count += 1

if sol_start is not None:
    for pidx in range(sol_start, doc.page_count):
        page = doc[pidx]
        w, h = page.rect.width, page.rect.height
        try:
            page.insert_text((w / 2 - 10, h - 22), f"- {pidx + 1} -", fontname="helv", fontsize=9, color=(0.3, 0.3, 0.35))
        except Exception:
            pass

print(f"[OVERLAY] {overlay_count}개 페이지, 해설매핑 {len(sol_map)}개")

doc.save(OUT, deflate=True, garbage=4)
doc.close()

os.system(f"xattr -c '{OUT}'")
print(f"[DONE] {OUT}  (총 {qidx}문제)")
