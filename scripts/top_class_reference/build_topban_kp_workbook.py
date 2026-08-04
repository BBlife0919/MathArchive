"""탑반 교재 KP+WORKBOOK 표준 합본 빌더 (올인원 HWPX 소스) — 직선의방정식·평면좌표.

build_jikseon_v2.py/build_jikseon_workbook.py/finalize_jikseon_v2.py 3분할 파이프라인을
한 파일로 통합 + 2026-08-01 도형의이동 빌드에서 확정된 필수 검수 로직(선택지 결번보정·
그림형 통합선택지 감지·이미지 파일별 독립 디렉터리) 반영. WORKBOOK 표지는 기존
"직선의방정식_KERNEL+WORKBOOK_합본.pdf"(기준완성본) 실측 좌표 그대로 재현
(AI혼공시스템 스타일 — build_jikseon_workbook.py에 있던 generate_book_pdf 기본 표지는
이 스타일과 다름을 실측으로 확인, 커스텀 HTML로 교체).
"""
import sys, os, zipfile, json, base64, re, sqlite3, random, importlib
from collections import Counter
sys.path.insert(0, "/Users/youngwoolee/MathDB/app")
sys.path.insert(0, "/Users/youngwoolee/MathDB/scripts")
from dotenv import load_dotenv; load_dotenv("/Users/youngwoolee/MathDB/.env")
import xml.etree.ElementTree as ET
from parse_hwpx import _extract_questions_from_xml
from strip_review_notes import strip_review_notes
import pdf_engine; importlib.reload(pdf_engine)
import build_pyeongjwapyo_by_difficulty as tpl; importlib.reload(tpl)
from pdf_engine import generate_book_pdf
from PIL import Image as PIL
import fitz
from playwright.sync_api import sync_playwright

SRC_DIR = "/Users/youngwoolee/Downloads/수업자료/탑반 교재"
DB = "/Users/youngwoolee/MathDB/db/mathdb.sqlite"
CW, CH = 595.9199, 842.8800

CHAPTERS = [
    {
        "tag": "jikseon2",
        "hwpx": f"{SRC_DIR}/올인원 직선의방정식.hwpx",
        "chapter": "직선의 방정식",
        "out": f"{SRC_DIR}/올인원_직선의방정식_KERNEL+WORKBOOK_합본.pdf",
    },
    {
        "tag": "pyeongjwa2",
        "hwpx": f"{SRC_DIR}/올인원 평면좌표.hwpx",
        "chapter": "평면좌표",
        "out": f"{SRC_DIR}/올인원_평면좌표_KERNEL+WORKBOOK_합본.pdf",
    },
]

IMG_MARKER = re.compile(r"<<IMG:(image\d+)>>")

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
"""


def parse_types_section(texts):
    q_to_type = {}
    i, qnum, current = 0, 0, None
    while i < len(texts):
        t = texts[i].strip()
        if re.match(r"^\d{2}$", t) and i + 1 < len(texts):
            nxt = texts[i + 1].strip()
            if nxt and any('가' <= c <= '힣' for c in nxt) and len(nxt) > 4 and "정답" not in nxt:
                current = (t, nxt); i += 2; continue
        if "정답" in t:
            qnum += 1
            if current: q_to_type[qnum] = current
        i += 1
    return q_to_type


def build_kp(cfg):
    z = zipfile.ZipFile(cfg["hwpx"])
    all_rows = []
    for sec_no in range(4):
        name = f"Contents/section{sec_no}.xml"
        if name not in z.namelist(): continue
        xml_str = z.read(name).decode("utf-8", errors="ignore")
        try: root = ET.fromstring(xml_str)
        except Exception: continue
        r = _extract_questions_from_xml(root, watermark_images=set(), debug=False)
        if not r: continue
        if sec_no == 0:
            texts = re.findall(r"<hp:t>([^<]*)</hp:t>", xml_str)
            q_to_type = parse_types_section(texts)
            for idx, q in enumerate(r, 1):
                tp = q_to_type.get(idx)
                q['chapter'] = f"유형 {tp[0]} · {tp[1]}" if tp else "유형 기타"
        else:
            for q in r: q['chapter'] = "고난도정복"
        all_rows.extend(r)
    print(f"[PARSE:{cfg['tag']}] 총 {len(all_rows)}문제")

    # 선택지 번호 결번 보정
    gap_fixed = 0
    for q in all_rows:
        choices = q.get('choices') or []
        if not choices: continue
        nums = sorted(c.get('number') for c in choices)
        have = {c.get('number') for c in choices}
        missing = set(range(nums[0], nums[-1] + 1)) - have
        if missing:
            for m in missing: choices.append({'number': m, 'text': ''})
            choices.sort(key=lambda c: c.get('number'))
            gap_fixed += 1
    if gap_fixed: print(f"[CHOICE-GAP:{cfg['tag']}] {gap_fixed}문제")

    # 그림형 통합 선택지 감지
    combined_img_fixed = 0
    for q in all_rows:
        choices = q.get('choices') or []
        if not choices: continue
        ref_count = Counter()
        for c in choices:
            for ref in set(IMG_MARKER.findall(c.get('text', '') or '')):
                ref_count[ref] += 1
        combined_ref = next((ref for ref, cnt in ref_count.items() if cnt >= 3), None)
        if not combined_ref: continue
        for c in choices:
            c['text'] = IMG_MARKER.sub('', c.get('text', '') or '').strip()
        q['question_text'] = (q.get('question_text', '') or '') + f"<<IMG:{combined_ref}>>"
        combined_img_fixed += 1
    if combined_img_fixed: print(f"[COMBINED-IMG:{cfg['tag']}] {combined_img_fixed}문제")

    # BinData 이미지 전량 추출 (파일별 독립 디렉터리)
    SRC_IMG = f"/tmp/topban_kp_bin_{cfg['tag']}"
    os.makedirs(SRC_IMG, exist_ok=True)
    for n in z.namelist():
        if n.startswith("BinData/") and not n.endswith("/"):
            with z.open(n) as f:
                open(f"{SRC_IMG}/{os.path.basename(n)}", "wb").write(f.read())
    z.close()

    SMALL_DIR = f"/tmp/topban_kp_small_{cfg['tag']}"
    os.makedirs(SMALL_DIR, exist_ok=True)

    referenced = set()
    for q in all_rows:
        for src in (q.get('question_text', ''), q.get('solution_text', '')):
            referenced.update(IMG_MARKER.findall(src or ''))
        for c in (q.get('choices') or []):
            referenced.update(IMG_MARKER.findall(c.get('text', '') or ''))

    ref_count2 = Counter()
    for q in all_rows:
        seen = set()
        for src in (q.get('question_text', ''), q.get('solution_text', '')):
            seen.update(IMG_MARKER.findall(src or ''))
        for c in (q.get('choices') or []):
            seen.update(IMG_MARKER.findall(c.get('text', '') or ''))
        for n in seen: ref_count2[n] += 1
    BADGES = set(n for n, c in ref_count2.items() if c >= 2)
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
            if h > 0 and (w / h > 2.0) and h < 200: BADGES.add(name)
            elif w < 150 and h < 150: BADGES.add(name)
        except Exception: pass

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
                if img.width > 800:
                    r = 800 / img.width
                    img = img.resize((800, int(img.height * r)))
                img.save(dst, "JPEG", quality=85)
            except Exception as e:
                print(f"[WARN:{cfg['tag']}] {name}: {e}"); continue
        with open(dst, "rb") as f:
            IMG_URL[name] = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
    print(f"[IMG:{cfg['tag']}] 참조={len(referenced)} 배지={len(BADGES)} 이관={len(IMG_URL)}")

    rows = []
    for i, q in enumerate(all_rows, 1):
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
        rows.append({
            'question_id': i,
            'question_text': tpl.typeset_body(qt),
            'solution_text': st,
            'answer': q.get('answer', ''),
            'choices': json.dumps(new_choices, ensure_ascii=False),
            'chapter': q.get('chapter', '기타'),
            'difficulty': '', 'school': '', 'year': None,
            'semester': '', 'exam_type': '',
            'question_number': i,
            'has_image': bool(q_imgs),
            'images': q_imgs,
        })

    overrides = {r['question_id']: 'full' for r in rows}
    pdf_bytes = generate_book_pdf(
        rows, title=cfg["chapter"], subtitle="공통수학2 KERNEL POINT",
        include_source=False, overrides=overrides, logo_path=None,
        kicker_mark=None, kicker_text=None,
        divider_meta_top=f"공통수학2 · {cfg['chapter']} · KERNEL POINT",
        divider_footer_title=f"공통수학2 · {cfg['chapter']} · KERNEL POINT",
        divider_footer_sub="이영우 T",
        cover_main_title="2학기 중간대비", cover_tagline=f"공통수학2 {cfg['chapter']}",
        cover_big_word="KERNEL POINT", cover_kicker="MATHOLOGY · 2026",
        cover_footer_main="MATHOLOGY · 2026",
        cover_footer_sub=f"공통수학2 · {cfg['chapter']} · KERNEL POINT",
        page_running_left=f"공통수학2 {cfg['chapter']} · KERNEL POINT",
        extra_css=CROME_CSS, extra_js=tpl.TYPESET_JS,
        running_numbering=True, major_hint=cfg["chapter"],
    )
    out = f"/tmp/topban_kp_{cfg['tag']}.pdf"
    open(out, "wb").write(pdf_bytes)
    print(f"[OK] KP:{cfg['tag']} {len(rows)}문제 → {out}")
    return out


# DB 원본 LaTeX 자체가 깨져 있는 것으로 확인된 문항 (괄호 누락 등 원본 오염 —
# 렌더 엔진 정규식으로 안전하게 복구 불가, 선별에서 제외).
EXCLUDE_QIDS = {185791}  # 평면좌표 55번 후보: \sqrt4+4, \mathrm{\overline} MG 등 중괄호 누락


def select_workbook(cfg, n=100, seed=42):
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT question_id FROM questions WHERE chapter=? AND difficulty IN ('중','상') "
        "AND question_id NOT IN ({}) ORDER BY question_id".format(
            ",".join(str(q) for q in EXCLUDE_QIDS) or "-1"),
        (cfg["chapter"],),
    )
    ids = [r[0] for r in c.fetchall()]
    random.seed(seed); random.shuffle(ids)
    picked = ids[:n]
    print(f"[SELECT:{cfg['tag']}] 후보 {len(ids)}개 중 {len(picked)}문제 선택")

    marks = ",".join(["?"] * len(picked))
    c.execute(
        f"SELECT question_id, question_text, choices, answer, answer_type, difficulty, "
        f"school, year, semester, exam_type, has_image FROM questions WHERE question_id IN ({marks})", picked)
    rows_by_id = {r["question_id"]: dict(r) for r in c.fetchall()}
    c.execute(f"SELECT question_id, solution_text FROM solutions WHERE question_id IN ({marks})", picked)
    sol_by_id = {r["question_id"]: r["solution_text"] for r in c.fetchall()}
    c.execute(f"SELECT question_id, image_ref, image_path, image_type FROM images WHERE question_id IN ({marks})", picked)
    img_by_q, sol_img_by_q = {}, {}
    for r in c.fetchall():
        target = sol_img_by_q if r["image_type"] == "solution" else img_by_q
        target.setdefault(r["question_id"], {})[r["image_ref"]] = r["image_path"]

    out = []
    for qid in picked:
        r = rows_by_id.get(qid)
        if not r: continue
        choices = r.get("choices")
        if choices:
            try: choices = json.loads(choices)
            except Exception: pass
            if isinstance(choices, list):
                for ch in choices:
                    if isinstance(ch, dict) and ch.get("text"):
                        ch["text"] = strip_review_notes(ch["text"])
        out.append({
            "question_id": qid,
            "question_text": strip_review_notes(r.get("question_text") or ""),
            "solution_text": strip_review_notes(sol_by_id.get(qid) or ""),
            "choices": choices,
            "answer": r.get("answer") or "",
            "difficulty": r.get("difficulty") or "",
            "school": r.get("school") or "",
            "year": r.get("year"),
            "semester": r.get("semester") or "",
            "exam_type": r.get("exam_type") or "",
            "has_image": bool(r.get("has_image")),
            "images": img_by_q.get(qid, {}),
            "images_sol": sol_img_by_q.get(qid, {}),
        })
    conn.close()
    json_path = f"/tmp/topban_kp_wb_{cfg['tag']}.json"
    json.dump(out, open(json_path, "w"), ensure_ascii=False)
    print(f"[OK] WB 선별:{cfg['tag']} {len(out)}문제 → {json_path}")
    return json_path, len(out)


def build_workbook_pdf(cfg, json_path):
    rows_raw = json.load(open(json_path))
    rows = []
    for i, q in enumerate(rows_raw, 1):
        q = dict(q)
        q['question_id'] = i
        q['question_number'] = i
        q['question_text'] = tpl.typeset_body(q.get('question_text', '') or '')
        q['chapter'] = f"{cfg['chapter']} · WORKBOOK"
        if isinstance(q.get('choices'), list):
            q['choices'] = json.dumps(q['choices'], ensure_ascii=False)
        rows.append(q)

    overrides = {r['question_id']: 'full' for r in rows}
    pdf = generate_book_pdf(
        rows, title=cfg["chapter"], subtitle="공통수학2 WORKBOOK",
        include_source=True, overrides=overrides, logo_path=None,
        divider_meta_top=f"공통수학2 · {cfg['chapter']} · WORKBOOK",
        divider_footer_title=f"공통수학2 · {cfg['chapter']} · WORKBOOK",
        divider_footer_sub="이영우 T",
        cover_main_title="2학기 중간대비", cover_tagline=f"공통수학2 {cfg['chapter']}",
        cover_big_word="WORKBOOK", cover_kicker="MATHOLOGY · 2026",
        cover_footer_main="MATHOLOGY · 2026",
        cover_footer_sub=f"공통수학2 · {cfg['chapter']} · WORKBOOK",
        page_running_left=f"공통수학2 {cfg['chapter']} · WORKBOOK",
        extra_css=CROME_CSS, extra_js=tpl.TYPESET_JS,
        running_numbering=True, major_hint=cfg["chapter"],
    )
    out = f"/tmp/topban_kp_wb_{cfg['tag']}.pdf"
    open(out, "wb").write(pdf)
    print(f"[OK] WORKBOOK:{cfg['tag']} {len(rows)}문제 → {out}")
    return out, len(rows)


def html_to_pdf(html):
    with sync_playwright() as p:
        b = p.chromium.launch(); page = b.new_page()
        page.set_content(html, wait_until="networkidle")
        page.wait_for_function("document.fonts.ready")
        out = page.pdf(format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    return out


def kp_cover_html(chapter):
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
  <div class="sub">공통수학2_{chapter}</div>
</div>
<div class="brand">공통수학2</div>
<div class="author">이영우 <span class="t">T</span></div>
<div class="mathology">M A T H O L O G Y  ·  2 0 2 6</div>
</body></html>"""


def wb_cover_html(chapter, count):
    """직선의방정식_KERNEL+WORKBOOK_합본.pdf(기준완성본) WB 표지 실측 좌표 재현
    (AI혼공시스템 스타일 — 킥커/과목/챕터명/히어로 실전기출·WORKBOOK/N제/저자박스/로고)."""
    return f"""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap" rel="stylesheet">
<style>
@font-face {{ font-family:'Paperlogy 9 Black'; src:url(data:font/ttf;base64,{paper_black}) format('truetype'); }}
@font-face {{ font-family:'Paperlogy 8 ExtraBold'; src:url(data:font/ttf;base64,{paper_eb}) format('truetype'); }}
@page {{ size: A4; margin: 0; }} * {{ box-sizing: border-box; }}
body {{ margin:0; padding:0; width:{CW}pt; height:{CH}pt; position:relative; background:#ffffff; font-family:'Paperlogy 8 ExtraBold', sans-serif; }}
.corner {{ position:absolute; width:42pt; height:42pt; border:1.2pt solid #1e3a8a; }}
.corner.tl {{ top:32pt; left:32pt; border-right:0; border-bottom:0; }}
.corner.br {{ bottom:32pt; right:32pt; border-left:0; border-top:0; }}
.kicker {{ position:absolute; top:96pt; left:0; right:0; text-align:center; font-size:11pt; color:#1e3a8a; letter-spacing:8pt; }}
.subject {{ position:absolute; top:220pt; left:0; right:0; text-align:center; font-family:'Black Han Sans', sans-serif; font-size:38pt; color:#0f172a; }}
.chapter {{ position:absolute; top:310pt; left:0; right:0; text-align:center; font-family:'Black Han Sans', sans-serif; font-size:30pt; color:#0f172a; }}
.hero1 {{ position:absolute; top:396pt; left:0; right:0; text-align:center; font-family:'Black Han Sans', sans-serif; font-size:66pt; color:#1e3a8a; }}
.hero2 {{ position:absolute; top:466pt; left:0; right:0; text-align:center; font-family:'Black Han Sans', sans-serif; font-size:78pt; color:#1e3a8a; letter-spacing:-2pt; }}
.count {{ position:absolute; top:596pt; left:0; right:0; text-align:center; font-size:13pt; letter-spacing:6pt; color:#334155; }}
.author {{ position:absolute; top:678pt; left:0; right:0; text-align:center; }}
.author span {{ display:inline-block; border:1pt solid #1e3a8a; border-radius:4mm; padding:8pt 30pt; font-size:14pt; letter-spacing:5pt; color:#1e3a8a; }}
.logo {{ position:absolute; bottom:56pt; right:50pt; max-height:34pt; }}
</style></head><body>
<div class="corner tl"></div><div class="corner br"></div>
<div class="kicker">M A T H &nbsp;&nbsp;WORKBOOK&nbsp;&nbsp; 2 0 2 6</div>
<div class="subject">공통수학2</div>
<div class="chapter">{chapter}</div>
<div class="hero1">실전기출</div>
<div class="hero2">WORKBOOK</div>
<div class="count">{count} 제</div>
<div class="author"><span>이 영 우 T</span></div>
<img class="logo" src="data:image/png;base64,{eum_logo}">
</body></html>"""


def finalize(cfg, kp_pdf_path, wb_pdf_path, wb_count):
    kp = fitz.open(kp_pdf_path)
    kp.delete_page(0)
    cover_pdf = fitz.open("pdf", html_to_pdf(kp_cover_html(cfg["chapter"])))
    kp.insert_pdf(cover_pdf, start_at=0); cover_pdf.close()

    COMBINED_OFFSET = 2  # 표지+목차 = 2p 추가

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
                if 1 <= n <= 300 and n not in sol_map:
                    sol_map[n] = i + 1 + COMBINED_OFFSET

    overlay_count = 0
    for pidx in range(kp.page_count):
        if sol_start is not None and pidx >= sol_start: break
        nums = get_slot_nums_problem(kp[pidx])
        slot_nums = [n for n in nums if 1 <= n <= 300]
        if not slot_nums: continue
        first_num = min(slot_nums)
        sol_pg = sol_map.get(first_num)
        if not sol_pg: continue
        page = kp[pidx]
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
        for pidx in range(sol_start, kp.page_count):
            page = kp[pidx]
            w, h = page.rect.width, page.rect.height
            combined_pg = pidx + 1 + COMBINED_OFFSET
            try:
                page.insert_text((w / 2 - 10, h - 22), f"- {combined_pg} -", fontname="helv", fontsize=9, color=(0.3, 0.3, 0.35))
            except Exception:
                pass
    print(f"[OVERLAY:{cfg['tag']}] {overlay_count}개 페이지, 해설매핑 {len(sol_map)}개")

    # WB 표지 교체 (AI혼공시스템 스타일)
    wb_doc = fitz.open(wb_pdf_path)
    wb_doc.delete_page(0)
    wb_cover_pdf = fitz.open("pdf", html_to_pdf(wb_cover_html(cfg["chapter"], wb_count)))
    wb_doc.insert_pdf(wb_cover_pdf, start_at=0); wb_cover_pdf.close()

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
<div class="sub">공통수학2 · {cfg['chapter']} · KERNEL POINT + WORKBOOK</div>
<hr>
<ul>
  <li><span class="name">KERNEL POINT</span><span class="dot"></span><span class="page">p. {kp_first_page_final}</span></li>
  <li><span class="name">KERNEL POINT · 정답 및 해설</span><span class="dot"></span><span class="page">p. {kp_sol_page_final}</span></li>
  <li><span class="name">WORKBOOK</span><span class="dot"></span><span class="page">p. {wb_cover_final}</span></li>
  <li><span class="name">WORKBOOK · 정답 및 해설</span><span class="dot"></span><span class="page">p. {wb_sol_page_final}</span></li>
</ul>
</body></html>"""

    toc_pdf = fitz.open("pdf", html_to_pdf(TOC_HTML))

    final = fitz.open()
    final.insert_pdf(kp, from_page=0, to_page=0)
    final.insert_pdf(toc_pdf)
    final.insert_pdf(kp, from_page=1, to_page=kp.page_count - 1)
    final.insert_pdf(wb_doc)

    final.save(cfg["out"], deflate=True, garbage=4)
    final.close(); kp.close(); wb_doc.close(); toc_pdf.close()

    os.system(f"xattr -c '{cfg['out']}'")
    print(f"[DONE:{cfg['tag']}] {cfg['out']}  KP={kp_total}p WB={wb_total}p 해설매핑={len(sol_map)}개")


if __name__ == "__main__":
    for cfg in CHAPTERS:
        kp_pdf = build_kp(cfg)
        json_path, wb_count = select_workbook(cfg)
        wb_pdf, _ = build_workbook_pdf(cfg, json_path)
        finalize(cfg, kp_pdf, wb_pdf, wb_count)
