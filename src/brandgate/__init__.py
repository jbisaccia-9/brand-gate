"""brand-gate: a deliverable does not ship until it passes the brand check.

The skill lives in skill/brand-style/ (installable on its own); this package
is the harness around it - sample builds, the deliberately off-brand
counterexamples, and the gate that must refuse them.
"""
import os
import sys

SKILL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "skill", "brand-style")
SCRIPTS = os.path.join(SKILL, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
