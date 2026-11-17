"""Figures and numbers for Example 2 of the lecture: a rotor turns through a fixed hot-gas
jet.  Build it with level sets, turn it (quasi-static: one steady solve per angle), and
tune one design parameter (minicut, 2D, P1).

Run:  python slide9_rotor.py OUTDIR
Problem at every angle:  -Δu = f in Ω_θ,  u = 0 on Γ_θ  (u = temperature rise above the
coolant, f = fixed Gaussian hot-gas jet, amplitude 1e5 in the units of the lecture).
"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from matplotlib.collections import LineCollection
from PIL import Image
from scipy.optimize import brentq
import minicut as mc

out = sys.argv[1] if len(sys.argv) > 1 else "."
BLUE, ORANGE, GREY = "#00509A", "#B34F00", "#6E6E6E"
C, NB = (0.5, 0.5), 5
PERIOD = 2 * np.pi / NB
JET = (0.5, 0.80, 0.06)          # centre x, centre y, width sigma
AMP = 1.0e5
NUM = {}


def f_jet(x, y):
    return AMP * np.exp(-((x - JET[0]) ** 2 + (y - JET[1]) ** 2) / (2 * JET[2] ** 2))


zero = lambda x, y: np.zeros_like(x)


def blade(b=0.055):
    return mc.ellipse((0.75, 0.5), 0.17, b, 0.35)


def blades(b=0.055):
    return mc.union(*[mc.rotate(blade(b), 2 * np.pi * k / NB) for k in range(NB)])


def rotor(b=0.055):
    return mc.union(mc.circle(C, 0.12), blades(b))


def solve_at(b, theta, n=40, ghost=True, kappa=False):
    geom = mc.CutGeometry(mc.Mesh(n), mc.rotate(rotor(b), theta))
    A, rhs = mc.poisson_system(geom, f_jet, zero, ghost=ghost)
    u = mc.solve(geom, A, rhs)
    k = mc.condition_number(geom, A) if kappa else (np.nan, 0)
    return geom, u, float(np.nanmax(u)), float(k[0]), int(k[1])


ANG = np.linspace(0, PERIOD, 25)[:-1]


def worst(b, n=40, m=24):
    ang = np.linspace(0, PERIOD, m + 1)[:-1]
    peaks = [solve_at(b, t, n)[2] for t in ang]
    i = int(np.argmax(peaks))
    return float(peaks[i]), float(ang[i])


def cells_ax(geom, ax, lim=(0.04, 0.96)):
    mc.plot_cells(geom, ax=ax)
    ax.collections[-1].set_color(ORANGE); ax.collections[-1].set_linewidth(2.2)
    ax.set_aspect("equal"); ax.set_xlim(*lim); ax.set_ylim(*lim); ax.axis("off")


def jet_ax(ax):
    ax.add_patch(plt.Circle((JET[0], JET[1]), 2 * JET[2], fill=False, ls="--", lw=1.8, color="#C0392B", zorder=5))


def solution_ax(geom, u, ax, vmax, lim=(0.04, 0.96), mesh=False):
    ns = len(geom.sub_verts)
    pts = geom.sub_verts.reshape(-1, 2)
    cells = np.repeat(geom.sub_cells, 3)
    vals = mc.evaluate(geom, u, cells, pts)
    tri = mtri.Triangulation(pts[:, 0], pts[:, 1], np.arange(3 * ns).reshape(-1, 3))
    ax.tripcolor(tri, vals, shading="gouraud", cmap="YlOrRd", vmin=0, vmax=vmax)
    if mesh:
        m = geom.mesh
        ax.triplot(mtri.Triangulation(m.nodes[:, 0], m.nodes[:, 1], m.cells), color=GREY, lw=0.3, alpha=0.4)
    ax.add_collection(LineCollection(geom.segments, colors="k", linewidths=1.8))
    ax.set_aspect("equal"); ax.set_xlim(*lim); ax.set_ylim(*lim); ax.axis("off")


# ---- build: three panels (geometry only, as before) ------------------------
fig, axs = plt.subplots(1, 3, figsize=(16.64, 4.03), dpi=100)
for ax, ph in zip(axs, (blade(), blades(), rotor())):
    mc.plot_cells(mc.CutGeometry(mc.Mesh(40), ph), ax=ax)
    ax.collections[-1].set_color(ORANGE); ax.collections[-1].set_linewidth(2.2)
    ax.set_aspect("equal"); ax.set_xlim(0, 1); ax.set_ylim(0.06, 0.94); ax.axis("off")
fig.subplots_adjust(0.02, 0.0, 0.98, 1.0, wspace=0.12)
fig.savefig(f"{out}/rotor_build.png", facecolor="white"); plt.close(fig)
g0 = mc.CutGeometry(mc.Mesh(40), rotor())
NUM["build"] = dict(area=float(mc.area(g0)), cut=int((g0.cell_type == mc.CUT).sum()))

# ---- turn: one cycle, n = 40 and 80 ---------------------------------------
b0 = 0.055
sweep = {n: [solve_at(b0, t, n)[2] for t in ANG] for n in (40, 80)}
kon = [solve_at(b0, t, 40, True, True) for t in ANG]
koff = [solve_at(b0, t, 40, False, True) for t in ANG]
NUM["turn"] = dict(
    peak40=sweep[40], peak80=sweep[80],
    max40=max(sweep[40]), min40=min(sweep[40]), max80=max(sweep[80]), min80=min(sweep[80]),
    argmax40_deg=float(np.degrees(ANG[int(np.argmax(sweep[40]))])),
    kappa_ghost=[min(r[3] for r in kon), max(r[3] for r in kon)],
    kappa_none=[min(r[3] for r in koff), max(r[3] for r in koff)], neg_max=max(r[4] for r in koff))
deg = np.degrees(ANG)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.2, 4.9), dpi=100, sharex=True)
for n, col, lw in ((40, BLUE, 2.2), (80, GREY, 1.6)):
    a1.plot(deg, sweep[n], "-o", ms=3.5, color=col, lw=lw, label=f"n = {n}")
a1.set_ylabel("peak temperature max u", fontsize=13); a1.legend(fontsize=12, frameon=False)
a2.semilogy(deg, [r[3] for r in koff], "-o", ms=3.5, lw=1.4, color=ORANGE, label="without ghost penalty")
a2.semilogy(deg, [r[3] for r in kon], "-o", ms=3.5, lw=2.2, color=BLUE, label="with ghost penalty")
a2.set_ylabel("condition number", fontsize=13); a2.set_xlabel("rotation angle θ  (one period = 72°)", fontsize=13)
a2.legend(fontsize=12, frameon=False, loc="center left", bbox_to_anchor=(0.0, 0.40)); a2.set_ylim(50, 2e9)
for a in (a1, a2):
    a.tick_params(labelsize=12); a.grid(alpha=0.3)
    for s in ("top", "right"): a.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{out}/rotor_turn_plot.png", facecolor="white"); plt.close(fig)

# ---- animation: mesh + cut cells | temperature, one period -----------------
frames = []
nf = 36
vmax = NUM["turn"]["max40"]
for k in range(nf):
    th = PERIOD * k / nf
    geom, u, pk, _, _ = solve_at(b0, th, 40)
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 5.4), dpi=100)
    cells_ax(geom, axs[0]); jet_ax(axs[0])
    solution_ax(geom, u, axs[1], vmax, mesh=True); jet_ax(axs[1])
    axs[0].set_title("background mesh, cut cells (orange)", fontsize=13, color="#3B3B3B")
    axs[1].set_title(f"temperature u   (peak {pk:.0f})", fontsize=13, color="#3B3B3B")
    fig.text(0.5, 0.03, f"θ = {np.degrees(th):4.1f}°   (red dashed: hot-gas jet, fixed in space)", ha="center", fontsize=13, color="#3B3B3B")
    fig.subplots_adjust(0.01, 0.08, 0.99, 0.93, wspace=0.03)
    fig.canvas.draw()
    frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()))
    if k == 0:
        fig.savefig(f"{out}/rotor_anim_first.png", facecolor="white")
    plt.close(fig)
pal = [im.convert("P", palette=Image.ADAPTIVE, colors=128) for im in frames]
pal[0].save(f"{out}/rotor_anim.gif", save_all=True, append_images=pal[1:], duration=90, loop=0, optimize=True)
solo = frames[0]
# a single-solution poster for the roadmap slide
geom, u, pk, _, _ = solve_at(b0, np.radians(24), 40)
fig, ax = plt.subplots(figsize=(4.9, 4.9), dpi=100); fig.subplots_adjust(0, 0, 1, 1)
solution_ax(geom, u, ax, vmax); jet_ax(ax)
fig.savefig(f"{out}/rotor_hot.png", facecolor="white"); plt.close(fig)

# ---- tune: widest blade with worst-case peak temperature <= T* -------------
T_star = 150.0
bs = np.linspace(0.03, 0.12, 19)
curve = {n: [worst(b, n)[0] for b in bs] for n in (40, 80)}
rows = []
for n in (40, 80):
    t0 = time.time(); calls = [0]
    def f(b):
        calls[0] += 1
        return worst(b, n)[0] - T_star
    bstar = brentq(f, 0.03, 0.12, xtol=1e-5)
    pk, th = worst(bstar, n)
    area = float(mc.area(mc.CutGeometry(mc.Mesh(n), rotor(bstar))))
    rows.append(dict(n=n, bstar=float(bstar), peak=pk, theta_deg=float(np.degrees(th)), area=area,
                     evals=calls[0], seconds=time.time() - t0))
bst = rows[0]["bstar"]
NUM["tune"] = dict(T_star=T_star, rows=rows)
fig, ax = plt.subplots(figsize=(7.4, 5.2), dpi=100)
for n, col, lw in ((40, BLUE, 2.2), (80, GREY, 1.6)):
    ax.plot(bs, curve[n], "-o", ms=4, lw=lw, color=col, label=f"n = {n}")
ax.axhline(T_star, color=ORANGE, lw=1.6, ls="--"); ax.text(0.031, T_star + 6, "limit T*", color=ORANGE, fontsize=14)
ymax = ax.get_ylim()[1]
for x, lab in ((b0, "start"), (bst, "optimum")):
    ax.axvline(x, color="k", lw=0.8, ls=":"); ax.text(x + 0.002, ymax * 0.78, lab, fontsize=14, rotation=90, va="bottom")
ax.set_xlabel("blade half-width b", fontsize=15); ax.set_ylabel("worst peak temperature over a turn", fontsize=15)
ax.tick_params(labelsize=13); ax.grid(alpha=0.3); ax.legend(fontsize=13, frameon=False, loc="upper left")
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{out}/rotor_tune_plot.png", facecolor="white"); plt.close(fig)
runs = {}
for tag, b in (("start", b0), ("opt", bst)):
    pk, th = worst(b, 40)
    geom, u, _, _, _ = solve_at(b, th, 40)
    runs[tag] = (geom, u, b, pk, th, float(mc.area(geom)))
for tag, (geom, u, b, pk, th, ar) in runs.items():
    fig, ax = plt.subplots(figsize=(4.0, 4.0), dpi=100); fig.subplots_adjust(0, 0, 1, 1)
    solution_ax(geom, u, ax, T_star); jet_ax(ax)
    fig.savefig(f"{out}/rotor_{tag}.png", facecolor="white"); plt.close(fig)
    NUM["tune"][tag] = dict(b=float(b), peak=pk, theta_deg=float(np.degrees(th)), area=ar)
json.dump(NUM, open(f"{out}/rotor_numbers.json", "w"), indent=1)
print(json.dumps({k: v for k, v in NUM.items() if k != "turn"}, indent=1))
print({k: v for k, v in NUM["turn"].items() if k not in ("peak40", "peak80")})
