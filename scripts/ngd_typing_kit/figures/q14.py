from figlib import *
def make():
    O=P(0,0); B=P(-9.487,-3.162); C=P(9.487,-3.162); A=P(5.69,8.22)
    E=P(0,-3.162); D=(A+B)/2
    f=Fig('q14',13500,(-12.3,12.0),(-10.6,10.7))
    f.circle(O,10.0)
    f.poly([A,B,C])
    f.seg(O,D); f.seg(O,E)
    f.dot(O,1.4)
    f.rightangle(D,A,O,0.95); f.rightangle(E,O,C,0.95)
    f.ticks(O,D,1,size=0.9,gap=0.5,frac=0.5); f.ticks(O,E,1,size=0.9,gap=0.5,frac=0.5)
    f.lab('A',A,5,9); f.lab('B',B,-10,-2); f.lab('C',C,10,-2); f.lab('D',D,-3,10); f.lab('E',E,0,-10); f.lab('O',O,11,-1)
    f.ngd_on(B,C,0.27)   # 변 BC 위
    return f.save()
if __name__=='__main__': print(make())
