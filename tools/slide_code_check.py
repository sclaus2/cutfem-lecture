"""Run the code shown on the slides 'The Nitsche form, and the same in code' and
'Example 1 · The recipe in code' and check it against minicut.

Run from the repository root:   PYTHONPATH=. python tools/slide_code_check.py
"""

import numpy as np
from scipy import ndimage as ndi

import minicut as mc

# ------------------------------------------------------------ slide: recipe in code
scan = mc.synthetic_scan()

B = scan > 0.5  # True = material
d_in = ndi.distance_transform_edt(B)
d_out = ndi.distance_transform_edt(~B)
phi_px = np.where(B, -d_in, d_out)
phi_px = ndi.gaussian_filter(phi_px, 1.5)

# minicut does these steps, and the interpolation, in one call:
phi = mc.levelset_from_image(B, smooth=1.5)
mesh = mc.Mesh(45)
geom = mc.CutGeometry(mesh, phi)  # phi at the 46 x 46 nodes

print(geom.summary())
# the pixel-unit field and the minicut level set agree up to the pixel size
pix = 1.0 / (B.shape[1] - 1)
x, y = 0.5, 0.5
col, row = x * (B.shape[1] - 1), (1 - y) * (B.shape[0] - 1)
print("phi at the centre", phi(x, y), " pixel field * pix", pix * ndi.map_coordinates(phi_px, [[row], [col]], order=1)[0])

# ------------------------------------------------------------ slide: Nitsche in code
gamma = 40.0
g = lambda x, y: np.sin(np.pi * x) * np.sinh(y)
mesh = mc.Mesh(20)
geom = mc.CutGeometry(mesh, mc.circle((0.5, 0.5), 0.33))

q = geom.interface
lam = mesh.bary(q.cells, q.points)
dn = np.einsum("qkd,qd->qk", mesh.grads[q.cells], q.normals)
w, pen = q.weights, gamma / mesh.h[q.cells]
gx = g(q.points[:, 0], q.points[:, 1])

local = -np.einsum("q,qi,qj->qij", w, lam, dn)
local += -np.einsum("q,qi,qj->qij", w, dn, lam)
local += np.einsum("q,qi,qj->qij", w * pen, lam, lam)
local_b = -(w * gx)[:, None] * dn + (w * pen * gx)[:, None] * lam

A = mc.assemble_matrix(mesh, q.cells, local)
b = mc.assemble_vector(mesh, q.cells, local_b)
A_ref, b_ref = mc.nitsche(geom, g, gamma)
print("Nitsche: max diff matrix", abs(A - A_ref).max(), " vector", np.abs(b - b_ref).max())
