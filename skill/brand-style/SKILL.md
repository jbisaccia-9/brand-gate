---
name: brand-style
description: "Applies the Northlight brand identity — approved fonts, the brand palette, and full-color logo artwork — to every deliverable file. Use this skill automatically and without being asked whenever producing a Word document, PowerPoint deck, Excel workbook, PDF, HTML page, dashboard, chart, or image for Northlight. Reports, memos, letters, board decks, one-pagers, proposals, policies, briefs, trackers, and scorecards all qualify. Trigger even when the user says nothing about branding, style, fonts, colors, or logos — branding is the default, not a request. Also use when asked to look up a brand color or hex value, restyle or clean up an existing file, check whether something is on brand, or fix a document that looks generic or off-brand. Do not apply to Markdown, Python, JSON, YAML, CSV, or source code files."
---

<!-- Northlight is a fictional organization. This file is a shell: the structure
     of a production brand skill with every identity value replaced. Swap
     assets/tokens.json, the logo files, and the voice section for your own. -->

# Northlight Brand Style

Every file that leaves this workspace and could be seen by a colleague, client,
or board member should look like Northlight made it. That is the whole job of
this skill: turn "a document" into "a Northlight document" without the user
having to ask.

Source of truth: `assets/tokens.json`. The palette, fonts, and logo files are
loaded from it — never paste hex codes into a builder.

## Apply by default

Brand these without being asked: `.docx` `.pptx` `.xlsx` `.pdf` `.html` and any
chart or image that will be embedded in them.

Leave these alone: `.md` `.py` `.json` `.yaml` `.csv` `.txt`, source code, and
config files. They're plumbing, not deliverables. If a Markdown file is a draft
that will *become* a Word doc or deck, brand the final artifact, not the draft.

The only reason to skip branding on a supported format is the user explicitly
saying so ("plain," "no branding," "unstyled"). Don't ask permission first;
produce the branded version and mention it in one line at the end.

## The rules that matter most

These are the ones that get violated, in the order they get violated. Each has
a number because `scripts/brand_check.py` enforces it by that number.

1. **R1 — Body text is Ink `#2B2B2B`, never pure black.** The guide names one
   text color and that's it.
2. **R3/R4 — The logo appears in full color, on a light surface.**
   `BRAND.logo("primary")` is the default everywhere, and color artwork needs a
   light background — so **design the surface around the logo, not the other
   way round**. Title slides, closing slides, letterheads, and page headers are
   white or Paper `#F7F7F5`; brand presence comes from Blue headings plus a
   green/amber accent band. Don't reach for `logo("reversed")` to make a dark
   layout work — change the background. Reversed is the exception, for a dark
   photograph or a supplied template you can't alter.
3. **R4 — Never put the color logo on a saturated fill.** Blue or Green behind
   the primary artwork closes up the mark's white channels and kills the
   wordmark. If a surface must be saturated (section dividers), leave the logo
   off entirely rather than knocking it out.
4. **Never modify the logo** — no stretching, recoloring, dropping the wordmark,
   adding shadows. Use the bundled files as-is and set *one* dimension so the
   aspect ratio is preserved. Minimum 1 inch wide.
5. **Stone `#7A7A78` is for physical swag.** In documents it's acceptable for
   captions and footers only — never as a chart or accent color when a primary
   color would do.
6. **R6 — The tint palette is for fills, never for type.** `#DCE8F5` text on
   white is unreadable.
7. **R5 — Charts follow the series order** in `BRAND.CHART_SERIES`
   (blue → green → amber → lilac → rose → clay). Don't let Office pick.

## Locate the toolkit first

The tokens, logo artwork, and builder scripts ship alongside this file. Normally
they sit right next to it in the installed skill directory; they may instead
live in a working folder. Locate them before doing anything else:

```python
import glob, os, sys

ROOTS = [os.path.expanduser("~/.claude/skills"), os.getcwd(), "/tmp",
         *glob.glob("/sessions/*/mnt")]
# Depth-bounded globs rather than a recursive walk: skill caches nest deep and
# rglob over them is slow enough to feel broken. Fixed-depth globs never
# enumerate the whole tree.
found = [p for root in ROOTS for d in range(7)
         for p in glob.glob(os.path.join(root, *(["*"] * d), "brand-style",
                                         "scripts", "brand.py"))]
# The marker file is the test, not the directory name: some locations hold a
# copy of this SKILL.md with no assets beside it.
roots = sorted({os.path.dirname(os.path.dirname(p)) for p in found})
SKILL = roots[0]
sys.path.insert(0, SKILL + "/scripts")
```

A valid library has `scripts/` (the builders + checker) and `assets/`
(`tokens.json`, `logo-primary.png`, `logo-reversed.png`).

If `roots` comes up empty, the toolkit isn't on this machine — say so plainly
rather than improvising. You can still apply the palette by hex for HTML, but
you cannot produce a properly branded Office file without the logo artwork.
Quietly shipping default fonts and no logo is worse than telling the user the
library is missing.

Treat the library as read-only; everything here writes only to the output path
you're given.

## How to build each format

All scripts live in `scripts/`. Every builder ends with `finish()`, which saves
and then **reopens** the file — a malformed part fails at write time on your
machine, not on the recipient's. Don't hand-roll a `save()`.

### Word

```python
from brand_docx import new_document, finish, style_table, add_callout

doc = new_document("Quarterly Review", "Prepared for the board", "Q3")
doc.add_heading("Findings", 1)          # already Blue, heading family
doc.add_paragraph("Body copy.")          # already Ink at 11pt
add_callout(doc, "Key takeaway in a tinted box.")
t = doc.add_table(rows=2, cols=3); ...; style_table(t)
finish(doc, "out.docx")
```

`new_document()` rewrites the built-in styles, so plain python-docx calls come
out branded. `header="letterhead"` (default) is a compact logo-rule-title block
with no page break — right for memos and one-pagers. `header="titlepage"` adds
the break for reports long enough to justify a cover.

### PowerPoint

```python
from brand_pptx import (new_deck, title_slide, section_slide, bullets_slide,
                        kpi_slide, chart_slide, closing_slide, content_slide, finish)

d = new_deck()                                    # 16:9
title_slide(d, "Quarterly Review", "Board of Directors", "Q3")
section_slide(d, "Where we stand", "Context")
bullets_slide(d, "Three things moved", ["Rate up 3 pts", ("detail", 1)])
kpi_slide(d, "The numbers", [("91%", "Rate"), ("13,910", "Sessions")])
chart_slide(d, "Sessions by quarter", ["Q1","Q2"], {"2026": [1200, 1310]})
closing_slide(d)
finish(d, "deck.pptx")
```

`chart_slide()` makes a *native* PowerPoint chart that stays editable — prefer
it over pasting a matplotlib image. For anything custom, `content_slide()`
returns `(slide, content_top)` with the branded header already drawn.

Title and closing slides are light with the color logo and a green band;
section dividers are full-bleed Green with no logo. That alternation gives a
deck rhythm — keep logo-bearing surfaces light and let saturated fills carry
type only.

### Excel

```python
from brand_xlsx import add_title_block, style_sheet, finish

hr = add_title_block(ws, "Quarterly Rates", "Q3")   # returns the header row
style_sheet(ws, header_row=hr, number_format="#,##0")
finish(wb, "rates.xlsx")
```

Call `add_title_block` *before* `style_sheet` and pass the row it returns.
Excel can't embed fonts; if exact typography matters, deliver a PDF too.

### HTML, dashboards, and PDF

```python
from brand_web import page, kpi, table, finish

html = page("Quarterly Dashboard", body_html, subtitle="Board review")
```

`page()` returns one self-contained file with the logo base64-embedded — no
external requests, so it survives being emailed around. Use the `.b-*` classes
(`b-card`, `b-kpi`, `table.b`) rather than inventing styling. For PDFs, build
the HTML and print it (the stylesheet has a print block), or convert a
`.docx`/`.pptx`.

## Fonts

| Use | Family name |
|---|---|
| Body copy | `Inter` |
| Bold/emphasis | `Inter` with bold on — *same* family |
| Headings | `Inter Medium` — a **separate** family name |

That last row is the gotcha that survives every brand: asking for the body
family + bold gives you Bold, not Medium. Headings must name the heading family
explicitly.

Licensing matters more than it looks. Inter is OFL — safe to bundle and embed.
Many corporate fonts are *preview-and-print* licensed: embedding is permitted
and files render correctly for recipients, but some Word builds open such
files read-only. If a recipient reports a read-only file, that's the cause —
disable embedding for editable drafts or send a PDF.

## Palette

```
Primary      Blue #1F5AA6   Green #2E9E6B   Amber #F2B84B
Background   Paper #F7F7F5  Blue tint #DCE8F5  Green tint #D7EDE3  Amber tint #FBEFD2
Text         Ink #2B2B2B
Secondary    Clay #E8C9B0   Rose #E9B3B3   Lilac #CFC3E0
Swag only    Stone #7A7A78
```

Import from `brand` (`BRAND.BLUE`, `BRAND.hex("BLUE")`, `BRAND.rgb("BLUE")`)
rather than pasting hex, so a palette correction propagates. Blue leads, green
and amber support, secondary pastels accent. A document that is mostly
blue-and-white with amber emphasis reads correctly; one that gives equal weight
to all seven colors doesn't.

## Voice, when writing the words too

<!-- Replace with your guide's register, required trademarks, and tagline. -->
Plain, warm, concrete. Write for the reader who has thirty seconds. Product
names carry their mark on first use. The tagline is set in lowercase.

## Before delivering

Cheap to fix, expensive to send:

- Any pure black `#000000` text? Should be Ink.
- Is the logo the full color version, on a light background? A white knockout
  logo means a surface got built dark that shouldn't have.
- Color logo sitting on Blue or Green? Lighten the background or drop the logo.
- Logo distorted, or under 1 inch wide?
- Headings using the body family where the heading family was intended?
- Chart colors off the series order, or an Office default palette?
- Does the file actually open? `finish()` reopens it for you.

All of that is machine-checkable, and **it is the gate**:

```bash
python scripts/brand_check.py <directory-of-outputs>
```

It prints PASS/FAIL per file with the rule number that failed, writes
`grading.json` beside the outputs, and exits non-zero if anything is
off-brand. Run it on anything headed outside the organization.
