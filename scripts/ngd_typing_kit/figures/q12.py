from figlib import *
def make():
    h=20*np.tan(np.radians(35))          # 그루터기 높이 ≈ 14.0
    Gt=P(0,h); Ge=P(20,0)                # 빗변: 그루터기 꼭대기 ~ 지면 접점
    f=Fig('q12',14500,(-3.0,23.5),(-6.2,16.2))
    ax=f.ax
    f.seg(P(-3.0,0),P(23.0,0),lw=0.8)    # 지면
    d=unit(Ge-Gt); n=P(-d[1],d[0])
    if n[1]<0: n=-n
    # 그루터기(수직 기둥)
    ax.fill([-0.55,0.55,0.55,-0.55],[0,0,h,h],fc="white",ec="none",zorder=3)
    ax.plot([-0.55,-0.55,0.55,0.55],[0,h,h,0],color="k",lw=LW,zorder=3.5)
    f.rightangle(P(0.55,0),P(0.55,1),P(2,0),1.0)
    # 잎 덩어리: 하나로 뭉친 수풀 모양(겹친 원의 합집합) — 바깥 윤곽선만 그림. 빗변(줄기) 위·아래로 걸쳐 있음
    crown=((0.30,1.0,0.6),(0.36,1.4,-0.2),(0.38,1.3,1.6),(0.45,1.7,0.4),(0.47,1.3,2.3),(0.54,1.8,0.2),
           (0.56,1.4,2.0),(0.63,1.6,0.6),(0.64,1.2,1.9),(0.71,1.3,0.4),(0.72,0.95,1.5),(0.78,0.8,0.5))
    ppu=f.pt_per_unit
    for t,r,o in crown:                              # 1) 바깥 윤곽(검정)
        c=Gt+(Ge-Gt)*t+n*o
        ax.add_patch(Circle(c,r,fc="k",ec="k",lw=1.1,zorder=1.5))
    for t,r,o in crown:                              # 2) 안쪽 채움(회색) — 윤곽 두께만큼 줄여서 겹친 원의 내부 경계선 제거
        c=Gt+(Ge-Gt)*t+n*o
        ax.add_patch(Circle(c,r-0.6/ppu,fc="#CFCFCF",ec="none",zorder=1.6))
    f.seg(Gt,Ge,lw=2.6,z=2.6)            # 줄기: 빗변 위에 놓인 나무(굵은 선)
    # 35°
    f.angle(Ge,Gt,P(0,0),3.4,'35°',fs=9)
    # 20 m 치수(밑동 오른쪽 끝 ~ 지면 접점)
    f.dimarc_pt(P(0.55,-0.2),P(Ge[0],-0.2),-1,'20 m',pt=10)
    f.ngd_on(P(-3.0,0),P(23.0,0),0.46)
    return f.save()
if __name__=='__main__': print(make())
