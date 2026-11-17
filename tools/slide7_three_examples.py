"""Three 2D examples computed with minicut: image data, moving interface, CSG shape.
Writes ex_image.png, ex_moving.png, ex_csg.png (square, solution of -Δu=1, u=0 on Γ)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import minicut as mc

out = sys.argv[1] if len(sys.argv) > 1 else "."
BLUE, ORANGE = "#00509A", "#B34F00"

def smooth_union(a, b, k=0.05):
    def phi(x, y):
        pa, pb = a(x, y), b(x, y)
        h = np.clip(0.5 + 0.5 * (pb - pa) / k, 0, 1)
        return pb * (1 - h) + pa * h - k * h * (1 - h)
    return phi

def draw(phi, n, name):
    mesh = mc.Mesh(n)
    geom = mc.CutGeometry(mesh, phi)
    A, b = mc.poisson_system(geom, lambda x, y: np.ones_like(x), lambda x, y: np.zeros_like(x))
    u = mc.solve(geom, A, b)
    fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=100)
    ax.set_aspect("equal"); ax.axis("off")
    ns = len(geom.sub_verts)
    pts = geom.sub_verts.reshape(-1, 2)
    cells = np.repeat(geom.sub_cells, 3)
    vals = mc.evaluate(geom, u, cells, pts)
    tri = mtri.Triangulation(pts[:, 0], pts[:, 1], np.arange(3 * ns).reshape(-1, 3))
    ax.tripcolor(tri, vals, shading="gouraud", cmap="YlGnBu", vmin=0)
    # background mesh, light
    bt = mtri.Triangulation(mesh.nodes[:, 0], mesh.nodes[:, 1], mesh.cells)
    ax.triplot(bt, color="#6E6E6E", lw=0.3, alpha=0.45)
    from matplotlib.collections import LineCollection
    ax.add_collection(LineCollection(geom.segments, colors=ORANGE, linewidths=2.2))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(os.path.join(out, name), facecolor="white")
    plt.close(fig)
    return u

# 1. image data
img = mc.synthetic_scan() > 0.5
draw(mc.levelset_from_image(img), 40, "ex_image.png")
# 2. moving interface: two bubbles close to merging
a = mc.circle((0.36, 0.5), 0.19)
b = mc.circle((0.66, 0.52), 0.15)
draw(smooth_union(a, b, 0.06), 40, "ex_moving.png")
# 3. complex shape from CSG: a cross of two ellipses, with a round hole and a notch
arm1 = mc.ellipse((0.5, 0.5), 0.42, 0.15)
arm2 = mc.ellipse((0.5, 0.5), 0.15, 0.42)
hole = mc.circle((0.5, 0.5), 0.09)
notch = mc.circle((0.9, 0.5), 0.07)
draw(mc.difference(mc.difference(mc.union(arm1, arm2), hole), notch), 40, "ex_csg.png")
