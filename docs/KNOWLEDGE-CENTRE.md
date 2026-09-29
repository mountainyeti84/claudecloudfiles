# Ads Yeti: Resources / Knowledge Centre

A new **Resources** section for adsyeti.com, replacing the "Knowledge Centre" menu label. It's built around Marcus Sheridan's *They Ask, You Answer* approach: answer every question a buyer asks before they buy, honestly, and make those answers easy to find.

The branding is taken from the live Bolt site (`mountainyeti84/adsyet-mainsite`, read-only; nothing there was changed):

- **Colours:** ink `#0B0B0D`, paper `#F6F2EA`, orange `#FF6B00` → amber `#FF8F40` → peach `#FFB25E` gradient, plus ice, mint, coral, lilac and pink accents.
- **Fonts:** Satoshi (Fontshare) and JetBrains Mono.
- **Visual style:** floating pill menu, 28px rounded cards, drifting gradient blobs with film grain, `// MONO EYEBROWS`, cream "paper" panels.
- **The real Yeti:** wave, point, peek, trek, cheer and dizzy poses, converted to WebP (about 40KB each, down from about 600KB).
- **The real logo, favicon, and Andy's photo and bio.**

## What's here

| Path | What it is |
|---|---|
| `site/resources/` | **Knowledge Centre hub**: search-first hero with the waving Yeti, "Start here" guides, browse by question type (the Big 5), browse by topic, latest articles, newsletter, Ask the Yeti |
| `site/resources/blog/` | **Blog archive**: every article, filterable by topic, question type and keyword, with sorting and "show more" |
| `site/resources/topics/<topic>/` | **Topic pillar pages**: Meta ads, Ad creative, Tracking & attribution, Leads/follow-up/bookings, Landing pages, Strategy |
| `site/resources/blog/<slug>/` | **Article template**: short-answer box, key takeaways, sticky table of contents, reading progress, inline Yeti CTA, FAQs, author box, related articles |
| `site/partials/header-with-resources-menu.html` | The menu with the new **Resources** dropdown, as plain HTML |
| `site/assets/` | CSS, JS, Yeti images, logo |
| `site/llms.txt`, `site/resources/sitemap.xml`, `site/resources/search-index.json`, `site/resources/blog/feed.xml` | Machine-readable files for AI assistants, search engines and on-site search |
| `kc/` | Source: `articles.json`, article content, and `build.py` which generates everything above |

## Preview it

```bash
python3 kc/build.py
cd site && python3 -m http.server 8000
# open http://localhost:8000/resources/
```

## Adding an article

1. Add an entry to `kc/articles.json` (the title as the question people actually ask, a `topic`, a `type`, a date).
2. Add `kc/content/<slug>.html` (body with `<h2 id="...">` sections) and `kc/content/<slug>.json` (`answer`, `takeaways`, `faqs`).
3. Run `python3 kc/build.py`. The hub, archive, topic page, search, sitemap, RSS and `llms.txt` all update.

Question types (the Big 5): `cost` · `problems` · `comparisons` · `reviews` · `howto`. Pricing and comparison articles usually convert best, and they're the ones agencies avoid writing.

## Going live on the Bolt site (when you're ready)

The homepage is a React app that renders in the browser. Its HTML is just an empty `<div id="root">`, so crawlers see very little until JavaScript runs. The Resources pages are deliberately **plain, pre-rendered HTML** instead, the same way `/meta-ads-diagnostic-tool/` already works. Search engines and AI crawlers read them instantly.

1. Copy `site/resources/`, `site/assets/` and `site/llms.txt` into the Bolt project's `public/` folder.
2. In `public/_redirects`, add these lines **above** the `/*  /index.html  200` catch-all, so the React app doesn't swallow the pages:
   ```
   /resources   /resources/index.html   200
   /resources/  /resources/index.html   200
   /resources/blog   /resources/blog/index.html   200
   /resources/blog/  /resources/blog/index.html   200
   ```
   (Netlify serves `index.html` for folders automatically, so article and topic URLs work without extra rules.)
3. Add Resources to the homepage menu in `src/components/Navigation.tsx`, between "Why us" and "Contact":
   ```tsx
   <li><a href="/resources/" onClick={() => setMenuOpen(false)}>Resources</a></li>
   ```
4. Submit `https://www.adsyeti.com/resources/sitemap.xml` in Google Search Console.

## SEO and AI search: what's built in

- **Fully server-rendered HTML.** No JavaScript is needed to see content.
- **Answer-first structure.** Every article opens with a 2–3 sentence "short answer" and key takeaways. That's what Google's AI Overviews, ChatGPT and Perplexity tend to lift and cite.
- **Question-led titles and H2s** that match how people search and prompt.
- **Structured data (JSON-LD):** `Organization`, `WebSite` + `SearchAction`, `CollectionPage`/`Blog` + `ItemList`, `BlogPosting` (with author `Person`, `dateModified`, `speakable`), `FAQPage`, `BreadcrumbList`.
- **E-E-A-T signals:** Andy named as author with photo, bio and LinkedIn (`sameAs`), plus visible published and updated dates.
- **Topic clusters:** hub → topic pillar pages → articles, with breadcrumbs, related articles and in-content links.
- **Canonicals, Open Graph, `en-GB`, RSS, sitemap and `llms.txt`.**
- **Performance and accessibility:** one CSS and one JS file, WebP images, lazy loading, a skip link, keyboard-accessible menu and search, reduced-motion support, and no horizontal scroll on phones.

## Still to do

- [ ] **Articles:** `kc/articles.json` has 14 *example* titles; only one has a full article written. Write these or swap in real ones.
- [ ] **Forms:** Ask the Yeti and the newsletter currently send people to the "Let's Chat" wizard (`/?wizard=1`). Connect them to Supabase (`submit-contact-form`) or GoHighLevel.
- [ ] **Facebook and Instagram links** are `#` on the live site, so they're left out here. Add them to `org_ld()` `sameAs` once they exist.
- [ ] **robots.txt:** don't block GPTBot, ClaudeBot, PerplexityBot or Google-Extended if you want to appear in AI answers.
