import argparse
import sys

import brandgate  # noqa: F401
from brandgate import samples


def main():
    ap = argparse.ArgumentParser(prog="brandgate", description="nothing ships until it passes the brand check")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="build on-brand samples").add_argument("out", nargs="?", default="out/onbrand")
    sub.add_parser("offbrand", help="build the counterexamples that must be refused").add_argument("out", nargs="?", default="out/offbrand")
    sub.add_parser("check", help="run the gate on a directory").add_argument("dir")
    a = ap.parse_args()
    if a.cmd == "build":
        print("built on-brand samples ->", samples.build(a.out))
    elif a.cmd == "offbrand":
        print("built off-brand counterexamples ->", samples.offbrand(a.out))
    else:
        from brand_check import main as check
        sys.exit(check(["brand_check", a.dir]))


if __name__ == "__main__":
    main()
