#!/usr/bin/env python3
"""Renumber top-level <h2> sections sequentially within each chapter file."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = sys.argv[1:] or [p.name for p in sorted(ROOT.glob("0*-*.html"))]

def renumber(path):
    p = ROOT / path
    t = p.read_text(encoding="utf-8")
    n = [0]
    def rep(m):
        attrs = m.group(1) or ""
        inner = re.sub(r"^\s*\d+\.\s*", "", m.group(2)).strip()
        n[0] += 1
        return f"<h2{attrs}>{n[0]}. {inner}</h2>"
    t2 = re.sub(r"<h2(\s[^>]*)?>(.*?)</h2>", rep, t, flags=re.S)
    p.write_text(t2, encoding="utf-8")
    print(f"{path}: {n[0]} h2 renumbered")

for f in FILES:
    renumber(f)
