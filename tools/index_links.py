#!/usr/bin/env python3
"""Parse the EndoTODAY atlas index into per-section link lists (for curation)."""
import re, sys, html as htmllib
from pathlib import Path

IDX = Path(__file__).resolve().parent.parent / "work" / "index_utf8.html"
doc = IDX.read_text(encoding="utf-8", errors="replace")

anchors = [(m.start(), m.group(1)) for m in re.finditer(r'<a name="([^"]+)"', doc)]
anchors.append((len(doc), "__end__"))

for i in range(len(anchors) - 1):
    start, name = anchors[i]
    end = anchors[i + 1][0]
    chunk = doc[start:end]
    links = re.findall(r'href="([^"]+\.html)"', chunk)
    seen, out = set(), []
    for l in links:
        if l in seen:
            continue
        seen.add(l)
        out.append(l)
    print(f"\n=== {name}  ({len(out)} links) ===")
    for l in out:
        print("  " + l)
