"""Nitsche penalty gamma versus definiteness: same 81 disc positions as cond_sweep.py.

Run from the repository root:   PYTHONPATH=. python tools/gamma_sweep.py OUTDIR  -> gamma_sweep.json, gamma_sweep.png
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import minicut as mc

out = Path(sys.argv[1] if len(sys.argv) > 1 else "gamma_out"); out.mkdir(parents=True, exist_ok=True)
C0 = (0.037, -0.021)
mesh = mc.Mesh(20, box=(-1, -1, 1, 1))
u_ex = lambda x, y: np.sin(np.pi * x) * np.sin(np.pi * y)
f = lambda x, y: 2 * np.pi**2 * u_ex(x, y)
GAMMA_G = 0.1
gammas = [5, 10, 20, 40, 100, 300, 1000, 3000, 10000]
radii = np.linspace(0.50, 0.60, 81)
geoms = [mc.CutGeometry(mesh, mc.circle(C0, r)) for r in radii]
import os
res = {}
if (out / "gamma_sweep.json").exists():
    res = {int(k): v for k, v in json.load(open(out / "gamma_sweep.json")).items()}
for g in ([] if res else gammas):
    row = {}
    for name, ghost in (("none", False), ("ghost", True)):
        neg, kap, err = [], [], []
        for geom in geoms:
            A, b = mc.poisson_system(geom, f, u_ex, float(g), GAMMA_G, ghost=ghost)
            k, n = mc.condition_number(geom, A)
            kap.append(k); neg.append(n)
            err.append(mc.l2_error(geom, mc.solve(geom, A, b), u_ex))
        row[name] = dict(indefinite=int(np.sum(np.array(neg) > 0)), kmin=float(min(kap)), kmed=float(np.median(kap)),
                         kmax=float(max(kap)), errmed=float(np.median(err)), errmax=float(max(err)))
    res[g] = row
    print(g, row["none"]["indefinite"], f'{row["none"]["kmed"]:.2e}', row["ghost"]["indefinite"], f'{row["ghost"]["kmed"]:.2e}', f'{row["none"]["errmed"]:.2e}', flush=True)
json.dump({str(k): v for k, v in res.items()}, open(out / "gamma_sweep.json", "w"), indent=1)

# ---------------------------------------------------------------- figure
ORANGE, BLUE = "#C2570C", "#00509A"
plt.rcParams.update({"font.size": 17, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#555", "axes.grid": True, "grid.color": "#e6e6e6"})
G = np.array(gammas, float)
fig, ax = plt.subplots(1, 2, figsize=(11.0, 4.4))
for name, col, lab in (("none", ORANGE, "no stabilisation"), ("ghost", BLUE, "with stabilisation")):
    ax[0].plot(G, [res[g][name]["indefinite"] for g in gammas], "o-", color=col, lw=2.4, ms=7, label=lab)
    med = np.array([res[g][name]["kmed"] for g in gammas])
    ax[1].fill_between(G, [res[g][name]["kmin"] for g in gammas], [res[g][name]["kmax"] for g in gammas], color=col, alpha=0.15, lw=0)
    ax[1].plot(G, med, "o-", color=col, lw=2.4, ms=7, label=lab)
ax[0].set_xscale("log"); ax[0].set_xlabel(r"Nitsche penalty $\gamma$"); ax[0].set_ylabel("indefinite matrices (of 81)")
ax[0].set_title("Definiteness", fontsize=18, color="#333"); ax[0].axvline(40, color="#888", ls="--", lw=1.4)
ax[0].legend(frameon=False, loc="upper right", fontsize=15)
ax[1].set_xscale("log"); ax[1].set_yscale("log"); ax[1].set_xlabel(r"Nitsche penalty $\gamma$"); ax[1].set_ylabel(r"condition number $\kappa$")
ax[1].set_title("Condition number (median, range)", fontsize=18, color="#333"); ax[1].axvline(40, color="#888", ls="--", lw=1.4)
fig.tight_layout()
fig.savefig(out / "gamma_sweep.png", dpi=200, transparent=False, facecolor="white")
