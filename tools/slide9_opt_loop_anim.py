"""Animation of a real optimisation loop for the rotor: maximise the area over (a, b) subject to the worst peak
temperature over a turn <= T*.  COBYLA (derivative free) around the real cut solver, every evaluation is a frame.
Run: python slide9_opt_loop_anim.py OUTDIR  (needs OUTDIR/opt2_grid.npz for the background map)"""
import sys, os, json, time
out = sys.argv[1] if len(sys.argv) > 1 else "."
sys.argv = [sys.argv[0], out]
import numpy as np
import slide9_opt2 as o
from PIL import Image
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.interpolate import RectBivariateSpline
mc = o.mc
T_star, A_MAX = 150.0, 0.2067
z = np.load(f"{out}/opt2_grid.npz"); As, Bs, T = z["As"][:5], z["Bs"], z["T"][:5]
spT = RectBivariateSpline(As, Bs, T, kx=3, ky=3)
ANG = np.linspace(0, o.PERIOD, 25)[:-1]
hist = []                                  # one entry per evaluation
cache = {}

def evaluate(x):
    a, b = float(x[0]), float(x[1])
    key = (round(a, 9), round(b, 9))
    if key in cache: return cache[key]
    pk = [o.peak2(a, b, t) for t in ANG]; i = int(np.argmax(pk))
    g = mc.CutGeometry(mc.Mesh(40), mc.rotate(o.rot2(a, b), ANG[i]))
    A, r = mc.poisson_system(g, o.f_jet, o.zero, ghost=True); u = mc.solve(g, A, r)
    area = float(mc.area(mc.CutGeometry(mc.Mesh(40), o.rot2(a, b))))
    res = dict(a=a, b=b, peak=max(pk), area=area, geom=g, u=u, theta=float(ANG[i]))
    cache[key] = res; hist.append(res); print(len(hist), f"a={a:.3f} b={b:.3f} peak={max(pk):.1f} area={area:.3f}", flush=True)
    return res

x0 = np.array([0.17, 0.055])
cons = [dict(type="ineq", fun=lambda x: (T_star - evaluate(x)["peak"]) / 100.0),
        dict(type="ineq", fun=lambda x: A_MAX - x[0]), dict(type="ineq", fun=lambda x: x[0] - 0.10),
        dict(type="ineq", fun=lambda x: x[1] - 0.03), dict(type="ineq", fun=lambda x: 0.10 - x[1])]
sol = minimize(lambda x: -evaluate(x)["area"], x0, method="COBYLA", constraints=cons,
               options=dict(rhobeg=0.02, tol=1e-4, maxiter=60))
print(sol.x, sol.fun, len(hist))
af = np.linspace(As[0], As[-1], 80); bf = np.linspace(Bs[0], Bs[-1], 80); Z = spT(af, bf)
# frames
frames = []
best = None
for k, h in enumerate(hist):
    feas = h["peak"] <= T_star * 1.01
    if feas and (best is None or h["area"] > best["area"]): best = h
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 5.2), dpi=100, gridspec_kw=dict(width_ratios=[1, 1.05]))
    o.solution_ax(h["geom"], h["u"], axs[0], T_star); o.jet_ax(axs[0])
    axs[0].set_title(f"evaluation {k+1}:  a = {h['a']:.3f}, b = {h['b']:.3f}\nworst angle {np.degrees(h['theta']):.0f}°,  peak {h['peak']:.0f},  area {h['area']:.3f}", fontsize=13, color="#3B3B3B")
    ax = axs[1]
    ax.contourf(bf, af, Z, levels=np.arange(0, 260, 20), cmap="YlOrRd", alpha=0.55)
    ax.contour(bf, af, Z, levels=[T_star], colors=o.ORANGE, linewidths=3)
    xs = [q["b"] for q in hist[:k+1]]; ys = [q["a"] for q in hist[:k+1]]
    ax.plot(xs, ys, "-", color="k", lw=1, alpha=0.5)
    ax.plot(xs[:-1], ys[:-1], "o", color="#00509A", ms=5, alpha=0.7)
    ax.plot([h["b"]], [h["a"]], "o", color="k", ms=11, mfc="#00509A" if feas else "#C0392B")
    if best: ax.plot([best["b"]], [best["a"]], "*", color="k", ms=15)
    ax.axhline(A_MAX, color="k", lw=1, ls=":"); ax.text(0.099, A_MAX - 0.006, "a ≤ 0.207 (mesh box)", fontsize=11, ha="right")
    ax.text(0.0585, 0.1075, "limit T = 150", color=o.ORANGE, fontsize=12, ha="center", fontweight="bold")
    ax.set_xlim(Bs[0], Bs[-1]); ax.set_ylim(As[0], As[-1] + 0.005)
    ax.set_xlabel("blade half-width b", fontsize=13); ax.set_ylabel("blade semi-length a", fontsize=13); ax.tick_params(labelsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9)); fig.canvas.draw()
    frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()))
    if k == len(hist) - 1: fig.savefig(f"{out}/opt_loop_last.png", facecolor="white")
    plt.close(fig)
frames += [frames[-1]] * 8
pal = [im.convert("P", palette=Image.ADAPTIVE, colors=128) for im in frames]
pal[0].save(f"{out}/opt_loop.gif", save_all=True, append_images=pal[1:], duration=250, loop=0, optimize=True)
json.dump(dict(n=len(hist), best=dict(a=best["a"], b=best["b"], peak=best["peak"], area=best["area"]), x=list(map(float, sol.x)),
               path=[[h["a"], h["b"], h["peak"], h["area"]] for h in hist]), open(f"{out}/opt_loop.json", "w"))
print(best["a"], best["b"], best["peak"], best["area"], os.path.getsize(f"{out}/opt_loop.gif"))
