from figlib import *
def make():
    B=P(0,0); C=P(10,0); A=P(6,6)
    f=Fig('s3',14500,(-1.6,11.2),(-1.6,7.4))
    f.poly([A,B,C])
    f.dimarc_pt(B,A,+1,r'$6\sqrt{2}$',pt=11)
    f.angle(B,C,A,1.3,'45°',fs=8.5)
    f.lab('A',A,0,9); f.lab('B',B,-9,-2); f.lab('C',C,9,-2)
    f.ngd_on(A,C,0.5)
    return f.save()
if __name__=='__main__': print(make())
