import sys; sys.path.insert(0,'/Users/sclaus/Workspace/FEniCSx-pr/cutfem-lecture')
import numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import minicut as mc
B,O='#00509A','#B34F00'
C,R0,AMP,K=(0.5,0.5),0.30,0.07,5
phi=mc.star(C,R0,AMP,K)
th=np.linspace(0,2*np.pi,400); r=R0+AMP*np.cos(K*th); bx,by=C[0]+r*np.cos(th),C[1]+r*np.sin(th)
def fig():
    f,ax=plt.subplots(figsize=(4.24,3.4),dpi=200); ax.set_aspect('equal'); ax.axis('off')
    h=0.5*4.24/3.4*0.84; ax.set_xlim(0.5-h,0.5+h); ax.set_ylim(0.08,0.92); f.subplots_adjust(0,0,1,1); return f,ax
# phi map
f,ax=fig()
x=np.linspace(0.5-0.5*4.24/3.4*0.84,0.5+0.5*4.24/3.4*0.84,400); y=np.linspace(0.08,0.92,330)
X,Y=np.meshgrid(x,y); P=phi(X,Y)
cm=LinearSegmentedColormap.from_list('c',['#4F86C0','#FFFFFF','#EDA866'])
ax.pcolormesh(X,Y,P,cmap=cm,norm=TwoSlopeNorm(0,P.min(),P.max()),shading='auto')
ax.plot(np.r_[bx,bx[0]],np.r_[by,by[0]],color='#1C2B3A',lw=2.6)
ax.text(0.5,0.5,'φ < 0\ninside Ω',ha='center',va='center',fontsize=17,color='#0B2F5C',weight='bold')
ax.text(0.5-0.5*4.24/3.4*0.84+0.03,0.12,'φ > 0\noutside',ha='left',va='bottom',fontsize=15,color='#7A3500',weight='bold')
ax.annotate('φ = 0\nboundary Γ',xy=(C[0]+R0+AMP*0.98,C[1]),xytext=(0.5+0.5*4.24/3.4*0.84-0.20,0.80),fontsize=14,color='#1C2B3A',weight='bold',ha='center',arrowprops=dict(arrowstyle='->',color='#1C2B3A',lw=1.8))
f.savefig('figs/p1.png',facecolor='white'); plt.close(f)
# plain background mesh + curve
n=18; mesh=mc.Mesh(n,box=(0,0,1,1)); N=mesh.nodes
f,ax=fig()
for cell in mesh.cells: ax.add_patch(Polygon(N[cell],closed=True,fc='white',ec='#A9BDD6',lw=0.5))
ax.plot(np.r_[bx,bx[0]],np.r_[by,by[0]],color=B,lw=2.6)
f.savefig('figs/k0.png',facecolor='white'); plt.close(f)
