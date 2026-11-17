"""Flower figures of Example 1 and its convergence study, made with minicut only.

Run from the repository root:   PYTHONPATH=. python tools/lecture_figures.py OUTDIR
Writes first_active, first_warp, classify_cut, ps3_zoom, ps4_normals, ps_stab, convergence (png)
and lecture_figures.json (the numbers quoted on the slides).
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection

import minicut as mc

out = Path(sys.argv[1] if len(sys.argv) > 1 else "fig_out")
out.mkdir(parents=True, exist_ok=True)

GREEN, ORANGE_L, ORANGE, RED, BLUE, GREY = "#74d3ae", "#f9b252", "#f9b252", "#c0392b", "#00509A", "#9aa5b1"
OR, GR, BL = "#C2570C", "#2E8B57", "#00509A"
INK = "#151a2a"


def level_set(x, y):  # flower, 6 petals
    r = 0.48 * (1 + 0.18 * np.cos(6 * np.arctan2(y, x)))
    return np.sqrt(x**2 + y**2) - r


mesh = mc.Mesh(18, box=(-1, -1, 1, 1))
geom = mc.CutGeometry(mesh, level_set(mesh.nodes[:, 0], mesh.nodes[:, 1]), order=2)
t = geom.cell_type
V = mesh.nodes[mesh.cells]
f1 = lambda x, y: np.ones_like(x)
g0 = lambda x, y: np.zeros_like(x)
A, b = mc.poisson_system(geom, f1, g0)
u = mc.solve(geom, A, b)
numbers = dict(summary=geom.summary(), max_u=float(np.nanmax(u)), area=float(mc.area(geom)))


def canvas(w=4.0, h=4.2, lim=1.0):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_aspect("equal"); ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.axis("off")
    fig.subplots_adjust(0.01, 0.01, 0.99, 0.99)
    return fig, ax


def mesh_lines(ax, lw=0.5, col="#9aa5b1"):
    ax.add_collection(PolyCollection(V, facecolors="none", edgecolors=col, linewidths=lw))


def curve(ax, lw=2.4):
    ax.add_collection(LineCollection(geom.segments, colors=INK, linewidths=lw))


def save(fig, name):
    fig.savefig(out / name, dpi=250); plt.close(fig)


# --- active domain: inside green, cut orange
fig, ax = canvas(4.0, 4.2, 1.0)
cols = [GREEN if k == mc.INSIDE else (ORANGE if k == mc.CUT else "white") for k in t]
ax.add_collection(PolyCollection(V, facecolors=cols, edgecolors="none"))
mesh_lines(ax); curve(ax, 2.6)
save(fig, "first_active.png")

# --- cut cells only
fig, ax = canvas(4.0, 4.2, 1.0)
ax.add_collection(PolyCollection(V[t == mc.CUT], facecolors=ORANGE, edgecolors="none"))
mesh_lines(ax); curve(ax, 2.6)
save(fig, "classify_cut.png")

# --- 3D warp on the physical cut domain
ns = len(geom.sub_verts)
pts = geom.sub_verts.reshape(-1, 2)
cells = np.repeat(geom.sub_cells, 3)
vals = mc.evaluate(geom, u, cells, pts)
tri_s = mtri.Triangulation(pts[:, 0], pts[:, 1], np.arange(3 * ns).reshape(-1, 3))
fig = plt.figure(figsize=(6.6, 5.9))
ax = fig.add_subplot(111, projection="3d")
surf = ax.plot_trisurf(tri_s, vals, cmap="viridis", edgecolor="#40485a", linewidth=0.25, antialiased=True)
ax.set_zlim(0, vals.max() * 1.15)
ax.set_xlim(-0.62, 0.62); ax.set_ylim(-0.62, 0.62)
ax.set_box_aspect((1, 1, 0.45)); ax.view_init(elev=30, azim=-62)
ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
for a in (ax.xaxis, ax.yaxis, ax.zaxis):
    a.pane.set_facecolor((0.95, 0.95, 0.96, 1)); a.pane.set_edgecolor("#dddddd")
cb = fig.colorbar(surf, ax=ax, shrink=0.55, pad=0.02); cb.set_label("u", fontsize=13)
fig.subplots_adjust(0, 0, 0.95, 1)
fig.savefig(out / "first_warp.png", dpi=250, bbox_inches="tight", pad_inches=0.05); plt.close(fig)

# --- zoom on one petal: sub-triangles and volume points; interface points with normals
x0, x1, y0, y1 = 0.22, 0.74, -0.2, 0.2


def zoom(w=6.5):
    fig, ax = plt.subplots(figsize=(w, w * (y1 - y0) / (x1 - x0)))
    ax.set_aspect("equal"); ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.axis("off")
    fig.subplots_adjust(0.01, 0.01, 0.99, 0.99)
    ax.add_collection(PolyCollection(V[t == mc.CUT], facecolors="#fde9c9", edgecolors="none"))
    ax.add_collection(PolyCollection(V, facecolors="none", edgecolors="#9aa5b1", linewidths=1.0))
    return fig, ax


fig, ax = zoom()
ax.add_collection(PolyCollection(geom.sub_verts, facecolors="none", edgecolors=BL, linewidths=0.9, linestyles="--"))
ax.plot(geom.volume.points[:, 0], geom.volume.points[:, 1], "o", color=BL, ms=6)
curve(ax, 2.4)
save(fig, "ps3_zoom.png")

fig, ax = zoom()
curve(ax, 1.6)
q = geom.interface
ax.plot(q.points[:, 0], q.points[:, 1], "o", color=RED, ms=6, zorder=3)
ax.quiver(q.points[:, 0], q.points[:, 1], q.normals[:, 0], q.normals[:, 1], color=RED,
          angles="xy", scale_units="xy", scale=14, width=0.004, zorder=3)
save(fig, "ps4_normals.png")

# --- stabilisation: ghost facets and aggregation on the flower
agg = mc.aggregate(geom, 0.25)
numbers.update(n_ill=int(len(agg.ill_cells)), n_removed=int(len(agg.removed_dofs)),
               n_good=int(len(agg.good_dofs)), n_active=int(len(geom.active_dofs)),
               n_ghost=int(len(geom.ghost_facets)), n_cut=int(np.sum(t == mc.CUT)))
kap = {}
for name, ghost, a in [("none", False, None), ("ghost", True, None), ("aggregation", False, agg)]:
    Ai, bi = mc.poisson_system(geom, f1, g0, ghost=ghost)
    kap[name] = mc.condition_number(geom, Ai, a)
numbers["kappa"] = {k: [float(v[0]), int(v[1])] for k, v in kap.items()}

fig, ax = plt.subplots(1, 2, figsize=(8.4, 4.2))
for a in ax:
    a.set_aspect("equal"); a.set_xlim(-0.75, 0.75); a.set_ylim(-0.75, 0.75); a.axis("off")
ax[0].add_collection(PolyCollection(V[t == mc.CUT], facecolors="#fde9c9", edgecolors="none"))
ax[0].add_collection(PolyCollection(V, facecolors="none", edgecolors="#c5ccd4", linewidths=0.5))
ax[0].add_collection(LineCollection(mesh.nodes[mesh.facet_nodes[geom.ghost_facets]], colors=RED, linewidths=2.2))
ax[0].add_collection(LineCollection(geom.segments, colors=INK, linewidths=1.6))
ax[0].set_title("ghost penalty: jump on red facets", fontsize=12, color=BL, loc="left")
ill = set(agg.ill_cells.tolist()); roots = set(agg.root[list(ill)].tolist())
cols = []
for c in range(mesh.n_cells):
    if t[c] == mc.OUTSIDE: cols.append("white")
    elif c in ill: cols.append("#f2a65a")
    elif c in roots: cols.append("#5b9bd5")
    else: cols.append("#e3edf7")
ax[1].add_collection(PolyCollection(V, facecolors=cols, edgecolors="#c5ccd4", linewidths=0.5))
act = t != mc.OUTSIDE
fc = mesh.facet_cells
agg_id = np.where(act & np.isin(agg.root, list(roots)), agg.root, -2)
ra, rb = agg_id[fc[:, 0]], agg_id[fc[:, 1]]
sel = (ra != rb) & ((ra >= 0) | (rb >= 0))
ax[1].add_collection(LineCollection(mesh.nodes[mesh.facet_nodes[sel]], colors="#333333", linewidths=1.8))
ax[1].add_collection(LineCollection(geom.segments, colors="k", linewidths=1.4))
ax[1].set_title("aggregation: orange cells join the blue root", fontsize=12, color=GR, loc="left")
fig.subplots_adjust(0.01, 0.01, 0.99, 0.92, wspace=0.04)
save(fig, "ps_stab.png")

# --- convergence on the flower, manufactured solution, P1
u_ex = lambda x, y: np.sin(np.pi * x) * np.sin(np.pi * y)
f_ex = lambda x, y: 2 * np.pi**2 * u_ex(x, y)
grad_ex = lambda x, y: (np.pi * np.cos(np.pi * x) * np.sin(np.pi * y), np.pi * np.sin(np.pi * x) * np.cos(np.pi * y))
ns_ = [10, 20, 40, 80, 160]
conv = {k: dict(L2=[], H1=[]) for k in ["none", "ghost", "aggregation"]}
for n in ns_:
    m = mc.Mesh(n, box=(-1, -1, 1, 1))
    gm = mc.CutGeometry(m, level_set(m.nodes[:, 0], m.nodes[:, 1]), order=2)
    ag = mc.aggregate(gm, 0.25)
    for name, ghost, a in [("none", False, None), ("ghost", True, None), ("aggregation", False, ag)]:
        Ai, bi = mc.poisson_system(gm, f_ex, u_ex, ghost=ghost)
        uh = mc.solve(gm, Ai, bi) if a is None else mc.solve_aggregated(gm, Ai, bi, a)
        conv[name]["L2"].append(mc.l2_error(gm, uh, u_ex))
        conv[name]["H1"].append(mc.h1_error(gm, uh, grad_ex))
h = 2.0 / np.array(ns_)
rates = {k: {m: float(np.polyfit(np.log(h), np.log(v[m]), 1)[0]) for m in v} for k, v in conv.items()}
numbers["convergence"] = dict(n=ns_, h=h.tolist(), errors=conv, rates=rates)

fig, ax = plt.subplots(1, 2, figsize=(15, 6.06))
sty = {"none": ("#C2570C", "o", "no stabilisation"), "ghost": (BL, "s", "ghost penalty"),
       "aggregation": (GR, "^", "aggregation")}
for j, (mkey, ttl, ref) in enumerate([("L2", "L² error", 2), ("H1", "H¹ seminorm error", 1)]):
    for k, (c, mk, lab) in sty.items():
        ax[j].loglog(h, conv[k][mkey], "-" + mk, color=c, lw=2, ms=9, label=f"{lab}  (slope {rates[k][mkey]:.2f})")
    e0 = conv["ghost"][mkey][0]
    ax[j].loglog(h, e0 * (h / h[0]) ** ref, "--", color="#555", lw=1.2, label=f"slope {ref}")
    ax[j].set_xlabel("cell size h", fontsize=17); ax[j].set_ylabel(ttl, fontsize=17)
    ax[j].tick_params(labelsize=14); ax[j].grid(True, which="both", color="#e6e6e6")
    ax[j].legend(fontsize=14, loc="lower right")
    for s in ("top", "right"): ax[j].spines[s].set_visible(False)
fig.tight_layout()
save(fig, "convergence.png")

json.dump(numbers, open(out / "lecture_figures.json", "w"), indent=1)
print(json.dumps(numbers, indent=1))
