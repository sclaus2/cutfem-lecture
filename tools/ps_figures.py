"""Figures and checked code of the five 'Poisson step by step' slides (minicut version).

The code blocks of the slides are executed here, so what is shown is what runs.
Run from the repository root:   PYTHONPATH=. python tools/ps_figures.py OUTDIR
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection

import minicut as mc

out = Path(sys.argv[1] if len(sys.argv) > 1 else "ps_out")
out.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- slide 1/5
mesh = mc.Mesh(18, box=(-1, -1, 1, 1))

def level_set(x, y):  # flower, 6 petals
    r = 0.48 * (1 + 0.18 * np.cos(6 * np.arctan2(y, x)))
    return np.sqrt(x**2 + y**2) - r

phi = level_set(mesh.nodes[:, 0], mesh.nodes[:, 1])  # at the nodes

# ---------------------------------------------------------------- slide 2/5
geom = mc.CutGeometry(mesh, phi, order=2)

t = geom.cell_type
inside_cells = np.where(t == mc.INSIDE)[0]
cut_cells = np.where(t == mc.CUT)[0]
active_cells = geom.active_cells

# ---------------------------------------------------------------- slide 3/5
vol = geom.volume  # points, weights on T ∩ Ω
intf = geom.interface  # points, weights, normals on Γ ∩ T
ghost_facets = geom.ghost_facets  # facets of cut cells

# ---------------------------------------------------------------- slide 4/5
f = lambda x, y: np.ones_like(x)  # right-hand side f = 1
g = lambda x, y: np.zeros_like(x)  # boundary value g = 0

A = mc.stiffness(geom)  # ∫Ω ∇u·∇v dx
An, bn = mc.nitsche(geom, g, gamma=40.0)  # Nitsche on Γ
Ag = mc.ghost_penalty(geom, gamma_g=0.1)  # ghost penalty

A = A + An + Ag
b = mc.load(geom, f) + bn  # ∫Ω f v dx and Nitsche

# ---------------------------------------------------------------- slide 5/5
u = mc.solve(geom, A, b)  # on the active dofs only

outside_dofs = np.setdiff1d(np.arange(mesh.n_nodes), geom.active_dofs)
n_outside = len(outside_dofs)

area = mc.area(geom)

# numbers for the notes and a sanity check against the exact value of the problem:
# -Δu = 1, u = 0 on Γ has no closed form for the flower, so check against a disc below
print(geom.summary())
print("cells inside", len(inside_cells), "cut", len(cut_cells), "active", len(active_cells))
print("volume points", len(vol), "interface points", len(intf), "ghost facets", len(ghost_facets))
print("deactivated dofs", n_outside, " area", area, " exact", np.pi*(0.48**2 + 0.5*(0.48*0.18)**2), " max u", np.nanmax(u))
print("vol shape", vol.points.shape, "intf", intf.points.shape, intf.normals.shape)

# check: disc of radius 0.5, exact u = (r0^2 - r^2)/4, error should be small
disc = mc.circle(c=(0, 0), r=0.5)
gd = mc.CutGeometry(mesh, disc, order=2)
Ad, bd = mc.poisson_system(gd, f, g)
ud = mc.solve(gd, Ad, bd)
err = mc.l2_error(gd, ud, lambda x, y: (0.25 - x**2 - y**2) / 4)
print("disc check: L2 error", err)

# ---------------------------------------------------------------- figures
GREEN, ORANGE, RED, BLUE = "#cfe8d5", "#fbd9a8", "#c0392b", "#00509A"
V = mesh.nodes[mesh.cells]


def canvas(w=4.0, h=4.2):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_aspect("equal")
    ax.set_xlim(-1.02, 1.02)
    ax.set_ylim(-1.02, 1.02)
    ax.axis("off")
    fig.subplots_adjust(0.01, 0.01, 0.99, 0.99)
    return fig, ax


def mesh_lines(ax, lw=0.4):
    ax.add_collection(PolyCollection(V, facecolors="none", edgecolors="#555555", linewidths=lw))


def gamma(ax, lw=2.4):
    ax.add_collection(LineCollection(geom.segments, colors="k", linewidths=lw))


def save(fig, name):
    fig.savefig(out / name, dpi=300)
    plt.close(fig)


# 1: mesh + Gamma
fig, ax = canvas(4.0, 4.2)
mesh_lines(ax)
tri = mtri.Triangulation(mesh.nodes[:, 0], mesh.nodes[:, 1], mesh.cells)
ax.tricontour(tri, geom.phi, levels=[0.0], colors="k", linewidths=2.6)
save(fig, "ps1_mesh.png")

# 2: inside / cut cells
for name, cells, col in [("ps2_inside.png", inside_cells, GREEN), ("ps2_cut.png", cut_cells, ORANGE)]:
    fig, ax = canvas(4.0, 4.2)
    ax.add_collection(PolyCollection(V[cells], facecolors=col, edgecolors="none"))
    mesh_lines(ax)
    gamma(ax, 1.6)
    save(fig, name)

# 3: quadrature points
fig, ax = canvas(4.0, 4.2)
mesh_lines(ax, 0.3)
ax.plot(vol.points[:, 0], vol.points[:, 1], ".", color=BLUE, ms=3.2)
save(fig, "ps3_volume.png")
fig, ax = canvas(4.0, 4.2)
mesh_lines(ax, 0.3)
gamma(ax, 1.2)
ax.plot(intf.points[:, 0], intf.points[:, 1], "o", color=RED, ms=3.2)
save(fig, "ps3_interface.png")

# 4: ghost facets
fig, ax = canvas(4.0, 4.2)
ax.add_collection(PolyCollection(V[cut_cells], facecolors=ORANGE, edgecolors="none"))
mesh_lines(ax)
ax.add_collection(
    LineCollection(mesh.nodes[mesh.facet_nodes[ghost_facets]], colors=RED, linewidths=2.6)
)
gamma(ax, 1.6)
save(fig, "ps4_ghost.png")

# 5: deactivated dofs and solution
fig, ax = canvas(4.0, 4.2)
mesh_lines(ax, 0.3)
act = geom.active_dofs
ax.plot(mesh.nodes[act, 0], mesh.nodes[act, 1], ".", color="#555555", ms=3)
ax.plot(mesh.nodes[outside_dofs, 0], mesh.nodes[outside_dofs, 1], "o", color=RED, ms=3.6)
gamma(ax, 1.6)
save(fig, "ps5_dofs.png")

fig, ax = canvas(4.0, 4.2)
ax.set_xlim(-0.66, 0.66)
ax.set_ylim(-0.66, 0.66)
ns = len(geom.sub_verts)
pts = geom.sub_verts.reshape(-1, 2)
cells = np.repeat(geom.sub_cells, 3)
vals = mc.evaluate(geom, u, cells, pts)
tri_s = mtri.Triangulation(pts[:, 0], pts[:, 1], np.arange(3 * ns).reshape(-1, 3))
ax.tricontourf(tri_s, vals, levels=20, cmap="viridis")
gamma(ax, 1.4)
save(fig, "ps5_solution.png")
print("figures written to", out)
print("sum of volume weights", vol.weights.sum())
