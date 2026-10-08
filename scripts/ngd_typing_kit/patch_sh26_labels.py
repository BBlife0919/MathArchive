# -*- coding: utf-8 -*-
"""사용자가 수정한 소하고 HWPX에서 [중단원]/[난이도] 라벨이 빠진 문항에 라벨 두 줄만 추가한다(다른 바이트는 그대로)."""
import zipfile, re, sys, shutil
sys.path.insert(0, '.')
from sh26_content import Q
U = sys.argv[1]
zin = zipfile.ZipFile(U)
s = zin.read('Contents/section0.xml').decode('utf8')
depth = 0; tops = []; st = None
for m in re.finditer(r'<hp:p[ >]|</hp:p>', s):
    if m.group().startswith('</'):
        depth -= 1
        if depth == 0:
            tops.append((st, m.end()))
    else:
        if depth == 0:
            st = m.start()
        depth += 1
def plain(p):
    t = re.sub(r'<hp:endNote.*?</hp:endNote>', 'EN', p, flags=re.S)
    t = re.sub(r'<hp:script>.*?</hp:script>', '', t, flags=re.S)
    t = re.sub(r'<hp:pic .*?</hp:pic>', 'PIC', t, flags=re.S)
    return re.sub(r'<[^>]+>', '', t).strip()
# 템플릿: 첫 [중단원] / [난이도] 문단
tpl_ch = tpl_lv = None
for a, b in tops:
    t = plain(s[a:b])
    if tpl_ch is None and t.startswith('[중단원]'): tpl_ch = s[a:b]
    if tpl_lv is None and t.startswith('[난이도]'): tpl_lv = s[a:b]
assert tpl_ch and tpl_lv
# 문항 시작 문단 인덱스(끝노트 번호)
en_idx = {}
for k, (a, b) in enumerate(tops):
    for n in re.findall(r'<hp:endNote number="(\d+)"', s[a:b]):
        en_idx[int(n)] = k
N = len(Q)
ins = []   # (문단 끝 위치, 삽입 xml)
for n in range(1, N + 1):
    k0 = en_idx[n]; k1 = en_idx[n + 1] if n + 1 <= N else len(tops)
    blk = [plain(s[a:b]) for a, b in tops[k0:k1]]
    if any(t.startswith('[중단원]') for t in blk):
        continue
    # 마지막 비어있지 않은 문단 뒤에 삽입
    last = max(i for i, t in enumerate(blk) if t)
    pos = tops[k0 + last][1]
    ch, lv = Q[n - 1]['ch'], Q[n - 1]['lv']
    x1 = re.sub(r'(<hp:t>)\[중단원\][^<]*(</hp:t>)', lambda m: f'{m.group(1)}[중단원] {ch}{m.group(2)}', tpl_ch, count=1)
    x2 = re.sub(r'(<hp:t>)\[난이도\][^<]*(</hp:t>)', lambda m: f'{m.group(1)}[난이도] {lv}{m.group(2)}', tpl_lv, count=1)
    ins.append((pos, x1 + x2, n, ch, lv))
for pos, x, n, ch, lv in sorted(ins, reverse=True):
    s = s[:pos] + x + s[pos:]
print('추가:', [(n, ch, lv) for _, _, n, ch, lv in sorted(ins, key=lambda t: t[2])])
tmp = U + '.tmp'
zo = zipfile.ZipFile(tmp, 'w')
for zi in zin.infolist():
    data = zin.read(zi.filename)
    if zi.filename == 'Contents/section0.xml':
        data = s.encode('utf8')
    ni = zipfile.ZipInfo(zi.filename, date_time=zi.date_time)
    ni.compress_type = zi.compress_type; ni.external_attr = zi.external_attr
    zo.writestr(ni, data)
zo.close(); shutil.move(tmp, U)
