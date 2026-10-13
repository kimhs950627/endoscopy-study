#!/usr/bin/env python3
"""Assemble a chapter HTML from fragment files (inner sections) + per-chapter meta."""
import sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRAG = ROOT / "work" / "frag"

META = {
    "01-식도-양성": dict(
        no="01", title="식도 양성 질환",
        lead="역류·감염·호산구·부식성 식도염부터 Barrett식도, 정맥류, 게실, 이완불능증, SMT·유두종, 열공탈장까지. 증상이 애매하고 소견이 겹치는 병이 많아 <b>형태 기술과 감별</b>이 진단의 핵심이다.",
        prev=("00-총론.html", "◀ 이전"), next=("02-식도-악성.html", "다음 ▶"),
        frags=["01.A", "01.B", "01.C"]),
    "03-위-양성": dict(
        no="03", title="위 양성 질환",
        lead="정상 해부와 관찰법, H. pylori, 만성위염, 소화성궤양(출혈·Forrest), 용종·선종, 점막하종양(GIST·NET), GAVE·문맥압항진위병증·정맥류, 이물·PEG 등 위의 양성 질환을 망라한다.",
        prev=("02-식도-악성.html", "◀ 이전"), next=("04-위-악성.html", "다음 ▶"),
        frags=["03.A", "03.B", "03.C"]),
    "04-위-악성": dict(
        no="04", title="위 악성 질환",
        lead="조기위암 육안분류와 ESD 적응(eCura), 진행위암 Borrmann 분류, Lauren/WHO 조직형, TNM 8판 병기, GEJ암, MALT림프종·림프종, 그리고 수술·항암·표적치료까지.",
        prev=("03-위-양성.html", "◀ 이전"), next=("05-십이지장-양성.html", "다음 ▶"),
        frags=["04.A", "04.B", "04.C"]),
}

SKEL = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CHAPTER {no} · {title} — EndoTODAY 참고서</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/book.css">
</head>
<body>
<header class="topbar">
  <a class="brand" href="index.html">EndoTODAY 참고서</a>
  <span class="chap">CHAPTER {no} · {title}</span>
  <span class="nav"><a href="{prevf}">{prevl}</a><a href="index.html">목차</a><a href="{nextf}">{nextl}</a></span>
</header>
<div class="layout">
  <nav class="toc"><div class="ttl">목차</div><div id="toc"></div></nav>
  <main>
    <div class="chapter-head">
      <div class="no">CHAPTER {no}</div>
      <h1>{title}</h1>
      <p class="lead">{lead}</p>
    </div>
{body}
    <a class="back" href="index.html">← 목차로</a>
    <footer>출처: EndoTODAY(endotoday.com, 이준행) 강의·아틀라스 기반 개인 학습용 정리. 약제·용량·기간은 실제 처방 관례에 따름. 임상 적용 시 최신 가이드라인과 환자 상태를 확인할 것.</footer>
  </main>
</div>
<button id="totop" title="맨 위로">↑</button>
<script src="assets/book.js"></script>
</body>
</html>
"""

def assemble(ch):
    m = META[ch]
    parts = []
    for f in m["frags"]:
        p = FRAG / (f + ".html")
        if not p.exists():
            print(f"  ! missing fragment {p}")
            continue
        t = p.read_text(encoding="utf-8").strip()
        # strip any accidental full-doc wrappers
        t = re.sub(r"(?is)^.*?<body[^>]*>", "", t)
        t = re.sub(r"(?is)</body>.*$", "", t)
        t = re.sub(r"(?is)<!DOCTYPE.*?>", "", t)
        parts.append(t)
    body = "\n\n".join(parts)
    (ROOT / f"{ch}.html").write_text(SKEL.format(
        no=m["no"], title=m["title"], lead=m["lead"],
        prevf=m["prev"][0], prevl=m["prev"][1],
        nextf=m["next"][0], nextl=m["next"][1], body=body), encoding="utf-8")
    print(f"  => wrote {ch}.html  ({len(body)} chars body)")

if __name__ == "__main__":
    for ch in (sys.argv[1:] or META):
        assemble(ch)
