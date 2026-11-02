#!/usr/bin/env python3
"""Merge all EGD chapters into egd/book.html (single document for reading + PDF export).

Sources
  egd/00-총론.html … egd/06-십이지장-악성.html   chapter bodies (<main>…</main>)
  (학회노트는 notes/*.md → tools/apply_notes.py 로 각 장의 해당 절 안에 삽입된다)

Also stamps the "최종 갱신" date on egd/index.html so the cover never lies.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EGD = ROOT / "egd"

ORDER = [
    "00-총론.html",
    "01-식도-양성.html",
    "02-식도-악성.html",
    "03-위-양성.html",
    "04-위-악성.html",
    "05-십이지장-양성.html",
    "06-십이지장-악성.html",
    "07-감별증례.html",
]



def chapter_inner(path: Path) -> str:
    t = path.read_text(encoding="utf-8")
    m = re.search(r"<main>(.*)</main>", t, re.S)
    if not m:
        raise SystemExit(f"no <main> in {path.name}")
    body = m.group(1)
    body = re.sub(r'<a class="back".*?</a>', "", body, flags=re.S)
    body = re.sub(r"<footer>.*?</footer>", "", body, flags=re.S)
    return body.strip()


def notes_inner(path: Path) -> str:
    t = path.read_text(encoding="utf-8")
    m = re.search(r'<article class="notes-body">(.*?)</article>', t, re.S)
    if not m:
        raise SystemExit(f"no notes-body in {path.name}")
    body = m.group(1)
    body = re.sub(r'<div class="notes-head">.*?</div>\s*</div>', "", body, count=1, flags=re.S)
    body = re.sub(r'<div class="srcbox">.*?</div>', "", body, flags=re.S)
    body = re.sub(r"<footer.*?</footer>", "", body, flags=re.S)
    body = re.sub(r'<p class="lead">.*?</p>', "", body, count=1, flags=re.S)
    body = re.sub(r'<div class="updated">.*?</div>', "", body, flags=re.S)
    body = body.replace('<div class="notes-head">', "")
    return body.strip()


COVER = """<section class="bookcover">
  <div class="kicker">EGD · UPPER GI · WORKBOOK 01</div>
  <h1>상부위장관 내시경<br>워크북</h1>
  <p class="lead">총론 · 식도(양성/악성) · 위(양성/악성) · 십이지장(양성/악성)</p>
  <p class="mut">이준행 교수님의 EndoTODAY(endotoday.com) 강의·아틀라스 기반 개인 학습용 정리.
  원저작물의 권리는 원저자에게 있으며, 상업적 이용·재배포를 하지 않는다.</p>
  <p class="mut">'학회노트' 표시가 붙은 부분은 본인 OneNote 학회 정리를 옮긴 것. 약제는 실제 처방 약어로 표기.</p>
  <p class="mut">최종 갱신 {stamp}</p>
</section>"""


def main() -> None:
    stamp = date.today().isoformat()
    parts = [COVER.format(stamp=stamp)]

    for i, name in enumerate(ORDER):
        inner = chapter_inner(EGD / name)
        cls = "bookchapter" + ("" if i == 0 else " newpage")
        parts.append(f'<section class="{cls}">\n{inner}\n</section>')


    doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>상부위장관 내시경 워크북 (합본)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/book.css">
<style>
  body{{background:#EFEBE1}}
  .book{{max-width:900px;margin:0 auto;background:#FFFDF8;padding:0 38px 60px;box-shadow:0 0 50px -12px rgba(21,33,29,.25)}}
  .bookcover{{padding:110px 0 44px;border-bottom:3px solid var(--acc)}}
  .bookcover .kicker{{color:var(--acc);font-family:var(--mono);font-size:12px;letter-spacing:.22em}}
  .bookcover h1{{font-family:var(--serif);font-weight:400;font-size:clamp(34px,5vw,58px);margin:16px 0 0;line-height:1.1}}
  .bookcover .lead{{font-family:var(--serif);font-size:19px;color:#2B3A34;margin:18px 0 0}}
  .bookcover .mut{{color:var(--mut);font-size:13.5px;margin:6px 0 0}}
  .bookchapter{{padding-top:10px}}
  .bookchapter.newpage{{border-top:1px solid var(--line);margin-top:40px;padding-top:34px}}
  .note + .note{{margin-top:46px;padding-top:30px;border-top:2px solid var(--ink)}}
  .note-meta{{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin:0 0 6px}}
  .note-meta .idx{{font-family:var(--mono);font-size:10.5px;letter-spacing:.18em;color:var(--acc)}}
  .note-meta b{{font-family:var(--serif);font-size:15px;color:var(--ink-2)}}
  .note-meta .upd{{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--mut)}}
  .note > h2:first-of-type{{margin-top:10px;border-top:0;padding-top:0}}
  .notes-body h2:first-child{{margin-top:0}}
  @media print{{
    body{{background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
    .book{{max-width:none;box-shadow:none;padding:0}}
    .bookcover{{padding:70px 0 40px}}
    .bookchapter.newpage{{border-top:0;page-break-before:always;margin:0;padding-top:0}}
    .tblwrap{{overflow:visible!important;break-inside:auto}}
    .notes-body .tblwrap{{overflow:visible!important}}
    table{{min-width:0!important;width:100%}}
    th{{white-space:normal!important}}
    th,td{{overflow-wrap:anywhere;word-break:break-word}}
    td img{{width:58px}}
    thead{{display:table-header-group}}
    tr{{break-inside:avoid}}
    figure,.quiz{{break-inside:avoid}}
    .rx,.pf,.pearl,blockquote{{break-inside:auto;
      box-decoration-break:clone;-webkit-box-decoration-break:clone}}
    .rx .t,.pf .t,.pearl .t{{break-after:avoid}}
    p,li,td,th{{orphans:2;widows:2}}
    h2,h3{{break-after:avoid}}
    h1,h2,h3,.chapter-head .no{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
    details>summary{{display:none}}
    details>div.ans{{display:block!important}}
    a{{color:inherit;text-decoration:none}}
  }}
</style>
</head>
<body>
<div class="book">
{chr(10).join(parts)}
</div>
<script>
// 합본: 연습문제 해설을 모두 펼쳐 둔다(화면·PDF 동일).
document.querySelectorAll("details").forEach(function(d){{ d.open = true; }});
</script>
</body>
</html>
"""
    out = EGD / "book.html"
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}  {len(doc):,} chars")

    # stamp the cover date
    cover = EGD / "index.html"
    c = cover.read_text(encoding="utf-8")
    c = re.sub(r'(<time data-updated>)[^<]*(</time>)', rf"\g<1>{stamp}\g<2>", c)
    cover.write_text(c, encoding="utf-8")
    print(f"stamped {cover.relative_to(ROOT)} → {stamp}")


if __name__ == "__main__":
    main()
