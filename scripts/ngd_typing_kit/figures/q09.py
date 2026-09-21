from figlib import *
def make():
    O=P(0,0); T=P(0,-1); Pp=P(-np.tan(np.radians(54)),-1)
    u=unit(-Pp); B=u; C=-u
    A=P(np.cos(np.radians(115)),np.sin(np.radians(115)))
    f=Fig('q09',13500,(-1.95,1.4),(-1.45,1.35))
    f.circle(O,1.0)
    f.seg(Pp,B); f.seg(Pp,T); f.seg(A,B); f.seg(A,T)
    f.dot(O,1.4)
    f.lab('O',O,9,-9)
    f.lab('A',A,-2,9); f.lab('B',B,9,4); f.lab('C',C,-9,4); f.lab('P',Pp,-9,-1); f.lab('T',T,0,-10)
    f.angle(A,B,T,0.24,'63°')
    f.angle(Pp,B,T,0.36,'x',italic=True)
    f.ngd_on(Pp,T,0.62)   # 접선 PT 위
    return f.save()
if __name__=='__main__': print(make())
