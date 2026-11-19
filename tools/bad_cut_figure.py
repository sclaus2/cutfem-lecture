"""One triangle cut at three positions: good cut, small cut, bad cut (sliver). Run: python tools/bad_cut_figure.py OUTDIR"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, DARK, INK, GREY = "#CFE2F5", "#F9C48F", "#B34F00", "#1F2937", "#6e7a88"
for name, t in (("good", 0.7), ("small", 0.2), ("bad", 0.03)):
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-0.16, 1.16); ax.set_ylim(-0.16, 1.16)
    fig.subplots_adjust(0, 0, 1, 1)
    ax.add_patch(Polygon([(0, 0), (1, 0), (0, 1)], fc=ORANGE, ec=GREY, lw=2.2, joinstyle="round"))
    ax.add_patch(Polygon([(0, 0), (t, 0), (0, t)], fc=BLUE, ec="none"))
    ax.plot([t, 0], [0, t], color=DARK, lw=3.6, solid_capstyle="round")
    ax.plot([0], [0], "o", ms=13, mfc=INK, mec=INK)
    for p in ((1, 0), (0, 1)):
        ax.plot(*p, "o", ms=13, mfc="white", mec=INK, mew=2.4)
    fig.savefig(out / f"badcut_{name}.png", dpi=200, transparent=True); plt.close(fig)
