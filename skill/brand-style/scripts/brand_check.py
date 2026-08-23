"""The gate. Grades a directory of deliverables against the brand rules and
refuses (exit 1) if any file fails. Every rule here is one that actually gets
violated, in the order it gets violated.

  R1  no pure-black text               (#000000 anywhere type is set)
  R2  only approved font families      (explicitly-set fonts must be in the set)
  R3  logo present on the opening surface (page 1 / slide 1 / header)
  R4  no logo on a saturated fill      (picture on a slide whose background is a primary color)
  R5  chart series follow brand order  (first N series colors == CHART_SERIES[:N])
  R6  tint palette never used for type (text colored with a background tint)

Usage: python brand_check.py <dir>   -> prints PASS/FAIL per file, writes grading.json
"""
import json
import os
import re
import sys

from brand import BRAND, PRIMARY, TINTS

BLACK = "000000"


def _hex(rgb):
    return str(rgb).upper() if rgb is not None else None


# ---------- docx ----------
def _docx_paragraphs(doc):
    yield from doc.paragraphs
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                yield from cell.paragraphs
    for sec in doc.sections:
        yield from sec.header.paragraphs


def check_docx(path):
    from docx import Document
    doc = Document(path)
    f = []
    fonts, colors, used_styles = set(), [], set()
    for p in _docx_paragraphs(doc):
        # Grade what text resolves to: run overrides, else the paragraph's
        # style chain. The template's unused built-in styles (Courier "Macro
        # Text", etc.) are invisible to the reader and must not fail the file.
        st = p.style
        while st is not None:
            used_styles.add(st.name)
            st = st.base_style
        for r in p.runs:
            if r.font.name:
                fonts.add(r.font.name)
            if r.font.color is not None and r.font.color.rgb is not None:
                colors.append(_hex(r.font.color.rgb))
    for name in used_styles:
        st = doc.styles[name]
        if st.font.name:
            fonts.add(st.font.name)
        if st.font.color is not None and st.font.color.rgb is not None:
            colors.append(_hex(st.font.color.rgb))
    if BLACK in colors:
        f.append("R1 pure-black text")
    bad = fonts - BRAND.APPROVED_FONTS
    if bad:
        f.append(f"R2 unapproved font(s): {sorted(bad)}")
    if not doc.inline_shapes:
        f.append("R3 no logo on page 1")
    if any("#" + c in TINTS for c in colors):
        f.append("R6 tint used for type")
    return f


# ---------- pptx ----------
def _slide_bg(slide):
    try:
        fill = slide.background.fill
        return "#" + _hex(fill.fore_color.rgb) if fill.type == 1 else None
    except Exception:
        return None


def check_pptx(path):
    from pptx import Presentation
    from pptx.util import Inches
    d = Presentation(path)
    f = []
    fonts, colors = set(), []
    for i, s in enumerate(d.slides):
        pics = [sh for sh in s.shapes if sh.shape_type == 13]
        bg = _slide_bg(s)
        if i == 0 and not pics:
            f.append("R3 no logo on slide 1")
        if pics and bg in PRIMARY:
            f.append(f"R4 logo on saturated fill (slide {i + 1}, {bg})")
        if any(p.width < Inches(BRAND.tokens['logo']['min_width_in']) for p in pics):
            f.append(f"R3 logo under minimum width (slide {i + 1})")
        for sh in s.shapes:
            if sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        if r.font.name:
                            fonts.add(r.font.name)
                        try:
                            if r.font.color and r.font.color.type is not None and r.font.color.rgb is not None:
                                colors.append(_hex(r.font.color.rgb))
                        except AttributeError:
                            pass
            if getattr(sh, "has_chart", False) and sh.has_chart:
                got = []
                for ser in sh.chart.series:
                    try:
                        got.append("#" + _hex(ser.format.fill.fore_color.rgb))
                    except Exception:
                        got.append(None)
                want = BRAND.CHART_SERIES[:len(got)]
                if got != want:
                    f.append(f"R5 chart series off-order (slide {i + 1}): {got}")
    if BLACK in colors:
        f.append("R1 pure-black text")
    bad = fonts - BRAND.APPROVED_FONTS
    if bad:
        f.append(f"R2 unapproved font(s): {sorted(bad)}")
    if any("#" + c in TINTS for c in colors):
        f.append("R6 tint used for type")
    return f


# ---------- xlsx ----------
def check_xlsx(path):
    from openpyxl import load_workbook
    wb = load_workbook(path)
    f = []
    fonts, colors = set(), []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.value is None:
                    continue
                if c.font and c.font.name:
                    fonts.add(c.font.name)
                if c.font and c.font.color is not None and c.font.color.type == "rgb" and c.font.color.rgb:
                    colors.append(str(c.font.color.rgb)[-6:].upper())
    if BLACK in colors:
        f.append("R1 pure-black text")
    bad = fonts - BRAND.APPROVED_FONTS
    if bad:
        f.append(f"R2 unapproved font(s): {sorted(bad)}")
    return f


# ---------- html ----------
def check_html(path):
    with open(path) as fh:
        html = fh.read()
    f = []
    css = "".join(re.findall(r"<style>(.*?)</style>", html, re.S))
    # Only the screen stylesheet counts; print blocks may legitimately go black.
    screen = re.sub(r"@media print\s*\{.*?\}\s*\}", "", css, flags=re.S)
    if re.search(r"color\s*:\s*#000(000)?\b", screen, re.I):
        f.append("R1 pure-black text")
    fams = re.findall(r'font-family\s*:\s*"([^"]+)"', screen)
    bad = {x for x in fams if x not in BRAND.APPROVED_FONTS}
    if bad:
        f.append(f"R2 unapproved font(s): {sorted(bad)}")
    if "<img" not in html.split("<main", 1)[0]:
        f.append("R3 no logo in header")
    for t in TINTS:
        if re.search(rf"color\s*:\s*{t}", screen, re.I) and not re.search(rf"background[^;]*{t}", screen, re.I):
            f.append(f"R6 tint used for type ({t})")
    return f


CHECKS = {".docx": check_docx, ".pptx": check_pptx, ".xlsx": check_xlsx, ".html": check_html}


def grade(directory):
    results = {}
    for root, _, files in os.walk(directory):
        for name in sorted(files):
            ext = os.path.splitext(name)[1].lower()
            if ext in CHECKS:
                p = os.path.join(root, name)
                rel = os.path.relpath(p, directory)
                try:
                    results[rel] = CHECKS[ext](p)
                except Exception as e:               # a file that won't open fails loudly
                    results[rel] = [f"R0 could not open: {type(e).__name__}"]
    return results


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    results = grade(argv[1])
    if not results:
        print("BRAND GATE: nothing to check")
        return 2
    for rel, fails in results.items():
        print(f"  {'PASS' if not fails else 'FAIL'}  {rel}" + ("" if not fails else "  <- " + "; ".join(fails)))
    with open(os.path.join(argv[1], "grading.json"), "w") as fh:
        json.dump(results, fh, indent=2)
    n_fail = sum(1 for v in results.values() if v)
    if n_fail:
        print(f"BRAND GATE: FAILED - {n_fail} of {len(results)} file(s) are off-brand; do not send.")
        return 1
    print(f"BRAND GATE: PASSED - {len(results)} file(s) cleared.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
