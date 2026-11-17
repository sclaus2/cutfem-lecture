
import html, re, sys
from pathlib import Path
D = Path(sys.argv[1])

def code(lines, size=22, pad="24px 32px", gap=2):
    out=[]
    for ln in lines:
        if not ln.strip():
            out.append(f'<p style="font-size:{size}px;line-height:1.38;font-family:\'Courier New\', monospace;color:#F3F4F6;white-space:pre">&nbsp;</p>'); continue
        pad_n=len(ln)-len(ln.lstrip(" ")); body=ln.lstrip(" ")
        if "#" in body:
            k=body.index("#"); txt=html.escape(body[:k])+f'<span style="color:#9CA3AF">{html.escape(body[k:])}</span>'
        else: txt=html.escape(body)
        out.append(f'<p style="font-size:{size}px;line-height:1.38;font-family:\'Courier New\', monospace;color:#F3F4F6;white-space:pre;padding-left:{round(pad_n*size*0.6)}px">{txt}</p>')
    return f'<div style="background:#1F2937;padding:{pad};border-radius:16px;display:flex;flex-direction:column;gap:{gap}px">'+"".join(out)+"</div>"

CODEBOX = re.compile(r'<div style="background:#1F2937;[^"]*">(?:\s*<p .*?</p>)+\s*</div>', re.S)

def sub1(s, old, new, name):
    if old not in s and new in s:
        return s  # already applied
    assert old in s, f"{name}: not found: {old[:60]}"
    return s.replace(old, new, 1)

# ---- img2ls-1
f=D/"img2ls-1.html"; s=f.read_text()
s=sub1(s,"/_blob/b25d17988edcb1bf4b7c514613c7a8ae","/_blob/0c71fa6b23f24386843bad739f6948c6","img2ls-1 img")
s=sub1(s,"Synthetic image generated for this lecture (filtered noise, thresholded); the same steps apply to a real scan.","Synthetic scan made with minicut for this lecture (a porous blob plus bounded noise); the same steps apply to a real scan.","img2ls-1 caption")
s=sub1(s,"(here a synthetic micro-CT-like slice that I generated: filtered random noise, thresholded, with added scanner noise; with a real scan the steps are identical)","(here a synthetic slice made with mc.synthetic_scan: a porous blob with bounded noise added; with a real scan the steps are identical)","img2ls-1 notes a")
s=sub1(s,"748 of 4050 triangles","382 of 4050 triangles","img2ls-1 notes b")
f.write_text(s)

# ---- img2ls-2
f=D/"img2ls-2.html"; s=f.read_text()
new=code([
 "from scipy import ndimage as ndi",
 "",
 "B = scan > 0.5                  # True = material",
 "d_in  = ndi.distance_transform_edt(B)",
 "d_out = ndi.distance_transform_edt(~B)",
 "phi_px = np.where(B, -d_in, d_out)",
 "phi_px = ndi.gaussian_filter(phi_px, 1.5)",
 "",
 "# minicut: these steps and the interpolation in one call",
 "phi = mc.levelset_from_image(B, smooth=1.5)",
 "",
 "mesh = mc.Mesh(45)",
 "geom = mc.CutGeometry(mesh, phi)",
])
assert CODEBOX.search(s)
s=CODEBOX.sub(lambda m:new,s,count=1)
s=sub1(s,"(Dino.stl demo in CutFEMx)","(CutFEMx ships an STL demo)","img2ls-2 bullet")
s=sub1(s,"The recipe in code, with SciPy: distance transforms on both sides of the boundary, the sign convention negative inside, a light Gaussian smoothing, and a regular grid interpolator that is evaluated at the nodes of the background mesh through phi.interpolate. The coordinates have to be scaled from pixels to physical units. This is a sketch of the recipe used to make the previous figure.","The recipe in code, with SciPy: distance transforms on both sides of the boundary, the sign convention negative inside, a light Gaussian smoothing, and a bilinear interpolation that lets phi be evaluated at any point, in particular at the nodes of the background mesh. mc.levelset_from_image does exactly these steps (and scales pixels to physical units); this is the code that made the previous figure and the next slide. CutGeometry evaluates phi at the nodes of the 45 by 45 mesh and cuts it.","img2ls-2 notes a")
s=sub1(s,"For CAD or STL geometries the signed distance to the surface does the same job: CutFEMx has an STL distance demo (python/demo/demo_stl_distance.py, Dino.stl).","For CAD or STL geometries the signed distance to the surface does the same job: CutFEMx has an STL distance demo (python/demo/demo_stl_distance.py, Dino.stl), which minicut does not have.","img2ls-2 notes b")
f.write_text(s)

# ---- nitsche-code
f=D/"nitsche-code.html"; s=f.read_text()
new=code([
 "q = geom.interface                                         # points x_q, weights w_q, normals n_q on Γ",
 "lam = mesh.bary(q.cells, q.points)                         # basis functions v_i(x_q)",
 "dn = np.einsum(\"qkd,qd->qk\", mesh.grads[q.cells], q.normals)   # their normal derivatives ∂n v_i(x_q)",
 "w, pen = q.weights, gamma / mesh.h[q.cells]                # w_q and γ/h",
 "gx = g(q.points[:, 0], q.points[:, 1])                     # boundary data g(x_q)",
 "",
 "local   = - np.einsum(\"q,qi,qj->qij\", w, lam, dn)                # - ∫ ∂n u v",
 "local  += - np.einsum(\"q,qi,qj->qij\", w, dn, lam)                # - ∫ u ∂n v",
 "local  += np.einsum(\"q,qi,qj->qij\", w * pen, lam, lam)           # + γ/h ∫ u v",
 "local_b = - (w * gx)[:, None] * dn + (w * pen * gx)[:, None] * lam   # - ∫ g ∂n v + γ/h ∫ g v",
], size=22, pad="28px 36px", gap=6)
assert CODEBOX.search(s)
s=CODEBOX.sub(lambda m:new,s,count=1)
s=sub1(s,"Poisson demo in CutFEMx and UFL, γ = 40: dx_omega integrates over Ω, dx_gamma over Γ, n_gamma = ∇φ/|∇φ|","minicut, γ = 40: local[q, i, j] with i the test and j the trial function, scattered into the matrix; the Ω term is mc.stiffness, mc.load","nitsche-code caption")
s=sub1(s,"Five minutes. The code is the formula: the first line is lecture 1, the Gamma integrals are the Nitsche terms. The only new objects are the two measures: dx_omega carries the volume quadrature rules of T intersect Omega and dx_gamma carries the interface rules. UFL (already used by FEniCS and FFCx) lets us write forms close to the mathematics. Source: python/demo/demo_poisson.py. Ghost penalty term is added in the stability block.","Five minutes. The code is the formula, in minicut. The interface rule gives the points x_q, weights w_q and normals n_q on Gamma; lam holds the P1 basis functions at those points and dn their normal derivatives. The three boundary terms of the left-hand side are three lines (consistency, symmetry, penalty) and the two data terms are the last line. The volume term is mc.stiffness (lecture 1, with the cut volume rule) and mc.load; local[q, i, j] is scattered into the global matrix by mc.assemble_matrix. These are the lines of mc.nitsche, which the students write in section 5 of the notebook. In CutFEMx the same forms are written in UFL, a = inner(grad(u), grad(v)) * dx_omega + (...) * dx_gamma, where dx_omega and dx_gamma carry the runtime quadrature rules. The ghost penalty term is added in the stability block.","nitsche-code notes")
f.write_text(s)

# ---- plan
f=D/"plan.html"; s=f.read_text()
s=sub1(s,"The algorithm and five steps in CutFEMx, convergence","The algorithm and five steps in code, convergence","plan")
f.write_text(s)

# ---- deck.json
f=D.parent/"deck.json"; s=f.read_text()
s=sub1(s,"Poisson step by step in CutFEMx","Poisson step by step in minicut","deck.json")
f.write_text(s)
print("edited")
