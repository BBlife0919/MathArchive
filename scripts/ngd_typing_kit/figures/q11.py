from figlib import *
def pol(a): return P(np.cos(np.radians(a)),np.sin(np.radians(a)))
def make():
    O=P(0,0); A=pol(-150); B=pol(-120); C=pol(-60); D=pol(0)
    E=P(1.55,B[1])
    f=Fig('q11',13500,(-1.35,1.85),(-1.3,1.3))
    f.circle(O,1.0)
    f.seg(B,C,lw=LW)
    f.dashed(C,E)
    f.seg(A,B); f.seg(C,D); f.seg(D,A)
    f.dot(O,1.4); f.lab('O',O,0,10)
    f.dot(E,1.2)
    f.lab('A',A,-9,-2); f.lab('B',B,-2,-10); f.lab('C',C,3,-10); f.lab('D',D,10,3); f.lab('E',E,0,-10)
    f.angle(B,A,C,0.15,'x',italic=True)
    f.angle(C,D,E,0.15,'y',italic=True)
    f.ngd_on(A,D,0.5)   # 현 AD 위
    return f.save()
if __name__=='__main__': print(make())
