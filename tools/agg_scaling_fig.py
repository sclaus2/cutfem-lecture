"""Figure for the ghost penalty / aggregation summary slide. Run: python tools/agg_scaling_fig.py JSON OUTDIR"""
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = json.load(open(sys.argv[1])); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, INK, GREY, GREEN = "#00509a", "#C2570C", "#1F2937", "#6e7a88", "#2E8B57"
plt.rcParams.update({"font.size": 17, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e6e6e6"})
N = np.array([r["ndof"] for r in rows], float)
def slope(key):
    y = np.array([r[key] for r in rows]); return np.polyfit(np.log(N[-3:]), np.log(y[-3:]), 1)[0]
series = [("t_asm_ghost", "assembly with ghost penalty", BLUE, "-"), ("t_asm_plain", "assembly (for aggregation)", GREEN, "--"),
          ("t_agg_build", "building the aggregates", ORANGE, "-"), ("t_solve_ghost", "solve, ghost penalty", BLUE, ":"),
          ("t_solve_agg", "solve, aggregation", ORANGE, ":")]
fig, ax = plt.subplots(figsize=(9.2, 6.0))
for k, lab, c, ls in series:
    y = [r[k] for r in rows]
    ax.loglog(N, y, ls, color=c, lw=3, marker="o", ms=7, label=f"{lab}: N$^{{{slope(k):.2f}}}$")
y0 = rows[0]["t_asm_plain"]
ax.loglog(N, y0*N/N[0]*0.35, color=GREY, lw=2, ls="-.", label="linear: N")
ax.set_xlabel("active DOFs N"); ax.set_ylabel("time (s)")
ax.legend(fontsize=14, frameon=False, loc="upper left")
fig.tight_layout(); fig.savefig(out / "agg_scaling.png", dpi=170, transparent=True); plt.close(fig)
# second figure: nnz overhead and removed dofs
fig, ax = plt.subplots(figsize=(7.2, 6.0))
ax.loglog(N, [r["nnz_ghost"]-r["nnz_plain"] for r in rows], "-o", color=BLUE, lw=3, ms=7, label="ghost penalty: extra non-zeros")
ax.loglog(N, [r["n_removed"] for r in rows], "-o", color=ORANGE, lw=3, ms=7, label="aggregation: removed DOFs")
ax.loglog(N, np.sqrt(N)*8, color=GREY, lw=2, ls="-.", label="$\\sqrt{N}$ (boundary)")
ax.set_xlabel("active DOFs N"); ax.legend(fontsize=14, frameon=False, loc="upper left")
fig.tight_layout(); fig.savefig(out / "agg_overhead.png", dpi=170, transparent=True); plt.close(fig)
for k, *_ in series: print(k, round(slope(k), 2))
print("extra nnz", [r["nnz_ghost"]-r["nnz_plain"] for r in rows], "removed", [r["n_removed"] for r in rows])
