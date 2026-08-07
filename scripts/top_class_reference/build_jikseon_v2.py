"""직선의 방정식 KP 재빌드 v2 — 통번호·전량 이미지 이관·정답 마커 정확도."""
import sys, os, zipfile, json, base64, glob, importlib, re, io
sys.path.insert(0, "/Users/youngwoolee/MathDB/app")
sys.path.insert(0, "/Users/youngwoolee/MathDB/scripts")
from dotenv import load_dotenv; load_dotenv("/Users/youngwoolee/MathDB/.env")
import xml.etree.ElementTree as ET
from parse_hwpx import _extract_questions_from_xml
import pdf_engine; importlib.reload(pdf_engine)
import build_pyeongjwapyo_by_difficulty as tpl; importlib.reload(tpl)
from pdf_engine import generate_book_pdf
from PIL import Image as PIL

HWPX = "/Users/youngwoolee/Downloads/수업자료/탑반 교재/직선의 방정식.hwpx"
OUT_DIR = "/Users/youngwoolee/Downloads/수업자료/탑반 교재"
KP_PDF = "/tmp/jikseon_kernel_v2.pdf"
COMBINED = f"{OUT_DIR}/직선의방정식_KERNEL+WORKBOOK_합본.pdf"

# ── 1. HWPX 파싱: 4개 section + 챕터 태깅
z = zipfile.ZipFile(HWPX)

def parse_types_section(texts):
    q_to_type = {}
    i, qnum, current = 0, 0, None
    while i < len(texts):
        t = texts[i].strip()
        if re.match(r"^\d{2}$", t) and i+1 < len(texts):
            nxt = texts[i+1].strip()
            if nxt and any('가' <= c <= '힣' for c in nxt) and len(nxt) > 4 and "정답" not in nxt:
                current = (t, nxt); i += 2; continue
        if "정답" in t:
            qnum += 1
            if current: q_to_type[qnum] = current
        i += 1
    return q_to_type

all_rows = []
for sec_no in range(4):
    name = f"Contents/section{sec_no}.xml"
    if name not in z.namelist(): continue
    xml_str = z.read(name).decode("utf-8", errors="ignore")
    try: root = ET.fromstring(xml_str)
    except: continue
    r = _extract_questions_from_xml(root, watermark_images=set(), debug=False)
    if not r: continue
    if sec_no == 0:
        texts = re.findall(r"<hp:t>([^<]*)</hp:t>", xml_str)
        q_to_type = parse_types_section(texts)
        for idx, q in enumerate(r, 1):
            tp = q_to_type.get(idx)
            q['chapter'] = f"유형 {tp[0]} · {tp[1]}" if tp else "유형 기타"
    elif sec_no == 1:
        for q in r: q['chapter'] = "고난도정복"
    elif sec_no == 2:
        # 종합 실전 별도 유형 X → 고난도정복에 통합
        for q in r: q['chapter'] = "고난도정복"
    all_rows.extend(r)

# ── 2. HWPX BinData 이미지 전량 추출 → JPG 변환 → base64
BIN_DIR = "/tmp/jikseon_bin_v2"
os.makedirs(BIN_DIR, exist_ok=True)
for n in z.namelist():
    if n.startswith("BinData/") and not n.endswith("/"):
        with z.open(n) as f:
            open(f"{BIN_DIR}/{os.path.basename(n)}", "wb").write(f.read())
z.close()

# HWPX 안 hp:pic 참조 매핑 (imageN → BinData 파일명) 필요.
# parse_hwpx 가 이미 <<IMG:imageN>> 삽입할 때 순서대로 매김. 실제 매핑은 header.xml/content 안 relIDs.
# 간단화: /tmp/jikseon_images (기존) 을 그대로 재활용 — 이미 imageN.bmp 로 저장됨.
SRC_IMG = "/tmp/jikseon_images"
SMALL_DIR = "/tmp/jikseon_images_small_v2"
os.makedirs(SMALL_DIR, exist_ok=True)

# 모든 참조된 이미지 이름 수집 (본문 + 선지)
referenced = set()
IMG_MARKER = re.compile(r"<<IMG:(image\d+)>>")
for q in all_rows:
    for src in (q.get('question_text',''), q.get('solution_text','')):
        referenced.update(IMG_MARKER.findall(src or ''))
    for c in (q.get('choices') or []):
        referenced.update(IMG_MARKER.findall(c.get('text','') or ''))

# 배지 판정: 여러 문제에서 반복 참조되면 배지 (아이콘/워터마크). aspect·크기 병용.
from collections import Counter
ref_count = Counter()
for q in all_rows:
    seen = set()
    for src in (q.get('question_text',''), q.get('solution_text','')):
        seen.update(IMG_MARKER.findall(src or ''))
    for c in (q.get('choices') or []):
        seen.update(IMG_MARKER.findall(c.get('text','') or ''))
    for n in seen: ref_count[n] += 1

BADGES = set(n for n, c in ref_count.items() if c >= 2)  # 2문제+ 반복 = 배지(다른풀이·대표문제)
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
        # 다른풀이 배지 (오렌지 손글씨) = 대략 272x120 aspect 2.27
        if h > 0 and (w/h > 2.0) and h < 200:
            BADGES.add(name)
        elif w < 150 and h < 150:
            BADGES.add(name)
    except: pass

# 배지 아닌 것 전부 JPG 변환 → base64 (Playwright 는 BMP 불가)
IMG_URL = {}
for name in referenced:
    if name in BADGES: continue
    src = None
    for ext in (".bmp", ".png", ".jpg", ".jpeg"):
        cand = f"{SRC_IMG}/{name}{ext}"
        if os.path.exists(cand): src = cand; break
    if not src: continue
    dst = f"{SMALL_DIR}/{name}.jpg"
    if not os.path.exists(dst):
        try:
            img = PIL.open(src).convert("RGB")
            # 폭 800 초과면 축소 (Playwright 메모리 절약)
            if img.width > 800:
                r = 800 / img.width
                img = img.resize((800, int(img.height * r)))
            img.save(dst, "JPEG", quality=85)
        except Exception as e:
            print(f"[WARN] {name}: {e}"); continue
    with open(dst, "rb") as f:
        IMG_URL[name] = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"

print(f"[IMG] 참조={len(referenced)} 배지={len(BADGES)} 이관={len(IMG_URL)}")

# ── 3. rows 구성: 문항번호 통번호, 본문·선지 이미지 dict 부착
rows = []
for i, q in enumerate(all_rows, 1):
    qt = q.get('question_text','') or ''
    st = q.get('solution_text','') or ''
    for k in BADGES:
        qt = qt.replace(f"<<IMG:{k}>>", "")
        st = st.replace(f"<<IMG:{k}>>", "")
    # 이 문항 전체 (본문+선지) 참조 이미지
    used = set(IMG_MARKER.findall(qt) + IMG_MARKER.findall(st))
    for c in (q.get('choices') or []):
        used.update(IMG_MARKER.findall(c.get('text','') or ''))
    q_imgs = {name: IMG_URL[name] for name in used if name in IMG_URL}
    # 선지 도 배지 제거
    new_choices = []
    for c in (q.get('choices') or []):
        t = c.get('text','') or ''
        for k in BADGES:
            t = t.replace(f"<<IMG:{k}>>", "")
        new_choices.append({**c, 'text': t})
    rows.append({
        'question_id': i,
        'question_text': tpl.typeset_body(qt),
        'solution_text': st,
        'answer': q.get('answer',''),
        'choices': json.dumps(new_choices, ensure_ascii=False),
        'chapter': q.get('chapter','기타'),
        'difficulty': '', 'school': '', 'year': None,
        'semester': '', 'exam_type': '',
        'question_number': i,
        'has_image': bool(q_imgs),
        'images': q_imgs,
    })

# ── 4. 크롬 폰트 CSS + 통번호 KP 빌드
paper_black = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/Paperlogy-9Black.ttf"),"rb").read()).decode()
paper_eb = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/Paperlogy-8ExtraBold.ttf"),"rb").read()).decode()
hcr = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/HANBatang.ttf"),"rb").read()).decode()
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
"""

overrides = {r['question_id']:'full' for r in rows}
pdf_bytes = generate_book_pdf(
    rows, title="직선의 방정식", subtitle="공통수학2 KERNEL POINT",
    include_source=False, overrides=overrides, logo_path=None,
    kicker_mark=None, kicker_text=None,
    divider_meta_top="공통수학2 · 직선의 방정식 · KERNEL POINT",
    divider_footer_title="공통수학2 · 직선의 방정식 · KERNEL POINT",
    divider_footer_sub="이영우 T",
    cover_main_title="2학기 중간대비", cover_tagline="공통수학2 직선의 방정식",
    cover_big_word="KERNEL POINT", cover_kicker="MATHOLOGY · 2026",
    cover_footer_main="MATHOLOGY · 2026",
    cover_footer_sub="공통수학2 · 직선의 방정식 · KERNEL POINT",
    page_running_left="공통수학2 직선의 방정식 · KERNEL POINT",
    extra_css=CROME_CSS, extra_js=tpl.TYPESET_JS,
    running_numbering=True,
)
open(KP_PDF, "wb").write(pdf_bytes)
print(f"[OK] KP: {len(rows)}문제 → {KP_PDF}")
