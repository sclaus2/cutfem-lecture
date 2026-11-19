"""Gamma_D as a small transparent image whose baseline matches 41 px Arial text in a 1.35 line box (the slide editor drops HTML subscripts)."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fam = "Arial" if any(f.name == "Arial" for f in fm.fontManager.ttflist) else "DejaVu Sans"
plt.rcParams.update({"font.family": fam, "mathtext.fontset": "custom", "mathtext.rm": fam, "mathtext.it": fam + ":italic"})
PX, LH, W = 41, 41 * 1.35, 48            # font px, line box px, image width px
BASE = (LH - (0.905 + 0.212) * PX) / 2 + 0.905 * PX   # baseline distance from top of the line box
dpi = 100
fig = plt.figure(figsize=(W / dpi, LH / dpi))
fig.text(0, 1 - BASE / LH, r"$\mathrm{\Gamma_D}$", fontsize=PX * 72 / dpi, color="#3b3b3b", va="baseline", ha="left")
fig.savefig(sys.argv[1], dpi=3 * dpi, transparent=True)
print(W, round(LH, 1))
