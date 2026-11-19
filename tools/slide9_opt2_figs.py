"""Figures for the two-parameter optimisation slides (needs opt2_grid.npz from slide9_opt2.py).
Run: python slide9_opt2_figs.py DIR   (reads DIR/opt2_grid.npz, writes DIR/opt2_*.png, opt2_numbers.json)"""
import sys, json, numpy as np
D = sys.argv[1]
sys.argv = [sys.argv[0], D]
import slide9_opt2 as o
from scipy.interpolate import RectBivariateSpline
from scipy.optimize import brentq
import matplotlib.pyplot as plt
mc = o.mc; BLUE, ORANGE, GREY = o.BLUE, o.ORANGE, o.GREY
z = np.load(f"{D}/opt2_grid.npz"); As, Bs, T = z["As"][:5], z["Bs"], z["T"][:5]   # a <= 0.207: the blade tips (reach 0.25 + a) must stay inside the unit-square mesh
T_star = 150.0
spT = RectBivariateSpline(As, Bs, T, kx=3, ky=3)
Ar = np.array([[float(mc.area(mc.CutGeometry(mc.Mesh(40), o.rot2(a, b)))) for b in Bs] for a in As])
spA = RectBivariateSpline(As, Bs, Ar, kx=1, ky=1)
# constraint curve: for every a, the b with T_worst(a, b) = T*  (T grows with b)
ag = np.linspace(As[0], As[-1], 60)
bstar = np.array([brentq(lambda b: float(spT(a, b)[0, 0]) - T_star, Bs[0], Bs[-1]) if spT(a, Bs[-1])[0, 0] > T_star else np.nan for a in ag])
area_c = np.array([float(spA(a, b)[0, 0]) if np.isfinite(b) else np.nan for a, b in zip(ag, bstar)])
k = int(np.nanargmax(area_c)); a_opt, b_opt = float(ag[k]), float(bstar[k])
# verify at the optimum with the real solver
true_T = o.worst2(a_opt, b_opt); true_A = float(mc.area(mc.CutGeometry(mc.Mesh(40), o.rot2(a_opt, b_opt))))
print("optimum", a_opt, b_opt, "T", true_T, "area", true_A)
B1 = 0.0750   # one-parameter optimum (a = 0.17)
a1, A1 = 0.17, float(mc.area(mc.CutGeometry(mc.Mesh(40), o.rot2(0.17, B1))))
# ---- figure 1: map of the worst peak temperature, constraint curve, optimum
fig, axs = plt.subplots(1, 2, figsize=(14.6, 5.6), dpi=100, gridspec_kw=dict(width_ratios=[1.25, 1]))
ax = axs[0]
af = np.linspace(As[0], As[-1], 80); bf = np.linspace(Bs[0], Bs[-1], 80)
Z = spT(af, bf)
cs = ax.contourf(bf, af, Z, levels=np.arange(0, 260, 20), cmap="YlOrRd", alpha=0.85)
ax.contour(bf, af, Z, levels=[T_star], colors=ORANGE, linewidths=3)
ar_f = spA(af, bf); cc = ax.contour(bf, af, ar_f, levels=[0.15, 0.20, 0.25, 0.30, 0.35], colors="k", linewidths=1, linestyles=":")
ax.clabel(cc, fmt="A=%.2f", fontsize=11)
ax.plot([0.055], [0.17], "ks", ms=9); ax.annotate("start", (0.055, 0.17), (0.0345, 0.125), fontsize=14, bbox=dict(fc="white", ec="none", alpha=0.85), arrowprops=dict(arrowstyle="-", lw=0.8))
ax.plot([B1], [a1], "o", color=BLUE, ms=10); ax.annotate("1 parameter", (B1, a1), (0.078, 0.13), fontsize=14, color=BLUE, bbox=dict(fc="white", ec="none", alpha=0.85), arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8))
ax.plot([b_opt], [a_opt], "*", color="k", ms=18); ax.annotate("2 parameters", (b_opt, a_opt), (0.0745, 0.1955), fontsize=14, bbox=dict(fc="white", ec="none", alpha=0.85), arrowprops=dict(arrowstyle="-", lw=0.8))
ax.set_xlabel("blade half-width b", fontsize=15); ax.set_ylabel("blade semi-length a", fontsize=15); ax.tick_params(labelsize=13)
cb = fig.colorbar(cs, ax=ax, pad=0.02); cb.set_label("worst peak temperature over a turn", fontsize=13)
ax.text(0.0585, 0.1075, "limit curve T = 150", color=ORANGE, fontsize=14, ha="center", fontweight="bold", bbox=dict(fc="white", ec="none", alpha=0.85))
ax = axs[1]
ax.plot(ag, area_c, color=BLUE, lw=2.5); ax.plot([a_opt], [area_c[k]], "*", color="k", ms=18)
ax.plot([a1], [A1], "o", color=BLUE, ms=10)
ax.set_xlabel("blade semi-length a", fontsize=15); ax.set_ylabel("rotor area on the limit curve T = 150", fontsize=15)
ax.tick_params(labelsize=13); ax.grid(alpha=0.3)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{D}/opt2_map.png", facecolor="white"); plt.close(fig)
# ---- figure 2: three rotors at their worst angle
def run(a, b):
    ang = np.linspace(0, o.PERIOD, 25)[:-1]
    pk = [o.peak2(a, b, t) for t in ang]; t = ang[int(np.argmax(pk))]
    g = mc.CutGeometry(mc.Mesh(40), mc.rotate(o.rot2(a, b), t)); A, r = mc.poisson_system(g, o.f_jet, o.zero, ghost=True)
    return g, mc.solve(g, A, r), max(pk), float(mc.area(g))
res = {"start": (0.17, 0.055), "one": (0.17, B1), "two": (a_opt, b_opt)}
NUM = {}
for tag, (a, b) in res.items():
    g, u, pk, ar = run(a, b)
    fig, ax = plt.subplots(figsize=(4.0, 4.0), dpi=100); fig.subplots_adjust(0, 0, 1, 1)
    o.solution_ax(g, u, ax, T_star); o.jet_ax(ax); fig.savefig(f"{D}/opt2_{tag}.png", facecolor="white"); plt.close(fig)
    NUM[tag] = dict(a=a, b=b, peak=pk, area=ar)
NUM["grid_seconds_per_solve"] = 0.13
json.dump(NUM, open(f"{D}/opt2_numbers.json", "w"), indent=1); print(json.dumps(NUM, indent=1))
