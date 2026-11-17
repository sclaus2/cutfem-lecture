"""Conditioning experiment of the lecture, made with minicut only.

A disc of radius r in [0.50, 0.60] slides one cell width on a fixed 20 x 20 mesh of
[-1, 1]^2.  For every radius: Nitsche without stabilisation, with ghost penalty, and with
cell aggregation; condition number, number of negative eigenvalues, L2 error, GMRES
iterations (plain and diagonally scaled), smallest cut fraction eta.

Run from the repository root:   PYTHONPATH=. python tools/cond_sweep.py OUTDIR
Writes OUTDIR/cond_sweep.json and the figures cond_setup, cond_sweep, small_cuts, cond_modes,
cond_cost, aggregation (png).
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection

import minicut as mc

out = Path(sys.argv[1] if len(sys.argv) > 1 else "cond_out")
out.mkdir(parents=True, exist_ok=True)

ORANGE, BLUE, GREEN, TITLE, GREY = "#C2570C", "#00509A", "#2E8B57", "#00509A", "#333333"
CELL_IN, CELL_CUT = "#d3e3f3", "#e8a96a"
plt.rcParams.update({"font.size": 15, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#555", "axes.grid": True, "grid.color": "#e6e6e6"})

C0 = (0.037, -0.021)
mesh = mc.Mesh(20, box=(-1, -1, 1, 1))
u_ex = lambda x, y: np.sin(np.pi * x) * np.sin(np.pi * y)
f = lambda x, y: 2 * np.pi**2 * u_ex(x, y)
GAMMA, GAMMA_G, THRESH = 40.0, 0.1, 0.25


def run(r):
    geom = mc.CutGeometry(mesh, mc.circle(C0, r))
    res = dict(r=r, eta=float(geom.volume_fraction[geom.cell_type == mc.CUT].min()))
    A0, b0 = mc.poisson_system(geom, f, u_ex, GAMMA, GAMMA_G, ghost=False)
    A1, b1 = mc.poisson_system(geom, f, u_ex, GAMMA, GAMMA_G, ghost=True)
    agg = mc.aggregate(geom, THRESH)
    res["n_removed"], res["n_ill"] = len(agg.removed_dofs), len(agg.ill_cells)
    for k, (A, b, a) in enumerate([(A0, b0, None), (A1, b1, None), (A0, b0, agg)]):
        res[f"k{k}"], res[f"n{k}"] = mc.condition_number(geom, A, a)
        u = mc.solve(geom, A, b) if a is None else mc.solve_aggregated(geom, A, b, a)
        res[f"e{k}"] = mc.l2_error(geom, u, u_ex)
        res[f"it{k}"] = mc.gmres_iterations(geom, A, b, agg=a)
        res[f"its{k}"] = mc.gmres_iterations(geom, A, b, scale=True, agg=a)
        d = geom.active_dofs if a is None else None
        M = A[d][:, d] if a is None else (a.E.T @ A @ a.E)
        s = 1 / np.sqrt(np.abs(M.diagonal()))
        ev = np.linalg.eigvalsh((np.diag(s) @ M.toarray() @ np.diag(s)))
        res[f"ks{k}"] = float(np.abs(ev).max() / np.abs(ev).min())
    return res


radii = np.linspace(0.50, 0.60, 81)
rows = [run(r) for r in radii]
R = {k: np.array([row[k] for row in rows]) for k in rows[0]}

# ---------------------------------------------------------------- numbers
def rng(a):
    return float(np.min(a)), float(np.max(a))

kappa_err_corr = [float(np.corrcoef(np.log(R[f"k{k}"]), np.log(R[f"e{k}"]))[0, 1]) for k in range(3)]
worst = int(np.argmax(R["k0"]))
stats = dict(
    n_radii=len(radii),
    kappa={k: rng(R[f"k{i}"]) for i, k in enumerate(["none", "ghost", "aggregation"])},
    indefinite={k: int(np.sum(R[f"n{i}"] > 0)) for i, k in enumerate(["none", "ghost", "aggregation"])},
    err={k: rng(R[f"e{i}"]) for i, k in enumerate(["none", "ghost", "aggregation"])},
    gmres={k: rng(R[f"it{i}"]) for i, k in enumerate(["none", "ghost", "aggregation"])},
    gmres_scaled={k: rng(R[f"its{i}"]) for i, k in enumerate(["none", "ghost", "aggregation"])},
    kappa_scaled={k: rng(R[f"ks{i}"]) for i, k in enumerate(["none", "ghost", "aggregation"])},
    eta=rng(R["eta"]),
    removed=rng(R["n_removed"]), ill=rng(R["n_ill"]),
    corr_logk_loge=kappa_err_corr,
    worst=dict(r=float(radii[worst]), k0=float(R["k0"][worst]), eta=float(R["eta"][worst]),
               n0=int(R["n0"][worst])),
)

# ---------------------------------------------------------------- smallest modes at the worst radius
geom_w = mc.CutGeometry(mesh, mc.circle(C0, radii[worst]))
A0, _ = mc.poisson_system(geom_w, f, u_ex, GAMMA, GAMMA_G, ghost=False)
A1, _ = mc.poisson_system(geom_w, f, u_ex, GAMMA, GAMMA_G, ghost=True)
ev0, mode0 = mc.smallest_mode(geom_w, A0)
ev1, mode1 = mc.smallest_mode(geom_w, A1)
stats["worst"].update(ev0=float(ev0), ev1=float(ev1))
# if it can be located: node of the largest amplitude, and the volume fraction around it
k0 = int(np.nanargmax(np.abs(mode0)))
stats["worst"]["mode_node"] = [float(v) for v in mesh.nodes[k0]]
touch = np.where((mesh.cells == k0).any(1) & (geom_w.cell_type == mc.CUT))[0]
stats["worst"]["mode_fractions"] = [float(geom_w.volume_fraction[c]) for c in touch]
stats["worst"]["mode_inside"] = bool(geom_w.phi[k0] < 0)

json.dump(dict(stats=stats, rows=[{k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in row.items()}
                                  for row in rows]), open(out / "cond_sweep.json", "w"), indent=1)
print(json.dumps(stats, indent=1))


# ---------------------------------------------------------------- figures
def finish(ax):
    ax.tick_params(labelsize=14)


def title(ax, t, c=TITLE):
    ax.set_title(t, loc="left", fontsize=17, color=c)


# --- setup: the mesh and the three discs
fig, ax = plt.subplots(figsize=(6, 6.17), dpi=200)
geom = mc.CutGeometry(mesh, mc.circle(C0, 0.545))
V = mesh.nodes[mesh.cells]
cols = [CELL_IN if t == mc.INSIDE else (CELL_CUT if t == mc.CUT else "white") for t in geom.cell_type]
ax.add_collection(PolyCollection(V, facecolors=cols, edgecolors="#aab4be", linewidths=0.35))
th = np.linspace(0, 2 * np.pi, 400)
for r, ls, lw in [(0.50, "--", 1.1), (0.60, "--", 1.1), (0.545, "-", 2.0)]:
    ax.plot(C0[0] + r * np.cos(th), C0[1] + r * np.sin(th), color=GREY, ls=ls, lw=lw)
ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_aspect("equal"); ax.axis("off")
fig.subplots_adjust(0, 0, 1, 1)
fig.savefig(out / "cond_setup.png"); plt.close(fig)

# --- sweep: kappa and error, no stabilisation vs ghost penalty
def sweep_fig(names, fname, size=(11, 4.69)):
    fig, ax = plt.subplots(1, 2, figsize=size, dpi=200)
    style = {0: (ORANGE, "no stabilisation"), 1: (BLUE, "ghost penalty"), 2: (GREEN, "aggregation")}
    for i in names:
        c, lab = style[i]
        k, n, e = R[f"k{i}"], R[f"n{i}"], R[f"e{i}"]
        ax[0].plot(radii, k, "-", color=c, lw=1.4, alpha=0.9, zorder=2)
        pos, neg = n == 0, n > 0
        ax[0].plot(radii[pos], k[pos], "o", color=c, ms=4.5, zorder=3,
                   label=lab + (", matrix positive definite" if i == 0 else ""))
        if neg.any():
            ax[0].plot(radii[neg], k[neg], "X", color=c, ms=8, zorder=3,
                       label=lab + ", matrix indefinite")
        ax[1].plot(radii, e, "o-", color=c, ms=4.5, lw=1.4, label=lab)
    ax[0].set_yscale("log")
    ax[0].set_ylabel("condition number κ", fontsize=16); ax[1].set_ylabel("L² error", fontsize=16)
    for a in ax:
        a.set_xlabel("disc radius r  (cell size h = 0.1)", fontsize=16); finish(a)
    ax[1].set_ylim(0.005, 0.0115)
    ax[0].legend(fontsize=12.5, loc="upper right", framealpha=0.95)
    title(ax[0], "Conditioning", GREY); title(ax[1], "Accuracy", GREY)
    ax[0].set_ylim(5e1, 3e14)
    ax[0].set_yticks([1e2, 1e4, 1e6, 1e8, 1e10])
    fig.tight_layout()
    fig.savefig(out / fname); plt.close(fig)


sweep_fig([0, 1], "cond_sweep.png")
sweep_fig([0, 1, 2], "cond_sweep3.png")

# --- small cuts: kappa against eta
fig, ax = plt.subplots(figsize=(6.6, 5.28), dpi=200)
pos, neg = R["n0"] == 0, R["n0"] > 0
ax.loglog(R["eta"][pos], R["k0"][pos], "o", color=ORANGE, ms=6, label="positive definite")
ax.loglog(R["eta"][neg], R["k0"][neg], "X", color=ORANGE, ms=9, label="indefinite")
e = np.array([R["eta"].min(), R["eta"].max()])
c = np.median(R["k0"] * R["eta"])
ax.loglog(e, c / e, "--", color=GREY, lw=1.2, label="slope −1")
ax.set_xlabel("smallest cut fraction η", fontsize=16); ax.set_ylabel("condition number κ", fontsize=16)
ax.legend(fontsize=13, loc="upper right"); finish(ax)
fig.tight_layout(); fig.savefig(out / "small_cuts.png"); plt.close(fig)

# --- modes at the worst radius
def mode_panel(ax, mode, ev, cmap, colour, name):
    d = geom_w.active_dofs
    a = np.abs(mode[d]); a = a / a.max()
    xy = mesh.nodes[d]
    sc = ax.scatter(xy[:, 0], xy[:, 1], c=a, cmap=cmap, vmin=0, vmax=1, s=70, edgecolor="#8a96a3", linewidth=0.5)
    k = d[np.argmax(a)]
    ax.scatter(*mesh.nodes[k], s=420, facecolor="none", edgecolor=GREY, linewidth=2.2)
    ax.plot(C0[0] + radii[worst] * np.cos(th), C0[1] + radii[worst] * np.sin(th), color=GREY, lw=2.2)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(name, loc="left", fontsize=18, color=colour, fontweight="bold")
    ax.text(0.5, -0.02, f"smallest eigenvalue: {ev:+.1e}", transform=ax.transAxes, ha="center", va="top",
            fontsize=15, color=colour)
    cb = plt.colorbar(sc, ax=ax, fraction=0.04, pad=0.0); cb.set_label("mode amplitude", fontsize=14)
    cb.ax.tick_params(labelsize=12)


th = np.linspace(0, 2 * np.pi, 400)
fig, ax = plt.subplots(1, 2, figsize=(12.4, 5.62), dpi=200)
mode_panel(ax[0], mode0, ev0, "Oranges", ORANGE, "No stabilisation")
mode_panel(ax[1], mode1, ev1, "Blues", BLUE, "Ghost penalty")
fig.tight_layout(); fig.savefig(out / "cond_modes.png"); plt.close(fig)

# --- solver cost
fig, ax = plt.subplots(1, 2, figsize=(13, 5.55), dpi=200)
for i, (c, lab) in enumerate([(ORANGE, "no stabilisation"), (BLUE, "ghost penalty"), (GREEN, "aggregation")]):
    ax[0].plot(radii, R[f"it{i}"], "-", color=c, lw=1.6, label=lab)
    ax[0].plot(radii, R[f"its{i}"], "--", color=c, lw=1.6)
    ax[1].plot(radii, R[f"ks{i}"], "-", color=c, lw=1.6, label=lab)
ax[1].set_yscale("log")
ax[0].set_ylabel("GMRES iterations (tol 1e-8)", fontsize=16); ax[1].set_ylabel("κ after diagonal scaling", fontsize=16)
for a in ax:
    a.set_xlabel("disc radius r  (cell size h = 0.1)", fontsize=16); finish(a)
ax[0].legend(fontsize=13, loc="upper left")
ax[0].text(0.985, 0.04, "solid: plain      dashed: diagonal scaling", transform=ax[0].transAxes,
           ha="right", fontsize=12.5, color=GREY)
title(ax[0], "Iterations", GREY); title(ax[1], "Condition number after scaling", GREY)
ax[0].set_ylim(bottom=0)
fig.tight_layout(); fig.savefig(out / "cond_cost.png"); plt.close(fig)

# --- aggregation figure: coarse mesh so that the cells are visible
mesh_c = mc.Mesh(12, box=(-1, -1, 1, 1))
geom_c = mc.CutGeometry(mesh_c, mc.circle(C0, 0.6))
agg = mc.aggregate(geom_c, THRESH)
print("aggregation figure:", agg.summary(), "; cut cells", int(np.sum(geom_c.cell_type == mc.CUT)))
fig, ax = plt.subplots(figsize=(6, 6), dpi=200)
V = mesh_c.nodes[mesh_c.cells]
ill = set(agg.ill_cells.tolist())
roots = set(agg.root[list(ill)].tolist())
cols = []
for c in range(mesh_c.n_cells):
    t = geom_c.cell_type[c]
    if t == mc.OUTSIDE:
        cols.append("white")
    elif c in ill:
        cols.append("#f2a65a")
    elif c in roots:
        cols.append("#5b9bd5")
    else:
        cols.append("#e3edf7")
ax.add_collection(PolyCollection(V, facecolors=cols, edgecolors="#aab4be", linewidths=0.5))
# aggregates: thick edges around every group of cells that share a root
act = geom_c.cell_type != mc.OUTSIDE
fc = mesh_c.facet_cells
agg_id = np.where(act & np.isin(agg.root, list(roots)), agg.root, -2)  # -2: not in an aggregate
ra, rb = agg_id[fc[:, 0]], agg_id[fc[:, 1]]
sel = (ra != rb) & ((ra >= 0) | (rb >= 0))
segs = mesh_c.nodes[mesh_c.facet_nodes[sel]]
ax.add_collection(LineCollection(segs, colors=GREY, linewidths=2.2))
ax.add_collection(LineCollection(geom_c.segments, colors="k", linewidths=1.6))
ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_aspect("equal"); ax.axis("off")
fig.subplots_adjust(0, 0, 1, 1); fig.savefig(out / "aggregation.png"); plt.close(fig)
json.dump(dict(ill=int(len(agg.ill_cells)), cut=int(np.sum(geom_c.cell_type == mc.CUT)),
               removed=int(len(agg.removed_dofs)), left=int(len(agg.good_dofs))),
          open(out / "aggregation.json", "w"))
print("done")
