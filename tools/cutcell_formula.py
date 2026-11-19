"""Formula strip for the 'Cutting one cell' slide: integral over T cap Omega and over Gamma cap T."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"mathtext.fontset": "cm"})
out = sys.argv[1] if len(sys.argv) > 1 else "cutcell_formula.png"
fig = plt.figure(figsize=(15.6, 0.9))
tex = (r"$\int_{T\cap\Omega} f\,dx=\sum_{K\subset T\cap\Omega}\,\int_K f\,dx"
       r"\approx\sum_{K}\,\sum_{q}\,w_q\,f(x_q)$"
       r"$\qquad\qquad\int_{\Gamma\cap T} g\,ds\approx\sum_{q}\,w_q\,g(x_q)$")
fig.text(0.0, 0.5, tex, fontsize=30, color="#3b3b3b", va="center", ha="left")
fig.savefig(out, dpi=200, transparent=True, bbox_inches="tight", pad_inches=0.05)
