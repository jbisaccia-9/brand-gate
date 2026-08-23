"""Builds one deliverable per format, on-brand (build) or off-brand (offbrand).
The off-brand set exists to fail: each file violates exactly the rule named
in its filename, so the gate's refusal is specific and testable."""
import os

import brandgate  # noqa: F401  (puts the skill scripts on sys.path)
from brand import BRAND
import brand_docx as D
import brand_pptx as P
import brand_xlsx as X
import brand_web as Wb

CATS = ["Q1", "Q2", "Q3"]
SERIES = {"Sessions": [1200, 1310, 1450], "Visits": [800, 860, 910]}
TABLE = [["Region", "Rate"], ["North", "$142"], ["South", "$138"]]


def build(out):
    os.makedirs(out, exist_ok=True)
    doc = D.new_document("Quarterly Review", "Prepared for the board", "Q3")
    doc.add_heading("Findings", 1)
    doc.add_paragraph("Body copy in the brand ink color, never pure black.")
    D.add_callout(doc, "Key takeaway in a tinted box.")
    t = doc.add_table(rows=3, cols=2)
    for r, row in enumerate(TABLE):
        for c, v in enumerate(row):
            t.cell(r, c).text = v
    D.style_table(t)
    D.finish(doc, os.path.join(out, "review.docx"))

    d = P.new_deck()
    P.title_slide(d, "Quarterly Review", "Board of Directors", "Q3")
    P.section_slide(d, "Where we stand", "Context")
    P.bullets_slide(d, "Three things moved", ["Rate up 3 pts", ("detail", 1)])
    P.kpi_slide(d, "The numbers", [("91%", "Rate"), ("13,910", "Sessions")])
    P.chart_slide(d, "Sessions by quarter", CATS, SERIES)
    P.closing_slide(d)
    P.finish(d, os.path.join(out, "review.pptx"))

    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active
    hr = X.add_title_block(ws, "Quarterly Rates", "Q3")
    for i, row in enumerate(TABLE):
        for j, v in enumerate(row):
            ws.cell(row=hr + i, column=j + 1, value=v)
    X.style_sheet(ws, header_row=hr)
    X.finish(wb, os.path.join(out, "rates.xlsx"))

    html = Wb.page("Quarterly Dashboard", Wb.kpi("91%", "Rate") + Wb.table(TABLE), "Board review")
    Wb.finish(html, os.path.join(out, "dashboard.html"))
    return out


def offbrand(out):
    """Each file breaks one rule - the way real files break them."""
    os.makedirs(out, exist_ok=True)
    from docx import Document
    from docx.shared import RGBColor
    doc = Document()                                     # no logo, default styles
    r = doc.add_paragraph().add_run("Typed in Calibri, pure black, no logo.")
    r.font.name = "Calibri"; r.font.color.rgb = RGBColor(0, 0, 0)
    doc.save(os.path.join(out, "r1-r2-r3-black-calibri-nologo.docx"))

    d = P.new_deck()
    s = P.section_slide(d, "Divider")                    # saturated green...
    s.shapes.add_picture(BRAND.logo("primary"), P.Inches(0.5), P.Inches(0.5), width=P.Inches(2))  # ...with the logo on it
    d.save(os.path.join(out, "r4-logo-on-saturated.pptx"))

    d = P.new_deck()
    P.title_slide(d, "Chart")
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE
    s = d.slides.add_slide(d.slide_layouts[6])
    data = CategoryChartData(); data.categories = CATS
    for k, v in SERIES.items():
        data.add_series(k, v)
    s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, P.Inches(1), P.Inches(1), P.Inches(8), P.Inches(5), data)  # Office picks the colors
    d.save(os.path.join(out, "r5-default-chart-colors.pptx"))

    html = Wb.page("Tint type", "<p>x</p>").replace(f"color:var(--ink)", f"color:{BRAND.BLUE_TINT}")  # tint text on white
    Wb.finish(html, os.path.join(out, "r6-tint-for-type.html"))
    return out
