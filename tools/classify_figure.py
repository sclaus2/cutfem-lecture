"""All three cell classes of the flower mesh in the colours of the slide boxes (inside blue, cut orange, outside green).

Run from the repository root:   PYTHONPATH=. python tools/classify_figure.py OUTDIR      -> classify_all.png
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
print(geom.summary())
