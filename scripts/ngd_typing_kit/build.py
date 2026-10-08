# -*- coding: utf-8 -*-
"""포산중 3-2 기말(2025) HWPX 조립기.
골격: 사용자 본인 제출본(광명고, 고등) 파일의 헤더·스타일·표 → 본문(section0 첫 문단 이후)만 새로 생성.
"""
import re, zipfile, json, os, sys, math, datetime
from xml.sax.saxutils import escape
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import Q

SP = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get('NGD_SKELETON', '/Users/youngwoolee/05_NGD/02_NGD 추가로 넣을거/[02054][고][2025][1-2-a][경기광명시][광명고][공수2][평면좌표-도형의이동][02054][그림4-0-4-0].hwpx')
FIG = os.path.join(SP, 'figures', 'png')
OUTDIR = os.path.join(SP, 'out')
os.makedirs(OUTDIR, exist_ok=True)

SCHOOL_TITLE = '2024년 2학기 중간'
SCHOOL = '명문고등학교'
COURSE = '2학년 수학Ⅱ'
UNITS = '함수의 극한 ~ 함수의 그래프'
PROD_DATE = '2026년 09월 19일'
FILENAME_STEM = '[고][2024][2-2-a][경기광명시][명문고][수2][함수의극한-함수의그래프][그림1]'
DOC_TITLE = '2024년 2학기 중간 명문고등학교 2학년 함수의극한~함수의그래프'

COL_W = 30188          # 단 폭(HWPUNIT)
LINE_W = 29000         # 줄바꿈 판정 폭(안전 여유)
PITCH_BLANK = 1600
PITCH_EQ = 1725

# ------------------------------------------------------------------ 폭 추정
_CH = {'(': 369, ')': 485, '+': 1052, ',': 291, '-': 1014, '.': 307, '=': 1174, ':': 350, '[': 400, ']': 400, '<': 1000, '>': 1000,
       '!': 400, '/': 500, '|': 300, "'": 250, '°': 500}
_UP = 880
_LOW = {'a': 623, 'b': 552, 'c': 529, 'd': 666, 'e': 635, 'f': 702, 'g': 595, 'h': 638, 'i': 380, 'j': 380, 'k': 630, 'l': 410,
        'm': 977, 'n': 735, 'o': 640, 'p': 620, 'q': 538, 'r': 466, 's': 556, 't': 471, 'u': 706, 'v': 650, 'w': 842, 'x': 677,
        'y': 629, 'z': 620}
_KW0 = {'rm', 'it', 'left', 'right', 'LEFT', 'RIGHT', 'bold', 'over', 'sqrt', 'bar', 'arch',
        'RM', 'IT', 'BAR'}
_KW = {'DEG': 800, 'angle': 800, 'ANGLE': 800, 'triangle': 900, 'TRIANGLE': 900, 'therefore': 1000, 'times': 1050, 'pi': 640,
       'prime': 250, 'sin': 1300, 'cos': 1350, 'tan': 1350, 'cdot': 400, 'div': 1050, 'nabla': 800,
       'THEREFORE': 1000, 'BECAUSE': 1000, 'LEQ': 1174, 'GEQ': 1174, 'NEQ': 1174, 'CIRC': 900,
       'SUBSET': 1174, 'EMPTYSET': 900, 'CAP': 900, 'cap': 900, 'CUP': 900, 'cup': 900,
       'IN': 900, 'SIM': 1000, 'TIMES': 1050, 'cot': 1350}
_TOK = re.compile(r'\{|\}|\^|_|~|`|[A-Za-z]+|\d+\.?\d*|.', re.S)


def _parse(tokens, i=0, until_close=False):
    nodes = []
    while i < len(tokens):
        t = tokens[i]
        if t == '{':
            sub, i = _parse(tokens, i + 1, True)
            nodes.append(('g', sub))
            continue
        if t == '}':
            return nodes, i + 1
        nodes.append(('t', t))
        i += 1
    return nodes, i


def _w(nodes):
    total = 0.0
    prev = 0.0
    i = 0
    n = len(nodes)
    ws = []
    while i < n:
        k, v = nodes[i]
        if k == 'g':
            ws.append(_w(v))
            i += 1
            continue
        t = v
        if t == 'over':
            nxt = 0.0
            if i + 1 < n:
                nk, nv = nodes[i + 1]
                nxt = _w(nv) if nk == 'g' else _atom(nv)
                i += 1
            p = ws.pop() if ws else 0.0
            ws.append(max(p, nxt) + 560)
            i += 1
            continue
        if t == 'sqrt':
            nxt = 0.0
            if i + 1 < n:
                nk, nv = nodes[i + 1]
                nxt = _w(nv) if nk == 'g' else _atom(nv)
                i += 1
            ws.append(nxt + 870)
            i += 1
            continue
        if t in ('bar',):
            i += 1
            continue
        if t in ('^', '_'):
            nxt = 0.0
            if i + 1 < n:
                nk, nv = nodes[i + 1]
                nxt = _w(nv) if nk == 'g' else _atom(nv)
                i += 1
            ws.append(nxt * 0.7)
            i += 1
            continue
        ws.append(_atom(t))
        i += 1
    return sum(ws)


def _atom(t):
    if t in _KW0:
        return 0
    if t in _KW:
        return _KW[t]
    if t == '~':
        return 500
    if t == '`':
        return 130
    if t == ' ' or t == '\n':
        return 0
    if re.fullmatch(r'\d+\.?\d*', t):
        return sum(307 if c == '.' else 570 for c in t)
    if re.fullmatch(r'[A-Za-z]+', t):
        return sum(_UP if c.isupper() else _LOW.get(c, 600) for c in t)
    return _CH.get(t, 700)


def eqw(script):
    nodes, _ = _parse([t for t in _TOK.findall(script) if t not in (' ', '\n', '\r', '\t')])
    return int(math.ceil((_w(nodes) - 80) / 10.0) * 10)


def eq_metrics(script):
    has_over = bool(re.search(r'\bover\b', script))
    has_sqrt = 'sqrt' in script
    has_sup = '^' in script
    if has_over:
        return (62, 2736) if has_sqrt else (65, 2580)
    if has_sqrt and has_sup:
        return (88, 1478)
    if has_sqrt:
        return (87, 1290)
    if has_sup:
        return (87, 1313)
    if re.search(r'\bbar\b', script):
        return (87, 1350)
    return (85, 1125)


def tw(s):
    """일반 텍스트 폭(10pt 나눔고딕 근사)."""
    w = 0
    for c in s:
        o = ord(c)
        if c == ' ':
            w += 260
        elif c.isdigit() or c.isascii() and c.isalpha():
            w += 520
        elif c in '.,':
            w += 260
        elif c in '()[]':
            w += 340
        elif c in '?!:':
            w += 400
        elif 0xAC00 <= o <= 0xD7A3 or 0x3130 <= o <= 0x318F:
            w += 930
        elif 0x2460 <= o <= 0x2473:
            w += 1000
        else:
            w += 800
    return w


# ------------------------------------------------------------------ 마크업 파싱
def parse_mix(s):
    items = []
    for part in re.split(r'(\$[^$]*\$)', s):
        if not part:
            continue
        if part.startswith('$') and part.endswith('$') and len(part) >= 2:
            items.append(('eq', part[1:-1]))
        else:
            for sub in re.split(r'(\[\[.*?\]\])', part):
                if sub.startswith('[[') and sub.endswith(']]'):
                    items.append(('u', sub[2:-2]))
                elif sub:
                    items.append(('t', sub))
    return items


class Ids:
    def __init__(self):
        self.eq = 900000000
        self.z = 100
        self.pic = 700000000
        self.inst = 90000

    def eqid(self):
        self.eq += 1
        return self.eq

    def zo(self):
        self.z += 1
        return self.z

    def picid(self):
        self.pic += 1
        return self.pic

    def instid(self):
        self.inst += 1
        return self.inst


IDS = Ids()


def eq_xml(script, height_override=None):
    bl, h = eq_metrics(script)
    if height_override:
        h = height_override
    w = eqw(script)
    return (f'<hp:equation id="{IDS.eqid()}" zOrder="{IDS.zo()}" numberingType="EQUATION" textWrap="TOP_AND_BOTTOM" '
            f'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" version="Equation Version 60" baseLine="{bl}" '
            f'textColor="#000000" baseUnit="1100" lineMode="CHAR" font="HYhwpEQ">'
            f'<hp:sz width="{w}" widthRelTo="ABSOLUTE" height="{h}" heightRelTo="ABSOLUTE" protect="0"/>'
            f'<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" '
            f'vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
            f'<hp:outMargin left="56" right="56" top="0" bottom="0"/><hp:shapeComment>수식입니다.</hp:shapeComment>'
            f'<hp:script>{escape(script)}</hp:script></hp:equation>')


def t_xml(text):
    return f'<hp:t>{escape(text)}</hp:t>'


def tab_xml(widths):
    return '<hp:t>' + ''.join(f'<hp:tab width="{w}" leader="0" type="1"/>' for w in widths) + '</hp:t>'


def runs_xml(items, cp='1'):
    """items: ('t',text) ('eq',script) ('u',text) ('raw',xml). 밑줄은 charPr 14 런으로 분리."""
    out = []
    cur = []
    curcp = cp

    def flush():
        if cur:
            out.append(f'<hp:run charPrIDRef="{curcp}">{"".join(cur)}</hp:run>')
            cur.clear()
    for k, v in items:
        if k == 'u':
            flush()
            out.append(f'<hp:run charPrIDRef="14">{t_xml(v)}</hp:run>')
        elif k == 't':
            cur.append(t_xml(v))
        elif k == 'eq':
            cur.append(eq_xml(v))
        elif k == 'raw':
            cur.append(v)
    flush()
    return ''.join(out)


def item_w(items):
    w = 0
    for k, v in items:
        if k in ('t', 'u'):
            w += tw(v)
        elif k == 'eq':
            w += eqw(v) + 112
    return w


def item_h(items):
    h = 1000
    for k, v in items:
        if k == 'eq':
            h = max(h, eq_metrics(v)[1])
    return h


def pitch(h):
    return h + 600


def sim_lines(items, first_indent=0, width=LINE_W):
    """어절 단위 줄바꿈 시뮬레이션 → 각 줄의 최대 높이 리스트."""
    # 어절 분해: 공백 기준, 수식은 인접 글자에 붙는 하나의 어절
    words = []  # (width, height, trailing_space_w)
    cur_w, cur_h = 0, 1000
    for k, v in items:
        if k in ('t', 'u'):
            for ch in re.split(r'( )', v):
                if ch == ' ':
                    words.append((cur_w, cur_h, 260))
                    cur_w, cur_h = 0, 1000
                elif ch:
                    cur_w += tw(ch)
        elif k == 'eq':
            cur_w += eqw(v) + 112
            cur_h = max(cur_h, eq_metrics(v)[1])
    words.append((cur_w, cur_h, 0))
    lines = []
    x = first_indent
    lh = 1000
    for (w, h, sp) in words:
        if x + w > width and x > first_indent:
            lines.append(lh)
            x, lh = 0, 1000
        x += w + sp
        lh = max(lh, h)
    lines.append(lh)
    return lines


def flow_items(items, width=LINE_W, first_indent=0):
    """items를 어절 단위로 줄바꿈하여 (line_items, height) 리스트로 재구성.
    한 <hp:p>에 여러 줄을 몰아넣지 않기 위해(2026-09-14 오버랩 버그 방지),
    실제 물리적 줄 단위로 쪼개서 반환한다."""
    words = []  # (word_items, word_width, trailing_space_bool)
    cur, cur_w = [], 0
    for k, v in items:
        if k in ('t', 'u'):
            for ch in re.split(r'( )', v):
                if ch == ' ':
                    words.append((cur, cur_w, True))
                    cur, cur_w = [], 0
                elif ch:
                    cur.append((k, ch))
                    cur_w += tw(ch)
        elif k == 'eq':
            cur.append((k, v))
            cur_w += eqw(v) + 112
        elif k == 'raw':
            cur.append((k, v))
    words.append((cur, cur_w, False))
    lines = []
    curline, curx, curh = [], 0, 1000
    line_no = 0
    for w_items, w_w, has_space in words:
        if not w_items:
            continue
        limit = width - (first_indent if line_no == 0 else 0)
        if curx > 0 and curx + w_w > limit:
            lines.append((curline, curh))
            curline, curx, curh = [], 0, 1000
            line_no += 1
        curline = curline + w_items
        curx += w_w
        for k, v in w_items:
            if k == 'eq':
                curh = max(curh, eq_metrics(v)[1])
        if has_space:
            curline.append(('t', ' '))
            curx += 260
    if curline:
        lines.append((curline, curh))
    if not lines:
        lines = [([], 1000)]
    return lines


def flow_paras(items, width=LINE_W, first_indent=0, pr='0', prefix_run=''):
    """items(또는 마크업 문자열)를 물리적 줄 단위 <hp:p> 리스트로 렌더링.
    반환: (paras_xml_list, total_height)"""
    if isinstance(items, str):
        items = parse_mix(items)
    lines = flow_items(items, width=width, first_indent=first_indent)
    paras = []
    total = 0
    for i, (litems, h) in enumerate(lines):
        runs = (prefix_run if i == 0 else '') + runs_xml(litems)
        paras.append(para(runs, pr=pr, vertsize=h))
        total += pitch(h)
    return paras, total


# ------------------------------------------------------------------ 문단
def lineseg(vertpos=0, vertsize=1000, horz=COL_W):
    bl = int(vertsize * 0.85)
    return (f'<hp:linesegarray><hp:lineseg textpos="0" vertpos="{vertpos}" vertsize="{vertsize}" textheight="{vertsize}" '
            f'baseline="{bl}" spacing="600" horzpos="0" horzsize="{horz}" flags="393216"/></hp:linesegarray>')


def para(runs, pr='0', pid='0', cb=0, pb=0, vertpos=0, vertsize=1000, horz=COL_W):
    return (f'<hp:p id="{pid}" paraPrIDRef="{pr}" styleIDRef="0" pageBreak="{pb}" columnBreak="{cb}" merged="0">'
            f'{runs}{lineseg(vertpos, vertsize, horz)}</hp:p>')


def blank(cb=0, cp='1'):
    return para(f'<hp:run charPrIDRef="{cp}"/>', cb=cb)


# ------------------------------------------------------------------ 해설(끝노트)
def endnote_xml(q, num):
    inst = IDS.instid()
    paras = []
    vp = 0
    # [정답] 문단
    if q['kind'] == 'mc':
        ans_runs = f'<hp:run charPrIDRef="12"><hp:t>{q["ans"]}</hp:t></hp:run>'
        aw = 1000
    else:
        if 'ans_mix' in q:
            items = parse_mix(q['ans_mix'])
            ans_runs = runs_xml(items, '12')
            aw = item_w(items)
        else:
            ans_runs = f'<hp:run charPrIDRef="12">{eq_xml(q["ans_eq"])}</hp:run>'
            aw = eqw(q['ans_eq']) + 112
        # 정답 줄이 길면 경고
    head = (f'<hp:run charPrIDRef="9"><hp:ctrl><hp:autoNum num="{num}" numType="ENDNOTE"><hp:autoNumFormat type="DIGIT" '
            f'userChar="" prefixChar="" suffixChar="." supscript="0"/></hp:autoNum></hp:ctrl></hp:run>'
            f'<hp:run charPrIDRef="1"><hp:t> [정답] </hp:t></hp:run>{ans_runs}')
    h0 = 1200 if q['kind'] == 'mc' else max(1200, item_h(parse_mix(q.get('ans_mix', '$' + q.get('ans_eq', '1') + '$'))))
    paras.append(f'<hp:p id="2147483648" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">{head}'
                 f'{lineseg(vp, h0)}</hp:p>')
    vp += pitch(h0)
    warns = []
    if 1400 + aw > LINE_W:
        warns.append(f'정답줄 폭 초과 추정 {1400 + aw}')
    for line in q['sol']:
        items = parse_mix(line)
        for litems, h in flow_items(items, width=LINE_W):
            paras.append(f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                         f'{runs_xml(litems)}{lineseg(vp, h)}</hp:p>')
            vp += pitch(h)
    xml = (f'<hp:ctrl><hp:endNote number="{num}" suffixChar="46" instId="{inst}"><hp:subList id="" textDirection="HORIZONTAL" '
           f'lineWrap="BREAK" vertAlign="TOP" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" '
           f'hasTextRef="0" hasNumRef="0">{"".join(paras)}</hp:subList></hp:endNote></hp:ctrl>')
    return xml, warns


# ------------------------------------------------------------------ 선지 배치
CIRC = ['①', '②', '③', '④', '⑤']
LABEL_W = 1368


def next4000(x):
    return (int(x) // 4000 + 1) * 4000


def choice_rows(q):
    lay = q['layout']
    n = len(q['choices'])
    if lay == '3+2':
        return [[0, 1, 2], [3, 4]]
    if lay == '2+2+1':
        return [[0, 1], [2, 3], [4]]
    if lay == '1x5':
        return [[i] for i in range(n)]
    raise ValueError(lay)


def choices_xml(q):
    warns = []
    lay = q['layout']
    rows = choice_rows(q)
    xmls, heights = [], []
    for row in rows:
        items_all = []
        pos = 0
        rh = 1000
        for ci, idx in enumerate(row):
            it = parse_mix(q['choices'][idx])
            w = LABEL_W + item_w(it)
            items_all.append(('t', CIRC[idx] + ' '))
            items_all.extend(it)
            rh = max(rh, item_h(it))
            x = pos + w
            if ci < len(row) - 1:
                if lay == '3+2':
                    target = (int(pos) // 12000 + 1) * 12000
                    while x >= target - 300:
                        target += 12000
                    first = next4000(x) - x
                    tabs = [first]
                    p = next4000(x)
                    while p < target:
                        tabs.append(4000)
                        p += 4000
                    pos = target
                else:  # 2+2+1 특수: 탭 정확히 3개
                    p1 = next4000(x)
                    tabs = [p1 - x, 4000, 4000]
                    pos = p1 + 8000
                items_all.append(('raw', tab_xml(tabs)))
            else:
                pos = x
        if pos > COL_W - 200:
            warns.append(f'선지 줄 폭 초과 {int(pos)} (layout {lay})')
        heights.append(rh)
        xmls.append(para(runs_xml(items_all), vertsize=1000))
    return xmls, heights, warns


# ------------------------------------------------------------------ 그림
def pic_xml(figname, imgid):
    info = json.load(open(os.path.join(FIG, f'{figname}.json')))
    w, h = info['w_hwp'], info['h_hwp']
    ow, oh = w * 2, h * 2
    pid = IDS.picid()
    return (f'<hp:pic id="{pid}" zOrder="{IDS.zo()}" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" '
            f'lock="0" dropcapstyle="None" href="" groupLevel="0" instid="{pid}" reverse="0"><hp:offset x="0" y="0"/>'
            f'<hp:orgSz width="{ow}" height="{oh}"/><hp:curSz width="{w}" height="{h}"/><hp:flip horizontal="0" vertical="0"/>'
            f'<hp:rotationInfo angle="0" centerX="{w // 2}" centerY="{h // 2}" rotateimage="1"/><hp:renderingInfo>'
            f'<hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:scaMatrix e1="0.5" e2="0" e3="0" e4="0" e5="0.5" e6="0"/>'
            f'<hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo>'
            f'<hc:img binaryItemIDRef="{imgid}" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/>'
            f'<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="{ow}" y="0"/><hc:pt2 x="{ow}" y="{oh}"/><hc:pt3 x="0" y="{oh}"/></hp:imgRect>'
            f'<hp:imgClip left="0" right="{ow}" top="0" bottom="{oh}"/><hp:inMargin left="0" right="0" top="0" bottom="0"/>'
            f'<hp:imgDim dimwidth="{ow}" dimheight="{oh}"/><hp:effects/>'
            f'<hp:sz width="{w}" widthRelTo="ABSOLUTE" height="{h}" heightRelTo="ABSOLUTE" protect="0"/>'
            f'<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" '
            f'horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
            f'<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:shapeComment>그림입니다.</hp:shapeComment></hp:pic>'), h


def pic_para(figname, imgid):
    px, h = pic_xml(figname, imgid)
    return (f'<hp:p id="2147483648" paraPrIDRef="1" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            f'<hp:run charPrIDRef="1">{px}<hp:t/></hp:run>{lineseg(0, h)}</hp:p>'), h


# ------------------------------------------------------------------ 보기 박스(사용자 제출본 clone)
BOX_SRC = open(os.path.join(SP, 'bogi_box_user.xml'), encoding='utf8').read()


def bogi_box(items):
    xml = BOX_SRC
    # id 재부여
    xml = re.sub(r'<hp:tbl id="\d+" zOrder="\d+"', lambda m: f'<hp:tbl id="{IDS.picid()}" zOrder="{IDS.zo()}"', xml)
    xml = re.sub(r'<hp:equation id="\d+" zOrder="\d+"', lambda m: f'<hp:equation id="{IDS.eqid()}" zOrder="{IDS.zo()}"', xml)
    marker_start = '<hp:p id="2147483648" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="1"><hp:t>ㄱ. </hp:t>'
    a = xml.index(marker_start)
    m3 = xml.index('<hp:t>ㄷ. </hp:t>')
    b = xml.index('</hp:p>', m3) + len('</hp:p>')
    labels = ['ㄱ. ', 'ㄴ. ', 'ㄷ. ']
    ps = []
    total_h = 0
    for lab, s in zip(labels, items):
        its = [('t', lab)] + parse_mix(s)
        for litems, h in flow_items(its, width=27800):
            ps.append(f'<hp:p id="2147483648" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                      f'{runs_xml(litems)}{lineseg(0, h, 27800)}</hp:p>')
            total_h += pitch(h)
    xml = xml[:a] + ''.join(ps) + xml[b:]
    return xml, total_h


# ------------------------------------------------------------------ 조건틀(NGD 매뉴얼 hp:rect clone)
JOGEON_RAW = open(os.path.join(SP, 'jogeon_box_manual.xml'), encoding='utf8').read()
_JG_I = JOGEON_RAW.find('<hp:p ')
_JG_J = JOGEON_RAW.rfind('</hp:p>') + len('</hp:p>')
JOGEON_HEAD = JOGEON_RAW[:_JG_I]
JOGEON_TAIL = JOGEON_RAW[_JG_J:]
JOGEON_LABELS = ['(가) ', '(나) ', '(다) ', '(라) ']


def jogeon_box(items, width=29437):
    ps = []
    max_h = 1000
    for lab, s in zip(JOGEON_LABELS, items):
        its = [('t', lab)] + parse_mix(s)
        h = item_h(its)
        max_h = max(max_h, h)
        ps.append(para(runs_xml(its), pr='0', vertsize=h, horz=width - 1700))
    line_pitch = 3180 if max_h > 2000 else 1725
    height = len(items) * line_pitch + 1700 + 1418
    height = max(height, 4000)
    rid = IDS.picid()
    iid = IDS.instid()
    zid = IDS.zo()
    head = JOGEON_HEAD.replace('id="1159475994"', f'id="{rid}"', 1)
    head = head.replace('zOrder="1" numberingType', f'zOrder="{zid}" numberingType', 1)
    head = head.replace('instid="85734171"', f'instid="{iid}"', 1)
    head = head.replace('<hp:orgSz width="28644" height="12587"/>', f'<hp:orgSz width="{width}" height="{height}"/>')
    head = head.replace('<hp:curSz width="29437" height="11450"/>', f'<hp:curSz width="{width}" height="{height}"/>')
    head = head.replace('<hc:scaMatrix e1="1.027685" e2="0" e3="0" e4="0" e5="0.909669" e6="0"/>',
                         '<hc:scaMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>')
    tail = JOGEON_TAIL.replace(
        '<hc:pt1 x="28644" y="0"/><hc:pt2 x="28644" y="12587"/><hc:pt3 x="0" y="12587"/>',
        f'<hc:pt1 x="{width}" y="0"/><hc:pt2 x="{width}" y="{height}"/><hc:pt3 x="0" y="{height}"/>')
    tail = tail.replace('<hp:sz width="29437" widthRelTo="ABSOLUTE" height="6468" heightRelTo="ABSOLUTE" protect="0"/>',
                         f'<hp:sz width="{width}" widthRelTo="ABSOLUTE" height="{height}" heightRelTo="ABSOLUTE" protect="0"/>')
    box_xml = head + ''.join(ps) + tail
    p = (f'<hp:p id="2147483648" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
         f'<hp:run charPrIDRef="1">{box_xml}<hp:t/></hp:run>{lineseg(0, height)}</hp:p>')
    return p, height


# ------------------------------------------------------------------ 문항 블록
class Block:
    def __init__(self):
        self.paras = []      # 본문 문단 XML
        self.h = 0           # 예상 높이
        self.warns = []


def build_block(q, num, imgmap):
    B = Block()
    # 서술형 라벨
    if q['kind'] == 'sub':
        B.paras.append(para(runs_xml([('t', f'[서술형 {q["no"]}]')])))
        B.h += PITCH_BLANK
    # 문제 본문
    en, w = endnote_xml(q, num)
    B.warns += [f'Q{q["id"]}: {x}' for x in w]
    items = parse_mix(q['text'])
    prefix_run = f'<hp:run charPrIDRef="1">{en}</hp:run>'
    body_paras, body_h = flow_paras(items, width=LINE_W, first_indent=1300, prefix_run=prefix_run)
    B.paras += body_paras
    B.h += body_h
    B.h_lines = len(body_paras)
    B.paras.append(blank())
    B.h += PITCH_BLANK
    if q.get('fig'):
        pp, h = pic_para(q['fig'], imgmap[q['fig']])
        B.paras.append(pp)
        B.h += h + 600
        B.paras.append(blank())
        B.h += PITCH_BLANK
    if q.get('box'):
        bx, bh = bogi_box(q['box_items'])
        B.paras.append(bx)
        B.h += bh + 1926 + 1100
        B.paras.append(blank())
        B.h += PITCH_BLANK
    if q.get('jogeon'):
        jx, jh = jogeon_box(q['jogeon_items'])
        B.paras.append(jx)
        B.h += jh + 600
        B.paras.append(blank())
        B.h += PITCH_BLANK
        if q.get('text2'):
            text2_paras, text2_h = flow_paras(q['text2'], width=LINE_W)
            B.paras += text2_paras
            B.h += text2_h
            B.paras.append(blank())
            B.h += PITCH_BLANK
    if q['kind'] == 'mc':
        cx, ch, w = choices_xml(q)
        B.warns += [f'Q{q["id"]}: {x}' for x in w]
        B.paras += cx
        B.h += sum(pitch(x) for x in ch)
    # 단원/난이도
    B.paras.append(para(runs_xml([('t', f'[중단원] {q["ch"]}')], '2')))
    B.paras.append(para(runs_xml([('t', f'[난이도] {q["lv"]}')], '2')))
    B.h += 2 * PITCH_BLANK
    return B


# ------------------------------------------------------------------ 단 배치
COL_USABLE = 80000
MAX_PER = 3             # 한 단 최대 문항 수(고등부는 2)
FIRST_OFFSET = 11100
MIN_GAP = 2


def layout(blocks):
    """반환: (문단 리스트, 그룹 정보). 단당 최대 3문항, 문항 사이 동분할 패딩."""
    groups = []
    i = 0
    first = True
    while i < len(blocks):
        cap = COL_USABLE - (FIRST_OFFSET if first else 0) - PITCH_BLANK  # 맨위 빈 줄 1
        n = 0
        tot = 0
        for k in range(MAX_PER):
            if i + k >= len(blocks):
                break
            need = tot + blocks[i + k].h + (MIN_GAP * PITCH_BLANK if k else 0)
            if need <= cap:
                tot = need
                n += 1
            else:
                break
        if n == 0:
            n = 1
            tot = blocks[i].h
        groups.append((list(range(i, i + n)), cap, first))
        i += n
        first = False
    out = []
    info = []
    for gi, (idxs, cap, first) in enumerate(groups):
        if first:
            out.append(blank())
        else:
            out.append(blank(cb=1))
        y = 0
        n = len(idxs)
        hs = [blocks[k].h for k in idxs]
        pads = []
        for j, k in enumerate(idxs):
            out += blocks[k].paras
            y += blocks[k].h
            if j < n - 1:
                target = cap * (j + 1) / n
                desired = round((target - y) / PITCH_BLANK)
                rest = sum(hs[j + 1:]) + (n - j - 2) * MIN_GAP * PITCH_BLANK
                safe = (cap - y - rest) // PITCH_BLANK
                pad = max(MIN_GAP, min(desired, safe))
                pads.append(pad)
                out += [blank() for _ in range(pad)]
                y += pad * PITCH_BLANK
        info.append(dict(qs=[Q[k]['id'] for k in idxs], used=y, cap=cap, pads=pads, hs=hs))
    return out, info


# ------------------------------------------------------------------ 패키징
def build():
    zin = zipfile.ZipFile(SRC)
    sec = zin.read('Contents/section0.xml').decode('utf8')
    # 첫 문단(secPr 포함) 경계
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
    # 헤더 표/제작일 치환
    for a, b in (('2025년 2학기 중간', SCHOOL_TITLE), ('광명 고등학교', SCHOOL), ('공통수학2', COURSE),
                 ('평면좌표 ~ 도형의 이동', UNITS), ('2026년 05월 29일', PROD_DATE)):
        assert a in prefix, a
        prefix = prefix.replace(a, b, 1)
    # 그림 id 매핑
    figs = []
    for q in Q:
        if q.get('fig'):
            figs.append(q['fig'])
    imgmap = {f: f'image{3 + i}' for i, f in enumerate(figs)}
    blocks = []
    warns = []
    for n, q in enumerate(Q, start=1):
        b = build_block(q, n, imgmap)
        blocks.append(b)
        warns += b.warns
    body, info = layout(blocks)
    tail = blank(cb=1)   # 끝노트를 새 단에서 시작
    section = prefix + ''.join(body) + tail + '</hs:sec>'
    # 이 시점에 lineseg 첫 문단 재사용 없음
    # header.xml: 밑줄 charPr(14) 추가
    hdr = zin.read('Contents/header.xml').decode('utf8')
    m = re.search(r'<hh:charPr id="1" .*?</hh:charPr>', hdr, re.S)
    new_cp = m.group().replace('id="1"', 'id="14"', 1).replace('<hh:underline type="NONE"', '<hh:underline type="BOTTOM"')
    hdr = hdr.replace('</hh:charProperties>', new_cp + '</hh:charProperties>', 1)
    hdr = hdr.replace('<hh:charProperties itemCnt="14">', '<hh:charProperties itemCnt="15">', 1)
    assert 'itemCnt="15"' in hdr
    # content.hpf
    hpf = zin.read('Contents/content.hpf').decode('utf8')
    hpf = re.sub(r'<opf:title xml:space="preserve">.*?</opf:title>', f'<opf:title xml:space="preserve">{escape(DOC_TITLE)}</opf:title>', hpf)
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
    # 미리보기 텍스트
    prv = ' 「콘텐츠산업 진흥법 시행령」 제33조에 의한 표시 (1) 제작연월일 : ' + PROD_DATE + '\r\n\r\n' + \
          re.sub(r'\$', '', Q[0]['text']) + '\r\n'
    settings = zin.read('settings.xml').decode('utf8').replace('paraIDRef="241"', 'paraIDRef="0"')
    # 미리보기 이미지(간단)
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('RGB', (192, 272), 'white')
    dr = ImageDraw.Draw(im)
    try:
        ft = ImageFont.truetype('/Users/youngwoolee/.fonts/HCRBatang.ttf', 14)
    except Exception:
        ft = ImageFont.load_default()
    for i, t in enumerate([SCHOOL_TITLE, SCHOOL, COURSE, UNITS]):
        dr.text((12, 20 + i * 22), t, fill='black', font=ft)
    import io
    buf = io.BytesIO()
    im.save(buf, 'PNG')
    prv_img = buf.getvalue()

    out_path = os.path.join(OUTDIR, FILENAME_STEM + '.hwpx')
    zo = zipfile.ZipFile(out_path, 'w')
    def put(name, data, stored=False):
        zi = zipfile.ZipInfo(name, date_time=(2026, 9, 21, 12, 0, 0))
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
        put(f'BinData/{imgmap[f]}.png', open(os.path.join(FIG, f + '.png'), 'rb').read(), True)
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
