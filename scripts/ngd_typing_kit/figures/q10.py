from figlib import *
def pol(a): return P(np.cos(np.radians(a)),np.sin(np.radians(a)))
def make():
    O=P(0,0); C=pol(-90); D=pol(-26); A=pol(122); B=pol(190)
    d=D-A; t=(-1-D[1])/d[1]; Pp=D+t*d
    f=Fig('q10',15000,(-1.5,2.0),(-1.42,1.3))
    f.circle(O,1.0)
    f.seg(P(-1.3,-1),P(1.85,-1))
    f.seg(A,Pp); f.seg(A,B); f.seg(B,C); f.seg(A,C); f.seg(D,C)
    f.dot(O,1.4); f.lab('O',O,0,9)
    f.ticks(A,C,2,size=0.09,gap=0.055); f.ticks(A,D,2,size=0.09,gap=0.055)
    f.angle(B,A,C,0.16)
    f.angle(Pp,A,Pp+P(-1,0),0.3,'42°',tr=0.55,dtext=(0,-1),fs=8.5)
    f.lab('A',A,0,9); f.lab('B',B,-9,3); f.lab('C',C,0,-10); f.lab('D',D,9,3); f.lab('P',Pp,9,9)
    f.ngd_on(P(-1.3,-1),P(1.85,-1),0.16)   # 접선 위(선과 나란히)
    return f.save()
if __name__=='__main__': print(make())
