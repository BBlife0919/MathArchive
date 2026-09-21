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
    # 잎 덩어리: 빗변(나무가 놓인 선)을 중심으로 양쪽에 걸쳐 있음(선 아래에 깔림)
    for t,r,o in ((0.24,0.9,0.3),(0.33,1.15,-0.2),(0.42,1.3,0.35),(0.51,1.3,-0.15),(0.60,1.25,0.3),(0.68,0.95,-0.1)):
        c=Gt+(Ge-Gt)*t+n*o*r
        ax.add_patch(Circle(c,r,fc="#D9D9D9",ec="k",lw=0.7,zorder=1.6))
    f.seg(Gt,Ge,lw=2.4,z=2.6)            # 줄기: 빗변 위에 놓인 나무(굵은 선)
    # 35°
    f.angle(Ge,Gt,P(0,0),3.4,'35°',fs=9)
    # 20 m 치수(밑동 오른쪽 끝 ~ 지면 접점)
    f.dimarc_pt(P(0.55,-0.2),P(Ge[0],-0.2),-1,'20 m',pt=10)
    f.ngd_on(P(-3.0,0),P(23.0,0),0.46)
    return f.save()
if __name__=='__main__': print(make())
