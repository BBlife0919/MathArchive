# -*- coding: utf-8 -*-
"""명문고 2학년 2026 2학기 중간 미적분Ⅰ HWPX 조립기 (2026-10-22).
골격: out/_skel_blank_ext.hwpx(양식지 기반) + std_build.py. 이 파일에서 추가로 처리하는 것:
  - 내어쓰기(ㄱㄴㄷ·(가)(나) 이어짐 줄): 새 paraPr 4(left 1450), 5(left 1870)를 헤더에 연속 id로 추가
  - 독립줄 수식 탭 들여쓰기('<<TAB>>' 접두), cases 수식 높이 보정
"""
import os, re, zipfile, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import std_build as S
from mm26_content import Q

B = S.B
B.Q = Q
S.Q = Q
B.COL_USABLE = 77000
B.MAX_PER = 2
B.IDS.z = 1000
B.SCHOOL_TITLE = '2026년 2학기 중간'
B.SCHOOL = '명문 고등학교'
B.COURSE = '미적분Ⅰ'
B.UNITS = '함수의 극한 ~ 함수의 그래프'
B.PROD_DATE = '2026년 10월 22일'
B.FILENAME_STEM = '[고][2026][2-2-a][경기광명시][명문고][미적분1][함수의극한-함수의그래프][그림3-0-3-0]'
B.DOC_TITLE = '2026년 2학기 중간 명문고등학교 2학년 함수의극한~함수의그래프'

HANG_BOGI = 1450   # "ㄱ. " 폭
HANG_COND = 1870   # "(가) " 폭

# ------------------------------------------------------------------ 파서 보강: 탭 들여쓰기 독립줄
_orig_parse_mix = B.parse_mix


def _parse_mix(s):
    if s.startswith('<<TAB>>'):
        return [('raw', B.tab_xml([4000]))] + _orig_parse_mix(s[len('<<TAB>>'):])
    return _orig_parse_mix(s)


B.parse_mix = _parse_mix

B._KW['inf'] = 1000   # ∞ 기호 폭(NGD 실작업 파일은 inf/INF 사용; infty 는 한글에서 키워드가 아님)
B._KW['INF'] = 1000

# ------------------------------------------------------------------ cases 수식 높이 보정(2행)
_orig_metrics = B.eq_metrics


def _metrics(script):
    if 'cases' in script:
        return (62, 4900) if re.search(r'\bover\b', script) else (65, 2600)
    return _orig_metrics(script)


B.eq_metrics = _metrics


# ------------------------------------------------------------------ 내어쓰기 줄바꿈
def hang_lines(items, hang, width):
    """첫 줄은 width, 이어지는 줄은 width-hang 로 줄바꿈. 반환: [(line_items, h, is_first)]"""
    l1 = B.flow_items(items, width=width)
    if len(l1) <= 1:
        return [(l1[0][0], l1[0][1], True)]
    rest = []
    for l, h in l1[1:]:
        rest += l
    l2 = B.flow_items(rest, width=width - hang)
    return [(l1[0][0], l1[0][1], True)] + [(l, h, False) for l, h in l2]


# ------------------------------------------------------------------ 해설(끝노트) — ㄱㄴㄷ 줄 내어쓰기 지원
_LAB = re.compile(r'^(ㄱ|ㄴ|ㄷ|ㄹ|ㅁ)\. ')


def endnote_xml(q, num, imgmap=None):
    inst = B.IDS.instid()
    paras = []
    vp = 0
    ans_runs = f'<hp:run charPrIDRef="12"><hp:t>{q["ans"]}</hp:t></hp:run>'
    head = (f'<hp:run charPrIDRef="9"><hp:ctrl><hp:autoNum num="{num}" numType="ENDNOTE"><hp:autoNumFormat type="DIGIT" '
            f'userChar="" prefixChar="" suffixChar="." supscript="0"/></hp:autoNum></hp:ctrl></hp:run>'
            f'<hp:run charPrIDRef="1"><hp:t> [정답] </hp:t></hp:run>{ans_runs}')
    paras.append(f'<hp:p id="2147483648" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">{head}'
                 f'{B.lineseg(vp, 1200)}</hp:p>')
    vp += B.pitch(1200)
    for line in q['sol']:
        if isinstance(line, dict):   # {'fig': 이름} = 해설 속 그림
            pp, ph = B.pic_para(line['fig'], imgmap[line['fig']])
            paras.append(pp)
            vp += B.pitch(ph)
            continue
        items = B.parse_mix(line)
        if _LAB.match(line):
            lines = hang_lines(items, HANG_BOGI, B.LINE_W)
        else:
            lines = [(l, h, True) for l, h in B.flow_items(items, width=B.LINE_W)]
        for litems, h, first in lines:
            pr = '0' if first else '4'
            paras.append(f'<hp:p id="0" paraPrIDRef="{pr}" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                         f'{B.runs_xml(litems)}{B.lineseg(vp, h)}</hp:p>')
            vp += B.pitch(h)
    xml = (f'<hp:ctrl><hp:endNote number="{num}" suffixChar="46" instId="{inst}"><hp:subList id="" textDirection="HORIZONTAL" '
           f'lineWrap="BREAK" vertAlign="TOP" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" '
           f'hasTextRef="0" hasNumRef="0">{"".join(paras)}</hp:subList></hp:endNote></hp:ctrl>')
    return xml, []


B.endnote_xml = endnote_xml


# ------------------------------------------------------------------ 보기틀 — 내어쓰기
def bogi_box(items):
    xml = B.BOX_SRC
    xml = re.sub(r'<hp:tbl id="\d+" zOrder="\d+"', lambda m: f'<hp:tbl id="{B.IDS.picid()}" zOrder="{B.IDS.zo()}"', xml)
    xml = re.sub(r'<hp:equation id="\d+" zOrder="\d+"', lambda m: f'<hp:equation id="{B.IDS.eqid()}" zOrder="{B.IDS.zo()}"', xml)
    marker_start = '<hp:p id="2147483648" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="1"><hp:t>ㄱ. </hp:t>'
    a = xml.index(marker_start)
    m3 = xml.index('<hp:t>ㄷ. </hp:t>')
    b = xml.index('</hp:p>', m3) + len('</hp:p>')
    labels = ['ㄱ. ', 'ㄴ. ', 'ㄷ. ', 'ㄹ. ', 'ㅁ. ']
    ps = []
    total_h = 0
    for lab, s in zip(labels, items):
        its = [('t', lab)] + B.parse_mix(s)
        for litems, h, first in hang_lines(its, HANG_BOGI, 27800):
            pr = '0' if first else '4'
            ps.append(f'<hp:p id="2147483648" paraPrIDRef="{pr}" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                      f'{B.runs_xml(litems)}{B.lineseg(0, h, 27800)}</hp:p>')
            total_h += B.pitch(h)
    xml = xml[:a] + ''.join(ps) + xml[b:]
    return xml, total_h


B.bogi_box = bogi_box


# ------------------------------------------------------------------ 조건틀 — 라벨 자동 + 내어쓰기('>> ' 이어짐 줄)
def cond_box(items, width=29437):
    W = width - 3400
    labs = ['(가) ', '(나) ', '(다) ', '(라) ']
    ps = []
    inner = 0
    li = 0
    for s in items:
        if s.startswith('>> '):
            its = B.parse_mix(s[3:])
            lines = [(l, h, False) for l, h in B.flow_items(its, width=W - HANG_COND)]
            # 이어짐 줄은 모두 내어쓰기 paraPr
        else:
            its = [('t', labs[li])] + B.parse_mix(s)
            li += 1
            lines = hang_lines(its, HANG_COND, W)
        for litems, h, first in lines:
            pr = '0' if first else '5'
            ps.append(B.para(B.runs_xml(litems), pr=pr, vertsize=h, horz=width - 1700))
            inner += B.pitch(h)
    height = max(inner + 1700 + 1418, 4000)
    rid, iid, zid = B.IDS.picid(), B.IDS.instid(), B.IDS.zo()
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


B.jogeon_box = cond_box


# ------------------------------------------------------------------ 헤더 후처리: paraPr 4, 5 (연속 id) 추가
def add_parapr(path):
    tmp = path + '.tmp'
    zin = zipfile.ZipFile(path)
    hdr = zin.read('Contents/header.xml').decode('utf8')
    m = re.search(r'<hh:paraPr id="0" .*?</hh:paraPr>', hdr, re.S)
    base = m.group()
    assert '<hh:paraProperties itemCnt="4">' in hdr
    new = ''
    for nid, left in ((4, HANG_BOGI), (5, HANG_COND)):
        x = base.replace('<hh:paraPr id="0"', f'<hh:paraPr id="{nid}"', 1)
        x = x.replace('<hc:left value="0" unit="HWPUNIT"/>', f'<hc:left value="{left}" unit="HWPUNIT"/>')
        assert x.count(f'value="{left}"') == 2
        new += x
    hdr = hdr.replace('</hh:paraProperties>', new + '</hh:paraProperties>', 1)
    hdr = hdr.replace('<hh:paraProperties itemCnt="4">', '<hh:paraProperties itemCnt="6">', 1)
    zo = zipfile.ZipFile(tmp, 'w')
    for zi in zin.infolist():
        data = zin.read(zi.filename)
        if zi.filename == 'Contents/header.xml':
            data = hdr.encode('utf8')
        n = zipfile.ZipInfo(zi.filename, date_time=zi.date_time)
        n.compress_type = zi.compress_type
        n.external_attr = zi.external_attr
        zo.writestr(n, data)
    zo.close()
    zin.close()
    shutil.move(tmp, path)


if __name__ == '__main__':
    p, warns, info = S.build()
    add_parapr(p)
    print(p)
    for w in warns:
        print('WARN', w)
    for g in info:
        print(g)
