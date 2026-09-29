# Ads Yeti: Resources / Knowledge Centre

A new **Resources** section for adsyeti.com, replacing the "Knowledge Centre" menu label. It's built around Marcus Sheridan's *They Ask, You Answer* approach: answer every question a buyer asks before they buy, honestly, and make those answers easy to find.

## What's here

| Path | What it is |
|---|---|
| `site/resources/` | **Knowledge Centre hub**: search-first hero, "Start here" guides, browse by question type (the Big 5), browse by topic, latest articles, the Ask the Yeti form |
| `site/resources/blog/` | **Blog archive**: every article, filterable by topic, question type and keyword, with sorting and "show more" |
| `site/resources/topics/<topic>/` | **Topic pillar pages** (Meta ads, Google ads, Tracking, CRM, Landing pages, Strategy) |
| `site/resources/blog/<slug>/` | **Article template**: short-answer box, key takeaways, sticky table of contents, reading progress, inline Yeti CTA, FAQs, author box, related articles |
| `site/partials/header-with-resources-menu.html` | Main menu with the new **Resources** mega menu, ready to paste into the site header |
| `site/assets/` | Shared CSS, JS and Yeti artwork |
| `site/llms.txt`, `site/resources/sitemap.xml`, `site/resources/search-index.json`, `site/resources/blog/feed.xml` | Machine-readable files for AI assistants, search engines and on-site search |
| `kc/` | Source: `articles.json`, article content, and `build.py` which generates everything above |

## Preview it

```bash
python3 kc/build.py
cd site && python3 -m http.server 8000
# open http://localhost:8000/resources/
```

## Adding an article

1. Add an entry to `kc/articles.json` (title as the question people actually ask, a `topic`, a `type`, a date).
2. Add `kc/content/<slug>.html` (body with `<h2 id="...">` sections) and `kc/content/<slug>.json` (`answer`, `takeaways`, `faqs`).
3. Run `python3 kc/build.py`. The hub, archive, topic page, search, sitemap, RSS and `llms.txt` all update.

### Question types (the Big 5)

`cost` Pricing & cost · `problems` Problems & fixes · `comparisons` Comparisons · `reviews` Reviews & best-of · `howto` How-to & explainers.
Aim for a spread. Pricing and comparison articles usually convert best, and they're the ones agencies avoid writing.

## SEO and AI search: what's built in

- **Fully server-rendered HTML.** Nothing depends on JavaScript to show content, so Googlebot, Bing, GPTBot, ClaudeBot and PerplexityBot see everything.
- **Answer-first structure.** Every article opens with a 2–3 sentence "short answer" and key takeaways. That's what Google's AI Overviews, ChatGPT and Perplexity tend to lift and cite.
- **Question-led titles and H2s** that match how people search and prompt.
- **Structured data (JSON-LD):** `Organization`, `WebSite` + `SearchAction`, `CollectionPage`/`Blog` + `ItemList`, `BlogPosting` (with `author` Person, `dateModified`, `speakable`), `FAQPage`, `BreadcrumbList`.
- **E-E-A-T signals:** named author with bio and `rel="author"`, visible published/updated dates, a "spotted something out of date?" note.
- **Topic clusters:** hub → topic pillar pages → articles, with breadcrumbs, related articles and in-content links.
- **Canonicals, Open Graph, `en-GB`, RSS, sitemap and `llms.txt`.**
- **Performance and accessibility:** one small CSS and JS file, no images required (thumbnails are generated in CSS), lazy loading, skip link, keyboard-accessible menu and search, reduced-motion support, and no horizontal scroll on phones.

## Before going live: things to confirm

The live site couldn't be reached from the build environment, so these are placeholders:

- [ ] **Brand colours and fonts:** edit the tokens at the top of `site/assets/css/knowledge-centre.css`.
- [ ] **Yeti artwork:** replace `site/assets/img/yeti.svg` and `yeti-mark.svg` with the official Yeti (same filenames).
- [ ] **Main menu items and URLs:** `MAIN_NAV` in `kc/build.py` (currently Services, Results, About, Resources, Contact, plus Book a call).
- [ ] **Articles:** `kc/articles.json` has 14 *example* titles; only one has a full article written. Swap in real articles (or write these ones).
- [ ] **Andy's photo and LinkedIn:** `AUTHORS` in `kc/build.py` (`image`, `same_as`).
- [ ] **Forms:** the Ask the Yeti and newsletter forms post to `/contact/`. Point them at the GoHighLevel form/webhook.
- [ ] **Redirect** any old Knowledge Centre URLs to `/resources/` with 301s, and add `/resources/sitemap.xml` to the main sitemap index / Search Console.
- [ ] **robots.txt:** make sure GPTBot, ClaudeBot, PerplexityBot and Google-Extended aren't blocked if you want to show up in AI answers.
