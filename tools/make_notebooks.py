"""Build the lecture notebooks (student version and solutions) with nbformat.

    python make_notebooks.py

writes notebooks/cutfem_lecture.ipynb and solutions/cutfem_lecture_solutions.ipynb.
The two differ only in the exercise cells marked SOLUTION below.
"""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parent.parent


def md(text):
    return nbf.v4.new_markdown_cell(text.strip("\n"))


def code(text):
    return nbf.v4.new_code_cell(text.strip("\n"))


def build(solutions):
    def ex(student, solution):
        return code(solution if solutions else student)

    c = []

    # ------------------------------------------------------------------ intro
    c.append(md(r"""
# Cut FEM in pure Python

*MINES Paris – PSL, cut finite element methods, hands-on part*

In the lecture we meshed a **simple box** instead of a complicated geometry, described the
domain $\Omega$ by a **level set function** $\phi$, and found that only the **cut cells** need
new work. In this notebook you build every step yourself:

| Section | Lecture idea | You do |
|---|---|---|
| 0 | **Example 1: Poisson on a flower in six steps** | run the lecture code on the flower |
| 1 | background mesh, level set | look at $\phi$ |
| 2 | classify cells, active mesh | count inside / cut / outside |
| 3 | from an image to a level set (Example 2) | cut a (synthetic) scan, solve in the solid matrix |
| 4 | sub-triangulation and quadrature | check that area and perimeter converge |
| 5 | Dirichlet condition with Nitsche | **write the Nitsche terms** |
| 6 | convergence | measure the rates |
| 7 | what goes wrong: small cuts | sweep a circle, watch $\kappa$ explode |
| 8 | the remedy: ghost penalty | switch it on, see $\kappa$ stay flat |
| 9 | play | star, image, moving domain |
| 10 | Examples 2 and 3 of the lecture | image data; a rotor built, turned through a hot jet and tuned |

Everything runs with **numpy, scipy and matplotlib** only, so it works on any laptop, in Colab
and in the browser. The code lives in `minicut.py` at the root of the repository (about 500 lines,
well commented): when you want to know what a function does, `print(inspect.getsource(mc.nitsche))`.
It reproduces the CutFEMx results of the lecture: on the same mesh the errors agree with CutFEMx
to about 5 digits and the condition numbers to 12 digits.

**Problem.** $-\Delta u = f$ in $\Omega$, $u = g$ on $\Gamma = \partial\Omega$, with P1 elements.
"""))
    c.append(code(r"""
import inspect, os, sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))   # the repository root holds minicut.py
try:
    import minicut as mc
except ImportError:  # e.g. Colab: only the notebook was uploaded, fetch the module
    import urllib.request
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/sclaus2/cutfem-lecture/main/minicut.py", "minicut.py")
    import minicut as mc

plt.rcParams["figure.dpi"] = 100
"""))

    # ------------------------------------------------------------------ 0
    c.append(md(r"""
## 0. Example 1: Poisson on a flower in six steps

First the whole method in one go, with exactly the code of the lecture slides: the six-petal flower in the
box $[-1,1]^2$, $-\Delta u = 1$ in $\Omega$, $u = 0$ on $\Gamma$. Run each cell and look at the figure under it.
The sections that follow take the steps apart one by one.

**Step 1: mesh and level set.**
"""))
    c.append(code(r"""
mesh = mc.Mesh(18, box=(-1, -1, 1, 1))

def level_set(x, y):  # flower, 6 petals
    r = 0.48 * (1 + 0.18 * np.cos(6 * np.arctan2(y, x)))
    return np.sqrt(x**2 + y**2) - r

phi = level_set(mesh.nodes[:, 0], mesh.nodes[:, 1])
# phi: its values at the nodes (a P1 function)

mc.plot_levelset(mesh, phi); plt.show()
"""))
    c.append(md(r"""
**Step 2: cut and classify.** One call cuts the mesh; `cell_type` says INSIDE, CUT or OUTSIDE for every cell.
"""))
    c.append(code(r"""
geom = mc.CutGeometry(mesh, phi, order=2)

t = geom.cell_type
inside_cells = np.where(t == mc.INSIDE)[0]
cut_cells = np.where(t == mc.CUT)[0]
active_cells = geom.active_cells

print(geom.summary())
mc.plot_cells(geom); plt.show()
"""))
    c.append(md(r"""
**Step 3: quadrature rules** on $T\cap\Omega$ and $\Gamma\cap T$, and the facets for the ghost penalty.
"""))
    c.append(code(r"""
vol = geom.volume
intf = geom.interface

# vol:  points, weights on T ∩ Ω
# intf: points, weights, normals on Γ ∩ T

print(vol.points.shape, intf.points.shape)   # (606, 2) (246, 2)

# facets of the cut cells, for step 4
ghost_facets = geom.ghost_facets

fig, ax = plt.subplots(1, 2, figsize=(11, 5.5))
mc.plot_cells(geom, ax[0], quadrature="volume");    ax[0].set_title("volume points")
mc.plot_cells(geom, ax[1], quadrature="interface"); ax[1].set_title("interface points")
plt.show()
"""))
    c.append(md(r"""
**Step 4: the variational form**, one function per term:

$$a(u,v)=\int_\Omega\nabla u\cdot\nabla v\,dx\;-\int_\Gamma(\partial_n u\,v+u\,\partial_n v)\,ds+\frac{\gamma}{h}\int_\Gamma uv\,ds\;+\;\gamma_g\,h\sum_F\int_F[\partial_n u][\partial_n v]\,ds .$$
"""))
    c.append(code(r"""
f = lambda x, y: np.ones_like(x)    # f = 1
g = lambda x, y: np.zeros_like(x)   # g = 0

A = mc.stiffness(geom)                   # ∫Ω ∇u·∇v dx
An, bn = mc.nitsche(geom, g, gamma=40.0) # Nitsche on Γ

A = A + An
b = mc.load(geom, f) + bn   # ∫Ω f v dx and Nitsche
"""))
    c.append(md(r"""
**Step 5: small cuts and the repair.** A cut cell with a tiny piece of $\Omega$ makes the matrix ill-conditioned
(section 7 measures it). Two repairs: the **ghost penalty** adds a term on the facets of cut cells, **aggregation**
removes the unstable degrees of freedom. Compare the condition numbers on this mesh:
"""))
    c.append(code(r"""
Ag = mc.ghost_penalty(geom, gamma_g=0.1)

# condition_number: (kappa, negative eigenvalues)
print("none       ", mc.condition_number(geom, A))
print("ghost      ", mc.condition_number(geom, A + Ag))

agg = mc.aggregate(geom, 0.25)
print("aggregation", mc.condition_number(geom, A, agg), agg.summary())

A = A + Ag     # we continue with the ghost penalty
mc.plot_cells(geom, ghost=True); plt.title("ghost facets in red"); plt.show()
"""))
    c.append(md(r"""
**Step 6: solve and look.** Degrees of freedom outside the active mesh have empty rows; `solve` leaves them out.
"""))
    c.append(code(r"""
u = mc.solve(geom, A, b)   # on the active dofs only

outside = np.setdiff1d(np.arange(mesh.n_nodes),
                       geom.active_dofs)
print(len(outside), "dofs left out")

mc.plot_solution(geom, u); plt.show()   # u_h on Ω_h itself

print("area", mc.area(geom), "(exact", np.pi * (0.48**2 + 0.5 * (0.48 * 0.18)**2), ")")
"""))
    c.append(md(r"""
**Try it.** Change the number of petals or the mesh (`mc.Mesh(36, ...)`), set $\gamma_g = 0$, or use a different
right-hand side $f$ and watch the solution change.
"""))

    # ------------------------------------------------------------------ 1
    c.append(md(r"""
## 1. Background mesh and level set

A **background mesh** is a plain structured triangle mesh of a box that contains the geometry. The
domain is *not* meshed. It is described by a function $\phi(x,y)$ with

$$\phi<0 \text{ in } \Omega,\qquad \phi=0 \text{ on } \Gamma,\qquad \phi>0 \text{ outside}.$$

We store $\phi$ as a P1 function: its values at the mesh vertices. For a disk of radius $r$ the signed
distance $\phi(x,y)=\sqrt{(x-x_c)^2+(y-y_c)^2}-r$ is a good choice.
"""))
    c.append(code(r"""
mesh = mc.Mesh(20)                        # 20 x 20 squares, each split into two triangles, box [0,1]^2
phi = mc.circle(c=(0.5, 0.5), r=0.3)      # a function phi(x, y)

print(mesh.n_nodes, "vertices,", mesh.n_cells, "triangles")
print("phi at the centre of the disk :", phi(0.5, 0.5))
print("phi at the corner (0, 0)      :", phi(0.0, 0.0))

mc.plot_levelset(mesh, phi)
plt.title("level set function: negative inside, zero on Gamma (black)")
plt.show()
"""))
    c.append(md(r"""
**Try it.** Change the centre and the radius. Then try `mc.ellipse(...)`, `mc.star(...)` and the
CSG operations `mc.union(a, b)`, `mc.intersection(a, b)`, `mc.difference(a, b)` that you saw
in the lecture (`union` is the minimum of the two level sets, `intersection` the maximum).
"""))
    c.append(code(r"""
# Try it: a disk with a smaller disk removed (a ring), made with CSG
ring = mc.difference(mc.circle((0.5, 0.5), 0.35), mc.circle((0.5, 0.5), 0.15))
mc.plot_levelset(mesh, ring)
plt.show()
"""))

    # ------------------------------------------------------------------ 2
    c.append(md(r"""
## 2. Cut the mesh: classify the cells

`CutGeometry` does the cut. First it classifies every cell by the signs of $\phi$ at its three vertices:

* **inside**: $\phi<0$ at all vertices (green),
* **outside**: $\phi>0$ at all vertices (grey),
* **cut**: the signs differ, so $\Gamma$ passes through the cell (orange).

The **active mesh** consists of the inside and the cut cells. Degrees of freedom are only created for
vertices of active cells: the outside part of the box costs nothing.
"""))
    c.append(code(r"""
geom = mc.CutGeometry(mesh, phi)
print(geom.summary())

fig, ax = plt.subplots(1, 2, figsize=(11, 5.5))
mc.plot_cells(geom, ax[0]); ax[0].set_title("classified cells and interface")
mc.plot_cells(geom, ax[1], zoom=(0.45, 0.85, 0.35, 0.75), subtriangulation=True)
ax[1].set_title("zoom, with the sub-triangulation of the cut cells")
plt.show()
"""))
    c.append(md(r"""
**Questions.**
1. How many cells are cut? Does that number grow like $1/h$ or like $1/h^2$ when you refine the mesh? (try `mc.Mesh(40)`)
2. What fraction of all degrees of freedom of the background mesh is active?
"""))
    c.append(code(r"""
for n in (10, 20, 40, 80):
    g = mc.CutGeometry(mc.Mesh(n), phi)
    cut = np.sum(g.cell_type == mc.CUT)
    print(f"n = {n:3d}: {cut:4d} cut cells, {len(g.active_dofs):5d} active dofs of {g.mesh.n_nodes}")
"""))

    # ------------------------------------------------------------------ 3
    c.append(md(r"""
## 3. From an image to a level set

Many geometries do not come from a formula but from an **image** (CT scan, micrograph, photo). The recipe from
the lecture:

1. threshold the image into a binary mask (material / no material),
2. compute the **signed distance** to the boundary on both sides with the Euclidean distance transform,
3. **smooth** it slightly (Gaussian filter),
4. **interpolate** it at the vertices of the background mesh.

`minicut.levelset_from_image` does steps 2–4 and returns a function $\phi(x,y)$, so it plugs in everywhere a
formula did. The image below is *synthetic* (a porous specimen), but a real scan works the same way: `mask = scan > threshold`.
"""))
    c.append(code(r"""
img = mc.synthetic_scan() > 0.5               # True = material.  Replace by: img = plt.imread("scan.png")[..., 0] > 0.5
phi_img = mc.levelset_from_image(img, smooth=1.5)

mesh_img = mc.Mesh(64)
geom_img = mc.CutGeometry(mesh_img, phi_img)
print(geom_img.summary())

fig, ax = plt.subplots(1, 3, figsize=(15, 5))
ax[0].imshow(img, cmap="gray", origin="upper"); ax[0].set_title("binary image"); ax[0].axis("off")
mc.plot_levelset(mesh_img, phi_img, ax[1]); ax[1].set_title("level set from the image")
mc.plot_cells(geom_img, ax[2]); ax[2].set_title("cut on a 64 x 64 background mesh")
plt.tight_layout(); plt.show()
"""))

    # ------------------------------------------------------------------ 4
    c.append(md(r"""
## 4. Integrals on cut cells: sub-triangulation and quadrature

For a P1 level set a cut triangle is divided **exactly** into one or two triangles that lie in $\Omega$, and
$\Gamma\cap T$ is a straight segment. We then integrate with standard Gauss rules

* on every sub-triangle: $\int_{\Omega\cap T} v\,dx$ (blue points),
* on every interface segment: $\int_{\Gamma\cap T} v\,ds$ (red points), together with the normal
  $n=\nabla\phi/|\nabla\phi|$ (red arrows), which points out of $\Omega$.

The weights already contain the area or length, so $\int_\Omega 1\,dx=\sum_q w_q$.
"""))
    c.append(code(r"""
geom = mc.CutGeometry(mc.Mesh(12), mc.circle((0.5, 0.5), 0.3))

fig, ax = plt.subplots(1, 2, figsize=(11, 5.5))
mc.plot_cells(geom, ax[0], subtriangulation=True, quadrature="volume", zoom=(0.45, 0.85, 0.3, 0.7))
ax[0].set_title("volume quadrature on Omega ∩ T")
mc.plot_cells(geom, ax[1], quadrature="interface", normals=True, zoom=(0.45, 0.85, 0.3, 0.7))
ax[1].set_title("interface quadrature and normals")
plt.show()

print("number of volume points   :", len(geom.volume))
print("number of interface points:", len(geom.interface))
"""))
    c.append(md(r"""
**Check the quadrature.** The exact values are $|\Omega|=\pi r^2$ and $|\Gamma|=2\pi r$. The error should drop by a
factor 4 when $h$ is halved (second order, the price of replacing the circle by a polygon). Fill in the rate column.
"""))
    c.append(ex(r"""
r = 0.3
print("   n   |area err|  rate   |perimeter err|  rate")
prev = None
for n in (10, 20, 40, 80, 160):
    g = mc.CutGeometry(mc.Mesh(n), mc.circle((0.5, 0.5), r))
    ea = abs(mc.area(g) - np.pi * r**2)
    ep = abs(mc.perimeter(g) - 2 * np.pi * r)
    # TODO: the rate is log2(previous error / error): compute it for area and perimeter
    ra = rp = float("nan")
    print(f"{n:4d}  {ea:10.3e} {ra:6.2f}  {ep:10.3e} {rp:6.2f}")
    prev = (ea, ep)
""", r"""
r = 0.3
print("   n   |area err|  rate   |perimeter err|  rate")
prev = None
for n in (10, 20, 40, 80, 160):
    g = mc.CutGeometry(mc.Mesh(n), mc.circle((0.5, 0.5), r))
    ea = abs(mc.area(g) - np.pi * r**2)
    ep = abs(mc.perimeter(g) - 2 * np.pi * r)
    ra = rp = float("nan") if prev is None else None
    if prev is not None:
        ra, rp = np.log2(prev[0] / ea), np.log2(prev[1] / ep)
    print(f"{n:4d}  {ea:10.3e} {ra:6.2f}  {ep:10.3e} {rp:6.2f}")
    prev = (ea, ep)
"""))
    c.append(md(r"""
**The small-cut problem starts here.** A cut cell can contain an arbitrarily small part of $\Omega$. The volume
fraction $|T\cap\Omega|/|T|$ tells you how small. Look at the distribution of volume fractions of the cut cells:
"""))
    c.append(code(r"""
g = mc.CutGeometry(mc.Mesh(40), mc.circle((0.5, 0.5), 0.3))
frac = g.volume_fraction[g.cell_type == mc.CUT]
print(f"{len(frac)} cut cells, smallest volume fraction {frac.min():.2e}, median {np.median(frac):.2f}")
plt.hist(frac, bins=30); plt.xlabel("|T ∩ Ω| / |T|"); plt.ylabel("number of cut cells"); plt.show()
"""))

    # ------------------------------------------------------------------ 5
    c.append(md(r"""
## 5. Dirichlet condition with Nitsche's method

There is no mesh vertex on $\Gamma$, so we cannot set boundary values. **Nitsche's method** adds boundary
integrals to the weak form. Find $u_h\in V_h$ such that for all $v_h\in V_h$

$$
\underbrace{\int_\Omega \nabla u_h\cdot\nabla v_h\,dx}_{\text{stiffness}}
\;\underbrace{-\int_\Gamma \partial_n u_h\,v_h\,ds}_{\text{consistency}}
\;\underbrace{-\int_\Gamma u_h\,\partial_n v_h\,ds}_{\text{symmetry}}
\;\underbrace{+\frac{\gamma}{h}\int_\Gamma u_h v_h\,ds}_{\text{penalty}}
=\int_\Omega f v_h\,dx\;\underbrace{-\int_\Gamma g\,\partial_n v_h\,ds+\frac{\gamma}{h}\int_\Gamma g\,v_h\,ds}_{\text{boundary data}}
$$

with $\gamma=40$ and $h$ the cell size. The three boundary terms of the left-hand side are what you implement.

On every interface quadrature point $x_q$ with weight $w_q$ the local matrix is indexed `[q, i, j]`, with
$i$ the test function $v$ and $j$ the trial function $u$, where the P1 basis functions of the cell are
$\lambda_0,\lambda_1,\lambda_2$:

* `lam[q, k]` $=\lambda_k(x_q)$ and `dn[q, k]` $=\partial_n\lambda_k(x_q)=\nabla\lambda_k\cdot n$,
* the consistency term is $-\sum_q w_q\,\lambda_i\,\partial_n\lambda_j$ : `-np.einsum("q,qi,qj->qij", w, lam, dn)`.

Implement the other two terms and the two right-hand side terms, then compare with `mc.nitsche`.
"""))
    c.append(ex(r"""
def my_nitsche(geom, g, gamma=40.0):
    q, m = geom.interface, geom.mesh
    lam = m.bary(q.cells, q.points)                                # (nq, 3)  basis functions at the points
    dn = np.einsum("qkd,qd->qk", m.grads[q.cells], q.normals)      # (nq, 3)  normal derivatives of the basis functions
    w = q.weights                                                  # weights (contain the segment length)
    pen = gamma / m.h[q.cells]                                     # gamma / h of the cell of every point
    gx = g(q.points[:, 0], q.points[:, 1])                         # boundary data at the points

    local = np.zeros((len(w), 3, 3))
    local += -np.einsum("q,qi,qj->qij", w, lam, dn)                # consistency   - ∫ (∂n u) v
    # TODO: symmetry   - ∫ u (∂n v)
    # TODO: penalty    + gamma/h ∫ u v

    local_b = np.zeros((len(w), 3))
    # TODO: boundary data   - ∫ g ∂n v
    # TODO: boundary data   + gamma/h ∫ g v
    return mc.assemble_matrix(m, q.cells, local), mc.assemble_vector(m, q.cells, local_b)
""", r"""
def my_nitsche(geom, g, gamma=40.0):
    q, m = geom.interface, geom.mesh
    lam = m.bary(q.cells, q.points)                                # (nq, 3)  basis functions at the points
    dn = np.einsum("qkd,qd->qk", m.grads[q.cells], q.normals)      # (nq, 3)  normal derivatives of the basis functions
    w = q.weights                                                  # weights (contain the segment length)
    pen = gamma / m.h[q.cells]                                     # gamma / h of the cell of every point
    gx = g(q.points[:, 0], q.points[:, 1])                         # boundary data at the points

    local = np.zeros((len(w), 3, 3))
    local += -np.einsum("q,qi,qj->qij", w, lam, dn)                # consistency   - ∫ (∂n u) v
    local += -np.einsum("q,qi,qj->qij", w, dn, lam)                # symmetry      - ∫ u (∂n v)
    local += np.einsum("q,qi,qj->qij", w * pen, lam, lam)          # penalty       + gamma/h ∫ u v

    local_b = np.zeros((len(w), 3))
    local_b += -(w * gx)[:, None] * dn                             # - ∫ g ∂n v
    local_b += (w * pen * gx)[:, None] * lam                       # + gamma/h ∫ g v
    return mc.assemble_matrix(m, q.cells, local), mc.assemble_vector(m, q.cells, local_b)
"""))
    c.append(code(r"""
# Check your implementation against the reference (the test problem below has u = sin(pi x) sinh(y))
u_exact = lambda x, y: np.sin(np.pi * x) * np.sinh(y)
f = lambda x, y: (np.pi**2 - 1) * np.sin(np.pi * x) * np.sinh(y)           # f = -Δ u_exact
grad_exact = lambda x, y: (np.pi * np.cos(np.pi * x) * np.sinh(y), np.sin(np.pi * x) * np.cosh(y))

geom = mc.CutGeometry(mc.Mesh(20), mc.circle((0.5, 0.5), 0.33))
try:
    A_mine, b_mine = my_nitsche(geom, u_exact)
    A_ref, b_ref = mc.nitsche(geom, u_exact)
    dA, db = abs(A_mine - A_ref).max(), np.abs(b_mine - b_ref).max()
    print("max difference matrix:", dA, "  vector:", db)
    print("OK, your Nitsche terms are correct" if max(dA, db) < 1e-12 else "Not yet: check the signs and the factors")
except Exception as e:
    print("Not finished yet:", type(e).__name__, e)
"""))
    c.append(md(r"""
**Solve.** Now assemble stiffness + Nitsche (use `mc.nitsche` if you did not finish yours), the load vector, and solve on the active dofs.
For the moment we **do not** use the ghost penalty (`ghost=False`).
"""))
    c.append(code(r"""
geom = mc.CutGeometry(mc.Mesh(20), mc.circle((0.5, 0.5), 0.33))

A, b = mc.poisson_system(geom, f, u_exact, gamma=40.0, ghost=False)   # = stiffness + nitsche, load + boundary data
u = mc.solve(geom, A, b)

fig, ax = plt.subplots(1, 2, figsize=(11, 5))
mc.plot_solution(geom, u, ax[0]); ax[0].set_title("u_h on Omega_h (only the sub-triangulation is drawn)")
uh_at = lambda g, u: mc.evaluate(g, u, g.volume.cells, g.volume.points)
q = geom.volume
sc = ax[1].scatter(q.points[:, 0], q.points[:, 1], c=uh_at(geom, u) - u_exact(q.points[:, 0], q.points[:, 1]), s=6, cmap="RdBu")
ax[1].set_aspect("equal"); plt.colorbar(sc, ax=ax[1]); ax[1].set_title("error u_h - u at quadrature points")
plt.show()
print("L2 error:", mc.l2_error(geom, u, u_exact))
"""))

    # ------------------------------------------------------------------ 6
    c.append(md(r"""
## 6. Is it a proper finite element method? Convergence

For P1 elements we expect $\|u-u_h\|_{L^2}=O(h^2)$ and $\|\nabla(u-u_h)\|_{L^2}=O(h)$, exactly as on a body-fitted
mesh ("It is still the Galerkin method" from the lecture). The domain is **never meshed**, only the box is.
"""))
    c.append(code(r"""
ns = [10, 20, 40, 80, 160]
e0, e1 = [], []
for n in ns:
    g = mc.CutGeometry(mc.Mesh(n), mc.circle((0.5, 0.5), 0.33))
    A, b = mc.poisson_system(g, f, u_exact, ghost=True)          # with ghost penalty, see section 8
    u = mc.solve(g, A, b)
    e0.append(mc.l2_error(g, u, u_exact)); e1.append(mc.h1_error(g, u, grad_exact))

h = 1.0 / np.array(ns)
plt.loglog(h, e0, "o-", label="L2 error")
plt.loglog(h, e1, "s-", label="H1 seminorm error")
plt.loglog(h, e0[0] * (h / h[0]) ** 2, "k--", lw=0.8, label="h²")
plt.loglog(h, e1[0] * (h / h[0]), "k:", lw=0.8, label="h")
plt.xlabel("h"); plt.ylabel("error"); plt.legend(); plt.grid(True, which="both", alpha=0.3)
plt.show()
print("L2 rates:", np.round(np.log2(np.array(e0[:-1]) / np.array(e0[1:])), 2))
print("H1 rates:", np.round(np.log2(np.array(e1[:-1]) / np.array(e1[1:])), 2))
"""))

    # ------------------------------------------------------------------ 7
    c.append(md(r"""
## 7. What goes wrong: small cuts and the condition number

Now we apply the cut integration **naively**, without any stabilisation. We keep the mesh and the problem fixed and
let the circle's radius grow by exactly one cell width. The mesh does not change, only the way the circle cuts it,
and the cut fractions of the cells change continuously with the radius.

For each radius we compute the condition number $\kappa(A)=|\lambda|_{\max}/|\lambda|_{\min}$ of the system matrix,
the smallest volume fraction among the cut cells, and the number of **negative eigenvalues**. The matrix should be
positive definite; negative eigenvalues mean that the discrete problem has lost its coercivity.
"""))
    c.append(code(r"""
n = 20
mesh = mc.Mesh(n)
radii = np.linspace(0.30, 0.30 + 1.0 / n, 120)

def sweep(ghost):
    kappa, neg, small = [], [], []
    for r in radii:
        g = mc.CutGeometry(mesh, mc.circle((0.5, 0.5), r))
        A, b = mc.poisson_system(g, f, u_exact, ghost=ghost)
        k, nneg = mc.condition_number(g, A)
        kappa.append(k); neg.append(nneg)
        small.append(g.volume_fraction[g.cell_type == mc.CUT].min())
    return np.array(kappa), np.array(neg), np.array(small)

k_naive, neg_naive, small = sweep(ghost=False)

fig, ax = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
ax[0].semilogy(radii, k_naive, "C3.-", label="no stabilisation")
bad = neg_naive > 0
ax[0].semilogy(radii[bad], k_naive[bad], "ko", mfc="none", ms=9, label="matrix indefinite")
ax[0].set_ylabel("condition number κ"); ax[0].legend(); ax[0].grid(True, which="both", alpha=0.3)
ax[1].semilogy(radii, small, "C0.-"); ax[1].set_ylabel("smallest volume fraction")
ax[1].set_xlabel("radius r"); ax[1].grid(True, which="both", alpha=0.3)
plt.show()
print(f"κ ranges from {k_naive.min():.1e} to {k_naive.max():.1e} while the mesh does not change")
"""))
    c.append(md(r"""
**Read the plot.** The spikes of $\kappa$ sit exactly where the smallest volume fraction is tiny: a cell whose cut-off
piece of $\Omega$ is tiny gives a row of the stiffness matrix of size $\approx|T\cap\Omega|$, but the vertex
it belongs to may lie almost entirely outside $\Omega$. Below, at the worst radius, the **solution** looks fine in the
$L^2$ norm, but not at the vertices that barely touch $\Omega$:
"""))
    c.append(code(r"""
r_worst = radii[np.argmax(k_naive)]
g = mc.CutGeometry(mesh, mc.circle((0.5, 0.5), r_worst))
d, X = g.active_dofs, g.mesh.nodes

for ghost in (False, True):
    A, b = mc.poisson_system(g, f, u_exact, ghost=ghost)
    u = mc.solve(g, A, b)
    nodal = np.abs(u[d] - u_exact(X[d, 0], X[d, 1])).max()
    print(f"ghost penalty {str(ghost):5s}:  κ = {mc.condition_number(g, A)[0]:9.2e}   "
          f"L2 error on Omega = {mc.l2_error(g, u, u_exact):.2e}   max nodal error = {nodal:.2e}")
"""))
    c.append(md(r"""
**Question.** The $L^2$ error on $\Omega$ is almost unchanged, while the largest error at a vertex is huge. Why does
the error integral hardly notice? *(Hint: where is that vertex, and how much of $\Omega$ does its basis function see?)*
"""))

    # ------------------------------------------------------------------ 8
    c.append(md(r"""
## 8. The remedy: ghost penalty

The ghost penalty adds a term on the **interior facets of the cut cells** (the red facets below), penalising the jump
of the normal derivative:

$$ g_h(u,v)=\gamma_g\,h\sum_{F\in\mathcal F_G}\int_F [\![\partial_n u]\!]\,[\![\partial_n v]\!]\,ds ,\qquad \gamma_g=0.1 .$$

For P1 elements the gradient is constant per cell, so this is a closed-form rank-one update per facet (read it with
`print(inspect.getsource(mc.ghost_penalty))`). It couples the vertices of a small cut cell to those of its neighbours, so a cell
with almost no $\Omega$ in it can no longer carry a free, nearly invisible degree of freedom.
"""))
    c.append(code(r"""
geom = mc.CutGeometry(mc.Mesh(20), mc.circle((0.5, 0.5), 0.33))
mc.plot_cells(geom, ghost=True)
plt.title(f"ghost facets (red): {len(geom.ghost_facets)} interior facets of cut cells"); plt.show()
"""))
    c.append(code(r"""
k_ghost, neg_ghost, _ = sweep(ghost=True)

plt.figure(figsize=(9, 4.5))
plt.semilogy(radii, k_naive, "C3.-", label="no stabilisation")
plt.semilogy(radii, k_ghost, "C2.-", label="ghost penalty  γ_g = 0.1")
plt.xlabel("radius r"); plt.ylabel("condition number κ"); plt.legend(); plt.grid(True, which="both", alpha=0.3)
plt.show()
print(f"naive : κ in [{k_naive.min():.1e}, {k_naive.max():.1e}],  {np.sum(neg_naive > 0)} of {len(radii)} radii indefinite")
print(f"ghost : κ in [{k_ghost.min():.1e}, {k_ghost.max():.1e}],  {np.sum(neg_ghost > 0)} of {len(radii)} radii indefinite")
"""))
    c.append(md(r"""
**What the ghost penalty does and does not change.** The condition number no longer depends on how the domain cuts the mesh,
and the solution stays accurate. Check by how much the stabilisation changes the *accuracy* for a well-cut geometry, and how the
parameter $\gamma_g$ matters. Run the cell and answer: **what happens for very small and for very large $\gamma_g$?**
"""))
    c.append(code(r"""
g = mc.CutGeometry(mc.Mesh(20), mc.circle((0.5, 0.5), r_worst))
print("  gamma_g        κ        L2 error   max nodal error")
for gg in [0.0, 1e-4, 1e-2, 1e-1, 1.0, 1e2, 1e4]:
    A, b = mc.poisson_system(g, f, u_exact, gamma_g=gg, ghost=gg > 0)
    u = mc.solve(g, A, b)
    k = mc.condition_number(g, A)[0]
    nodal = np.abs(u[g.active_dofs] - u_exact(*g.mesh.nodes[g.active_dofs].T)).max()
    print(f"{gg:9.0e}  {k:10.2e}  {mc.l2_error(g, u, u_exact):10.2e}  {nodal:10.2e}")
"""))
    c.append(md(r"""
**Aggregation** (the second remedy of the lecture) attaches every ill-posed cut cell (volume fraction below a threshold, 0.25 here) to a
well-cut root cell and removes the degrees of freedom that only the ill cells see: on an aggregate the function is the polynomial of the root cell.
In matrix form the unknowns are reduced, $u = E\,u_{\rm red}$, and the system is $E^T A E$. `mc.aggregate` builds the aggregates and `mc.solve_aggregated` solves the reduced system.
Nothing is added to the form, and the system has fewer unknowns. Here it is next to the ghost penalty on the worst radius of the sweep:
"""))
    c.append(code(r"""
g = mc.CutGeometry(mc.Mesh(20), mc.circle((0.5, 0.5), r_worst))
agg = mc.aggregate(g, 0.25)
print(agg.summary())
A0, b0 = mc.poisson_system(g, f, u_exact, ghost=False)
A1, b1 = mc.poisson_system(g, f, u_exact, ghost=True)
for name, A_, b_, a_ in [("none", A0, b0, None), ("ghost penalty", A1, b1, None), ("aggregation", A0, b0, agg)]:
    u = mc.solve(g, A_, b_) if a_ is None else mc.solve_aggregated(g, A_, b_, a_)
    k, neg = mc.condition_number(g, A_, a_)
    print(f"{name:14s} kappa = {k:9.2e}  negative eigenvalues: {neg}  L2 error = {mc.l2_error(g, u, u_exact):.2e}  "
          f"GMRES iterations: {mc.gmres_iterations(g, A_, b_, agg=a_)}")
"""))

    # ------------------------------------------------------------------ 9
    c.append(md(r"""
## 9. Play

Everything composes. Some ideas, from easy to open-ended.
"""))
    c.append(md(r"""
**9a. A flower.** Solve $-\Delta u=1$ with $u=0$ on a star-shaped domain. No formula for $u$ is needed.
"""))
    c.append(code(r"""
f1 = lambda x, y: np.ones_like(x)
zero = lambda x, y: np.zeros_like(x)

geom = mc.CutGeometry(mc.Mesh(80), mc.star(r0=0.28, amp=0.09, k=6))
A, b = mc.poisson_system(geom, f1, zero)
u = mc.solve(geom, A, b)
mc.plot_solution(geom, u); plt.title("-Δu = 1, u = 0 on a flower"); plt.show()
print(geom.summary(), "  κ =", f"{mc.condition_number(geom, A)[0]:.1e}")
"""))
    c.append(md(r"""
**9b. A porous solid from an image.** The synthetic scan from section 3: $-\Delta u = 1$ in the solid matrix, $u=0$ on all its
boundaries (the outer edge and every pore, which stays empty). The interface is one level set, with its inner and outer boundaries.
Compare the unstabilised solution with the stabilised one.
"""))
    c.append(code(r"""
geom = mc.CutGeometry(mc.Mesh(80), phi_img)
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
for a, ghost in zip(ax, (False, True)):
    A, b = mc.poisson_system(geom, f1, zero, ghost=ghost)
    u = mc.solve(geom, A, b)
    mc.plot_solution(geom, u, a)
    a.set_title(f"ghost penalty {'on' if ghost else 'off'}:  u in [{np.nanmin(u):.4f}, {np.nanmax(u):.4f}],  κ = {mc.condition_number(geom, A)[0]:.0e}")
plt.tight_layout(); plt.show()
"""))
    c.append(md(r"""
**9c. A moving domain.** Move the disk across the **same** mesh. Without stabilisation the condition number jumps by orders of
magnitude from one position to the next. With the ghost penalty it stays flat. This is why a moving or optimised geometry needs a robust method.
"""))
    c.append(code(r"""
mesh = mc.Mesh(24)
xs = np.linspace(0.40, 0.40 + 1.0 / 24, 60)          # move the centre by one cell width
kn, kg = [], []
for x0 in xs:
    g = mc.CutGeometry(mesh, mc.circle((x0, 0.5), 0.27))
    kn.append(mc.condition_number(g, mc.poisson_system(g, f1, zero, ghost=False)[0])[0])
    kg.append(mc.condition_number(g, mc.poisson_system(g, f1, zero, ghost=True)[0])[0])
plt.semilogy(xs, kn, "C3.-", label="no stabilisation"); plt.semilogy(xs, kg, "C2.-", label="ghost penalty")
plt.xlabel("x position of the centre"); plt.ylabel("κ"); plt.legend(); plt.grid(True, which="both", alpha=0.3); plt.show()
"""))
    c.append(md(r"""
**9d. Open questions.**
* How does the result change with the Nitsche parameter $\gamma$ (try 1, 10, 40, 1000)? What happens to the error and to $\kappa$ if $\gamma$ is too small?
* Replace $g=0$ by a non-zero boundary value that varies along $\Gamma$ and check that the boundary condition is satisfied (plot $u_h$ on the interface points).
* Use `mc.union` of two overlapping disks and watch the cut cells appear and merge as you move them.
* Take your own picture: threshold it, call `levelset_from_image`, and solve something on it.
"""))

    # ------------------------------------------------------------------ 10
    c.append(md(r"""
## 10. The two examples of the lecture

The lecture built two examples on one 2D code, in steps: describe the geometry with a level set, cut the background
mesh, solve and check. Here they are, so you can reproduce every figure and every number and then change them.

| Example | Geometry | What it shows |
|---|---|---|
| 10a | a porous solid from an image | no mesh generator: pixels, distance, level set |
| 10b | a five-bladed rotor, built with `min`, turned through a hot-gas jet, and tuned | CSG with level sets; a moving shape on one mesh; a shape optimisation loop |

10a uses the manufactured solution $u=\sin 2\pi x\,\sin 2\pi y$ (so $f=8\pi^2 u$ and $g=u$ on $\Gamma$), Nitsche with
$\gamma=40$ and the ghost penalty with $\gamma_g=0.1$. The helper `report` prints the $L^2$ error on $20^2$, $40^2$
and $80^2$ meshes with the observed rates, and the condition number at $40^2$ with and without the ghost penalty.
"""))
    c.append(code(r"""
u_ex = lambda x, y: np.sin(2 * np.pi * x) * np.sin(2 * np.pi * y)
f_ex = lambda x, y: 8 * np.pi**2 * u_ex(x, y)


def solve_case(phi, n, ghost=True, kappa=False, f=f_ex, g=u_ex):
    geom = mc.CutGeometry(mc.Mesh(n), phi)
    A, b = mc.poisson_system(geom, f, g, ghost=ghost)
    u = mc.solve(geom, A, b)
    k, neg = mc.condition_number(geom, A) if kappa else (np.nan, 0)
    return geom, u, dict(n=n, cut=int((geom.cell_type == mc.CUT).sum()),
                         l2=mc.l2_error(geom, u, u_ex), kappa=k, negative=neg)


def report(phi, name):
    print(f"{name}:    n   cut cells    L2 error   rate")
    prev = None
    for n in (20, 40, 80):
        geom, u, r = solve_case(phi, n)
        rate = "" if prev is None else f"{np.log2(prev / r['l2']):.2f}"
        print(f"        {n:4d}   {r['cut']:8d}   {r['l2']:.2e}   {rate}")
        prev = r["l2"]
    k_on = solve_case(phi, 40, True, True)[2]
    k_off = solve_case(phi, 40, False, True)[2]
    print(f"condition number at n = 40: {k_off['kappa']:.1e} without the ghost penalty "
          f"({k_off['negative']} negative eigenvalues), {k_on['kappa']:.0f} with it")


def show(phi, n, title):
    geom, u, _ = solve_case(phi, n)
    fig, ax = plt.subplots(1, 2, figsize=(11, 5.2))
    mc.plot_cells(geom, ax[0]); ax[0].set_title(f"{title}: cells of the {n} x {n} mesh")
    mc.plot_solution(geom, u, ax[1]); ax[1].set_title("solution on the active cells")
    plt.tight_layout(); plt.show()
"""))
    c.append(md(r"""
### 10a. Image data: the solid matrix with empty pores

The level set `phi_img` of section 3 (pixels $\to$ signed distance $\to$ smoothed $\to$ interpolated). The error
converges at second order although no mesh was built for the pores.
"""))
    c.append(code(r"""
report(phi_img, "image")
show(phi_img, 40, "image")
"""))
    c.append(md(r"""
**Try it.** Replace `mc.synthetic_scan() > 0.5` by your own picture (`plt.imread("scan.png")[..., 0] > 0.5`) and call
`report` on the new level set. What happens when a pore is thinner than one mesh cell?
"""))
    c.append(md(r"""
### 10b. A rotor: build it, turn it, tune it

**Build.** Constructive solid geometry with the rules of the lecture: union is `min`, intersection is `max`,
difference is `max(phi_a, -phi_b)`. One blade is a tilted ellipse. The other blades are copies turned by multiples of
72°: `mc.rotate(phi, angle)` evaluates $\phi$ at the back-rotated point, $\phi(R^{-1}(x-c)+c)$, so it is the only new
ingredient. The hub is a disc added with another union.
"""))
    c.append(code(r"""
from math import pi
from scipy.optimize import brentq

def blade(b=0.055):
    return mc.ellipse((0.75, 0.5), 0.17, b, 0.35)              # one tilted blade, half-width b

def rotor(b=0.055, n_blades=5):
    hub = mc.circle((0.5, 0.5), 0.12)
    return mc.union(hub, *[mc.rotate(blade(b), 2 * pi * k / n_blades) for k in range(n_blades)])

fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
one_blade = blade()
five_blades = mc.union(*[mc.rotate(blade(), 2 * pi * k / 5) for k in range(5)])
for a, ph, name in zip(ax, (one_blade, five_blades, rotor()),
                       ("one blade", "min over five turned blades", "min with the hub: the rotor")):
    mc.plot_cells(mc.CutGeometry(mc.Mesh(40), ph), a); a.set_title(name); a.set_ylim(0.06, 0.94)
plt.tight_layout(); plt.show()
"""))
    c.append(md(r"""
**Turn it, through a hot-gas jet.** Turning the rotor is a change of $\phi$ only: `mc.rotate(rotor(), theta)`. The mesh,
the cut and the solve are the same code. To make the problem interesting the load stays where it is: a hot-gas jet
$f$ fixed in space (a Gaussian), while the rotor turns through it. At each angle we solve the steady problem
$-\Delta u = f$ in $\Omega_\theta$, $u = 0$ on $\Gamma_\theta$, where $u$ is the temperature rise above the coolant
(quasi-static: one steady solve per angle; the unit is arbitrary, $f=10^5$ at the jet centre). If the load turned with
the rotor the answer would be the same at every angle.
"""))
    c.append(code(r"""
zero = lambda x, y: np.zeros_like(x)

def jet(x, y, x0=0.5, y0=0.80, s=0.06):
    return 1e5 * np.exp(-((x - x0) ** 2 + (y - y0) ** 2) / (2 * s * s))

def temperature(b, theta, n=40, ghost=True, kappa=False):
    # solve at one angle: returns geom, u and the condition number of A (or nan)
    geom = mc.CutGeometry(mc.Mesh(n), mc.rotate(rotor(b), theta))
    A, rhs = mc.poisson_system(geom, jet, zero, ghost=ghost)
    u = mc.solve(geom, A, rhs)
    return geom, u, (mc.condition_number(geom, A)[0] if kappa else np.nan)

def peak(b, theta, n=40):
    return np.nanmax(temperature(b, theta, n)[1])

fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
for a, deg in zip(ax, (0, 15, 36)):
    g, u, _ = temperature(0.055, np.radians(deg))
    mc.plot_solution(g, u, a); a.set_title(f"theta = {deg} degrees, peak {np.nanmax(u):.0f}")
    a.add_patch(plt.Circle((0.5, 0.8), 0.12, fill=False, ls="--", color="C3")); a.set_xlim(0.04, 0.96); a.set_ylim(0.04, 0.96)
plt.tight_layout(); plt.show()
"""))
    c.append(md(r"""
Now one period (72°, the five-fold symmetry) in 24 steps: the peak temperature, and the condition number with and
without the ghost penalty (this takes about ten seconds: the condition number needs the full spectrum).
"""))
    c.append(code(r"""
angles = np.linspace(0.0, 2 * pi / 5, 25)[:-1]
T40 = np.array([peak(0.055, t, 40) for t in angles])
T80 = np.array([peak(0.055, t, 80) for t in angles])
k_on = np.array([temperature(0.055, t, 40, True, True)[2] for t in angles])
k_off = np.array([temperature(0.055, t, 40, False, True)[2] for t in angles])

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(np.degrees(angles), T40, "o-", ms=3, label="n = 40"); ax[0].plot(np.degrees(angles), T80, "o-", ms=3, label="n = 80")
ax[0].set_xlabel("angle theta [deg]"); ax[0].set_ylabel("peak temperature"); ax[0].legend(); ax[0].grid(alpha=0.3)
ax[1].semilogy(np.degrees(angles), k_off, "C3o-", ms=3, label="without ghost penalty")
ax[1].semilogy(np.degrees(angles), k_on, "C0o-", ms=3, label="with ghost penalty")
ax[1].set_xlabel("angle theta [deg]"); ax[1].set_ylabel("condition number"); ax[1].legend(); ax[1].grid(alpha=0.3)
plt.tight_layout(); plt.show()
print(f"peak temperature over a turn: {T40.min():.0f} to {T40.max():.0f} (n = 40), {T80.max():.0f} at the worst angle (n = 80)")
print(f"condition number: {k_on.min():.0f} to {k_on.max():.0f} with the ghost penalty, "
      f"{k_off.min():.0e} to {k_off.max():.0e} without")
"""))
    c.append(md(r"""
**Animation.** The whole turn as a film: the background mesh never changes, the orange cut cells follow the boundary.
"""))
    c.append(code(r"""
from matplotlib.animation import FuncAnimation
from IPython.display import HTML

fig, ax = plt.subplots(1, 2, figsize=(10, 5))
def frame(k):
    for a in ax: a.clear()
    th = 2 * pi / 5 * k / 24
    g, u, _ = temperature(0.055, th)
    mc.plot_cells(g, ax[0]); mc.plot_solution(g, u, ax[1])
    ax[0].set_title(f"theta = {np.degrees(th):.0f} deg: cut cells"); ax[1].set_title("temperature")
    for a in ax: a.add_patch(plt.Circle((0.5, 0.8), 0.12, fill=False, ls="--", color="C3")); a.set_xlim(0.04, 0.96); a.set_ylim(0.04, 0.96)
anim = FuncAnimation(fig, frame, frames=24, interval=120)
plt.close(fig)
HTML(anim.to_jshtml())      # use anim.save("rotor.gif") to keep it
"""))
    c.append(md(r"""
**Tune it.** A first shape optimisation with one design parameter, the blade half-width $b$. Wider blades are
stronger but get hotter in the jet. We want the *widest* blade whose peak temperature stays below $T^* = 150$ at every
angle of the turn. $T_\text{worst}(b)$ is the maximum over the 24 angles; it grows with $b$, so the optimum is where
$T_\text{worst}(b) = T^*$: a root-finding problem. Every evaluation is 24 new level sets, cuts of the same mesh and
solves; nothing is meshed in the loop (n = 80 takes about 20 s).
"""))
    c.append(code(r"""
T_star = 150.0
def T_worst(b, n=40):
    return max(peak(b, t, n) for t in angles)

for n in (40, 80):
    b_star = brentq(lambda b: T_worst(b, n) - T_star, 0.03, 0.12, xtol=1e-5)
    area = mc.area(mc.CutGeometry(mc.Mesh(n), rotor(b_star)))
    print(f"n = {n}:  b* = {b_star:.4f}   area = {area:.3f}")
print(f"starting design b = 0.055:  T_worst = {T_worst(0.055):.0f},  "
      f"area = {mc.area(mc.CutGeometry(mc.Mesh(40), rotor(0.055))):.3f}")

bs = np.linspace(0.03, 0.12, 19)
plt.figure(figsize=(7, 4.5))
for n in (40, 80):
    plt.plot(bs, [T_worst(b, n) for b in bs], "o-", ms=3, label=f"n = {n}")
plt.axhline(T_star, color="C3", ls="--"); plt.text(0.031, 156, "limit T*", color="C3")
plt.xlabel("blade half-width b"); plt.ylabel("worst peak temperature over a turn"); plt.legend(); plt.grid(alpha=0.3); plt.show()
"""))
    c.append(md(r"""
**Try it.**
* Add the number of blades as a second design parameter. Without the temperature limit the widest blade would always win,
  and without a requirement on strength the thinnest blade would always win: why is a *limit* the right way to pose it?
* Move the jet (`x0`, `y0`) or make it narrower. Where is the worst angle now?
* Let the load turn with the rotor (put the jet in the rotor's frame). What does the peak temperature do, and why?
* Use `mc.difference` to drill a round cooling hole in the hub with $u = 0$ on it.
"""))

    # ------------------------------------------------------------------ end
    c.append(md(r"""
## What you have built, and what comes next

| This notebook | In CutFEMx |
|---|---|
| structured P1 mesh, P1 level set | any DOLFINx mesh, P1 or P2 level set, 2D and 3D |
| `CutGeometry`: classify, clip, Gauss rules | `cutfemx.cut`, `locate_entities`, `runtime_quadrature` |
| `nitsche`, `ghost_penalty` by hand | the same terms written in UFL, assembled with `cutfemx.fem` |
| ghost penalty only | ghost penalty and cell aggregation |
| 2D Poisson, P1 | elasticity, Stokes, DG, surface PDEs, MPI-parallel runs |

The terms you wrote are *exactly* the terms in the CutFEMx demo: on the same mesh, the errors and condition numbers agree with CutFEMx to 5 and 12 digits. To go further, **install CutFEMx** and rerun the Poisson problem with
a P2 level set or on a 3D geometry (see the last slides of the lecture for the installation steps).
"""))

    nb = nbf.v4.new_notebook()
    nb["cells"] = c
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }
    return nb


if __name__ == "__main__":
    for sol, name in ((False, "notebooks/cutfem_lecture.ipynb"), (True, "solutions/cutfem_lecture_solutions.ipynb")):
        nbf.write(build(sol), ROOT / name)
        print("wrote", ROOT / name)
