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

### Why step 4 matters

DanubeData serves `/css/*` and `/js/*` with `cache-control: max-age=31536000, immutable` — a one-year cache on filenames that never change. An edited stylesheet will *never* reach a returning visitor unless its URL changes. [`tools/version-assets.py`](tools/version-assets.py) appends a content hash (`main.css?v=<hash>`) to every reference in `/public`. HTML itself is served `no-cache`, so a re-stamped page invalidates the old asset immediately.

## Sovereignty

Hosted on DanubeData, EU infrastructure, Romania. No US cloud providers. No CLOUD Act exposure. No tracking, no analytics, no advertising. We practise what we publish.
