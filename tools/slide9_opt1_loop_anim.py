"""Animation of the one-parameter optimisation loop (brentq on the blade half-width b): every evaluation of
the worst peak temperature over a turn is a frame.  Run: python slide9_opt1_loop_anim.py OUTDIR"""
import sys, os, json
out = sys.argv[1] if len(sys.argv) > 1 else "."
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "slide9_rotor.py")).read()
sys.argv = [sys.argv[0], out]
exec(src[:src.index("# ---- build: three panels")])
T_star = 150.0
A = np.linspace(0, PERIOD, 25)[:-1]
hist = []
def ev(b):
    runs = [solve_at(b, th, 40) for th in A]                 # (geom, u, peak, ., .) at every angle
    pk = [r[2] for r in runs]
    area = float(mc.area(mc.CutGeometry(mc.Mesh(40), rotor(b))))
    hist.append(dict(b=float(b), peak=float(max(pk)), area=area, runs=runs, pk=pk))
    print(len(hist), f"b={b:.4f} peak={max(pk):.1f} area={area:.3f}", flush=True)
    return max(pk) - T_star
bstar = brentq(ev, 0.03, 0.09, xtol=1e-5)
bs = np.linspace(0.03, 0.09, 13)
curve = [max(solve_at(b, t, 40)[2] for t in A) for b in bs]
frames, durs = [], []
for k, h in enumerate(hist):
    for j, th in enumerate(A):
        g, u = h["runs"][j][0], h["runs"][j][1]
        run = max(h["pk"][:j + 1]); last = j == len(A) - 1
        fig, axs = plt.subplots(1, 2, figsize=(10.4, 5.2), dpi=100, gridspec_kw=dict(width_ratios=[1, 1.05]))
        solution_ax(g, u, axs[0], T_star, mesh=True); jet_ax(axs[0])
        axs[0].set_title(f"evaluation {k+1}:  b = {h['b']:.4f}   (area {h['area']:.3f})\nangle {np.degrees(th):4.1f}°,  peak {h['pk'][j]:.0f},  worst so far {run:.0f}", fontsize=13, color="#3B3B3B")
        ax = axs[1]
        ax.plot(bs, curve, "-", color=GREY, lw=1.6, alpha=0.6)
        ax.axhline(T_star, color=ORANGE, lw=1.6, ls="--"); ax.text(0.031, T_star + 5, "limit T*", color=ORANGE, fontsize=13)
        ax.plot([q["b"] for q in hist[:k]], [q["peak"] for q in hist[:k]], "o", color=BLUE, ms=7, alpha=0.7)
        for m_, q in enumerate(hist[:k]):
            ax.annotate(str(m_ + 1), (q["b"], q["peak"]), (0, 8), textcoords="offset points", ha="center", fontsize=11)
        ax.plot([h["b"]], [run], "o", color="k", ms=11, mfc=BLUE if (last and abs(run - T_star) < 1) else ("#C0392B" if run > T_star else "white"))
        if last: ax.annotate(str(k + 1), (h["b"], run), (0, 8), textcoords="offset points", ha="center", fontsize=11)
        ax.set_xlim(0.03, 0.09); ax.set_ylim(0, max(curve) * 1.05)
        ax.set_xlabel("blade half-width b", fontsize=13); ax.set_ylabel("worst peak temperature over a turn", fontsize=13)
        ax.tick_params(labelsize=11); ax.grid(alpha=0.3)
        for s in ("top", "right"): ax.spines[s].set_visible(False)
        fig.tight_layout(rect=(0, 0, 1, 0.9)); fig.canvas.draw()
        frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()))
        durs.append(900 if last else 70)
        if k == len(hist) - 1 and last: fig.savefig(f"{out}/opt1_loop_last.png", facecolor="white")
        plt.close(fig)
durs[-1] = 2500
pal = [im.convert("P", palette=Image.ADAPTIVE, colors=64) for im in frames]
pal[0].save(f"{out}/opt1_loop.gif", save_all=True, append_images=pal[1:], duration=durs, loop=0, optimize=True)
json.dump(dict(n=len(hist), bstar=float(bstar), path=[[h["b"], h["peak"], h["area"]] for h in hist]), open(f"{out}/opt1_loop.json", "w"))
print(len(hist), bstar, len(frames), os.path.getsize(f"{out}/opt1_loop.gif"))
