from figlib import *
def make():
    O=P(0,0); r=1.0
    B=P(0,-1); C=P(1,0); A=P(np.cos(np.radians(120)),np.sin(np.radians(120)))
    T=P(1.02,-1)
    f=Fig('s1',13500,(-1.9,1.75),(-1.55,1.4))
    f.circle(O,r)
    f.poly([A,B,C])
    f.seg(P(-1.75,-1),P(1.6,-1))
    f.dot(O); f.lab('O',O,10,-1)
    f.dot(T,1.3)
    f.angle(B,C,T,0.32)
    f.lab('A',A,-6,6); f.lab('B',B,0,-9); f.lab('C',C,9,3); f.lab('T',T,0,-9)
    f.ngd_on(P(-1.75,-1),P(1.6,-1),0.15)
    return f.save()
if __name__=='__main__': print(make())
