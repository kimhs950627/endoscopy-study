#!/usr/bin/env python3
"""Merge all chapters into a single book.html (for screen reading and PDF export)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORDER = ["00-총론.html", "01-식도-양성.html", "02-식도-악성.html", "03-위-양성.html",
         "04-위-악성.html", "05-십이지장-양성.html", "06-십이지장-악성.html"]

def main_inner(path):
    t = path.read_text(encoding="utf-8")
    m = re.search(r"<main>(.*)</main>", t, re.S)
    body = m.group(1)
    body = re.sub(r'<a class="back".*?</a>', "", body, flags=re.S)
    body = re.sub(r"<footer>.*?</footer>", "", body, flags=re.S)
    return body.strip()

cover = """<section class="bookcover">
  <div class="kicker">ENDOTODAY STUDY COMPANION</div>
  <h1>상부위장관 내시경 참고서</h1>
  <p class="lead">총론 · 식도(양성/악성) · 위(양성/악성) · 십이지장(양성/악성)</p>
  <p class="mut">EndoTODAY(endotoday.com, 이준행) 강의·아틀라스 기반 개인 학습용 정리.<br>약제는 실제 처방 약어로 표기.</p>
</section>"""

parts = [cover]
for i, f in enumerate(ORDER):
    inner = main_inner(ROOT / f)
    cls = "bookchapter" + ("" if i == 0 else " newpage")
    parts.append(f'<section class="{cls}">\n{inner}\n</section>')

doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EndoTODAY 참고서 — 상부위장관 내시경 (합본)</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/book.css">
<style>
  body{{background:#eef2f7}}
  .book{{max-width:900px;margin:0 auto;background:#fff;padding:0 34px 60px;box-shadow:0 0 40px rgba(0,0,0,.08)}}
  .bookcover{{padding:90px 0 40px;border-bottom:3px solid var(--acc);text-align:left}}
  .bookcover .kicker{{color:var(--acc);font-weight:800;letter-spacing:.18em;font-size:13px}}
  .bookcover h1{{font-size:clamp(30px,5vw,52px);margin:10px 0;letter-spacing:-.02em}}
  .bookcover .lead{{font-size:19px;color:#33475c;font-weight:600}}
  .bookchapter{{padding-top:10px}}
  .bookchapter.newpage{{border-top:1px solid var(--line);margin-top:36px;padding-top:30px}}
  @media print{{
    body{{background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
    .book{{max-width:none;box-shadow:none;padding:0}}
    .bookchapter.newpage{{border-top:0;page-break-before:always;margin:0;padding-top:0}}
    .tblwrap{{overflow:visible!important;break-inside:auto}}
    table{{min-width:0!important;width:100%}}
    th{{white-space:normal!important}}
    th,td{{overflow-wrap:anywhere;word-break:break-word}}
    td img{{width:58px}}
    thead{{display:table-header-group}}
    tr{{break-inside:avoid}}
    figure,.quiz,.rx,.pf,.pearl,blockquote{{break-inside:avoid}}
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
(ROOT / "book.html").write_text(doc, encoding="utf-8")
print("wrote book.html", len(doc), "chars")
