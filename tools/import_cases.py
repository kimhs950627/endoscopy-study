#!/usr/bin/env python3
"""Import the 100-case EGC/esophageal-cancer atlas into the workbook.

Source (local, not committed):
  D:/pdf_to_cards/100증례 조기위암, 식도암 감별_vflatScan.pdf
  D:/pdf_to_cards/out/cards.json   (case → pages / images mapping)

Output:
  data/cases.json                  normalized fields for the web/PDF chapter
  assets/img/cases/pNNN_x.jpg      cropped case images

Text is re-extracted from the PDF (natural reading order) instead of reusing the
scrambled text in cards.json; only the page/image mapping comes from cards.json.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pymupdf
from PIL import Image

SRC_DIR = Path("/mnt/d/pdf_to_cards")
PDF = SRC_DIR / "100증례 조기위암, 식도암 감별_vflatScan.pdf"
CARDS = SRC_DIR / "out" / "cards.json"

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "data" / "cases.json"
OUT_IMG = ROOT / "assets" / "img" / "cases"
MAX_W, Q = 820, 82   # keep the repo and the PDF small; 3-up on A4 needs ~800px

NOISE = re.compile(
    r"^(?:"
    r"\d{1,3}|[a-zA-Z]{1,2}|LO|CO|or|\*\*|"
    r"그림\s*\d+[a-z]?|그 밖의 해답|난이도|Lesion\s*\d|해답"
    r")$"
)
FIG_PREFIX = re.compile(r"^그림\s*\d*[a-z]?\s*")
TAGLINE = re.compile(r"^(\d{3})\s+(#.*)$")
HP_FIXES = [
    (r"음\s*성", "음성"),
    (r"양\s*성", "양성"),
    (r"제\s*균", "제균"),
    (r"미\s*시\s*행", "미시행"),
    (r"상\s*세\s*불\s*명", "상세불명"),
    (r"\[\s*Helicobacter\s*", "[Helicobacter "),
    (r"\s*\]", "] "),
    (r"\s+,", ","),
]


def clean_lines(text: str) -> list[str]:
    out = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line or NOISE.match(line):
            continue
        line = line.lstrip("|").strip()
        line = re.sub(r"^[\d|\s]*(?=그림)", "", line)
        line = FIG_PREFIX.sub("", line).strip()
        # table-cell debris and figure captions that survived the prefix strip
        if not line or re.fullmatch(r"[\d|*.\s]+", line) or line.startswith("그림"):
            continue
        out.append(line)
    return out


def join_lines(lines: list[str]) -> list[str]:
    """Join hard-wrapped lines into paragraphs (Korean wraps mid-word, no hyphen)."""
    paras, buf = [], ""
    for line in lines:
        buf += line
        if re.search(r"[.?!。:]\s*$", line):
            paras.append(buf.strip())
            buf = ""
    if buf.strip():
        paras.append(buf.strip())
    return [p for p in paras if p]


def fix_header(s: str) -> str:
    for pat, rep in HP_FIXES:
        s = re.sub(pat, rep, s)
    return re.sub(r"\s{2,}", " ", s).strip()


def parse_case(doc, card) -> dict | None:
    text = "\n".join(doc[p - 1].get_text("text") for p in card["pages"])
    if "해답" not in text:
        return None
    head_raw, ans_raw = text.split("해답", 1)

    head_lines = clean_lines(head_raw)
    ans_lines = clean_lines(ans_raw)

    # drop the repeated "증례 NNN" heading and parse the demographic line
    head_lines = [l for l in head_lines if not re.match(r"^증례\s*\d+", l)]
    demo = next((l for l in head_lines if re.match(r"^\d{2}대", l)), "")

    # on some pages the answer key sits above the "해답" heading
    pre_summary = ""
    for line in head_lines:
        if re.match(r"^[①-⑩0-9,\s]+에?\s*조기암", line):
            pre_summary = line
            break
    rest = [l for l in head_lines if l != demo and l != pre_summary]
    history = fix_header(" ".join(rest))

    tags: list[str] = []
    body_lines: list[str] = []
    for line in ans_lines:
        m = TAGLINE.match(line)
        if m:
            tags = [t.strip("# ") for t in m.group(2).split("#") if t.strip()]
            continue
        body_lines.append(line)

    summary = pre_summary
    if not summary and body_lines and re.match(r"^[①-⑩0-9,\s]+에?\s*조기암", body_lines[0]):
        summary = body_lines.pop(0)

    paras = join_lines(body_lines)
    path = next((p for p in paras if p.startswith("병리검사")), "")
    body = [p for p in paras if p != path]

    body_text = " ".join(body)
    is_esophagus = re.search(r"식도|EGJ|편평상피|편평세포|이완불능|식도암", body_text) is not None
    organ = "식도" if is_esophagus else "위"

    return {
        "case": card["case"],
        "pages": card["pages"],
        "imgs": card["imgs"],
        "age_sex": demo,
        "history": history,
        "summary": summary,
        "body": body,
        "pathology": path,
        "tags": tags,
        "organ": organ,
    }


def main() -> None:
    cards = json.loads(CARDS.read_text(encoding="utf-8"))
    doc = pymupdf.open(PDF)
    OUT_IMG.mkdir(parents=True, exist_ok=True)

    cases, skipped = [], 0
    for card in cards:
        parsed = parse_case(doc, card)
        if not parsed:
            skipped += 1
            continue
        for name in card["imgs"]:
            src = SRC_DIR / "out" / "img" / name
            dst = OUT_IMG / name
            if not src.exists():
                continue
            im = Image.open(src).convert("RGB")
            if im.width > MAX_W:
                im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
            im.save(dst, "JPEG", quality=Q, optimize=True)
        cases.append(parsed)

    OUT_JSON.write_text(json.dumps(cases, ensure_ascii=False, indent=1), encoding="utf-8")
    eso = sum(1 for c in cases if c["organ"] == "식도")
    print(f"{len(cases)} cases ({eso} 식도 / {len(cases) - eso} 위), skipped {skipped}")
    print(f"images: {len(list(OUT_IMG.glob('*.jpg')))} → {OUT_IMG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
