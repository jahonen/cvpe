#!/usr/bin/env python3
"""
Stamp CSS/JS references in /public with a content hash.

DanubeData serves /css/* and /js/* with `cache-control: max-age=31536000,
immutable` — a one-year cache on filenames that never change. Without a
version marker, an edited stylesheet never reaches a returning visitor.
HTML itself is served `no-cache`, so a hash in the query string invalidates
the moment the page reloads.

Run after editing anything in public/css or public/js, before committing:

    python3 tools/version-assets.py
"""
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent / "public"
ASSETS = ["/css/main.css", "/js/bluesky.js", "/js/subscribe.js", "/js/search.js"]


def short_hash(path: pathlib.Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


def main() -> None:
    versions = {}
    for asset in ASSETS:
        f = ROOT / asset.lstrip("/")
        if f.exists():
            versions[asset] = short_hash(f)

    changed = 0
    for html in ROOT.rglob("*.html"):
        text = original = html.read_text()
        for asset, digest in versions.items():
            # Match the asset with or without an existing ?v= stamp
            text = re.sub(
                re.escape(asset) + r"(\?v=[a-f0-9]+)?",
                f"{asset}?v={digest}",
                text,
            )
        if text != original:
            html.write_text(text)
            changed += 1

    for asset, digest in versions.items():
        print(f"  {asset} -> v={digest}")
    print(f"stamped {changed} HTML file(s)")


if __name__ == "__main__":
    main()
