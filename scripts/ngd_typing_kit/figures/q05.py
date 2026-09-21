from figx1 import *
def make():
    A=P(0,0); B=P(10,0); C=P(3,3*np.sqrt(3))
    f=Fig('q05',15000,(-1.3,11.0),(-1.9,6.5))
    f.poly([A,B,C])
    f.angle(A,B,C,1.2,'60°')
    f.dimarc_pt(A,C,+1,'6',pt=10)          # AC=6 : 왼쪽으로 부풂
    f.dimarc_pt(A,B,-1,'10',pt=10)         # AB=10 : 아래로 부풂
    f.lab('A',A,-8,-6); f.lab('B',B,8,-5); f.lab('C',C,2,9)
    f.ngd(on_seg(C,B,0.62),ang=seg_ang(C,B))
    return f.save()
if __name__=='__main__': print(make())
