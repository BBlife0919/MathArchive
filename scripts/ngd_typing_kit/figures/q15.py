from figlib import *
def make():
    s3=np.sqrt(3)
    A=P(-6,0); O=P(0,0); B=P(6,0); O2=P(9,0); C=P(12,0); Pp=P(3,3*s3)
    f=Fig('q15',16000,(-7.4,14.3),(-4.4,8.6))
    FILL="#CFCFCF"
    # 색칠: 삼각형 OPC에서 부채꼴 OPB를 뺀 부분 + 아래 작은 반원
    th=np.linspace(0,60,40)
    arcpts=[P(6*np.cos(np.radians(t)),6*np.sin(np.radians(t))) for t in th]   # B(0°) -> P(60°)
    f.fill_poly([C]+arcpts[::-1][:0]+[Pp]+arcpts[::-1]+[],FILL)   # C, P, (P->B 호), (B->C 밑변)
    f.wedge_fill(O2,3,180,360,FILL)
    # 큰 반원(위), 작은 반원(아래)
    f.arc(O,6,0,180); f.arc(O2,3,180,360)
    f.seg(A,C)
    f.seg(O,Pp)
    u=unit(Pp-C); f.seg(C,Pp+u*5.0)
    f.rightangle(Pp,O,C,0.8)
    f.dot(O,1.3); f.dot(O2,1.3)
    f.lab('A',A,-2,-10); f.lab('O',O,0,-10); f.lab('B',B,-8,-9); f.lab("O′",O2,0,-10)
    f.lab('C',C,10,-3); f.lab('P',Pp,8,9)
    f.ngd_on(P(-6,0),P(12,0),0.22)   # AC선 위(선과 나란히)
    return f.save()
if __name__=='__main__': print(make())
