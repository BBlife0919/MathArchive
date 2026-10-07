# -*- coding: utf-8 -*-
"""소하고 2026 2학기 정기시험 1차(공통수학2) HWPX 조립기.
골격: 광명고 1-2-a(공수2) 완성본 clone(다른 과목이지만 같은 학교 계통 charPr/paraPr 재사용).
build.py의 저수준 헬퍼를 재사용하고, 단답형(다중 소문항) 문항만 이 파일에서 커스텀 처리한다.
"""
import os, re, zipfile, datetime
from xml.sax.saxutils import escape

os.environ.setdefault('NGD_SKELETON',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out',
                 '[고][2025][1-2-a][경기광명시][소하고][공수2][이차함수-집합][02054][그림]_신규.hwpx'))

import build as B
from sh26_content import Q

B.Q = Q
B.COL_USABLE = 77000
B.IDS.z = 1000   # 골격 첫 문단의 zOrder(592~595)와 겹치지 않게
B.SCHOOL_TITLE = '2026년 2학기 정기1차'
B.SCHOOL = '소하 고등학교'
B.COURSE = '공통수학2'
B.UNITS = '평면좌표 ~ 집합'
B.PROD_DATE = '2026년 09월 29일'
B.FILENAME_STEM = '[고][2026][1-2-a][경기광명시][소하고][공수2][평면좌표-집합][그림2-0-2-0]'
B.DOC_TITLE = '2026년 2학기 정기시험1차 소하고등학교 1학년 평면좌표~집합'


# ------------------------------------------------------------------ 라벨 없는 평문 박스(단답형3 조건)
def plain_box(items, width=29437):
    ps = []
    max_h = 1000
    for s in items:
        its = B.parse_mix(s)
        h = B.item_h(its)
        max_h = max(max_h, h)
        ps.append(B.para(B.runs_xml(its), pr='0', vertsize=h, horz=width - 1700))
    line_pitch = 3180 if max_h > 2000 else 1725
    height = len(items) * line_pitch + 1700 + 1418
    height = max(height, 4000)
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




def build_block_midtext(q, num, imgmap):
    """text -> fig -> mid_text(질문+배점) -> box -> choices 순서가 필요한 문항(Q14)용."""
    Bl = B.Block()
    en, w = B.endnote_xml(q, num)
    Bl.warns += [f'Q{q["id"]}: {x}' for x in w]
    items = B.parse_mix(q['text'])
    prefix_run = f'<hp:run charPrIDRef="1">{en}</hp:run>'
    body_paras, body_h = B.flow_paras(items, width=B.LINE_W, first_indent=1300, prefix_run=prefix_run)
    Bl.paras += body_paras
    Bl.h += body_h
    Bl.paras.append(B.blank())
    Bl.h += B.PITCH_BLANK
    if q.get('fig'):
        pp, h = B.pic_para(q['fig'], imgmap[q['fig']])
        Bl.paras.append(pp)
        Bl.h += h + 600
        Bl.paras.append(B.blank())
        Bl.h += B.PITCH_BLANK
    mid_paras, mid_h = B.flow_paras(q['mid_text'], width=B.LINE_W)
    Bl.paras += mid_paras
    Bl.h += mid_h
    Bl.paras.append(B.blank())
    Bl.h += B.PITCH_BLANK
    if q.get('box'):
        bx, bh = B.bogi_box(q['box_items'])
        Bl.paras.append(bx)
        Bl.h += bh + 1926 + 1100
        Bl.paras.append(B.blank())
        Bl.h += B.PITCH_BLANK
    if q['kind'] == 'mc':
        cx, ch, w2 = B.choices_xml(q)
        Bl.warns += [f'Q{q["id"]}: {x}' for x in w2]
        Bl.paras += cx
        Bl.h += sum(B.pitch(x) for x in ch)
    Bl.paras.append(B.para(B.runs_xml([('t', f'[중단원] {q["ch"]}')], '2')))
    Bl.paras.append(B.para(B.runs_xml([('t', f'[난이도] {q["lv"]}')], '2')))
    Bl.h += 2 * B.PITCH_BLANK
    return Bl


def build_block(q, num, imgmap):
    if q.get('mid_text'):
        return build_block_midtext(q, num, imgmap)
    if q['kind'] != 'short':
        return B.build_block(q, num, imgmap)
    Bl = B.Block()
    Bl.paras.append(B.para(B.runs_xml([('t', f'[서술형 {q["no"]}]')])))
    Bl.h += B.PITCH_BLANK
    en = endnote_short_xml(q, num)
    items = B.parse_mix(q['intro'])
    prefix_run = f'<hp:run charPrIDRef="1">{en}</hp:run>'
    body_paras, body_h = B.flow_paras(items, width=B.LINE_W, first_indent=1300, prefix_run=prefix_run)
    Bl.paras += body_paras
    Bl.h += body_h
    Bl.paras.append(B.blank())
    Bl.h += B.PITCH_BLANK
    if q.get('fig'):
        pp, h = B.pic_para(q['fig'], imgmap[q['fig']])
        Bl.paras.append(pp)
        Bl.h += h + 600
        Bl.paras.append(B.blank())
        Bl.h += B.PITCH_BLANK
    if q.get('jogeon_eq'):
        its = B.parse_mix(q['jogeon_eq'])
        ps, h = B.flow_paras(its, width=B.LINE_W, first_indent=1300)
        Bl.paras += ps
        Bl.h += h
        Bl.paras.append(B.blank())
        Bl.h += B.PITCH_BLANK
        its2 = B.parse_mix(q['intro2'])
        ps2, h2 = B.flow_paras(its2, width=B.LINE_W)
        Bl.paras += ps2
        Bl.h += h2
        Bl.paras.append(B.blank())
        Bl.h += B.PITCH_BLANK
    if q.get('box_items'):
        bx, bh = plain_box(q['box_items'])
        Bl.paras.append(bx)
        Bl.h += bh + 600
        Bl.paras.append(B.blank())
        Bl.h += B.PITCH_BLANK
        its3 = B.parse_mix(q['intro3'])
        ps3, h3 = B.flow_paras(its3, width=B.LINE_W)
        Bl.paras += ps3
        Bl.h += h3
        Bl.paras.append(B.blank())
        Bl.h += B.PITCH_BLANK
    for s in q['subs']:
        its = B.parse_mix(s['label'])
        ps, h = B.flow_paras(its, width=B.LINE_W)
        Bl.paras += ps
        Bl.h += h
        Bl.paras.append(B.blank())
        Bl.h += B.PITCH_BLANK
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
    for a, b in (('2025년 2학기 중간', B.SCHOOL_TITLE), ('소하 고등학교', B.SCHOOL), ('공통수학2', B.COURSE),
                 ('이차함수 ~ 집합', B.UNITS), ('2026년 09월 19일', B.PROD_DATE)):
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
    hpf = re.sub(r'<opf:title xml:space="preserve">.*?</opf:title>', f'<opf:title xml:space="preserve">{escape(B.DOC_TITLE)}</opf:title>', hpf)
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
