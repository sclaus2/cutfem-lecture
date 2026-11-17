"""Slide HTML for Example 2 (rotor): ex2-build, ex2-turn, ex2-opt.
Run:  python slide9_build.py OUTDIR rotor_numbers.json     (asset ids are the artifact's)"""
import json, os, sys
out = sys.argv[1]; N = json.load(open(sys.argv[2]))
ID = dict(build="71b8c2d63287965fdf455a1b874e8baf", anim="2125713db3bc0dcbcf9c5bc5e6e84d6d",
          turn="736c04f0c5084e223bc2a36e1392184d", tune="be6a50df30e78f4f4664ec2e672c61c3",
          start="b24a9e25c19177add26885f131f0e971", opt="90944c51c982b3c5e5931a64a79f5cc3",
          hot="2934d2c92e1f800a915253ec6dc19959")
F = "font-family:Arial, sans-serif"
MONO = "font-family:'Courier New', monospace"


def sci(x, d=1):
    m, e = f"{x:.{d}e}".split("e"); return f"{m}·10<sup>{int(e)}</sup>"


def footer(n):
    return f'''  <p style="position:absolute; top:992px; left:480px; width:960px; {F}; font-size:24px; text-align:center; color:#6e6e6e">Cut finite element methods · MINES Paris – PSL</p>
  <p style="position:absolute; top:992px; right:128px; width:120px; {F}; font-size:24px; text-align:right; color:#6e6e6e">{n}</p>'''


def section(id_, title, body, note, n="0", gap=36):
    return f'''<section id="{id_}" data-transition="fade" style="display:flex; flex-direction:column; gap:{gap}px; padding:96px 128px 160px; background:#ffffff">
  <h2 style="{F}; font-size:60px; font-weight:700; line-height:1.1; color:#00509a">{title}</h2>
{body}
{footer(n)}
  <aside>{note}</aside>
</section>
'''


def img(key, w, h, alt, extra=""):
    return f'<img src="/_blob/{ID[key]}" alt="{alt}" style="width:{w}px; height:{h}px; object-fit:contain; flex:0 0 auto{extra}">'


def cap(txt, w, extra=""):
    return f'<p style="width:{w}px; {F}; font-size:24px; line-height:1.3; color:#6e6e6e{extra}">{txt}</p>'


def code(lines, w=None):
    ps = "".join(f'<p style="font-size:24px; line-height:1.4; {MONO}; color:#f3f4f6; white-space:pre">{l}</p>' for l in lines)
    ww = f"width:{w}px; box-sizing:border-box; " if w else ""
    return f'<div style="{ww}background:#1f2937; border-radius:16px; padding:20px 32px; display:flex; flex-direction:column; gap:2px">{ps}</div>'


def box(title, paras, colour="blue", w=None):
    bg, fg = ("#eaf1f8", "#00509a") if colour == "blue" else ("#fdebd8", "#b34f00")
    ww = f"width:{w}px; box-sizing:border-box; flex:0 0 auto; " if w else ""
    ps = "".join(f'<p style="{F}; font-size:26px; line-height:1.35; color:#3b3b3b">{p}</p>' for p in paras)
    return f'<div style="{ww}background:{bg}; border-radius:16px; padding:20px 28px; display:flex; flex-direction:column; gap:8px"><p style="{F}; font-size:30px; font-weight:700; color:{fg}">{title}</p>{ps}</div>'


slides = {}

# ---- build ----------------------------------------------------------------
cc = [("φ<sub>blade</sub>", "one blade: a tilted ellipse"),
      ("min over five turned copies", "φ<sub>blade</sub>(R<sub>k</sub><sup>−1</sup>x), each copy turned by 72°"),
      ("min(φ<sub>hub</sub>, φ<sub>blades</sub>)", "union with a disc for the hub: the rotor")]
caps = "".join(f'<div style="width:552px; flex:0 0 auto; text-align:center; {F}; font-size:26px; line-height:1.3; color:#3b3b3b"><b style="color:#00509a">{a}</b><br>{b}</div>' for a, b in cc)
body = f'''  <div style="display:flex; flex-direction:column; gap:12px">
    {img("build", 1664, 403, "Three panels on the same background mesh: one tilted elliptical blade, five blades turned by 72 degrees each, and the five blades united with a round hub as a five-bladed rotor; cells inside in green, cut cells in orange")}
    <div style="display:flex; flex-direction:row">{caps}</div>
  </div>
  {code(["blade = ellipse((0.75, 0.5), 0.17, 0.055, 0.35)",
         "hub   = circle((0.5, 0.5), 0.12)",
         "rotor = union(hub, *[rotate(blade, 2*pi*k/5) for k in range(5)])"])}'''
slides["ex2-build"] = section("ex2-build", "Example 2 · Build a rotor from simple shapes", body,
    "Three minutes. The second example: a turbine rotor, built from simple level sets, then turned, then tuned. First the build. One blade is a tilted ellipse, as in the example code (an approximate signed distance). The blades of the rotor are copies of this blade turned by multiples of 72 degrees: the only new function is rotate, which turns a shape by evaluating its level set at the back-rotated point, φ(R⁻¹(x − c) + c). The union is the pointwise minimum, as on the previous slide, and the hub is a disc added by another union. Each panel is the same 40 by 40 background mesh: the rotor is 0.187 in area and cuts 332 cells; nothing is meshed. The whole construction is three lines of the example code. Next slide: turn it, through a hot-gas jet.", gap=28)

# ---- turn -----------------------------------------------------------------
t = N["turn"]
body = f'''  <div style="display:flex; flex-direction:row; gap:44px; align-items:flex-start">
    <div style="width:980px; display:flex; flex-direction:column; gap:20px; flex:0 0 auto">
      {img("anim", 980, 509, "Animation: a five-bladed rotor turns by one period through a fixed hot-gas jet, shown as a red dashed circle. Left, the background mesh with the cut cells in orange follows the rotor boundary; right, the temperature is high only in the blade that is inside the jet.")}
      {box("The load stays, the rotor turns", ["At each angle θ: −Δu = f in Ω<sub>θ</sub>, u = 0 on Γ<sub>θ</sub>. f is a hot-gas jet fixed in space, u is the temperature rise above the coolant (quasi-static: one steady solve per angle).", f'<span style="{MONO}; font-size:24px">rotor_t = rotate(rotor, theta)</span>&nbsp; then cut, assemble, solve as before'], "blue", 980)}
    </div>
    <div style="width:640px; display:flex; flex-direction:column; gap:20px; flex:0 0 auto">
      {img("turn", 620, 490, "Top: the peak temperature against the rotation angle over one period, from about 4 when no blade is in the jet to about 95 when one is; the n equal 80 curve is within five percent of the n equal 40 curve. Bottom: the condition number against the angle, between 184 and 354 with the ghost penalty and between 2 times 10 to the 5 and 3 times 10 to the 8 without it.")}
      {box("The solution changes with θ", [f'Peak temperature from {t["min40"]:.0f} to {t["max40"]:.0f} within one turn. Condition number: {t["kappa_ghost"][0]:.0f} to {t["kappa_ghost"][1]:.0f} with the ghost penalty, {sci(t["kappa_none"][0],0)} to {sci(t["kappa_none"][1],0)} without.'], "orange", 640)}
    </div>
  </div>'''
slides["ex2-turn"] = section("ex2-turn", "Example 2 · Turn it: same mesh, new cut", body,
    f"Three minutes. Play the animation first and ask what moves and what does not. The grey background mesh never changes; the rotor boundary turns, so the orange cut cells change at every frame, and the temperature field changes with them. Physical story: a rotor turns through a hot-gas jet. The jet is a heat source f fixed in space (the red dashed circle marks twice its width); the boundary of the rotor is kept at the coolant temperature, u = 0; u is the temperature rise. At each angle we solve a steady Poisson problem, so this is a quasi-static picture; a real turbine would need the time-dependent heat equation with the solution carried along with the body, which is a natural extension. Why a fixed load? If the load turned with the rotor, nothing would change: the rotation of a symmetric problem gives the same answer at every angle, and the example would be boring. Right, top: the peak temperature over one period (72 degrees, the five-fold symmetry): about {t['max40']:.0f} when a blade is in the jet (worst angle about {t['argmax40_deg']:.0f} degrees), about {t['min40']:.0f} when the jet falls between two blades. The n = 80 curve (grey) is within 5 percent of the n = 40 curve ({t['max80']:.0f} at the worst angle). Right, bottom: the condition number at the same 24 angles. With the ghost penalty it stays between {t['kappa_ghost'][0]:.0f} and {t['kappa_ghost'][1]:.0f}. Without it, between 2·10⁵ and 3·10⁸, and the matrix is indefinite for some angles (up to {t['neg_max']} negative eigenvalues): in a moving problem you cannot choose where the cuts fall, which is why the ghost penalty came first. The temperature unit is arbitrary: f has amplitude 10⁵ at the jet centre.", gap=30)

# ---- tune -----------------------------------------------------------------
u = N["tune"]; r = {x["n"]: x for x in u["rows"]}; s0, s1 = u["start"], u["opt"]
body = f'''  <div style="display:flex; flex-direction:row; gap:48px; align-items:flex-start">
    <div style="width:700px; display:flex; flex-direction:column; gap:14px; flex:0 0 auto">
      {img("tune", 700, 492, "Worst peak temperature over a turn against the blade half-width b for n equal 40 and n equal 80, increasing from about 30 to 250; the limit T star equal 150 is reached at b about 0.075")}
      {box("The optimum hardly depends on the mesh", [f'b* = {r[40]["bstar"]:.3f} at n = 40, {r[80]["bstar"]:.3f} at n = 80. Cost at n = 40: {r[40]["evals"]} evaluations of the worst case, each 24 cut-and-solves, {r[40]["seconds"]:.0f} s in total.'], "orange", 700)}
    </div>
    <div style="width:916px; display:flex; flex-direction:column; gap:20px; flex:0 0 auto">
      <div style="display:flex; flex-direction:row; gap:24px">
        <div style="display:flex; flex-direction:column; gap:6px; width:446px; align-items:center">{img("start", 340, 340, "Temperature on the starting rotor at its worst angle: the blade in the jet is hot")}{cap(f"start: b = {s0['b']:.3f}, peak {s0['peak']:.0f}, A = {s0['area']:.2f}", 446, "; text-align:center")}</div>
        <div style="display:flex; flex-direction:column; gap:6px; width:446px; align-items:center">{img("opt", 340, 340, "Temperature on the optimised rotor with wider blades at its worst angle")}{cap(f"optimum: b = {s1['b']:.3f}, peak {s1['peak']:.0f}, A = {s1['area']:.2f}", 446, "; text-align:center")}</div>
      </div>
      {box("Design to a temperature limit", ["Widest (strongest) blade with peak temperature ≤ T* = 150 at every angle. The peak grows with b: the optimum is where the worst angle just reaches T*."], "blue", 916)}
      {code(["T_worst = lambda b: max(peak(b, t) for t in angles)",
             "b_star  = brentq(lambda b: T_worst(b) - T_star, 0.03, 0.12)"], 916)}
    </div>
  </div>'''
slides["ex2-opt"] = section("ex2-opt", "Example 2 · A simple shape optimisation", body,
    f"Three minutes. The simplest shape optimisation we can do in the time: one design parameter, the blade half-width b, and one requirement. Wider blades are stronger, but they also get hotter in the jet. We want the widest blade whose temperature stays below the limit T* = 150 at every angle of the turn. peak(b, t) is the maximum of u for the rotor with half-width b turned by t: a new level set, a cut of the same mesh and a solve. T_worst(b) is the maximum over the 24 angles of one period. Because the peak grows with b, the optimum is where T_worst(b) = T*: a one-dimensional root finding with scipy's brentq. Without the temperature limit the widest blade would always win, and without a requirement on strength the thinnest blade would always win: that is why the problem is posed as a limit. It takes {r[40]['evals']} evaluations of T_worst, so {r[40]['evals'] * 24} cut-and-solve steps and {r[40]['seconds']:.0f} s at n = 40 ({r[80]['seconds']:.0f} s at n = 80): no meshing in the loop. Result: b* = {r[40]['bstar']:.4f} at n = 40, {r[80]['bstar']:.4f} at n = 80 (a 2.5 percent difference; the peak itself differs by 5 percent between the two meshes, see the previous slide); the worst angle is about {s1['theta_deg']:.0f} degrees for both designs. The area grows from {s0['area']:.3f} to {s1['area']:.3f}. Real shape optimisation has many parameters or a free boundary and uses the gradient of the objective with respect to the shape (shape derivative), which costs about one more solve; the next slide shows the same loop for a wing. Homework: add the number of blades as a second parameter.", gap=30)

for k, v in slides.items():
    open(os.path.join(out, k + ".html"), "w").write(v)
print(list(slides))
