"""Side-by-side animation: one-parameter vs two-parameter optimal rotor turning through the jet.
Run: python slide9_compare_anim.py OUTDIR   (needs slide9_opt2.py; writes OUTDIR/rotor_compare.gif, rotor_compare_first.png)"""
import sys, os, json
out = sys.argv[1] if len(sys.argv) > 1 else "."
sys.argv = [sys.argv[0], out]
import numpy as np
import slide9_opt2 as o
from PIL import Image
import matplotlib.pyplot as plt
mc = o.mc
T_star = 150.0
cfg = [("1 parameter: a = 0.17, b = 0.075", 0.17, 0.075), ("2 parameters: a = 0.21, b = 0.072", 0.2067, 0.0719)]
nf = 36
frames = []
peaks = [[], []]
for k in range(nf):
    th = o.PERIOD * k / nf
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 5.6), dpi=100)
    for j, (lab, a, b) in enumerate(cfg):
        g = mc.CutGeometry(mc.Mesh(40), mc.rotate(o.rot2(a, b), th))
        A, r = mc.poisson_system(g, o.f_jet, o.zero, ghost=True)
        u = mc.solve(g, A, r); pk = float(np.nanmax(u)); peaks[j].append(pk)
        o.solution_ax(g, u, axs[j], T_star); o.jet_ax(axs[j])
        axs[j].set_title(f"{lab}\narea {mc.area(g):.3f}   peak {pk:.0f}", fontsize=14, color="#3B3B3B")
    fig.text(0.5, 0.03, f"θ = {np.degrees(th):4.1f}°   (red dashed: hot-gas jet, fixed in space; colour scale 0 to 150)", ha="center", fontsize=13, color="#3B3B3B")
    fig.subplots_adjust(0.01, 0.08, 0.99, 0.86, wspace=0.03)
    fig.canvas.draw()
    frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()))
    if k == 0: fig.savefig(f"{out}/rotor_compare_first.png", facecolor="white")
    plt.close(fig)
pal = [im.convert("P", palette=Image.ADAPTIVE, colors=128) for im in frames]
pal[0].save(f"{out}/rotor_compare.gif", save_all=True, append_images=pal[1:], duration=90, loop=0, optimize=True)
json.dump(dict(peaks=peaks, max=[max(p) for p in peaks]), open(f"{out}/rotor_compare.json", "w"))
print([max(p) for p in peaks], os.path.getsize(f"{out}/rotor_compare.gif"))
