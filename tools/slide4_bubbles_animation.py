import numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.tri as mtri
from matplotlib.collections import PolyCollection
from PIL import Image
import io
n=22; xs=np.linspace(0,1,n+1); X,Y=np.meshgrid(xs,xs,indexing='ij'); N=np.c_[X.ravel(),Y.ravel()]
idx=np.arange((n+1)**2).reshape(n+1,n+1)
v00,v10,v11,v01=idx[:-1,:-1].ravel(),idx[1:,:-1].ravel(),idx[1:,1:].ravel(),idx[:-1,1:].ravel()
T=np.vstack([np.c_[v00,v10,v11],np.c_[v00,v11,v01]])
tri=mtri.Triangulation(N[:,0],N[:,1],T)
def phi_at(s):
    # s in [0,1]: bubbles approach and merge
    e=0.5-0.5*np.cos(np.pi*s)
    d=0.30*(1-e)+0.08*e
    r1,r2=0.21,0.17
    c1=(0.5-d-0.0, 0.5+0.04*np.sin(2*np.pi*s)); c2=(0.5+d, 0.5-0.03*np.sin(2*np.pi*s))
    p1=np.hypot(N[:,0]-c1[0],N[:,1]-c1[1])-r1; p2=np.hypot(N[:,0]-c2[0],N[:,1]-c2[1])-r2
    eps=0.025
    return -eps*np.log(np.exp(-p1/eps)+np.exp(-p2/eps))
def frame(s):
    ph=phi_at(s); pc=ph[T]
    ins=(pc<0).all(1); cut=(pc<0).any(1)&(pc>0).any(1)
    f=plt.figure(figsize=(5.2,5.2),dpi=100); ax=f.add_axes([0,0,1,1]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    col=np.where(cut,'#FDEBD8',np.where(ins,'#EAF1F8','#FFFFFF'))
    ax.add_collection(PolyCollection(N[T],facecolors=col,edgecolors='#A9BDD6',linewidths=0.5))
    ax.tricontour(tri,ph,levels=[0],colors='#00509A',linewidths=3)
    # cut cells outline darker orange
    ax.add_collection(PolyCollection(N[T[cut]],facecolors='none',edgecolors='#E0A36B',linewidths=0.7))
    f.canvas.draw(); im=Image.fromarray(np.asarray(f.canvas.buffer_rgba())[:,:,:3].copy()); plt.close(f); return im
S=np.r_[np.linspace(0,1,30),np.ones(14)]
fr=[frame(s) for s in S]; fr=fr+fr[-2:0:-1]
fr[0].save('bubbles.gif',save_all=True,append_images=fr[1:],duration=[80]*len(fr),loop=0,optimize=True)
fr[len(S)//2].save('bubbles_mid.png'); fr[-0].save('b0.png')
print(len(fr))
