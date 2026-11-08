#!/usr/bin/env python3
"""Render notes/*.md into workbook pages declared in notes/pages.json.

The markdown files are the SSOT for OneNote-derived material: the sync step only
rewrites them, and every HTML page is regenerated from them.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "notes" / "pages.json"

CHROME = {
    "egd": ("EGD", "상부위장관 내시경", "var(--egd)", "var(--egd-soft)"),
    "cfs": ("CFS", "대장내시경", "var(--cfs)", "var(--cfs-soft)"),
}


# ---------------------------------------------------------------- front matter
def split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    meta = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[end + 4 :].lstrip("\n")


# ---------------------------------------------------------------- inline rules
def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def slug(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[^0-9A-Za-z가-힣]+", "-", s).strip("-").lower()
    return s or "sec"


# ---------------------------------------------------------------- block rules
def render_md(md: str) -> tuple[str, list[tuple[str, str, int]]]:
    """Return (html, [(id, text, level)])."""
    out: list[str] = []
    toc: list[tuple[str, str, int]] = []
    lines = md.splitlines()
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            if level == 1:
                has = slug(text)
                out.append(f'<h1 id="{has}">{inline(text)}</h1>')
            else:
                has = slug(text)
                toc.append((has, re.sub(r"<[^>]+>", "", inline(text)), level))
                tag = "h2" if level == 2 else "h3"
                out.append(f'<{tag} id="{has}">{inline(text)}</{tag}>')
            i += 1
            continue

        # image: ![caption](path)
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
        if m:
            cap, src = m.group(1).strip(), m.group(2).strip()
            out.append(
                f'<figure class="fig"><img src="{html.escape(src, quote=True)}" '
                f'alt="{html.escape(cap, quote=True)}" loading="lazy">'
                f'<figcaption>{inline(cap)}</figcaption></figure>'
            )
            i += 1
            continue

        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            body = " ".join(x for x in buf if x)
            out.append(f"<blockquote><p>{inline(body)}</p></blockquote>")
            continue

        # GFM table
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            head = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            body = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows
            )
            out.append(f'<div class="tblwrap"><table class="tbl"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>')
            continue

        # lists
        if re.match(r"^([-*]|\d+\.)\s+", stripped):
            ordered = bool(re.match(r"^\d+\.\s", stripped))
            items = []
            while i < n and re.match(r"^([-*]|\d+\.)\s+", lines[i].strip()):
                item = re.sub(r"^([-*]|\d+\.)\s+", "", lines[i].strip())
                i += 1
                # an indented non-list line continues the current item
                while i < n:
                    nxt_raw = lines[i]
                    nxt = nxt_raw.strip()
                    if not nxt or not nxt_raw.startswith(("  ", "\t")):
                        break
                    if re.match(r"^([-*]|\d+\.)\s+", nxt) or nxt.startswith(("|", ">", "#")):
                        break
                    item += " " + nxt
                    i += 1
                items.append(f"<li>{inline(item)}</li>")
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue

        # paragraph (join continuation lines)
        buf = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith(("#", ">", "|", "- ", "* ")) or re.match(r"^\d+\.\s", nxt)):
                break
            buf.append(nxt)
            i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")

    return "\n".join(out), toc


# ---------------------------------------------------------------- page shell
def page(item: dict, body: str, toc, sources) -> str:
    channel = item.get("channel", "egd")
    code, label, acc, soft = CHROME.get(channel, CHROME["egd"])
    home = "index.html" if channel == "egd" else "index.html"
    upd = item["updated"]

    nav = "".join(
        f'<a class="{"h3" if lvl > 2 else ""}" href="#{hid}">{html.escape(txt)}</a>'
        for hid, txt, lvl in toc
        if lvl <= 3
    )
    src = "".join(f"<li><code>{html.escape(s)}</code></li>" for s in sources)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(item["title"])} — {code} 워크북</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/site.css">
<style>
  :root{{--acc:{acc};--accSoft:{soft}}}
  .notes-wrap{{display:grid;grid-template-columns:230px minmax(0,1fr);gap:44px;padding-top:34px}}
  .notes-side{{position:sticky;top:74px;align-self:start;font-size:13.5px}}
  .notes-side .t{{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);margin-bottom:10px}}
  .notes-side a{{display:block;color:var(--mut);text-decoration:none;padding:4px 9px;border-left:2px solid transparent;border-radius:0 6px 6px 0;line-height:1.5}}
  .notes-side a:hover{{color:var(--acc);background:var(--paper-2)}}
  .notes-side a.h3{{padding-left:22px;font-size:12.8px}}
  .notes-body{{max-width:820px;min-width:0}}
  .notes-body h2{{font-size:26px;margin:44px 0 12px;padding-top:14px;border-top:1px solid var(--line)}}
  .notes-body h2:first-child{{border-top:0;padding-top:0;margin-top:0}}
  .notes-body h3{{font-size:19px;margin:26px 0 8px;color:var(--ink-2)}}
  .notes-body p{{margin:10px 0}}
  .notes-body ul,.notes-body ol{{margin:10px 0;padding-left:22px}}
  .notes-body li{{margin:5px 0}}
  .notes-body blockquote{{margin:16px 0;padding:12px 18px;background:var(--accSoft);border-left:4px solid var(--acc);border-radius:0 8px 8px 0;color:var(--ink-2)}}
  .notes-body blockquote p{{margin:0}}
  .notes-body code{{font-family:var(--mono);font-size:13px;background:var(--paper-2);padding:1px 5px;border-radius:4px}}
  .notes-body hr{{border:0;border-top:1px solid var(--line);margin:34px 0}}
  .notes-body .tblwrap{{overflow-x:auto;margin:16px 0}}
  .note + .note{{margin-top:46px;padding-top:34px;border-top:2px solid var(--ink)}}
  .note-meta{{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin:0 0 6px}}
  .note-meta .idx{{font-family:var(--mono);font-size:10.5px;letter-spacing:.18em;color:var(--acc)}}
  .note-meta b{{font-family:var(--serif);font-size:15px;color:var(--ink-2)}}
  .note-meta .upd{{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--mut)}}
  .note > h2:first-of-type{{margin-top:10px;border-top:0;padding-top:0}}
  .notes-head{{border-bottom:2px solid var(--ink);padding-bottom:18px;margin-bottom:6px}}
  .notes-head .kicker{{font-family:var(--mono);font-size:11.5px;letter-spacing:.2em;color:var(--acc);text-transform:uppercase}}
  .notes-head h1{{font-family:var(--serif);font-size:clamp(30px,4.4vw,46px);margin:12px 0 0}}
  .notes-head .lead{{color:var(--ink-2);font-size:15.5px;margin:12px 0 0;max-width:64ch}}
  .srcbox{{margin:26px 0 0;font-size:12.5px;color:var(--mut);background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 18px}}
  .srcbox ul{{margin:6px 0 0;padding-left:18px}}
  .updated{{font-family:var(--mono);font-size:12px;color:var(--mut);margin-top:8px}}
  @media(max-width:900px){{.notes-wrap{{grid-template-columns:1fr;gap:20px}}.notes-side{{position:static;border-bottom:1px solid var(--line);padding-bottom:12px}}}}
</style>
</head>
<body>
<header class="sitebar">
  <a class="mark" href="../index.html"><i style="background:{acc}"></i> Endoscopy&nbsp;Study</a>
  <nav>
    <a href="../egd/index.html" class="{"on" if channel == "egd" else ""}">EGD</a>
    <a href="../cfs/index.html" class="{"on" if channel == "cfs" else ""}">CFS</a>
    <a href="https://media.githubusercontent.com/media/kimhs950627/endoscopy-study/master/downloads/EGD-workbook.pdf" rel="noopener">PDF</a>
  </nav>
</header>
<main class="wrap">
  <div class="notes-wrap">
    <aside class="notes-side">
      <div class="t">이 페이지</div>
      {nav}
    </aside>
    <article class="notes-body">
      <div class="notes-head">
        <div class="kicker">{html.escape(item["kicker"])}</div>
        <h1>{html.escape(item["title"])}</h1>
        <p class="lead">{html.escape(item["lead"])}</p>
        <div class="updated">마지막 동기화 {upd} · <a href="{home}">{code} 워크북으로</a></div>
      </div>
      {body}
      <div class="srcbox">
        <b>출처</b> — OneNote에서 자동 동기화한 노트
        <ul>{src}</ul>
      </div>
      <footer class="sitefoot">
        <p>개인 학회 정리를 내시경 판단용으로 재편집한 것. 약제·용량·적응은 최신 가이드라인과 환자 상태로 재확인할 것.</p>
      </footer>
    </article>
  </div>
</main>
</body>
</html>
"""


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for target, item in manifest.items():
        chunks = []
        sources = []
        latest = ""
        for rel in item["files"]:
            path = ROOT / rel
            meta, body_md = split_front_matter(path.read_text(encoding="utf-8"))
            body, toc = render_md(body_md)
            label = ""
            if meta.get("title"):
                label = (
                    f'<div class="note-meta"><span class="idx">NOTE {len(chunks) + 1:02d}</span>'
                    f'<b>{html.escape(meta["title"])}</b>'
                    f'<span class="upd">{html.escape(meta.get("updated", ""))}</span></div>'
                )
            chunks.append(f'<section class="note">\n{label}{body}\n</section>')
            sources.append(f'{rel} — {meta.get("title", "")} ({meta.get("source", "OneNote")})')
            latest = max(latest, meta.get("updated", ""))
        item["updated"] = item.get("updated") or latest or date.today().isoformat()

        body = "\n".join(chunks)
        _, toc_all = render_md("\n\n".join(split_front_matter((ROOT / r).read_text(encoding="utf-8"))[1] for r in item["files"]))
        out = ROOT / target
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(item, body, toc_all, sources), encoding="utf-8")
        print(f"wrote {target}  ({len(body):,} chars, {len(toc_all)} headings)")


if __name__ == "__main__":
    main()
