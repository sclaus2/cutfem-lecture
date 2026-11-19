"""Example 3, richer optimisation: two design variables (blade semi-length a, half-width b) of the rotor.
Maximise the blade area (strength proxy) subject to the worst-case peak temperature <= T* over a turn.
Reuses slide9_rotor.py's problem set-up. Run: python slide9_opt2.py OUTDIR"""
import sys, os, json, time
import numpy as np
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "."]
out = sys.argv[1]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "slide9_rotor.py")).read()
exec(src[:src.index("# ---- build: three panels")])      # problem set-up only


def rot2(a, b, al=0.35):
    return mc.union(mc.circle(C, 0.12), *[mc.rotate(mc.ellipse((0.75, 0.5), a, b, al), 2 * np.pi * k / NB) for k in range(NB)])


def peak2(a, b, t, n=40):
    g = mc.CutGeometry(mc.Mesh(n), mc.rotate(rot2(a, b), t))
    A, r = mc.poisson_system(g, f_jet, zero, ghost=True)
    return float(np.nanmax(mc.solve(g, A, r)))


def worst2(a, b, n=40, m=24):
    ang = np.linspace(0, PERIOD, m + 1)[:-1]
    return max(peak2(a, b, t, n) for t in ang)


def blade_area(a, b):                      # one ellipse; the five blades do not overlap outside the hub
    return float(np.pi * a * b)


if __name__ == "__main__":
    As = np.linspace(0.10, 0.26, 7); Bs = np.linspace(0.03, 0.10, 8)
    T = np.zeros((len(As), len(Bs))); t0 = time.time()
    for i, a in enumerate(As):
        for j, b in enumerate(Bs):
            T[i, j] = worst2(a, b)
        print(i, time.time() - t0, flush=True)
    np.savez(f"{out}/opt2_grid.npz", As=As, Bs=Bs, T=T)
