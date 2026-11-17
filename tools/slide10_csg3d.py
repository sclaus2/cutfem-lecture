import numpy as np
from PIL import Image
W,H,SS=800,600,1.25
BLUE=np.array([0.0,0.314,0.604]); ORANGE=np.array([0.80,0.36,0.04])
def box(p,c,h):
    q=np.abs(p-c)-h
    return np.linalg.norm(np.maximum(q,0),axis=-1)+np.minimum(q.max(-1),0)
def sph(p,c,r): return np.linalg.norm(p-c,axis=-1)-r
def make(op):
    if op=='inputs':
        fa=lambda p:box(p,np.array([-1.05,0,0]),np.array([0.7,0.7,0.7])); fb=lambda p:sph(p,np.array([1.05,0,0]),0.85)
        comb=lambda a,b:np.minimum(a,b); col=lambda a,b:a<=b
    else:
        fa=lambda p:box(p,np.zeros(3),np.array([0.75,0.75,0.75])); fb=lambda p:sph(p,np.array([0.75,0.75,0.75]),0.8)
        if op=='union': comb=lambda a,b:np.minimum(a,b); col=lambda a,b:a<=b
        if op=='inter': comb=lambda a,b:np.maximum(a,b); col=lambda a,b:a>=b
        if op=='diff':  comb=lambda a,b:np.maximum(a,-b); col=lambda a,b:a>=-b
    return fa,fb,comb,col
def render(op,name):
    fa,fb,comb,col=make(op)
    f=lambda p:comb(fa(p),fb(p))
    w,h=int(W*SS),int(H*SS)
    cam=np.array([4.2,3.0,4.8]) if op!='inputs' else np.array([0.5,2.2,6.2])
    tgt=np.array([0.1,0.0,0.1]) if op!='inputs' else np.array([0.0,0.0,0.0])
    fw=(tgt-cam); fw/=np.linalg.norm(fw); rt=np.cross(fw,[0,1,0]); rt/=np.linalg.norm(rt); up=np.cross(rt,fw)
    fov=np.deg2rad(30 if op!='inputs' else 30); sc=np.tan(fov/2)
    xs=(np.arange(w)+0.5)/w*2-1; ys=1-(np.arange(h)+0.5)/h*2
    X,Y=np.meshgrid(xs*sc*w/h,ys*sc)
    d=fw[None,None,:]+X[...,None]*rt+Y[...,None]*up; d/=np.linalg.norm(d,axis=-1,keepdims=True)
    d=d.reshape(-1,3); o=np.broadcast_to(cam,d.shape)
    t=np.zeros(len(d)); hit=np.zeros(len(d),bool); alive=np.ones(len(d),bool)
    for i in range(160):
        idx=np.where(alive)[0]
        if len(idx)==0: break
        p=o[idx]+d[idx]*t[idx,None]; s=f(p)
        h_=s<1e-3; hit[idx[h_]]=True; alive[idx[h_]]=False
        t[idx]+=np.where(h_,0,s*0.9)
        far=t[idx]>14; alive[idx[far]]=False
    ygnd=-0.95 if op!='inputs' else -0.78
    L=np.array([-0.5,0.85,0.55]); L/=np.linalg.norm(L)
    img=np.ones((len(d),3))
    # ground
    tg=(ygnd-o[:,1])/np.where(np.abs(d[:,1])<1e-6,1e-6,d[:,1])
    gm=(~hit)&(tg>0)&(tg<30)
    gi=np.where(gm)[0]; gp=o[gi]+d[gi]*tg[gi,None]
    # shadow
    tt=np.full(len(gi),0.03); sh=np.ones(len(gi)); 
    for i in range(110):
        s=f(gp+L*tt[:,None]); sh=np.minimum(sh,np.clip(8*s/np.maximum(tt,1e-3),0,1)); tt+=np.clip(s,0.03,0.5)
        if tt.min()>7: break
    rad=np.linalg.norm(gp[:,[0,2]]-np.array([0.3,0.3]),axis=1)
    fade=np.clip(1-(rad/3.4)**2,0,1)
    g=1-0.30*(1-sh)*fade[:,None].repeat(1,1) if False else 1-0.32*(1-sh)*fade
    img[gi]=g[:,None]*np.ones(3)
    hi=np.where(hit)[0]
    if len(hi):
        p=o[hi]+d[hi]*t[hi,None]; e=2e-3
        n=np.stack([f(p+np.array([e,0,0])*v)-f(p-np.array([e,0,0])*v) for v in [1]]+
                   [f(p+np.array([0,e,0]))-f(p-np.array([0,e,0])), f(p+np.array([0,0,e]))-f(p-np.array([0,0,e]))],-1)
        n=np.stack([f(p+[e,0,0])-f(p-[e,0,0]),f(p+[0,e,0])-f(p-[0,e,0]),f(p+[0,0,e])-f(p-[0,0,e])],-1)
        n/=np.linalg.norm(n,axis=-1,keepdims=True)+1e-12
        a=fa(p); b=fb(p); isA=col(a,b)
        base=np.where(isA[:,None],BLUE,ORANGE)
        diff=np.clip(n@L,0,1); hemi=0.5+0.5*n[:,1]
        # soft shadow on object
        tt=np.full(len(hi),0.04); sh=np.ones(len(hi))
        for i in range(50):
            s=f(p+n*0.01+L*tt[:,None]); sh=np.minimum(sh,np.clip(10*s/np.maximum(tt,1e-3),0,1)); tt+=np.clip(s,0.02,0.3)
            if tt.min()>5: break
        v=-d[hi]; hv=(L+v); hv/=np.linalg.norm(hv,axis=-1,keepdims=True); spec=np.clip((n*hv).sum(-1),0,1)**40
        light=0.42+0.26*hemi+0.55*diff*(0.35+0.65*sh)
        c=base*light[:,None]+0.25*spec[:,None]*sh[:,None]
        # lighten toward white a bit for pastel look
        c=np.clip(c*1.15+0.03,0,1)
        img[hi]=c
    im=Image.fromarray((np.clip(img.reshape(h,w,3),0,1)*255).astype(np.uint8)).resize((W,H),Image.LANCZOS)
    im.save(f'figs/{name}.png'); print(name)
import sys
for op,name in [('inputs','csg_ab'),('union','csg_union'),('inter','csg_inter'),('diff','csg_diff')]:
    if name in sys.argv[1:]: render(op,name)
