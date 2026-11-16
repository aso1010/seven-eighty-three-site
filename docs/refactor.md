# Lab 783 static architecture

The public directory is `seven-eighty-three-website/`. It runs directly on static hosting: no framework, package installation, compilation, or build step.

- Each HTML head retains the exact embedded Archivo and JetBrains Mono WOFF2 declarations.
- `styles.css` owns shared tokens, content roles, navigation, components and explicit responsive/state variants. Each selector is declared once per media context. No sequential editorial/layout passes.
- `opening.css` is loaded only by the homepage. It preserves the opening geometry, caption, Archivo variable settings and transform origins.
- The opening script retains its 1000ms arrival and 860ms recoil keyframes. It enables one static button. Enter, Space and pointer all use the native button click; an active gesture rejects repeats and reduced-motion changes cancel it.
- `site.js` observes reading position. Native links, fragments, history and scrolling remain browser-owned. No interception, scroll hijacking or hidden content.
- Page-specific components (form, structure table, venture plate) use the same core stylesheet. The generic non-published authoring reference is `subpage-template.html`.
- `schema.json` is the canonical ecosystem graph, embedded identically in all seven pages. It defines the lab, founder, research laboratory, first company, Food API specification and acquisition offer, Universe API framework, websites, pages, breadcrumbs and section indexes. `site.json`, `llms.txt` and `llm.txt` use the same identities and stage claims.
- `/ventures/food-api/` remains the stable public route; the existing Communal Foundation redirects are unchanged.

## Preserved visual constants

Fibonacci tokens (`8, 13, 21, 34, 55, 89, 144, 233`) and phi (`1.618`, `2.618`) govern the existing spatial system. Exact visual preservation takes priority over replacing approved optical/fluid constants: the monolith's gutters, caption's 11–15px clamp and 1.5 line-height, border widths, touch targets, letter spacing, media breakpoints and artwork crop remain intentional exceptions. The desktop slab remains 12 columns: rail 1–3, reading flow 3–11, void 11–13; the existing featured-venture layout retains its deliberate wider image treatment.

## Verification and deployment

Run `python3 tools/validate.py`. The browser regression check is `python3 tools/browser-check.py` in the development environment (Playwright and Chromium); these are verification tools, not website dependencies. Browser checks must cover 390, 1440 and 2048 pixels, plus intermediate breakpoints, reduced motion including live changes, keyboard/pointer recoil, native anchor/history behavior, form validation/drafting and no-JavaScript rendering.

The existing deployment workflow is a normal push to the GitHub `main` branch, followed by the Cloudflare Pages check for that exact commit. Do not force push. Confirm the deployment result before reporting it live.

## Public content and transmission protocol

The homepage now has four sections: Thesis, Architecture, Entities, and Protocol. The six subpages document systems architecture, governance and topology, architectural notes, selected systems, the intake ledger, and the Food API acquisition dossier. Existing fragment identifiers remain as aliases for incoming links.

Universe API descriptions stay at the macro-systems and deterministic-indexing layer. Food API resource paths describe proposed contracts, not live endpoints. Acquisition price, transfer scope, licensing, capital allocation and other unconfirmed terms remain subject to agreement. The existing community return commitment is retained.

The intake requires Entity Name, Structural Bottleneck, Capital/Equity Scope, and Timeline. It drafts an email and does not send it automatically. Both acquisition query aliases continue to prefill the Structural Bottleneck field.

The selected-systems source byte counts measure actual delivered file sizes. A sub-50ms delivery time is a benchmark target, not an asserted measurement. No external traffic, revenue, throughput or latency results are invented.
