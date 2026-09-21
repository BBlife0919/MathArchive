from figx1 import *
def make():
    A=P(0,0); C=P(2,0); B=P(2,np.sqrt(5))
    f=Fig('q02',11000,(-0.45,2.55),(-0.7,2.6))
    f.poly([A,B,C])
    f.rightangle(C,A,B,0.17)
    f.dimarc_pt(A,B,+1,'3',pt=10)     # AB : 왼쪽/위로 부풂
    f.dimarc_pt(C,A,+1,'2',pt=10)     # CA : 아래로 부풂
    f.lab('A',A,-8,-2); f.lab('B',B,6,7); f.lab('C',C,8,-3)
    f.ngd(on_seg(C,B,0.5),ang=90)
    return f.save()
if __name__=='__main__': print(make())
