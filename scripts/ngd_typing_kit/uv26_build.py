# -*- coding: utf-8 -*-
"""운산고 2026 2학기 중간(2학년 미적분Ⅰ) HWPX 조립기.
골격: 광명북고 1-2-a(공수2) 완성본 clone(같은 학교 계통 charPr/paraPr 재사용).
build.py의 저수준 헬퍼를 재사용하고, 단답형(다중 소문항) 문항만 이 파일에서 커스텀 처리한다.
"""
import os, re, zipfile, datetime
from xml.sax.saxutils import escape

os.environ.setdefault('NGD_SKELETON',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out',
                 '[고][2026][1-2-a][경기광명시][광명북고][공수2][평면좌표-도형의이동][그림4-0-4-0].hwpx'))

import build as B
from uv26_content import Q

B.Q = Q
B.COL_USABLE = 77000
B.MAX_PER = 2   # 고등부: 한 단 2문항(동분할)
B.IDS.z = 1000   # 골격 첫 문단의 zOrder와 겹치지 않게
B.SCHOOL_TITLE = '2026년 2학기 중간'
B.SCHOOL = '운산 고등학교'
B.COURSE = '미적분Ⅰ'
B.UNITS = '함수의 극한 ~ 도함수의 활용'
B.PROD_DATE = '2026년 09월 29일'
B.FILENAME_STEM = '[고][2026][2-2-a][경기광명시][운산고][미적분1][함수의극한-도함수의활용][그림1]'
B.DOC_TITLE = '2026년 2학기 중간 운산고등학교 2학년 함수의극한~도함수의활용'


# ------------------------------------------------------------------ 관계연산자 1개 규칙: 수식 하나에 관계연산자 하나만
_REL = ('LEQ', 'GEQ', 'NEQ', '<', '>', '=')
_NOSPLIT = set()
_orig_parse_mix = B.parse_mix


def _split_rel(script):
    out, d, start, n = [], 0, 0, 0
    i = 0
    while i < len(script):
        if script.startswith('LEFT', i) and not script[i:i+5].startswith('LEFT'):
            pass
        if script.startswith('LEFT', i):
            d += 1; i += 4; continue
        if script.startswith('RIGHT', i):
            d -= 1; i += 5; continue
        ch = script[i]
        if ch in '{([':
            d += 1
        elif ch in '})]':
            d -= 1
        elif d == 0:
            tok = None
            for r in ('LEQ', 'GEQ', 'NEQ'):
                if script.startswith(r, i):
                    tok = r
                    break
            if tok is None and ch in '<>=':
                tok = ch
            if tok:
                n += 1
                if n >= 2:
                    out.append(script[start:i]); start = i
                    n = 1
                i += len(tok); continue
        i += 1
    out.append(script[start:])
    return out


def _parse_mix(s):
    items = []
    for kind, v in _orig_parse_mix(s):
        if kind == 'eq' and s not in _NOSPLIT:
            parts = _split_rel(v)
            for p in parts:
                items.append(('eq', p))
        else:
            items.append((kind, v))
    return items


B.parse_mix = _parse_mix


# ------------------------------------------------------------------ 조건틀(hp:rect) 범용: 줄 단위 문단 목록
def rect_box(lines, width=29437):
    """lines: [(label, mix)] — label은 첫 줄 앞에 붙는 평문('(가) ' 등, 없으면 '')."""
    ps = []
    total = 0
    for lab, s in lines:
        its = ([('t', lab)] if lab else []) + B.parse_mix(s)
        for litems, h in B.flow_items(its, width=26500):
            ps.append(B.para(B.runs_xml(litems), pr='0', vertsize=h, horz=width - 1700))
            total += 3180 if h > 2000 else 1725
    height = max(total + 1700 + 1418, 4000)
    rid = B.IDS.picid()
    iid = B.IDS.instid()
    zid = B.IDS.zo()
    head = B.JOGEON_HEAD.replace('id="1159475994"', f'id="{rid}"', 1)
    head = head.replace('zOrder="1" numberingType', f'zOrder="{zid}" numberingType', 1)
    head = head.replace('instid="85734171"', f'instid="{iid}"', 1)
    head = head.replace('<hp:orgSz width="28644" height="12587"/>', f'<hp:orgSz width="{width}" height="{height}"/>')
    head = head.replace('<hp:curSz width="29437" height="11450"/>', f'<hp:curSz width="{width}" height="{height}"/>')
    head = head.replace('<hc:scaMatrix e1="1.027685" e2="0" e3="0" e4="0" e5="0.909669" e6="0"/>',
                         '<hc:scaMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>')
    tail = B.JOGEON_TAIL.replace(
        '<hc:pt1 x="28644" y="0"/><hc:pt2 x="28644" y="12587"/><hc:pt3 x="0" y="12587"/>',
        f'<hc:pt1 x="{width}" y="0"/><hc:pt2 x="{width}" y="{height}"/><hc:pt3 x="0" y="{height}"/>')
    tail = tail.replace('<hp:sz width="29437" widthRelTo="ABSOLUTE" height="6468" heightRelTo="ABSOLUTE" protect="0"/>',
                         f'<hp:sz width="{width}" widthRelTo="ABSOLUTE" height="{height}" heightRelTo="ABSOLUTE" protect="0"/>')
    box_xml = head + ''.join(ps) + tail
    p = (f'<hp:p id="2147483648" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
         f'<hp:run charPrIDRef="1">{box_xml}<hp:t/></hp:run>{B.lineseg(0, height)}</hp:p>')
    return p, height


# ------------------------------------------------------------------ 4항목 보기박스(ㄱㄴㄷㄹ)
def bogi_box4(items):
    xml = B.BOX_SRC
    xml = re.sub(r'<hp:tbl id="\d+" zOrder="\d+"', lambda m: f'<hp:tbl id="{B.IDS.picid()}" zOrder="{B.IDS.zo()}"', xml)
    xml = re.sub(r'<hp:equation id="\d+" zOrder="\d+"', lambda m: f'<hp:equation id="{B.IDS.eqid()}" zOrder="{B.IDS.zo()}"', xml)
    marker_start = '<hp:p id="2147483648" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="1"><hp:t>ㄱ. </hp:t>'
    a = xml.index(marker_start)
    m3 = xml.index('<hp:t>ㄷ. </hp:t>')
    b = xml.index('</hp:p>', m3) + len('</hp:p>')
    labels = ['ㄱ. ', 'ㄴ. ', 'ㄷ. ', 'ㄹ. ']
    ps = []
    total_h = 0
    for lab, s in zip(labels, items):
        its = [('t', lab)] + B.parse_mix(s)
        for litems, h in B.flow_items(its, width=27800):
            ps.append(f'<hp:p id="2147483648" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                      f'{B.runs_xml(litems)}{B.lineseg(0, h, 27800)}</hp:p>')
            total_h += B.pitch(h)
    xml = xml[:a] + ''.join(ps) + xml[b:]
    return xml, total_h


# ------------------------------------------------------------------ 단답형(다중 소문항) 끝노트
def endnote_short_xml(q, num):
    inst = B.IDS.instid()
    paras = []
    vp = 0
    mix = q['ans_mix'] if q.get('ans_mix') else ' '.join(f'({i+1}) {s["ans"]}' for i, s in enumerate(q['subs']))
    items = B.parse_mix(mix)
    ans_runs = B.runs_xml(items, '12')
    h0 = max(1200, B.item_h(items))
    head = (f'<hp:run charPrIDRef="9"><hp:ctrl><hp:autoNum num="{num}" numType="ENDNOTE"><hp:autoNumFormat type="DIGIT" '
            f'userChar="" prefixChar="" suffixChar="." supscript="0"/></hp:autoNum></hp:ctrl></hp:run>'
            f'<hp:run charPrIDRef="1"><hp:t> [정답] </hp:t></hp:run>{ans_runs}')
    paras.append(f'<hp:p id="2147483648" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">{head}'
                 f'{B.lineseg(vp, h0)}</hp:p>')
    vp += B.pitch(h0)
    sol_lines = q.get('sol_all')
    if sol_lines is None:
        sol_lines = []
        for s in q['subs']:
            sol_lines += s['sol']
    for line in sol_lines:
        its = B.parse_mix(line)
        for litems, h in B.flow_items(its, width=B.LINE_W):
            paras.append(f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                         f'{B.runs_xml(litems)}{B.lineseg(vp, h)}</hp:p>')
            vp += B.pitch(h)
    xml = (f'<hp:ctrl><hp:endNote number="{num}" suffixChar="46" instId="{inst}"><hp:subList id="" textDirection="HORIZONTAL" '
           f'lineWrap="BREAK" vertAlign="TOP" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" '
           f'hasTextRef="0" hasNumRef="0">{"".join(paras)}</hp:subList></hp:endNote></hp:ctrl>')
    return xml




def _add_text(Bl, q, num, key, first=True):
    en, w = B.endnote_xml(q, num)
    Bl.warns += [f'Q{q["id"]}: {x}' for x in w]
    items = B.parse_mix(q[key])
    prefix_run = f'<hp:run charPrIDRef="1">{en}</hp:run>'
    ps, h = B.flow_paras(items, width=B.LINE_W, first_indent=1300, prefix_run=prefix_run)
    Bl.paras += ps
    Bl.h += h


def _add_plain(Bl, key_q, key):
    its = B.parse_mix(key_q[key])
    ps, h = B.flow_paras(its, width=B.LINE_W)
    Bl.paras += ps
    Bl.h += h


def _blank(Bl):
    Bl.paras.append(B.blank())
    Bl.h += B.PITCH_BLANK


def build_block(q, num, imgmap):
    if q['kind'] == 'short':
        return build_short(q, num, imgmap)
    Bl = B.Block()
    _add_text(Bl, q, num, 'text')
    Bl.h_lines = 1
    _blank(Bl)
    if q.get('fig'):
        pp, h = B.pic_para(q['fig'], imgmap[q['fig']])
        Bl.paras.append(pp)
        Bl.h += h + 600
        _blank(Bl)
    if q.get('mid_text'):
        _add_plain(Bl, q, 'mid_text')
        _blank(Bl)
    if q.get('box'):
        bx, bh = B.bogi_box(q['box_items'])
        Bl.paras.append(bx)
        Bl.h += bh + 1926 + 1100
        _blank(Bl)
    if q.get('box4'):
        bx, bh = bogi_box4(q['box_items'])
        Bl.paras.append(bx)
        Bl.h += bh + 1926 + 1100 + 600
        _blank(Bl)
    if q.get('jogeon_lines'):
        bx, bh = rect_box(q['jogeon_lines'])
        Bl.paras.append(bx)
        Bl.h += bh + 600
        _blank(Bl)
    if q.get('plain_box_items'):
        bx, bh = rect_box([('', s) for s in q['plain_box_items']])
        Bl.paras.append(bx)
        Bl.h += bh + 600
        _blank(Bl)
    cx, ch, w2 = B.choices_xml(q)
    Bl.warns += [f'Q{q["id"]}: {x}' for x in w2]
    Bl.paras += cx
    Bl.h += sum(B.pitch(x) for x in ch)
    Bl.paras.append(B.para(B.runs_xml([('t', f'[중단원] {q["ch"]}')], '2')))
    Bl.paras.append(B.para(B.runs_xml([('t', f'[난이도] {q["lv"]}')], '2')))
    Bl.h += 2 * B.PITCH_BLANK
    return Bl


def build_short(q, num, imgmap):
    Bl = B.Block()
    Bl.paras.append(B.para(B.runs_xml([('t', f'[서술형 {q["no"]}]')])))
    Bl.h += B.PITCH_BLANK
    en = endnote_short_xml(q, num)
    items = B.parse_mix(q['intro'])
    prefix_run = f'<hp:run charPrIDRef="1">{en}</hp:run>'
    ps, h = B.flow_paras(items, width=B.LINE_W, first_indent=1300, prefix_run=prefix_run)
    Bl.paras += ps
    Bl.h += h
    _blank(Bl)
    if q.get('plain_box_items') or q.get('jogeon_lines'):
        if q.get('plain_box_items'):
            bx, bh = rect_box([('', s) for s in q['plain_box_items']])
        else:
            bx, bh = rect_box(q['jogeon_lines'])
        Bl.paras.append(bx)
        Bl.h += bh + 600
        _blank(Bl)
    if q.get('intro3'):
        _add_plain(Bl, q, 'intro3')
        _blank(Bl)
    for sb in q.get('subs', []):
        ps2, h2 = B.flow_paras(B.parse_mix(sb['label']), width=B.LINE_W)
        Bl.paras += ps2
        Bl.h += h2
        _blank(Bl)
    Bl.paras.append(B.para(B.runs_xml([('t', f'[중단원] {q["ch"]}')], '2')))
    Bl.paras.append(B.para(B.runs_xml([('t', f'[난이도] {q["lv"]}')], '2')))
    Bl.h += 2 * B.PITCH_BLANK
    return Bl


# ------------------------------------------------------------------ 패키징
def build():
    zin = zipfile.ZipFile(B.SRC)
    sec = zin.read('Contents/section0.xml').decode('utf8')
    depth = 0
    end0 = None
    for m in re.finditer(r'<hp:p[ >]|</hp:p>', sec):
        if m.group().startswith('</'):
            depth -= 1
            if depth == 0:
                end0 = m.end()
                break
        else:
            depth += 1
    prefix = sec[:end0]
    for a, b in (('2026년 2학기 정기1차', B.SCHOOL_TITLE), ('광명북 고등학교', B.SCHOOL), ('공통수학2', B.COURSE),
                 ('평면좌표 ~ 도형의 이동', B.UNITS), ('2026년 09월 29일', B.PROD_DATE)):
        assert a in prefix, a
        prefix = prefix.replace(a, b, 1)
    figs = [q['fig'] for q in Q if q.get('fig')]
    imgmap = {f: f'image{3 + i}' for i, f in enumerate(figs)}
    blocks = []
    warns = []
    for n, q in enumerate(Q, start=1):
        blk = build_block(q, n, imgmap)
        blocks.append(blk)
        warns += blk.warns
    body, info = B.layout(blocks)
    tail = B.blank(cb=1)
    section = prefix + ''.join(body) + tail + '</hs:sec>'
    hdr = zin.read('Contents/header.xml').decode('utf8')
    m = re.search(r'<hh:charPr id="1" .*?</hh:charPr>', hdr, re.S)
    new_cp = m.group().replace('id="1"', 'id="14"', 1).replace('<hh:underline type="NONE"', '<hh:underline type="BOTTOM"')
    hdr = hdr.replace('</hh:charProperties>', new_cp + '</hh:charProperties>', 1)
    hdr = hdr.replace('<hh:charProperties itemCnt="14">', '<hh:charProperties itemCnt="15">', 1)
    assert 'itemCnt="15"' in hdr
    hpf = zin.read('Contents/content.hpf').decode('utf8')
    hpf = re.sub(r'<opf:title[^>]*>.*?</opf:title>', f'<opf:title>{escape(B.DOC_TITLE)}</opf:title>', hpf)
    hpf = re.sub(r'(name="ModifiedDate" content="text">)[^<]*', r'\g<1>' + datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), hpf)
    items = ['<opf:item id="header" href="Contents/header.xml" media-type="application/xml"/>',
             '<opf:item id="image1" href="BinData/image1.bmp" media-type="image/bmp" isEmbeded="1"/>',
             '<opf:item id="masterpage0" href="Contents/masterpage0.xml" media-type="application/xml"/>',
             '<opf:item id="image2" href="BinData/image2.bmp" media-type="image/bmp" isEmbeded="1"/>']
    for f in figs:
        iid = imgmap[f]
        items.append(f'<opf:item id="{iid}" href="BinData/{iid}.png" media-type="image/png" isEmbeded="1"/>')
    items += ['<opf:item id="section0" href="Contents/section0.xml" media-type="application/xml"/>',
              '<opf:item id="settings" href="settings.xml" media-type="application/xml"/>']
    hpf = re.sub(r'<opf:manifest>.*?</opf:manifest>', '<opf:manifest>' + ''.join(items) + '</opf:manifest>', hpf, flags=re.S)
    prv = ' 「콘텐츠산업 진흥법 시행령」 제33조에 의한 표시 (1) 제작연월일 : ' + B.PROD_DATE + '\r\n\r\n' + \
          re.sub(r'\$', '', Q[0]['text']) + '\r\n'
    settings = zin.read('settings.xml').decode('utf8').replace('paraIDRef="241"', 'paraIDRef="0"')
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('RGB', (192, 272), 'white')
    dr = ImageDraw.Draw(im)
    try:
        ft = ImageFont.truetype('/Users/youngwoolee/.fonts/HCRBatang.ttf', 14)
    except Exception:
        ft = ImageFont.load_default()
    for i, t in enumerate([B.SCHOOL_TITLE, B.SCHOOL, B.COURSE, B.UNITS]):
        dr.text((12, 20 + i * 22), t, fill='black', font=ft)
    import io
    buf = io.BytesIO()
    im.save(buf, 'PNG')
    prv_img = buf.getvalue()

    out_path = os.path.join(B.OUTDIR, B.FILENAME_STEM + '.hwpx')
    zo = zipfile.ZipFile(out_path, 'w')

    def put(name, data, stored=False):
        zi = zipfile.ZipInfo(name, date_time=(2026, 9, 28, 12, 0, 0))
        zi.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
        zi.external_attr = 0o600 << 16
        zo.writestr(zi, data)
    put('mimetype', zin.read('mimetype'), True)
    put('version.xml', zin.read('version.xml'))
    put('Contents/header.xml', hdr.encode('utf8'))
    put('BinData/image1.bmp', zin.read('BinData/image1.bmp'))
    put('Contents/masterpage0.xml', zin.read('Contents/masterpage0.xml'))
    put('BinData/image2.bmp', zin.read('BinData/image2.bmp'))
    for f in figs:
        put(f'BinData/{imgmap[f]}.png', open(os.path.join(B.FIG, f + '.png'), 'rb').read(), True)
    put('Contents/section0.xml', section.encode('utf8'))
    put('Preview/PrvText.txt', prv.encode('utf8'))
    put('settings.xml', settings.encode('utf8'))
    put('Preview/PrvImage.png', prv_img, True)
    put('META-INF/container.rdf', zin.read('META-INF/container.rdf'))
    put('Contents/content.hpf', hpf.encode('utf8'))
    put('META-INF/container.xml', zin.read('META-INF/container.xml'))
    put('META-INF/manifest.xml', zin.read('META-INF/manifest.xml'))
    zo.close()
    return out_path, warns, info


if __name__ == '__main__':
    p, warns, info = build()
    print(p)
    for w in warns:
        print('WARN', w)
    for g in info:
        print(g)
