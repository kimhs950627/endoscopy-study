#!/usr/bin/env python3
"""Validate workbook HTML: referenced images exist, and required blocks are present."""
import re

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EGD = ROOT / "egd"
FILES = sorted(p for p in EGD.glob("*.html") if p.name not in {"book.html", "conference-notes.html", "index.html"})


def check(f: Path) -> dict:
    t = f.read_text(encoding="utf-8")
    imgs = re.findall(r'<img[^>]+src="([^"]+)"', t)
    missing = [s for s in imgs if not s.startswith("http") and not (f.parent / s).resolve().exists()]
    return dict(
        file=f.name,
        imgs=len(imgs),
        missing=missing,
        figures=t.count("<figure"),
        tblwrap=t.count("tblwrap"),
        quiz_blocks=t.count('class="quiz"'),
        questions=t.count('class="q"'),
        rx=t.count('class="rx"'),
    )


def main() -> None:
    bad = 0
    for f in FILES:
        r = check(f)
        flag = f"  MISSING={len(r['missing'])}" if r["missing"] else ""
        bad += len(r["missing"])
        print(
            f"{r['file']:28} imgs={r['imgs']:4} fig={r['figures']:3} tbl={r['tblwrap']:2} "
            f"rx={r['rx']:3} quiz={r['quiz_blocks']} q={r['questions']:3}{flag}"
        )
        for m in r["missing"]:
            print("      x " + m)
    print(f"\n{len(FILES)} chapters · {bad} missing images")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
