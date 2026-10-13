#!/usr/bin/env python3
"""Delete images under assets/img not referenced by any root *.html, then report size."""
import re, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
used = set()
for f in ROOT.glob("*.html"):
    t = f.read_text(encoding="utf-8", errors="ignore")
    for m in re.findall(r'(assets/img/[^"\')\s>]+)', t):
        used.add(m)

IMG = ROOT / "assets" / "img"
total = kept = removed = 0
removed_bytes = 0
for f in IMG.rglob("*"):
    if not f.is_file():
        continue
    total += 1
    rel = f.relative_to(ROOT).as_posix()
    if rel in used:
        kept += 1
    else:
        removed_bytes += f.stat().st_size
        f.unlink()
        removed += 1

# remove empty dirs
for d in sorted([p for p in IMG.rglob("*") if p.is_dir()], reverse=True):
    if not any(d.iterdir()):
        d.rmdir()

print(f"images: total={total} kept={kept} removed={removed}")
print(f"freed: {removed_bytes/1e6:.1f} MB")
