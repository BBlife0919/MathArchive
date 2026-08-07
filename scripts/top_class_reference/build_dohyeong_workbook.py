"""도형의 이동 WORKBOOK 재빌드 — 통번호(1부터), 매쏠로지 100문제."""
import sys, os, base64, json, importlib
sys.path.insert(0, "/Users/youngwoolee/MathDB/app")
sys.path.insert(0, "/Users/youngwoolee/MathDB/scripts")
from dotenv import load_dotenv; load_dotenv("/Users/youngwoolee/MathDB/.env")
import pdf_engine; importlib.reload(pdf_engine)
import build_pyeongjwapyo_by_difficulty as tpl; importlib.reload(tpl)
from pdf_engine import generate_book_pdf

rows_raw = json.load(open('/tmp/dohyeong_workbook.json'))

rows = []
for i, q in enumerate(rows_raw, 1):
    q = dict(q)
    q['question_id'] = i
    q['question_number'] = i
    q['question_text'] = tpl.typeset_body(q.get('question_text','') or '')
    q['chapter'] = "도형의 이동 · WORKBOOK"
    if isinstance(q.get('choices'), list):
        q['choices'] = json.dumps(q['choices'], ensure_ascii=False)
    rows.append(q)

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
pdf = generate_book_pdf(
    rows, title="도형의 이동", subtitle="공통수학2 WORKBOOK",
    include_source=True, overrides=overrides, logo_path=None,
    divider_meta_top="공통수학2 · 도형의 이동 · WORKBOOK",
    divider_footer_title="공통수학2 · 도형의 이동 · WORKBOOK",
    divider_footer_sub="이영우 T",
    cover_main_title="2학기 중간대비", cover_tagline="공통수학2 도형의 이동",
    cover_big_word="WORKBOOK", cover_kicker="MATHOLOGY · 2026",
    cover_footer_main="MATHOLOGY · 2026",
    cover_footer_sub="공통수학2 · 도형의 이동 · WORKBOOK",
    page_running_left="공통수학2 도형의 이동 · WORKBOOK",
    extra_css=CROME_CSS, extra_js=tpl.TYPESET_JS,
    running_numbering=True,
)
open('/tmp/dohyeong_workbook.pdf','wb').write(pdf)
print(f"[OK] WORKBOOK {len(rows)}문제")
