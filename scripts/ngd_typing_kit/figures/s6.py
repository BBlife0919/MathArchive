from figlib import *
def make():
    B=P(0,0); C=P(20,0); A=P(0,8); D=P(20,8); E=P(5,8)
    O=P(4,4); O2=P(17,5)
    f=Fig('s6',16500,(-1.7,21.8),(-3.4,11.4))
    g="#C8C8C8"
    f.circle(O,4,fill=g); f.circle(O2,3,fill=g)
    f.poly([A,D,C,B])
    f.seg(E,C)
    f.dot(O,1.3); f.dot(O2,1.3)
    f.lab('O',O,0,-9); f.lab("O′",O2,-1,-9)
    f.dimarc_pt(A,E,+1,'5cm',pt=9)
    f.dimarc_pt(B,C,-1,'20cm',pt=10)
    f.lab('A',A,-8,3); f.lab('E',E,9,8); f.lab('D',D,9,3); f.lab('B',B,-8,-3); f.lab('C',C,9,-3)
    f.ngd_on(E,C,0.5)
    return f.save()
if __name__=='__main__': print(make())
