import sys, zipfile, re
import xml.etree.ElementTree as ET
NS={'hp':'http://www.hancom.co.kr/hwpml/2011/paragraph','hs':'http://www.hancom.co.kr/hwpml/2011/section'}
def q(t): return '{%s}%s'%(NS['hp'],t)
def summ(p, depth=0):
    out=[]
    for r in p.iter(q('run')):
        pass
    parts=[]
    def walk(e):
        for c in e:
            tag=c.tag.split('}')[1]
            if tag=='t':
                txt=(c.text or '')
                sub=''.join(('<TAB%s>'%c2.get('width') if c2.tag.endswith('tab') else ('<BR>' if c2.tag.endswith('lineBreak') else (c2.text or ''))+ (c2.tail or '')) for c2 in c)
                parts.append('T(%s)'%(txt+sub))
            elif tag=='equation':
                parts.append('EQ[%s]'%c.find(q('script')).text)
            elif tag=='tbl': parts.append('<TBL>')
            elif tag=='rect': parts.append('<RECT>')
            elif tag=='pic': parts.append('<PIC>')
            elif tag=='ctrl':
                for cc in c:
                    t2=cc.tag.split('}')[1]
                    if t2=='endNote': parts.append('<ENDNOTE %s>'%cc.get('number'))
                    elif t2=='autoNum': parts.append('<AUTONUM>')
                    else: parts.append('<%s>'%t2)
            elif tag in('run',):
                parts.append('{cp%s'%c.get('charPrIDRef')); walk(c); parts.append('}')
    walk(p)
    return ''.join(parts)
if __name__=='__main__':
    z=zipfile.ZipFile(sys.argv[1]); s=z.read('Contents/section0.xml')
    root=ET.fromstring(s)
    lo=int(sys.argv[2]) if len(sys.argv)>2 else 0
    hi=int(sys.argv[3]) if len(sys.argv)>3 else 10**9
    for i,p in enumerate(root.findall(q('p'))):
        if lo<=i<hi:
            print(i,'pr%s'%p.get('paraPrIDRef'),'pb' if p.get('pageBreak')=='1' else '', 'cb' if p.get('columnBreak')=='1' else '', summ(p)[:600])
