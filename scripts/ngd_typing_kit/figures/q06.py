from figx1 import *
def make():
    s=2*np.sqrt(3)
    A=P(0,0); B=P(5,0); C=P(5,s); D=P(2,s)
    f=Fig('q06',13500,(-0.75,5.65),(-0.75,4.75))
    f.poly([A,B,C,D])
    f.rightangle(B,A,C,0.25); f.rightangle(C,B,D,0.25)
    f.angle(A,B,D,0.6,'60°')
    f.dimarc_pt(A,D,+1,'4',pt=10)         # AD=4 : 왼쪽/위로 부풂
    f.dimarc_pt(D,C,+1,'3',pt=10)         # DC=3 : 위로 부풂
    f.lab('A',A,-8,-5); f.lab('B',B,8,-5); f.lab('C',C,8,6); f.lab('D',D,-4,9)
    f.ngd(on_seg(B,C,0.55),ang=90)
    return f.save()
if __name__=='__main__': print(make())
