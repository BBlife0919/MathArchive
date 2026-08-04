"""신규 KP 표지 템플릿 (2026-08-05) — CIRCUIT_미적분1_중간고사대비.pdf 표지를 베이스로
사용자 지시대로 수정: CIRCUIT→KERNEL POINT, 우측상단 문구 교체, 우측하단 태그 삭제,
좌하단 로고→우하단 이동+축소. 그라디언트 반원 도형은 원본 PDF에서 고해상도로
크롭한 이미지를 그대로 재사용(직접 CSS로 재현하지 않음 — 픽셀 그대로라 색감 100% 동일).
"""
import base64, os

CW, CH = 595.9199, 842.8800

_paper_black = base64.b64encode(open(os.path.expanduser("~/Library/Fonts/Paperlogy-9Black.ttf"), "rb").read()).decode()
_gradient_img = base64.b64encode(open("/Users/youngwoolee/MathDB/app/assets/kp_cover_gradient_shape.png", "rb").read()).decode()
_eum_logo = base64.b64encode(open("/Users/youngwoolee/MathDB/app/assets/eum_logo.png", "rb").read()).decode()


def kp_cover_v2_html(subtitle: str = "공수2 중간고사대비", instructor: str = "이영우 T") -> str:
    return f"""<!DOCTYPE html><html><head>
<style>
@font-face {{ font-family:'Paperlogy 9 Black'; src:url(data:font/ttf;base64,{_paper_black}) format('truetype'); }}
@page {{ size: A4; margin: 0; }} * {{ box-sizing: border-box; }}
body {{ margin:0; padding:0; width:{CW}pt; height:{CH}pt; position:relative; background:#ffffff;
  font-family: -apple-system, 'Apple SD Gothic Neo', sans-serif; }}
.subtitle {{ position:absolute; top:58pt; right:50pt; text-align:right; font-size:14.5pt;
  font-weight:600; color:#8a8f9d; line-height:1.35; }}
.gradient {{ position:absolute; left:50pt; top:100pt; width:330pt; height:480pt; }}
.big-word {{ position:absolute; left:400pt; right:50pt; top:220pt; bottom:150pt; display:flex;
  flex-direction:row; align-items:flex-start; justify-content:center; gap:20pt; }}
.big-word .col {{ display:flex; flex-direction:column; align-items:center; }}
.big-word .col span {{ font-family:'Paperlogy 9 Black', sans-serif; font-size:46pt; color:#16171b;
  line-height:1.25; letter-spacing:0; }}
.rule {{ position:absolute; left:50pt; right:50pt; top:672pt; height:1pt; background:#d8dade; }}
.footer {{ position:absolute; left:50pt; right:50pt; top:686pt; display:flex; align-items:center; }}
.footer .instructor {{ flex:1; text-align:center; font-size:15pt; font-weight:700; color:#16171b; }}
.footer .logo {{ position:absolute; right:0; top:50%; transform:translateY(-50%); max-height:26pt; }}
</style></head><body>
<div class="subtitle">{subtitle}</div>
<img class="gradient" src="data:image/png;base64,{_gradient_img}">
<div class="big-word">
  <div class="col">{''.join(f'<span>{ch}</span>' for ch in 'KERNEL')}</div>
  <div class="col">{''.join(f'<span>{ch}</span>' for ch in 'POINT')}</div>
</div>
<div class="rule"></div>
<div class="footer">
  <span class="instructor">{instructor}</span>
  <img class="logo" src="data:image/png;base64,{_eum_logo}">
</div>
</body></html>"""
