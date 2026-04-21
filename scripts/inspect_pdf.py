"""샘플 PDF 1개의 텍스트·레이아웃을 덤프해 [중단원]/[난이도] 앵커 위치와 문항 경계 패턴을 파악한다."""
import sys
import fitz

path = sys.argv[1]
doc = fitz.open(path)
print(f"=== {path}")
print(f"pages={len(doc)}")

for pno, page in enumerate(doc):
    print(f"\n--- page {pno+1} size={page.rect}")
    blocks = page.get_text("blocks")
    for b in blocks:
        x0, y0, x1, y1, text, bno, btype = b
        t = text.strip().replace("\n", " | ")
        if len(t) > 120:
            t = t[:120] + "..."
        print(f"  [{y0:6.1f}-{y1:6.1f}] x={x0:5.1f}-{x1:5.1f} #{bno} type={btype}: {t}")
