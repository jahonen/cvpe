#!/usr/bin/env python3
"""
Per-essay Open Graph card generator (1200x630 PNG).

Reads the PUBLISHED title/tag/date from an essay page — not the frontmatter,
since titles are sometimes edited after publication — and renders the house
card via headless Chrome.

Usage:
    python3 tools/og/generate.py <slug> [<slug> ...]
    python3 tools/og/generate.py --all
"""
import html as H
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PUB = os.path.join(ROOT, "public")
OUT_DIR = os.path.join(PUB, "assets", "og")
WORK = os.path.join(ROOT, ".cache", "og")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

TEMPLATE = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1200px;height:630px;background:#1d3557;display:flex;flex-direction:column;
justify-content:space-between;padding:66px 80px;overflow:hidden}}
.eyebrow{{font-family:'JetBrains Mono',monospace;font-size:22px;letter-spacing:.3em;
text-transform:uppercase;color:#c8963c}}
.rule{{height:2px;width:120px;background:#c8963c;margin:26px 0 0}}
.headline{{display:flex;align-items:center;flex:1}}
h1{{font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:78px;line-height:1.14;
color:#f7f5f0;max-height:340px}}
.bottom{{display:flex;justify-content:space-between;align-items:baseline}}
.wordmark{{font-family:'JetBrains Mono',monospace;font-size:26px;letter-spacing:.2em;
text-transform:uppercase;color:#f7f5f0}}
.wordmark span{{color:#c8963c}}
.date{{font-family:'JetBrains Mono',monospace;font-size:20px;letter-spacing:.1em;color:#8fa3bd}}
</style></head><body>
<div><p class="eyebrow">{eyebrow}</p><div class="rule"></div></div>
<div class="headline"><h1 id="h">{title}</h1></div>
<div class="bottom"><span class="wordmark">CVPE<span>.</span>eu</span><span class="date">{date}</span></div>
<script>(function(){{var h=document.getElementById('h');var s=78;
while(h.scrollHeight>340&&s>34){{s-=2;h.style.fontSize=s+'px';}}}})();</script>
</body></html>"""


def extract(slug):
    src = open(os.path.join(PUB, "essays", slug, "index.html")).read()
    def grab(p):
        m = re.search(p, src, re.S)
        return H.unescape(m.group(1)).strip() if m else None
    title = re.sub(r"<[^>]+>", "", grab(r"<article[^>]*>.*?<h1>(.*?)</h1>") or "")
    return title, grab(r'<span class="tag">(.*?)</span>'), grab(r'<time datetime="[\d-]+">(.*?)</time>')


def render(slug):
    os.makedirs(WORK, exist_ok=True); os.makedirs(OUT_DIR, exist_ok=True)
    title, tag, date = extract(slug)
    if not title:
        print(f"  !! no title found for {slug}"); return
    work = os.path.join(WORK, f"{slug}.html")
    open(work, "w").write(TEMPLATE.format(eyebrow=H.escape(tag or "Essay"),
                                          title=H.escape(title), date=H.escape(date or "")))
    out = os.path.join(OUT_DIR, f"{slug}.png")
    subprocess.run([CHROME, "--headless", "--disable-gpu", f"--screenshot={out}",
                    "--window-size=1200,630", "--hide-scrollbars",
                    "--virtual-time-budget=8000", f"file://{work}"], capture_output=True)
    size = os.path.getsize(out) // 1024 if os.path.exists(out) else 0
    print(f"  {slug}.png ({size} KB) — \"{title[:56]}\"")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return 1
    slugs = (sorted(d for d in os.listdir(os.path.join(PUB, "essays"))
                    if os.path.isdir(os.path.join(PUB, "essays", d)))
             if args[0] == "--all" else args)
    for s in slugs:
        render(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
