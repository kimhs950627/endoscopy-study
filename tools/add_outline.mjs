import fs from "fs";
import { createRequire } from "module";
import { getDocument, GlobalWorkerOptions } from "pdfjs-dist/legacy/build/pdf.mjs";
import pkg from "pdf-lib";

const require = createRequire(import.meta.url);
GlobalWorkerOptions.workerSrc = require.resolve("pdfjs-dist/legacy/build/pdf.worker.mjs");
const { PDFDocument, PDFName, PDFNumber, PDFHexString, PDFArray, PDFDict, PDFNull } = pkg;

const [pdfPath, htmlPath, outPath] = process.argv.slice(2);

const strip = (s) =>
  s
    .replace(/<[^>]+>/g, " ")
    .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ").replace(/&#39;/g, "'").replace(/&quot;/g, '"')
    .replace(/\s+/g, " ").trim();
const key = (s) => s.replace(/[^\p{L}\p{N}]/gu, "");

// ---- 1. parse structure from merged book.html ----
const html = fs.readFileSync(htmlPath, "utf8");
const secs = html.split(/<section class="bookchapter[^"]*">/).slice(1);
const groups = [];
for (const sec of secs) {
  const h1 = sec.match(/<h1[^>]*>([\s\S]*?)<\/h1>/);
  const children = [...sec.matchAll(/<h2[^>]*>([\s\S]*?)<\/h2>/g)].map((m) => strip(m[1]));
  groups.push({ title: h1 ? strip(h1[1]) : "?", children });
}

// ---- 2. map each heading to a page (sequential search) ----
const bytes = new Uint8Array(fs.readFileSync(pdfPath));
const doc = await getDocument({ data: bytes, useWorkerFetch: false, isEvalSupported: false }).promise;
const n = doc.numPages;
const pageText = [];
for (let p = 1; p <= n; p++) {
  const tc = await (await doc.getPage(p)).getTextContent();
  pageText.push(tc.items.map((i) => i.str).join("").replace(/[^\p{L}\p{N}]/gu, ""));
}
let cursor = 0;
function findPage(title) {
  const k = key(title);
  for (let p = cursor; p < n; p++) if (pageText[p].includes(k)) { cursor = p; return p; }
  const prefix = k.slice(0, 12);
  for (let p = 0; p < n; p++) if (pageText[p].includes(prefix)) return p;
  return cursor;
}

const chapters = groups.map((g) => ({
  title: g.title,
  page: findPage(g.title),
  children: g.children.map((c) => ({ title: c, page: findPage(c) })),
}));

// ---- 3. inject outline with pdf-lib ----
// NOTE: pdfjs transfers the ArrayBuffer above, so re-read the file for pdf-lib.
const pdf = await PDFDocument.load(new Uint8Array(fs.readFileSync(pdfPath)), { updateMetadata: false });
const ctx = pdf.context;
const pages = pdf.getPages();
const pageRef = (i) => pages[Math.max(0, Math.min(pages.length - 1, i))].ref;

const rootRef = ctx.nextRef();
const chRefs = chapters.map(() => ctx.nextRef());
const childRefs = chapters.map((c) => c.children.map(() => ctx.nextRef()));

const dest = (i) => {
  const a = PDFArray.withContext(ctx);
  a.push(pageRef(i)); a.push(PDFName.of("XYZ"));
  a.push(PDFNull); a.push(PDFNull); a.push(PDFNull);
  return a;
};
function dict(o) {
  const d = PDFDict.withContext(ctx);
  d.set(PDFName.of("Title"), PDFHexString.fromText(o.title));
  if (o.parent) d.set(PDFName.of("Parent"), o.parent);
  d.set(PDFName.of("Dest"), dest(o.page));
  if (o.first) d.set(PDFName.of("First"), o.first);
  if (o.last) d.set(PDFName.of("Last"), o.last);
  if (o.count) d.set(PDFName.of("Count"), PDFNumber.of(o.count));
  if (o.prev) d.set(PDFName.of("Prev"), o.prev);
  if (o.next) d.set(PDFName.of("Next"), o.next);
  return d;
}

let total = 0;
chapters.forEach((c, i) => {
  const kids = c.children;
  kids.forEach((k, j) => {
    ctx.assign(childRefs[i][j], dict({
      title: k.title, page: k.page, parent: chRefs[i],
      prev: j > 0 ? childRefs[i][j - 1] : undefined,
      next: j < kids.length - 1 ? childRefs[i][j + 1] : undefined,
    }));
  });
  ctx.assign(chRefs[i], dict({
    title: c.title, page: c.page, parent: rootRef,
    first: kids.length ? childRefs[i][0] : undefined,
    last: kids.length ? childRefs[i][kids.length - 1] : undefined,
    count: kids.length || undefined,
    prev: i > 0 ? chRefs[i - 1] : undefined,
    next: i < chapters.length - 1 ? chRefs[i + 1] : undefined,
  }));
  total += 1 + kids.length;
});
ctx.assign(rootRef, (() => {
  const d = PDFDict.withContext(ctx);
  d.set(PDFName.of("Type"), PDFName.of("Outlines"));
  d.set(PDFName.of("First"), chRefs[0]);
  d.set(PDFName.of("Last"), chRefs[chRefs.length - 1]);
  d.set(PDFName.of("Count"), PDFNumber.of(total));
  return d;
})());
pdf.catalog.set(PDFName.of("Outlines"), rootRef);
pdf.catalog.set(PDFName.of("PageMode"), PDFName.of("UseOutlines"));

const out = await pdf.save({ useObjectStreams: false, addDefaultPage: false });
fs.writeFileSync(outPath, out);
console.log(`bookmarks: ${chapters.length} chapters, ${total - chapters.length} sections, total ${total}`);
chapters.forEach((c) => console.log(`  p${c.page + 1}  ${c.title}  (${c.children.length})`));
