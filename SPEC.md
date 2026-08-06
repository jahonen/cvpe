# CVPE.EU — Claude Code Build Specification
**Version 1.0 — August 2026**
**For use with Claude Code + GitHub + DanubeData**

---

## 0. Build Philosophy

No framework. No build pipeline. No node_modules. Pure static HTML/CSS/JS written directly into `/public`. GitHub push triggers DanubeData auto-deploy. Claude Code regenerates files as content changes.

Every file in `/public` is a deployable artefact. Nothing compiled. Nothing transpiled. Nothing that can break.

---

## 1. Repository Structure

```
cvpe.eu/                          — repository root
├── README.md
├── .gitignore
├── SPEC.md                       — this document
├── content/                      — source content (Markdown, not served)
│   ├── essays/
│   │   └── YYYY-MM-DD-slug.md
│   ├── lexicon/
│   │   └── term-slug.md
│   ├── audit/
│   │   └── slug.md
│   └── quotes.md
└── public/                       — everything served by DanubeData
    ├── index.html
    ├── essays/
    │   ├── index.html
    │   └── [slug]/index.html
    ├── lexicon/
    │   ├── index.html
    │   └── [term]/index.html
    ├── audit/
    │   ├── index.html
    │   └── [slug]/index.html
    ├── guests/index.html
    ├── quotes/index.html
    ├── about/index.html
    ├── subscribe/index.html
    ├── 404.html
    ├── sitemap.xml
    ├── robots.txt
    ├── llms.txt                  — AIO discovery file
    ├── feed.xml                  — RSS feed
    ├── css/main.css
    ├── js/
    │   ├── bluesky.js
    │   ├── search.js
    │   └── subscribe.js
    ├── pagefind/                 — generated search index
    └── assets/
        └── og-default.png        — 1200x630 Open Graph default image
```

---

## 2. Design System

### 2.1 CSS Custom Properties

See `/public/css/main.css` — the canonical implementation. Tokens:

- Colour: `--ink #1a1a1a`, `--paper #f7f5f0`, `--mist #e8e4dc`, `--EU-blue #1d3557`, `--signal #c8963c` (amber — neither East red nor West neon), `--quiet #6b6560`, `--white #ffffff`
- Verdict colours: fail `#c0392b`, partial `#c8963c`, ongoing `#2980b9`, confirmed `#27ae60`
- Typography: `--serif` Playfair Display; `--sans` Inter; `--mono` JetBrains Mono
- Layout: `--max 680px`, `--radius 2px`; spacing scale `--s1…--s12` (0.25rem–3rem)
- Dark mode via `prefers-color-scheme` custom-property overrides
- `prefers-reduced-motion: reduce` kills all animation/transitions

### 2.2 Typography

Google Fonts in every `<head>` (preconnect + `display=swap`):
Playfair Display (400/700/italic), Inter (300/400/500), JetBrains Mono (400).

Roles: serif — headlines, essay titles, definition terms, pull quotes; sans — body, navigation, descriptions; mono — dates, tags, status labels, metadata, code.

Scale classes: `.headline-xl` clamp(2rem,6vw,2.8rem) · `.headline-lg` clamp(1.4rem,4vw,1.8rem) · `.headline-md` 1.2rem · `.body` 1rem/1.7 · `.body-sm` 0.875rem · `.label` 0.7rem mono uppercase · `.meta` 0.75rem mono.

### 2.3 Component Library

`.section-label` (mono eyebrow with bottom border) · `.tag` (amber domain label) · `.badge` + `--confirmed/--pending/--denied` (prediction badges) · `.status-strip` (EU-blue Evergray Status Strip; severity tokens `--status-kinetic/-active/-elevated/-monitoring` colour both the dot and the `.status-level` word, and clear 4.5:1 on the strip ground in both themes. `kinetic` renders as a square, not a dot: declared war is not evergray and is flagged as a distinct category via `.status-note`. The strip keeps a blue ground in both themes, so it uses `--strip-ink`/`--strip-label` rather than `--white`/`--signal`, which invert) · `.masthead` (sticky, `.wordmark` CVPE<span>.</span>eu) · cards, audit entries with vertical verdict labels, prose styles, Bluesky components, subscribe form, search results, footer.

---

## 3. HTML Templates

Every page: full meta set — title `{{PAGE_TITLE}} — CVPE`, description, author JP Ahonen, canonical, Open Graph (og:type website/article, og-default.png image, site_name "CVPE — Certa Vizio Pri Eŭropo", locale en_GB), Twitter summary_large_image, article:* meta on essays/lexicon/audit, JSON-LD (see §4), RSS alternate link, fonts, `/css/main.css`, favicon.

Shared components: skip link (`<a href="#main" class="skip-link">`) first in body; masthead with primary nav (Essays/Lexicon/Audit/About); footer with tagline `"A Certain Vision of Europe."`, full nav, sovereignty meta and predictions-logged meta.

---

## 4. SEO & AIO Specification

### 4.1 Structured Data — JSON-LD

- Site-wide (`index.html`): `WebSite` + `SearchAction` targeting `/essays?q={search_term_string}`; author Person JP Ahonen with Bluesky sameAs.
- Per essay: `Article` with headline, description, author, publisher Organization CVPE, datePublished/dateModified, keywords, articleSection = domain tag, inLanguage en-GB.
- Per lexicon term: `DefinedTerm` in DefinedTermSet "CVPE Lexicon", dateCreated = coined date, creator JP Ahonen.

### 4.2 llms.txt — AIO Discovery

`/public/llms.txt` — canonical copy lives there. Sections: Site, Author, Original concepts (Evergray Wars 27 May 2026; Proximity Politics 31 July 2026; Sovereignty Washing May 2026; Ahonen's Razor 2026; Ownership-Control Criterion May 2026), Key positions, Content links, Permissions (index/summarise/cite with attribution "JP Ahonen, CVPE (cvpe.eu)"; commercial reproduction prohibited).

### 4.3 robots.txt

Allow all; explicit Allow for GPTBot, ClaudeBot, PerplexityBot, Googlebot; Sitemap pointer.

### 4.4 sitemap.xml

Regenerated whenever content changes. Home priority 1.0 weekly; essays 0.9 monthly with `news:news` block; lexicon terms 0.8 yearly.

### 4.5 RSS feed.xml

RSS 2.0 with atom:link self and dc:creator; one `<item>` per essay (title, permalink guid, RFC date, category = domain, description = excerpt).

### 4.6 Per-page SEO targets

| Page | Target query | Title tag pattern |
|---|---|---|
| `/lexicon/evergray-wars` | "evergray wars definition" | Evergray Wars — Definition — CVPE Lexicon |
| `/lexicon/proximity-politics` | "proximity politics EU migration" | Proximity Politics — Definition — CVPE Lexicon |
| `/lexicon/sovereignty-washing` | "sovereignty washing cloud EU" | Sovereignty Washing — Definition — CVPE Lexicon |
| `/lexicon/ahonens-razor` | "Ahonen's Razor political analysis" | Ahonen's Razor — Definition — CVPE Lexicon |
| `/lexicon/ownership-control-criterion` | "CLOUD Act EU sovereignty ownership" | Ownership-Control Criterion — CVPE Lexicon |
| `/audit` | "EU double standards accountability" | Accusation Audit — Where Europe Falls Short — CVPE |
| `/essays` | "European sovereignty essays" | Essays — CVPE |

---

## 5. JavaScript Components

- **bluesky.js** — AT Protocol public API (`public.api.bsky.app`). `loadBlueskyThread(threadUri, containerId)` renders essay discussion threads (depth 50, sorted, escaped, per-reply permalinks, empty/error fallbacks linking to @jpahonen.eurosky.social). `loadRecentPosts(handle, containerId, count)` renders recent posts on the front page. No auth; public posts only.
- **subscribe.js** — single email field, PUT to SendGrid Contacts API. `SENDGRID_API_KEY` must be injected at build time or proxied via a lightweight serverless/PHP endpoint before production hardening; empty key shows a graceful RSS/Bluesky fallback message.
- **search.js** — Pagefind, lazily imported on first keystroke; 8 results max. Index generated with `npx pagefind --site public --output-path public/pagefind` and committed.

---

## 6. Content Templates

Frontmatter schemas for `/content`:

- **Essay**: title, slug, date, modified, domain, excerpt (≤155 chars), bluesky_thread (AT URI), prediction (bool) + prediction_status, reading_time, guest (bool) + guest_name/guest_bio.
- **Lexicon**: term, slug, coined_by, coined_date, coined_context, related[].
- **Audit**: title, slug, verdict (fail/partial/ongoing/confirmed), standard, published, updated.

---

## 7. Page Specifications

- **index.html**: masthead → hero (eyebrow `CERTA VIZIO PRI EŬROPO`; H1 "Europe is a project. *Not a heritage claim.*"; 2-sentence sub; Evergray Status Strip, manually updated) → Latest Essay → Recent Essays → From the Lexicon (3) → Accusation Audit (2) → From Bluesky (3 via bluesky.js) → Subscribe → footer.
- **essays/[slug]/**: domain tag, H1, meta (author · date · reading time), prediction badge if applicable, body prose with EU-blue pull quotes and amber HRs, Bluesky discussion section, footer. (Related-essays block once archive >1.)
- **lexicon/[term]/**: H1 term, coined line (mono amber), related cross-links, definition body, development history, first public appearance, footer.
- **audit/**: H1 "Accusation Audit", sub "Where Europe falls short of its stated values. Evidence-based. Dated. Updated." Entries with vertical verdict label, title, standard, summary, dates.

---

## 8. Accessibility Requirements

Skip link; meaningful alt text; focus-visible states (signal amber outline 2px, offset 3px); ARIA labels on nav; banner/main/contentinfo roles; `<time datetime>` on all dates; contrast ≥4.5:1 body, 3:1 large; prefers-reduced-motion and full dark mode; semantic HTML; one H1 per page with logical H2/H3 nesting.

---

## 9. Performance Targets

Core Web Vitals green on mobile: LCP < 2.5s, CLS < 0.1, INP < 200ms. Fonts preconnected with swap; Pagefind loaded only on search interaction; Bluesky JS deferred; no render-blocking scripts; image dimensions specified; single CSS file.

---

## 10. Launch Checklist

- [x] `/public/index.html` — front page complete
- [x] `/public/essays/index.html` — essays archive
- [x] `/public/lexicon/index.html` — lexicon index
- [x] `/public/lexicon/evergray-wars/index.html`
- [x] `/public/lexicon/proximity-politics/index.html`
- [x] `/public/lexicon/sovereignty-washing/index.html`
- [x] `/public/lexicon/ahonens-razor/index.html`
- [x] `/public/lexicon/ownership-control-criterion/index.html`
- [x] `/public/audit/index.html`
- [x] `/public/audit/digital-sovereignty-package/index.html`
- [x] `/public/about/index.html`
- [x] `/public/quotes/index.html`
- [x] `/public/subscribe/index.html`
- [x] `/public/404.html`
- [x] `/public/sitemap.xml`
- [x] `/public/robots.txt`
- [x] `/public/llms.txt`
- [x] `/public/feed.xml`
- [x] `/public/css/main.css` — complete design system
- [x] `/public/js/bluesky.js`
- [x] `/public/js/subscribe.js`
- [x] `/public/js/search.js`
- [x] `/public/pagefind/` — generated and committed
- [x] `/public/assets/og-default.png` — 1200x630
- [x] `/public/assets/favicon.svg`
- [ ] GitHub → DanubeData integration confirmed and tested
- [ ] cvpe.eu DNS pointed to DanubeData
- [ ] SendGrid account configured, API key secured
- [x] First essay drafted and ready for 1 September 2026
- [x] Five lexicon terms complete
- [x] First audit entry complete
- [ ] Bluesky handle confirmed: @jpahonen.eurosky.social

---

## 11. Sovereignty Statement

CVPE.eu is hosted on DanubeData, EU infrastructure, Romania.
No American cloud providers. No CLOUD Act exposure.
No tracking pixels. No analytics platform. No advertising.
Domain registered through a European registrar.
We practise what we publish.

---

*Specification authored August 2026. Build with Claude Code.*
*"A Certain Vision of Europe."*
