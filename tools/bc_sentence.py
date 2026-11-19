"""Intro sentence of the Dirichlet slide with Gamma_D typeset by matplotlib mathtext (the slide editor drops HTML subscripts)."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fam = "Arial" if any(f.name == "Arial" for f in fm.fontManager.ttflist) else "DejaVu Sans"
plt.rcParams.update({"font.family": fam, "mathtext.fontset": "custom",
                     "mathtext.rm": fam, "mathtext.it": fam + ":italic", "mathtext.bf": fam + ":bold"})
out = sys.argv[1]
W, PX = 1664, 41            # slide px width, font px
dpi = 100
fig = plt.figure(figsize=(W / dpi, 2.2 * PX * 1.35 / dpi))
lines = [r"Lecture 2 fixed the nodal values on $\mathrm{\Gamma_D}$ and solved for the rest. Now no node lies",
         r"on $\mathrm{\Gamma_D}$: the boundary runs through the cells."]
for i, t in enumerate(lines):
    fig.text(0, 1 - (i + 0.62) / 2.0, t, fontsize=PX * 72 / dpi, color="#3b3b3b", va="center", ha="left")
fig.savefig(out, dpi=2 * dpi, transparent=True)
