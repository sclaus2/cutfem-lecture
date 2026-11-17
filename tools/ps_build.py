"""Build the slides of Example 1 that show code: steps 1 to 6 (minicut).

Usage:  python tools/ps_build.py SLIDES_DIR
The code shown is the code in tools/ps_figures.py (which runs it).
"""

import html
import sys
from pathlib import Path

SLIDES = Path(sys.argv[1])

IMG = {
    "mesh": "/_blob/d396e1f77e68b2fa5053982b7ca90771",
    "inside": "/_blob/c3136de6bae5ed7028d3d53331b45fe9",
    "cut": "/_blob/65f6b82f1040f04c0f0c22779e9e9ab2",
    "vol": "/_blob/2bb2108c9b21f61b130773de18f17bcf",
    "intf": "/_blob/309bad6182d4328a939934be61235add",
    "ghost": "/_blob/f6e39b1be9c2fe8a184ba313db3fec81",
    "dofs": "/_blob/968f86871ccfe5d25816e6337f760fe0",
    "sol": "/_blob/e56284a2c551b54a14d7beabe00bb171",
    "zoom": "/_blob/8c35da609fbe89c58bdb34dba0c8e8ce",
    "normals": "/_blob/f14d90d0895d8a7fbfd74f6d2bdb9ab9",
    "stab": "/_blob/b11767ec779097002e94991e347764d8",
}


def code(lines, size=26):
    """lines: plain strings; '#' starts a grey comment; leading spaces become padding."""
    ch = size * 0.6
    out = []
    for ln in lines:
        if not ln.strip():
            out.append(f'<p style="font-size:{size}px;line-height:1.38;font-family:\'Courier New\', monospace;color:#F3F4F6;padding-left:0px">&nbsp;</p>')
            continue
        pad = len(ln) - len(ln.lstrip(" "))
        body = ln.lstrip(" ")
        if "#" in body:
            k = body.index("#")
            main, com = body[:k], body[k:]
            txt = html.escape(main) + f'<span style="color:#9CA3AF">{html.escape(com)}</span>'
        else:
            txt = html.escape(body)
        out.append(f'<p style="font-size:{size}px;line-height:1.38;font-family:\'Courier New\', monospace;color:#F3F4F6;white-space:pre;padding-left:{round(pad * ch)}px">{txt}</p>')
    return ('<div style="background:#1F2937;padding:24px 32px;border-radius:16px;display:flex;flex-direction:column;gap:2px">'
            + "".join(out) + "</div>")


def fig(src, alt, w, h, cap):
    return (f'<div style="display:flex;flex-direction:column;gap:8px;align-items:center"><img src="{src}" alt="{alt}" '
            f'style="width:{w}px;height:{h}px;object-fit:contain"><p style="font-size:24px;line-height:1.3;color:#6E6E6E;width:{w}px">{cap}</p></div>')


def section(sid, n, title, left, right, notes):
    return f'''<section id="{sid}" data-transition="fade" style="background:#FFFFFF;color:#3B3B3B;font-family:Arial, Helvetica, sans-serif;padding:96px 128px 160px;display:flex;flex-direction:column;gap:28px">
<h2 style="font-size:60px;font-weight:700;line-height:1.1;color:#00509A">{title}</h2>
<div style="display:flex;flex-direction:row;gap:40px;align-items:flex-start;"><div style="display:flex;flex-direction:column;gap:20px;flex:1">{left}</div><div style="display:flex;flex-direction:column;gap:16px;flex:none;align-items:center">{right}</div></div>
<p style="position:absolute;left:480px;top:992px;width:960px;text-align:center;font-size:24px;color:#6E6E6E">Cut finite element methods · MINES Paris – PSL</p>
<p style="position:absolute;right:128px;top:992px;width:120px;text-align:right;font-size:24px;color:#6E6E6E">{n}</p>
<aside>{notes}</aside>
</section>
'''


def row(*figs):
    return '<div style="display:flex;flex-direction:row;gap:20px;align-items:flex-start;">' + "".join(figs) + "</div>"


# ---- step 1
s1 = section(
    "ps-1", 0, "Example 1 · Step 1/6: mesh and level set",
    code([
        "mesh = mc.Mesh(18, box=(-1, -1, 1, 1))",
        "",
        "def level_set(x, y):  # flower, 6 petals",
        "    r = 0.48 * (1 + 0.18 * np.cos(6 * np.arctan2(y, x)))",
        "    return np.sqrt(x**2 + y**2) - r",
        "",
        "phi = level_set(mesh.nodes[:, 0], mesh.nodes[:, 1])",
        "# phi: its values at the nodes (a P1 function)",
    ]),
    fig(IMG["mesh"], "Triangular background mesh of the square with the flower-shaped zero level set drawn in black", 600, 630,
        "Background mesh and the zero level set Γ"),
    "Two minutes. Step 1 of the flower example, in minicut, the Python code of the notebook: a structured triangle mesh of the box [-1, 1]² (18 × 18 squares, 648 triangles) and a level set. Everything about the geometry is in phi, here the values of a formula at the nodes; it could equally come from an image (Example 2) or from a combination of shapes (Example 3). minicut stores phi as a P1 function, so the zero set is piecewise linear on the mesh.",
)

# ---- step 2
s2 = section(
    "ps-2", 0, "Example 1 · Step 2/6: cut and classify",
    code([
        "geom = mc.CutGeometry(mesh, phi, order=2)",
        "",
        "t = geom.cell_type",
        "inside_cells = np.where(t == mc.INSIDE)[0]",
        "cut_cells = np.where(t == mc.CUT)[0]",
        "active_cells = geom.active_cells",
        "",
        "# t: from the signs of phi at the vertices",
        "#   INSIDE   all < 0",
        "#   CUT      the signs differ",
        "#   OUTSIDE  all > 0",
    ]),
    row(fig(IMG["inside"], "Mesh with the cells entirely inside the flower in green", 420, 441, "inside_cells (82)"),
        fig(IMG["cut"], "Mesh with the cells crossed by the flower boundary in orange", 420, 441, "cut_cells (82)")),
    "Two minutes. mc.CutGeometry(mesh, phi) does the whole cut in one call: it classifies every cell from the signs of phi at its vertices, cuts the cut cells into sub-triangles, and builds the quadrature rules of the next step. Its attributes are the cell lists: cell_type is INSIDE, CUT or OUTSIDE for every cell, active_cells is inside and cut together, the active mesh of the earlier slide. Here 82 cells are inside, 82 are cut and 484 are outside.",
)

# ---- step 3
s3 = section(
    "ps-3", 0, "Example 1 · Step 3/6: quadrature rules",
    code([
        "vol = geom.volume",
        "intf = geom.interface",
        "",
        "# vol:  points, weights on T ∩ Ω",
        "# intf: points, weights, normals on Γ ∩ T",
        "",
        "vol.points.shape    # (606, 2)",
        "intf.points.shape   # (246, 2)",
        "",
        "# integrals become sums:",
        "# ∫_Ω f dx ≈ Σ_q w_q f(x_q)",
        "np.sum(vol.weights)   # |Ω_h| = 0.7316",
    ]),
    row(fig(IMG["zoom"], "Zoom on one petal of the flower: the cut cells are subdivided into triangles and a three-point rule is placed on each piece", 560, 431,
            "volume points: the pieces of T ∩ Ω near one petal"),
        fig(IMG["intf"], "Interface quadrature points along the flower boundary", 380, 399, "interface points")),
    "Two minutes. This is the step that replaces the Gauss rule of lecture 2. The rules were built by the constructor of the previous step: geom.volume holds the points and weights on the pieces T ∩ Ω (a three-point interior triangle rule, exact for degree 2, on every sub-triangle; the dense clusters at the boundary come from the thin sub-triangles of cut cells, see the zoom), geom.interface the Gauss points on the straight segments Γ ∩ T with the outward unit normal. With a P1 level set the cut is exact: the pieces are triangles and Γ is a segment in every cut cell. The sum of the volume weights is the area of the discrete flower, 0.7316, against 0.7355 for the smooth flower: the level set was interpolated on a mesh with h = 0.11, so the geometry error shrinks with the mesh like the rest.",
)

# ---- step 4
formula = (
    '<div style="background:#EAF1F8;border-radius:16px;padding:16px 28px;display:flex;flex-direction:column;gap:6px">'
    '<p style="font-size:28px;line-height:1.35;color:#3B3B3B"><span style="font-weight:700;color:#00509A">a(u, v)</span> = ∫<sub>Ω</sub> ∇u·∇v dx'
    ' <span style="color:#6E6E6E">stiffness</span></p>'
    '<p style="font-size:28px;line-height:1.35;color:#3B3B3B">&nbsp;&nbsp;&nbsp;− ∫<sub>Γ</sub> (∂<sub>n</sub>u v + u ∂<sub>n</sub>v) ds + (γ/h) ∫<sub>Γ</sub> u v ds'
    ' <span style="color:#6E6E6E">Nitsche</span></p></div>'
)
s4 = section(
    "ps-4", 0, "Example 1 · Step 4/6: the variational form",
    code([
        "f = lambda x, y: np.ones_like(x)    # f = 1",
        "g = lambda x, y: np.zeros_like(x)   # g = 0",
        "",
        "A = mc.stiffness(geom)                   # ∫Ω ∇u·∇v dx",
        "An, bn = mc.nitsche(geom, g, gamma=40.0) # Nitsche on Γ",
        "",
        "A = A + An",
        "b = mc.load(geom, f) + bn   # ∫Ω f v dx and Nitsche",
    ], size=24) + formula,
    fig(IMG["normals"], "Zoom on one petal: interface quadrature points on the boundary with the outward unit normals drawn as arrows", 640, 492,
        "interface points and normals n on Γ ∩ T"),
    "Three minutes. The weak form has two parts so far and each is one function of minicut. mc.stiffness integrates the gradient term over Ω with the volume rule; mc.nitsche integrates the Nitsche terms over Γ with the interface rule and returns the matrix and its right-hand side contribution (the g terms); the arrows are the normals n of the interface rule that the Nitsche terms use. The right-hand side f = 1 is integrated by mc.load. Inside, each function evaluates the integrals at the quadrature points and scatters the local matrices: short functions in minicut.py, which the students can read in the notebook; writing the Nitsche terms is their exercise. Nitsche's penalty is gamma / h with gamma = 40. Question for the room: is this matrix safe? The next step shows when it is not.",
)

# ---- step 5
formula_g = (
    '<div style="background:#EAF1F8;border-radius:16px;padding:16px 28px;display:flex;flex-direction:column;gap:6px">'
    '<p style="font-size:26px;line-height:1.35;color:#3B3B3B"><span style="font-weight:700;color:#00509A">ghost penalty</span>'
    ' &nbsp;+ γ<sub>g</sub> h Σ<sub>F</sub> ∫<sub>F</sub> [∂<sub>n</sub>u][∂<sub>n</sub>v] ds</p>'
    '<p style="font-size:26px;line-height:1.35;color:#3B3B3B"><span style="font-weight:700;color:#2E8B57">aggregation</span>'
    ' &nbsp;sliver dofs = polynomial of a root cell, E<sup>T</sup> A E</p></div>'
)
s5s = section(
    "ps-stab", 0, "Example 1 · Step 5/6: small cuts, and the repair",
    code([
        "Ag = mc.ghost_penalty(geom, gamma_g=0.1)",
        "",
        "# condition_number: (kappa, negative eigenvalues)",
        "mc.condition_number(geom, A)       # (5.4e4, 0)",
        "mc.condition_number(geom, A + Ag)  # (248, 0)",
        "",
        "agg = mc.aggregate(geom, 0.25)",
        "agg.summary()  # 38 ill-posed cells, 18 dofs removed",
        "mc.condition_number(geom, A, agg)  # (105, 0)",
        "",
        "A = A + Ag     # we continue with the ghost penalty",
    ], size=22) + formula_g,
    fig(IMG["stab"], "Left: the facets of cut cells where the ghost penalty acts, in red. Right: ill-posed cut cells in orange attached to their blue root cell by aggregation", 900, 450,
        "left: ghost_facets (red); right: aggregates (orange cells join the blue root)"),
    "Three minutes. The code for the stabilisation, with the numbers of this flower mesh. Without it the condition number is 5.4e4, with the ghost penalty 248, with aggregation 105. On this particular mesh the unstabilised matrix is still positive definite, but this is luck of the cut: the sweep of the conditioning block moved the boundary by one cell width and found indefinite matrices for 55 of 81 positions and condition numbers up to 2e9. Ghost penalty: mc.ghost_penalty adds the jump of the normal derivative on the facets of cut cells (red on the left), 122 facets here. Aggregation: mc.aggregate attaches every cut cell whose volume fraction is below 0.25 to a well-cut root cell; the dofs that touch no well-cut cell are removed (18 of 103) and their values are the polynomial of the root cell, which is a matrix E, so the reduced system is E^T A E. Both are tools that restore the conditioning, and both are consistent. The ghost penalty is the one we keep for the rest of the example.",
)

# ---- step 6
s5 = section(
    "ps-5", 0, "Example 1 · Step 6/6: solve and look",
    code([
        "u = mc.solve(geom, A, b)   # on the active dofs only",
        "",
        "outside = np.setdiff1d(np.arange(mesh.n_nodes),",
        "                       geom.active_dofs)",
        "len(outside)               # 258 dofs left out (red)",
        "",
        "mc.plot_solution(geom, u)  # u_h on Ω_h itself",
        "",
        "mc.area(geom)              # 0.7316  (exact 0.7355)",
    ], size=24),
    row(fig(IMG["dofs"], "Background mesh nodes with the deactivated nodes outside the active mesh marked in red", 340, 357, "deactivated DOFs"),
        fig(IMG["sol"], "Contour plot of the solution on the flower-shaped domain", 340, 357, "solution on Ω")),
    "Two minutes. The matrix is assembled over the cut pieces only. The dofs that do not touch an active cell (the red points on the left; 258 of 361) have empty rows, so mc.solve removes them and solves the system on the 103 active dofs with a sparse direct solver. mc.plot_solution draws u_h on the sub-triangulation of Ω, so the picture shows the flower and not the box. As a check, the same code on a disc of radius 0.5 reproduces the exact solution (0.25 - r²)/4 with an L2 error of 1.1e-3. The next slide measures the convergence on the flower itself with a manufactured solution.",
)

for name, s in [("ps-1", s1), ("ps-2", s2), ("ps-3", s3), ("ps-4", s4), ("ps-stab", s5s), ("ps-5", s5)]:
    (SLIDES / f"{name}.html").write_text(s)
    print("wrote", name, len(s))
