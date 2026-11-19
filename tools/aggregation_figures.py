"""Figures for the aggregation implementation slides. Run: PYTHONPATH=. python tools/aggregation_figures.py OUTDIR"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import minicut as mc

matplotlib.rcParams["mathtext.fontset"] = "cm"
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, DARK, INK, GREY, B = "#CFE2F5", "#F9C48F", "#B34F00", "#1F2937", "#6e7a88", "#00509a"

mesh = mc.Mesh(5, box=(-1, -1, 1, 1))
R = 0.48
geom = mc.CutGeometry(mesh, mc.circle((0, 0), R))
agg = mc.aggregate(geom, 0.25)
ct = geom.cell_type if hasattr(geom, "cell_type") else None
ill = set(int(c) for c in agg.ill_cells)
roots = set(int(agg.root[c]) for c in agg.ill_cells)
active = set(int(c) for c in geom.active_cells)
removed = [int(d) for d in agg.removed_dofs]
good = [int(d) for d in agg.good_dofs]
P = mesh.nodes
cent = lambda c: P[mesh.cells[c]].mean(0)

# ---- figure 1: mesh with ill-posed cells, roots, removed dofs
fig, ax = plt.subplots(figsize=(6.4, 6.4))
ax.set_aspect("equal"); ax.axis("off"); fig.subplots_adjust(0, 0, 1, 1)
for c in range(mesh.n_cells):
    poly = P[mesh.cells[c]]
    if c in ill:
        ax.add_patch(Polygon(poly, fc=ORANGE, ec=GREY, lw=1.2, hatch="////"))
    elif c in active:
        ax.add_patch(Polygon(poly, fc=BLUE, ec=GREY, lw=1.2))
    else:
        ax.add_patch(Polygon(poly, fc="white", ec="#d5d9de", lw=1.0))
for c in roots:
    ax.add_patch(Polygon(P[mesh.cells[c]], fc="none", ec=B, lw=4.2, joinstyle="round"))
th = np.linspace(0, 2*np.pi, 400)
ax.plot(R*np.cos(th), R*np.sin(th), color=DARK, lw=3.6)
for c in ill:
    a, b = cent(c), cent(int(agg.root[c]))
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=B, lw=2.4, shrinkA=4, shrinkB=4))
act = set(int(d) for d in geom.active_dofs)
for d in act:
    if d in removed:
        ax.plot(*P[d], "o", ms=17, mfc=DARK, mec="white", mew=2)
    else:
        ax.plot(*P[d], "o", ms=11, mfc=INK, mec="white", mew=1.5)
for d in removed + [13, 14, 20]:
    if d == 7: x, y, ha, va = P[d][0] - 0.07, P[d][1] - 0.04, "right", "top"
    elif d == 28: x, y, ha, va = P[d][0] + 0.07, P[d][1] + 0.04, "left", "bottom"
    else: x, y, ha, va = P[d][0] + 0.03, P[d][1] - 0.075, "left", "top"
    ax.text(x, y, str(d), fontsize=17, fontweight="bold", color=DARK if d in removed else INK, ha=ha, va=va)
ax.set_xlim(-0.85, 0.85); ax.set_ylim(-0.85, 0.85)
fig.savefig(out / "agg_mesh.png", dpi=170, transparent=True); plt.close(fig)

# ---- figure 2: E as a coloured grid (active rows)
rows = sorted(act)
nr, nc = len(rows), len(good)
E = agg.E.toarray()
fig, ax = plt.subplots(figsize=(7.0, 6.4))
ax.set_aspect("equal"); ax.axis("off"); fig.subplots_adjust(0.1, 0, 1, 0.9)
order = [d for d in rows if d not in removed] + removed
for i, d in enumerate(order):
    for j in range(nc):
        v = E[d, j]
        fc = "white"
        if d in removed: fc = "#FDEBD8"
        if v != 0: fc = ORANGE if d in removed else BLUE
        ax.add_patch(Rectangle((j, nr-1-i), 1, 1, fc=fc, ec="#c9ced6", lw=0.8))
        if v != 0:
            ax.text(j+.5, nr-1-i+.5, f"{v:g}".replace("-", "−"), ha="center", va="center", fontsize=14, color=INK, fontweight="bold")
    ax.text(-0.25, nr-1-i+.5, str(d), ha="right", va="center", fontsize=14, color=DARK if d in removed else INK, fontweight="bold" if d in removed else "normal")
for j, d in enumerate(good):
    ax.text(j+.5, nr+0.25, str(d), ha="center", va="bottom", fontsize=14, color=INK, rotation=0)
ax.add_patch(Rectangle((0, 0), nc, 2, fc="none", ec=DARK, lw=2.4))
ax.set_xlim(-1.3, nc+.2); ax.set_ylim(-.2, nr+1.1)
fig.savefig(out / "agg_E.png", dpi=170, transparent=True, bbox_inches="tight", pad_inches=0.05); plt.close(fig)

# ---- figure 3: formulas
def tex(name, s, fs=34, w=9, h=0.9):
    fig = plt.figure(figsize=(w, h)); fig.text(0.0, 0.5, s, fontsize=fs, color=INK, va="center", ha="left")
    fig.savefig(out / name, dpi=200, transparent=True, bbox_inches="tight", pad_inches=0.04); plt.close(fig)
tex("agg_f1.png", r"$u_7 \;=\; 1\cdot u_{13} \,+\, 1\cdot u_{14} \,-\, 1\cdot u_{20}$")
tex("agg_f2.png", r"$u \;=\; E\,u_{\mathrm{good}}$,  $\quad E^{T}A\,E\,u_{\mathrm{good}} \;=\; E^{T}b$")
print("removed", removed, "good", good, "E", E.shape, "act", len(act))

# ---- figure 4: root cell and ill-posed cell in the reference frame of the root cell
c_ill = 6; c_root = int(agg.root[c_ill])
rv = [int(v) for v in mesh.cells[c_root]]          # root vertices
iv = [int(v) for v in mesh.cells[c_ill]]
# reference vertices: 13 -> (0,0), 14 -> (1,0), 20 -> (0,1)
ref = {13: (0, 0), 14: (1, 0), 20: (0, 1)}
a0, a1, a2 = P[13], P[14], P[20]
M = np.column_stack([a1 - a0, a2 - a0]); Minv = np.linalg.inv(M)
to_ref = lambda x: Minv @ (np.asarray(x) - a0)
fig, ax = plt.subplots(figsize=(6.4, 6.4))
ax.set_aspect("equal"); ax.axis("off"); fig.subplots_adjust(0, 0, 1, 1)
root_poly = np.array([ref[v] for v in rv], float)
ill_poly = np.array([to_ref(P[v]) for v in iv])
ax.add_patch(Polygon(root_poly, fc=BLUE, ec=B, lw=4.2, joinstyle="round"))
illp = Polygon(ill_poly, fc=ORANGE, ec=GREY, lw=1.6, hatch="////"); ax.add_patch(illp)
_th = np.linspace(0, 2*np.pi, 800)
disc = np.array([to_ref((R*np.cos(t), R*np.sin(t))) for t in _th])
inside = Polygon(disc, fc=BLUE, ec="none"); ax.add_patch(inside); inside.set_clip_path(illp)
ax.add_patch(Polygon(ill_poly, fc="none", ec=GREY, lw=1.6))
# boundary of the disc in reference coordinates
th = np.linspace(0, 2*np.pi, 800)
circ = np.array([to_ref((R*np.cos(t), R*np.sin(t))) for t in th])
keep = (circ[:, 0] > -0.6) & (circ[:, 0] < 1.9) & (circ[:, 1] > -1.4) & (circ[:, 1] < 1.5)
circ[~keep] = np.nan
ax.plot(circ[:, 0], circ[:, 1], color=DARK, lw=3.6)
# plane extension indicator: x7 and the arrow from the root
x7 = to_ref(P[7])
ax.annotate("", xy=x7, xytext=root_poly.mean(0), arrowprops=dict(arrowstyle="-|>", color=B, lw=2.4, shrinkA=6, shrinkB=10, ls="--"))
for v in rv:
    ax.plot(*ref[v], "o", ms=12, mfc=INK, mec="white", mew=1.5)
ax.plot(*x7, "o", ms=18, mfc=DARK, mec="white", mew=2)
# reference axes xi1, xi2 through vertex 13
for (dx, dy, lab, pos) in ((1, 0, r"$\xi_1$", (1.56, -0.12)), (0, 1, r"$\xi_2$", (0.04, 1.2))):
    ax.annotate("", xy=(1.5*dx + 0.0*dy - (0 if dx else 0), 1.15*dy + 0.0), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2, shrinkA=0, shrinkB=0, mutation_scale=22), zorder=1)
    ax.text(*pos, lab, fontsize=26, color=INK, ha="left" if dx else "left", va="top" if dx else "bottom")
ax.text(-0.06, -0.08, "13  (0, 0)", fontsize=18, fontweight="bold", color=INK, ha="right", va="top")
ax.text(1.04, 0.09, "14  (1, 0)", fontsize=18, fontweight="bold", color=INK, ha="left", va="bottom")
ax.text(-0.06, 1.0, "20  (0, 1)", fontsize=18, fontweight="bold", color=INK, ha="right", va="center")
ax.text(x7[0] + 0.07, x7[1] - 0.02, "7  (1, \u22121)", fontsize=20, fontweight="bold", color=DARK, ha="left", va="top")
ax.text(*(root_poly.mean(0) + (0.02, 0.12)), "root", fontsize=17, color=B, ha="center", fontweight="bold")
ax.set_xlim(-0.95, 2.1); ax.set_ylim(-1.3, 1.35)
fig.savefig(out / "agg_ref.png", dpi=170, transparent=True, bbox_inches="tight", pad_inches=0.05); plt.close(fig)
print("x7 ref", x7)
tex("agg_f3.png", r"$p(\xi)\;=\;u_{13}+(u_{14}-u_{13})\,\xi_1+(u_{20}-u_{13})\,\xi_2$", fs=32)
tex("agg_f4.png", r"$u_7=p(1,-1)=u_{13}+u_{14}-u_{20}$", fs=32)
tex("agg_phi.png", r"$\varphi_{13}(\xi)=1-\xi_1-\xi_2,\qquad \varphi_{14}(\xi)=\xi_1,\qquad \varphi_{20}(\xi)=\xi_2$", fs=30)
tex("agg_p.png", r"$p(\xi)=u_{13}\,\varphi_{13}(\xi)+u_{14}\,\varphi_{14}(\xi)+u_{20}\,\varphi_{20}(\xi)$", fs=30)
tex("agg_eval.png", r"$\xi=(1,-1):\quad \varphi_{13}=1,\;\varphi_{14}=1,\;\varphi_{20}=-1$", fs=30)
tex("agg_u7.png", r"$u_7=p(1,-1)=u_{13}+u_{14}-u_{20}$", fs=30)
