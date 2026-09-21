from figlib import *
def make():
    r=1.0; d=r/np.sin(np.radians(20))
    O=P(0,0); A=P(r*np.cos(np.radians(70)), r*np.sin(np.radians(70))); B=P(A[0],-A[1]); Pp=P(d,0)
    f=Fig('q01', 14500, (-1.35, 3.45), (-1.75, 1.75))
    f.circle(O,r)
    ext=0.85
    uA=unit(A-Pp); uB=unit(B-Pp)
    f.seg(Pp,A+uA*ext); f.seg(Pp,B+uB*ext)
    f.seg(A,B)
    f.dot(O)
    f.lab('O',O,-8,-6)
    f.lab('A',A,4,8); f.lab('B',B,4,-9); f.lab('P',Pp,9,-1)
    f.angle(Pp,A,B,0.42,'40°',tr=0.95,dtext=(0,-1))
    f.angle(A,Pp,B,0.28)
    f.lab('x',A+P(0.13,-0.34),0,0,italic=True)
    f.ngd_on(Pp,A,0.62)   # 접선 PA(직선)와 나란히 겹침
    return f.save()
if __name__=='__main__': print(make())
