from figlib import *
def hit_ground(p,d):
    s=-p[1]/d[1]; return p+s*d
def make():
    h=20*np.tan(np.radians(35))          # 그루터기 높이 ≈ 14.0
    Gt=P(0,h); Ge=P(20,0)
    f=Fig('q12',14500,(-3.0,23.5),(-6.2,16.2))
    ax=f.ax
    f.seg(P(-3.0,0),P(23.0,0),lw=0.8)
    d=unit(Ge-Gt); n=P(-d[1],d[0])
    if n[1]<0: n=-n
    hw=0.42
    S=Gt+P(0,-0.25)
    lo0,up0=S-n*hw,S+n*hw
    lo1,up1=hit_ground(lo0,d),hit_ground(up0,d)
    band=[lo0,lo1,up1,up0]
    # 잎 덩어리(띠 위쪽, 겹쳐서 잎 무리처럼)
    for t,r in ((0.36,1.15),(0.47,1.35),(0.58,1.4),(0.69,1.4),(0.80,1.25),(0.90,0.95)):
        c=S+(Ge-S)*t+n*(hw+r*0.35)
        ax.add_patch(Circle(c,r,fc="#D9D9D9",ec="k",lw=0.7,zorder=1.6))
    ax.fill([p[0] for p in band],[p[1] for p in band],fc="white",ec="k",lw=LW,zorder=2)
    # 그루터기(수직)
    ax.fill([-0.55,0.55,0.55,-0.55],[0,0,h,h],fc="white",ec="none",zorder=3)
    ax.plot([-0.55,-0.55,0.55,0.55],[0,h,h,0],color="k",lw=LW,zorder=3.5)
    f.rightangle(P(0.55,0),P(0.55,1),P(2,0),1.0)
    # 35° (띠 아래쪽 모서리와 지면 사이)
    f.angle(lo1,lo0,P(lo1[0]-1,0),3.6,'35°',fs=9)
    # 20 m 치수
    f.dimarc_pt(P(0.55,-0.2),P(lo1[0],-0.2),-1,'20 m',pt=10)   # 밑동 오른쪽 끝 ~ 지면 접점, 숫자는 점선 사이
    f.ngd_on(P(-3.0,0),P(23.0,0),0.46)   # 지면선 위
    return f.save()
if __name__=='__main__': print(make())
