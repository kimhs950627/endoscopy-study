#!/usr/bin/env python3
"""Build the disease sub-tab navigation for every EGD chapter.

For each chapter listed in data/structure.json:
  1. give every <h2> a stable id (slug of its title without the leading number)
  2. mark sections that received an inline 학회노트 block (data-note="1")
  3. inject <div id="dxnav"> + inline JSON after </header>
  4. tag <body class="dx"> and load assets/dx.js

Running it twice is a no-op (ids and blocks are replaced, not appended).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EGD = ROOT / "egd"
STRUCT = ROOT / "data" / "structure.json"
OUT_JSON = ROOT / "assets" / "dx-nav.json"

MARK_START = "<!-- dxnav:start -->"
MARK_END = "<!-- dxnav:end -->"


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"^\s*\d+(?:-\d+)?\.?\s*", "", text)  # drop "12. " / "12-3. "
    text = re.sub(r"[^0-9A-Za-z가-힣]+", "-", text).strip("-").lower()
    return "s-" + (text[:50] or "sec")


def main() -> None:
    struct = json.loads(STRUCT.read_text(encoding="utf-8"))
    nav_data: dict[str, dict] = {}

    chapters: list[tuple[str, str, str, str]] = []  # file, organ label, nature, chapter no
    for organ in struct["organs"]:
        chapters.append((organ["benign"], organ["label"], "양성", ""))
        chapters.append((organ["malignant"], organ["label"], "악성", ""))
    general = struct["general"]
    chapters.append((general["file"], general["label"], "공통", ""))

    for filename, organ_label, nature, _ in chapters:
        path = EGD / filename
        html = path.read_text(encoding="utf-8")

        # drop a previously injected nav block
        html = re.sub(re.escape(MARK_START) + r".*?" + re.escape(MARK_END), "", html, flags=re.S)

        used: set[str] = set()
        sections = []

        def fix_h2(m: re.Match) -> str:
            attrs, title = m.group(1), m.group(2).strip()
            raw = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", title))
            base = slugify(title)
            sec_id, k = base, 2
            while sec_id in used:
                sec_id = f"{base}-{k}"
                k += 1
            used.add(sec_id)
            note = ' data-note="1"' if 'data-note="1"' in attrs else ""
            attrs = re.sub(r'\s*id="[^"]*"', "", attrs)
            attrs = re.sub(r'\s*data-note="[^"]*"', "", attrs)
            sections.append({"id": sec_id, "title": raw, "note": bool(note)})
            return f'<h2 id="{sec_id}"{note}>' + title + "</h2>"

        html = re.sub(r"<h2([^>]*)>(.*?)</h2>", lambda m: fix_h2(m), html, flags=re.S)

        chapter_no = re.search(r"CHAPTER\s+(\d+)", html)
        nav_data[filename] = {
            "file": filename,
            "organ": organ_label,
            "nature": nature,
            "chapter": chapter_no.group(1) if chapter_no else "",
            "sections": sections,
            "organs": [{"label": o["label"], "benign": o["benign"], "malignant": o["malignant"]} for o in struct["organs"]],
            "general": struct["general"],
        }

        # breadcrumb
        crumb = f"EGD · {organ_label} {nature}" if nature != "공통" else "EGD · 총론"
        html = re.sub(r'<span class="chap">.*?</span>', f'<span class="chap">{crumb}</span>', html, count=1, flags=re.S)

        # body marker + script tag
        if re.search(r"<body[^>]*>", html):
            html = re.sub(r"<body([^>]*)>", lambda m: "<body" + re.sub(r'\s*class="[^"]*"', "", m.group(1)) + ' class="dx">', html, count=1)
        if "assets/dx.js" not in html:
            html = html.replace("</body>", '<script src="../assets/dx.js"></script>\n</body>')

        payload = json.dumps(nav_data[filename], ensure_ascii=False, separators=(",", ":"))
        block = (
            f"{MARK_START}\n"
            f'<div id="dxnav"></div>\n'
            f'<script type="application/json" id="dx-data">{payload}</script>\n'
            f"{MARK_END}\n"
        )
        if "</header>" in html:
            html = html.replace("</header>", "</header>\n" + block, 1)
        else:
            html = re.sub(r"(<body[^>]*>)", r"\1\n" + block, html, count=1)

        path.write_text(html, encoding="utf-8")
        print(f"{filename:26} {len(sections):3} sections")

    OUT_JSON.write_text(json.dumps(nav_data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
