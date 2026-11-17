"""Sign-convention picture of the lecture with the flower of Example 1 (phi<0 inside, normals on Gamma).

Run:   python tools/levelset_flower_figure.py OUTDIR      -> levelset_flower.png
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

out = Path(sys.argv[1] if len(sys.argv) > 1 else "fig_out"); out.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, INK, GREY = "#00509A", "#C2570C", "#3a3d40", "#6e6e6e"
plt.rcParams["font.family"] = ["Arial", "Helvetica", "DejaVu Sans"]


def phi(x, y):
    return np.sqrt(x**2 + y**2) - 0.48 * (1 + 0.18 * np.cos(6 * np.arctan2(y, x)))


fig, ax = plt.subplots(figsize=(5.0, 5.0))
ax.set_aspect("equal"); ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_color("#9aa5b1"); s.set_linewidth(1.2)
fig.subplots_adjust(0.01, 0.01, 0.99, 0.99)

th = np.linspace(0, 2 * np.pi, 721)
r = 0.48 * (1 + 0.18 * np.cos(6 * th))
bx, by = r * np.cos(th), r * np.sin(th)
ax.fill(bx, by, color="#D0E2F3", zorder=1)
ax.plot(np.r_[bx, bx[0]], np.r_[by, by[0]], color=INK, lw=3.2, zorder=3)

# outward normals n = grad(phi)/|grad(phi)| at a few boundary points (central differences)
e = 1e-6
for t0 in np.deg2rad([40, 100, 195, 290, 335]):
    rr = 0.48 * (1 + 0.18 * np.cos(6 * t0)); x0, y0 = rr * np.cos(t0), rr * np.sin(t0)
    g = np.array([(phi(x0 + e, y0) - phi(x0 - e, y0)) / (2 * e), (phi(x0, y0 + e) - phi(x0, y0 - e)) / (2 * e)])
    n = g / np.linalg.norm(g)
    ax.annotate("", xy=(x0 + 0.27 * n[0], y0 + 0.27 * n[1]), xytext=(x0, y0), zorder=4,
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=2.4, mutation_scale=20))
ax.text(0, 0, "φ < 0\nΩ", ha="center", va="center", fontsize=22, fontweight="bold", color=BLUE, linespacing=1.2, zorder=5)
ax.text(-0.93, 0.86, "φ > 0", ha="left", va="center", fontsize=22, color=GREY)
ax.text(0.9, 0.86, "n = ∇φ/|∇φ|", ha="right", va="center", fontsize=19, fontweight="bold", color=ORANGE)
ax.text(0.9, -0.84, "Γ: φ = 0", ha="right", va="center", fontsize=19, fontweight="bold", color=INK)
fig.savefig(out / "levelset_flower.png", dpi=320); plt.close(fig)
