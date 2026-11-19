"""Step-by-step figures for the image -> level set recipe. Run: PYTHONPATH=. python tools/image_steps_figures.py OUTDIR [r0 c0]"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from matplotlib.collections import PolyCollection, LineCollection
from scipy import ndimage as ndi
import minicut as mc

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
r0 = int(sys.argv[2]) if len(sys.argv) > 2 else 58
c0 = int(sys.argv[3]) if len(sys.argv) > 3 else 54
N = 7                                   # zoom window: N x N pixels
BLUE, ORANGE, DARK, INK, GREY, TITLE = "#CFE2F5", "#F9C48F", "#B34F00", "#1F2937", "#6e7a88", "#00509a"
FS = 13
FS2 = 11.5

scan = mc.synthetic_scan()
B = scan > 0.5
d_in = ndi.distance_transform_edt(B)
d_out = ndi.distance_transform_edt(~B)
phi_px = np.where(B, -d_in, d_out)
sm = ndi.gaussian_filter(phi_px, 1.5)
sl = (slice(r0, r0 + N), slice(c0, c0 + N))

def grid(ax, vals, fmt, cmap, vmin, vmax, title, sub=None, fs=None):
    ax.imshow(vals, cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
    for i in range(N):
        for j in range(N):
            v = vals[i, j]
            ax.text(j, i, fmt(v), ha="center", va="center", fontsize=fs or FS, color=INK)
    ax.set_xticks(np.arange(-.5, N, 1), minor=True); ax.set_yticks(np.arange(-.5, N, 1), minor=True)
    ax.grid(which="minor", color="white", lw=1.5); ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold", color=TITLE)
    if sub: ax.set_xlabel(sub, fontsize=FS, color=GREY)

bw = matplotlib.colors.ListedColormap(["#F3D2B0", "#CFE2F5"])

# ---- step 1: scan -> B
fig, ax = plt.subplots(1, 3, figsize=(12, 4.3), dpi=200, gridspec_kw={"width_ratios": [1.15, 1, 1]})
ax[0].imshow(scan, cmap="gray", vmin=-0.2, vmax=1.2)
ax[0].add_patch(Rectangle((c0 - .5, r0 - .5), N, N, fc="none", ec="#d0021b", lw=2.5))
ax[0].set_xticks([]); ax[0].set_yticks([])
ax[0].set_title("scan: one grey value per pixel", loc="left", fontsize=15, fontweight="bold", color=TITLE)
ax[0].set_xlabel("300 × 300 pixels", fontsize=FS, color=GREY)
grid(ax[1], scan[sl], lambda v: f"{v:.2f}", "gray", -0.2, 1.2, "zoom: the grey values", "red square, 7 × 7 pixels")
grid(ax[2], B[sl].astype(float), lambda v: "True" if v > .5 else "False", bw, 0, 1, "B = scan > 0.5", "same 7 × 7 pixels")
fig.subplots_adjust(0.01, 0.1, 0.99, 0.9, wspace=0.08); fig.savefig(out / "img_s1.png"); plt.close(fig)

# ---- step 2: distances
fig, ax = plt.subplots(1, 4, figsize=(12, 3.4), dpi=200)
grid(ax[0], B[sl].astype(float), lambda v: "T" if v > .5 else "F", bw, 0, 1, "B", "True = matrix")
grid(ax[1], d_in[sl], lambda v: f"{v:.1f}".rstrip("0").rstrip(".") if v else "0", "Blues", 0, 6, "d_in", "inside: distance to pore")
grid(ax[2], d_out[sl], lambda v: f"{v:.1f}".rstrip("0").rstrip(".") if v else "0", "Oranges", 0, 6, "d_out", "outside: distance to matrix")
grid(ax[3], phi_px[sl], lambda v: f"{v:.1f}".rstrip("0").rstrip(".") if v else "0", "RdBu_r", -4, 4, "φ  (pixels)", "−d_in in B, +d_out elsewhere", fs=FS2)
fig.subplots_adjust(0.01, 0.12, 0.99, 0.86, wspace=0.08); fig.savefig(out / "img_s2.png"); plt.close(fig)

# ---- step 3: smoothing
W = 26
rr, cc = slice(r0 - 10, r0 - 10 + W), slice(c0 - 10, c0 - 10 + W)
fig, ax = plt.subplots(1, 3, figsize=(12, 4.2), dpi=200, gridspec_kw={"width_ratios": [1, 1, 1.15]})
for a, f, t in ((ax[0], phi_px, "before smoothing"), (ax[1], sm, "after Gaussian filter, σ = 1.5")):
    a.imshow(f[rr, cc], cmap="RdBu_r", vmin=-6, vmax=6, interpolation="nearest")
    a.contour(f[rr, cc], levels=[0], colors="k", linewidths=2.2)
    a.set_xticks([]); a.set_yticks([])
    a.set_title(t, loc="left", fontsize=15, fontweight="bold", color=TITLE)
    a.set_xlabel("zero contour in black", fontsize=FS, color=GREY)
# profile along a row through the boundary
row = r0 + 3
x = np.arange(c0 - 10, c0 + 16)
ax[2].axhline(0, color=GREY, lw=1)
ax[2].plot(x, phi_px[row, x], "o-", color=ORANGE, ms=5, lw=2, label="before")
ax[2].plot(x, sm[row, x], "-", color=TITLE, lw=3, label="after")
ax[2].legend(fontsize=FS, frameon=False, loc="upper left"); ax[2].tick_params(labelsize=FS)
ax[2].set_title("φ along one row of pixels", loc="left", fontsize=15, fontweight="bold", color=TITLE)
ax[2].set_xlabel("pixel column", fontsize=FS, color=GREY)
for s in ("top", "right"): ax[2].spines[s].set_visible(False)
fig.subplots_adjust(0.01, 0.16, 0.99, 0.88, wspace=0.12); fig.savefig(out / "img_s3.png"); plt.close(fig)

# ---- step 4: nodes of the background mesh
phi = mc.levelset_from_image(B, smooth=1.5)
mesh = mc.Mesh(45)
geom = mc.CutGeometry(mesh, phi)
# window in physical units that covers the pixel window
x0w, x1w = (c0 - 10) / 299.0, (c0 - 10 + W) / 299.0
y1w, y0w = 1 - (r0 - 10) / 299.0, 1 - (r0 - 10 + W) / 299.0
fig, ax = plt.subplots(1, 2, figsize=(12, 5.0), dpi=200)
g = np.linspace(0, 1, 600); X, Y = np.meshgrid(g, g)
Pf = phi(X, Y)
V = mesh.nodes[mesh.cells]
for k, a in enumerate(ax):
    a.imshow(B[::-1], cmap=bw, extent=(0, 1, 0, 1), origin="lower", interpolation="nearest", alpha=0.55)
    a.contour(X, Y, Pf, levels=[0], colors=TITLE, linewidths=2.6)
    a.set_xlim(x0w, x1w); a.set_ylim(y0w, y1w); a.set_aspect("equal"); a.set_xticks([]); a.set_yticks([])
    for s in a.spines.values(): s.set_visible(False)
tris = PolyCollection(V, facecolors="none", edgecolors="#4b5563", linewidths=1.0)
ax[1].add_collection(tris)
nodes = mesh.nodes; pv = geom.phi
sel = (nodes[:, 0] > x0w) & (nodes[:, 0] < x1w) & (nodes[:, 1] > y0w) & (nodes[:, 1] < y1w)
ax[1].scatter(nodes[sel, 0], nodes[sel, 1], c=np.where(pv[sel] < 0, "#1f6fbf", "#d9701a"), s=110, zorder=5, edgecolor="white", linewidth=1.5)
ax[1].add_collection(LineCollection(geom.segments, colors="k", linewidths=2.6, zorder=4))
ax[0].set_title("φ is known at every pixel", loc="left", fontsize=15, fontweight="bold", color=TITLE)
ax[1].set_title("keep φ only at the mesh nodes", loc="left", fontsize=15, fontweight="bold", color=TITLE)
ax[0].set_xlabel("blue line: φ = 0 of the pixel image", fontsize=FS, color=GREY)
ax[1].set_xlabel("dots: sign of φ at the nodes   black: the cut geometry", fontsize=FS, color=GREY)
fig.subplots_adjust(0.01, 0.1, 0.99, 0.9, wspace=0.06); fig.savefig(out / "img_s4.png"); plt.close(fig)
print("window", r0, c0, "phi window rows", phi_px[sl].min(), phi_px[sl].max())
