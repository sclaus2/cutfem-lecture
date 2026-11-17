"""Figures and numbers of the image example (Example 2), made with minicut only.

The specimen is a disc of solid matrix with pores; the problem is solved in the matrix, the
pores are empty.  Run from the repository root:   PYTHONPATH=. python tools/image_example.py OUTDIR
Writes scan.png (greyscale image), tile.png (-Δu = 1, u = 0 on Γ, for the roadmap slide),
cells.png, solution.png (manufactured solution) and image_numbers.json.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.collections import LineCollection

import minicut as mc

out = Path(sys.argv[1] if len(sys.argv) > 1 else "img_out")
out.mkdir(parents=True, exist_ok=True)
GREY, ORANGE = "#6E6E6E", "#B34F00"
ue = lambda x, y: np.sin(2 * np.pi * x) * np.sin(2 * np.pi * y)
fe = lambda x, y: 8 * np.pi**2 * ue(x, y)
one = lambda x, y: np.ones_like(x)
zero = lambda x, y: np.zeros_like(x)

scan = mc.synthetic_scan()
B = scan > 0.5
phi = mc.levelset_from_image(B)


def square(size=5.2):
    fig, ax = plt.subplots(figsize=(size, size), dpi=200)
    ax.set_aspect("equal"); ax.axis("off"); fig.subplots_adjust(0, 0, 1, 1)
    return fig, ax


def field(geom, u, ax, vmin=None, vmax=None, cmap="RdBu_r", mesh=True):
    ns = len(geom.sub_verts)
    pts = geom.sub_verts.reshape(-1, 2)
    cells = np.repeat(geom.sub_cells, 3)
    tri = mtri.Triangulation(pts[:, 0], pts[:, 1], np.arange(3 * ns).reshape(-1, 3))
    ax.tripcolor(tri, mc.evaluate(geom, u, cells, pts), shading="gouraud", cmap=cmap, vmin=vmin, vmax=vmax)
    if mesh:
        m = geom.mesh
        ax.triplot(mtri.Triangulation(m.nodes[:, 0], m.nodes[:, 1], m.cells), color=GREY, lw=0.3, alpha=0.4)
    ax.add_collection(LineCollection(geom.segments, colors=ORANGE if cmap == "YlGnBu" else "k",
                                     linewidths=2.2 if cmap == "YlGnBu" else 1.8))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")


# greyscale scan
fig, ax = square(7.1)
ax.imshow(scan, cmap="gray", vmin=-0.2, vmax=1.2, origin="upper")
fig.savefig(out / "scan.png", facecolor="white"); plt.close(fig)

# tile for the roadmap slide
m = mc.Mesh(40); g = mc.CutGeometry(m, phi)
A, b = mc.poisson_system(g, one, zero)
fig, ax = square(); field(g, mc.solve(g, A, b), ax, 0.0, None, "YlGnBu")
fig.savefig(out / "tile.png", facecolor="white"); plt.close(fig)

rows = []
for n in (20, 40, 80):
    m = mc.Mesh(n); g = mc.CutGeometry(m, phi)
    A, b = mc.poisson_system(g, fe, ue)
    u = mc.solve(g, A, b)
    r = dict(n=n, cut=int((g.cell_type == mc.CUT).sum()), active=len(g.active_cells),
             l2=float(mc.l2_error(g, u, ue)))
    if n == 40:
        k, neg = mc.condition_number(g, A)
        A0, _ = mc.poisson_system(g, fe, ue, ghost=False)
        k0, neg0 = mc.condition_number(g, A0)
        r.update(kappa=float(k), neg=int(neg), kappa_noghost=float(k0), neg_noghost=int(neg0))
        fig, ax = square(); mc.plot_cells(g, ax=ax)
        ax.collections[-1].set_color(ORANGE); ax.collections[-1].set_linewidth(2.2); ax.axis("off")
        fig.savefig(out / "cells.png", facecolor="white"); plt.close(fig)
        fig, ax = square(); field(g, u, ax, -1, 1)
        fig.savefig(out / "solution.png", facecolor="white"); plt.close(fig)
        un = mc.solve(g, A0, mc.poisson_system(g, fe, ue, ghost=False)[1])
        r["l2_noghost"] = float(mc.l2_error(g, un, ue))
    rows.append(r)
for a, b_ in zip(rows[:-1], rows[1:]):
    b_["rate"] = float(np.log2(a["l2"] / b_["l2"]))
json.dump(dict(rows=rows, porosity=float(1 - B.mean())), open(out / "image_numbers.json", "w"), indent=1)
print(json.dumps(rows, indent=1), "matrix fraction of the box", B.mean())
