from figx1 import *
def make():
    ac=2*np.sqrt(7)
    A=P(0,0); C=P(ac,0); B=P(ac,6)
    f=Fig('q04',11000,(-0.8,6.3),(-0.75,6.85))
    f.poly([A,B,C])
    f.rightangle(C,A,B,0.28)
    f.dimarc_pt(A,B,+1,'8',pt=11)
    f.lab('A',A,-8,-4); f.lab('B',B,6,6); f.lab('C',C,8,-4)
    f.ngd(on_seg(C,B,0.5),ang=90)
    return f.save()
if __name__=='__main__': print(make())
