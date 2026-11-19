"""QR code of the repository address for the install slide (needs: pip install segno).

Run:  python tools/qr_repo.py OUTDIR [URL]
"""
import sys
from pathlib import Path

import segno

out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
url = sys.argv[2] if len(sys.argv) > 2 else "https://github.com/sclaus2/cutfem-lecture"
out.mkdir(parents=True, exist_ok=True)
q = segno.make(url, error=segno.consts.ERROR_CORRECTION_LEVELS["M"] if hasattr(segno.consts, "ERROR_CORRECTION_LEVELS") else "m")
q.save(out / "repo_qr.png", scale=14, border=2, dark="#1F2937", light="#FFFFFF")
print(url, q.version, q.designator)
