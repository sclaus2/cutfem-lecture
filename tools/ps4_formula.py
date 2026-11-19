"""Variational form of the 'Minicut: the variational form' slide, typeset with matplotlib mathtext (Computer Modern)."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"mathtext.fontset": "cm"})
fig = plt.figure(figsize=(8.8, 1.5))
FS = 30 * 72 / 100   # 30 px at 100 dpi
INK, GREY, BLUE = "#3b3b3b", "#6e6e6e", "#00509a"
fig.text(0.0, 0.74, r"$a(u,v)=\int_\Omega \nabla u\cdot\nabla v\,dx$", fontsize=FS, color=INK, va="center")
fig.text(0.56, 0.74, r"stiffness", fontsize=FS * 0.8, color=GREY, va="center", family="Arial")
fig.text(0.03, 0.22, r"$-\int_\Gamma\left(\partial_n u\,v+u\,\partial_n v\right)ds+\frac{\gamma}{h}\int_\Gamma u\,v\,ds$", fontsize=FS, color=INK, va="center")
fig.text(0.56, 0.22, r"Nitsche", fontsize=FS * 0.8, color=GREY, va="center", family="Arial")
fig.savefig(sys.argv[1], dpi=300, transparent=True, bbox_inches="tight", pad_inches=0.04)
