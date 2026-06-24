"""Render KaTeX HTML snippets -> tightly cropped high-DPI PNGs.

Reads items.json: [{"id": "...", "html": "<inner html with $..$ math>",
                    "width": 520}].
Outputs <outdir>/<id>.png cropped to the .content box.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
KATEX_DIST = HERE / "node_modules" / "katex" / "dist"
KATEX_CSS = (KATEX_DIST / "katex.min.css").as_uri()
KATEX_JS = (KATEX_DIST / "katex.min.js").as_uri()
AUTO_JS = (KATEX_DIST / "contrib" / "auto-render.min.js").as_uri()

TEMPLATE = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{css}">
<script src="{kjs}"></script>
<script src="{ajs}"></script>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html,body {{ background:#ffffff; }}
  .content {{
    width:{width}px; padding:2px 2px 2px 2px;
    font-family:"Nanum Gothic","AppleSDGothicNeo-Regular","Apple SD Gothic Neo",sans-serif;
    font-size:{fs}px; line-height:1.55; color:#15192e;
    font-weight:600;
  }}
  .content p {{ margin:0 0 {pgap}px 0; }}
  .content p:last-child {{ margin-bottom:0; }}
  .katex {{ font-size:1.06em; }}
  .cbox {{ border:1px solid #2a3550; border-radius:3px;
           padding:{bp}px {bp2}px; margin:{pgap}px 0; }}
  .choices {{ display:flex; flex-wrap:wrap; }}
  .choices .ch {{ width:33.33%; padding:{cgap}px 0; white-space:nowrap; }}
  .choices.col2 .ch {{ width:50%; }}
  .figrow {{ text-align:center; margin:{fig}px 0 2px 0; }}
  .figrow img {{ max-width:{figw}px; height:auto; }}
  .ind {{ padding-left:1.0em; }}
  .small {{ font-size:0.88em; }}
  .bl {{ display:inline-block; border:1px solid #8a8f9c; border-radius:3px;
         padding:0 0.34em; margin:0 0.06em; font-weight:700; font-size:0.92em;
         line-height:1.25; }}
  .lead {{ color:#5a5f6e; font-size:0.95em; margin-bottom:{pgap}px; }}
  .case {{ margin-top:{pgap}px; }}
  ol.parts {{ list-style:none; }}
  ol.parts > li {{ margin:{pgap}px 0; }}
  .pno {{ font-weight:700; }}
</style></head>
<body><div class="content" id="c">{body}</div>
<script>
renderMathInElement(document.getElementById('c'), {{
  delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}],
  throwOnError:true, strict:false
}});
// 폭 넘치는 수식 자동 축소 (컨테이너 밖 잘림 방지)
(function(){{
  var c=document.getElementById('c');
  var avail=c.clientWidth - 6;
  document.querySelectorAll('.katex-display').forEach(function(d){{
    var k=d.querySelector('.katex'); if(!k) return;
    var box=Math.min(d.clientWidth, avail);
    var w=k.scrollWidth;
    if(w>box-1){{ d.style.fontSize=(Math.max(0.45,(box/w)*0.97)*100)+'%'; }}
  }});
  document.querySelectorAll('#c p .katex, #c li .katex').forEach(function(k){{
    if(k.closest('.katex-display')) return;
    var w=k.scrollWidth;
    if(w>avail-1){{ k.style.fontSize=(Math.max(0.45,(avail/w)*0.97)*100)+'%'; }}
  }});
}})();
</script></body></html>"""


def main():
    items = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    outdir = Path(sys.argv[2]).resolve(); outdir.mkdir(parents=True, exist_ok=True)
    tmp = outdir / "_html"; tmp.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(device_scale_factor=3)
        for it in items:
            fs = it.get("fs", 30)
            html = TEMPLATE.format(
                css=KATEX_CSS, kjs=KATEX_JS, ajs=AUTO_JS,
                width=it.get("width", 520), fs=fs,
                pgap=it.get("pgap", round(fs*0.42)),
                bp=round(fs*0.30), bp2=round(fs*0.42),
                cgap=round(fs*0.18), fig=round(fs*0.5),
                figw=it.get("figw", 360), body=it["html"])
            f = tmp / f"{it['id']}.html"
            f.write_text(html, encoding="utf-8")
            pg.goto(f.as_uri())
            pg.wait_for_timeout(120)
            el = pg.query_selector("#c")
            el.screenshot(path=str(outdir / f"{it['id']}.png"))
            print("rendered", it["id"])
        b.close()


if __name__ == "__main__":
    main()
