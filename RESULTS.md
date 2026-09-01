# Results

Generated 2026-09-01 by `scripts/make_results.py` — every block below is captured command output, not prose.

## Unit tests

`python -m pytest -q` — exit 0, OK

```
.....                                                                    [100%]
5 passed in 0.63s
```

## Build on-brand samples

`python -m brandgate build out/onbrand` — exit 0, OK

```
built on-brand samples -> out/onbrand
```

## Gate on the on-brand samples

`python -m brandgate check out/onbrand` — exit 0, OK

```
PASS  dashboard.html
  PASS  rates.xlsx
  PASS  review.docx
  PASS  review.pptx
BRAND GATE: PASSED - 4 file(s) cleared.
```

## Build the off-brand counterexamples

`python -m brandgate offbrand out/offbrand` — exit 0, OK

```
built off-brand counterexamples -> out/offbrand
```

## Gate refuses the counterexamples

`python -m brandgate check out/offbrand` — expected non-zero exit, OK

```
FAIL  r1-r2-r3-black-calibri-nologo.docx  <- R1 pure-black text; R2 unapproved font(s): ['Calibri']; R3 no logo on page 1
  FAIL  r4-logo-on-saturated.pptx  <- R4 logo on saturated fill (slide 1, #2E9E6B)
  FAIL  r5-default-chart-colors.pptx  <- R5 chart series off-order (slide 2): [None, None]
  FAIL  r6-tint-for-type.html  <- R6 tint used for type (#DCE8F5)
BRAND GATE: FAILED - 4 of 4 file(s) are off-brand; do not send.
```
