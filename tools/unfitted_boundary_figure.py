"""Unfitted boundary: the flower curve running through a background mesh (no node on it).

Run from the repository root:   PYTHONPATH=. python tools/unfitted_boundary_figure.py OUTDIR  -> unfitted_boundary.png
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

import minicut as mc

out = Path(sys.argv[1] if len(sys.argv) > 1 else "fig_out"); out.mkdir(parents=True, exist_ok=True)
mesh = mc.Mesh(12, box=(-1, -1, 1, 1))
x, y = mesh.nodes[:, 0], mesh.nodes[:, 1]
fig, ax = plt.subplots(figsize=(4.0, 4.0))
ax.set_aspect("equal"); ax.set_xlim(-1.02, 1.02); ax.set_ylim(-1.02, 1.02); ax.axis("off")
fig.subplots_adjust(0.01, 0.01, 0.99, 0.99)
V = mesh.nodes[mesh.cells]
edges = np.concatenate([V[:, [0, 1]], V[:, [1, 2]], V[:, [2, 0]]])
ax.add_collection(LineCollection(edges, colors="#8d99a6", linewidths=0.8))
ax.plot(x, y, "o", ms=3.2, color="#6e7a88")
th = np.linspace(0, 2 * np.pi, 600)
rr = 0.48 * (1 + 0.18 * np.cos(6 * th))   # exact flower, not the facets
ax.plot(rr * np.cos(th), rr * np.sin(th), color="#B34F00", lw=3.4, solid_capstyle="round")
fig.savefig(out / "unfitted_boundary.png", dpi=250, transparent=True); plt.close(fig)
