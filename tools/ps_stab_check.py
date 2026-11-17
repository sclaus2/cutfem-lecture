"""Runs the code of the slide 'Example 1 · Step 5: it breaks, and the repair' (minicut)."""
import numpy as np
import minicut as mc

mesh = mc.Mesh(18, box=(-1, -1, 1, 1))
phi = lambda x, y: np.sqrt(x**2 + y**2) - 0.48 * (1 + 0.18 * np.cos(6 * np.arctan2(y, x)))
geom = mc.CutGeometry(mesh, phi, order=2)
f = lambda x, y: np.ones_like(x)
g = lambda x, y: np.zeros_like(x)
A = mc.stiffness(geom)
An, bn = mc.nitsche(geom, g, gamma=40.0)
A = A + An
b = mc.load(geom, f) + bn

# ---- shown on the slide
Ag = mc.ghost_penalty(geom, gamma_g=0.1)
print("Nitsche only   ", mc.condition_number(geom, A))
print("+ ghost penalty", mc.condition_number(geom, A + Ag))

agg = mc.aggregate(geom, threshold=0.25)
print(agg.summary())
print("aggregation    ", mc.condition_number(geom, A, agg))
A = A + Ag
u = mc.solve(geom, A, b)
print("max u", np.nanmax(u), " area", mc.area(geom))
