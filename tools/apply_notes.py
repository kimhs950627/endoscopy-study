#!/usr/bin/env python3
"""Insert OneNote-derived notes inline into the disease section they belong to.

notes/notes.map.json declares {file, chapter, h2, label}. Each markdown file is rendered
and dropped immediately after the matching <h2> section (before the next <h2>), wrapped in
markers so a re-run replaces it instead of appending a duplicate.
"""
from __future__ import annotations

import html as html_mod
import json
import re
from pathlib import Path

from build_notes import render_md, split_front_matter

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "notes" / "notes.map.json"


def norm(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"^\s*\d+(?:-\d+)?\.?\s*", "", s)
    return re.sub(r"[\s·\-–—:()'\"]", "", s).lower()


def block_html(meta: dict, body_html: str, slug: str) -> str:
    label = meta.get("label", meta.get("title", ""))
    return (
        f'<!-- note:{slug}:start -->\n'
        f'<section class="note-inline" id="note-{slug}" data-slug="{slug}">\n'
        f'  <div class="note-h"><span class="tag">학회노트</span>'
        f"<b>{html_mod.escape(label)}</b>"
        f'<span class="upd">{html_mod.escape(meta.get("updated", ""))} · OneNote</span></div>\n'
        f"{body_html}\n"
        f"</section>\n"
        f"<!-- note:{slug}:end -->\n"
    )


def main() -> None:
    entries = json.loads(MAP.read_text(encoding="utf-8"))

    # strip every previously injected block first (chapter may have changed mapping)
    chapters: dict[str, str] = {}
    for e in entries:
        rel = e["chapter"]
        if rel not in chapters:
            chapters[rel] = (ROOT / rel).read_text(encoding="utf-8")

    for rel in chapters:
        chapters[rel] = re.sub(r"<!-- note:.*?:start -->.*?<!-- note:.*?:end -->\n?", "", chapters[rel], flags=re.S)

    inserted = 0
    for e in entries:
        rel = e["chapter"]
        md_path = ROOT / e["file"]
        meta, body_md = split_front_matter(md_path.read_text(encoding="utf-8"))
        meta = {**meta, "label": e.get("label", meta.get("title", ""))}
        body_html, _ = render_md(body_md)
        slug = Path(e["file"]).stem
        block = block_html(meta, body_html, slug)

        doc = chapters[rel]
        target = norm(e["h2"])

        # locate the matching <h2 ...>title</h2>
        hit = None
        for m in re.finditer(r"<h2([^>]*)>(.*?)</h2>", doc, flags=re.S):
            if norm(m.group(2)).startswith(target) or target in norm(m.group(2)):
                hit = m
                break
        if hit is None:
            print(f"  ! anchor not found: {e['h2']} in {rel}")
            continue

        # mark the heading so the nav can show a dot
        head_open = hit.group(1)
        new_open = head_open if 'data-note="1"' in head_open else head_open + ' data-note="1"'
        doc = doc[: hit.start()] + f"<h2{new_open}>{hit.group(2)}</h2>" + doc[hit.end() :]

        # find the end of this section: next <h2, or the chapter footer
        after = doc.find("<h2", hit.start() + 4)
        footer = doc.find("<footer", hit.start() + 4)
        ends = [x for x in (after, footer) if x != -1]
        cut = min(ends) if ends else len(doc)
        doc = doc[:cut] + block + doc[cut:]

        chapters[rel] = doc
        inserted += 1

    for rel, doc in chapters.items():
        (ROOT / rel).write_text(doc, encoding="utf-8")
        print(f"  updated {rel}")
    print(f"inserted {inserted} note blocks")


if __name__ == "__main__":
    main()
