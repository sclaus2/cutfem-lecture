"""Figures for 'pixels -> node value' and 'node values -> cut'. Run: PYTHONPATH=. python tools/image_embed_figures.py OUTDIR"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from scipy import ndimage as ndi
import minicut as mc

matplotlib.rcParams["mathtext.fontset"] = "cm"
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
INK, GREY, TITLE = "#1F2937", "#6e7a88", "#00509a"
COL = ["#d9701a", "#2a9d8f", "#8e44ad", "#1f6fbf"]       # corners 00, 10, 01, 11
FS = 15
B = mc.synthetic_scan() > 0.5
d = ndi.gaussian_filter(ndi.distance_transform_edt(~B) - ndi.distance_transform_edt(B), 1.5)
phi = mc.levelset_from_image(B, smooth=1.5)
mesh = mc.Mesh(45); geom = mc.CutGeometry(mesh, phi)
NODE = 358
x, y = mesh.nodes[NODE]
col, row = x * 299, (1 - y) * 299
i, j = int(np.floor(row)), int(np.floor(col)); t, s = row - i, col - j
v00, v10, v01, v11 = d[i, j], d[i, j + 1], d[i + 1, j], d[i + 1, j + 1]
w = [(1 - s) * (1 - t), s * (1 - t), (1 - s) * t, s * t]
vals = [v00, v10, v01, v11]
res = sum(a * b for a, b in zip(w, vals))
assert abs(res - phi(np.array([x]), np.array([y]))[0] * 299) < 1e-9
print("node", NODE, "s,t", s, t, "w", np.round(w, 3), "vals", np.round(vals, 2), "res", res)

# ---------- figure A: pixels -> node
fig, (a0, a1) = plt.subplots(1, 2, figsize=(12, 4.7), dpi=200, gridspec_kw={"width_ratios": [1, 1.15]})
cs, rs = np.arange(j - 3, j + 5), np.arange(i - 3, i + 5)
CC, RR = np.meshgrid(cs, rs)
a0.scatter(CC, RR, s=40, color="#9aa5b1", zorder=3)
for (c, r), k in zip([(j, i), (j + 1, i), (j, i + 1), (j + 1, i + 1)], range(4)):
    a0.scatter([c], [r], s=190, color=COL[k], zorder=4)
a0.add_patch(Rectangle((j, i), 1, 1, fc="none", ec=INK, lw=1.6, zorder=2))
a0.axvline(col, color=INK, lw=1.2, ls=(0, (4, 3)), zorder=1); a0.axhline(row, color=INK, lw=1.2, ls=(0, (4, 3)), zorder=1)
a0.scatter([col], [row], marker="*", s=520, color="#d0021b", edgecolor="white", linewidth=1.2, zorder=6)
a0.set_xlim(cs[0] - .5, cs[-1] + .5); a0.set_ylim(rs[-1] + .5, rs[0] - .5); a0.set_aspect("equal")
a0.set_xticks([]); a0.set_yticks([])
for sp in a0.spines.values(): sp.set_color("#c5cdd6")
a0.set_title("pixel centres and one mesh node", loc="left", fontsize=FS, fontweight="bold", color=TITLE)
a0.set_xlabel("dashed: mesh lines through the node", fontsize=FS - 1, color=GREY)

a1.set_xlim(-0.5, 1.5); a1.set_ylim(1.50, -0.32); a1.set_aspect("equal"); a1.axis("off")
rects = [(s, t, 1 - s, 1 - t), (0, t, s, 1 - t), (s, 0, 1 - s, t), (0, 0, s, t)]   # opposite rectangle of corner k
for k, (rx, ry, rw, rh) in enumerate(rects):
    a1.add_patch(Rectangle((rx, ry), rw, rh, fc=COL[k], alpha=0.22, ec="none"))
    a1.text(rx + rw / 2, ry + rh / 2, f"{w[k]:.2f}", ha="center", va="center", fontsize=FS + 1, fontweight="bold", color=COL[k])
a1.add_patch(Rectangle((0, 0), 1, 1, fc="none", ec=INK, lw=1.6))
for k, (cx, cy, ha, va, dx, dy) in enumerate([(0, 0, "right", "bottom", -.04, -.04), (1, 0, "left", "bottom", .04, -.04), (0, 1, "right", "top", -.04, .04), (1, 1, "left", "top", .04, .04)]):
    a1.scatter([cx], [cy], s=190, color=COL[k], zorder=5)
    a1.text(cx + dx, cy + dy, f"{vals[k]:.2f}".replace("-", "−"), ha=ha, va=va, fontsize=FS + 1, color=COL[k], fontweight="bold")
a1.scatter([s], [t], marker="*", s=520, color="#d0021b", edgecolor="white", linewidth=1.2, zorder=6)
a1.set_title("weight = area of the opposite rectangle", loc="left", fontsize=FS, fontweight="bold", color=TITLE)
a1.text(0.5, 1.22, r"$\varphi=0.10\,(-0.43)+0.10\,(-1.28)$", ha="center", va="center", fontsize=FS + 1, color=INK)
a1.text(0.5, 1.40, r"$+\,0.39\,(-1.28)+0.41\,(-2.08)=%.2f$" % res, ha="center", va="center", fontsize=FS + 1, color=INK)
fig.subplots_adjust(0.01, 0.07, 0.99, 0.9, wspace=0.05); fig.savefig(out / "img_e1.png"); plt.close(fig)

# ---------- figure B: node values -> cut
cell = [c for c in range(mesh.n_cells) if geom.cell_type[c] == mc.CUT and NODE in mesh.cells[c] and set(mesh.cells[c].tolist()) == {312, 358, 359}][0]
vs = mesh.cells[cell]; ph = geom.phi * 299
P = {int(k): mesh.nodes[k] * 299 for k in vs}
A, Bv, C = 358, 312, 359
pA, pB, pC = P[A], P[Bv], P[C]
fA, fB, fC = ph[A], ph[Bv], ph[C]
sB = fA / (fA - fB); sC = fA / (fA - fC)
qB, qC = pA + sB * (pB - pA), pA + sC * (pC - pA)
print("cell", cell, "phi", fA, fB, fC, "frac", sB, sC, "inside fraction", sB * sC)
fig, (b0, b1) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=200, gridspec_kw={"width_ratios": [1.1, 1]})
o = pA
tri = lambda *p: Polygon([q - o for q in p], closed=True)
b0.add_patch(Polygon([pA - o, pB - o, pC - o], closed=True, fc="#F9C48F", ec=INK, lw=2.2, alpha=0.75))
b0.add_patch(Polygon([pA - o, qB - o, qC - o], closed=True, fc="#9CC3EA", ec="none"))
b0.plot([qB[0] - o[0], qC[0] - o[0]], [qB[1] - o[1], qC[1] - o[1]], color="k", lw=4, solid_capstyle="round", zorder=5)
for p, f, ha, dx, dy in [(pA, fA, "left", 0.25, -0.55), (pB, fB, "right", -0.45, -0.55), (pC, fC, "left", 0.25, 0.2)]:
    b0.scatter([p[0] - o[0]], [p[1] - o[1]], s=170, color=INK, zorder=6)
    b0.text(p[0] - o[0] + dx, p[1] - o[1] + dy, f"φ = {f:.2f}".replace("-", "−"), ha=ha, fontsize=FS + 1, fontweight="bold", color=INK)
for q, tx, ty, ha, txt in [(qB, -0.1, 0.5, "center", f"{sB:.2f}"), (qC, 0.3, 0.0, "left", f"{sC:.2f}")]:
    b0.scatter([q[0] - o[0]], [q[1] - o[1]], s=170, color="#d0021b", zorder=7, edgecolor="white", linewidth=1.2)
b0.text(qB[0] - o[0], qB[1] - o[1] - 1.5, f"{sB:.2f} of the edge", ha="center", va="top", fontsize=FS, color="#d0021b", fontweight="bold")
b0.text(qC[0] - o[0] + 0.5, qC[1] - o[1], f"{sC:.2f} of the edge", ha="left", va="center", fontsize=FS, color="#d0021b", fontweight="bold")
b0.set_xlim(-8.6, 3.0); b0.set_ylim(-4.6, 7.6); b0.set_aspect("equal"); b0.axis("off")
b0.set_title("one triangle, φ at its nodes", loc="left", fontsize=FS, fontweight="bold", color=TITLE)
b1.axis("off")
b1.set_title("zero of φ on an edge a → b", loc="left", fontsize=FS, fontweight="bold", color=TITLE)
b1.text(0.0, 0.80, r"$\varphi_h$ is linear on each edge, so it is zero at", fontsize=FS + 1, color=INK, transform=b1.transAxes)
b1.text(0.0, 0.60, r"$x^{*}=x_a+\dfrac{\varphi_a}{\varphi_a-\varphi_b}\,(x_b-x_a)$", fontsize=FS + 5, color=INK, transform=b1.transAxes)
b1.text(0.0, 0.33, r"$\dfrac{-1.52}{-1.52-3.99}=%.2f,\qquad \dfrac{-1.52}{-1.52-3.27}=%.2f$" % (sB, sC), fontsize=FS + 3, color=INK, transform=b1.transAxes)
b1.text(0.0, 0.10, "the black segment joining the two zeros is the\npiece of Γ in this triangle; it cuts off %.0f%%\nof the triangle (blue, inside Ω)" % (100 * sB * sC), fontsize=FS + 1, color=INK, transform=b1.transAxes, va="center")
fig.subplots_adjust(0.01, 0.02, 0.99, 0.9, wspace=0.04); fig.savefig(out / "img_e2.png"); plt.close(fig)

# ---------- figure C: the background mesh box and how to find the pixel box of a node
fig, (c0, c1) = plt.subplots(1, 2, figsize=(12, 4.8), dpi=200, gridspec_kw={"width_ratios": [1, 1.25]})
c0.imshow(B, extent=(0, 1, 0, 1), origin="upper", cmap=matplotlib.colors.ListedColormap(["#F3D2B0", "#CFE2F5"]), interpolation="nearest")
ks = np.linspace(0, 1, 46)
c0.vlines(ks, 0, 1, color="#4b5563", lw=0.35, alpha=0.55); c0.hlines(ks, 0, 1, color="#4b5563", lw=0.35, alpha=0.55)
c0.add_patch(Rectangle((0, 0), 1, 1, fc="none", ec=INK, lw=2.4))
c0.scatter([x], [y], marker="*", s=420, color="#d0021b", edgecolor="white", linewidth=1.2, zorder=6)
c0.annotate("node (x, y)", xy=(x, y), xytext=(0.30, 0.93), fontsize=FS, color="#d0021b", fontweight="bold", arrowprops=dict(arrowstyle="->", color="#d0021b", lw=1.6), va="center")
c0.set_xlim(-0.14, 1.14); c0.set_ylim(-0.24, 1.08); c0.set_aspect("equal"); c0.axis("off")
c0.text(0, -0.04, "x0", ha="center", va="top", fontsize=FS, color=INK); c0.text(1, -0.04, "x1", ha="center", va="top", fontsize=FS, color=INK)
c0.text(-0.03, 0, "y0", ha="right", va="center", fontsize=FS, color=INK); c0.text(-0.03, 1, "y1", ha="right", va="center", fontsize=FS, color=INK)
c0.set_title("the box [x0, x1] × [y0, y1]", loc="left", fontsize=FS, fontweight="bold", color=TITLE)
c0.text(0.5, -0.17, "image = pixels, grey lines = the 45 × 45 mesh", ha="center", va="center", fontsize=FS - 1, color=GREY)

nc, nr = 6, 5
cs, rs = np.arange(j - 2, j + 4), np.arange(i - 2, i + 3)
CC, RR = np.meshgrid(cs, rs)
c1.scatter(CC, RR, s=70, color="#9aa5b1", zorder=3)
for (c, r), k in zip([(j, i), (j + 1, i), (j, i + 1), (j + 1, i + 1)], range(4)):
    c1.scatter([c], [r], s=300, color=COL[k], zorder=4)
c1.add_patch(Rectangle((j, i), 1, 1, fc="none", ec=INK, lw=1.8, zorder=2))
c1.scatter([col], [row], marker="*", s=620, color="#d0021b", edgecolor="white", linewidth=1.2, zorder=6)
top = rs[0] - 0.75
for c, lab in zip(cs, ["j−2", "j−1", "j", "j+1", "j+2", "j+3"]):
    c1.text(c, top, lab, ha="center", va="bottom", fontsize=FS, color=INK)
for r, lab in zip(rs, ["i−2", "i−1", "i", "i+1", "i+2"]):
    c1.text(cs[0] - 0.6, r, lab, ha="right", va="center", fontsize=FS, color=INK)
# s and t
c1.annotate("", xy=(col, i - 0.35), xytext=(j, i - 0.35), arrowprops=dict(arrowstyle="<->", color="#d0021b", lw=1.8))
c1.text((col + j) / 2, i - 0.45, "s", ha="center", va="bottom", fontsize=FS + 2, color="#d0021b", fontweight="bold")
c1.annotate("", xy=(j - 0.35, row), xytext=(j - 0.35, i), arrowprops=dict(arrowstyle="<->", color="#d0021b", lw=1.8))
c1.text(j - 0.45, (row + i) / 2, "t", ha="right", va="center", fontsize=FS + 2, color="#d0021b", fontweight="bold")
c1.set_xlim(cs[0] - 1.9, cs[-1] + 0.6); c1.set_ylim(rs[-1] + 0.6, rs[0] - 1.2); c1.set_aspect("equal"); c1.axis("off")
c1.set_title("zoom: the four pixel centres around the node", loc="left", fontsize=FS, fontweight="bold", color=TITLE)
c1.text(cs[-1] + 0.5, rs[-1] + 0.45, "col = j + s,  row = i + t", ha="right", va="bottom", fontsize=FS, color=INK)
fig.subplots_adjust(0.01, 0.02, 0.99, 0.9, wspace=0.03); fig.savefig(out / "img_e0.png"); plt.close(fig)
