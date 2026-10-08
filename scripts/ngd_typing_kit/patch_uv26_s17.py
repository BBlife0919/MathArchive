# -*- coding: utf-8 -*-
"""사용자가 직접 수정한 운산고 HWPX에 17번 해설 그림(f(t) 그래프)만 추가하는 패치. 다른 바이트는 건드리지 않는다."""
import zipfile, re, sys, json, os, shutil
SP = os.path.dirname(os.path.abspath(__file__))
U = sys.argv[1]
info = json.load(open(os.path.join(SP, 'figures', 'png', 'uv26_s17.json')))
png = open(os.path.join(SP, 'figures', 'png', 'uv26_s17.png'), 'rb').read()
w, h = info['w_hwp'], info['h_hwp']
zin = zipfile.ZipFile(U)
s = zin.read('Contents/section0.xml').decode('utf8')
assert 'binaryItemIDRef="image4"' not in s, '이미 추가됨'
i = s.index('<hp:endNote number="17"'); j = s.index('</hp:endNote>', i)
blk = s[i:j]
paras = list(re.finditer(r'<hp:p .*?</hp:p>', blk, re.S))
anchor = paras[16]
assert '1&lt;t' in anchor.group() and 'f(t)=0' in anchor.group()
vp0 = int(re.search(r'vertpos="(\d+)"', anchor.group()).group(1))
LS = 'textpos="0" vertpos="{v}" vertsize="{h}" textheight="{h}" baseline="{b}" spacing="600" horzpos="0" horzsize="30188" flags="393216"'
def blank(v):
    return ('<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="1"/>'
            f'<hp:linesegarray><hp:lineseg {LS.format(v=v, h=1000, b=850)}/></hp:linesegarray></hp:p>')
ow, oh = w * 2, h * 2
pic = (f'<hp:p id="0" paraPrIDRef="1" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="1">'
       f'<hp:pic id="700000005" zOrder="9005" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="700000005" reverse="0">'
       f'<hp:offset x="0" y="0"/><hp:orgSz width="{ow}" height="{oh}"/><hp:curSz width="{w}" height="{h}"/><hp:flip horizontal="0" vertical="0"/>'
       f'<hp:rotationInfo angle="0" centerX="{w // 2}" centerY="{h // 2}" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
       f'<hc:scaMatrix e1="0.5" e2="0" e3="0" e4="0" e5="0.5" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo>'
       f'<hc:img binaryItemIDRef="image4" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/>'
       f'<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="{ow}" y="0"/><hc:pt2 x="{ow}" y="{oh}"/><hc:pt3 x="0" y="{oh}"/></hp:imgRect>'
       f'<hp:imgClip left="0" right="{ow}" top="0" bottom="{oh}"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="{ow}" dimheight="{oh}"/><hp:effects/>'
       f'<hp:sz width="{w}" widthRelTo="ABSOLUTE" height="{h}" heightRelTo="ABSOLUTE" protect="0"/>'
       f'<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
       f'<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:shapeComment>그림입니다.</hp:shapeComment></hp:pic><hp:t/></hp:run>'
       f'<hp:linesegarray><hp:lineseg {LS.format(v=vp0 + 1725 + 1600, h=h, b=int(h * 0.85))}/></hp:linesegarray></hp:p>')
v_blank1 = vp0 + 1725
v_blank2 = vp0 + 1725 + 1600 + h + 600
shift = 1600 + (h + 600) + 1600
ins = blank(v_blank1) + pic + blank(v_blank2)
# 뒤따르는 문단의 줄 위치(캐시) 이동 — 17번 해설 안에서만
tail = blk[anchor.end():]
tail = re.sub(r'vertpos="(\d+)"', lambda m: f'vertpos="{int(m.group(1)) + shift}"', tail)
new_blk = blk[:anchor.end()] + ins + tail
s2 = s[:i] + new_blk + s[j:]
hpf = zin.read('Contents/content.hpf').decode('utf8')
item3 = '<opf:item id="image3" href="BinData/image3.png" media-type="image/png" isEmbeded="1"/>'
assert item3 in hpf
hpf2 = hpf.replace(item3, item3 + '<opf:item id="image4" href="BinData/image4.png" media-type="image/png" isEmbeded="1"/>', 1)
tmp = U + '.tmp'
zo = zipfile.ZipFile(tmp, 'w')
for zi in zin.infolist():
    data = zin.read(zi.filename)
    if zi.filename == 'Contents/section0.xml':
        data = s2.encode('utf8')
    elif zi.filename == 'Contents/content.hpf':
        data = hpf2.encode('utf8')
    ni = zipfile.ZipInfo(zi.filename, date_time=zi.date_time)
    ni.compress_type = zi.compress_type
    ni.external_attr = zi.external_attr
    zo.writestr(ni, data)
    if zi.filename == 'BinData/image3.png':
        n4 = zipfile.ZipInfo('BinData/image4.png', date_time=zi.date_time)
        n4.compress_type = zipfile.ZIP_STORED
        n4.external_attr = zi.external_attr
        zo.writestr(n4, png)
zo.close()
shutil.move(tmp, U)
print('patched', U)
