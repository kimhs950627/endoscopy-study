#!/usr/bin/env python3
"""Inject a Korean outline (bookmarks) into the printed workbook PDF.

Usage: python3 tools/add_outline.py <in.pdf> <book.html> [out.pdf]

Page mapping is done by scanning the printed text page by page: headings are read
from the merged HTML in document order, then matched sequentially so a repeated
word never jumps backwards.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import pymupdf

NORM = re.compile(r"[^\w가-힣]", re.UNICODE)


def norm(s: str) -> str:
    return NORM.sub("", s).lower()


def headings(html_path: Path) -> list[tuple[int, str]]:
    src = html_path.read_text(encoding="utf-8")
    body = src[src.find('<div class="book">') :]
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    out = []
    for m in re.finditer(r"<(h1|h2|h3)\b[^>]*>(.*?)</\1>", body, re.S):
        level = int(m.group(1)[1])
        text = re.sub(r"<[^>]+>", " ", m.group(2))
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        if text:
            out.append((level, text))
    return out


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    pdf_in = Path(sys.argv[1])
    html_in = Path(sys.argv[2])
    pdf_out = Path(sys.argv[3]) if len(sys.argv) > 3 else pdf_in.with_suffix(".out.pdf")

    doc = pymupdf.open(pdf_in)
    pages = [norm(p.get_text()) for p in doc]
    heads = headings(html_in)
    print(f"{len(heads)} headings · {len(pages)} pages")

    toc: list[list] = []
    cursor = 0
    misses = 0
    for level, text in heads:
        key = norm(text)[:28]
        found = None
        if key:
            for p in range(cursor, len(pages)):
                if key in pages[p]:
                    found = p
                    break
        if found is None:
            # tolerate hyphenation / spacing differences in long headings
            short = norm(text)[:12]
            for p in range(cursor, len(pages)):
                if short and short in pages[p]:
                    found = p
                    break
        if found is None:
            misses += 1
            continue
        cursor = found
        toc.append([level, text, found + 1])

    doc.set_toc(toc)
    doc.save(pdf_out, garbage=3, deflate=True)
    doc.close()
    print(f"outline: {len(toc)} entries, {misses} unmatched → {pdf_out}")


if __name__ == "__main__":
    main()
