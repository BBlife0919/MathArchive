from figlib import *
def make():
    r=2.5
    T=P(0,0); O=P(0,r); Pp=P(-r*np.sqrt(3),0)
    u=unit(O-Pp); A=O-r*u; B=O+r*u
    f=Fig('s5',13500,(-5.4,3.6),(-2.0,6.1))
    f.circle(O,r)
    f.seg(Pp,B)
    f.seg(P(-4.75,0),P(3.2,0))
    f.seg(A,T)
    f.dot(O)
    f.dimarc_pt(A,B,+1,'5',pt=10)
    f.angle(T,Pp,A,0.9)
    f.lab('30°',P(-0.9,0),-6,-9,fs=8.5,ha='center')   # 좁은 각이라 호 바로 아래(선 밑)에 붙임(원본 위치)
    f.lab('P',Pp,-4,-11); f.lab('T',T,7,-9); f.lab('A',A,-9,3); f.lab('B',B,8,5); f.lab('O',O,9,-6)
    f.ngd_on(T,P(3.2,0),0.5)
    return f.save()
if __name__=='__main__': print(make())
