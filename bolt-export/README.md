# Knowledge Centre for the Bolt site (React)

The Resources / Knowledge Centre homepage as React + TypeScript components for the Ads Yeti Bolt project (`adsyet-mainsite`). It inherits the site's own CSS (colour and font variables, `.btn`, `.eyebrow`, the gradient blobs, the `.rv` scroll reveals), so it looks like the rest of the site. Everything new is prefixed `kc-` so nothing clashes.

No new packages: it uses `react-router-dom`, which is already installed.

## What's in here

The folder mirrors the Bolt project, so every file goes in the same place.

**New files**

| File | What it is |
|---|---|
| `src/pages/KnowledgeCentre.tsx` | The Knowledge Centre homepage at `/resources/` |
| `src/pages/KcComingSoon.tsx` | Friendly placeholder for article, topic and blog URLs until those pages are built |
| `src/components/knowledge-centre/KcHero.tsx` | Gradient hero with search, popular questions, stats and the waving Yeti |
| `src/components/knowledge-centre/KcSearch.tsx` | Instant as-you-type search (keyboard accessible) |
| `src/components/knowledge-centre/StartHere.tsx` | Three "start here" cards |
| `src/components/knowledge-centre/QuestionTypes.tsx` | Browse by question: the *They Ask, You Answer* Big 5 |
| `src/components/knowledge-centre/TopicGrid.tsx` | Browse by topic, on a cream panel |
| `src/components/knowledge-centre/LatestAnswers.tsx` | Featured article and latest six |
| `src/components/knowledge-centre/ArticleCard.tsx` | Article card, featured card, thumbnail and topic tag |
| `src/components/knowledge-centre/NewsletterStrip.tsx` | Newsletter sign-up |
| `src/components/knowledge-centre/AskTheYeti.tsx` | Question form with the peeking Yeti |
| `src/data/knowledgeCentre.ts` | **All the content**: articles, topics, question types and search |
| `src/hooks/useSeo.ts` | Sets the page title, description, canonical, Open Graph and JSON-LD |
| `src/hooks/useReveal.ts` | Scroll-reveal for the new page |
| `src/lib/submitContact.ts` | Sends forms to the existing `submit-contact-form` Supabase function |
| `src/styles/knowledge-centre.css` | Page styles |
| `src/styles/nav-resources.css` | Resources dropdown styles |
| `public/kc/*.webp` | Yeti poses and Andy's photo, compressed (about 40KB each) |

**Changed files: replace the existing ones**

| File | What changed |
|---|---|
| `src/App.tsx` | Wrapped in `BrowserRouter`. The homepage moved, unchanged, into a `HomePage` component. Added routes for `/resources/` and `/resources/*` |
| `src/components/Navigation.tsx` | Added the **Resources** dropdown. Links changed from `#work` to `/#work`, so they also work from the Resources page |

## Adding it to Bolt

**Option A: GitHub (easiest if Bolt is synced to `adsyet-mainsite`)**
Copy `bolt-export/src` and `bolt-export/public` over the project's `src` and `public` folders, commit, and Bolt picks it up.

**Option B: paste into Bolt**
Upload the files (or the zip) to Bolt and use this prompt:

> Add the Knowledge Centre files I've uploaded. Put each file at the same path shown (src/pages, src/components/knowledge-centre, src/data, src/hooks, src/lib, src/styles, public/kc). Replace src/App.tsx and src/components/Navigation.tsx with the uploaded versions. Don't restyle or rewrite them, and don't install any new packages. Then check /resources/ loads.

Netlify's `/*  /index.html  200` rule in `public/_redirects` already sends `/resources/` to the React app, so no redirect changes are needed.

## Previewing changes here

```bash
./bolt-export/preview.sh /path/to/adsyet-mainsite
# then open http://localhost:5199/resources/
```

This copies the Bolt project to a temp folder (the original is never touched), overlays these files, then runs the type check, lint and build before starting the dev server.

## Editing content

Everything is in `src/data/knowledgeCentre.ts`. Add an article to the `articles` array and it shows up in search, the latest list, and the topic and question-type counts. `featured: true` picks the big card, and `startHere: 1–3` picks the Start Here cards. Apart from "Why are my Facebook ads getting leads but no sales?", the titles are **examples**.

## One thing to know about SEO

The Bolt site is a single-page React app, so a page's HTML is empty until JavaScript runs. `useSeo` sets the title, meta tags and structured data once the page loads. Google runs JavaScript, so it will see all of it. Many AI crawlers (ChatGPT, Perplexity, Claude) don't run JavaScript, so they'd see an empty page.

For the Knowledge Centre to show up in AI answers, the best next step is to **pre-render** the `/resources/` pages at build time, so each URL ships as real HTML. That can be done inside this Vite project later without changing these components. The article pages are where it matters most.

## Next pages

The blog archive, topic pages and article template (already designed in `site/`) are next. Each becomes a component in `src/pages/` and replaces its `/resources/*` placeholder route.
