"""Single-panel animation of the rotor turning through the fixed hot-gas jet (Example 3 poster).

Run from the repository root:   PYTHONPATH=. python tools/rotor_poster_gif.py OUTDIR
Same setup as tools/slide9_rotor.py: five elliptic blades plus a hub, one steady solve per angle,
the mesh never changes; the red dashed circle is the jet, fixed in space.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.collections import LineCollection
from PIL import Image

import minicut as mc

out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
out.mkdir(parents=True, exist_ok=True)
C, NB, JET, AMP, B0 = (0.5, 0.5), 5, (0.5, 0.80, 0.06), 1.0e5, 0.055
PERIOD = 2 * np.pi / NB


def f_jet(x, y):
    return AMP * np.exp(-((x - JET[0]) ** 2 + (y - JET[1]) ** 2) / (2 * JET[2] ** 2))


blade = mc.ellipse((0.75, 0.5), 0.17, B0, 0.35)
rotor = mc.union(mc.circle(C, 0.12), *[mc.rotate(blade, 2 * np.pi * k / NB) for k in range(NB)])
mesh = mc.Mesh(40)
NF = 36
sol = []
for k in range(NF):
    g = mc.CutGeometry(mesh, mc.rotate(rotor, PERIOD * k / NF))
    A, rhs = mc.poisson_system(g, f_jet, lambda x, y: np.zeros_like(x))
    sol.append((g, mc.solve(g, A, rhs)))
vmax = max(float(np.nanmax(u)) for _, u in sol)

frames = []
for g, u in sol:
    fig, ax = plt.subplots(figsize=(4.0, 4.0), dpi=150)
    fig.subplots_adjust(0, 0, 1, 1)
    pts = g.sub_verts.reshape(-1, 2)
    tri = mtri.Triangulation(pts[:, 0], pts[:, 1], np.arange(len(pts)).reshape(-1, 3))
    vals = mc.evaluate(g, u, np.repeat(g.sub_cells, 3), pts)
    ax.tripcolor(tri, vals, shading="gouraud", cmap="YlOrRd", vmin=0, vmax=vmax)
    ax.add_collection(LineCollection(g.segments, colors="k", linewidths=1.6))
    ax.add_patch(plt.Circle((JET[0], JET[1]), 2 * JET[2], fill=False, ls="--", lw=1.6, color="#C0392B", zorder=5))
    ax.set_aspect("equal"); ax.set_xlim(0.04, 0.96); ax.set_ylim(0.04, 0.96); ax.axis("off")
    fig.canvas.draw()
    frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()))
    plt.close(fig)
pal = [im.convert("P", palette=Image.ADAPTIVE, colors=128) for im in frames]
pal[0].save(out / "rotor_poster.gif", save_all=True, append_images=pal[1:], duration=90, loop=0, optimize=True)
print(len(frames), "frames, vmax", vmax)
