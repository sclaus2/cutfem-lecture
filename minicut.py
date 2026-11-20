"""minicut: a small cut finite element method in pure Python.

Only numpy, scipy and matplotlib are needed, so it runs on any laptop, in
Google Colab and in the browser (JupyterLite / Pyodide).  It follows the
CutFEMx workflow of the lecture:

    background mesh  ->  level set  ->  classify cells  ->  cut cells
    ->  quadrature on  Omega ∩ T  and  Gamma ∩ T
    ->  Nitsche boundary condition  ->  ghost penalty  ->  solve

Scope: 2D, P1 elements on a structured triangle mesh, P1 level set, Poisson
problem  -Δu = f  in Omega,  u = g  on Gamma.  With a P1 level set a cut
triangle is split exactly into sub-triangles and the interface Gamma is a
straight segment in each cut triangle, so all integrals below are computed
with the same ingredients CutFEMx uses at lowest order.

Conventions: phi < 0 inside Omega, phi > 0 outside, phi = 0 on Gamma, and
the interface normal n = grad(phi) / |grad(phi)| points out of Omega.
Local matrices are indexed [q, i, j] with i = test function, j = trial.
"""

from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

INSIDE, CUT, OUTSIDE = 0, 1, 2


# --------------------------------------------------------------------------
# Background mesh
# --------------------------------------------------------------------------
class Mesh:
    """Structured triangle mesh of the box (x0, y0, x1, y1), P1 geometry."""

    def __init__(self, nx, ny=None, box=(0.0, 0.0, 1.0, 1.0)):
        ny = nx if ny is None else ny
        x0, y0, x1, y1 = box
        xs, ys = np.linspace(x0, x1, nx + 1), np.linspace(y0, y1, ny + 1)
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        self.nodes = np.column_stack([X.ravel(), Y.ravel()])
        idx = np.arange((nx + 1) * (ny + 1)).reshape(nx + 1, ny + 1)
        v00, v10 = idx[:-1, :-1].ravel(), idx[1:, :-1].ravel()
        v11, v01 = idx[1:, 1:].ravel(), idx[:-1, 1:].ravel()
        self.cells = np.vstack(
            [np.column_stack([v00, v10, v11]), np.column_stack([v00, v11, v01])]
        )
        self.n_nodes, self.n_cells = len(self.nodes), len(self.cells)
        self._p1_data()
        self._facets()

    def _p1_data(self):
        p = self.nodes[self.cells]  # (nt, 3, 2)
        e1, e2 = p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]
        det = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]
        self.area = 0.5 * det
        g1 = np.column_stack([e2[:, 1], -e2[:, 0]]) / det[:, None]
        g2 = np.column_stack([-e1[:, 1], e1[:, 0]]) / det[:, None]
        # grads[c, k] = gradient of the P1 basis function of vertex k on cell c
        self.grads = np.stack([-g1 - g2, g1, g2], axis=1)
        # lambda_k(x) = offs[c, k] + grads[c, k] . x
        self.offs = 1.0 - np.einsum("ckd,ckd->ck", self.grads, p)
        edges = np.stack([p[:, 1] - p[:, 2], p[:, 2] - p[:, 0], p[:, 0] - p[:, 1]], 1)
        self.h = np.linalg.norm(edges, axis=2).max(axis=1)  # cell diameter

    def _facets(self):
        c = self.cells
        a = np.stack([c[:, 1], c[:, 2], c[:, 0]], 1).ravel()
        b = np.stack([c[:, 2], c[:, 0], c[:, 1]], 1).ravel()
        owner = np.repeat(np.arange(len(c)), 3)
        key = np.sort(np.column_stack([a, b]), axis=1)
        _, inv = np.unique(key, axis=0, return_inverse=True)
        order = np.argsort(inv.ravel(), kind="stable")
        same = inv.ravel()[order][:-1] == inv.ravel()[order][1:]  # interior edges occur twice
        f0, f1 = order[:-1][same], order[1:][same]
        self.facet_cells = np.column_stack([owner[f0], owner[f1]])
        self.facet_nodes = np.column_stack([a[f0], b[f0]])
        t = self.nodes[b[f0]] - self.nodes[a[f0]]
        self.facet_length = np.linalg.norm(t, axis=1)
        # normal of the first cell pointing outwards (cells are counter-clockwise)
        self.facet_normal = np.column_stack([t[:, 1], -t[:, 0]]) / self.facet_length[:, None]

    def bary(self, cells, X):
        """Values (nq, 3) of the three P1 basis functions of `cells` at points X."""
        return self.offs[cells] + np.einsum("qkd,qd->qk", self.grads[cells], X)


# --------------------------------------------------------------------------
# Level sets
# --------------------------------------------------------------------------
def circle(c=(0.5, 0.5), r=0.3):
    """Signed distance to a circle (negative inside)."""
    return lambda x, y: np.hypot(x - c[0], y - c[1]) - r


def ellipse(c=(0.5, 0.5), a=0.35, b=0.2, angle=0.0):
    """Approximate signed distance to an ellipse (negative inside)."""
    ca, sa = np.cos(angle), np.sin(angle)

    def phi(x, y):
        u, v = ca * (x - c[0]) + sa * (y - c[1]), -sa * (x - c[0]) + ca * (y - c[1])
        k = np.sqrt((u / a) ** 2 + (v / b) ** 2)
        return (k - 1.0) * min(a, b)

    return phi


def star(c=(0.5, 0.5), r0=0.28, amp=0.08, k=5):
    """Star-shaped (flower) domain  r < r0 + amp cos(k theta)."""

    def phi(x, y):
        th = np.arctan2(y - c[1], x - c[0])
        return np.hypot(x - c[0], y - c[1]) - (r0 + amp * np.cos(k * th))

    return phi


def union(*phis):
    """Level set of a union (CSG): the minimum."""
    return lambda x, y: np.minimum.reduce([p(x, y) for p in phis])


def intersection(*phis):
    return lambda x, y: np.maximum.reduce([p(x, y) for p in phis])


def difference(a, b):
    """a minus b."""
    return lambda x, y: np.maximum(a(x, y), -b(x, y))



def rotate(phi, angle, c=(0.5, 0.5)):
    """The shape of `phi` turned by `angle` (radians, counter-clockwise) about the point c.

    A rigid motion of the shape is a change of variable in phi: phi_turned(x) = phi(R^-1 (x - c) + c).
    """
    ca, sa = np.cos(angle), np.sin(angle)

    def phi_turned(x, y):
        X, Y = x - c[0], y - c[1]
        return phi(c[0] + ca * X + sa * Y, c[1] - sa * X + ca * Y)

    return phi_turned


def _specimen(n, seed):
    """Porous specimen: a disc of solid matrix with pores where the filtered noise is high.

    Returns (matrix mask, rng); True = solid matrix, the pores are empty.
    """
    from scipy import ndimage as ndi

    rng = np.random.default_rng(seed)
    f = ndi.gaussian_filter(rng.standard_normal((n, n)), 9.0 * n / 300.0, mode="wrap")
    f /= f.std()
    pores = ndi.binary_opening(f > 0.35)  # pores where the noise is high
    yy, xx = np.mgrid[0:n, 0:n]
    disc = (xx - n / 2) ** 2 + (yy - n / 2) ** 2 < (0.46 * n) ** 2
    return disc & ~pores, rng  # the solid matrix: the disc with the pores removed


def synthetic_image(n=300, seed=7):
    """The clean binary image of a synthetic 'scan': a porous specimen.  True = solid matrix.

    Row 0 of the array is the top of the picture (y = 1), as in any image file.
    """
    return _specimen(n, seed)[0][::-1]


def synthetic_scan(n=300, seed=7):
    """The same specimen as a noisy greyscale 'scan' in [0, 1]: matrix ~ 0.78, pores and air ~ 0.18.

    The threshold 0.5 gives back synthetic_image up to the pixels on the boundary.
    """
    from scipy import ndimage as ndi

    mask, rng = _specimen(n, seed)
    grey = np.where(mask, 0.78, 0.18) + 0.07 * rng.standard_normal((n, n))
    return ndi.gaussian_filter(grey, 1.0)[::-1]


def levelset_from_image(mask, box=(0.0, 0.0, 1.0, 1.0), smooth=1.5):
    """Turn a binary image into a level set function phi(x, y).

    1. signed distance to the material boundary in pixels (negative inside),
       using the Euclidean distance transform on both sides,
    2. Gaussian smoothing,
    3. bilinear interpolation, so phi can be evaluated at any (x, y).
    """
    from scipy import ndimage as ndi

    mask = np.asarray(mask, dtype=bool)
    d = ndi.distance_transform_edt(~mask) - ndi.distance_transform_edt(mask)
    d = ndi.gaussian_filter(d, smooth)
    x0, y0, x1, y1 = box
    ny, nx = mask.shape
    pix = (x1 - x0) / (nx - 1.0)

    def phi(x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        col = (x - x0) / (x1 - x0) * (nx - 1.0)
        row = (y1 - y) / (y1 - y0) * (ny - 1.0)
        out = ndi.map_coordinates(d, [row.ravel(), col.ravel()], order=1, mode="nearest")
        return pix * out.reshape(x.shape)

    return phi


# --------------------------------------------------------------------------
# Quadrature on reference triangles and segments
# --------------------------------------------------------------------------
def triangle_rule(order=4):
    """Barycentric points (nr, 3) and weights (sum = 1) on the reference triangle."""
    if order <= 2:
        a, b = 1.0 / 6.0, 2.0 / 3.0  # three interior points, exact for degree 2
        L = np.array([[b, a, a], [a, b, a], [a, a, b]])
        return L, np.full(3, 1.0 / 3.0)
    a, b = 0.445948490915965, 0.091576213509771
    L = np.array(
        [[a, a, 1 - 2 * a], [a, 1 - 2 * a, a], [1 - 2 * a, a, a]]
        + [[b, b, 1 - 2 * b], [b, 1 - 2 * b, b], [1 - 2 * b, b, b]]
    )
    w = np.array([0.223381589678011] * 3 + [0.109951743655322] * 3)
    return L, w


@dataclass
class Quadrature:
    """Flat list of quadrature points: point q lives in cell cells[q]."""

    cells: np.ndarray
    points: np.ndarray  # (nq, 2)
    weights: np.ndarray  # (nq,) already contain the area / length
    normals: np.ndarray = None  # (nq, 2), only for interface rules

    def __len__(self):
        return len(self.weights)


# --------------------------------------------------------------------------
# The cut: classification, sub-triangulation, quadrature rules
# --------------------------------------------------------------------------
def clip_triangle(P, f):
    """Clip the triangle with vertices P (3,2) to {f < 0}, f linear (values f at vertices).

    Returns the polygon of the clipped part (3 or 4 points, or none) and the
    points where the edges cross f = 0 (two for a cut triangle).
    """
    poly, cross = [], []
    for i in range(3):
        a, b, fa, fb = P[i], P[(i + 1) % 3], f[i], f[(i + 1) % 3]
        if fa < 0:
            poly.append(a)
        if (fa < 0) != (fb < 0):
            q = a + fa / (fa - fb) * (b - a)  # linear interpolation of the root
            poly.append(q)
            cross.append(q)
    return poly, cross


class CutGeometry:
    """Everything the cut produces from a mesh and a P1 level set.

    Attributes
    ----------
    cell_type   INSIDE / CUT / OUTSIDE for every cell
    sub_cells, sub_verts   sub-triangulation of Omega ∩ T (parent cell, vertices)
    volume      Quadrature on Omega ∩ T
    interface   Quadrature on Gamma ∩ T (with outward normals)
    active_cells, active_dofs, ghost_facets
    """

    def __init__(self, mesh, phi, order=4, interface_points=3):
        self.mesh = mesh
        phi = phi(mesh.nodes[:, 0], mesh.nodes[:, 1]) if callable(phi) else np.asarray(phi, float)
        scale = np.abs(phi).max() if phi.size else 1.0
        phi = np.where(phi == 0.0, 1e-14 * scale, phi)  # keep exact zeros off the vertices
        self.phi = phi
        pc = phi[mesh.cells]
        self.cell_type = np.where(
            (pc < 0).all(1), INSIDE, np.where((pc > 0).all(1), OUTSIDE, CUT)
        )
        self._cut_cells(order, interface_points)
        self.active_cells = np.where(self.cell_type != OUTSIDE)[0]
        self.active_dofs = np.unique(mesh.cells[self.active_cells])
        fc = mesh.facet_cells
        both = (self.cell_type[fc] != OUTSIDE).all(1)
        one_cut = (self.cell_type[fc] == CUT).any(1)
        self.ghost_facets = np.where(both & one_cut)[0]

    def _cut_cells(self, order, nseg):
        m, pc, ct = self.mesh, self.phi[self.mesh.cells], self.cell_type
        verts = m.nodes[m.cells]
        sub_cells, sub_verts, seg_cells, segs = [], [], [], []
        for c in np.where(ct == INSIDE)[0]:
            sub_cells.append(c)
            sub_verts.append(verts[c])
        for c in np.where(ct == CUT)[0]:
            poly, cross = clip_triangle(verts[c], pc[c])
            for k in range(1, len(poly) - 1):  # fan triangulation of the polygon
                sub_cells.append(c)
                sub_verts.append(np.array([poly[0], poly[k], poly[k + 1]]))
            seg_cells.append(c)
            segs.append(np.array(cross))
        self.sub_cells = np.array(sub_cells, dtype=int)
        self.sub_verts = np.array(sub_verts).reshape(-1, 3, 2)
        self.seg_cells = np.array(seg_cells, dtype=int)
        self.segments = np.array(segs).reshape(-1, 2, 2)

        # volume rule: a standard triangle rule on every sub-triangle
        L, w = triangle_rule(order)
        e1 = self.sub_verts[:, 1] - self.sub_verts[:, 0]
        e2 = self.sub_verts[:, 2] - self.sub_verts[:, 0]
        area = 0.5 * np.abs(e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0])
        pts = np.einsum("rk,skd->srd", L, self.sub_verts).reshape(-1, 2)
        self.volume = Quadrature(
            np.repeat(self.sub_cells, len(w)), pts, (area[:, None] * w).ravel()
        )
        self.area_in = np.bincount(self.sub_cells, weights=area, minlength=m.n_cells)
        self.volume_fraction = self.area_in / m.area

        # interface rule: Gauss-Legendre on every segment, normal = grad(phi) / |grad(phi)|
        xg, wg = np.polynomial.legendre.leggauss(nseg)
        xg, wg = 0.5 * (xg + 1.0), 0.5 * wg
        a, b = self.segments[:, 0], self.segments[:, 1]
        length = np.linalg.norm(b - a, axis=1)
        pts = (a[:, None, :] + xg[None, :, None] * (b - a)[:, None, :]).reshape(-1, 2)
        grad = np.einsum("ck,ckd->cd", pc[self.seg_cells], m.grads[self.seg_cells])
        n = grad / np.linalg.norm(grad, axis=1)[:, None]
        self.interface = Quadrature(
            np.repeat(self.seg_cells, nseg),
            pts,
            (length[:, None] * wg).ravel(),
            np.repeat(n, nseg, axis=0),
        )

    def summary(self):
        ct = self.cell_type
        return (
            f"{len(ct)} cells: {np.sum(ct == INSIDE)} inside, {np.sum(ct == CUT)} cut, "
            f"{np.sum(ct == OUTSIDE)} outside;  {len(self.active_dofs)} active dofs, "
            f"{len(self.ghost_facets)} ghost facets"
        )


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------
def assemble_matrix(mesh, cells, local):
    """Scatter local matrices local[q, i, j] of cells[q] into a sparse matrix."""
    d = mesh.cells[cells]
    rows = np.repeat(d[:, :, None], 3, axis=2).ravel()
    cols = np.repeat(d[:, None, :], 3, axis=1).ravel()
    n = mesh.n_nodes
    return sp.coo_matrix((local.ravel(), (rows, cols)), shape=(n, n)).tocsr()


def assemble_vector(mesh, cells, local):
    """Scatter local vectors local[q, i] of cells[q] into a vector."""
    d = mesh.cells[cells]
    return np.bincount(d.ravel(), weights=local.ravel(), minlength=mesh.n_nodes)


def stiffness(geom):
    """a(u, v) = ∫_Omega grad u . grad v dx."""
    q, m = geom.volume, geom.mesh
    G = m.grads[q.cells]
    local = q.weights[:, None, None] * np.einsum("qid,qjd->qij", G, G)
    return assemble_matrix(m, q.cells, local)


def load(geom, f):
    """L(v) = ∫_Omega f v dx."""
    q, m = geom.volume, geom.mesh
    lam = m.bary(q.cells, q.points)
    fx = f(q.points[:, 0], q.points[:, 1])
    return assemble_vector(m, q.cells, (q.weights * fx)[:, None] * lam)


def nitsche(geom, g, gamma=40.0):
    """Nitsche terms for u = g on Gamma.  Returns (matrix, vector).

    a_N(u, v) = - ∫_Γ ∂n u v  - ∫_Γ u ∂n v  + (γ/h) ∫_Γ u v
    L_N(v)    =              - ∫_Γ g ∂n v  + (γ/h) ∫_Γ g v
    """
    q, m = geom.interface, geom.mesh
    lam = m.bary(q.cells, q.points)  # (nq, 3)   v_i, u_j
    dn = np.einsum("qkd,qd->qk", m.grads[q.cells], q.normals)  # (nq, 3)  ∂n of basis fns
    w, pen = q.weights, gamma / m.h[q.cells]
    local = (
        -np.einsum("q,qi,qj->qij", w, lam, dn)  # consistency   - ∫ ∂n u v
        - np.einsum("q,qi,qj->qij", w, dn, lam)  # symmetry      - ∫ u ∂n v
        + np.einsum("q,qi,qj->qij", w * pen, lam, lam)  # penalty   γ/h ∫ u v
    )
    gx = g(q.points[:, 0], q.points[:, 1])
    local_b = (-(w * gx))[:, None] * dn + (w * pen * gx)[:, None] * lam
    return assemble_matrix(m, q.cells, local), assemble_vector(m, q.cells, local_b)


def ghost_penalty(geom, gamma_g=0.1):
    """Ghost penalty  γ_g h_avg ∫_F [∂n u][∂n v] ds  on the facets of cut cells.

    For P1 the gradient is constant per cell, so the jump of the normal
    derivative is constant on a facet and the integral is exact.
    """
    m, F = geom.mesh, geom.ghost_facets
    if len(F) == 0:
        n = m.n_nodes
        return sp.csr_matrix((n, n))
    c0, c1 = m.facet_cells[F, 0], m.facet_cells[F, 1]
    n = m.facet_normal[F]
    # jump vector over the 3 + 3 local dofs:  [∂n phi_k on c0 , - ∂n phi_k on c1]
    jump = np.concatenate(
        [np.einsum("fkd,fd->fk", m.grads[c0], n), -np.einsum("fkd,fd->fk", m.grads[c1], n)], 1
    )
    coef = gamma_g * 0.5 * (m.h[c0] + m.h[c1]) * m.facet_length[F]
    dofs = np.concatenate([m.cells[c0], m.cells[c1]], 1)  # (nf, 6), repeats are summed
    local = coef[:, None, None] * np.einsum("fi,fj->fij", jump, jump)
    rows = np.repeat(dofs[:, :, None], 6, axis=2).ravel()
    cols = np.repeat(dofs[:, None, :], 6, axis=1).ravel()
    return sp.coo_matrix((local.ravel(), (rows, cols)), shape=(m.n_nodes,) * 2).tocsr()


def poisson_system(geom, f, g, gamma=40.0, gamma_g=0.1, ghost=True):
    """A, b of  -Δu = f  with Nitsche (and ghost penalty if ghost=True)."""
    An, bn = nitsche(geom, g, gamma)
    A = stiffness(geom) + An
    if ghost:
        A = A + ghost_penalty(geom, gamma_g)
    return A.tocsr(), load(geom, f) + bn


# --------------------------------------------------------------------------
# Solving and analysing
# --------------------------------------------------------------------------
def solve(geom, A, b):
    """Solve on the active dofs.  Dofs outside the active mesh are NaN."""
    d = geom.active_dofs
    u = np.full(geom.mesh.n_nodes, np.nan)
    u[d] = spla.spsolve(A[d][:, d].tocsc(), b[d])
    return u


def condition_number(geom, A, agg=None):
    """2-norm condition number |λ|max / |λ|min of the (symmetric) active matrix.

    With `agg` (see aggregate) the matrix of the aggregated space E^T A E is used.
    Returns (kappa, number of negative eigenvalues).
    """
    if agg is None:
        d = geom.active_dofs
        ev = np.linalg.eigvalsh(A[d][:, d].toarray())
    else:
        ev = np.linalg.eigvalsh((agg.E.T @ A @ agg.E).toarray())
    return np.abs(ev).max() / np.abs(ev).min(), int(np.sum(ev < 0))


def evaluate(geom, u, cells, X):
    """P1 function u evaluated at points X lying in `cells`."""
    return np.einsum("qk,qk->q", geom.mesh.bary(cells, X), u[geom.mesh.cells[cells]])


def l2_error(geom, u, exact):
    q = geom.volume
    e = evaluate(geom, u, q.cells, q.points) - exact(q.points[:, 0], q.points[:, 1])
    return np.sqrt(np.sum(q.weights * e**2))


def h1_error(geom, u, grad_exact):
    """Energy error  ||grad(u - u_exact)||_L2(Omega)."""
    q, m = geom.volume, geom.mesh
    gu = np.einsum("qkd,qk->qd", m.grads[q.cells], u[m.cells[q.cells]])
    ge = np.column_stack(grad_exact(q.points[:, 0], q.points[:, 1]))
    return np.sqrt(np.sum(q.weights * np.sum((gu - ge) ** 2, axis=1)))


def area(geom):
    """|Omega_h| = sum of the volume weights."""
    return geom.volume.weights.sum()


def integral(geom, u):
    """Integral of the P1 function u over Omega_h (cut quadrature)."""
    q = geom.volume
    return float(np.sum(q.weights * evaluate(geom, u, q.cells, q.points)))


def perimeter(geom):
    """|Gamma_h| = sum of the interface weights."""
    return geom.interface.weights.sum()


# --------------------------------------------------------------------------
# Cell aggregation (the second remedy for small cuts)
# --------------------------------------------------------------------------
class Aggregation:
    """Cell aggregation for P1 (Badia, Verdugo, Martin 2018).

    A cut cell is ill-posed when its volume fraction |T ∩ Ω| / |T| is below `threshold`.
    Every ill-posed cell is attached to a well-posed root cell, reached through the facets of
    the active mesh.  A dof that touches no well-posed cell is removed: its value is the
    polynomial of the root cell evaluated at the dof.  This is a matrix E with
    u_full = E u_good, so the reduced system is  E^T A E  u_good = E^T b.

    Attributes: ill_cells, root (root cell of every active cell, -1 elsewhere),
    good_dofs, removed_dofs, E (n_nodes x n_good, sparse).
    """

    def __init__(self, geom, threshold=0.25):
        m, ct = geom.mesh, geom.cell_type
        act = ct != OUTSIDE
        good = act & (geom.volume_fraction >= threshold)
        self.threshold = threshold
        self.ill_cells = np.where(act & ~good)[0]
        # facet graph of the active cells, multi-source BFS from the well-posed cells
        fc = m.facet_cells
        both = act[fc].all(1)
        nbr = [[] for _ in range(m.n_cells)]
        for a, b in fc[both]:
            nbr[a].append(b)
            nbr[b].append(a)
        root = np.full(m.n_cells, -1)
        dist = np.full(m.n_cells, np.inf)
        queue = list(np.where(good)[0])
        root[queue], dist[queue] = queue, 0
        for c in queue:  # the list grows while we loop: breadth-first
            for d in nbr[c]:
                if root[d] < 0:
                    root[d], dist[d] = root[c], dist[c] + 1
                    queue.append(d)
        self.root, self.dist = root, dist
        # dofs: good if they touch a well-posed cell, otherwise removed
        gdofs = np.unique(m.cells[np.where(good)[0]])
        self.good_dofs = gdofs
        self.removed_dofs = np.setdiff1d(geom.active_dofs, gdofs)
        n, ng = m.n_nodes, len(gdofs)
        pos = np.full(n, -1)
        pos[gdofs] = np.arange(ng)
        rows, cols, vals = [gdofs], [np.arange(ng)], [np.ones(ng)]
        if len(self.removed_dofs):
            # for every removed dof take its closest ill-posed cell and that cell's root
            best = {}
            for c in self.ill_cells:
                for v in m.cells[c]:
                    if pos[v] < 0 and (v not in best or dist[c] < dist[best[v]]):
                        best[v] = c
            dofs = np.array(list(best.keys()))
            rc = np.array([root[best[v]] for v in dofs])
            lam = m.bary(rc, m.nodes[dofs])  # root polynomial at the removed dof
            rows.append(np.repeat(dofs, 3))
            cols.append(pos[m.cells[rc]].ravel())
            vals.append(lam.ravel())
        self.E = sp.coo_matrix(
            (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, ng)
        ).tocsr()

    def summary(self):
        return (f"{len(self.ill_cells)} ill-posed cells (fraction < {self.threshold}), "
                f"{len(self.removed_dofs)} dofs removed, {len(self.good_dofs)} left")


def aggregate(geom, threshold=0.25):
    """Aggregation object for `geom` (see Aggregation)."""
    return Aggregation(geom, threshold)


def solve_aggregated(geom, A, b, agg):
    """Solve E^T A E u_good = E^T b and return the full vector u = E u_good."""
    E = agg.E
    ug = spla.spsolve((E.T @ A @ E).tocsc(), E.T @ b)
    u = np.full(geom.mesh.n_nodes, np.nan)
    u[geom.active_dofs] = (E @ ug)[geom.active_dofs]
    return u


def smallest_mode(geom, A, agg=None):
    """Eigenvalue of smallest magnitude of A on the active dofs and its eigenvector.

    With `agg` the reduced matrix E^T A E is used and the mode is expanded to all dofs.
    Returns (eigenvalue, mode on the nodes, NaN outside the active dofs).
    """
    if agg is None:
        d = geom.active_dofs
        ev, V = np.linalg.eigh(A[d][:, d].toarray())
        k = np.argmin(np.abs(ev))
        mode = np.full(geom.mesh.n_nodes, np.nan)
        mode[d] = V[:, k]
    else:
        ev, V = np.linalg.eigh((agg.E.T @ A @ agg.E).toarray())
        k = np.argmin(np.abs(ev))
        mode = np.full(geom.mesh.n_nodes, np.nan)
        mode[geom.active_dofs] = (agg.E @ V[:, k])[geom.active_dofs]
    return ev[k], mode


def gmres_iterations(geom, A, b, tol=1e-8, scale=False, agg=None):
    """Number of GMRES iterations to reduce the residual by `tol` (no preconditioner,
    or diagonal scaling if scale=True).  Works on the active dofs (or the reduced system)."""
    if agg is None:
        d = geom.active_dofs
        M, r = A[d][:, d].tocsr(), b[d]
    else:
        M, r = (agg.E.T @ A @ agg.E).tocsr(), agg.E.T @ b
    if scale:
        s = 1.0 / np.sqrt(np.abs(M.diagonal()))
        M, r = sp.diags(s) @ M @ sp.diags(s), s * r
    count = [0]
    spla.gmres(M, r, rtol=tol, atol=0.0, restart=M.shape[0], maxiter=M.shape[0],
               callback=lambda _: count.__setitem__(0, count[0] + 1), callback_type="pr_norm")
    return count[0]


# --------------------------------------------------------------------------
# Plotting
# --------------------------------------------------------------------------
_COLOURS = {INSIDE: "#CFE2F5", CUT: "#F9C48F", OUTSIDE: "#FFFFFF"}  # inside blue, cut orange, outside white (inactive)


def _axes(ax):
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.set_aspect("equal")
    return ax


def plot_levelset(mesh, phi, ax=None, levels=15):
    """Filled contours of the level set with the zero contour in black."""
    import matplotlib.tri as mtri

    ax = _axes(ax)
    phi = phi(mesh.nodes[:, 0], mesh.nodes[:, 1]) if callable(phi) else phi
    tri = mtri.Triangulation(mesh.nodes[:, 0], mesh.nodes[:, 1], mesh.cells)
    cs = ax.tricontourf(tri, phi, levels=levels, cmap="RdBu_r")
    ax.tricontour(tri, phi, levels=[0.0], colors="k", linewidths=2)
    ax.triplot(tri, color="k", lw=0.2, alpha=0.4)
    ax.figure.colorbar(cs, ax=ax, shrink=0.8, label="phi")
    return ax


def plot_cells(geom, ax=None, subtriangulation=False, interface=True, quadrature=None,
               ghost=False, normals=False, zoom=None):
    """Classified background mesh.

    quadrature: None, 'volume' or 'interface' (draw the quadrature points)
    zoom: (x0, x1, y0, y1) to zoom in on a few cells
    """
    from matplotlib.collections import LineCollection, PolyCollection

    ax = _axes(ax)
    m = geom.mesh
    V = m.nodes[m.cells]
    ax.add_collection(
        PolyCollection(V, facecolors=[_COLOURS[t] for t in geom.cell_type],
                       edgecolors="k", linewidths=0.4 if m.n_cells < 3000 else 0.05)
    )
    if subtriangulation:
        ax.add_collection(
            PolyCollection(geom.sub_verts, facecolors="none", edgecolors="#1f6fb2", linewidths=0.8)
        )
    if ghost and len(geom.ghost_facets):
        pts = m.nodes[m.facet_nodes[geom.ghost_facets]]
        ax.add_collection(LineCollection(pts, colors="#c0392b", linewidths=2.5))
    if interface:
        ax.add_collection(LineCollection(geom.segments, colors="k", linewidths=2))
    if quadrature == "volume":
        p = geom.volume.points
        ax.plot(p[:, 0], p[:, 1], ".", color="#1f6fb2", ms=3)
    elif quadrature == "interface":
        p = geom.interface.points
        ax.plot(p[:, 0], p[:, 1], "o", color="#c0392b", ms=3)
    if normals:
        p, n = geom.interface.points, geom.interface.normals
        ax.quiver(p[:, 0], p[:, 1], n[:, 0], n[:, 1], color="#c0392b", scale=25, width=0.004)
    x0, y0 = m.nodes.min(0)
    x1, y1 = m.nodes.max(0)
    ax.set_xlim(*(zoom[:2] if zoom else (x0, x1)))
    ax.set_ylim(*(zoom[2:] if zoom else (y0, y1)))
    return ax


def plot_aggregation(geom, agg, ax=None, zoom=None):
    """Aggregates of a cell aggregation: well-posed cells blue, ill-posed cut cells red,
    an arrow from every ill-posed cell to its root cell, removed dofs as black crosses."""
    from matplotlib.collections import LineCollection, PolyCollection

    ax = _axes(ax)
    m = geom.mesh
    act = geom.cell_type != OUTSIDE
    ill = np.zeros(m.n_cells, bool)
    ill[agg.ill_cells] = True
    colours = [("#E8795C" if ill[c] else "#CFE2F5") if act[c] else "#FFFFFF" for c in range(m.n_cells)]
    ax.add_collection(PolyCollection(m.nodes[m.cells], facecolors=colours, edgecolors="k",
                                     linewidths=0.4 if m.n_cells < 3000 else 0.05))
    ax.add_collection(LineCollection(geom.segments, colors="k", linewidths=2))
    cen = m.nodes[m.cells].mean(1)
    for c in agg.ill_cells:
        r = agg.root[c]
        if r >= 0:
            ax.annotate("", xy=cen[r], xytext=cen[c], arrowprops=dict(arrowstyle="->", color="#7a1f0c", lw=1.4))
    if len(agg.removed_dofs):
        p = m.nodes[agg.removed_dofs]
        ax.plot(p[:, 0], p[:, 1], "kx", ms=7, mew=1.6)
    x0, y0 = m.nodes.min(0)
    x1, y1 = m.nodes.max(0)
    ax.set_xlim(*(zoom[:2] if zoom else (x0, x1)))
    ax.set_ylim(*(zoom[2:] if zoom else (y0, y1)))
    return ax


def plot_solution(geom, u, ax=None, levels=20, mesh_lines=False):
    """Solution on Omega_h only (the sub-triangulation of the active cells)."""
    import matplotlib.tri as mtri

    ax = _axes(ax)
    ns = len(geom.sub_verts)
    pts = geom.sub_verts.reshape(-1, 2)
    cells = np.repeat(geom.sub_cells, 3)
    vals = evaluate(geom, u, cells, pts)
    tri = mtri.Triangulation(pts[:, 0], pts[:, 1], np.arange(3 * ns).reshape(-1, 3))
    tc = ax.tricontourf(tri, vals, levels=levels, cmap="viridis")
    ax.figure.colorbar(tc, ax=ax, shrink=0.8, label="u_h")
    if mesh_lines:
        ax.triplot(tri, color="k", lw=0.2)
    return ax
