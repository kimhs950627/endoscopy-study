#!/usr/bin/env python3
"""Validate chapter HTML: referenced images exist, and required blocks are present."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = sorted(p for p in ROOT.glob("*.html"))

def check(f):
    t = f.read_text(encoding="utf-8")
    imgs = re.findall(r'<img[^>]+src="([^"]+)"', t)
    missing = [s for s in imgs if not s.startswith("http") and not (ROOT / s).exists()]
    n_fig = t.count("<figure")
    n_tblwrap = t.count("tblwrap")
    n_q = t.count('class="q"')
    n_rx = t.count('class="rx"')
    n_quiz = t.count('class="quiz"')
    return dict(file=f.name, imgs=len(imgs), missing=missing, figures=n_fig,
                tblwrap=n_tblwrap, quiz_blocks=n_quiz, questions=n_q, rx=n_rx)

for f in FILES:
    r = check(f)
    flag = ""
    if r["missing"]:
        flag += f"  MISSING={len(r['missing'])}"
    print(f"{r['file']:28} imgs={r['imgs']:4} fig={r['figures']:3} tbl={r['tblwrap']:2} rx={r['rx']:3} quiz={r['quiz_blocks']} q={r['questions']:3}{flag}")
    for m in r["missing"]:
        print("      x " + m)
