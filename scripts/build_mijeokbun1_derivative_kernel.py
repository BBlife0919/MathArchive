"""미적분1 KERNEL POINT — 함수의 극한~함수의 극대극소와 그래프 (마플시너지 5파일 합본).

소스: 마플시너지-수학2-0{1..5}.*.hwpx (사용자 다운로드 폴더, 유형서 — 파일명의 "수학2"는
발행사 자체 시리즈 번호일 뿐 과목명이 아님. 실제 과목은 미적분1. [정답]기준
문항분리는 기출 파서와 동일 구조라 parse_hwpx._extract_questions_from_xml 재사용).
"유형 NN 제목" 라벨은 파일 안에 결번(빈 제목 스텁)이 많아 실제 제목 있는 유형만
추출 후 5개 파일 전체에서 등장순으로 1부터 통연번(사용자 지시: "유형 넘버만 땡겨줘"
+ "문항번호도 이어붙여서 1번부터 쭉").

표지/CSS/빠른정답/해설 파이프라인은 scripts/top_class_reference/build_topban_kp_workbook.py
(기준완성본 "공수2 평면좌표_KERNEL+WORKBOOK_합본.pdf"를 만든 스크립트)의 KP 절반을 그대로 재사용.

구조 (2026-09-10 재작업): 5개 챕터를 개별 generate_book_pdf() 호출 후 이어붙이던 방식은
"문제-해설-문제-해설"이 챕터마다 반복돼 사용자가 반려 — 전체 362문제를 ONE
generate_book_pdf() 호출로 합쳐서 표지→(5개 대단원 디바이더+유형 소단원 디바이더+문제,
통번호)→빠른정답(1개, 전체)→해설(1개, 전체) 구조로 변경. 대단원 그루핑은
pdf_engine._minor_to_major 를 몽키패치해서 "유형 NN · 제목"(minor) → 실제 5개 단원명
(major) 역매핑 테이블로 해결(major_hint 는 단일 문자열이라 여러 대단원 동시 처리 불가).
"""
import sys, os, zipfile, json, base64, re
from collections import Counter
sys.path.insert(0, "/Users/youngwoolee/MathDB/app")
sys.path.insert(0, "/Users/youngwoolee/MathDB/scripts")
import xml.etree.ElementTree as ET
from parse_hwpx import _extract_questions_from_xml
import build_pyeongjwapyo_by_difficulty as tpl
import pdf_engine
from pdf_engine import generate_book_pdf
from PIL import Image as PIL
import fitz
from playwright.sync_api import sync_playwright

SRC_DIR = "/Users/youngwoolee/Downloads"
OUT_DIR = "/Users/youngwoolee/클로드교재/04_미적분1"
OUT_PATH = f"{OUT_DIR}/미적분1_함수의극한_미분_KERNEL_POINT.pdf"
CW, CH = 595.9199, 842.8800

CHAPTERS = [
    {"tag": "gukhan", "hwpx": f"{SRC_DIR}/마플시너지-수학2-01.함수의 극한.hwpx",
     "chapter": "함수의 극한"},
    {"tag": "yeonsok", "hwpx": f"{SRC_DIR}/마플시너지-수학2-02.함수의 연속.hwpx",
     "chapter": "함수의 연속"},
    {"tag": "mibungyesu", "hwpx": f"{SRC_DIR}/마플시너지-수학2-03.미분계수와 도함수.hwpx",
     "chapter": "미분계수와 도함수"},
    {"tag": "jeopseon", "hwpx": f"{SRC_DIR}/마플시너지-수학2-04.접선의 방정식.hwpx",
     "chapter": "접선의 방정식"},
    {"tag": "geukdae", "hwpx": f"{SRC_DIR}/마플시너지-수학2-05.함수의 극대 극소와 그래프.hwpx",
     "chapter": "함수의 극대 극소와 그래프"},
]

IMG_MARKER = re.compile(r"<<IMG:(image\d+)>>")
TYPE_HEAD = re.compile(r"^유형\s*(\d+)\s+(.+)$")

paper_black = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/Paperlogy-9Black.ttf"), "rb").read()).decode()
paper_eb = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/Paperlogy-8ExtraBold.ttf"), "rb").read()).decode()
hcr = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/HANBatang.ttf"), "rb").read()).decode()
eum_logo = base64.b64encode(open("/Users/youngwoolee/MathDB/app/assets/eum_logo.png", "rb").read()).decode()

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
/* 빠른정답 표 압축 (362문제라 기본 크기면 여러 페이지 잡아먹음, 2026-09-10 사용자 요청) */
.quick-answers td {{ padding: 1.3mm 1mm !important; }}
.quick-answers {{ font-size: 8.5pt !important; }}
.quick-answers td.qa-num {{ font-weight: 700 !important; }}
"""


def parse_types_section(texts, start_num):
    """유형 헤더(제목 있는 것만) → 전체 파일 통틀어 등장순으로 start_num부터 통연번.

    반환: (qnum(1부터, "정답" 등장 순서) -> (새 유형번호, 제목) 딕셔너리, 이 파일에서
    쓴 유형 개수, 다음 파일이 이어 쓸 start_num)
    """
    real_types = []  # [(orig_num, title)] 등장 순
    seen_orig = set()
    for t in texts:
        m = TYPE_HEAD.match(t.strip())
        if not m:
            continue
        title = m.group(2).strip()
        if not title:
            continue  # 빈 제목 스텁 — 실제 유형 아님
        orig = int(m.group(1))
        key = (orig, title)
        if key in seen_orig:
            continue
        seen_orig.add(key)
        real_types.append((orig, title))

    renum = {orig_title: start_num + i for i, orig_title in enumerate(real_types)}

    q_to_type = {}
    qnum, current = 0, None
    for t in texts:
        s = t.strip()
        m = TYPE_HEAD.match(s)
        if m:
            title = m.group(2).strip()
            if title:
                current = (renum[(int(m.group(1)), title)], title)
            continue
        if "정답" in s:
            qnum += 1
            if current:
                q_to_type[qnum] = current
    return q_to_type, len(real_types)


def extract_chapter_rows(cfg, type_offset):
    """한 hwpx 파일 → (rows, 이 파일이 쓴 유형 개수). chapter 필드는 전역 유형번호로 부여."""
    z = zipfile.ZipFile(cfg["hwpx"])
    xml_str = z.read("Contents/section0.xml").decode("utf-8", errors="ignore")
    root = ET.fromstring(xml_str)
    rows = _extract_questions_from_xml(root, watermark_images=set(), debug=False)

    texts = re.findall(r"<hp:t>([^<]*)</hp:t>", xml_str)
    q_to_type, n_types = parse_types_section(texts, type_offset)
    for idx, q in enumerate(rows, 1):
        tp = q_to_type.get(idx)
        q['chapter'] = f"유형 {tp[0]:02d} · {tp[1]}" if tp else "유형 기타"
        q['_major'] = cfg["chapter"]
    print(f"[PARSE:{cfg['tag']}] {cfg['chapter']}: 유형 {n_types}개(전역 {type_offset:02d}~{type_offset+n_types-1:02d}), 문제 {len(rows)}개")

    # 원본 소스 자체의 중괄호 구조 오류 2건(미분계수와 도함수, "{ \left\{...} \right\}"
    # 형태로 바깥 여분 중괄호가 \left\{/\right\} 짝을 깨서 KaTeX 파싱 실패).
    # 범용 정규식 보정은 다른 정상 수식까지 오폭(2026-09-09 확인)해서 위험 —
    # 이 2건만 정확히 특정해서 바깥 여분 중괄호를 제거.
    _KNOWN_BRACE_FIXES = [
        (r"{ \left\{ \dfrac{ f(x)-f(2)}{ x-2} \times \dfrac{ 1}{ x+2} } \right\}",
         r"\left\{ \dfrac{ f(x)-f(2)}{ x-2} \times \dfrac{ 1}{ x+2} \right\}"),
        (r"{\left\{ \dfrac{ g(x)-g(2)}{ x-2} \times \dfrac{ 1}{x^2 +2x+4 } }\right\}",
         r"\left\{ \dfrac{ g(x)-g(2)}{ x-2} \times \dfrac{ 1}{x^2 +2x+4 } \right\}"),
    ]
    for q in rows:
        st = q.get('solution_text') or ''
        for bad, good in _KNOWN_BRACE_FIXES:
            if bad in st:
                st = st.replace(bad, good)
        q['solution_text'] = st

    # 선택지 번호 결번 보정
    for q in rows:
        choices = q.get('choices') or []
        if not choices:
            continue
        nums = sorted(c.get('number') for c in choices)
        have = {c.get('number') for c in choices}
        missing = set(range(nums[0], nums[-1] + 1)) - have
        if missing:
            for m in missing:
                choices.append({'number': m, 'text': ''})
            choices.sort(key=lambda c: c.get('number'))

    # BinData 이미지 전량 추출
    SRC_IMG = f"/tmp/mijeokbun1_kp_bin_{cfg['tag']}"
    os.makedirs(SRC_IMG, exist_ok=True)
    for n in z.namelist():
        if n.startswith("BinData/") and not n.endswith("/"):
            with z.open(n) as f:
                open(f"{SRC_IMG}/{os.path.basename(n)}", "wb").write(f.read())
    z.close()

    SMALL_DIR = f"/tmp/mijeokbun1_kp_small_{cfg['tag']}"
    os.makedirs(SMALL_DIR, exist_ok=True)

    referenced = set()
    for q in rows:
        for src in (q.get('question_text', ''), q.get('solution_text', '')):
            referenced.update(IMG_MARKER.findall(src or ''))
        for c in (q.get('choices') or []):
            referenced.update(IMG_MARKER.findall(c.get('text', '') or ''))

    ref_count = Counter()
    for q in rows:
        seen = set()
        for src in (q.get('question_text', ''), q.get('solution_text', '')):
            seen.update(IMG_MARKER.findall(src or ''))
        for c in (q.get('choices') or []):
            seen.update(IMG_MARKER.findall(c.get('text', '') or ''))
        for n in seen:
            ref_count[n] += 1
    BADGES = set(n for n, c in ref_count.items() if c >= 2)
    for name in referenced:
        p = f"{SRC_IMG}/{name}.bmp"
        if not os.path.exists(p):
            for ext in (".png", ".jpg", ".jpeg"):
                if os.path.exists(f"{SRC_IMG}/{name}{ext}"):
                    p = f"{SRC_IMG}/{name}{ext}"
                    break
            else:
                continue
        try:
            img = PIL.open(p)
            w, h = img.size
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
                src = cand
                break
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
                print(f"[WARN:{cfg['tag']}] {name}: {e}")
                continue
        with open(dst, "rb") as f:
            IMG_URL[name] = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
    print(f"[IMG:{cfg['tag']}] 참조={len(referenced)} 배지={len(BADGES)} 이관={len(IMG_URL)}")

    out_rows = []
    for q in rows:
        qt = q.get('question_text', '') or ''
        st = q.get('solution_text', '') or ''
        for k in BADGES:
            qt = qt.replace(f"<<IMG:{k}>>", "")
            st = st.replace(f"<<IMG:{k}>>", "")
        used = set(IMG_MARKER.findall(qt) + IMG_MARKER.findall(st))
        for c in (q.get('choices') or []):
            used.update(IMG_MARKER.findall(c.get('text', '') or ''))
        q_imgs = {name: IMG_URL[name] for name in used if name in IMG_URL}
        new_choices = []
        for c in (q.get('choices') or []):
            t = c.get('text', '') or ''
            for k in BADGES:
                t = t.replace(f"<<IMG:{k}>>", "")
            new_choices.append({**c, 'text': t})
        out_rows.append({
            'question_text': tpl.typeset_body(qt),
            'solution_text': st,
            'answer': q.get('answer', ''),
            'choices': json.dumps(new_choices, ensure_ascii=False),
            'chapter': q.get('chapter', '기타'),
            '_major': q['_major'],
            'difficulty': '', 'school': '', 'year': None,
            'semester': '', 'exam_type': '',
            'has_image': bool(q_imgs),
            'images': q_imgs,
        })
    return out_rows, n_types


def html_to_pdf(html):
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        page.set_content(html, wait_until="networkidle")
        page.wait_for_function("document.fonts.ready")
        out = page.pdf(format="A4", print_background=True,
                        margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    return out


def cover_html():
    return f"""<!DOCTYPE html><html><head>
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
.title-block {{ position:absolute; left:30pt; top:300pt; transform:rotate(-45deg); transform-origin:left top; }}
.title-block .kicker {{ font-size:10pt; color:#23315e; letter-spacing:2pt; margin-bottom:8pt; }}
.title-block .title {{ font-family:'Black Han Sans', sans-serif; font-size:66pt; color:#16171b; letter-spacing:-3pt; line-height:0.95; }}
.title-block .rule {{ width:260pt; height:2pt; background:#c73a2b; margin-top:6pt; }}
.title-block .sub {{ margin-top:10pt; font-size:12pt; color:#4a4d59; letter-spacing:-0.3pt; }}
.brand {{ position:absolute; right:55pt; bottom:130pt; font-family:'Paperlogy 9 Black', sans-serif; font-size:30pt; color:#16171b; letter-spacing:-1pt; text-align:right; }}
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
  <div class="kicker">핵 심 유 형  총 정 리</div>
  <div class="title">KERNEL<br>POINT</div>
  <div class="rule"></div>
  <div class="sub">미적분1_함수의 극한과 미분</div>
</div>
<div class="brand">미적분1</div>
<div class="author">이영우 <span class="t">T</span></div>
<div class="mathology">M A T H O L O G Y  ·  2 0 2 6</div>
</body></html>"""


def toc_html(entries):
    rows = "".join(
        f'<li><span class="name">{e["name"]}</span><span class="dot"></span><span class="page">p. {e["page"]}</span></li>'
        for e in entries
    )
    return f"""<!DOCTYPE html><html><head><style>
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
<div class="sub">미적분1 · 함수의 극한과 미분 · KERNEL POINT</div>
<hr>
<ul>{rows}</ul>
</body></html>"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    all_rows = []
    minor_to_major = {}
    type_offset = 1
    total_types = 0
    for cfg in CHAPTERS:
        rows, n_types = extract_chapter_rows(cfg, type_offset)
        for q in rows:
            minor_to_major[q['chapter']] = q['_major']
        all_rows.extend(rows)
        type_offset += n_types
        total_types += n_types

    for i, q in enumerate(all_rows, 1):
        q['question_id'] = i
        q['question_number'] = i
    print(f"\n[MERGE] 총 유형 {total_types}개, 총 문제 {len(all_rows)}개 — 1번부터 통번호 부여 완료")

    # major_hint 는 문자열 하나만 받아서 5개 대단원을 동시에 못 살림 — 실제 대단원
    # 역매핑 테이블로 _minor_to_major 를 몽키패치(이 프로세스 안에서만 유효).
    _orig_minor_to_major = pdf_engine._minor_to_major
    def _patched_minor_to_major(chapter):
        return minor_to_major.get(chapter) or _orig_minor_to_major(chapter)
    pdf_engine._minor_to_major = _patched_minor_to_major

    overrides = {r['question_id']: 'full' for r in all_rows}
    pdf_bytes = generate_book_pdf(
        all_rows, title="미적분1 함수의 극한과 미분", subtitle="미적분1 KERNEL POINT",
        include_source=False, overrides=overrides, logo_path=None,
        kicker_mark=None, kicker_text=None,
        divider_meta_top="미적분1 · KERNEL POINT",
        divider_footer_title="미적분1 · 함수의 극한과 미분 · KERNEL POINT",
        divider_footer_sub="이영우 T",
        cover_main_title="핵심유형 총정리", cover_tagline="미적분1 함수의 극한과 미분",
        cover_big_word="KERNEL POINT", cover_kicker="MATHOLOGY · 2026",
        cover_footer_main="MATHOLOGY · 2026",
        cover_footer_sub="미적분1 · 함수의 극한과 미분 · KERNEL POINT",
        page_running_left="미적분1 KERNEL POINT",
        extra_css=CROME_CSS, extra_js=tpl.TYPESET_JS,
        running_numbering=True, major_hint=None,
        qa_cols=10,
    )
    pdf_engine._minor_to_major = _orig_minor_to_major  # 원복

    body_path = "/tmp/mijeokbun1_kp_body.pdf"
    open(body_path, "wb").write(pdf_bytes)

    body = fitz.open(body_path)
    body.delete_page(0)  # generate_book_pdf 자체 표지 제거(내 커스텀 표지로 교체)

    # 대단원(CHAPTER · 0N) 전환 지점을 실제 렌더 결과에서 스캔해 TOC 페이지번호 확정.
    chapter_first_page = {}
    for i in range(body.page_count):
        # letter-spacing CSS 탓에 "C H A P T E R  ·  0 1"처럼 글자마다 공백이 끼어
        # 나온다 — 공백 다 지우고 매칭(2026-09-10 실측 확인).
        txt_nospace = re.sub(r"\s+", "", body[i].get_text())
        m = re.search(r"CHAPTER·0?(\d+)", txt_nospace)
        if m:
            n = int(m.group(1))
            if n not in chapter_first_page:
                chapter_first_page[n] = i  # 0-indexed, body 기준(표지 제거 후)

    FRONT_OFFSET = 2  # 커스텀 표지(1) + 목차(1)
    entries = [
        {"name": cfg["chapter"], "page": chapter_first_page[i + 1] + 1 + FRONT_OFFSET}
        for i, cfg in enumerate(CHAPTERS) if (i + 1) in chapter_first_page
    ]

    final = fitz.open()
    cover_pdf = fitz.open("pdf", html_to_pdf(cover_html()))
    final.insert_pdf(cover_pdf, start_at=0)
    cover_pdf.close()

    toc_pdf = fitz.open("pdf", html_to_pdf(toc_html(entries)))
    final.insert_pdf(toc_pdf)
    toc_pdf.close()

    final.insert_pdf(body)
    body.close()

    final.save(OUT_PATH, deflate=True, garbage=4)
    final.close()
    os.system(f"xattr -c '{OUT_PATH}'")
    print(f"\n[DONE] {OUT_PATH}")
    print(f"  총 유형 {total_types}개, 총 문제 {len(all_rows)}개, 총 {sum(1 for _ in fitz.open(OUT_PATH))}페이지")
    for e in entries:
        print(f"   - {e['name']}: p.{e['page']}")


if __name__ == "__main__":
    main()
