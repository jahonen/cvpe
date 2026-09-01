#!/usr/bin/env python3
"""
IndexNow submission.

Tells participating search engines (Bing, Yandex, Seznam, Naver, Yep) that a
set of URLs changed, instead of waiting for them to recrawl. One POST, no
account, no API key to keep secret: the key is a public file at the site root,
and possession of that file is the whole proof of ownership.

    public/9fc82b96989779e92490c0d31f485df0.txt   <- the key, served publicly
    https://cvpe.eu/9fc82b96989779e92490c0d31f485df0.txt

The key file is discovered by globbing, so rotating the key means dropping in a
new file and deleting the old one — nothing here to edit.

IMPORTANT — order of operations. IndexNow verifies the key file by fetching it
from the live site, and the engines crawl the submitted URLs shortly after. Run
this AFTER the deploy is live, never before: submitting URLs that 404 wastes
the submission and can get the host throttled.

Usage:
    python3 tools/indexnow/submit.py                    # uncommitted changes
    python3 tools/indexnow/submit.py --since HEAD~1     # what a push contains
    python3 tools/indexnow/submit.py --all              # every URL in sitemap.xml
    python3 tools/indexnow/submit.py /essays/foo/ ...   # explicit paths
    python3 tools/indexnow/submit.py --since HEAD~1 --dry-run

The default endpoint is the protocol's neutral shared endpoint, which forwards
to every participating engine. --endpoint accepts an alternative for anyone who
would rather not hand the first hop to a US operator; the EU-operated Seznam
endpoint (https://search.seznam.cz/indexnow) shares submissions identically.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PUB = os.path.join(ROOT, "public")
SITE = "https://cvpe.eu"
HOST = "cvpe.eu"
DEFAULT_ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS = 10_000  # protocol limit per request
KEY_RE = re.compile(r"^[0-9a-f]{8,128}\.txt$")


def find_key():
    """The key file is the only [0-9a-f]{8,128}.txt at the public root."""
    names = [os.path.basename(p) for p in glob.glob(os.path.join(PUB, "*.txt"))]
    keys = [n for n in names if KEY_RE.match(n)]
    if len(keys) != 1:
        raise SystemExit(
            f"expected exactly one IndexNow key file in {PUB} — found {keys or 'none'}.\n"
            "Create one with:\n"
            "    python3 -c \"import secrets;print(secrets.token_hex(16))\"\n"
            "and write it, with no trailing newline, to public/<that value>.txt")
    key = keys[0][:-4]
    body = open(os.path.join(PUB, keys[0])).read().strip()
    if body != key:
        raise SystemExit(f"{keys[0]} must contain exactly its own filename stem; found {body!r}")
    return key


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args],
                          capture_output=True, text=True, check=True).stdout


def path_to_url(rel):
    """public/essays/foo/index.html -> https://cvpe.eu/essays/foo/"""
    if not rel.startswith("public/"):
        return None
    rest = rel[len("public/"):]
    if rest.endswith("/index.html"):
        return f"{SITE}/{rest[:-len('index.html')]}"
    if rest == "index.html":
        return f"{SITE}/"
    if rest.endswith(".html"):                      # e.g. 404.html — not worth submitting
        return None
    return None


def urls_from_git(since):
    if since:
        changed = git("diff", "--name-only", f"{since}..HEAD").split()
    else:
        changed = [line[3:] for line in git("status", "--porcelain").splitlines()]
        changed += git("ls-files", "--others", "--exclude-standard").split()
    return [u for u in (path_to_url(p.strip()) for p in changed if p.strip()) if u]


def urls_from_sitemap():
    xml = open(os.path.join(PUB, "sitemap.xml")).read()
    return re.findall(r"<loc>(.*?)</loc>", xml)


def submit(urls, key, endpoint, dry_run):
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"{SITE}/{key}.txt",
        "urlList": urls,
    }
    body = json.dumps(payload).encode()
    print(f"IndexNow → {endpoint}")
    print(f"  key {key} ({payload['keyLocation']})")
    for u in urls:
        print(f"  {u}")
    if dry_run:
        print(f"\n  dry run — {len(urls)} URL(s) not submitted")
        return 0
    req = urllib.request.Request(endpoint, data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"\n  HTTP {r.status} — {len(urls)} URL(s) submitted")
            return 0
    except urllib.error.HTTPError as e:
        # 400 bad request · 403 key not verifiable at keyLocation · 422 host/key
        # mismatch or URLs not under host · 429 too many requests
        print(f"\n  HTTP {e.code} {e.reason}\n  {e.read().decode(errors='replace')[:500]}",
              file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"\n  network error: {e.reason}", file=sys.stderr)
        return 1


def main():
    ap = argparse.ArgumentParser(description="Submit changed URLs to IndexNow.")
    ap.add_argument("paths", nargs="*", help="explicit site paths, e.g. /essays/foo/")
    ap.add_argument("--all", action="store_true", help="every URL in sitemap.xml")
    ap.add_argument("--since", metavar="REF", help="URLs changed in REF..HEAD")
    ap.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.all:
        urls = urls_from_sitemap()
    elif a.paths:
        urls = [p if p.startswith("http") else f"{SITE}{p if p.startswith('/') else '/' + p}"
                for p in a.paths]
    else:
        urls = urls_from_git(a.since)

    urls = sorted(dict.fromkeys(urls))
    if not urls:
        print("no changed URLs — nothing to submit")
        return 0
    if len(urls) > MAX_URLS:
        raise SystemExit(f"{len(urls)} URLs exceeds the {MAX_URLS} per-request limit")

    return submit(urls, find_key(), a.endpoint, a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
