"""All three cell classes of the flower mesh in the colours of the slide boxes (inside blue, cut orange, outside green).

Run from the repository root:   PYTHONPATH=. python tools/classify_figure.py OUTDIR      -> classify_all.png, activemesh_all.png
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection

import minicut as mc

out = Path(sys.argv[1] if len(sys.argv) > 1 else "fig_out"); out.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, GREEN, INK = "#CFE2F5", "#F9C48F", "#CFEBD8", "#151a2a"   # same as the boxes on the slide

mesh = mc.Mesh(18, box=(-1, -1, 1, 1))
x, y = mesh.nodes[:, 0], mesh.nodes[:, 1]
r = 0.48 * (1 + 0.18 * np.cos(6 * np.arctan2(y, x)))
geom = mc.CutGeometry(mesh, np.sqrt(x**2 + y**2) - r, order=2)
t = geom.cell_type
V = mesh.nodes[mesh.cells]
cols = [BLUE if k == mc.INSIDE else (ORANGE if k == mc.CUT else GREEN) for k in t]

fig, ax = plt.subplots(figsize=(4.0, 4.2))
ax.set_aspect("equal"); ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.axis("off")
fig.subplots_adjust(0.01, 0.01, 0.99, 0.99)
ax.add_collection(PolyCollection(V, facecolors=cols, edgecolors="#8d99a6", linewidths=0.5))
ax.add_collection(LineCollection(geom.segments, colors=INK, linewidths=2.6))
fig.savefig(out / "classify_all.png", dpi=250); plt.close(fig)

# active mesh figure: same colours, thick outline around the active cells (inside + cut)
act = t != mc.OUTSIDE
fc = mesh.facet_cells
sel = act[fc[:, 0]] != act[fc[:, 1]]
fig, ax = plt.subplots(figsize=(4.0, 4.2))
ax.set_aspect("equal"); ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.axis("off")
fig.subplots_adjust(0.01, 0.01, 0.99, 0.99)
cols_a = ["white" if k == mc.OUTSIDE else c for k, c in zip(t, cols)]  # inactive cells white
ax.add_collection(PolyCollection(V, facecolors=cols_a, edgecolors="#c5ccd4", linewidths=0.5))
ax.add_collection(LineCollection(mesh.nodes[mesh.facet_nodes[sel]], colors="#1F2937", linewidths=3.4, capstyle="round"))
ax.add_collection(LineCollection(geom.segments, colors=INK, linewidths=2.0))
fig.savefig(out / "activemesh_all.png", dpi=250); plt.close(fig)
# Example 1 figures in the same colours: inactive (outside) cells white
def panel(name, keep):
    fig, ax = plt.subplots(figsize=(4.0, 4.2))
    ax.set_aspect("equal"); ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.axis("off")
    fig.subplots_adjust(0.01, 0.01, 0.99, 0.99)
    cc = [c if k in keep else "white" for k, c in zip(t, cols)]
    ax.add_collection(PolyCollection(V, facecolors=cc, edgecolors="#c5ccd4", linewidths=0.5))
    ax.add_collection(LineCollection(geom.segments, colors=INK, linewidths=2.4))
    fig.savefig(out / name, dpi=250); plt.close(fig)


panel("first_active2.png", {mc.INSIDE, mc.CUT})
panel("ps2_inside2.png", {mc.INSIDE})
panel("ps2_cut2.png", {mc.CUT})
print(geom.summary())
