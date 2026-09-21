from figx1 import *
def make():
    s3=np.sqrt(3)
    A=P(0,0); C=P(2*s3,0); D=P(0,2*s3); B=P(2*s3,2)
    f=Fig('q03',12000,(-0.55,4.2),(-0.6,4.05))
    f.poly([A,D,C],close=True)      # 삼각형 ACD (변 AD, DC, CA)
    f.seg(A,B); f.seg(B,C)          # 삼각형 ABC의 나머지 변
    f.rightangle(A,D,C,0.2); f.rightangle(C,A,B,0.2)
    f.angle(D,A,C,0.42,'45°')
    f.angle(B,C,A,0.32,'60°')
    f.dimarc_pt(B,C,+1,'2',pt=10)   # BC=2 : 오른쪽으로 부풂
    f.lab('D',D,-8,5); f.lab('B',B,8,5); f.lab('A',A,-8,-6); f.lab('C',C,9,-5)
    f.ngd(on_seg(A,C,0.5),ang=0)
    return f.save()
if __name__=='__main__': print(make())
