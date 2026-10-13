#!/usr/bin/env python3
"""
Crawl EndoTODAY (endotoday.com) into per-chapter digests + local images.

- Static HTML pages, EUC-KR (fallback cp949/utf-8).
- Requires browser-like headers; the IIS front blocks bare curl/urllib.
- Output:
    work/html/<chapter>/<page>.html     raw cached HTML (utf-8)
    work/digest/<chapter>.md            readable text with local image refs
    assets/img/<chapter>/<file>         downloaded images (jpg/png/gif/webp)
"""
import re, os, sys, html, hashlib, time, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://www.endotoday.com/endotoday/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
HDRS = {
    "User-Agent": UA,
    "Referer": "http://www.endotoday.com/",
    "Accept": "text/html,image/*,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}
IMG_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")
SKIP_IMG = {"youtube.jpg", "logo.png", "arrow.gif", "spacer.gif"}

CHAPTERS = {
    "00-총론": [
        "lecture_01.html", "insertion_faq.html", "anatomy.html",
        "lecture_02.html", "biopsy.html", "biopsy_faq.html",
        "chromoendoscopy.html", "IEE.html", "magnifying.html",
        "size.html", "pictures.html", "terminology.html",
        "classification.html", "dex_workshop.html",
        "sedation_introduction.html", "sedation_complication.html",
        "antiplatelet.html", "warfarin.html", "noac.html",
        "antispasmodics.html", "antibiotics.html", "safe_endoscopy.html",
        "perforation.html", "EGD_malloryweiss.html", "clip.html",
        "chronic_gastritis_13.html", "pathology.html", "em.html",
        "endoscope.html",
    ],
    "01-식도-양성": [
        "tuberculous_esophagitis.html", "esophageal_candidiasis.html",
        "viral.html", "EoE.html", "corrosive.html", "melanocytosis.html",
        "foreign_body.html", "esophagus_002.html",
        "reflux_esophagitis.html", "PPI.html", "PPI_adverse.html",
        "pcab.html", "GERD_FAQ.html", "GERD_RPL.html", "minimal.html",
        "sentinel.html", "asymptomatic_esophagitis.html", "refractory.html",
        "gerd.html", "lars.html", "stretta.html",
        "barretts.html", "FAQ_barretts.html",
        "zenker.html", "KJ.html", "diverticulum_midesophageal.html",
        "esophagus.html", "laryngopharyngeal.html",
        "hiatal_hernia.html", "acid_pocket.html", "20120718.html",
        "fistula.html", "achalasia.html", "papilloma.html",
        "esophageal_smt.html", "pill.html", "granular.html",
        "esophagus_burn.html", "heterotopic.html", "malloryweiss.html",
    ],
    "02-식도-악성": [
        "esophageal_cancer.html", "Monday_20170116.html",
        "20130112.html", "20121222.html", "eso_ESD_stricture.html",
        "barrett_adenocarcinoma.html", "esophagus_node.html",
        "tube.html", "esophagus_060.html", "esophageal_melanoma.html",
    ],
    "03-위-양성": [
        "anatomy.html", "normal.html", "gastric_diverticulum.html",
        "situs_inversus.html", "angiodysplasia.html",
        "helicobacter.html", "helicobacter_treatment.html",
        "helicobacter_medication_timing.html", "helicobacter_resistance.html",
        "helicobacter_situation.html", "helicobacter_faq.html",
        "gastritis.html", "chronic_gastritis.html",
        "helicobacter_gastritis.html", "gastritis_nonatrophic.html",
        "gastritis_atrophic.html", "gastritis_metaplastic.html",
        "gastritis_erosive.html", "erosive.html", "prepyloric.html",
        "gastritis_hypertrophic.html", "gastritis_hemorrhagic.html",
        "gastritis_lymphofollicular.html", "agml.html", "RT.html",
        "autoimmune.html", "gave.html", "gastritis_phlegmonous.html",
        "anisakiasis.html", "portal.html", "gastritis_kyoto.html",
        "chronic_gastritis_27.html", "NSAID.html", "syphilis.html",
        "CMV.html", "ulcer.html", "20111009.html", "20111119.html",
        "bleeding_ulcer.html", "refractory.html",
        "polyp.html", "fundic.html", "atypical.html", "adenoma.html",
        "schwannoma.html", "compression.html", "ectopic_pancreas.html",
        "gist.html", "submucosal.html", "FAQ_submucosal.html",
        "carcinoid.html", "xanthoma.html", "lipoma.html",
        "bezoar.html", "20131029.html", "peg.html", "fd.html",
        "gastric_varix.html", "lecs.html",
    ],
    "04-위-악성": [
        "diagnosis.html", "cancer.html", "classification_egc.html",
        "egc.html", "agc.html", "20130210.html", "20110719.html",
        "postoperative.html", "GEJ.html", "screening.html", "src.html",
        "mucinous.html", "remnant.html", "gastric_metastasis.html",
        "young.html", "elderly.html", "PET.html", "hpngc.html",
        "EBV.html", "papillary.html", "20130721.html", "gcae.html",
        "pathology.html", "differentiation.html", "undifferentiated.html",
        "staging.html", "depth_of_invasion.html", "cancer_faq.html",
        "chemotherapy.html",
        "esd_training.html", "esd_20181101.html", "expanded.html",
        "ESD_LN.html", "ESD_HGD.html", "esd_group_classification.html",
        "undifferentiated_LN.html", "esd_ulcer.html", "esd_followup.html",
        "curative.html", "esd_longterm.html", "SM_invasion.html",
        "metachronous.html", "ESD_definition.html", "ESD_size.html",
        "lymphoma.html", "dlbl.html", "dlbl2.html", "maltoma.html",
        "maltoma_endoscopy.html", "mantle.html", "NKT.html", "Burkitt.html",
    ],
    "05-십이지장-양성": [
        "small.html", "20110519.html", "heterotopia.html",
        "lymphangiectasia.html", "hsp.html", "brunner.html",
        "follicular.html", "duodenal_SMT.html", "duodenal_adenoma.html",
    ],
    "06-십이지장-악성": [
        "duodenal_cancer.html", "duodenal_carcinoid.html", "ampullary.html",
        "maltoma_extragastric.html", "20131002.html", "20131128.html",
        "small_024.html",
    ],
}


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def decode(raw):
    for enc in ("utf-8", "euc-kr", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("euc-kr", "replace")


def page_title(doc):
    m = re.search(r"<title>(.*?)</title>", doc, re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(m.group(1)).strip()) if m else ""


def to_text(doc):
    doc = re.sub(r"<(script|style|head)\b.*?</\1>", " ", doc, flags=re.S | re.I)
    doc = re.sub(r"<!--.*?-->", " ", doc, flags=re.S)
    doc = re.sub(r"<br\s*/?>", "\n", doc, flags=re.I)
    doc = re.sub(r"</(p|div|tr|li|blockquote|h[1-6]|table|ul|ol)>", "\n", doc, flags=re.I)
    doc = re.sub(r"</t[dh]>", " | ", doc, flags=re.I)
    doc = re.sub(r"<img[^>]*?src=\"([^\"]+)\"[^>]*>", r"\n[[IMG:\1]]\n", doc, flags=re.I)
    doc = re.sub(r"<[^>]+>", " ", doc)
    doc = html.unescape(doc)
    doc = re.sub(r"[ \t\u00a0]+", " ", doc)
    doc = re.sub(r"\n\s*\n\s*\n+", "\n\n", doc)
    return doc.strip()


def local_img(url, chapter):
    name = os.path.basename(urllib.parse.urlparse(url).path)
    if name.lower() in SKIP_IMG:
        return None
    ext = os.path.splitext(name)[1].lower()
    if ext not in IMG_EXT:
        return None
    dest_dir = ROOT / "assets" / "img" / chapter
    dest_dir.mkdir(parents=True, exist_ok=True)
    # collision-safe name
    stem, ext = os.path.splitext(name)
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    dest = dest_dir / safe
    if dest.exists() and dest.stat().st_size > 0:
        return f"assets/img/{chapter}/{safe}"
    try:
        raw = fetch(url, binary=True)
        if len(raw) < 200:
            return None
        dest.write_bytes(raw)
        return f"assets/img/{chapter}/{safe}"
    except Exception as e:
        print(f"    ! img fail {url}: {e}", file=sys.stderr)
        return None


def crawl_chapter(chapter, pages):
    print(f"\n### {chapter} ({len(pages)} pages)")
    cache_dir = ROOT / "work" / "html" / chapter
    cache_dir.mkdir(parents=True, exist_ok=True)
    digest_dir = ROOT / "work" / "digest"
    digest_dir.mkdir(parents=True, exist_ok=True)
    out = [f"# {chapter}\n"]
    ok = fail = 0
    for page in pages:
        url = urllib.parse.urljoin(BASE, page)
        try:
            raw = fetch(url)
        except Exception as e:
            print(f"  x {page}: {e}", file=sys.stderr)
            fail += 1
            continue
        doc = decode(raw)
        (cache_dir / (os.path.splitext(os.path.basename(page))[0] + ".html")).write_text(doc, encoding="utf-8")
        title = page_title(doc)
        body = to_text(doc)
        # resolve image refs to local paths
        def repl(m):
            src = m.group(1)
            if src.startswith(("http://", "https://")):
                absu = src
            else:
                absu = urllib.parse.urljoin(url, src)
            local = local_img(absu, chapter)
            return f"\n\n![{os.path.basename(src)}]({local})\n\n" if local else ""
        body = re.sub(r"\[\[IMG:([^\]]+)\]\]", repl, body)
        body = re.sub(r"\n{3,}", "\n\n", body)
        out.append(f"\n\n---\n## {title or page}\n출처: {url}\n\n{body}\n")
        print(f"  + {page}  ({len(body)} chars)")
        ok += 1
        time.sleep(0.2)
    (digest_dir / f"{chapter}.md").write_text("\n".join(out), encoding="utf-8")
    print(f"  => {chapter}: ok={ok} fail={fail} -> work/digest/{chapter}.md")
    return ok, fail


if __name__ == "__main__":
    only = sys.argv[1:] or list(CHAPTERS)
    for ch in only:
        if ch in CHAPTERS:
            crawl_chapter(ch, CHAPTERS[ch])
