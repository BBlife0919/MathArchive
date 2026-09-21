import zipfile, re, glob, sys, collections
import xml.etree.ElementTree as ET
p=glob.glob(SP_OUT:= '/private/tmp/claude-501/-Users-youngwoolee-MathDB/b9f96fd3-de5c-47c5-a3dc-3c0c95f620a7/scratchpad/out/*.hwpx')[0]
z=zipfile.ZipFile(p)
s=z.read('Contents/section0.xml').decode('utf8')
root=ET.fromstring(s)
H='{http://www.hancom.co.kr/hwpml/2011/paragraph}'
issues=[]
# 1 tab inside t
for t in root.iter(H+'run'):
    for c in t:
        if c.tag==H+'tab': issues.append('tab directly in run')
for pp in root.iter(H+'p'):
    for r in pp.findall(H+'run'):
        for c in r:
            if c.tag==H+'tab': issues.append('tab in run')
# 2 ids
ids=collections.Counter()
for tag in ('equation','pic','tbl'):
    for e in root.iter(H+tag): ids[(tag,e.get('id'))]+=1
print('dup ids:',[k for k,v in ids.items() if v>1][:5])
zs=collections.Counter(e.get('zOrder') for tag in ('equation','pic','tbl') for e in root.iter(H+tag))
print('dup zOrder:',[k for k,v in zs.items() if v>1][:5])
print('max id',max(int(k[1]) for k in ids), 'int32 ok', max(int(k[1]) for k in ids)<2**31)
# 3 relations
REL=re.compile(r'!=|<=|>=|LEQ|GEQ|NEQ|=|<|>')
def depth0(sc):
    d=0; out=[]
    i=0
    while i<len(sc):
        c=sc[i]
        if c=='{': d+=1
        elif c=='}': d-=1
        out.append(c if d==0 else ' ')
        i+=1
    t=''.join(out)
    t=re.sub(r'left\(.*?right\)','',t)  # crude
    return t
bad=[]
for e in root.iter(H+'script'):
    sc=(e.text or '')
    d=depth0(sc)
    n=len(re.findall(r'!=|LEQ|GEQ|NEQ|=|<|>',d))
    if n>1: bad.append(('multi-rel',sc))
    if re.search(r'(=|LEQ|GEQ|NEQ)\s*-',sc): bad.append(('rel-minus',sc))
    if re.search(r'\brm\s+bar\b|rmbar',sc): bad.append(('rm bar',sc))
    if '$' in sc: bad.append(('dollar',sc))
    if re.search(r'\d(sin|cos|tan)',sc): bad.append(('num-func',sc))
    if re.search(r'[가-힣]',sc): bad.append(('hangul-in-eq',sc))
for b in bad[:20]: print('BAD',b)
print('bad count',len(bad))
# 4 digits in plain text (outside eq)
dig=[]
for t in root.iter(H+'t'):
    if t.text and re.search(r'\d',t.text): dig.append(t.text)
print('plain-text digits:',dig[:20])
# 5 answer symbols wrapped
print('정답 symbol runs w/o t:', len(re.findall(r'<hp:run charPrIDRef="12">[①-⑤]',s)))
print('endnotes',s.count('<hp:endNote '),'pics',s.count('<hp:pic '),'tbl',s.count('<hp:tbl '))
print('issues',issues[:5])
