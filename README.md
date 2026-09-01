# CVPE.eu — Certa Vizio Pri Eŭropo

*"A Certain Vision of Europe."*

Independent European political essay site by JP Ahonen. Essays, a lexicon of coined terms, and an accountability audit — from the crosshairs of the evergray wars.

## Architecture

No framework. No build pipeline. No node_modules. Pure static HTML/CSS/JS in [`/public`](public/), served directly by DanubeData. A push to `main` triggers auto-deploy.

- [`SPEC.md`](SPEC.md) — the canonical build specification
- [`/content`](content/) — Markdown sources (not served); frontmatter drives regeneration
- [`/public`](public/) — every file is a deployable artefact

## Workflow

1. Add or edit Markdown in `/content`
2. Claude Code regenerates the corresponding HTML in `/public` (plus `sitemap.xml`, `feed.xml`)
3. Regenerate the search index: `npx pagefind --site public --output-path public/pagefind`
4. **If `public/css` or `public/js` changed**, re-stamp the asset versions: `python3 tools/version-assets.py`
5. Commit and push — DanubeData deploys
6. **Once the deploy is live**, ping IndexNow: `python3 tools/indexnow/submit.py --since HEAD~1`

### Why step 4 matters

DanubeData serves `/css/*` and `/js/*` with `cache-control: max-age=31536000, immutable` — a one-year cache on filenames that never change. An edited stylesheet will *never* reach a returning visitor unless its URL changes. [`tools/version-assets.py`](tools/version-assets.py) appends a content hash (`main.css?v=<hash>`) to every reference in `/public`. HTML itself is served `no-cache`, so a re-stamped page invalidates the old asset immediately.

### Why step 6 matters

Sitemaps are a passive invitation; crawlers get to them when they get to them. [IndexNow](https://www.indexnow.org/) is the push version — one POST tells Bing, Yandex, Seznam, Naver, and Yep that specific URLs changed. Ownership is proved by a public key file at the site root ([`public/9fc82b96989779e92490c0d31f485df0.txt`](public/9fc82b96989779e92490c0d31f485df0.txt)); [`tools/indexnow/submit.py`](tools/indexnow/submit.py) finds it by globbing, so rotating the key is a matter of dropping in a new file and deleting the old one.

Order matters. The engines verify the key file, and crawl the submitted URLs, by fetching them from the live site — so this runs **after** the push has deployed, never before. Submitting URLs that still 404 wastes the submission. Run it with `--dry-run` first if in doubt; `--all` resubmits everything in the sitemap, and `--endpoint https://search.seznam.cz/indexnow` routes the first hop through the EU-operated endpoint instead of the default, which shares submissions identically.

## Sovereignty

Hosted on DanubeData, EU infrastructure, Romania. No US cloud providers. No CLOUD Act exposure. No tracking, no analytics, no advertising. We practise what we publish.
