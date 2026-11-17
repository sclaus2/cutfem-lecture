"""Four-panel figure of 'Example 1 · From an image to a level set', made with minicut.

Run from the repository root:   PYTHONPATH=. python tools/slide_image_figure.py OUT.png
"""

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from scipy import ndimage as ndi

import minicut as mc

out = sys.argv[1] if len(sys.argv) > 1 else "img_four_panels.png"

scan = mc.synthetic_scan()
B = scan > 0.5
phi = mc.levelset_from_image(B, smooth=1.5)
mesh = mc.Mesh(45)
geom = mc.CutGeometry(mesh, phi)
print(geom.summary())

BLUE, ORANGE, TITLE = "#d3e3f3", "#e8a96a", "#00509A"
fig, ax = plt.subplots(1, 4, figsize=(12, 3.26), dpi=200)
titles = ["1  Image (greyscale)", "2  Segmentation (threshold)", "3  Signed distance  φ", "4  Cut on the background mesh"]
for a, t in zip(ax, titles):
    a.set_title(t, loc="left", fontsize=11, fontweight="bold", color=TITLE)
    a.set_xticks([]); a.set_yticks([]); a.set_aspect("equal")
    for sp in a.spines.values():
        sp.set_visible(False)

ax[0].imshow(scan, cmap="gray", vmin=-0.2, vmax=1.2, origin="upper")

ax[1].imshow(np.where(B, 0.0, 1.0), cmap=matplotlib.colors.ListedColormap([BLUE, "white"]), origin="upper")
ax[1].contour(B.astype(float), levels=[0.5], colors="k", linewidths=0.8)

g = np.linspace(0, 1, 256)
X, Y = np.meshgrid(g, g)
P = phi(X, Y)
lim = np.abs(P).max()
ax[2].imshow(P, cmap="RdBu_r", vmin=-25 / 299, vmax=25 / 299, origin="lower", extent=(0, 1, 0, 1))
ax[2].contour(X, Y, P, levels=[0.0], colors="k", linewidths=1.2)

V = mesh.nodes[mesh.cells]
cols = [BLUE if t == mc.INSIDE else (ORANGE if t == mc.CUT else "white") for t in geom.cell_type]
ax[3].add_collection(PolyCollection(V, facecolors=cols, edgecolors="#9aa5b1", linewidths=0.25))
ax[3].add_collection(LineCollection(geom.segments, colors="k", linewidths=1.1))
ax[3].set_xlim(0, 1); ax[3].set_ylim(0, 1)

fig.subplots_adjust(0.005, 0.01, 0.995, 0.92, wspace=0.03)
fig.savefig(out)
print("wrote", out)
