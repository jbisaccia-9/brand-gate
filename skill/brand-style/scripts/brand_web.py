"""Self-contained HTML: one file, no external requests, so it survives email."""
import base64
import os

from brand import BRAND


def css():
    fam = ", ".join([f'"{BRAND.fonts["body"]}"'] + [f'"{f}"' for f in BRAND.fonts["fallback"]])
    return f"""
:root {{ --blue:{BRAND.BLUE}; --green:{BRAND.GREEN}; --amber:{BRAND.AMBER}; --ink:{BRAND.INK}; --paper:{BRAND.PAPER}; --tint:{BRAND.BLUE_TINT}; }}
body {{ font-family:{fam}; color:var(--ink); background:#fff; margin:0; }}
h1,h2,h3 {{ font-family:"{BRAND.fonts["heading"]}",{fam}; color:var(--blue); font-weight:500; }}
header {{ background:var(--paper); padding:16px 32px; border-bottom:4px solid var(--amber); }}
header img {{ height:40px; }}
main {{ padding:24px 32px; max-width:1100px; }}
.b-card {{ background:var(--paper); border-radius:8px; padding:16px; }}
.b-kpi {{ display:inline-block; background:var(--tint); padding:16px 24px; border-radius:8px; margin-right:12px; }}
.b-kpi b {{ display:block; font-size:32px; color:var(--blue); }}
table.b {{ border-collapse:collapse; width:100%; }}
table.b th {{ background:var(--blue); color:#fff; padding:8px; text-align:left; }}
table.b td {{ padding:8px; border-bottom:1px solid var(--tint); }}
@media print {{ header {{ border-bottom-color:#000; }} }}
"""


def _logo_data_uri():
    with open(BRAND.logo("primary"), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def page(title, body_html, subtitle=""):
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>
<style>{css()}</style></head><body>
<header><img src="{_logo_data_uri()}" alt="{BRAND.name}"></header>
<main><h1>{title}</h1><p>{subtitle}</p>{body_html}</main></body></html>"""


def kpi(value, label):
    return f'<div class="b-kpi"><b>{value}</b>{label}</div>'


def table(rows):
    head, *body = rows
    th = "".join(f"<th>{c}</th>" for c in head)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in body)
    return f'<table class="b"><tr>{th}</tr>{trs}</table>'


def finish(html, path):
    with open(path, "w") as f:
        f.write(html)
    return path
