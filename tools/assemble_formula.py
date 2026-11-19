"""Matrix assembled over the active cells (inside, cut volume, cut interface), mathtext. Run: python tools/assemble_formula.py OUT.png"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"mathtext.fontset": "cm"})
FS = 30 * 72 / 100
INK, GREY = "#3b3b3b", "#6e6e6e"
fig = plt.figure(figsize=(9.0, 2.6))
rows = [(0.84, r"$A_{ij}=\sum_{T\ \mathrm{inside}}\int_T \nabla\psi_j\cdot\nabla\psi_i\,dx$", "inside cells"),
        (0.50, r"$\quad+\sum_{T\ \mathrm{cut}}\int_{T\cap\Omega} \nabla\psi_j\cdot\nabla\psi_i\,dx$", "cut cells, volume part"),
        (0.16, r"$\quad+\sum_{T\ \mathrm{cut}}\int_{\Gamma\cap T}\left(\mathrm{Nitsche\ terms}\right)ds$", "cut cells, boundary part")]
for y, tex, lab in rows:
    fig.text(0.0, y, tex, fontsize=FS, color=INK, va="center")
    fig.text(0.54, y, lab, fontsize=FS * 0.8, color=GREY, va="center", family="Arial")
fig.savefig(sys.argv[1], dpi=300, transparent=True, bbox_inches="tight", pad_inches=0.04)
