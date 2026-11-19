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

## Content hierarchy

Use one H1 per page. The homepage keeps its original monolith as the accessible H1. Subpage H1 titles use the reading axis and the `page-title` role. H2 headings retain the section rails. H3 `content-heading` elements introduce related topics; H4 `content-label` elements describe a supporting detail within a topic. Add levels only when the content has that structure. Definition terms and form labels retain their native semantics.

`content-group` and `content-detail` keep headings close to their content. Paragraphs inside the reading flow have a 55ch limit; the 12-column outer grid remains fluid. Entity names use a larger title role, while status and transmission details use their appropriate heading levels. The page index remains observational and identifies the final section when the reader reaches the document end.

## Case Study 00

`/case-study/` documents the laboratory's own production system. It uses the same shared subpage shell and reading hierarchy with a scoped black-on-white palette. Its Content-Security-Policy admits the shared same-origin CSS and navigation script, plus the exact hash of the embedded font stylesheet. The article is declared as a TechArticle in the canonical graph and linked from the homepage, Selected Systems, footer, sitemap, and agent files.

The supplied standalone draft described an earlier single-file, no-JavaScript model. The published case instead describes the current shared-asset architecture and measures its actual uncompressed bytes, graph node count, and three core runtime resources. The attachment's shell patch is not run or published. Recalculate the case-study metrics whenever its source or shared assets change.

Homepage entity features now use one consistent Archivo title role. The dedicated acquisition dossier retains its supplied logo. The opening Seven Eighty Three monolith remains separate and unchanged.

## 783 Hz carrier

The shared header contains one native toggle. It remains hidden and disabled without JavaScript or Web Audio. `site.js` creates an AudioContext, one sine oscillator at 783 Hz, and one gain node only after the first document pointer or keyboard gesture. Touch release retries activation where the browser requires it. A direct toggle gesture is excluded from document activation, preventing a double toggle.

Peak gain is 0.018. Linear 35ms ramps start from the current automation value. Muting fades to zero before suspending the context; unmuting resumes the same nodes. Explicit mute is stored under `lab783CarrierMuted` in sessionStorage. Page restoration reloads that preference. Storage errors leave the local control functional. Native anchors and keyboard input are never intercepted.

Run `python3 tools/test_carrier.py` for real Web Audio graph, ramp timing, gesture, node reuse, session, touch, policy and fallback checks. The carrier loads no media files, requests or external dependencies. Existing opening geometry, SVGs, fonts and animation arrays are unchanged.
