"""Figures and numbers for the three worked examples (minicut, 2D, P1).

Run:  python slide8_examples.py OUTDIR
Writes PNGs and numbers.json.  Manufactured solution u = sin(2 pi x) sin(2 pi y),
Nitsche (gamma = 40) and ghost penalty (gamma_g = 0.1) as in minicut.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from matplotlib.collections import LineCollection
import minicut as mc

out = sys.argv[1] if len(sys.argv) > 1 else "."
BLUE, ORANGE, GREY = "#00509A", "#B34F00", "#6E6E6E"
ue = lambda x, y: np.sin(2 * np.pi * x) * np.sin(2 * np.pi * y)
fe = lambda x, y: 8 * np.pi**2 * ue(x, y)
one = lambda x, y: np.ones_like(x)
zero = lambda x, y: np.zeros_like(x)
N = {}


def smooth_union(a, b, k):
    def phi(x, y):
        pa, pb = a(x, y), b(x, y)
        h = np.clip(0.5 + 0.5 * (pb - pa) / k, 0, 1)
        return pb * (1 - h) + pa * h - k * h * (1 - h)
    return phi


def bubbles(t):
    d = 0.30 - 0.20 * t
    return smooth_union(mc.circle((0.5 - d, 0.47), 0.15), mc.circle((0.5 + d, 0.53), 0.13), 0.06)


def square_ax(size=5.2):
    fig, ax = plt.subplots(figsize=(size, size), dpi=100)
    ax.set_aspect("equal"); ax.axis("off"); fig.subplots_adjust(0, 0, 1, 1)
    return fig, ax


def cells_ax(geom, ax):
    mc.plot_cells(geom, ax=ax)
    ax.collections[-1].set_color(ORANGE); ax.collections[-1].set_linewidth(2.2)
    ax.axis("off")


def solution_ax(geom, u, ax, vmin=None, vmax=None, mesh=True, cmap="RdBu_r"):
    ns = len(geom.sub_verts)
    pts = geom.sub_verts.reshape(-1, 2)
    cells = np.repeat(geom.sub_cells, 3)
    vals = mc.evaluate(geom, u, cells, pts)
    tri = mtri.Triangulation(pts[:, 0], pts[:, 1], np.arange(3 * ns).reshape(-1, 3))
    ax.tripcolor(tri, vals, shading="gouraud", cmap=cmap, vmin=vmin, vmax=vmax)
    if mesh:
        m = geom.mesh
        ax.triplot(mtri.Triangulation(m.nodes[:, 0], m.nodes[:, 1], m.cells), color=GREY, lw=0.3, alpha=0.4)
    ax.add_collection(LineCollection(geom.segments, colors="k", linewidths=1.8))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")


def solve_case(phi, n, ghost=True, kappa=False, f=fe, g=ue):
    m = mc.Mesh(n); geom = mc.CutGeometry(m, phi)
    A, b = mc.poisson_system(geom, f, g, ghost=ghost)
    u = mc.solve(geom, A, b)
    k = mc.condition_number(geom, A) if kappa else (None, None)
    return geom, u, dict(n=n, cut=int((geom.cell_type == mc.CUT).sum()),
                         active=len(geom.active_cells), l2=float(mc.l2_error(geom, u, ue)),
                         kappa=None if k[0] is None else float(k[0]), neg=k[1])


def example_block(name, phi):
    rows = []
    for n in (20, 40, 80):
        geom, u, r = solve_case(phi, n, True, n == 40)
        rows.append(r)
        if n == 40:
            fig, ax = square_ax(); cells_ax(geom, ax); fig.savefig(f"{out}/{name}_cells.png", facecolor="white"); plt.close(fig)
            fig, ax = square_ax(); solution_ax(geom, u, ax, -1, 1); fig.savefig(f"{out}/{name}_solution.png", facecolor="white"); plt.close(fig)
    _, _, r0 = solve_case(phi, 40, False, True)
    for a, b in zip(rows[:-1], rows[1:]):
        b["rate"] = float(np.log2(a["l2"] / b["l2"]))
    N[name] = dict(rows=rows, noghost=r0)


# ---- example 1: image data -------------------------------------------------
img = mc.synthetic_scan() > 0.5
example_block("image", mc.levelset_from_image(img))

# ---- example 3: complex shape ----------------------------------------------
a1 = mc.ellipse((0.5, 0.5), 0.42, 0.15); a2 = mc.ellipse((0.5, 0.5), 0.15, 0.42)
hole = mc.circle((0.5, 0.5), 0.09); notch = mc.circle((0.9, 0.5), 0.07)
s1 = mc.union(a1, a2); s2 = mc.difference(s1, hole); s3 = mc.difference(s2, notch)
example_block("csg", s3)
steps = [a1, a2, s1, s2, s3]
fig, axs = plt.subplots(1, 5, figsize=(16.64, 3.4), dpi=100)
for ax, ph in zip(axs, steps):
    geom = mc.CutGeometry(mc.Mesh(40), ph)
    ax.set_aspect("equal"); cells_ax(geom, ax)
fig.subplots_adjust(0.005, 0.01, 0.995, 0.99, wspace=0.03)
fig.savefig(f"{out}/csg_steps.png", facecolor="white"); plt.close(fig)

# ---- example 2: moving interface -------------------------------------------
frames = (0.0, 0.5, 0.8, 1.0)
fig, axs = plt.subplots(1, 4, figsize=(16.64, 2.34), dpi=100)
sol = []
for ax, t in zip(axs, frames):
    geom = mc.CutGeometry(mc.Mesh(40), bubbles(t))
    ax.set_aspect("equal"); cells_ax(geom, ax); ax.set_ylim(0.22, 0.78)
fig.subplots_adjust(0.005, 0.01, 0.995, 0.99, wspace=0.03)
fig.savefig(f"{out}/moving_frames.png", facecolor="white"); plt.close(fig)
for i, t in enumerate(frames):
    geom, u, _ = solve_case(bubbles(t), 40, True, False, f=one, g=zero)
    fig, ax = plt.subplots(figsize=(4.0, 2.24), dpi=100); fig.subplots_adjust(0, 0, 1, 1); ax.set_aspect("equal"); solution_ax(geom, u, ax, 0.0, 0.007, mesh=False, cmap="YlGnBu"); ax.set_ylim(0.22, 0.78)
    fig.savefig(f"{out}/moving_sol{i}.png", facecolor="white"); plt.close(fig)
m = mc.Mesh(40)
ts = np.linspace(0, 1, 61); K = {"ghost": [], "none": []}; areas = []
for t in ts:
    geom = mc.CutGeometry(m, bubbles(t))
    for key, gh in (("ghost", True), ("none", False)):
        A, _ = mc.poisson_system(geom, one, zero, ghost=gh)
        K[key].append(float(mc.condition_number(geom, A)[0]))
    areas.append(float(mc.area(geom)))
N["moving"] = dict(t=ts.tolist(), kappa=K, area=areas)
fig, ax = plt.subplots(figsize=(9.6, 6.0), dpi=100)
ax.semilogy(ts, np.minimum(K["none"], 1e18), "-o", ms=3.5, lw=1.2, color=ORANGE, label="without ghost penalty")
ax.semilogy(ts, K["ghost"], "-o", ms=3.5, lw=2, color=BLUE, label="with ghost penalty")
ax.set_xlabel("time t", fontsize=18); ax.set_ylabel("condition number of A", fontsize=18)
ax.tick_params(labelsize=16); ax.set_ylim(1e1, 1e19)
ax.grid(alpha=0.3); ax.legend(fontsize=17, loc="center right")
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{out}/moving_kappa.png", facecolor="white"); plt.close(fig)
json.dump(N, open(f"{out}/numbers.json", "w"), indent=1)
print("ok")
