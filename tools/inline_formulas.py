"""Inline formula images with a common baseline (mathtext cm, 30 pt / 200 dpi).
Crop rows [100-ASC, 100+DESC] around the baseline; css scale = 0.36*px/30. Run: python tools/inline_formulas.py OUTDIR"""
import sys, json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
matplotlib.rcParams["mathtext.fontset"] = "cm"
ASC, DESC = 90, 40
F = {
 "i_minAB": r"$\min(\varphi_A,\,\varphi_B)$", "i_maxAB": r"$\max(\varphi_A,\,\varphi_B)$",
 "i_negA": r"$-\varphi_A$", "i_maxAnB": r"$\max(\varphi_A,\,-\varphi_B)$",
 "i_plate": r"$\varphi=\max(\varphi_{\mathrm{box}},\,-\varphi_{\mathrm{disc}})$",
 "i_phiA": r"$\varphi_A$", "i_phiB": r"$\varphi_B$", "i_phiAB": r"$\varphi_A,\ \varphi_B$",
 "i_blade": r"$\varphi_{\mathrm{blade}}$", "i_bladeR": r"$\varphi_{\mathrm{blade}}(R_k^{-1}x)$",
 "i_hubblades": r"$\min(\varphi_{\mathrm{hub}},\,\varphi_{\mathrm{blades}})$",
 "i_gg": r"$\gamma_g$", "i_N10": r"$N^{1.0}$", "i_N12": r"$N^{1.2}$", "i_N14": r"$N^{1.4}$",
}
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
dims = {}
for k, s in F.items():
    for col, tag in (("#3B3B3B", "k"), ("#00509A", "b"), ("#6E6E6E", "g")):
        fig = plt.figure(figsize=(8, 1), dpi=200)
        fig.text(0.02, 0.5, s, fontsize=30, color=col, va="baseline", ha="left")
        fig.savefig(out/"tmp.png", dpi=200, transparent=True); plt.close(fig)
        im = np.array(Image.open(out/"tmp.png").convert("RGBA"))
        a = im[..., 3] > 8
        cols = np.where(a.any(0))[0]
        # baseline row: figure height 200, baseline at y=0.5 -> row 100
        crop = im[100-ASC:100+DESC, cols[0]-3:cols[-1]+4]
        Image.fromarray(crop).save(out/f"{k}_{tag}.png")
        dims[f"{k}_{tag}"] = [crop.shape[1], crop.shape[0]]
(out/"tmp.png").unlink()
json.dump(dims, open(out/"dims.json", "w"))
print(dims["i_minAB_k"])
