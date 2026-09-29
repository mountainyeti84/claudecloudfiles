#!/usr/bin/env python3
"""Build the Ads Yeti Resources / Knowledge Centre as static HTML.

    python3 kc/build.py            # writes into site/

Inputs:  kc/articles.json, kc/content/<slug>.html + <slug>.json
Outputs: site/resources/** pages, search index, sitemap, site/llms.txt

Every page is fully rendered HTML (no client-side rendering), so Google, Bing
and AI crawlers (GPTBot, ClaudeBot, PerplexityBot…) can read everything.
"""
import html
import json
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "kc"
OUT = ROOT / "site"

# --------------------------------------------------------------------------
# Site settings: check these against the live site
# --------------------------------------------------------------------------
SITE = {
    "url": "https://www.adsyeti.com",
    "name": "Ads Yeti",
    "logo": "/assets/img/yeti-mark.svg",
    "cta_label": "Book a call",
    "cta_url": "/contact/",
    "hub_title": "Resources",
    "hub_path": "/resources/",
    "blog_path": "/resources/blog/",
}
AUTHORS = {
    "andy": {
        "name": "Andy Moore",
        "role": "Founder, Ads Yeti",
        "url": "/about/",
        "image": "",  # e.g. /assets/img/andy-moore.jpg
        "bio": "Andy runs Ads Yeti and has spent a slightly unreasonable amount of his life inside Meta and Google ad accounts, "
               "including spending his own company's money on them. He cares less about which platform claims the sale and more "
               "about what actually helped the business grow.",
        "same_as": [],  # e.g. ["https://www.linkedin.com/in/..."]
    }
}
# Main menu. "Knowledge Centre" is relabelled "Resources" and gets a mega menu.
MAIN_NAV = [
    ("Services", "/services/"),
    ("Results", "/case-studies/"),
    ("About", "/about/"),
    ("Resources", None),  # mega menu
    ("Contact", "/contact/"),
]
TOPICS = {
    "meta":     {"name": "Meta ads", "icon": "📣", "blurb": "Facebook and Instagram ads that turn into enquiries and sales, not just clicks."},
    "google":   {"name": "Google ads", "icon": "🔎", "blurb": "Search, Performance Max and YouTube: catching demand that already exists."},
    "tracking": {"name": "Tracking & attribution", "icon": "📊", "blurb": "Working out what actually drove the sale when every platform claims the trophy."},
    "crm":      {"name": "Leads, CRM & follow-up", "icon": "🤝", "blurb": "What happens after the click: speed to lead, nurture and GoHighLevel."},
    "landing":  {"name": "Landing pages & funnels", "icon": "🧭", "blurb": "Pages and forms that turn paid traffic into qualified enquiries."},
    "strategy": {"name": "Strategy for founders", "icon": "🧠", "blurb": "Budgets, channels, hiring and the commercial decisions behind the ads."},
}
# They Ask, You Answer: "The Big 5" questions buyers ask before they buy.
TYPES = {
    "cost":        {"name": "Pricing & cost", "icon": "💷", "blurb": "What things really cost, and why."},
    "problems":    {"name": "Problems & fixes", "icon": "🛠️", "blurb": "What goes wrong, and how to sort it."},
    "comparisons": {"name": "Comparisons", "icon": "⚖️", "blurb": "This vs that, honestly compared."},
    "reviews":     {"name": "Reviews & best-of", "icon": "⭐", "blurb": "Tools and tactics we'd actually use."},
    "howto":       {"name": "How-to & explainers", "icon": "📘", "blurb": "Plain-English, step-by-step."},
}
TOPIC_CSS = {k: f"c-{k}" for k in TOPICS}

e = html.escape


def abs_url(path):
    return SITE["url"] + path


def article_url(a):
    return f"{SITE['blog_path']}{a['slug']}/"


def fmt_date(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%-d %B %Y")


def jsonld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/") + "</script>"


def org_ld():
    return {"@type": "Organization", "@id": abs_url("/#organization"), "name": SITE["name"], "url": abs_url("/"),
            "logo": abs_url(SITE["logo"])}


def breadcrumb_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": abs_url(path)} for i, (name, path) in enumerate(items)]}


def breadcrumbs_html(items, light=False):
    lis = []
    for i, (name, path) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li><span aria-current="page">{e(name)}</span></li>')
        else:
            lis.append(f'<li><a href="{path}">{e(name)}</a></li>')
    cls = "breadcrumbs breadcrumbs--light" if light else "breadcrumbs"
    return f'<nav class="{cls}" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'


CHEVRON = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'


def header_html(active="Resources"):
    items = []
    for label, url in MAIN_NAV:
        if url is None:
            topic_links = "".join(
                f'<a class="mega__link" href="{SITE["hub_path"]}topics/{k}/"><span class="mega__icon" aria-hidden="true">{t["icon"]}</span>'
                f'<span><strong>{e(t["name"])}</strong></span></a>' for k, t in list(TOPICS.items())[:4])
            items.append(f'''<li class="nav__item nav__item--has-mega">
  <button class="nav__link" aria-expanded="false" aria-controls="mega-resources"{' aria-current="page"' if active == label else ''}>{label} {CHEVRON}</button>
  <div class="mega" id="mega-resources">
    <div class="mega__col">
      <h3>Resources</h3>
      <a class="mega__link" href="{SITE["hub_path"]}"><span class="mega__icon" aria-hidden="true">🏔️</span><span><strong>Knowledge Centre</strong><span>Every question we get asked, answered honestly.</span></span></a>
      <a class="mega__link" href="{SITE["blog_path"]}"><span class="mega__icon" aria-hidden="true">📝</span><span><strong>Blog</strong><span>All articles, filterable by topic and question.</span></span></a>
      <h3>Popular topics</h3>
      {topic_links}
    </div>
    <div class="mega__feature">
      <span class="eyebrow">Start here</span>
      <h4>Why are my Facebook ads getting leads but no sales?</h4>
      <p>The most common problem we see, and where to look first.</p>
      <a href="{SITE["blog_path"]}why-facebook-ads-get-leads-but-no-sales/">Read the answer →</a>
      <img class="yeti" src="/assets/img/yeti.svg" alt="" width="88" height="96">
    </div>
  </div>
</li>''')
        else:
            cur = ' aria-current="page"' if active == label else ""
            items.append(f'<li class="nav__item"><a class="nav__link" href="{url}"{cur}>{label}</a></li>')
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container site-header__inner">
    <a class="logo" href="/" aria-label="{SITE['name']} home"><img src="{SITE['logo']}" alt="" width="40" height="40">{SITE['name']}</a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>
    <nav class="nav" id="site-nav" aria-label="Main">
      <ul class="nav__list">{"".join(items)}</ul>
      <a class="btn btn--accent nav__cta" href="{SITE['cta_url']}">{SITE['cta_label']}</a>
    </nav>
  </div>
</header>'''


def footer_html():
    topic_lis = "".join(f'<li><a href="{SITE["hub_path"]}topics/{k}/">{e(t["name"])}</a></li>' for k, t in TOPICS.items())
    type_lis = "".join(f'<li><a href="{SITE["blog_path"]}?type={k}">{e(t["name"])}</a></li>' for k, t in TYPES.items())
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a class="logo" href="/"><img src="{SITE['logo']}" alt="" width="40" height="40">{SITE['name']}</a>
        <p style="margin-top:14px;max-width:34ch">Founder-led paid ads, judged on what happens after the click.</p>
      </div>
      <div><h2>Resources</h2><ul><li><a href="{SITE['hub_path']}">Knowledge Centre</a></li><li><a href="{SITE['blog_path']}">Blog</a></li><li><a href="{SITE['hub_path']}#ask">Ask a question</a></li></ul></div>
      <div><h2>Topics</h2><ul>{topic_lis}</ul></div>
      <div><h2>Questions</h2><ul>{type_lis}</ul></div>
    </div>
    <div class="footer-bottom"><span>© {date.today().year} {SITE['name']}</span><span><a href="/privacy/">Privacy</a> · <a href="/sitemap.xml">Sitemap</a></span></div>
  </div>
</footer>'''


def page(title, description, path, body, ld_graph, og_type="website", extra_head=""):
    canonical = abs_url(path)
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE['name']}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{SITE['name']} Blog" href="{SITE['blog_path']}feed.xml">
<link rel="icon" href="/assets/img/yeti-mark.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/knowledge-centre.css">
{extra_head}{jsonld({"@context": "https://schema.org", "@graph": ld_graph})}
</head>
<body>
{header_html()}
<main id="main">
{body}
</main>
{footer_html()}
<script src="/assets/js/knowledge-centre.js" defer></script>
</body>
</html>
'''


# --------------------------------------------------------------------------
# Components
# --------------------------------------------------------------------------
def thumb(a, big=False):
    t = TOPICS[a["topic"]]
    img = f'<img src="{e(a["image"])}" alt="" loading="lazy">' if a.get("image") else ""
    return (f'<div class="thumb {TOPIC_CSS[a["topic"]]}" aria-hidden="true"><span class="thumb__q">{e(TYPES[a["type"]]["name"])}</span>'
            f'<span class="thumb__icon">{t["icon"]}</span>{img}</div>')


def card(a):
    t, ty = TOPICS[a["topic"]], TYPES[a["type"]]
    return f'''<article class="card" data-topic="{a['topic']}" data-type="{a['type']}" data-date="{a['date']}" data-minutes="{a['minutes']}" data-popularity="{a.get('popularity', 0)}">
  {thumb(a)}
  <div class="card__body">
    <div class="tags"><a class="tag {TOPIC_CSS[a['topic']]}" href="{SITE['hub_path']}topics/{a['topic']}/">{e(t['name'])}</a></div>
    <h3><a href="{article_url(a)}">{e(a['title'])}</a></h3>
    <p>{e(a['summary'])}</p>
    <div class="meta"><time datetime="{a['date']}">{fmt_date(a['date'])}</time><span class="dot">{a['minutes']} min read</span></div>
  </div>
</article>'''


def featured_card(a):
    t = TOPICS[a["topic"]]
    return f'''<a class="featured" href="{article_url(a)}">
  {thumb(a, big=True)}
  <div class="featured__body">
    <div class="tags"><span class="tag {TOPIC_CSS[a['topic']]}">{e(t['name'])}</span><span class="tag tag--plain">Most read</span></div>
    <h3>{e(a['title'])}</h3>
    <p>{e(a['summary'])}</p>
    <div class="meta"><span>By {e(AUTHORS['andy']['name'])}</span><span class="dot">{a['minutes']} min read</span></div>
    <span class="link-arrow">Read the answer</span>
  </div>
</a>'''


def search_form(placeholder="Ask a question, e.g. “why is my cost per lead so high?”"):
    return f'''<form class="search" role="search" action="{SITE['blog_path']}" method="get" data-search>
  <label class="visually-hidden" for="kc-search">Search the Knowledge Centre</label>
  <div class="search__field">
    <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 20l-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    <input class="search__input" id="kc-search" name="q" type="search" autocomplete="off" placeholder="{e(placeholder)}" role="combobox" aria-expanded="false" aria-controls="kc-search-results" aria-autocomplete="list">
    <button class="btn btn--accent search__btn" type="submit">Search</button>
  </div>
  <ul class="search__results" id="kc-search-results" role="listbox" hidden></ul>
</form>'''


def ask_block():
    return f'''<section class="section" id="ask" aria-labelledby="ask-title">
  <div class="container">
    <div class="ask">
      <img class="yeti yeti--float" src="/assets/img/yeti.svg" alt="" width="200" height="218" loading="lazy">
      <div>
        <span class="eyebrow">Ask the Yeti</span>
        <h2 id="ask-title">Can't find your answer? Ask us.</h2>
        <p>If you're wondering about it, other founders are too. Send us your question about ads, tracking or leads and we'll answer it here, honestly, even if the honest answer is "you don't need an agency for that".</p>
        <form action="/contact/" method="post">
          <label class="visually-hidden" for="ask-q">Your question</label>
          <textarea id="ask-q" name="question" required placeholder="What would you like to know?"></textarea>
          <label class="visually-hidden" for="ask-email">Email (optional)</label>
          <input id="ask-email" name="email" type="email" placeholder="Email, if you'd like a reply">
          <button class="btn btn--accent" type="submit">Send my question</button>
        </form>
        <small>We never share your details. We'll let you know when your answer goes live.</small>
      </div>
    </div>
  </div>
</section>'''


def newsletter_block():
    return '''<div class="container"><div class="newsletter">
  <div><h3>New answers, once a fortnight</h3><p>One useful email. No fluff, and unsubscribing takes one click.</p></div>
  <form action="/contact/" method="post"><label class="visually-hidden" for="nl-email">Email address</label>
    <input id="nl-email" name="email" type="email" placeholder="you@company.co.uk" required><button class="btn btn--accent" type="submit">Subscribe</button></form>
</div></div>'''


def filters_html(show_topics=True):
    chips = ""
    if show_topics:
        chips = '<div class="chips" role="group" aria-label="Filter by topic"><button class="chip" type="button" data-filter-topic="all" aria-pressed="true">All topics</button>' + "".join(
            f'<button class="chip" type="button" data-filter-topic="{k}" aria-pressed="false">{e(t["name"])}</button>' for k, t in TOPICS.items()) + "</div>"
    types = '<option value="all">All question types</option>' + "".join(f'<option value="{k}">{e(t["name"])}</option>' for k, t in TYPES.items())
    return f'''<div class="filters">
  {chips}
  <div class="filters__right">
    <label class="visually-hidden" for="f-text">Filter articles</label><input id="f-text" type="search" placeholder="Filter by keyword…" data-filter-text>
    <label class="visually-hidden" for="f-type">Question type</label><select id="f-type" data-filter-type>{types}</select>
    <label class="visually-hidden" for="f-sort">Sort</label><select id="f-sort" data-sort><option value="latest">Newest first</option><option value="popular">Most read</option><option value="quick">Quick reads</option></select>
  </div>
</div>
<p class="results-count" aria-live="polite" data-results-count></p>'''


def no_results_html():
    return f'''<div class="no-results" data-no-results hidden>
  <img class="yeti" src="/assets/img/yeti.svg" alt="" width="140" height="152">
  <h3>The Yeti's searched everywhere…</h3>
  <p>We haven't answered that one yet. <a href="{SITE['hub_path']}#ask">Ask us</a> and we'll write it.</p>
</div>'''


def item_list_ld(arts, name):
    return {"@type": "ItemList", "name": name, "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": abs_url(article_url(a)), "name": a["title"]} for i, a in enumerate(arts)]}


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def build_hub(arts):
    by_date = sorted(arts, key=lambda a: a["date"], reverse=True)
    featured = next(a for a in arts if a.get("featured"))
    start = sorted([a for a in arts if a.get("start_here")], key=lambda a: a["start_here"])
    latest = [a for a in by_date if a is not featured][:6]
    popular_qs = sorted(arts, key=lambda a: -a.get("popularity", 0))[:4]

    start_cards = "".join(f'''<a class="start-card" href="{article_url(a)}"><span class="start-card__num">START HERE · 0{i + 1}</span>
<h3>{e(a['title'])}</h3><p>{e(a['summary'])}</p><span class="link-arrow">Read</span></a>''' for i, a in enumerate(start))
    qtypes = "".join(f'''<a class="qtype" href="{SITE['blog_path']}?type={k}"><span class="qtype__icon" aria-hidden="true">{t['icon']}</span>
<strong>{e(t['name'])}</strong><span>{e(t['blurb'])}</span><em>{sum(1 for a in arts if a['type'] == k)} answers →</em></a>''' for k, t in TYPES.items())
    topics = "".join(f'''<a class="topic {TOPIC_CSS[k]}" href="{SITE['hub_path']}topics/{k}/"><span class="topic__icon" aria-hidden="true">{t['icon']}</span>
<span><h3>{e(t['name'])}</h3><p>{e(t['blurb'])}</p><small>{sum(1 for a in arts if a['topic'] == k)} articles</small></span></a>''' for k, t in TOPICS.items())
    pq = "".join(f'<a href="{article_url(a)}">{e(a["title"])}</a>' for a in popular_qs[:3])

    crumbs = [("Home", "/"), ("Resources", SITE["hub_path"])]
    body = f'''<section class="hero">
  <div class="container hero__inner">
    <div>
      {breadcrumbs_html(crumbs)}
      <h1>Ask us anything about paid ads. <em>We'll answer it honestly.</em></h1>
      <p class="hero__lede">The Ads Yeti Knowledge Centre. Straight answers to the questions founders ask us about Meta, Google, tracking and turning leads into customers, including the ones most agencies would rather you didn't ask.</p>
      {search_form()}
      <div class="popular-qs"><span>Popular:</span>{pq}</div>
      <div class="hero__stats">
        <div><strong>{len(arts)}</strong>answers</div>
        <div><strong>{len(TOPICS)}</strong>topics</div>
        <div><strong>0</strong>sales pitches in disguise</div>
      </div>
    </div>
    <img class="hero__yeti yeti--float" src="/assets/img/yeti.svg" alt="The Ads Yeti mascot" width="320" height="349">
  </div>
</section>

<section aria-labelledby="start-title">
  <div class="container">
    <h2 id="start-title" class="visually-hidden">Start here</h2>
    <div class="start-grid">{start_cards}</div>
  </div>
</section>

<section class="section" aria-labelledby="qtypes-title">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Browse by question</span><h2 id="qtypes-title">The questions you'd ask before hiring anyone</h2>
    <p>Price, problems, comparisons, reviews and how-tos. If it's on your mind before you spend money, it's in here.</p></div></div>
    <div class="qtypes">{qtypes}</div>
  </div>
</section>

<section class="section section--snow" aria-labelledby="topics-title">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Browse by topic</span><h2 id="topics-title">From the ad to the sale</h2>
    <p>We follow the whole journey, so the Knowledge Centre does too: ad, lead, follow-up, conversation, customer.</p></div></div>
    <div class="topics">{topics}</div>
  </div>
</section>

<section class="section" aria-labelledby="latest-title">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">From the blog</span><h2 id="latest-title">Latest answers</h2></div>
      <a class="link-arrow" href="{SITE['blog_path']}">See all {len(arts)} articles</a></div>
    {featured_card(featured)}
    <div class="cards">{"".join(card(a) for a in latest)}</div>
  </div>
</section>

{newsletter_block()}
{ask_block()}'''

    graph = [
        org_ld(),
        {"@type": "WebSite", "@id": abs_url("/#website"), "url": abs_url("/"), "name": SITE["name"], "publisher": {"@id": abs_url("/#organization")},
         "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": abs_url(SITE["blog_path"] + "?q={search_term_string}")},
                             "query-input": "required name=search_term_string"}},
        {"@type": "CollectionPage", "@id": abs_url(SITE["hub_path"]), "url": abs_url(SITE["hub_path"]), "name": "Ads Yeti Knowledge Centre",
         "description": "Honest answers to the questions founders ask about Meta ads, Google ads, tracking and lead follow-up.",
         "isPartOf": {"@id": abs_url("/#website")}, "inLanguage": "en-GB",
         "mainEntity": item_list_ld(by_date, "Latest articles")},
        breadcrumb_ld(crumbs),
    ]
    write(SITE["hub_path"], page(
        "Resources: The Ads Yeti Knowledge Centre | Paid Ads Questions Answered",
        "Honest answers to the questions founders ask about Meta ads, Google ads, tracking, pricing and turning leads into customers. From the team at Ads Yeti.",
        SITE["hub_path"], body, graph))


def build_blog(arts):
    by_date = sorted(arts, key=lambda a: a["date"], reverse=True)
    crumbs = [("Home", "/"), ("Resources", SITE["hub_path"]), ("Blog", SITE["blog_path"])]
    body = f'''<section class="hero hero--compact">
  <div class="container hero__inner">
    <div>
      {breadcrumbs_html(crumbs)}
      <h1>The Ads Yeti blog</h1>
      <p class="hero__lede">Every article we've written, in one place. Filter by topic or by the kind of question you're asking.</p>
      {search_form("Search all articles…")}
    </div>
    <img class="hero__yeti yeti--float" src="/assets/img/yeti.svg" alt="" width="190" height="207">
  </div>
</section>
<section class="section" style="padding-top:40px" aria-label="All articles">
  <div class="container">
    {filters_html()}
    <div class="cards" data-filter-grid>{"".join(card(a) for a in by_date)}</div>
    {no_results_html()}
    <div class="load-more"><button class="btn btn--outline" type="button" data-load-more>Show more answers</button></div>
  </div>
</section>
{newsletter_block()}
{ask_block()}'''
    graph = [org_ld(), {"@type": ["CollectionPage", "Blog"], "@id": abs_url(SITE["blog_path"]), "url": abs_url(SITE["blog_path"]),
                        "name": "The Ads Yeti blog", "publisher": {"@id": abs_url("/#organization")}, "inLanguage": "en-GB",
                        "mainEntity": item_list_ld(by_date, "All articles")}, breadcrumb_ld(crumbs)]
    write(SITE["blog_path"], page("Blog: Meta Ads, Google Ads & Lead Generation Articles | Ads Yeti",
                                  "Every Ads Yeti article on Meta ads, Google ads, tracking, landing pages and lead follow-up, filterable by topic and question type.",
                                  SITE["blog_path"], body, graph))


def build_topic(key, arts):
    t = TOPICS[key]
    mine = sorted([a for a in arts if a["topic"] == key], key=lambda a: a["date"], reverse=True)
    path = f"{SITE['hub_path']}topics/{key}/"
    crumbs = [("Home", "/"), ("Resources", SITE["hub_path"]), (t["name"], path)]
    # Group by question type: a mini "pillar page" that reads well for people and AI
    groups = ""
    for k, ty in TYPES.items():
        items = [a for a in mine if a["type"] == k]
        if items:
            groups += f'<li><strong>{e(ty["name"])}:</strong> ' + ", ".join(f'<a href="{article_url(a)}">{e(a["title"])}</a>' for a in items) + "</li>"
    body = f'''<section class="hero hero--compact">
  <div class="container hero__inner">
    <div>
      {breadcrumbs_html(crumbs)}
      <span class="eyebrow" style="margin-top:18px">{t['icon']} Topic</span>
      <h1>{e(t['name'])}</h1>
      <p class="hero__lede">{e(t['blurb'])}</p>
    </div>
    <img class="hero__yeti yeti--float" src="/assets/img/yeti.svg" alt="" width="190" height="207">
  </div>
</section>
<section class="section" style="padding-top:40px">
  <div class="container">
    <div class="takeaways" style="max-width:none"><h2>Everything we've answered on {e(t['name'].lower())}</h2><ul>{groups}</ul></div>
    {filters_html(show_topics=False)}
    <div class="cards" data-filter-grid>{"".join(card(a) for a in mine)}</div>
    {no_results_html()}
    <div class="load-more"><button class="btn btn--outline" type="button" data-load-more>Show more answers</button></div>
  </div>
</section>
{ask_block()}'''
    graph = [org_ld(), {"@type": "CollectionPage", "@id": abs_url(path), "url": abs_url(path), "name": f"{t['name']}: questions answered",
                        "about": {"@type": "Thing", "name": t["name"]}, "inLanguage": "en-GB", "mainEntity": item_list_ld(mine, t["name"])},
             breadcrumb_ld(crumbs)]
    write(path, page(f"{t['name']}: Questions Answered | Ads Yeti Knowledge Centre", f"{t['blurb']} Honest answers from Ads Yeti.", path, body, graph))


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def build_article(a, arts):
    body_html = (SRC / "content" / a["body"]).read_text()
    extra = json.loads((SRC / "content" / (a["slug"] + ".json")).read_text())
    author = AUTHORS[a.get("author", "andy")]
    t, ty = TOPICS[a["topic"]], TYPES[a["type"]]
    path = article_url(a)
    crumbs = [("Home", "/"), ("Resources", SITE["hub_path"]), ("Blog", SITE["blog_path"]), (t["name"], f"{SITE['hub_path']}topics/{a['topic']}/")]

    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body_html)
    toc = "".join(f'<li><a href="#{i}">{h}</a></li>' for i, h in heads + [("faqs", "Frequently asked questions")])

    # Insert the inline CTA roughly halfway through the article
    cta = f'''<aside class="inline-cta" aria-label="Talk to Ads Yeti"><img class="yeti" src="/assets/img/yeti.svg" alt="" width="96" height="105" loading="lazy">
<div><h3>Want us to follow your leads through for you?</h3><p>We'll look at your ads, your forms and what happens after the enquiry, then tell you honestly where the sales are leaking.</p>
<a class="btn btn--accent" href="{SITE['cta_url']}">{SITE['cta_label']}</a></div></aside>'''
    parts = body_html.split("<h2 ")
    mid = max(1, len(parts) // 2)
    body_html = "<h2 ".join(parts[:mid]) + cta + "<h2 " + "<h2 ".join(parts[mid:])

    faqs = "".join(f'<details><summary>{e(f["q"])}</summary><div><p>{e(f["a"])}</p></div></details>' for f in extra["faqs"])
    takeaways = "".join(f"<li>{e(x)}</li>" for x in extra["takeaways"])
    related = [x for x in sorted(arts, key=lambda x: (x["topic"] != a["topic"], -x.get("popularity", 0))) if x is not a][:3]
    updated = a.get("updated", a["date"])
    avatar = f'<img class="avatar" src="{author["image"]}" alt="">' if author["image"] else '<img class="avatar" src="/assets/img/yeti-mark.svg" alt="">'
    words = len(re.sub("<[^>]+>", " ", body_html).split())

    body = f'''<div class="progress" aria-hidden="true"></div>
<header class="article-hero">
  <div class="container">
    {breadcrumbs_html(crumbs, light=True)}
    <div class="tags" style="margin-top:18px"><a class="tag {TOPIC_CSS[a['topic']]}" href="{SITE['hub_path']}topics/{a['topic']}/">{e(t['name'])}</a><a class="tag tag--plain" href="{SITE['blog_path']}?type={a['type']}">{e(ty['name'])}</a></div>
    <h1>{e(a['title'])}</h1>
    <p class="standfirst">{e(a['summary'])}</p>
    <div class="byline">{avatar}<div><strong><a href="{author['url']}" rel="author">{e(author['name'])}</a></strong>{e(author['role'])}</div>
      <span class="byline__sep" aria-hidden="true"></span>
      <div>Updated <time datetime="{updated}">{fmt_date(updated)}</time><br>{a['minutes']} min read</div></div>
  </div>
</header>
<div class="container article-layout">
  <article class="prose" data-article>
    <section class="answer-box" aria-labelledby="short-answer"><h2 class="answer-box__label" id="short-answer" style="font-size:.75rem;margin:0 0 10px">⚡ The short answer</h2><p>{e(extra['answer'])}</p></section>
    <section class="takeaways"><h2>Key takeaways</h2><ul>{takeaways}</ul></section>
    {body_html}
    <section class="faq" aria-labelledby="faqs"><h2 id="faqs">Frequently asked questions</h2>{faqs}</section>
    <section class="author-box" aria-label="About the author">{avatar}<div><h3>{e(author['name'])}</h3><div class="author-box__role">{e(author['role'])}</div>
      <p>{e(author['bio'])}</p><a href="{author['url']}">More about Andy →</a></div></section>
    <p class="updated-note">First published <time datetime="{a['date']}">{fmt_date(a['date'])}</time>. Last reviewed and updated <time datetime="{updated}">{fmt_date(updated)}</time>. Spotted something out of date? <a href="{SITE['hub_path']}#ask">Tell us</a>.</p>
  </article>
  <aside class="article-aside">
    <div class="aside-sticky">
      <nav class="toc" aria-label="On this page"><h2>On this page</h2><ol>{toc}</ol></nav>
      <div class="aside-cta"><img class="yeti" src="/assets/img/yeti.svg" alt="" width="76" height="83"><h3>Leads but no sales?</h3><p>Get a straight answer on where yours are going.</p><a class="btn btn--accent" href="{SITE['cta_url']}">{SITE['cta_label']}</a></div>
      <div class="share"><span>Share:</span>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url={e(abs_url(path))}" target="_blank" rel="noopener" aria-label="Share on LinkedIn">in</a>
        <a href="mailto:?subject={e(a['title'])}&amp;body={e(abs_url(path))}" aria-label="Share by email">✉</a>
        <button type="button" data-copy-link aria-label="Copy link">🔗</button></div>
    </div>
  </aside>
</div>
<section class="section section--snow" aria-labelledby="related-title">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Keep reading</span><h2 id="related-title">Related answers</h2></div><a class="link-arrow" href="{SITE['hub_path']}topics/{a['topic']}/">More on {e(t['name'].lower())}</a></div>
    <div class="cards">{"".join(card(r) for r in related)}</div>
  </div>
</section>
{ask_block()}'''

    person = {"@type": "Person", "@id": abs_url(author["url"] + "#person"), "name": author["name"], "jobTitle": author["role"], "url": abs_url(author["url"]),
              "worksFor": {"@id": abs_url("/#organization")}}
    if author["same_as"]:
        person["sameAs"] = author["same_as"]
    graph = [
        org_ld(), person,
        {"@type": "BlogPosting", "@id": abs_url(path) + "#article", "mainEntityOfPage": abs_url(path), "headline": a["title"],
         "description": a["summary"], "abstract": extra["answer"], "datePublished": a["date"], "dateModified": updated,
         "author": {"@id": person["@id"]}, "publisher": {"@id": abs_url("/#organization")}, "inLanguage": "en-GB",
         "articleSection": t["name"], "keywords": ", ".join(a.get("keywords", [])), "wordCount": words,
         "timeRequired": f"PT{a['minutes']}M", "isPartOf": {"@id": abs_url(SITE["blog_path"])},
         "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".answer-box", ".takeaways"]}},
        {"@type": "FAQPage", "@id": abs_url(path) + "#faq",
         "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in extra["faqs"]]},
        breadcrumb_ld(crumbs + [(a["title"], path)]),
    ]
    head = (f'<meta property="article:published_time" content="{a["date"]}">\n<meta property="article:modified_time" content="{updated}">\n'
            f'<meta property="article:section" content="{e(t["name"])}">\n<meta name="author" content="{e(author["name"])}">\n')
    write(path, page(f"{a['title']} | Ads Yeti", a["summary"], path, body, graph, og_type="article", extra_head=head))


# --------------------------------------------------------------------------
# Machine-readable files: search index, sitemap, RSS, llms.txt
# --------------------------------------------------------------------------
def build_feeds(arts):
    by_date = sorted(arts, key=lambda a: a["date"], reverse=True)
    idx = [{"title": a["title"], "summary": a["summary"], "url": article_url(a), "topic": TOPICS[a["topic"]]["name"],
            "type": TYPES[a["type"]]["name"], "keywords": a.get("keywords", [])} for a in by_date]
    (OUT / "resources" / "search-index.json").write_text(json.dumps(idx, ensure_ascii=False))

    urls = [(SITE["hub_path"], max(a["date"] for a in arts)), (SITE["blog_path"], max(a["date"] for a in arts))]
    urls += [(f"{SITE['hub_path']}topics/{k}/", max((a["date"] for a in arts if a["topic"] == k), default=None)) for k in TOPICS]
    urls += [(article_url(a), a.get("updated", a["date"])) for a in arts if a.get("body")]
    sm = "".join(f"<url><loc>{abs_url(u)}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>\n" for u, d in urls)
    (OUT / "resources" / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')

    def rfc822(d):
        return datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0000")
    items = "".join(f"<item><title>{e(a['title'])}</title><link>{abs_url(article_url(a))}</link><guid>{abs_url(article_url(a))}</guid>"
                    f"<pubDate>{rfc822(a['date'])}</pubDate><description>{e(a['summary'])}</description></item>\n" for a in by_date if a.get("body"))
    (OUT / "resources" / "blog" / "feed.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{SITE["name"]} Blog</title><link>{abs_url(SITE["blog_path"])}</link>'
        f"<description>Honest answers about paid ads, tracking and lead follow-up.</description><language>en-gb</language>\n{items}</channel></rss>\n")

    # llms.txt: a plain-text map of the Knowledge Centre for AI assistants (llmstxt.org)
    lines = [f"# {SITE['name']}", "",
             "> Ads Yeti is a founder-led paid ads agency (Meta ads and Google ads) that judges campaigns on what happens after the click: "
             "leads, follow-up, sales and revenue. The Knowledge Centre answers the questions founders ask before hiring anyone.", "",
             f"- [Knowledge Centre]({abs_url(SITE['hub_path'])}): hub, browse by topic or question type",
             f"- [Blog]({abs_url(SITE['blog_path'])}): every article", ""]
    for k, t in TOPICS.items():
        mine = [a for a in by_date if a["topic"] == k and a.get("body")]
        if not mine:
            continue
        lines += [f"## {t['name']}", ""] + [f"- [{a['title']}]({abs_url(article_url(a))}): {a['summary']}" for a in mine] + [""]
    (OUT / "llms.txt").write_text("\n".join(lines))


def write(path, content):
    target = OUT / path.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    print("wrote", target.relative_to(ROOT))


def main():
    arts = json.loads((SRC / "articles.json").read_text())["articles"]
    build_hub(arts)
    build_blog(arts)
    for k in TOPICS:
        build_topic(k, arts)
    for a in arts:
        if a.get("body"):
            build_article(a, arts)
    build_feeds(arts)
    # Standalone header snippet for pasting into the main site template
    (OUT / "partials").mkdir(exist_ok=True)
    (OUT / "partials" / "header-with-resources-menu.html").write_text(header_html(active=None) + "\n")


if __name__ == "__main__":
    main()
