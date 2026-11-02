#!/usr/bin/env python3
"""Convert a OneNote page (raw MCP/HTML export) into clean workbook markdown.

Usage
    python3 tools/onenote_to_md.py raw.html --out notes/egd-xxxx.md \
        --title "GERD · PPI 내성" --source "OneNote / Books_for_Meds / 위내시경 공부 / <page>"

The MCP `getPageContent(format="html")` output is HTML prefixed with a short
"📄 **title** (HTML Format)" banner; html-format pages from the desktop app work too.
Personal or unrelated material is dropped by DROP_PATTERNS before it can reach the web.
"""
from __future__ import annotations

import argparse
import html as html_mod
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

# Lines matching these never leave OneNote: private finance, identifiers, chatter.
DROP_PATTERNS = [
    r"실손", r"보험", r"적립", r"연금", r"계좌", r"카드값", r"월세", r"대출",
    r"주민등록", r"휴대폰", r"비밀번호",
    r"\d[\d,]*원",  # prices / premiums
]

BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "div"}


class OneNoteParser(HTMLParser):
    """Flatten OneNote's absolutely-positioned HTML into ordered text blocks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple[str, int, str]] = []  # (kind, depth, text)
        self._buf: list[str] = []
        self._kind = "p"
        self._depth = 0
        self._list_depth = 0
        self._in_table = False
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._skip = 0  # inside <style>/<script>/<title>

    # -- helpers -------------------------------------------------------
    def _flush(self) -> None:
        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        self._buf.clear()
        if text:
            self.blocks.append((self._kind, self._depth, text))

    # -- parser hooks --------------------------------------------------
    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "title", "head"):
            self._skip += 1
            return
        if tag in ("ul", "ol"):
            self._list_depth += 1
        elif tag in ("p", "h1", "h2", "h3", "h4"):
            self._flush()
            self._kind, self._depth = "h" if tag.startswith("h") else "p", 0
        elif tag == "li":
            self._flush()
            self._kind, self._depth = "li", max(self._list_depth - 1, 0)
        elif tag == "div":
            self._flush()
            self._kind, self._depth = "p", 0
        elif tag == "table":
            self._flush()
            self._in_table = True
        elif tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            self._cell = []
        elif tag == "br":
            self._buf.append(" ")

    def handle_endtag(self, tag):
        if tag in ("style", "script", "title", "head"):
            self._skip = max(self._skip - 1, 0)
            return
        if tag in ("ul", "ol"):
            self._list_depth = max(self._list_depth - 1, 0)
            self._flush()
        elif tag in ("p", "li", "h1", "h2", "h3", "h4", "div"):
            self._flush()
            self._kind = "p"
        elif tag in ("td", "th"):
            if self._row is not None and self._cell is not None:
                self._row.append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._cell = None
        elif tag == "tr":
            if self._row:
                self.blocks.append(("tr", 0, " | ".join(self._row)))
            self._row = None
        elif tag == "table":
            self._in_table = False

    def handle_data(self, data):
        if self._skip:
            return
        if self._cell is not None:
            self._cell.append(data)
            return
        self._buf.append(data)


def strip_wrapper(raw: str) -> str:
    """Drop the MCP banner and keep the HTML document body."""
    start = raw.find("<html")
    if start > 0:
        raw = raw[start:]
    return raw


def is_dropped(text: str) -> bool:
    return any(re.search(p, text) for p in DROP_PATTERNS)


def to_markdown(parsed: OneNoteParser) -> str:
    out: list[str] = []
    prev_was_row = False
    for kind, depth, text in parsed.blocks:
        if is_dropped(text):
            continue
        if kind == "h":
            out.append(f"\n## {text}\n")
        elif kind == "li":
            out.append(f"{'  ' * depth}- {text}")
        elif kind == "tr":
            cells = [c for c in text.split(" | ")]
            if len(cells) >= 2:
                if not prev_was_row:
                    out.append("| " + " | ".join(cells) + " |")
                    out.append("|" + "|".join("---" for _ in cells) + "|")
                else:
                    out.append("| " + " | ".join(cells) + " |")
            prev_was_row = True
            continue
        elif kind == "p":
            out.append(f"\n{text}\n")

        prev_was_row = False
    md = "\n".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()

    # collapse duplicated blocks (OneNote repeats nested content when flattened)
    seen: set[str] = set()
    kept: list[str] = []
    for line in md.split("\n"):
        key = re.sub(r"[\s\-]", "", line)
        if key and key in seen:
            continue
        seen.add(key)
        kept.append(line)
    return "\n".join(kept)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", help="raw HTML file saved from the OneNote MCP")
    ap.add_argument("--out", required=True, help="markdown file to write")
    ap.add_argument("--title", required=True)
    ap.add_argument("--source", default="OneNote")
    args = ap.parse_args()

    raw = Path(args.raw).read_text(encoding="utf-8", errors="replace")
    parser = OneNoteParser()
    parser.feed(strip_wrapper(raw))
    parser.close()
    body = to_markdown(parser)

    front = (
        "---\n"
        f"title: {args.title}\n"
        f"updated: {date.today().isoformat()}\n"
        f"source: {args.source}\n"
        "---\n\n"
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(front + body + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(body):,} chars)")


if __name__ == "__main__":
    main()
