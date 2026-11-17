import sys; sys.path.insert(0,'/Users/sclaus/Workspace/FEniCSx-pr/cutfem-lecture')
import numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.tri as mtri
from matplotlib.patches import Polygon, Rectangle
from scipy.spatial import Delaunay
import scipy.sparse as sp, scipy.sparse.linalg as spla
import minicut as mc
B,O,LB,LO,G='#00509A','#B34F00','#EAF1F8','#FDEBD8','#6E6E6E'
C,R0,AMP,K=(0.5,0.5),0.30,0.07,5
def rad(th): return R0+AMP*np.cos(K*th)
th=np.linspace(0,2*np.pi,400)
bx,by=C[0]+rad(th)*np.cos(th),C[1]+rad(th)*np.sin(th)
phi=mc.star(C,R0,AMP,K)
def fig():
    f,ax=plt.subplots(figsize=(4.24,3.4),dpi=200); ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(0.08,0.92); ax.set_ylim(0.08,0.92); ax.set_xlim(0.5-0.5*4.24/3.4*0.84,0.5+0.5*4.24/3.4*0.84); ax.set_ylim(0.08,0.92); f.subplots_adjust(0,0,1,1); return f,ax
def save(f,n): f.savefig(f'figs/{n}.png',facecolor='white'); plt.close(f)
# ---- fitted mesh
rng=np.random.default_rng(2)
N=64; t=np.linspace(0,2*np.pi,N,endpoint=False); bp=np.c_[C[0]+rad(t)*np.cos(t),C[1]+rad(t)*np.sin(t)]
pts=[bp]
for s,n in [(0.8,52),(0.6,40),(0.4,26),(0.2,13)]:  # concentric rings scaled
    tt=np.linspace(0,2*np.pi,n,endpoint=False)+0.2*s
    pts.append(np.c_[C[0]+s*rad(tt)*np.cos(tt),C[1]+s*rad(tt)*np.sin(tt)])
pts.append(np.array([C]))
P=np.vstack(pts); tri=Delaunay(P); T=tri.simplices
cen=P[T].mean(1); T=T[phi(cen[:,0],cen[:,1])<0]
nb=N  # first N points are boundary
def fitted(ax,lw=0.5):
    ax.triplot(P[:,0],P[:,1],T,color='#7A9CC0',lw=lw); ax.plot(np.r_[bx,bx[0]],np.r_[by,by[0]],color=B,lw=2.2)
f,ax=fig(); fitted(ax); save(f,'c1')
# ---- element types
f,ax=fig(); ax.set_xlim(0,2.12); ax.set_ylim(-0.05,1.3)
def reftri(ox,deg,lab):
    V=np.array([[0,0],[1,0],[0,1]],float)+[ox,0]
    ax.add_patch(Polygon(V,closed=True,fc=LB,ec=B,lw=2.2))
    pts=list(V)
    if deg==2: pts+= [(V[0]+V[1])/2,(V[1]+V[2])/2,(V[0]+V[2])/2]
    pts=np.array(pts); ax.scatter(pts[:,0],pts[:,1],s=110,color=O,zorder=3)
    ax.text(ox+0.5,1.2,lab,ha='center',fontsize=15,color=B,weight='bold')
reftri(0.02,1,'P1: 3 nodes'); reftri(1.12,2,'P2: 6 nodes')
ax.set_xlim(0,2.2); save(f,'c2')
# ---- element integrals: triangle with Gauss points and block in matrix
def blockfig(cut=False):
    f,ax=fig(); ax.set_xlim(0,2.3); ax.set_ylim(-0.1,1.25)
    V=np.array([[0.05,0.1],[0.95,0.2],[0.35,1.0]])
    ax.add_patch(Polygon(V,closed=True,fc=LB,ec=B,lw=2.2))
    # 3 Gauss points
    q=np.array([[1/6,1/6],[2/3,1/6],[1/6,2/3]]); X=q[:,0:1]*V[1]+q[:,1:2]*V[2]+(1-q.sum(1))[:,None]*V[0]
    ax.scatter(X[:,0],X[:,1],s=95,color=O,zorder=3)
    ax.annotate('',xy=(1.28,0.55),xytext=(1.02,0.55),arrowprops=dict(arrowstyle='->',color=G,lw=2))
    n=8; x0,y0,s=1.38,0.1,0.11
    for i in range(n):
        for j in range(n):
            ax.add_patch(Rectangle((x0+j*s,y0+(n-1-i)*s),s,s,fc='white',ec='#CCCCCC',lw=0.6))
    for (i,j) in [(2,2),(2,3),(2,5),(3,2),(3,3),(3,5),(5,2),(5,3),(5,5)]:
        ax.add_patch(Rectangle((x0+j*s,y0+(n-1-i)*s),s,s,fc=B,ec='white',lw=0.6))
    ax.text(x0+n*s/2,y0+n*s+0.08,'K, F',ha='center',fontsize=15,color=B,weight='bold')
    return f,ax
f,ax=blockfig(); save(f,'c3')
# ---- Dirichlet on fitted mesh
f,ax=fig(); fitted(ax,0.4); ax.scatter(bp[:,0],bp[:,1],s=26,color=O,zorder=3); save(f,'c4')
# ---- P1 system on fitted mesh
nv=len(P); rows=[];cols=[];vals=[]; Fv=np.zeros(nv)
for tt in T:
    p=P[tt]; M=np.c_[np.ones(3),p]; a=0.5*abs(np.linalg.det(M)); g=np.linalg.inv(M)[1:,:].T
    Ke=a*g@g.T
    for i in range(3):
        Fv[tt[i]]+=a/3
        for j in range(3): rows.append(tt[i]);cols.append(tt[j]);vals.append(Ke[i,j])
Kmat=sp.csr_matrix((vals,(rows,cols)),shape=(nv,nv))
free=np.arange(nb,nv); u=np.zeros(nv); u[free]=spla.spsolve(Kmat[free][:,free].tocsc(),Fv[free])
# order unknowns spatially for a banded pattern: sort by angle then radius? use reverse Cuthill-McKee
from scipy.sparse.csgraph import reverse_cuthill_mckee
def spyfig(A,name):
    perm=reverse_cuthill_mckee(sp.csr_matrix(A),symmetric_mode=True); Ap=sp.csr_matrix(A)[perm][:,perm].tocoo()
    f,ax=fig(); n=A.shape[0]; ax.set_xlim(0.5-0.5*4.24/3.4*0.84,0.5+0.5*4.24/3.4*0.84)
    sc=0.80/n; x0=0.5-0.40; y0=0.09
    ax.add_patch(Rectangle((x0,y0),0.80,0.80,fc='white',ec=G,lw=1.5))
    ax.scatter(x0+Ap.col*sc,y0+0.80-Ap.row*sc,s=1.6,color=B,marker='s',linewidths=0)
    save(f,name)
spyfig(Kmat,'c5')
f,ax=fig(); tr=mtri.Triangulation(P[:,0],P[:,1],T)
ax.tricontourf(tr,u,levels=14,cmap='Blues'); ax.plot(np.r_[bx,bx[0]],np.r_[by,by[0]],color=B,lw=2.2); save(f,'c6')
# ================= cut FEM
mesh=mc.Mesh(18,box=(0,0,1,1)); geom=mc.CutGeometry(mesh,phi,order=4)
ct=geom.cell_type; Nd=mesh.nodes
def bgmesh(ax,colored=True,lw=0.4):
    for c,cell in enumerate(mesh.cells):
        col='white'
        if colored: col={mc.INSIDE:LB,mc.CUT:LO}.get(ct[c],'white')
        ax.add_patch(Polygon(Nd[cell],closed=True,fc=col,ec='#9DB6D1',lw=lw))
    ax.plot(np.r_[bx,bx[0]],np.r_[by,by[0]],color=B,lw=2.2)
f,ax=fig(); bgmesh(ax,False,0.45); ax.plot(np.r_[bx,bx[0]],np.r_[by,by[0]],color=B,lw=2.2)
bgmesh(ax,True,0.45); save(f,'k1')
# k2: elements on active mesh with active dofs
f,ax=fig()
for c,cell in enumerate(mesh.cells):
    act=ct[c]!=mc.OUTSIDE
    ax.add_patch(Polygon(Nd[cell],closed=True,fc=LB if act else 'white',ec='#9DB6D1' if act else '#DDDDDD',lw=0.5))
d=geom.active_dofs; ax.scatter(Nd[d,0],Nd[d,1],s=9,color=B,zorder=3)
ax.plot(np.r_[bx,bx[0]],np.r_[by,by[0]],color=O,lw=2.0); save(f,'k2')
# k3: quadrature zoom
f,ax=fig(); x0,x1,y0,y1=0.68,0.88,0.43,0.63
cx=(x0+x1)/2; hh=(y1-y0)/2; ax.set_xlim(cx-hh*4.24/3.4,cx+hh*4.24/3.4); ax.set_ylim(y0,y1)
for c,cell in enumerate(mesh.cells):
    ax.add_patch(Polygon(Nd[cell],closed=True,fc={mc.INSIDE:LB,mc.CUT:LO}.get(ct[c],'white'),ec='#9DB6D1',lw=1.0))
for sv,pc in zip(geom.sub_verts,geom.sub_cells):
    if ct[pc]==mc.CUT: ax.add_patch(Polygon(sv,closed=True,fc='#FFFFFF',ec=B,lw=1.0,alpha=0.9))
ax.plot(bx,by,color=B,lw=2.6)
vp=geom.volume.points; m=ct[geom.volume.cells]==mc.CUT
ax.scatter(vp[m,0],vp[m,1],s=30,color=B,zorder=3)
ax.scatter(geom.interface.points[:,0],geom.interface.points[:,1],s=36,color=O,zorder=4)
save(f,'k3')
# k4: ghost facets
f,ax=fig(); bgmesh(ax,False,0.3)
fc=mesh.facet_cells if hasattr(mesh,'facet_cells') else None
for e in geom.ghost_facets:
    verts=mesh.facet_nodes[e]
    if verts is not None: ax.plot(Nd[verts,0],Nd[verts,1],color='#C0392B',lw=1.8)
ax.plot(np.r_[bx,bx[0]],np.r_[by,by[0]],color=B,lw=2.2)
# normals
ip=geom.interface; sel=np.arange(0,len(ip),9)
ax.quiver(ip.points[sel,0],ip.points[sel,1],ip.normals[sel,0],ip.normals[sel,1],color=O,scale=22,width=0.004,zorder=4)
save(f,'k4')
# k5: matrix
A,b=mc.poisson_system(geom,lambda x,y:np.ones_like(x),lambda x,y:np.zeros_like(x))
dd=geom.active_dofs; spyfig(sp.csr_matrix(A)[dd][:,dd],'k5')
# k6: solution
uu=mc.solve(geom,A,b)
f,ax=fig(); mc.plot_solution(geom,uu,ax=ax)
ax.set_xlim(0.5-0.5*4.24/3.4*0.84,0.5+0.5*4.24/3.4*0.84); ax.set_ylim(0.08,0.92); ax.axis('off'); f.subplots_adjust(0,0,1,1)

for c in ax.collections:
    try: c.set_cmap('Blues')
    except Exception: pass
for a_ in f.axes[1:]: a_.remove()
ax.plot(np.r_[bx,bx[0]],np.r_[by,by[0]],color=B,lw=2.2); save(f,'k6')
print('ok')
