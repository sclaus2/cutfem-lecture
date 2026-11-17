"""Generate the slide HTML for the three worked examples (ex1-solve, ex2-frames,
ex2-solve, ex3-steps, ex3-solve).  Image ids are the artifact asset ids."""
import json, sys, os
out = sys.argv[1]; nums = json.load(open(sys.argv[2]))
ID = dict(
    image_cells="027a712c9c676d67a45b97679e7d9b4f", image_sol="7a5a00e7bbd545a2f0d86f1298e20589",
    csg_cells="ddfc435a8bc7984fb6c311151aaf87b4", csg_sol="5830297bf6ea0241e469da427aecbdde",
    csg_steps="70fc2962b10948dbfca0adbcb336d247", mv_frames="8bd198d40ea2a48862ea45835e3eccaa",
    mv0="b07d30535858384d218a35446f855c19", mv1="d91d4abe43028039c438fd4b3bf2d7df",
    mv2="4067b192a28ff6cc00b53cebf9244004", mv3="94ffff09ebbcca4323de98401b4b9c41",
    mv_kappa="01db4b4a4605314e8124967310c3aa24")
F = "font-family:Arial, sans-serif"

def sci(x, d=1):
    m, e = f"{x:.{d}e}".split("e"); return f"{m}·10<sup>{int(e)}</sup>"

def footer(n):
    return f'''  <p style="position:absolute; top:992px; left:480px; width:960px; {F}; font-size:24px; text-align:center; color:#6e6e6e">Cut finite element methods · MINES Paris – PSL</p>
  <p style="position:absolute; top:992px; right:128px; width:120px; {F}; font-size:24px; text-align:right; color:#6e6e6e">{n}</p>'''

def section(id_, title, body, note, n="0"):
    return f'''<section id="{id_}" data-transition="fade" style="display:flex; flex-direction:column; gap:36px; padding:96px 128px 160px; background:#ffffff">
  <h2 style="{F}; font-size:60px; font-weight:700; line-height:1.1; color:#00509a">{title}</h2>
{body}
{footer(n)}
  <aside>{note}</aside>
</section>
'''

def img(key, w, h, alt, extra=""):
    return f'<img src="/_blob/{ID[key]}" alt="{alt}" style="width:{w}px; height:{h}px; object-fit:contain; flex:0 0 auto{extra}">'

def cap(txt, w):
    return f'<p style="width:{w}px; {F}; font-size:24px; line-height:1.3; color:#6e6e6e">{txt}</p>'

def solve_slide(id_, title, k, cells_key, sol_key, alts, shape_name, note):
    d = nums[k]; rows = d["rows"]; ng = d["noghost"]
    tr = ""
    for r in rows:
        rate = f'{r["rate"]:.2f}' if "rate" in r else "–"
        tr += (f'<tr><td>{r["n"]}</td><td>{r["cut"]}</td><td>{sci(r["l2"],2)}</td><td>{rate}</td></tr>')
    kg = rows[1]["kappa"]
    body = f'''  <div style="display:flex; flex-direction:row; gap:36px; align-items:flex-start">
    <div style="width:500px; display:flex; flex-direction:column; gap:10px; flex:0 0 auto">
      {img(cells_key, 500, 500, alts[0])}
      {cap("Cells of the 40 × 40 background mesh: green inside, orange cut", 500)}
    </div>
    <div style="width:500px; display:flex; flex-direction:column; gap:10px; flex:0 0 auto">
      {img(sol_key, 500, 500, alts[1])}
      {cap("u<sub>h</sub> on the active cells; the black line is Γ", 500)}
    </div>
    <div style="width:592px; display:flex; flex-direction:column; gap:22px; flex:0 0 auto">
      <div style="background:#eaf1f8; border-radius:16px; padding:22px 28px; display:flex; flex-direction:column; gap:10px">
        <p style="{F}; font-size:30px; font-weight:700; color:#00509a">Check against a known solution</p>
        <p style="{F}; font-size:26px; line-height:1.35; color:#3b3b3b">u = sin 2πx · sin 2πy, f = −Δu, u = g on Γ</p>
        <table style="{F}; font-size:26px; color:#3b3b3b; width:100%">
          <tr><th style="color:#00509a">n</th><th style="color:#00509a">cut cells</th><th style="color:#00509a">‖u − u<sub>h</sub>‖<sub>L²</sub></th><th style="color:#00509a">rate</th></tr>
          {tr}
        </table>
        <p style="{F}; font-size:24px; line-height:1.3; color:#6e6e6e">Second order, as on a fitted mesh</p>
      </div>
      <div style="background:#fdebd8; border-radius:16px; padding:22px 28px; display:flex; flex-direction:column; gap:8px">
        <p style="{F}; font-size:30px; font-weight:700; color:#b34f00">Why the ghost penalty</p>
        <p style="{F}; font-size:26px; line-height:1.35; color:#3b3b3b">Condition number at n = 40: {sci(ng["kappa"])} without it, with {ng["neg"]} negative eigenvalues; {kg:.0f} with it.</p>
      </div>
    </div>
  </div>'''
    return section(id_, title, body, note)

slides = {}
slides["ex1-solve"] = solve_slide(
    "ex1-solve", "Example 1 · Cut, solve, check", "image", "image_cells", "image_sol",
    ["Background triangle mesh of the porous domain from the image: cells inside in green, cut cells in orange, the boundary of the material and the pores in orange",
     "Computed solution on the porous domain; the pores are holes"],
    "image",
    "Three minutes. Same level set as the previous slides (the synthetic image), now taken all the way to a solution with minicut, the 2D example code of the lecture (P1, Nitsche with γ = 40, ghost penalty with γg = 0.1). Left: the classification of the 40 by 40 mesh, 338 cut cells. Middle: the solution of a manufactured problem, u = sin(2πx) sin(2πy) imposed on every boundary, pores included. Right: the check. Error ratios between 2.06 and 2.10: the order is two, as for a fitted mesh, even though no mesh was built for this geometry. The orange box is the link to the previous section: without the ghost penalty the condition number at n = 40 is 7·10⁵ and the matrix is indefinite (6 negative eigenvalues); with it, 467. Honest remark if asked: the error without ghost penalty is not larger (1.1e-3 against 1.4e-3 here); the ghost penalty repairs the matrix, not the accuracy.")
slides["ex3-solve"] = solve_slide(
    "ex3-solve", "Example 3 · Cut, solve, check", "csg", "csg_cells", "csg_sol",
    ["Background triangle mesh with the cross-shaped domain: cells inside in green, cut cells in orange",
     "Computed solution on the cross-shaped domain with a round hole and a notch"],
    "csg",
    "Two minutes. The shape of the previous slide, solved with minicut: manufactured solution u = sin(2πx) sin(2πy), Nitsche and ghost penalty. The mesh knows nothing about the hole, the notch or the four arms. Error ratios of 2.05 and 2.11: second order. Without the ghost penalty the condition number at n = 40 is 2.9·10⁶ with 7 negative eigenvalues; with it, 235.")

# ---- example 2
cols = "".join(f'<div style="width:392px; flex:0 0 auto; {F}; font-size:26px; line-height:1.3; color:#3b3b3b"><b style="color:#00509a">{a}</b><br>{b}</div>'
               for a, b in [("t = 0", "two separate bubbles"), ("t = 0.5", "they approach"), ("t = 0.8", "they touch: topology change"), ("t = 1", "one bubble")])
body = f'''  <div style="display:flex; flex-direction:column; gap:14px">
    {img("mv_frames", 1664, 234, "Four frames of two bubbles that approach and merge on the same 40 by 40 triangular background mesh; cells inside in green, cut cells in orange, the boundary in orange")}
    <div style="display:flex; flex-direction:row; gap:32px">{cols}</div>
  </div>
  <div style="display:flex; flex-direction:row; gap:48px; align-items:flex-start">
    <div style="width:880px; flex:0 0 auto; display:flex; flex-direction:column; gap:14px">
      <div style="background:#eaf1f8; border-radius:16px; padding:22px 28px"><p style="{F}; font-size:30px; line-height:1.4; color:#00509a">φ(x, y, t) = smooth min of |x − c<sub>1</sub>(t)| − r<sub>1</sub> and |x − c<sub>2</sub>(t)| − r<sub>2</sub></p></div>
      <ul style="margin:0; {F}; font-size:28px; line-height:1.4; color:#3b3b3b">
        <li>Centres c<sub>1</sub>(t), c<sub>2</sub>(t) move; the background mesh does not</li>
        <li>At each time step: evaluate φ at the nodes, classify the cells, rebuild the quadrature on the cut cells</li>
      </ul>
    </div>
    <div style="flex:1; background:#fdebd8; border-radius:16px; padding:22px 28px; display:flex; flex-direction:column; gap:8px">
      <p style="{F}; font-size:30px; font-weight:700; color:#b34f00">The merge is not an event</p>
      <p style="{F}; font-size:26px; line-height:1.35; color:#3b3b3b">With a fitted mesh, the merge needs remeshing and a change of topology. Here only the sign pattern of φ changes.</p>
    </div>
  </div>'''
slides["ex2-frames"] = section("ex2-frames", "Example 2 · A moving interface, a fixed mesh", body,
    "Two minutes. Four frames of the animation from the motivation slide, now with the cut cells shown for what they are. The level set is a smooth minimum of two disc distances, so the bubbles merge into one smooth shape; the centres move linearly. At each time step we evaluate φ at the nodes of the same 40 by 40 mesh, classify the cells (green inside, orange cut, grey outside), and compute the quadrature rules on the orange cells. Nothing else changes. At t = 0.8 the two bubbles touch: with a fitted mesh this is a change of topology; here it is only a different sign pattern. Next slide: what happens to the matrix at every step.")

tk = nums["moving"]["kappa"]
grid = "".join(f'<div style="width:340px; display:flex; flex-direction:column; gap:4px">{img(k, 340, 190, "Solution of a Poisson problem on the bubbles at time %s" % t)}<p style="{F}; font-size:24px; color:#6e6e6e">t = {t}</p></div>'
               for k, t in [("mv0", "0"), ("mv1", "0.5"), ("mv2", "0.8"), ("mv3", "1")])
body = f'''  <div style="display:flex; flex-direction:row; gap:40px; align-items:flex-start">
    <div style="width:900px; display:flex; flex-direction:column; gap:8px; flex:0 0 auto">
      {img("mv_kappa", 900, 562, "Condition number of the stiffness matrix against time for 61 time steps: with the ghost penalty it stays between 196 and 290; without it it jumps between 5000 and 10 to the 17")}
    </div>
    <div style="width:724px; display:flex; flex-direction:column; gap:22px; flex:0 0 auto">
      <div style="display:grid; grid-template-columns:340px 340px; gap:12px 20px">{grid}</div>
      <div style="background:#fdebd8; border-radius:16px; padding:20px 28px; display:flex; flex-direction:column; gap:8px">
        <p style="{F}; font-size:30px; font-weight:700; color:#b34f00">Same mesh, 61 time steps</p>
        <p style="{F}; font-size:26px; line-height:1.35; color:#3b3b3b">Condition number: {sci(min(tk["none"]),0)} to {sci(max(tk["none"]),0)} without the ghost penalty, {min(tk["ghost"]):.0f} to {max(tk["ghost"]):.0f} with it</p>
      </div>
    </div>
  </div>'''
slides["ex2-solve"] = section("ex2-solve", "Example 2 · Solve at every time step", body,
    "Three minutes. We solve −Δu = 1, u = 0 on Γ at each of 61 time steps, on the same 40 by 40 mesh (minicut, Nitsche, optional ghost penalty). Right: the solution at four of the instants. Left: the condition number of the matrix. Without the ghost penalty it is erratic: every time a bubble boundary passes close to a vertex, a cut cell becomes tiny and the condition number explodes; the peaks at 10 to the 16 or 17 mean the matrix is numerically singular. With the ghost penalty the condition number stays between 196 and 290 for the whole motion: a solver tuned once keeps working. This is the practical argument for the previous section: in a moving problem you cannot choose where the cuts fall.")

# ---- example 3
caps = [("φ₁", "ellipse 0.42 × 0.15"), ("φ₂", "ellipse 0.15 × 0.42"), ("min(φ₁, φ₂)", "union: a cross"),
        ("max(φ, −φ₃)", "difference: a round hole"), ("max(φ, −φ₄)", "difference: a notch")]
ccols = "".join(f'<div style="width:312px; flex:0 0 auto; {F}; font-size:26px; line-height:1.3; color:#3b3b3b"><b style="color:#00509a">{a}</b><br>{b}</div>' for a, b in caps)
code = [("c = (0.5, 0.5)", ""), ("arms  = union(ellipse(c, 0.42, 0.15), ellipse(c, 0.15, 0.42))", ""),
        ("shape = difference(difference(arms, circle(c, 0.09)),", ""),
        ("                   circle((0.9, 0.5), 0.07))", "")]
codehtml = "".join(f'<p style="font-size:24px; line-height:1.4; font-family:\'Courier New\', monospace; color:#f3f4f6; white-space:pre">{l}</p>' for l, _ in code)
body = f'''  <div style="display:flex; flex-direction:column; gap:12px">
    {img("csg_steps", 1664, 340, "Five panels on the same background mesh: an horizontal ellipse, a vertical ellipse, their union as a cross, the cross with a round hole in the middle, and the same with a notch on the right arm; cells inside in green, cut cells in orange")}
    <div style="display:flex; flex-direction:row; gap:26px">{ccols}</div>
  </div>
  <div style="background:#1f2937; border-radius:16px; padding:20px 32px; display:flex; flex-direction:column; gap:2px">{codehtml}</div>'''
slides["ex3-steps"] = section("ex3-steps", "Example 3 · Build a shape with min and max", body,
    "Three minutes. Constructive solid geometry step by step, in 2D, with the table of the min/max slide. Two ellipses, one horizontal and one vertical: each is a level set (an approximate distance). Their union is the pointwise minimum: a cross. The round hole is a difference: max(φ, −φ3), the cross without the disc. The notch on the right arm is a second difference. Each panel is the same 40 by 40 background mesh, classified again; nothing is meshed, we only combine functions. Bottom: the whole construction in minicut is two lines, with the functions union and difference of the example code. The same two lines work in CutFEMx with UFL expressions or interpolated functions. Next slide: solve on this shape.")
for k, v in slides.items():
    open(os.path.join(out, k + ".html"), "w").write(v)
print(list(slides))
