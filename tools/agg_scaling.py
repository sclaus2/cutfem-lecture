"""Scaling of ghost penalty vs aggregation with the mesh size (best of 3). Run: PYTHONPATH=. python tools/agg_scaling.py OUTDIR [nmax]"""
import json, sys, time
from pathlib import Path
import numpy as np
import minicut as mc

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 160
u_ex = lambda x, y: np.sin(np.pi*x)*np.sin(np.pi*y)
f = lambda x, y: 2*np.pi**2*u_ex(x, y)
g = lambda x, y: np.zeros_like(x)

def best(fn, reps=3):
    t = []
    for _ in range(reps):
        t0 = time.perf_counter(); res = fn(); t.append(time.perf_counter() - t0)
    return min(t), res

rows = []; n = 20
while n <= nmax:
    mesh = mc.Mesh(n, box=(-1, -1, 1, 1))
    geom = mc.CutGeometry(mesh, mc.circle((0.037, -0.021), 0.6))
    r = dict(n=n, ndof=int(len(geom.active_dofs)))
    r["t_asm_ghost"], (A, b) = best(lambda: mc.poisson_system(geom, f, g, ghost=True))
    r["t_asm_plain"], (A0, b0) = best(lambda: mc.poisson_system(geom, f, g, ghost=False))
    d = geom.active_dofs
    r["nnz_ghost"] = int(A[d][:, d].nnz); r["nnz_plain"] = int(A0[d][:, d].nnz)
    r["t_solve_ghost"], _ = best(lambda: mc.solve(geom, A, b))
    r["t_agg_build"], agg = best(lambda: mc.aggregate(geom, 0.25))
    r["t_solve_agg"], _ = best(lambda: mc.solve_aggregated(geom, A0, b0, agg))
    r["n_removed"] = int(len(agg.removed_dofs)); r["n_ill"] = int(len(agg.ill_cells))
    print(r, flush=True); rows.append(r); n *= 2
json.dump(rows, open(out / "agg_scaling.json", "w"), indent=1)
