import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
plt.rcParams.update({"mathtext.fontset":"cm","svg.fonttype":"path"})
C="#00509A"
H=272
fig=plt.figure(figsize=(3.85,H/100))
fig.patch.set_alpha(0)
ax=fig.add_axes([0,0,1,1]); ax.axis("off"); ax.set_xlim(0,385); ax.set_ylim(0,H)
xe=50; fs=27
rows=[(H-26,r"$\Omega$",r"$=\,\{\,x\,:\,\varphi(x)<0\,\}$"),
      (H-80,r"$\partial\Omega$",r"$=\,\{\,x\,:\,\varphi(x)=0\,\}$"),
      (H-150,r"$\mathbf{n}$",r"$=\dfrac{\nabla\varphi}{|\nabla\varphi|}$"),
      (H-228,r"$\kappa$",r"$=\nabla\!\cdot\!\mathbf{n}$")]
for y,l,r in rows:
    ax.text(xe,y,l,color=C,fontsize=fs,ha="right",va="center")
    ax.text(xe+4,y,r,color=C,fontsize=fs,ha="left",va="center")
fig.savefig("levelset_formulas2.svg",transparent=True)
fig.savefig("new_prev.png",dpi=100,facecolor="#eaf1f8")
