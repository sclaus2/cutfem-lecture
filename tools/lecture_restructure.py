"""Restructure the lecture deck around three examples, all in minicut.

Reads and writes the project folder of the Slides artifact (project/deck.json and
project/slides/*.html).  The step slides ps-1 ... ps-5 and ps-stab are written by
tools/ps_build.py, the figures by cond_sweep.py, lecture_figures.py, image_example.py.

Usage:  python tools/lecture_restructure.py BUILD_DIR      (BUILD_DIR/project/...)
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) / "project"
SL = ROOT / "slides"

# ids of the uploaded figures (artifact assets)
A = dict(
    aggregation="1ffc7b77cc7ddd9b9bb507483f5b2c1c", cells="233d891ecf566e3257938e28e7fc9598",
    classify_cut="c79f0db5584cf43616f0961596b75e45", cond_cost="65a0ee74bfd1cae44d294a2202811514",
    cond_modes="934973da2f21fe5c141f882ec842def7", cond_setup="00d324bfb924b79883402b698f9d3851",
    cond_sweep="830c855f01feaf735c2b9c3a422a3b5f", convergence="ff4102144b35760b9e5382af0794ab27",
    first_active="f11ef7edab25e57abe0564dc2116961e", first_warp="7151eca72b8e87592bd6fa6ac44b2b1b",
    img_four="c36c3f90ff5b14b623d9d328ba1356bd", scan="a398f991df1e6ee9d6c573cf03efd14b",
    small_cuts="7a60762ca59d7534bd33dcbaac3f45b6", solution="9d7ef1b2520322753500a641abb20ffd",
    tile="561f273224a43eea97971fd36e855627",
    # older assets that are still right
    ps3_volume="2bb2108c9b21f61b130773de18f17bcf", ps3_interface="309bad6182d4328a939934be61235add",
    ps4_ghost="f6e39b1be9c2fe8a184ba313db3fec81", ps5_solution="e56284a2c551b54a14d7beabe00bb171",
    rotor_tile="2934d2c92e1f800a915253ec6dc19959",
)


def rd(name):
    return (SL / f"{name}.html").read_text()


def wr(name, s):
    (SL / f"{name}.html").write_text(s)


def sub(s, old, new, count=1):
    assert s.count(old) == count, f"expected {count} x {old[:70]!r}, found {s.count(old)}"
    return s.replace(old, new)


def notes(s, text):
    assert s.count("<aside>") == 1
    return re.sub(r"<aside>.*?</aside>", lambda m: "<aside>" + text + "</aside>", s, flags=re.S)


def img(s, old_id, new_id):
    return sub(s, f"/_blob/{old_id}", f"/_blob/{new_id}")


def title(s, old, new):
    return sub(s, f">{old}</h2>", f">{new}</h2>")


# ------------------------------------------------------------------ opening
s = rd("mot-images")
s = img(s, "7ac8c7aef56228e47f56171b848b5fd3", A["scan"])
s = re.sub(r"Left: an image generated for this lecture, similar to a micro-CT slice of a porous material \(synthetic, not a real scan\)\.",
           "Left: an image generated for this lecture, similar to a micro-CT slice of a porous material: light solid matrix, dark pores (synthetic, not a real scan).", s)
assert "light solid matrix" in s
s = re.sub(r"how they would mesh the left image with the methods of this week: every pore needs its own boundary, and the mesh must follow it\.",
           "how they would mesh the left image with the methods of this week: every pore needs its own boundary, and the mesh must follow it. We will solve in the solid matrix, with the pores empty.", s)
wr("mot-images", s)

wr("three-examples", '''<section id="three-examples" data-transition="fade" style="display:flex; flex-direction:column; gap:40px; padding:96px 128px 160px; background:#ffffff">
  <h2 style="font-family:Arial, sans-serif; font-size:60px; font-weight:700; line-height:1.1; color:#00509a">Three examples we will build, step by step</h2>
  <div style="display:flex; flex-direction:row; gap:52px; align-items:start; justify-content:center">
    <div style="width:520px; display:flex; flex-direction:column; gap:14px; flex:0 0 auto">
      <img src="/_blob/%(ps5_solution)s" alt="Contour plot of the solution of a Poisson problem on a flower-shaped domain cut out of a square background mesh" style="width:520px; height:520px; object-fit:contain; align-self:center">
      <h3 style="font-family:Arial, sans-serif; font-size:32px; font-weight:700; color:#00509a">1. Poisson on a flower</h3>
      <p style="font-family:Arial, sans-serif; font-size:28px; line-height:1.35; color:#3b3b3b">Every step explained: level set, cut cells, quadrature, Nitsche, small cuts, convergence</p>
    </div>
    <div style="width:520px; display:flex; flex-direction:column; gap:14px; flex:0 0 auto">
      <img src="/_blob/%(tile)s" alt="Solution of a Poisson problem in the solid matrix of a porous specimen obtained from an image, computed on a fixed triangular background mesh; the pores are empty and the cut boundary is orange" style="width:520px; height:520px; object-fit:contain; align-self:center">
      <h3 style="font-family:Arial, sans-serif; font-size:32px; font-weight:700; color:#00509a">2. A porous specimen</h3>
      <p style="font-family:Arial, sans-serif; font-size:28px; line-height:1.35; color:#3b3b3b">Pixels → signed distance → level set φ, then solve in the matrix, with the pores empty</p>
    </div>
    <div style="width:520px; display:flex; flex-direction:column; gap:14px; flex:0 0 auto">
      <img src="/_blob/%(rotor_tile)s" alt="Temperature in a five-bladed rotor built from level sets, computed on a fixed triangular background mesh; one blade is hot where it passes through a fixed hot-gas jet, drawn as a red dashed circle" style="width:520px; height:520px; object-fit:contain; align-self:center">
      <h3 style="font-family:Arial, sans-serif; font-size:32px; font-weight:700; color:#00509a">3. A rotor: build, turn, tune</h3>
      <p style="font-family:Arial, sans-serif; font-size:28px; line-height:1.35; color:#3b3b3b">Union of turned blades, turned through a hot-gas jet by changing φ only, then the widest blade that stays below a temperature limit</p>
    </div>
  </div>
  <p style="position:absolute; top:992px; left:480px; width:960px; font-family:Arial, sans-serif; font-size:24px; text-align:center; color:#6e6e6e">Cut finite element methods · MINES Paris – PSL</p>
  <p style="position:absolute; top:992px; right:128px; width:120px; font-family:Arial, sans-serif; font-size:24px; text-align:right; color:#6e6e6e">0</p>
  <aside>Two minutes. The three situations of the previous slides: scans, implicit shapes, moving shapes. We build three examples, all with the Python code of this lecture (minicut: numpy, scipy, matplotlib, nothing to install). Example 1 is the long one: Poisson on a flower, built step by step, where each step is first explained and then written in code: level set, cut and classify, quadrature, Nitsche, small cuts and their repair, solve, convergence. Example 2 repeats the same steps for a porous specimen given as an image: we solve in the solid matrix, the pores are empty (they could also be filled with a second material, which is an interface problem). Example 3 is a five-bladed rotor built from simple level sets with union, turned through a hot-gas jet that is fixed in space by changing the level set only, and finally tuned: find the widest blade whose peak temperature stays below a limit at every angle (a first shape optimisation). In all of them the background mesh never changes, the orange line is the boundary, the grey lines are the mesh.</aside>
</section>
''' % A)

s = rd("idea")
s = notes(s, "Three minutes. This is the roadmap of the lecture, one block per column, and also the order of the steps of Example 1: the level set and the classification of cells (8 to 17 min), integration on cut cells (17 to 26), Nitsche (26 to 36), small cuts, conditioning and the two remedies (36 to 51), then solve and convergence (51 to 55). The same steps are then repeated for two more examples, an image (55 to 67) and a rotor (67 to 80). Stress that nothing else changes: the Galerkin method, the element spaces and the solver are those of the week.")
wr("idea", s)

s = rd("nutshell")
s = notes(s, "Three minutes. Same slide as the recap, now with the answers. Steps 2, 5 and 6 are untouched: same element spaces, same solver, same reconstruction. Steps 1, 3, 4 changed in the way the next blocks will show, and one new step stabilises small cuts. Say explicitly: the Galerkin method and its best-approximation property (lecture 1) are what we are still doing. From here on we go through these steps on one example, the flower, and every step ends with the code in minicut.")
wr("nutshell", s)

# ------------------------------------------------------------------ Example 1: geometry
s = rd("first-cut")
s = title(s, "A first cut: Poisson on a flower", "Example 1 · The goal: Poisson on a flower")
s = img(s, "b7efaaa488613c44a136ab7f58286caf", A["first_active"])
s = img(s, "5a6c824713d99fd0b77589b2ed1d878a", A["first_warp"])
s = sub(s, "width:660px;height:590px", "width:660px;height:562px")
s = notes(s, "Three minutes. Show the result before any theory. The problem is the Poisson problem of the week with a flower-shaped domain: the boundary is not made of mesh edges. The background mesh is a regular grid of 18 by 18 squares, each split into two triangles. Green cells are inside, orange cells are cut by the boundary, white cells are never touched. The solution on the right lives on the green and orange cells and is zero on the flower boundary (imposed weakly, see later). Promise: by the end of this example they will know every step that produced this picture, and each step ends with the lines of code that do it, in minicut, the small Python package of the lecture. Figures made with minicut (tools/lecture_figures.py).")
wr("first-cut", s)

s = rd("levelset")
s = notes(s, re.search(r"<aside>(.*?)</aside>", s, re.S).group(1).replace(
    "as in the demo (flower-shaped domain, six petals)", "as in the flower of Example 1 (six petals)"))
wr("levelset", s)

s = rd("classify")
s = img(s, "f00fd36aa70aa3ad689ade827a610261", A["classify_cut"])
wr("classify", s)

s = rd("activemesh")
s = img(s, "3a61c4cfdf7db11a991e2a36bf2dafc6", A["first_active"])
s = notes(s, "Two minutes. The finite element space is the usual P1 (or P2) space, restricted to the active mesh. Nothing new in the spaces. The warning about DOFs outside Ω is the seed for the conditioning block a few slides further on.")
wr("activemesh", s)

# ------------------------------------------------------------------ integration
s = rd("cut-cell")
s = sub(s, "With curved cuts (P2 level set) the pieces are curved and the rules are more involved; CutCells generates them, and the idea is the same.",
        "With curved cuts (P2 level set) the pieces are curved and the rules are more involved; the idea is the same.")
wr("cut-cell", s)

s = rd("quad-rules")
s = img(s, "5350ac974e83f253810ef9b800957d3c", A["ps3_volume"])
s = img(s, "6178d56b547c28d8201c8d44ed643fa7", A["ps3_interface"])
s = sub(s, "In CutFEMx the rules are generated at runtime per cut cell and passed to the form as a measure.",
        "In minicut the rules are two objects, geom.volume and geom.interface, produced when the mesh is cut; they hold the points, the weights and, on Γ, the normals.")
wr("quad-rules", s)

# ------------------------------------------------------------------ boundary conditions
s = rd("nitsche-code")
s = re.sub(r" In CutFEMx the same forms are written in UFL, a = inner\(grad\(u\), grad\(v\)\) \* dx_omega \+ \(\.\.\.\) \* dx_gamma, where dx_omega and dx_gamma carry the runtime quadrature rules\.", "", s)
assert "CutFEMx" not in s
wr("nitsche-code", s)

# ------------------------------------------------------------------ conditioning
s = rd("small-cuts")
s = img(s, "e775780b3729e5ad7531108348ef7e95", A["small_cuts"])
s = sub(s, "η = 1.3·10⁻⁸ gave κ(A) = 1.5·10⁹", "η = 1.3·10⁻⁸ gave κ(A) = 2.0·10⁹")
s = sub(s, "81 positions of a disc on a fixed mesh, no stabilisation.", "81 positions of a disc on a fixed mesh, no stabilisation (minicut).")
s = sub(s, "Three minutes. Notation:", "Three minutes. Notation:")
wr("small-cuts", s)

s = rd("cond-setup")
s = img(s, "56a02dc9fc5ee6e401d83d9a05b02e9e", A["cond_setup"])
s = sub(s, "Figure and data were generated for this lecture.",
        "Figure and data are computed with minicut (tools/cond_sweep.py in the repository); the same sweep is section 7 of the notebook.")
wr("cond-setup", s)

s = rd("cond-sweep")
s = img(s, "d563908a08e83ce8d602ef274cfe24b0", A["cond_sweep"])
s = sub(s, 'alt="Left: condition number against disc radius from 0.50 to 0.60 on a log scale. Without stabilisation it jumps between 2e3 and 1.5e9 and crosses mark an indefinite matrix; with ghost penalty it stays between 1e2 and 3e2. Right: L2 error against radius, with a spike up to ten times larger without stabilisation."',
        'alt="Left: condition number against disc radius from 0.50 to 0.60 on a log scale. Without stabilisation it jumps between 2e3 and 2e9 and crosses mark an indefinite matrix; with ghost penalty it stays between 1e2 and 3e2. Right: L2 error against radius, between 6e-3 and 1e-2 for both."')
s = sub(s, "κ from 2·10³ to 1.5·10⁹. Matrix indefinite for 59 of 81 positions. L² error up to 8·10⁻².",
        "κ from 2·10³ to 2·10⁹. Matrix indefinite for 55 of 81 positions. L² error between 6.6·10⁻³ and 9.4·10⁻³.")
s = sub(s, "κ between 1.3·10² and 2.9·10². Error between 7·10⁻³ and 10⁻².",
        "κ between 1.3·10² and 2.9·10². Error between 7.2·10⁻³ and 1.0·10⁻².")
s = sub(s, "Same mesh, same equation: only the boundary moved, by one cell width.",
        "Same mesh, same equation: only the boundary moved, by one cell width. The error hardly notices; the matrix does.")
s = notes(s, "Three minutes. This is the experiment. One fixed 20 by 20 mesh, h = 0.1, and a disc whose radius changes from 0.50 to 0.60, so the boundary moves by one cell width in 81 steps. For each position we assemble the Nitsche system with and without the ghost penalty. Left: the condition number. Without stabilisation it jumps over almost six orders of magnitude, from about 2e3 to 2e9, with no pattern in r. With the ghost penalty it stays between 130 and 290. Crosses mark the 55 positions where the matrix has negative eigenvalues. Right: the L2 error. It is between 6.6e-3 and 9.4e-3 without stabilisation and between 7.2e-3 and 1.0e-2 with it: the accuracy hardly changes, the error is controlled by the mesh and not by the bad cuts (correlation of log kappa with log error: 0.25). Ask the students: so why do we care? The next slides show the mechanism, and the cost: the solver. Say honestly that for a direct solve on this size the damage stays invisible in the error; for iterative solvers, for larger problems, for eigenvalue problems or when the matrix is indefinite, it does not. Data computed with minicut (dense eigenvalue computation on the active DOFs).")
wr("cond-sweep", s)

s = rd("cond-modes")
s = img(s, "6335885f7e9441d452b523725c35fc1c", A["cond_modes"])
s = sub(s, "eigenvalue minus 1.9e-8", "eigenvalue minus 1.4e-8")
s = sub(s, "eigenvalue is negative: the Nitsche matrix", "eigenvalue is negative: the Nitsche matrix")
s = notes(s, "Three minutes. We take the worst case of the sweep, r = 0.595, and look at the eigenvector that belongs to the smallest eigenvalue. Each dot is a degree of freedom on the active mesh and its colour is the amplitude of the mode. Without stabilisation the mode is a single spike on a DOF at the bottom of the mesh, at (-0.2, -0.7), a vertex outside the disc whose cells contain only a tiny piece of it (volume fractions 1e-8 and 4e-8). The energy of that mode is almost zero, and because the Nitsche boundary terms are not sign definite the eigenvalue is slightly negative: minus 1.4e-8. So the matrix is not even positive definite and the condition number blows up to 2e9. With the ghost penalty the same eigenvector is a smooth, global function and the eigenvalue is +0.15, a normal size. Link back to the active-mesh slide: the DOFs outside the domain were the warning. (mc.smallest_mode in minicut computes this.)")
wr("cond-modes", s)

s = rd("ghost")
s = img(s, "ea3ed1fd94ef99146330fdc6ae34b376", A["ps4_ghost"])
s = sub(s, "In the demo: gamma_g = 0.1 and the term sits on dS_ghost.", "In minicut: mc.ghost_penalty(geom, gamma_g=0.1), one term on the facets geom.ghost_facets.")
wr("ghost", s)

s = rd("aggregation")
s = img(s, "f27d442e492c0fed1e057de9369a6000", A["aggregation"])
s = sub(s, "12×12 mesh, disc of radius 0.6: 18 ill-posed cells among 48 cut cells.",
        "12×12 mesh, disc of radius 0.6: 18 ill-posed cells among 48 cut cells, 7 dofs removed.")
s = sub(s, "Both restore a well-conditioned system.",
        "Both restore a well-conditioned system: over the sweep κ stays between 1.2·10² and 2.2·10², and the matrix stays positive definite.")
s = notes(s, "Three minutes. Aggregation is the second repair. We detect the cut cells whose domain fraction is below a threshold, here 0.25, and attach each of them to a well-cut root cell nearby, through the facets of the active mesh; the group is an aggregate. On an aggregate the finite element function is the polynomial of the root cell, extended over the whole aggregate, so the DOFs on the sliver cells are no longer independent unknowns: a dof that touches no well-cut cell is removed and its value is the root polynomial evaluated at it. In matrix form u = E u_good, where E has one column per remaining dof, and the reduced system is E^T A E u_good = E^T b. Nothing is added to the weak form, the matrix is smaller, and the sliver is controlled by construction. In minicut: mc.aggregate(geom, threshold) and mc.solve_aggregated. The figure is made on a coarse 12 by 12 mesh so the cells are visible: orange cells are ill-posed (18 of 48 cut cells), blue are their root cells, thick lines outline the aggregates; 7 dofs are removed. On the 20 by 20 sweep 8 to 15 dofs are removed and kappa is between 121 and 220. Reference: Badia, Verdugo, Martin, Computer Methods in Applied Mechanics and Engineering, 2018.")
wr("aggregation", s)

s = rd("cond-cost")
s = img(s, "c639e467eb9877a9d48eabb134ee5765", A["cond_cost"])
s = sub(s, 'alt="Left: GMRES iterations against disc radius. Without stabilisation 88 to 144, with ghost penalty 48 to 62, both about 25 with diagonal scaling. Right: condition number with and without diagonal scaling."',
        'alt="Left: GMRES iterations against disc radius. Without stabilisation 102 to 150, with ghost penalty 61 to 77, with aggregation 51 to 66, and 34 to 48 for all three with diagonal scaling. Right: condition number after diagonal scaling, up to 101 without stabilisation and below 52 with ghost penalty or aggregation."')
s = sub(s, "Ghost penalty halves the GMRES iterations (48–62 instead of 88–144). A diagonal scaling brings both to about 25, but only the ghost penalty keeps κ below 52 and the matrix positive definite.",
        "Both repairs cut the GMRES iterations from 102–150 to 61–77 (ghost penalty) and 51–66 (aggregation). A diagonal scaling brings all three to 34–48, but only the repairs keep κ below 52 and the matrix positive definite.")
s = notes(s, "Two minutes. Link to lecture 3: the cost of the solve. The same 81 positions. Left: GMRES iterations to reduce the residual by 1e-8, with no preconditioner (solid) or with a diagonal (Jacobi) scaling (dashed). Without stabilisation 102 to 150 iterations, with ghost penalty 61 to 77, with aggregation 51 to 66. A simple diagonal scaling already removes most of the problem for all three, 34 to 48 iterations: it equilibrates the tiny rows of the sliver cells. Right: the condition number after scaling. With ghost penalty or aggregation it is between 37 and 52 for every position. Without stabilisation it is mostly small too, but it reaches 101 in the worst case, and the matrix is still indefinite for 55 of the 81 positions. Take-away: cheap preconditioning helps the solver, but the stabilisation is what makes the problem well posed. A direct solver is affected by the same near-singularity through the pivots. Dense eigenvalue and GMRES computations on the active DOFs with minicut (mc.gmres_iterations, mc.condition_number); no preconditioner other than the diagonal scaling was tested.")
wr("cond-cost", s)

# ------------------------------------------------------------------ Example 1: end
s = rd("convergence")
s = title(s, "Convergence: the rates of the fitted mesh", "Example 1 · Convergence: the rates of the fitted mesh")
s = img(s, "b844503e6b8dc0548011f88138b5850b", A["convergence"])
s = sub(s, 'alt="Two log-log plots of the error against h for the cut Poisson problem. L2 error slope about 2 and H1 seminorm slope about 1 with no stabilisation, ghost penalty and extension."',
        'alt="Two log-log plots of the error against h for the cut Poisson problem on the flower. L2 error slope about 2 and H1 seminorm slope about 1 with no stabilisation, ghost penalty and aggregation."')
s = sub(s, "P1 elements: L² slope ≈ 2, H¹ seminorm slope ≈ 1, with or without stabilisation",
        "P1 elements on the flower, manufactured solution u = sin πx · sin πy, h = 0.2 … 0.0125: L² slope ≈ 2, H¹ seminorm slope ≈ 1, with or without stabilisation")
s = notes(s, "Three minutes. Recall lecture 3: for P1 the error in L2 decreases like h squared and the H1 seminorm error like h. Here the flower of Example 1 is solved with a manufactured solution, u = sin(pi x) sin(pi y) with f and g taken from it, Nitsche gamma = 40, on meshes of 10, 20, 40, 80 and 160 squares per side. The measured L2 slopes are 1.93 (no stabilisation), 2.02 (ghost penalty) and 1.95 (aggregation); the H1 slopes are 0.99, 1.00 and 1.00. The same as on a fitted mesh. So the geometry is no longer paid for in accuracy. The stabilisation changes the conditioning (previous block) but not the rates. Computed with minicut (tools/lecture_figures.py); students reproduce it in the notebook.")
wr("convergence", s)

# ------------------------------------------------------------------ Example 2: image
s = rd("img2ls-1")
s = title(s, "Example 1 · From an image to a level set", "Example 2 · From an image to a level set")
s = img(s, "8850b31ecf6a94ea5c5c2de4a6f4f6c7", A["img_four"])
s = sub(s, 'alt="Four panels: a noisy greyscale image of a porous material, the segmented binary image, the signed distance function with its zero contour, and the zero level set drawn on a triangular background mesh with the cut cells in orange"',
        'alt="Four panels: a noisy greyscale image of a porous specimen, light matrix with dark pores, the segmented binary image, the signed distance function with its zero contour, and the zero level set drawn on a triangular background mesh with the cut cells in orange"')
s = sub(s, "threshold (or a classifier): material or void", "threshold (or a classifier): solid matrix or pore")
s = sub(s, "Synthetic scan made with minicut for this lecture (filtered noise, thresholded, scanner noise added); the same steps apply to a real scan.",
        "Synthetic scan made with minicut for this lecture (a disc of solid matrix, pores from thresholded filtered noise, scanner noise added); the same steps apply to a real scan. We solve in the matrix (blue), the pores are empty.")
s = sub(s, "(here a synthetic micro-CT-like slice made with mc.synthetic_scan: filtered random noise, thresholded, with added scanner noise; with a real scan the steps are identical)",
        "(here a synthetic micro-CT-like slice of a porous specimen made with mc.synthetic_scan: a light disc of solid matrix with dark pores, with added scanner noise; with a real scan the steps are identical)")
s = sub(s, "gives a binary image: material or void.", "gives a binary image: solid matrix or pore.")
s = sub(s, "negative in the material,", "negative in the matrix,")
s = sub(s, "748 of 4050 triangles", "856 of 4050 triangles")
s = sub(s, "No mesh generator was used.", "No mesh generator was used, and the pores are simply empty: they are outside Ω.")
wr("img2ls-1", s)

s = rd("img2ls-2")
s = title(s, "Example 1 · The recipe in code", "Example 2 · The recipe in code")
s = sub(s, "Threshold the image: B = true in the material (Ω)", "Threshold the image: B = true in the solid matrix (Ω), the pores are outside")
s = sub(s, "Same idea for CAD or STL: signed distance to the surface (CutFEMx ships an STL demo)", "Same idea for CAD or STL: signed distance to the surface")
s = sub(s, "# True = material", "# True = solid matrix")
s = sub(s, " For CAD or STL geometries the signed distance to the surface does the same job: CutFEMx has an STL distance demo (python/demo/demo_stl_distance.py, Dino.stl), which minicut does not have.",
        " For CAD or STL geometries the signed distance to the surface does the same job.")
assert "CutFEMx" not in s
wr("img2ls-2", s)

wr("ex1-solve", '''<section id="ex1-solve" data-transition="fade" style="display:flex; flex-direction:column; gap:36px; padding:96px 128px 160px; background:#ffffff">
  <h2 style="font-family:Arial, sans-serif; font-size:60px; font-weight:700; line-height:1.1; color:#00509a">Example 2 · Solve in the matrix, check</h2>
  <div style="display:flex; flex-direction:row; gap:36px; align-items:flex-start">
    <div style="width:500px; display:flex; flex-direction:column; gap:10px; flex:0 0 auto">
      <img src="/_blob/%(cells)s" alt="Background triangle mesh with the solid matrix of the porous specimen: cells inside in green, cut cells in orange, the boundary of the matrix, pores and outer edge, in orange" style="width:500px; height:500px; object-fit:contain; flex:0 0 auto">
      <p style="width:500px; font-family:Arial, sans-serif; font-size:24px; line-height:1.3; color:#6e6e6e">Cells of the 40 × 40 background mesh: green inside the matrix, orange cut; the pores are empty</p>
    </div>
    <div style="width:500px; display:flex; flex-direction:column; gap:10px; flex:0 0 auto">
      <img src="/_blob/%(solution)s" alt="Computed solution in the solid matrix of the porous specimen; the pores are holes" style="width:500px; height:500px; object-fit:contain; flex:0 0 auto">
      <p style="width:500px; font-family:Arial, sans-serif; font-size:24px; line-height:1.3; color:#6e6e6e">u<sub>h</sub> in the matrix; the black line is Γ, around every pore and along the specimen edge</p>
    </div>
    <div style="width:592px; display:flex; flex-direction:column; gap:22px; flex:0 0 auto">
      <div style="background:#eaf1f8; border-radius:16px; padding:22px 28px; display:flex; flex-direction:column; gap:10px">
        <p style="font-family:Arial, sans-serif; font-size:30px; font-weight:700; color:#00509a">Check against a known solution</p>
        <p style="font-family:Arial, sans-serif; font-size:26px; line-height:1.35; color:#3b3b3b">u = sin 2πx · sin 2πy, f = −Δu, u = g on Γ</p>
        <table style="font-family:Arial, sans-serif; font-size:26px; color:#3b3b3b; width:100%%">
          <tr><th style="color:#00509a">n</th><th style="color:#00509a">cut cells</th><th style="color:#00509a">‖u − u<sub>h</sub>‖<sub>L²</sub></th><th style="color:#00509a">rate</th></tr>
          <tr><td>20</td><td>358</td><td>4.54·10<sup>-3</sup></td><td>–</td></tr><tr><td>40</td><td>768</td><td>1.27·10<sup>-3</sup></td><td>1.84</td></tr><tr><td>80</td><td>1556</td><td>3.41·10<sup>-4</sup></td><td>1.90</td></tr>
        </table>
        <p style="font-family:Arial, sans-serif; font-size:24px; line-height:1.3; color:#6e6e6e">Rate approaching two as the mesh resolves the pores</p>
      </div>
      <div style="background:#fdebd8; border-radius:16px; padding:22px 28px; display:flex; flex-direction:column; gap:8px">
        <p style="font-family:Arial, sans-serif; font-size:30px; font-weight:700; color:#b34f00">Why the ghost penalty</p>
        <p style="font-family:Arial, sans-serif; font-size:26px; line-height:1.35; color:#3b3b3b">Condition number at n = 40: 5.6·10<sup>7</sup> without it, with 16 negative eigenvalues; 331 with it.</p>
      </div>
    </div>
  </div>
  <p style="position:absolute; top:992px; left:480px; width:960px; font-family:Arial, sans-serif; font-size:24px; text-align:center; color:#6e6e6e">Cut finite element methods · MINES Paris – PSL</p>
  <p style="position:absolute; top:992px; right:128px; width:120px; font-family:Arial, sans-serif; font-size:24px; text-align:right; color:#6e6e6e">0</p>
  <aside>Three minutes. Same level set as the previous slides (the synthetic scan thresholded at 0.5), now taken all the way to a solution with minicut (P1, Nitsche with γ = 40, ghost penalty with γg = 0.1). The domain is the solid matrix: a disc of material with the pores cut out, so Γ is the outer edge and the boundary of every pore, and the pores are empty. Left: the classification of the 40 by 40 mesh, 768 cut cells. Middle: the solution of a manufactured problem, u = sin(2πx) sin(2πy) imposed on every boundary, pores included; a few small isolated pieces of matrix are separate components, which is fine for a Dirichlet problem. Right: the check. Error ratios 1.84 from n = 20 to 40 and 1.90 from 40 to 80: the rate approaches two as the mesh resolves the thin features and the pores (at n = 20 several features are thinner than a cell). No mesh was built for this geometry. The orange box is the link to the previous section: without the ghost penalty the condition number at n = 40 is 6·10⁷ and the matrix is indefinite (16 negative eigenvalues); with it, 331. Honest remark if asked: the error without ghost penalty is not larger (1.1e-3 against 1.3e-3 here); the ghost penalty repairs the matrix, not the accuracy. Variants: insulated pores need no boundary term at all (Neumann is natural), and pores filled with a second material make an interface problem. Numbers: tools/image_example.py.</aside>
</section>
''' % A)

# ------------------------------------------------------------------ Example 3: rotor
for name, old in [("csg", "Example 2 · Combining shapes with min and max"), ("ex2-build", "Example 2 · Build a rotor from simple shapes"),
                  ("ex2-turn", "Example 2 · Turn it: same mesh, new cut"), ("ex2-opt", "Example 2 · A simple shape optimisation"),
                  ("mot-designs", "Example 2 · The same loop for a wing")]:
    s = rd(name)
    s = title(s, old, old.replace("Example 2", "Example 3"))
    wr(name, s)

# ------------------------------------------------------------------ close
s = rd("questions")
s = sub(s, "Software: CutFEMx and CutCells, built on FEniCSx", "Lecture code: minicut and the notebook (cutfem-lecture)")
wr("questions", s)

# ------------------------------------------------------------------ plan
rows = [
    ("0–8", "Opening", "Why cut, and the three examples"),
    ("8–17", "Example 1 · Steps 1–2", "Level set and cell classification: describing Ω without a mesh"),
    ("17–26", "Example 1 · Step 3", "Integration on cut cells"),
    ("26–36", "Example 1 · Step 4", "Boundary conditions: Lagrange multipliers or Nitsche"),
    ("36–51", "Example 1 · Step 5", "Small cuts degrade the matrix; what repairs it?"),
    ("51–55", "Example 1 · Step 6", "Solve, look, and convergence"),
    ("55–67", "Example 2 · image", "From a scan to a level set, solved in the solid matrix"),
    ("67–80", "Example 3 · rotor", "A rotor from level sets, turned through a hot jet, tuned"),
    ("80–90", "Close", "Try it, applications, key ideas, questions"),
]
s = rd("plan")
tab = "".join(f"\n    <tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
s = re.sub(r'(<th style="width:52%; color:#00509a">Question we answer</th></tr>).*?(\n  </table>)', lambda m: m.group(1) + tab + m.group(2), s, flags=re.S)
s = notes(s, "One minute. The story of the lecture: three examples, and one long one first. Why cut, the idea, and the three examples (8 minutes). Then Example 1, Poisson on a flower, built step by step, each step explained and then written in code with minicut: level set and classification, quadrature, Nitsche, the conditioning problem and its two remedies, solve and convergence. Then the same steps run on an image of a porous specimen (solved in the solid matrix) and on a rotor built from level sets, turned through a hot jet and tuned. Say that this lecture builds on the week: weak form and Galerkin (lecture 1), meshes, P1 and assembly (lecture 2), convergence and cost (lecture 3). Timings are estimates for 90 minutes; the conditioning step can be shortened by skipping the mode slide. Announce the two short exercises.")
s = s.replace("font-size:32px; line-height:1.7", "font-size:30px; line-height:1.5").replace("gap:40px", "gap:28px")
wr("plan", s)

# ------------------------------------------------------------------ deck order, sections, footers
order = ["cover", "plan", "meshed-vs-levelset", "recap", "mot-images", "three-examples", "idea",
         "nutshell", "first-cut", "levelset", "ps-1", "classify", "activemesh", "ex-classify", "ps-2",
         "quad-problem", "cut-cell", "quad-rules", "ex-cutcell", "ps-3",
         "bc-options", "lag-1", "lag-2", "nitsche-derive", "nitsche-code", "bc-compare", "ps-4",
         "cond-what", "small-cuts", "cond-setup", "cond-sweep", "cond-modes",
         "ghost-1d", "ghost", "aggregation", "cond-cost", "ps-stab", "ps-5", "convergence",
         "img2ls-1", "img2ls-2", "ex1-solve",
         "csg", "ex2-build", "ex2-turn", "ex2-opt", "mot-designs",
         "try-it", "applications", "limits", "keyideas", "questions", "references"]
for gone in ("cond-peak", "remedy"):
    p = SL / f"{gone}.html"
    if p.exists():
        p.unlink()
for n in order:
    assert (SL / f"{n}.html").exists(), n
extra = sorted(p.stem for p in SL.glob("*.html") if p.stem not in order)
assert not extra, extra

for i, n in enumerate(order, 1):
    s = rd(n)
    s, k = re.subn(r"(text-align:\s*right;[^>]*>)\s*\d+(\s*</p>)", lambda m: f"{m.group(1)}{i}{m.group(2)}", s)
    if n not in ("cover", "questions", "references"):
        assert k == 1, (n, k)
    wr(n, s)

s = rd("keyideas")
s = re.sub(r"Close the loop with slide \d+:", f"Close the loop with slide {order.index('recap') + 1}:", s)
wr("keyideas", s)

deck = json.loads((ROOT / "deck.json").read_text())
deck["order"] = order
deck["sections"] = {
    "why": {"start": "cover", "description": "Fitted meshes become the bottleneck, so we mesh a box and cut the geometry out of it; the three examples."},
    "flower": {"start": "nutshell", "description": "Example 1: Poisson on a flower, step by step: the algorithm and the goal."},
    "geometry": {"start": "levelset", "description": "Steps 1 and 2: describe the domain with a level set and classify the cells of the background mesh."},
    "integration": {"start": "quad-problem", "description": "Step 3: integrate over the cut cells with quadrature rules on the pieces."},
    "boundary": {"start": "bc-options", "description": "Step 4: impose Dirichlet conditions on the cut boundary: Lagrange multipliers and Nitsche's method."},
    "conditioning": {"start": "cond-what", "description": "Step 5: what conditioning is and how small cuts break it."},
    "remedy": {"start": "ghost-1d", "description": "Ghost penalty and aggregation repair the conditioning; the code; solve and convergence."},
    "image": {"start": "img2ls-1", "description": "Example 2: a porous specimen from an image, solved in the solid matrix."},
    "rotor": {"start": "csg", "description": "Example 3: a rotor built from level sets with min and max, turned and tuned."},
    "close": {"start": "try-it", "description": "Try it, applications, open questions, key ideas and references."},
}
(ROOT / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False) + "\n")
print("slides:", len(order))
