#!/usr/bin/env python3
"""
Quotes page generator.

content/quotes.md is the single source of truth for every attributed line on
the site. This renders it two ways:

  1. public/quotes/index.html — the human page, plus a CollectionPage/Quotation
     JSON-LD block so each line is independently attributable by a crawler or a
     language model rather than being buried in a paragraph it has to guess the
     boundaries of.
  2. hasPart on each essay's Article JSON-LD — so a quote still carries its
     attribution when only the essay page is fetched.

Sources are resolved by title against content/essays and content/lexicon, so an
attribution line that does not name a real essay or term is a hard error rather
than a silently dead link.

Chrome (masthead/footer) is lifted from a published page so nav changes
propagate automatically, matching tools/essay/generate.py.

Usage:
    python3 tools/quotes/generate.py
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = "https://cvpe.eu"
BSKY = "https://bsky.app/profile/jpahonen.eurosky.social"
SRC = os.path.join(ROOT, "content", "quotes.md")
OUT = os.path.join(ROOT, "public", "quotes", "index.html")
CHROME_FROM = os.path.join(ROOT, "public", "essays", "ceuta-first-evergray-battle", "index.html")
DESC = ("Curated lines from CVPE essays, lexicon entries, and threads. "
        "Each dated; each stands or falls with its context.")
AUTHOR = {"@type": "Person", "name": "JP Ahonen", "sameAs": BSKY}


def frontmatter(path):
    meta = {}
    for line in open(path).read().split("---\n")[1].strip().split("\n"):
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"')
    return meta


def body(path):
    """Source prose with link syntax unwrapped, for verbatim checking."""
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", open(path).read())


def sources():
    """Title (as written in an attribution line) -> source record."""
    out = {}
    d = os.path.join(ROOT, "content", "essays")
    for f in sorted(os.listdir(d)):
        path = os.path.join(d, f)
        m = frontmatter(path)
        out[m["title"]] = {"type": "Article", "url": f"{SITE}/essays/{m['slug']}/",
                           "date": m["date"], "slug": m["slug"], "name": m["title"],
                           "body": body(path)}
    d = os.path.join(ROOT, "content", "lexicon")
    for f in sorted(os.listdir(d)):
        path = os.path.join(d, f)
        m = frontmatter(path)
        out[f"Lexicon: {m['term']}"] = {
            "type": "DefinedTerm", "url": f"{SITE}/lexicon/{m['slug']}/",
            "date": m.get("coined_date", ""), "slug": None, "name": m["term"],
            "body": body(path)}
    return out


def verbatim(text, src):
    """Is this line a literal, contiguous substring of its cited source?

    Only quote characters are normalised — the page renders inner double quotes
    as single ones, which is typography, not a change to the words. Anything
    else that fails here is a condensation or comes from somewhere other than
    the work it cites, and must not be machine-asserted as part of that work.
    """
    def norm(s):
        return s.replace("\u201c", '"').replace("\u201d", '"').replace("'", '"')
    return norm(text) in norm(src["body"])


def parse(index):
    """Blocks of `> "quote"` / `> — *Source*, date label`."""
    quotes, text = [], None
    for line in open(SRC).read().split("\n"):
        line = line.strip()
        if not line.startswith(">"):
            continue
        body = line.lstrip("> ").strip()
        if body.startswith("—"):
            if text is None:
                raise SystemExit(f"attribution with no quote above it: {body}")
            m = re.match(r"—\s*\*(.+?)\*,\s*(.+)$", body)
            if not m:
                raise SystemExit(f"unparseable attribution: {body}")
            title, label = m.group(1), m.group(2).strip()
            if title not in index:
                raise SystemExit(f"attribution names no known essay or term: {title}")
            src = index[title]
            quotes.append({"text": text, "title": title, "label": label,
                           "src": src, "verbatim": verbatim(text, src)})
            text = None
        else:
            text = body.strip('"')
    if text is not None:
        raise SystemExit(f"quote with no attribution: {text}")
    return quotes


def figures(quotes):
    out = []
    for q in quotes:
        # inner double quotes render as single quotes, matching the existing page.
        # quote=False keeps apostrophes literal — this is element content, not an
        # attribute, so escaping them only makes the source unreadable.
        t = html.escape(q["text"].replace('"', "'"), quote=False)
        cite = html.escape(f"{q['title']} — {q['label']}", quote=False)
        out.append(f"""      <figure class="quote-item">
        <blockquote>{t}</blockquote>
        <cite><a href="{q['src']['url'].replace(SITE, '')}">{cite}</a></cite>
      </figure>""")
    return "\n".join(out)


def ld(quotes):
    parts = []
    for q in quotes:
        node = {"@type": "Quotation", "text": q["text"], "creator": AUTHOR,
                "inLanguage": "en-GB"}
        # A quote that is not literally in the work it cites still belongs to its
        # author, but claiming it is part of that page would be false.
        if q["verbatim"]:
            node["isPartOf"] = {"@type": q["src"]["type"], "name": q["src"]["name"],
                                "url": q["src"]["url"]}
        if q["src"]["date"]:
            node["dateCreated"] = q["src"]["date"]
        parts.append(node)
    return json.dumps({
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": "Quotes — CVPE", "url": f"{SITE}/quotes",
        "description": DESC, "author": AUTHOR, "inLanguage": "en-GB",
        "hasPart": parts,
    }, ensure_ascii=False, indent=2)


def page(quotes):
    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>Quotes — CVPE</title>
  <meta name="description" content="{DESC}">
  <meta name="author" content="JP Ahonen">
  <link rel="canonical" href="{SITE}/quotes/">

  <meta property="og:type" content="website">
  <meta property="og:title" content="Quotes — CVPE">
  <meta property="og:description" content="{DESC}">
  <meta property="og:url" content="{SITE}/quotes/">
  <meta property="og:image" content="{SITE}/assets/og-default.png">
  <meta property="og:site_name" content="CVPE — Certa Vizio Pri Eŭropo">
  <meta property="og:locale" content="en_GB">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Quotes — CVPE">
  <meta name="twitter:description" content="{DESC}">
  <meta name="twitter:image" content="{SITE}/assets/og-default.png">
  <script type="application/ld+json">{ld(quotes)}</script>

  <link rel="alternate" type="application/rss+xml"
        title="CVPE Essays" href="{SITE}/feed.xml">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="/css/main.css">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
</head>"""

    chrome = open(CHROME_FROM).read()
    masthead = chrome[chrome.index("<body>"):chrome.index("</header>") + len("</header>")]
    footer = chrome[chrome.index('<footer class="footer"'):]
    # the quotes page has no current nav item, so no aria-current belongs on it
    masthead = masthead.replace(' aria-current="page"', "")

    return head + masthead + f"""
<main id="main" role="main">
  <div class="container">
    <header class="article-header">
      <h1>Quotes</h1>
      <p class="hero-sub">Curated lines from the essays, the lexicon, and the threads. Each dated; each stands or falls with its context.</p>
    </header>
    <section aria-label="Quotes">
{figures(quotes)}
    </section>
    <p class="body-sm" style="color: var(--quiet);">Quotation with attribution is welcome: "JP Ahonen, CVPE (cvpe.eu)".</p>
  </div>
</main>
""" + footer


def inject_essays(quotes):
    """Add hasPart Quotation nodes to each essay's Article JSON-LD."""
    by_slug = {}
    for q in quotes:
        if q["src"]["slug"] and q["verbatim"]:
            by_slug.setdefault(q["src"]["slug"], []).append(q["text"])
    touched = 0
    for slug, texts in sorted(by_slug.items()):
        path = os.path.join(ROOT, "public", "essays", slug, "index.html")
        s = open(path).read()
        m = re.search(r'(<script type="application/ld\+json">)(\{.*?\})(</script>)', s, re.S)
        if not m:
            print(f"  !! no JSON-LD in {slug}"); continue
        data = json.loads(m.group(2))
        if data.get("@type") != "Article":
            print(f"  !! {slug} JSON-LD is not an Article"); continue
        data["hasPart"] = [{"@type": "Quotation", "text": t, "creator": AUTHOR,
                            "isPartOf": {"@type": "Article", "name": data["headline"],
                                         "url": data["url"]},
                            "inLanguage": "en-GB"} for t in texts]
        block = json.dumps(data, ensure_ascii=False, indent=2)
        s = s[:m.start(2)] + block + s[m.end(2):]
        open(path, "w").write(s)
        touched += 1
        print(f"  {slug}: {len(texts)} quote(s)")
    return touched


def main():
    index = sources()
    quotes = parse(index)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(page(quotes))
    print(f"wrote {OUT} — {len(quotes)} quote(s)")
    n = inject_essays(quotes)
    print(f"injected hasPart into {n} essay page(s)")
    loose = [q for q in quotes if not q["verbatim"]]
    if loose:
        print(f"\n{len(loose)} quote(s) are NOT a literal substring of the work they cite.")
        print("They keep their author attribution but carry no isPartOf claim:")
        for q in loose:
            print(f"  · \"{q['text'][:72]}…\"\n    cited to {q['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
