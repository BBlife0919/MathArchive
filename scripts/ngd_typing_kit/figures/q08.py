from figx1 import *
def make():
    a=np.radians(18)
    Pp=P(0,0); C=P(-1,0)
    O=Pp+2*np.cos(a)*P(-np.cos(a),np.sin(a))
    B=P(O[0]-np.sqrt(1-O[1]**2),0)
    u=unit(Pp-O); A=O+u; D=O-u
    for X in (A,B,C,D): assert abs(np.hypot(*(X-O))-1)<1e-9
    assert abs(np.hypot(*(C-O))-np.hypot(*(C-Pp)))<1e-9
    f=Fig('q08',14000,(-3.3,0.5),(-0.7,1.75))
    f.circle(O,1.0)
    f.seg(D,Pp); f.seg(B,Pp); f.seg(O,B); f.seg(O,C)
    f.dot(O,1.4)
    f.ticks(O,C,n=2); f.ticks(C,Pp,n=2)
    f.angle(Pp,B,O,0.42)
    f.lab('18°',P(-0.30,0.24),0,0)     # 원본: P의 호 바로 위쪽 옆
    f.lab('O',O,0,9); f.lab('D',D,-8,4); f.lab('A',A,-3,11)
    f.lab('B',B,-8,-5); f.lab('C',C,3,-9); f.lab('P',Pp,9,-3)
    f.ngd_on(B,C,0.5)   # 수평 현 BC 위
    return f.save()
if __name__=='__main__': print(make())
