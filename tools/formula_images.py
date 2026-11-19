"""LaTeX-style (mathtext, Computer Modern) formula images for the slides. Run: python tools/formula_images.py OUTDIR
Each image is rendered at 30 pt / 200 dpi: on a slide, width_css = png_width * 0.36 gives 30 px text."""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["mathtext.fontset"] = "cm"
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
INK = "#1F2937"
F = {
 "f_ghost": r"$+\,\gamma_g\, h \sum_{F}\int_{F} [\![\partial_n u]\!]\,[\![\partial_n v]\!]\; ds$",
 "f_aggr": r"$u_i=\sum_k \lambda_k(x_i)\,u_k$,   $E^{T}A\,E\,u_{\mathrm{good}}=E^{T}b$",
 "f_disc": r"$\varphi(x)=|x-c|-R$",
 "f_disc2": r"$\varphi=\sqrt{(x-c_x)^2+(y-c_y)^2}-R$",
 "f_flower": r"$\varphi=\sqrt{x^2+y^2}-0.48\,(1+0.18\cos 6\theta)$",
 "f_lag3": r"$\int_\Gamma\left(\frac{\partial u}{\partial n}+\lambda\right)v\,ds\;\Rightarrow\;\lambda=-\frac{\partial u}{\partial n}$",
 "f_poisson": r"$-\Delta u=1\ \mathrm{in}\ \Omega,\qquad u=0\ \mathrm{on}\ \Gamma$",
 "f_turn": r"$-\Delta u=f\ \mathrm{in}\ \Omega_\theta,\qquad u=0\ \mathrm{on}\ \Gamma_\theta$",
 "f_kappa": r"$\kappa(A)\sim 1/\eta$",
}
for k, s in F.items():
    fig = plt.figure(figsize=(8, 1)); fig.text(0.0, 0.5, s, fontsize=30, color=INK, va="center", ha="left")
    fig.savefig(out / (k + ".png"), dpi=200, transparent=True, bbox_inches="tight", pad_inches=0.03); plt.close(fig)
from PIL import Image
for k in F:
    w, h = Image.open(out / (k + ".png")).size; print(k, w, h, "css@30px:", round(w*0.36), round(h*0.36))
