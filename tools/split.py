#!/usr/bin/env python3
"""Split each chapter digest into per-source-page markdown files for easier reading."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIG = ROOT / "work" / "digest"
OUT = ROOT / "work" / "pages"

for f in sorted(DIG.glob("*.md")):
    ch = f.stem
    d = OUT / ch
    d.mkdir(parents=True, exist_ok=True)
    text = f.read_text(encoding="utf-8")
    parts = re.split(r"\n---\n## ", text)
    # first part is the chapter title
    for i, p in enumerate(parts[1:], 1):
        title = p.split("\n", 1)[0].strip()
        slug = re.sub(r"[^0-9A-Za-z가-힣]+", "-", title)[:50].strip("-")
        (d / f"{i:02d}-{slug}.md").write_text("## " + p, encoding="utf-8")
    print(f"{ch}: {len(parts)-1} pages -> {d}")
