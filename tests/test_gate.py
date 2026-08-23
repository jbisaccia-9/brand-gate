import os
import subprocess
import sys

import brandgate  # noqa: F401
from brandgate import samples
from brand import BRAND
import brand_check as C

PY = sys.executable


def test_onbrand_passes(tmp_path):
    out = samples.build(str(tmp_path / "on"))
    results = C.grade(out)
    assert len(results) == 4
    assert all(v == [] for v in results.values()), results


def test_each_offbrand_file_fails_its_named_rule(tmp_path):
    out = samples.offbrand(str(tmp_path / "off"))
    results = C.grade(out)
    assert len(results) == 4
    for name, fails in results.items():
        # filename encodes the rules it violates: r1-r2-r3-..., r4-..., etc.
        wanted = {tok.upper() for tok in name.split("-") if tok[:1] == "r" and tok[1:2].isdigit()}
        got = {f.split()[0] for f in fails}
        assert wanted <= got, (name, fails)


def test_cli_refuses_offbrand(tmp_path):
    out = samples.offbrand(str(tmp_path / "off"))
    rc = subprocess.run([PY, "-m", "brandgate", "check", out], capture_output=True, text=True)
    assert rc.returncode == 1
    assert "BRAND GATE: FAILED" in rc.stdout
    assert os.path.exists(os.path.join(out, "grading.json"))


def test_tokens_are_the_single_source():
    assert BRAND.INK != "#000000"
    assert BRAND.CHART_SERIES[0] == BRAND.BLUE
    assert BRAND.fonts["heading"] != BRAND.fonts["body"]   # the Medium-vs-Bold gotcha is structural


def test_unused_template_styles_do_not_fail_a_clean_doc(tmp_path):
    """python-docx's default template ships a Courier 'Macro Text' style nobody
    uses. The first run of this gate failed its own on-brand sample on that
    style; the checker now grades only what text resolves to."""
    import brand_docx as D
    doc = D.new_document("t")
    doc.add_paragraph("x")
    p = D.finish(doc, str(tmp_path / "t.docx"))
    assert C.check_docx(p) == []
