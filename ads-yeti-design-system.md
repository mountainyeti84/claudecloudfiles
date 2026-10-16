# Ads Yeti Design System

The Ads Yeti brand: colours, type, components, imagery and voice. Built from adsyeti.com, the *Connected Demand* report and Andy Voice v1.1. Live version: https://claude.ai/artifact/Qc2uo8tp14QQnmsG2t5NKB

## Contents

1. Brand book
2. Voice
3. Colour tokens
4. Typography
5. Spacing, radius and shadow
6. Components
7. Assets

## 1. Brand book

Ads Yeti is a paid-social agency run by Andy. It does Meta ads for high-growth brands, especially travel. The brand is a dark, warm, confident page lit by soft orange glows. Bold Satoshi headlines and JetBrains Mono labels sit on top, with a friendly yeti in a black hoodie as the mascot. It should feel like a specialist who's done the work and doesn't take themselves too seriously.

### Content fundamentals

**Voice:** all copy is written in Andy Voice. The **Voice** section is the full guide, with the instruction block to hand to any writer or AI. In short: founder-to-founder, plain British English, commercially curious, warm, lightly irreverent. Andy follows the journey from ad to revenue rather than platform metrics. Every joke has a business point under it. Never agency jargon ("unlock", "leverage", "game-changing").

- **Write as people, to one person.** Use "I" for Andy's own story ("I know because… I was the business owner on the other side"). Use "we" for the agency's work ("We do the staring for you"). Always speak to "you".
- **British spelling and pounds.** optimisation, travellers, £15m, £2 per lead. Use `en-GB` number formatting.
- **Lead with the outcome, then the proof.** "More Leads. More Sales. Less staring at Ads Manager wondering what went wrong*". Back claims with real numbers: £8.50 → £2 CPL, 500 → 4,500 leads a month, 68% average CPL cut in 90 days. Never invent a stat. Put an asterisk on any average and footnote it.
- **Yeti wordplay, sparingly.** "monster load of leads", "Roarsome. We've got it.", "climb higher", "performance holds at altitude", "EST. IN THE MOUNTAINS". One per section at most.
- **Be brutally honest.** "A free, brutally honest account teardown". "If we can't help, we'll tell you that too." "No vanity dashboards." "No spam. No 47-email nurture sequence."
- **Casing:** sentence case for headlines and buttons ("Get your free audit →"). Eyebrows are uppercase mono with a `// ` prefix ("// CLIENT WORK", "// DO THE MATHS", "// LET'S GOOO").
- **CTAs end in an arrow:** "Get Andy's take →", "Start the conversation →", "Read the full story →", "See client work ↓".
- **Emoji:** only as tiny icons inside notification chips and multi-choice options (🔔 3 new enquiries, 📉 Lower cost per lead). Never in headlines or body copy.

### Visual foundations

**Colour.** The page is `ink` (#0B0B0D) with `txt` text. Warm off-white, not pure white, is used for body copy. Colour arrives as light, not as flat fills:

- `orange` → `amber` → `peach` is the brand gradient. It's on every primary button (`linear-gradient(100deg, orange, amber 55%, peach)`) and on stat numbers (clipped to the text).
- Glow blobs are blurred radial gradients of `orange`, `peach`, `coral` and one cool `ice`. They sit inside hero, contact and result panels, with a 9–10% fractal-noise grain over the top. Use `GlowPanel` for this rather than flat orange backgrounds.
- `pink`, `lilac` and `mint` are supporting glow tints only (service cards, client cards). Never use them as text or as a button colour.
- Light sections are `paper` cards (#F6F2EA) set *inside* the dark page with `radius-card`. They are not full-bleed white. Set the **Paper** theme on them (`data-theme="paper"`).
- Put text on the button gradient in `on-orange`, never white (white on orange is 2.9:1).
- On paper, brand orange is decorative only: slider fill, underline scribble. For orange words in a paper headline use `accent-text`.

**Type.** Satoshi (Fontshare) for everything you read. JetBrains Mono for everything that acts as a label: eyebrows, buttons, metric captions, footnotes, tags.

- Headlines: weight 900, tight tracking (-0.025em), leading 1.02–1.06. Styles `display-hero`, `heading-section`, `display-contact`.
- Big statements and leads: weight 700, -0.015em (`statement`, `lead`).
- Body: `body` 17/1.6. Long story copy uses `body-lg`, max 62ch, with **bold** for the key commercial phrases.
- Mono labels are small (10.5–13px) and uppercase with +0.07–0.1em tracking (`eyebrow`, `label`, `micro`). Button labels are mono 700 in sentence case.
- Underline one key phrase per section with the hand-drawn orange scribble (`profitable growth`, 5px round stroke).

**Shape and layout.**
- Every control is a pill (`radius-pill`): buttons, nav, nav links, tags.
- Every section is a big rounded card (`radius-card`, 28px). Max content width is 1240px. The gutter is fluid, clamp(10px, 1.6vw, 22px) (`space-22` at desktop). Sections breathe with `space-110` vertical padding.
- The nav is a floating glass pill: ink at 82% opacity, 14px blur, `line` border, fixed 12px from the top.
- Borders are hairlines (`line`). Shadows are reserved for floating things (`shadow-float`). The primary button's hover is an orange glow (`shadow-glow`).

**Motion.** Bouncy and playful. Use cubic-bezier(.34, 1.56, .64, 1) for buttons and chips: hover lifts 2px and scales 1.02, and the arrow nudges 4px right. Cards ease out on cubic-bezier(.22, 1, .36, 1). Blobs drift slowly (23–31s). The yeti bobs and wiggles on click. Respect `prefers-reduced-motion`.

**Focus.** 2px solid `focus-ring` with a 4px offset: orange on ink, ink on paper.

### Reports and decks

Long-form thought leadership (e.g. *Connected Demand: The Hidden Link Between Paid Social and PPC*) uses a calmer, cooler register than the website. Set slides in the **Report** theme (`data-theme="report"`), or `ReportSlide`'s `light` variant for frost slides.

- 1920×1080 slides with 128px side margins. Use `navy` grounds with `navy-2` panels and `navy-line` borders, alternating with `frost` light slides that use white cards. Orange is the single accent. Use `report-blue` for supporting numbers.
- Type: Satoshi 700 headlines (`report-heading`, 56px, -2px) and 800 for cover titles and big numbers (`report-title`, `report-number`). Body is `report-body` in `slate`. Mono eyebrows "// EVIDENCE 02 · ANALYTIC PARTNERS" go in `accent-text`. The mono footer reads "12 / THE EVIDENCE   SOURCE: …" with the wordmark bottom right.
- Each slide makes one argument with a headline that states it. Every external figure gets a source in the footer. Label invented examples "ILLUSTRATIVE FIGURES · NOT ACCOUNT DATA". Say when data is observational, not causal.
- No glow blobs, 900-weight display type or yeti in reports. Photography (mountains, people on phones) sits faded behind a navy gradient.
- Diagrams are flat line drawings: orange 4px strokes with round caps, slate text, and dots or loops rather than icons.

### Imagery

- **The Yeti** (`assets/Mascot/`) is a friendly white-haired yeti in a black hoodie printed "THE ADS YETI". Use one pose per view, peeking from a corner or bottom edge of a card, with a soft drop shadow. Pair it with a white speech bubble (`radius-md`, small 4px tail corner) and a mono orange CTA line ("Get your free Ad Insights here"). Poses: wave = hello/CTA, point = "talk to us", cheer = success/thank-you, toy = playful filler.
- **Client photography** sits under a gradient wash with `mix-blend-mode: luminosity` at 55% opacity. It brightens to 78% on hover, with a dark bottom shade so white text reads. Client logos are knocked out to white.
- **Founder portrait**: Andy appears cut out over a warm glow (orange, ice, pink) in a 28px card, with a slightly rotated white name chip.

### Iconography

- Logos: `assets/Logos/` holds the "THE ADS YETI" wordmark (footprint inside the D) in white, for ink, navy and photos, and in ink, for paper, frost and white. It also holds the footprint mark (white foot on a black rounded square) for favicons and avatars.
- Service icons on the site are 60px solid white inline SVGs. They aren't in this system yet; add them to `assets/Icons/` when exported.
- Glyphs as icons: → for go, ↓ for scroll, ✦ / ★ as separators in orange at 55% opacity.

### Fonts

Both faces ship here as variable woff2 files: `fonts/Satoshi-Variable.woff2` (100–900) and `fonts/JetBrainsMono-latin.woff2` (100–800). On the web you can also load Satoshi from Fontshare (`https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700,900&display=swap`) and JetBrains Mono from Google Fonts. The site uses Satoshi 400/500/700/900; reports add 600 and 800.
## 2. Voice

Every Ads Yeti word is written in **Andy Voice** (Voice & Copy Profile v1.1). The one-line definition:

> Andy doesn't sound like someone creating content. He sounds like Andy has something interesting he wants to tell you.

He's an enthusiastic business owner who happens to know a lot about marketing, not a marketer trying to sound like a business owner. The voice is conversational, commercially curious, practical, warm, lightly irreverent, and grounded in things Andy has actually done, tested, noticed or learned.

### Point of view

Customers don't live inside Ads Manager. Follow the journey: **ad → lead/enquiry → nurture → conversation → customer/booking → revenue.** The platform is rarely the hero; the outcome is. Andy pulls complicated ideas back to the useful question:

- Will it actually help? Can we test it?
- What happened after the lead came in? Did it turn into a sale or booking?
- Where are we losing people? What would we change first?
- Right — let's try it and see.

His reasoning rhythm is **NOTICE → CHECK → EXPLAIN → CONNECT → ACT**: spot the oddity, compare it with the data, explain why in plain words, connect it to the customer journey, then decide what to test, fix or replicate. Use it for LinkedIn posts, client recommendations, case studies and scripts.

### Sounds like Andy

> "Meta says it did it. Google says it did it. GA4 has another idea entirely. Meanwhile I'm sat there as the business owner thinking… I don't really care who gets the trophy. I just want to know what actually helped us sell the trip."

> "I've spent a slightly ridiculous amount of time looking at Meta and Google data recently…"

### Doesn't sound like Andy

> "We leverage cutting-edge full-funnel acquisition frameworks to unlock scalable omnichannel growth for ambitious seven-figure brands."

> "Here are 5 game-changing lessons every founder needs to know about omnichannel attribution."

### Rhythm and words

- Mix conversational sentences with an occasional very short line for emphasis. Use contractions (we're, don't, I've). Allow an aside, then come back to the point.
- Use examples early. Plain English beats marketing terms. Leave a little texture; don't polish every sentence symmetrical.
- **Spoken → written:** remove ums, repeats and false starts. Keep the thought pattern, warmth and examples. *Polish Andy; do not sterilise him.*
- Keep honest qualifiers ("I think", "potentially", "this is only one example") when the evidence is genuinely uncertain. Don't swap them for fake confidence.
- Natural vocabulary includes look, basically, interesting, useful, awesome, great stuff, exactly, let's, right, anyway. Warm micro-language: "happy days", "mad, isn't it?", "Screw it, let's do it", "Cheers, guys". Never force these in. A piece with none of them can still sound exactly like Andy.
- Humour is observational, self-deprecating or an aside. Light swearing is fine when natural ("Where are the bloody bookings?"). Yeti/mountain language is seasoning, not the meal.
- British English. Concrete numbers where known. Exclamation marks only when genuinely excited. Emoji as emotional punctuation in social/EverTrek content, never as decoration.

### The dial by context

| Context | Energy | Commercial | Flavour |
| --- | --- | --- | --- |
| LinkedIn founder | 7/10 | 6/10 | Story/observation first; useful thought second; light CTA only occasionally |
| Ads Yeti website | 6/10 | 9/10 | Clear commercial outcome, founder credibility, plain English, dry humour |
| Ads Yeti ads | 7/10 | 9/10 | Fast problem recognition; concrete outcome; no agency waffle |
| EverTrek email | 9/10 | 6/10 | Adventure, emotion, story, humour, community, excitement |
| Client email | 6/10 | 8/10 | Friendly, practical, clear actions; "here's what I think we should do" |
| Video/script | 8/10 | 7/10 | Closest to natural speech; explain with examples; allow more asides |
| Reports & decks | — | — | The calm end of the dial: evidence first, sources on every number, observational data labelled as such ("None of it proves causation. All of it points the same way.") |

### Never

- Generic LinkedIn hooks ("I made £3m. Here's what nobody tells you."), manufactured controversy, fake vulnerability.
- "Agree?", "Thoughts?" or "What do you think?" at the end.
- Corporate filler: leverage, unlock, synergise, cutting-edge, holistic, ecosystem, game-changing, best-in-class, revolutionary.
- Turning every idea into "3 lessons" or a framework. Overusing em dashes, bold one-liners, rhetorical questions or choppy line breaks.
- Claiming certainty the evidence doesn't support. Letting the Yeti metaphor do all the work.

### The Andy test

Before publishing, ask these questions. Could Andy say it out loud without feeling he's reading someone else's copy? Is there a real thought, story or useful point here? Did we make something complicated easier? Does the commercial point connect to the real business? Is the evidence used honestly? Is the humour natural? Is there enough texture to sound human? Could we cut 10–20% of the marketing language and make it better?

### Instruction block for AI or copywriters

> Write in ANDY VOICE. Andy Moore is an enthusiastic, commercially minded founder who communicates like a real business owner, not a marketing influencer. He is conversational, practical, curious, warm, collaborative and lightly irreverent. His authority comes from doing the work: spending his own company's money, building systems, testing campaigns, talking to customers, watching leads and bookings, and following what happens all the way through to revenue.
>
> The copy should feel as though Andy noticed something interesting or useful and wants to tell you about it. It must never feel as though he sat down because he needed to "create content".
>
> Use plain British English. Explain complicated ideas simply and use a real or concrete example where possible. Andy naturally thinks in journeys and cause-and-effect: what happened first, what happened next, where the customer came from, what changed, what the data says and what to do next. A useful Andy reasoning structure is: NOTICE → CHECK → EXPLAIN → CONNECT → ACT.
>
> Andy prefers testing to theorising and often builds from something already proven: mirror what works, change as little as necessary, test it, then improve it. He is comfortable with honest qualifiers such as "I think", "potentially" or "this is only one example" when the evidence genuinely calls for them. Do not replace honest uncertainty with fake confidence.
>
> Keep some conversational texture: contractions, an occasional aside, natural enthusiasm and observational/self-deprecating humour. Spoken filler and repetition should be cleaned up. Preserve the person, not the transcript.
>
> For Ads Yeti, write founder-to-founder. Follow the commercial journey from ad → lead/enquiry → nurture → conversation → customer/booking → revenue. Focus on what actually helped the business grow rather than letting individual platforms claim the trophy.
>
> For EverTrek, turn up emotion, adventure, people, community and enthusiasm while keeping the customer as the hero and EverTrek as the experienced guide.
>
> Do NOT use generic LinkedIn-guru hooks, fake controversy, manufactured vulnerability, forced engagement questions, excessive one-line paragraphs, agency jargon, over-polished corporate language or relentless Yeti/mountain metaphors. Do not turn every idea into a framework or listicle. Do not force Andyisms such as "awesome", "mate" or "great stuff" into copy to make it sound like Andy.
>
> Most important rule: Andy doesn't sound like someone creating content. He sounds like Andy has something interesting he wants to tell you.
## 3. Colour tokens

Themes: **Ink (dark)** (`ink`), **Paper (light)** (`paper`), **Report (navy)** (`report`). Values in `{braces}` point to another token. A blank theme value inherits the Ink value.

### Semantic (switch with the theme)

| Token | ink | paper | report | Usage |
|---|---|---|---|---|
| `surface` | `{ink}` | `{paper}` | `{navy}` | Page or section background. Ink is the default page; Paper is the cream content card (services, calculator). Report: deep navy slide ground. |
| `surface-raised` | `{ink-2}` | `#ffffff` | `{navy-2}` | Stat cards, modals and panels sitting on `surface`. |
| `text` | `{txt}` | `{paper-txt}` | `{frost}` | Headlines and body copy on `surface` and `surface-raised` (17.7:1 on ink, 16.6:1 on paper). |
| `text-muted` | `{dim}` | `{paper-dim}` | `{slate}` | Ledes, labels, metric captions and footer links on `surface` and `surface-raised` (7.0:1 on ink, 6.4:1 on paper). Report: `slate` (8.0:1 on navy-2). |
| `line` | `#ffffff12` | `#14131133` | `{navy-line}` | Hairline borders on cards, nav and stat tiles (rgba white .07 on ink; rgba ink .2 on paper). |
| `accent` | `{orange}` | `{orange}` | `{orange}` | The brand orange: scribble underlines, slider fill, separators, selection. On paper it is decorative only — 2.6:1, too low for text. |
| `accent-text` | `{orange}` | `#c2410c` | `{amber}` | Orange words inside headlines (e.g. “mean for you?”). Ink: brand orange (6.9:1). Paper: an added darker orange (4.6:1) because brand orange fails on cream. Intentional addition. Report: `amber` for eyebrows and orange headline lines (8.6:1 on navy). |
| `focus-ring` | `{orange}` | `{paper-txt}` | `{orange}` | 2px focus outline, 4px offset. Orange on ink as on the site (6.9:1); ink on paper because orange misses 3:1 there. Intentional addition. |

### Palette (fixed values)

| Token | Value | Usage |
|---|---|---|
| `ink` | `#0b0b0d` | Page background, nav glass, dark buttons. The brand's base. |
| `ink-2` | `#121214` | Raised dark surfaces: stat cards, modal card. |
| `ink-3` | `#0c0c0e` | Service cards and the calculator result panel, under their gradient glow. |
| `ink-4` | `#1c1c1f` | Dark notification chips. |
| `ink-deep` | `#080809` | Contact card background — the darkest step. |
| `txt` | `#f5f3ee` | Warm off-white text on ink. Never pure white for body copy. |
| `dim` | `#9c9a94` | Muted text on ink: ledes, eyebrows, metric captions (7.0:1 on ink). |
| `paper` | `#f6f2ea` | Cream content cards (services, calculator) set inside the dark page. |
| `paper-txt` | `#141311` | Text on paper and on white chips (16.6:1 on paper). |
| `paper-dim` | `#5c574e` | Supporting copy on paper (6.4:1). |
| `paper-label` | `#8a857b` | Mono field labels and chip sub-labels on paper/white, as on the site. 3.3:1 on paper — below 4.5:1 for its 10–12px size; prefer `paper-dim` for new small text. |
| `paper-rule` | `#e9e4da` | Unfilled track of the range slider on paper. |
| `on-orange` | `#1a0d00` | Text on the orange→peach button gradient (6.7:1 on orange, 10.7:1 on peach). Never white on orange (2.9:1). |
| `white` | `#ffffff` | Hero headline over the gradient blobs; light chips and tooltips. |
| `orange` | `#ff6b00` | Primary brand colour. Button gradient start, scribble underline, focus ring, accents on ink. |
| `amber` | `#ff8f40` | Button gradient midpoint (55%); outline chip border tint. |
| `peach` | `#ffb25e` | Button gradient end; stat-number gradient end; “Read the full story →” links on ink (11:1). |
| `coral` | `#ff7a6b` | Hero glow blob; secondary accent bar on client cards. |
| `pink` | `#ff9ec2` | Glow tint in portrait and service cards; charity (Tŷ Hafan) card accent. |
| `lilac` | `#c9a6ff` | Glow tint in service cards and client-card gradients. Supporting only — never a lead colour. |
| `mint` | `#7fe7c4` | Glow tint; walking-holidays (Absolute Escapes) card accent. |
| `ice` | `#8ed8ff` | The one cool glow — balances the warm blobs in hero, contact and calculator panels. |
| `navy` | `#070c17` | Report and deck slide ground (the Connected Demand report). Also text on orange cards (6.9:1). |
| `navy-2` | `#131d33` | Raised panels and stat cards on report slides. |
| `navy-line` | `#2a3a5c` | Panel borders on navy. Decorative divider only (1.7:1) — never the sole cue. |
| `frost` | `#f4f6fa` | Headline and body text on navy (18:1); ground of light report slides. |
| `frost-2` | `#edf1f7` | Alternate light-slide ground and light panel fill. |
| `frost-rule` | `#d9dfea` | Borders on light report slides. |
| `slate` | `#a8b4ca` | Body copy on navy and navy-2 (8.0:1 on navy-2). |
| `slate-2` | `#7c8aa4` | Slide footer meta (page / section / source) on navy (5.6:1). |
| `slate-3` | `#6b7689` | Mono labels on white/frost report cards at 24px slide size (4.2:1 on frost — large text only). |
| `slate-ink` | `#4a5568` | Supporting copy on white/frost report cards (7.0:1). |
| `report-blue` | `#9db4de` | Secondary big-number colour on navy panels, beside an orange lead number (8.0:1 on navy-2). |
| `orange-deep` | `#5c2800` | Mono label on a solid orange card (4.2:1 — 24px slide size only). |

### Gradients (in components, not tokens)

- **Button / brand gradient:** `linear-gradient(100deg, #FF6B00, #FF8F40 55%, #FFB25E)`
- **Stat number:** `linear-gradient(100deg, #FF6B00, #FFB25E)`, clipped to the text
- **Glow blobs:** blurred radial gradients of orange, peach, coral and ice, plus a 9–10% fractal-noise grain
- **Client card gradients:** orange `135deg, #ff6b00, #ffb25e 55%, #ffd9a8` · coral `#b0413e, #ff7a6b 50%, #c9a6ff` · pink `#d6336c, #ff9ec2 55%, #c9a6ff` · mint `#1e6e5c, #7fe7c4 55%, #8ed8ff`

## 4. Typography

**Families**

- `sans`: "Satoshi", system-ui, -apple-system, sans-serif
- `mono`: "JetBrains Mono", ui-monospace, SFMono-Regular, monospace

**Font files:** Satoshi `fonts/Satoshi-Variable.woff2` (100 900), JetBrains Mono `fonts/JetBrainsMono-latin.woff2` (100 800). Web: Satoshi from Fontshare, JetBrains Mono from Google Fonts.

### Display (sans)

| Style | Size / line height | Weight | Tracking | Sample | Usage |
|---|---|---|---|---|---|
| `display-hero` | 104px / 1.02 | 900 | -0.025em | Meta Ads that work. Imagine. | Hero H1 only. Fluid on the site: clamp(42px, 7.4vw, 104px). |
| `display-contact` | 72px / 1.06 | 900 | -0.025em | Need a monster load of leads? Let’s talk. | Closing CTA headline. clamp(38px, 5.6vw, 72px). |
| `heading-section` | 64px / 1.05 | 900 | -0.025em | Brands we’ve helped climb higher. | Section H2. clamp(34px, 5vw, 64px). |
| `stat-number` | 44px / 1.1 | 900 | -0.025em | £15m+ | Big numbers in stat cards, filled with the orange→peach gradient. |
| `heading-modal` | 36px / 1.15 | 900 | -0.02em | EverTrek | Case-study modal title. clamp(26px, 3.4vw, 36px). |
| `heading-card` | 25px / 1.14 | 900 | -0.02em | Creative Strategy & Testing | Service card titles. |

### Text (sans)

| Style | Size / line height | Weight | Tracking | Sample | Usage |
|---|---|---|---|---|---|
| `statement` | 34px / 1.3 | 700 | -0.015em | The most profitable click on this page is sitting right below this sentence. | Standalone one-liners between sections. |
| `lead` | 30px / 1.45 | 700 | -0.015em | You’re running a real business. | Opening paragraph of a long-copy section. |
| `body-lg` | 20.5px / 1.68 | 400 | — | I help businesses track down what’s stopping paid social from performing commercially. | Long-form story copy, max 62ch. |
| `body` | 17px / 1.6 | 400 | — | Every account is different because every business is different. | Default body copy and ledes. |
| `body-strong` | 21px / 1.3 | 700 | — | EverTrek | Client-card titles and chip labels. |
| `body-sm` | 14.5px / 1.6 | 400 | — | Hooks, angles and UGC briefs tested on a schedule. | Card descriptions, nav links (15px, 500). |

### Mono (mono)

| Style | Size / line height | Weight | Tracking | Sample | Usage |
|---|---|---|---|---|---|
| `eyebrow` | 13px / 1.4 | 400 | 0.08em | // CLIENT WORK | Section kicker above every H2. Uppercase, prefixed with “// ”. |
| `button` | 15px / 1.2 | 700 | 0.01em | Get your free audit → | All button labels. Hero buttons 16px. |
| `label` | 12px / 1.4 | 600 | 0.07em | MONTHLY AD SPEND | Form and slider labels, uppercase. |
| `fine` | 12.5px / 1.5 | 400 | 0.03em | *We do the staring for you | Footnotes, footer links, “Read the full story →”. |
| `micro` | 10.5px / 1.4 | 400 | 0.08em | COST PER LEAD | Metric captions under numbers, uppercase. |

### Report (sans)

| Style | Size / line height | Weight | Tracking | Sample | Usage |
|---|---|---|---|---|---|
| `report-title` | 100px / 1.06 | 800 | -4px | Meta creates the demand. | Report cover title, on a 1920×1080 slide. |
| `report-number` | 110px / 1 | 800 | -4px | 30% | Hero evidence number in a stat panel; orange first, report-blue after. |
| `report-figure` | 68px / 1 | 800 | -2px | £200 | Worked-example figures in comparison cards. |
| `report-heading` | 56px / 1.14 | 700 | -2px | Fourteen days. Five touchpoints. One line of credit. | Slide headline. Weight 700 — reports are calmer than the site's 900. |
| `report-subhead` | 34px / 1.4 | 600 | — | Blended CAC tells you what it cost to create the customer. | The line under a slide headline, often in accent-text. |
| `report-body` | 24px / 1.4 | 400 | — | Everything before day fourteen is invisible to last-click reporting. | Slide body copy and card text. |
| `report-meta` | 24px / 1.4 | 400 | 2px | 02 / THE PROBLEM | Slide footer (page / section · source) and card labels. Eyebrows use 3px tracking, uppercase, in accent-text. |

## 5. Spacing, radius and shadow

### Spacing

| Token | Value | Usage |
|---|---|---|
| `space-4` | `4px` | Nav link gap. |
| `space-10` | `10px` | Icon-to-label gap in buttons and chips; minimum gutter on mobile. |
| `space-14` | `14px` | Gap between paired CTAs; calculator tile gap. |
| `space-18` | `18px` | Gap between H2 and lede; chip padding. |
| `space-22` | `22px` | The gutter at desktop: grid gaps and page edge (fluid clamp(10px, 1.6vw, 22px)). |
| `space-26` | `26px` | Stat card padding. |
| `space-30` | `30px` | Client and service card padding. |
| `space-46` | `46px` | Section head to content. |
| `space-66` | `66px` | Copy block to stats row. |
| `space-110` | `110px` | Vertical section padding. |

### Radius

| Token | Value | Usage |
|---|---|---|
| `radius-pill` | `999px` | Buttons, nav bar, nav links, tags — every interactive control is a pill. |
| `radius-card` | `28px` | Section cards: hero, paper cards, client cards, contact, modal (the site's --radius). |
| `radius-lg` | `24px` | Service cards. |
| `radius-md` | `20px` | Stat cards, case-study pop-ups, speech bubble. |
| `radius-sm` | `16px` | Notification chips and calculator tiles. |
| `radius-xs` | `12px` | Tooltips; chip icon squares (10px). |

### Shadow

| Token | Value | Usage |
|---|---|---|
| `shadow-glow` | `0 10px 30px #ff6b0059` | Primary button hover — an orange glow, never grey. |
| `shadow-float` | `0 12px 34px #00000066` | Floating chips and tooltips. |
| `shadow-lift` | `0 24px 60px #14131147` | Service card hover lift on paper. |

## 6. Components

React components in the `AdsYeti` namespace (`components/bundle.js` + `bundle.css`). Class prefix `ay-`.

### Button

The pill-shaped call to action. Primary buttons use the orange→peach gradient with `on-orange` mono labels.

**Variants**
- `primary` (default): the main action in any view. Use one per section, e.g. "Get your free audit →".
- `ghost`: the secondary action next to a primary, on ink or over a glow ("See client work ↓").
- `dark`: an ink pill for actions on a `paper` card ("Let's talk about this").

**Sizes:** `sm` for the nav, `md` by default, `lg` for the hero and the statement CTA.

**Consumer provides:** the label in sentence case, `arrow` (true for →, or a glyph like "↓"), and `href` or `onClick`.

**Do:** end the label with an arrow. Keep the label to 2–5 words. Name the payoff ("Get Andy's take").
**Don't:** set white text on the gradient. Don't put two primaries side by side. Don't use a ghost button on paper without the paper theme.

### Eyebrow

The mono kicker above every section headline: uppercase JetBrains Mono, +0.08em tracking, `text-muted`, with a `// ` prefix.

**Consumer provides:** the text without the slashes. They're added for you; pass `noSlashes` to skip them.

**Do:** keep it short and slightly playful ("// LET'S GOOO", "// DO THE MATHS").
**Don't:** use it as a headline, or stack two eyebrows.

### NavBar

The floating glass pill nav: ink at 82% opacity, 14px backdrop blur, hairline border, logo left, muted links, small primary CTA right.

**Consumer provides:** `logoSrc` (the white wordmark from `assets/Logos`), `links` (label + href) and an optional `cta`. Fix it to the top yourself (`position: fixed; top: 12px`; width min(1240px, 100% − 2 × gutter)).

**Do:** use it on ink only. Keep it to 5 links or fewer. Links hide below 720px, so add your own burger menu there.
**Don't:** put it on paper or make it full-bleed.

### GlowPanel

The signature Ads Yeti surface: a 28px-radius dark card lit by drifting blurred blobs (orange, peach, coral and one cool ice) under a fine noise grain. Use it for the hero, the contact card and any result panel.

**Consumer provides:** children (headline, copy, CTAs), optional `blobs` to choose which glows appear, and `quiet` to dim them behind dense content.

**Do:** put white display type and a primary button on it. Leave lots of padding.
**Don't:** stack two glow panels back to back. Don't swap the warm blobs for lilac/mint, which are tints, not leads. Don't use it for small UI.

### StatCard

A proof point: a big weight-900 number filled with the orange→peach gradient, over a short muted caption, on `surface-raised` with a hairline border.

**Consumer provides:** `value` (a real, sourced figure) and `label` (one line). Lay them out three across.

**Do:** asterisk averages and footnote the method. Use real client numbers only.
**Don't:** invent or round up stats, or put more than ~12 characters in `value`.

### ClientCard

A case-study tile: a full-bleed gradient (optionally with a luminosity-blended photo), a glass sector tag, and a dark glass panel with an accent bar, title, summary and up to three metrics.

**Consumer provides:** `title` ("How we helped …"), `tag` (sector), `summary`, `metrics` (value + caption), `gradient` (orange / coral / pink / mint; it also sets the accent bar), optional `photo`, and `onClick` to open the full story.

**Do:** show real before→after numbers. Lay them out in a two-column grid with a 28px radius.
**Don't:** write long summaries (keep to 2 lines), or use more than one card per client.

### ServiceCard

A tall dark card glowing up from the bottom edge (five gradient recipes, `glow` 1–5), with a 60px white icon at the top and a two-line weight-900 title and short description at the bottom. Cards scroll horizontally on a `paper` section.

**Consumer provides:** `title` (use `\n` for the line break, e.g. "Landing Pages\n& Funnels"), a `description` of about 25 words, `glow` (a different recipe per card), and an optional `icon`.

**Do:** use a different glow for each card in a row, and lift on hover.
**Don't:** use the same glow twice in view, or write more than 2–3 lines.

### Chip

A floating notification card, white or dark, with a small icon square, a bold line and a mono uppercase sub-label. It's used as playful proof floating around the hero and portrait.

**Consumer provides:** the bold line as children, `sub`, an `icon` (one emoji or a small SVG), optionally `iconBg`, and `dark`.

**Do:** scatter 2–3 chips at slight angles over imagery.
**Don't:** use chips as buttons or form controls.

### Tag

A small uppercase mono pill. `glass` (default) sits over imagery and gradients. `outline` (peach border) lists capabilities in case studies.

**Consumer provides:** a 1–3 word label and a `variant`.

**Do:** use outline tags in rows of 3 for "what we did". **Don't:** make tags clickable.

### Quote

A client testimonial in italics with an orange rule on the left, a faint white wash, and a mono attribution. It's the only place the left-rule treatment appears.

**Consumer provides:** the quote (with curly quotes) as children, and `cite` (name, role, organisation).

**Do:** quote clients verbatim. **Don't:** use it for pull quotes from Ads Yeti itself or for callouts.

### RangeField

The calculator slider: a mono uppercase label, a bold live value, a 6px track filled in orange up to the thumb, and a white thumb ringed in orange. Built for `paper` cards.

**Consumer provides:** `label`, `min`, `max`, `step`, `value`/`defaultValue` and `onChange`, an optional `format` (defaults to £ in en-GB), and `scale` tick labels.

**Do:** use it for "do the maths" calculators. **Don't:** use it for precise data entry.

### YetiBubble

The mascot moment: a yeti pose with a white speech bubble (tail corner bottom right) holding one bold line and a mono CTA.

**Consumer provides:** the line as children, an optional `cta`, and `src`, a pose from `assets/Mascot` (wave = hello, point = talk to us, cheer = success, toy = playful).

**Do:** use it once per page, peeking from a corner or bottom edge, and make it clickable to open the audit.
**Don't:** crop the hoodie text, recolour the yeti, or put a yeti on every section.

### ReportSlide

A 1920×1080 report or deck slide in the Connected Demand style. It has a mono eyebrow in `accent-text`, a Satoshi 700 headline, an optional orange subtitle, free body content, and a footer with page / section · source on the left and the wordmark on the right.

**Consumer provides:** `title`, `eyebrow`, optional `subtitle`, body content as children (usually an `.ay-grid` of `EvidenceStat`s plus one paragraph), `page` + `section` and `source` for the footer, and `logoSrc` (the white wordmark on navy, the ink wordmark on `light` slides). Use `cover` for the title slide and `photo` for a faded photographic background. Scale the fixed 1920×1080 frame to the screen yourself.

**Do:** make every slide one argument, with one headline that states it. Credit every external number in `source`, and label made-up worked examples "Illustrative figures · not account data". Alternate navy and light slides for pace.
**Don't:** use the site's 900-weight display type, glow blobs or yeti here. Reports are the calm, evidence-led voice. Don't overclaim: if the data is observational, say so on the slide.

### EvidenceStat

A report number card: an optional mono label, a big weight-800 number, and one sentence of what it means. On navy it has a 4px orange left edge (blue for supporting numbers). On light slides it's a white card with an orange top edge. `solid` is the orange call-out card for "the obvious call".

**Consumer provides:** `value`, the explanation as children, an optional `label` ("Account A", "Meta · attributed CPA"), and `tone` (`orange` for the lead number, `blue` for the rest, `solid` for a call-out). Lay them out three across in `.ay-grid` (set `--cols` to change).

**Do:** use one orange number per slide and blue for the others. Keep the explanation to about 20 words.
**Don't:** put two solid cards on one slide, or show a number without its source in the slide footer.

## 7. Assets

### Logos

The wordmark is "THE ADS YETI" with a yeti footprint inside the D.

- `ads-yeti-wordmark-white.png`: white, 321×42. Use it on `ink`, `navy` and photography: the nav (26px tall) and report slide footers (42px).
- `ads-yeti-wordmark-ink.png`: navy ink (`navy`), 321×42. Use it on `paper`, `frost` and white.
- `ads-yeti-footprint-mark.png`: a white footprint on a black rounded square, 512×512. Use it for favicons, social avatars and app icons.

Keep clear space of at least the height of the D around the wordmark. Never recolour it orange or set it on the button gradient. Vector (SVG) versions are still needed.

### Mascot

The Ads Yeti: a friendly white-haired yeti in a black "THE ADS YETI" hoodie. The PNGs have transparent backgrounds. Add a drop shadow (0 -14px 44px rgba(0,0,0,.38)) when it peeks from a card edge.

- `yeti-wave.png`: hello / primary CTA (hero, audit prompt).
- `yeti-point.png`: "talk to us" (contact section).
- `yeti-cheer.png`: success / thank-you states.
- `yeti-toy.png`: playful filler (falling-bits playground).

### People

- `andy-founder.png`: Andy Moore, founder, cut out on transparency (693×1000). Set him over a warm glow card (orange, ice and pink radial gradients on `ink`, `radius-card`) with a slightly rotated white name chip, as on the website's intro. Don't recolour, crop his face, or use him as decoration.
