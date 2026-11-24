"""Render report/fig/*.mmd (Mermaid) to tight vector PDFs with headless Chromium.

Usage: python experiment/scripts/render_diagrams.py [chrome_binary]
"""
import html
import subprocess
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parents[2] / "report" / "fig"
CHROME = sys.argv[1] if len(sys.argv) > 1 else "chromium"
CONFIG = ("{startOnLoad: false, theme: 'neutral', fontFamily: 'Helvetica, Arial, sans-serif', "
          "flowchart: {useMaxWidth: false}, sequence: {useMaxWidth: false, mirrorActors: false, "
          "messageFontSize: 15, actorFontSize: 15}}")

for src in sorted(FIG.glob("*.mmd")):
    page = FIG / f"{src.stem}.html"
    page.write_text(f"""<!doctype html><html><head><meta charset="utf-8">
<style>html, body {{ margin: 0; padding: 0; background: white; overflow: hidden; }} #d {{ display: inline-block; }}</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script></head>
<body><div id="d" class="mermaid">{html.escape(src.read_text())}</div>
<script>
mermaid.initialize({CONFIG});
mermaid.run({{querySelector: '#d'}}).then(() => {{
  const r = document.querySelector('#d svg').getBoundingClientRect();
  const st = document.createElement('style');  // page = diagram size, so the PDF needs no cropping
  st.textContent = `@page {{ size: ${{Math.ceil(r.width) + 24}}px ${{Math.ceil(r.height) + 24}}px; margin: 0 }}
                    body {{ padding: 4px }}`;
  document.head.appendChild(st);
}});
</script></body></html>""")
    out = FIG / f"{src.stem}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                    "--virtual-time-budget=20000", "--run-all-compositor-stages-before-draw",
                    f"--print-to-pdf={out}", page.as_uri()], check=True, capture_output=True)
    page.unlink()
    print("wrote", out)
