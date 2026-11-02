#!/usr/bin/env python3
"""Render data/cases.json into the EGD case chapter (egd/07-감별증례.html).

Each case is a self-test block: images first, answer behind a <details>. Print CSS in
book.css opens every <details> so the PDF carries the full explanations.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "data" / "cases.json"
OUT = ROOT / "egd" / "07-감별증례.html"

HEAD = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CHAPTER 07 · 감별 증례 100 — Endoscopy Study</title>
<link href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/book.css">
</head>
<body>
<header class="topbar">
  <a class="brand" href="index.html">EndoTODAY 참고서</a>
  <span class="chap">CHAPTER 07 · 감별 증례</span>
  <span class="nav"><a href="06-십이지장-악성.html">◀ 이전</a><a href="index.html">목차</a><a href="book.html">합본</a></span>
</header>
<div class="layout">
  <nav class="toc"><div class="ttl">목차</div><div id="toc"></div></nav>
  <main>
    <div class="chapter-head">
      <div class="no">CHAPTER 07</div>
      <h1>감별 증례 100</h1>
      <p class="lead">조기위암과 식도암을 <b>사진만 보고 스스로 판독</b>하는 증례집. 위 80례 + 식도 20례로,
      각 증례는 내시경 사진 → (정답·해설) 순서다. 해설에는 병변 기술, 색소·NBI 소견, 생검 결과, 병리 크기·심달도,
      그리고 저자가 붙인 태그(#혈관투시상 소실, #함몰, #위축 영역 …)가 들어 있다.</p>
    </div>

    <div class="casebar" data-casebar>
      <div class="csg" role="group" aria-label="부위 필터">
        <button class="csb on" data-filter="all">전체 100</button>
        <button class="csb" data-filter="위">위 80</button>
        <button class="csb" data-filter="식도">식도 20</button>
      </div>
      <label class="csearch">
        <span>검색</span>
        <input type="search" data-csearch placeholder="태그·키워드 (예: 인디고카민, 함몰, signet)">
      </label>
      <button class="csb cstoggle" data-toggle-answers>정답 모두 펼치기</button>
    </div>
    <p class="casehint">사진을 먼저 보고 병변 위치·색조·함몰/융기·경계를 스스로 기술한 뒤 정답을 펼친다.
    태그로 검색하면 같은 소견의 증례만 모인다.</p>
"""


def esc(s: str) -> str:
    return html.escape(s or "")


def render_case(c: dict) -> str:
    imgs = "\n".join(
        f'      <figure class="cfig"><img src="../assets/img/cases/{esc(name)}" alt="증례 {c["case"]:03d} 내시경 사진" loading="lazy"></figure>'
        for name in c["imgs"]
    )
    tags = "".join(f'<span class="ctag">#{esc(t)}</span>' for t in c["tags"])
    body = "".join(f"<p>{esc(p)}</p>" for p in c["body"])
    path = f'<p class="cpath">{esc(c["pathology"])}</p>' if c["pathology"] else ""
    summary = f'<p class="csum">{esc(c["summary"])}</p>' if c["summary"] else ""
    return f"""
    <article class="case" id="case-{c['case']:03d}" data-organ="{esc(c['organ'])}"
             data-text="{esc(' '.join([c['history'], c['summary'], ' '.join(c['body']), c['pathology'], ' '.join(c['tags'])]))}">
      <header class="chead">
        <span class="cno">CASE {c['case']:03d}</span>
        <span class="corg">{esc(c['organ'])}</span>
        <span class="cdemo">{esc(c['age_sex'])}</span>
      </header>
      <p class="chist">{esc(c['history'])}</p>
      <div class="cfigs">
{imgs}
      </div>
      <details class="cans">
        <summary>정답 · 해설 보기</summary>
        {summary}
        {body}
        {path}
        <div class="ctags">{tags}</div>
      </details>
    </article>"""


TAIL = """
    <footer class="credit">
      <p><b>원본</b> — 개인 소장 PDF 『100증례 조기위암, 식도암 감별』에서 증례 이미지와 해설을 추출해
      재구성했습니다. 원저작물의 권리는 원저자에게 있으며, 이 페이지는 개인 학습용이며 상업적 이용·재배포를 하지 않습니다.</p>
      <p>본 워크북 전체는 이준행 교수님이 운영하는 <a href="https://endotoday.com" target="_blank" rel="noopener">EndoTODAY(endotoday.com)</a>
      강의·아틀라스를 기반으로 한 2차 정리물입니다. 텍스트는 PDF에서 자동 추출해 일부 띄어쓰기·오탈자가 남아 있을 수 있습니다.
      임상 판단은 원본과 최신 가이드라인으로 재확인해야 합니다.</p>
    </footer>
  </main>
</div>
<button id="totop" title="맨 위로">↑</button>
<script src="../assets/book.js"></script>
<script>
(function () {
  var bar = document.querySelector('[data-casebar]');
  if (!bar) return;
  var cases = Array.prototype.slice.call(document.querySelectorAll('.case'));
  var filter = 'all', query = '';

  function apply() {
    var shown = 0;
    cases.forEach(function (el) {
      var okOrgan = filter === 'all' || el.dataset.organ === filter;
      var okText = !query || (el.dataset.text || '').toLowerCase().indexOf(query) !== -1;
      var vis = okOrgan && okText;
      el.hidden = !vis;
      if (vis) shown++;
    });
    document.querySelectorAll('[data-filter]').forEach(function (b) {
      b.classList.toggle('on', b.dataset.filter === filter);
    });
    document.querySelectorAll('.cgroup').forEach(function (g) {
      var any = g.querySelector('.case:not([hidden])');
      g.hidden = !any;
    });
  }

  bar.querySelectorAll('[data-filter]').forEach(function (b) {
    b.addEventListener('click', function () { filter = b.dataset.filter; apply(); });
  });
  var input = bar.querySelector('[data-csearch]');
  if (input) input.addEventListener('input', function () { query = input.value.trim().toLowerCase(); apply(); });

  var toggle = bar.querySelector('[data-toggle-answers]');
  var open = false;
  if (toggle) toggle.addEventListener('click', function () {
    open = !open;
    document.querySelectorAll('.case').forEach(function (c) {
      var d = c.querySelector('details');
      if (d) d.open = open;
    });
    toggle.textContent = open ? '정답 모두 접기' : '정답 모두 펼치기';
  });
})();
</script>
</body>
</html>
"""


GROUPS = [
    ("위", "위 조기위암 — 80례", "혈관투시상 소실·발적조·함몰/융기를 읽고 분화형 vs 미분화형을 가른 뒤 생검·병리로 확인한다."),
    ("식도", "식도 조기암 — 20례", "NBI brownish area, 요오드 불염대, 편평상피암의 경계와 심달도 판단."),
]


def main() -> None:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    parts = []
    for organ, title, lead in GROUPS:
        group = [c for c in cases if c["organ"] == organ]
        if not group:
            continue
        slug = "s-" + ("위-조기위암" if organ == "위" else "식도-조기암")
        parts.append(
            f'<section class="cgroup" data-group="{organ}">\n'
            f'<h2 id="{slug}">{title}</h2>\n'
            f'<p class="glead">{lead}</p>\n'
            + "\n".join(render_case(c) for c in group)
            + "\n</section>"
        )
    body = "\n".join(parts)
    doc = HEAD + body + TAIL
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  {len(cases)} cases · {len(doc):,} chars")


if __name__ == "__main__":
    main()
