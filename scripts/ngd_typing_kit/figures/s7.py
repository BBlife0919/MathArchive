from figlib import *
def make():
    f=Fig('s7',15500,(-3.9,7.2),(-1.5,6.5))
    ax=f.ax
    ax.annotate('',xy=(6.6,0),xytext=(-0.9,0),arrowprops=dict(arrowstyle='-|>',lw=0.9,color='k',mutation_scale=7,shrinkA=0,shrinkB=0),zorder=2)
    ax.annotate('',xy=(0,6.1),xytext=(0,-1.0),arrowprops=dict(arrowstyle='-|>',lw=0.9,color='k',mutation_scale=7,shrinkA=0,shrinkB=0),zorder=2)
    f.seg(P(-0.6,5.6),P(6.4,-1.4))
    A=P(4,4); B=P(2,0); C=P(5,0); D=P(3,2)
    f.seg(A,B)
    f.lab('x',P(6.6,0),4,-9,italic=True); f.lab('y',P(0,6.1),9,-2,italic=True)
    f.lab('O',P(0,0),-8,-8)
    f.lab('B',B,0,-10); f.lab('C',C,7,6); f.lab('A',A,7,6); f.lab('D',D,10,-2)
    f.lab('5',P(0,5),8,2,fs=7); f.lab('5',P(5,0),-5,-8,fs=7)
    f.lab('y=−x+5',P(-0.75,5.0),0,3,ha='right',italic=True,weight='bold')
    f.ngd_on(P(-0.6,5.6),P(6.4,-1.4),0.27)
    return f.save()
if __name__=='__main__': print(make())
