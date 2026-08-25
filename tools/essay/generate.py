#!/usr/bin/env python3
"""
Essay page generator.

Renders content/essays/YYYY-MM-DD-slug.md into public/essays/<slug>/index.html,
matching the house template: tag, title, byline, prose, Related block, Bluesky
discussion mount, and the full meta/JSON-LD head.

Chrome (masthead/footer) is lifted from an existing published essay so nav
changes propagate automatically instead of being duplicated here.

Usage:
    python3 tools/essay/generate.py <content-file.md> [--related slug,slug,slug]
    python3 tools/essay/generate.py content/essays/2026-08-25-the-right-size-for-the-job.md
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = "https://cvpe.eu"
BSKY = "https://bsky.app/profile/jpahonen.eurosky.social"
CHROME_FROM = os.path.join(ROOT, "public", "essays", "ceuta-first-evergray-battle", "index.html")

MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def human_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {MONTHS[m]} {y}"


def parse(path):
    raw = open(path).read()
    _, fm, body = raw.split("---\n", 2)
    meta = {}
    for line in fm.strip().split("\n"):
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"')
    return meta, body


def inline(t):
    # external links open in a new tab; internal ones stay in place
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<em>\1</em>', t)
    return t


def render_body(body):
    out = []
    for b in re.split(r"\n\n+", body.strip()):
        b = b.strip()
        if not b:
            continue
        if b.startswith("<"):                      # raw HTML block (figures)
            out.append("      " + b)
        elif b == "---":
            out.append("      <hr>")
        elif b.startswith("### "):
            out.append(f"      <h3>{inline(b[4:])}</h3>")
        elif b.startswith("## "):
            out.append(f"      <h2>{inline(b[3:])}</h2>")
        elif b.startswith("* "):
            items = "\n".join(f"        <li>{inline(l[2:].strip())}</li>"
                              for l in b.split("\n") if l.startswith("* "))
            out.append(f"      <ul>\n{items}\n      </ul>")
        elif b.startswith("*JP Ahonen"):
            out.append(f'      <p class="body-sm"><em>{inline(b.strip("*"))}</em></p>')
        else:
            out.append(f"      <p>{inline(b)}</p>")
    return "\n".join(out)


def related_block(pairs):
    """pairs: list of (href, label, blurb)"""
    if not pairs:
        return ""
    items = "\n".join(
        f'        <dt><a href="{h}">{l}</a></dt>\n        <dd>{b}</dd>' for h, l, b in pairs)
    return f"""
    <section class="section-block" aria-labelledby="related-label" data-pagefind-ignore>
      <h2 class="section-label" id="related-label">Related</h2>
      <dl class="term-preview">
{items}
      </dl>
    </section>
"""


def build(meta, body, desc, keywords, related):
    slug, title = meta["slug"], meta["title"]
    date, domain, rt = meta["date"], meta["domain"], meta["reading_time"]
    thread = meta.get("bluesky_thread", "")
    img = f"{SITE}/assets/og/{slug}.png"

    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": meta["excerpt"],
        "author": {"@type": "Person", "name": "JP Ahonen", "sameAs": BSKY},
        "publisher": {"@type": "Organization", "name": "CVPE", "url": SITE},
        "datePublished": date, "dateModified": meta.get("modified", date),
        "url": f"{SITE}/essays/{slug}",
        "keywords": keywords,
        "articleSection": domain, "inLanguage": "en-GB",
        "about": {"@type": "Thing", "name": domain},
    }, ensure_ascii=False, indent=2)

    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>{title} — CVPE</title>
  <meta name="description" content="{desc}">
  <meta name="author" content="JP Ahonen">
  <link rel="canonical" href="{SITE}/essays/{slug}/">

  <meta property="og:type" content="article">
  <meta property="og:title" content="{title} — CVPE">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{SITE}/essays/{slug}/">
  <meta property="og:image" content="{img}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="CVPE — {title}">
  <meta property="og:site_name" content="CVPE — Certa Vizio Pri Eŭropo">
  <meta property="og:locale" content="en_GB">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title} — CVPE">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{img}">
  <meta name="twitter:image:alt" content="CVPE — {title}">
  <meta property="article:published_time" content="{date}">
  <meta property="article:author" content="JP Ahonen">
  <meta property="article:tag" content="{domain}">
  <script type="application/ld+json">{ld}</script>

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
    thread_comment = "" if thread else "  // bluesky_thread: set when thread is posted"

    return head + masthead + f"""
<main id="main" role="main">
  <div class="container">
    <article data-pagefind-body>
      <header class="article-header">
        <span class="tag">{domain}</span>
        <h1>{title}</h1>
        <span class="meta">JP Ahonen · <time datetime="{date}">{human_date(date)}</time> · {rt} min read</span>
      </header>
      <div class="prose">
{render_body(body)}
      </div>
    </article>
{related_block(related)}
    <section class="section-block" aria-labelledby="discussion-label" data-pagefind-ignore>
      <h2 class="section-label" id="discussion-label">Discussion</h2>
      <div id="bsky-discussion" aria-live="polite"></div>
    </section>
  </div>
</main>
<script src="/js/bluesky.js" defer></script>
<script defer>
  window.addEventListener('DOMContentLoaded', function () {{
    loadBlueskyThread('{thread}', 'bsky-discussion');{thread_comment}
  }});
</script>
""" + footer


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = sys.argv[1]
    meta, body = parse(src)

    # Optional overrides passed by the caller; sensible fallbacks otherwise.
    desc = meta.get("meta_description") or meta["excerpt"][:155]
    keywords = meta.get("keywords", meta["domain"])
    related = []
    if "--related" in sys.argv:
        raise SystemExit("--related expects the caller to supply labels; edit RELATED below instead")

    out = os.path.join(ROOT, "public", "essays", meta["slug"], "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(build(meta, body, desc, keywords, related))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
