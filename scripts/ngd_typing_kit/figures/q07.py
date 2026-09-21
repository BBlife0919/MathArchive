from figx1 import *
def inter(p1,d1,p2,d2):
    M=np.array([d1,-np.array(d2)]).T
    t=np.linalg.solve(M,np.subtract(p2,p1))
    return np.add(p1,t[0]*np.array(d1))
def make():
    O=P(0,0); A=P(-1,0); B=P(1,0)
    th=lambda d:P(np.cos(np.radians(d)),np.sin(np.radians(d)))
    D=th(128); E=th(72)                       # 호 DE = 56°
    C=inter(A,D-A,B,E-B)
    # 검산: ∠ACB = 62°, ∠DOE = 56°
    ca,cb=A-C,B-C
    angC=np.degrees(np.arccos(ca@cb/np.hypot(*ca)/np.hypot(*cb)))
    assert abs(angC-62)<0.01,angC
    f=Fig('q07',10300,(-1.28,1.28),(-1.1,1.95))
    f.circle(O,1.0)
    f.seg(A,B); f.seg(A,C); f.seg(B,C)
    f.seg(O,D); f.seg(O,E)
    f.angle(C,A,B,0.13,'62°',fs=7.5)
    f.angle(O,D,E,0.2,'x',italic=True)
    f.lab('C',C,0,8); f.lab('D',D,-8,5); f.lab('E',E,8,6)
    f.lab('A',A,-8,-4); f.lab('B',B,8,-4); f.lab('O',O,0,-9)
    f.ngd_on(P(-1,0),P(1,0),0.22)   # 지름 AB 위(선과 나란히)
    return f.save()
if __name__=='__main__': print(make())
