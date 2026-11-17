"""Write the install-minicut slide (Windows) and renumber the footers of a deck directory.

usage: python tools/install_slide.py DECK_ROOT      (DECK_ROOT/project/deck.json and project/slides/*.html)
"""
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) / "project"
# Footer logos (République Française, ONERA) are not published here; set LOGO_HTML to the two <img> tags in your private copy.
LOGO_HTML = ''


def line(text, pad=0, grey=False):
    col = "#566275" if grey else "#1F2937"
    inner = text if text else "&nbsp;"
    ws = "white-space:pre;" if text else ""
    return (f'<p style="font-size:26px;line-height:1.45;font-family:Consolas, Menlo, \'DejaVu Sans Mono\', \'Courier New\', monospace; font-weight:700;color:{col};{ws}'
            f'padding-left:{pad}px">{inner}</p>')


def code(lines):
    return ('<div style="background:#F4F7FB;border:2px solid #B9C7D8;padding:24px 32px;border-radius:16px;display:flex;flex-direction:column;gap:2px">'
            + "".join(lines) + "</div>")


def step(n, title, body):
    return ('<div style="display:flex;flex-direction:row;gap:24px;align-items:flex-start">'
            f'<div style="width:48px;height:48px;border-radius:24px;background:#00509A;color:#FFFFFF;font-size:28px;font-weight:700;'
            f'display:flex;flex-direction:row;align-items:center;justify-content:center;flex:none">{n}</div>'
            '<div style="display:flex;flex-direction:column;gap:4px;flex:1">'
            f'<p style="font-size:32px;font-weight:700;color:#00509A;line-height:1.2">{title}</p>'
            f'<p style="font-size:26px;line-height:1.35">{body}</p></div></div>')


steps = (
    step(1, "Install Python 3.9 or newer", "From python.org. In the installer tick <b>Add python.exe to PATH</b>.")
    + step(2, "Download the repository", "Open <b>github.com/sclaus2/cutfem-lecture</b>, click <b>Code → Download ZIP</b>, "
           "then right-click the file and choose <b>Extract All</b>. (With git: <span style=\"font-family:Consolas, Menlo, 'DejaVu Sans Mono', 'Courier New', monospace; font-weight:700\">git clone</span> the same address.)")
    + step(3, "Open PowerShell in that folder", "In File Explorer click the address bar of the extracted folder, type <b>powershell</b>, press Enter.")
    + step(4, "Install and start", "Paste the commands on the right, one block at a time. Jupyter opens in your browser.")
)

cmds = code([
    line("py -m venv .venv"),
    line(".venv\\Scripts\\Activate.ps1"),
    line("pip install -r requirements.txt"),
    line(""),
    line("jupyter lab notebooks\\cutfem_lecture.ipynb"),
])
tips = ('<div style="background:#FDEBD8;padding:16px 28px;border-radius:16px;display:flex;flex-direction:column;gap:6px">'
        '<p style="font-size:28px;font-weight:700;color:#B34F00">If something fails</p>'
        '<p style="font-size:24px;line-height:1.35">PowerShell refuses to run <b>Activate.ps1</b>: first run '
        "<span style=\"font-family:Consolas, Menlo, 'DejaVu Sans Mono', 'Courier New', monospace; font-weight:700\">Set-ExecutionPolicy -Scope Process Bypass</span></p>"
        '<p style="font-size:24px;line-height:1.35">Keep the folder as it is: the notebook imports <b>minicut.py</b> from the folder above it.</p></div>')

URL = "https://github.com/sclaus2/cutfem-lecture/archive/main.zip"
banner = ('<div style="background:#EAF1F8;border:3px solid #00509A;border-radius:16px;padding:18px 28px;display:flex;flex-direction:column;gap:10px">'
          '<p style="font-size:28px;font-weight:700;color:#00509A">In one line: just minicut, nothing else to download</p>'
          '<div style="background:#F4F7FB;border:2px solid #B9C7D8;border-radius:12px;padding:12px 24px">'
          f'<p style="font-size:28px;line-height:1.4;font-family:Consolas, Menlo, \'DejaVu Sans Mono\', \'Courier New\', monospace; font-weight:700;color:#1F2937;white-space:pre">pip install {URL}</p></div>'
          '<p style="font-size:24px;line-height:1.35">After installing Python (step 1), run this in any PowerShell window. It installs numpy, scipy and matplotlib too, '
          "and <span style=\"font-family:Consolas, Menlo, 'DejaVu Sans Mono', 'Courier New', monospace; font-weight:700\">import minicut</span> then works in any folder. "
          'The notebooks and exercises need the repository folder: steps 2 to 4.</p></div>')

html = f'''<section id="install-minicut" data-transition="fade" style="background:#FFFFFF;color:#3B3B3B;font-family:Arial, Helvetica, sans-serif;padding:96px 128px 160px;display:flex;flex-direction:column;gap:22px">
<h2 style="font-size:60px;font-weight:700;line-height:1.1;color:#00509A">Get minicut: install it on Windows</h2>
{banner}
<div style="display:flex;flex-direction:row;gap:56px;align-items:flex-start">
<div style="display:flex;flex-direction:column;gap:20px;flex:1">{steps}</div>
<div style="display:flex;flex-direction:column;gap:18px;width:760px;flex:none">{cmds}{tips}</div>
</div>
<p style="font-size:24px;line-height:1.3;color:#6E6E6E">minicut is one file, minicut.py: numpy, scipy and matplotlib only, no compiler, no FEniCSx. On macOS or Linux: python3 -m venv .venv, source .venv/bin/activate, then the same pip and jupyter lines.</p>
{LOGO_HTML}
<p style="position:absolute;left:480px;top:992px;width:960px;text-align:center;font-size:24px;color:#6E6E6E">Cut finite element methods · MINES Paris – PSL</p>
<p style="position:absolute;right:128px;top:992px;width:120px;text-align:right;font-size:24px;color:#6E6E6E">0</p>
<aside>Two minutes, or skip it in the lecture and point to it. Everything we run in the lecture is minicut: one Python file with numpy, scipy and matplotlib, so it installs on a Windows laptop without a compiler. Steps: install Python from python.org and tick "Add python.exe to PATH"; download the repository as a ZIP from GitHub (Code, Download ZIP) and extract it; open PowerShell in the extracted folder (type powershell in the address bar of File Explorer); create a virtual environment with py -m venv .venv, activate it with .venv\\Scripts\\Activate.ps1, install numpy, scipy, matplotlib and jupyterlab with pip install -r requirements.txt, and start the notebook with jupyter lab notebooks\\cutfem_lecture.ipynb. To only get minicut, one line after installing Python is enough: pip install https://github.com/sclaus2/cutfem-lecture/archive/main.zip (the repository has a pyproject.toml; this installs minicut and its three dependencies, and import minicut works in any folder; it needs no git). The notebooks are not part of that package, so for the exercises use the ZIP steps. If PowerShell blocks the activation script, Set-ExecutionPolicy -Scope Process Bypass allows it for this window only. The notebook finds minicut.py in the folder above it, so keep the folder structure. On macOS or Linux use python3 -m venv .venv and source .venv/bin/activate. Not tested here: Google Colab or other online notebooks.</aside>
</section>
'''
(root / "slides" / "install-minicut.html").write_text(html)

deck = json.loads((root / "deck.json").read_text())
order = deck["order"]
if "install-minicut" not in order:
    order.insert(order.index("levelset") + 1, "install-minicut")
(root / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False) + "\n")

changed = []
for i, sid in enumerate(order, 1):
    p = root / "slides" / f"{sid}.html"
    s = p.read_text()
    m = list(re.finditer(r'(text-align:right[^>]*>)(\d+)(</p>)', s))
    if not m:
        continue
    if int(m[-1].group(2)) != i:
        s = s[:m[-1].start(2)] + str(i) + s[m[-1].end(2):]
        p.write_text(s); changed.append(sid)
print("footers changed:", len(changed), "slides:", len(order))
print(json.dumps(changed))
