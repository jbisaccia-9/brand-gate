"""Brand tokens, loaded once from assets/tokens.json.

Import colors from here (BRAND.BLUE, BRAND.hex("BLUE"), BRAND.rgb("BLUE"))
instead of pasting hex codes, so a palette correction propagates everywhere.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")


class _Brand:
    def __init__(self, tokens):
        self.tokens = tokens
        self.name = tokens["brand"]
        self.fonts = tokens["fonts"]
        self.colors = {}                      # flat name -> "#RRGGBB"
        self.groups = {}                      # name -> group ("primary", "text", ...)
        for group, items in tokens["colors"].items():
            for k, v in items.items():
                self.colors[k] = v.upper()
                self.groups[k] = group
        self.CHART_SERIES = [self.colors[k] for k in tokens["chart_series"]]
        self.APPROVED_FONTS = {self.fonts["body"], self.fonts["heading"]}

    def __getattr__(self, key):               # BRAND.BLUE -> "#1F5AA6"
        try:
            return self.colors[key]
        except KeyError:
            raise AttributeError(key)

    def hex(self, key):
        return self.colors[key]

    def rgb(self, key):
        h = self.colors[key].lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def by_group(self, group):
        return [v for k, v in self.colors.items() if self.groups[k] == group]

    def logo(self, variant="primary"):
        return os.path.join(ASSETS, self.tokens["logo"][variant])


with open(os.path.join(ASSETS, "tokens.json")) as _f:
    BRAND = _Brand(json.load(_f))

# Convenience aliases used by the checker.
PRIMARY = set(BRAND.by_group("primary"))
TINTS = set(BRAND.by_group("background"))
TEXT = BRAND.INK
