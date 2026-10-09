// Knowledge Centre content. Add an article here and it appears on the hub,
// in search, in its topic and question-type counts, and in the page's JSON-LD.
//
// NOTE: apart from the first article, these are EXAMPLE titles that show the
// They Ask, You Answer "Big 5" structure. Swap them for real articles.

export type TopicKey = 'meta' | 'creative' | 'tracking' | 'crm' | 'landing' | 'strategy';
export type QuestionType = 'cost' | 'problems' | 'comparisons' | 'reviews' | 'howto';

export interface Topic {
  key: TopicKey;
  name: string;
  icon: string;
  /** gradient recipe, matches the homepage service cards (.sg1–.sg5) */
  gradient: 'g1' | 'g2' | 'g3' | 'g4' | 'g5' | 'g6';
  blurb: string;
}

export interface QuestionTypeInfo {
  key: QuestionType;
  name: string;
  icon: string;
  blurb: string;
}

export interface Article {
  slug: string;
  title: string;
  summary: string;
  topic: TopicKey;
  type: QuestionType;
  date: string; // YYYY-MM-DD
  updated?: string;
  minutes: number;
  popularity: number;
  featured?: boolean;
  startHere?: number;
  keywords: string[];
  image?: string;
}

export const KC_PATH = '/resources/';
export const BLOG_PATH = '/resources/blog/';

export const topics: Topic[] = [
  { key: 'meta', name: 'Meta ads', icon: '📣', gradient: 'g1', blurb: 'Facebook and Instagram ads that turn into enquiries and bookings, not just clicks.' },
  { key: 'creative', name: 'Ad creative', icon: '🎬', gradient: 'g4', blurb: "Hooks, formats and testing. The creative is usually the biggest lever you've got." },
  { key: 'tracking', name: 'Tracking & attribution', icon: '📊', gradient: 'g3', blurb: 'Working out what actually drove the sale when every platform claims the trophy.' },
  { key: 'crm', name: 'Leads, follow-up & bookings', icon: '🤝', gradient: 'g2', blurb: 'What happens after the click: speed to lead, nurture, CRM and GoHighLevel.' },
  { key: 'landing', name: 'Landing pages & funnels', icon: '🧭', gradient: 'g5', blurb: 'Pages and forms that turn paid traffic into qualified enquiries.' },
  { key: 'strategy', name: 'Strategy for founders', icon: '🧠', gradient: 'g6', blurb: 'Budgets, channels, hiring and the commercial decisions behind the ads.' },
];

// They Ask, You Answer: the "Big 5" questions buyers ask before they buy.
export const questionTypes: QuestionTypeInfo[] = [
  { key: 'cost', name: 'Pricing & cost', icon: '💷', blurb: 'What things really cost, and why.' },
  { key: 'problems', name: 'Problems & fixes', icon: '🛠️', blurb: 'What goes wrong, and how to sort it.' },
  { key: 'comparisons', name: 'Comparisons', icon: '⚖️', blurb: 'This vs that, honestly compared.' },
  { key: 'reviews', name: 'Reviews & best-of', icon: '⭐', blurb: "Tools and tactics we'd actually use." },
  { key: 'howto', name: 'How-to & explainers', icon: '📘', blurb: 'Plain English, step by step.' },
];

export const articles: Article[] = [
  { slug: 'why-facebook-ads-get-leads-but-no-sales', title: 'Why are my Facebook ads getting leads but no sales?', summary: "Cheap leads that never book usually aren't an ads problem. Here's where the journey actually breaks, and what to check first.", topic: 'crm', type: 'problems', date: '2026-09-22', updated: '2026-09-28', minutes: 9, popularity: 98, featured: true, startHere: 2, keywords: ['meta', 'facebook', 'lead quality', 'follow up', 'speed to lead', 'nurture', 'bookings'] },
  { slug: 'how-much-does-a-meta-ads-agency-cost-uk', title: 'How much does a Meta ads agency cost in the UK?', summary: "Retainers, percentage of spend and performance fees explained, with what's actually included in each.", topic: 'meta', type: 'cost', date: '2026-09-15', minutes: 11, popularity: 95, startHere: 1, keywords: ['pricing', 'facebook ads agency', 'retainer', 'management fee'] },
  { slug: 'meta-ads-vs-google-ads-travel-brands', title: 'Meta ads vs Google ads for travel brands: where should you start?', summary: 'Creating demand versus catching it. How to choose based on whether people are already searching for your trips.', topic: 'strategy', type: 'comparisons', date: '2026-09-08', minutes: 10, popularity: 90, startHere: 3, keywords: ['facebook vs google', 'ppc', 'paid social', 'travel marketing'] },
  { slug: 'meta-roas-doesnt-match-bookings', title: "Why doesn't Meta's reported ROAS match your actual bookings?", summary: 'Attribution windows, modelled conversions and double counting. How to find the number you can actually trust.', topic: 'tracking', type: 'problems', date: '2026-09-01', minutes: 8, popularity: 88, keywords: ['attribution', 'roas', 'ga4', 'reporting', 'revenue'] },
  { slug: 'how-much-should-travel-company-spend-meta-ads', title: 'How much should a travel company spend on Meta ads?', summary: 'Working backwards from what a booking is worth to a budget that gives Meta enough to learn from.', topic: 'strategy', type: 'cost', date: '2026-08-25', minutes: 7, popularity: 84, keywords: ['budget', 'ad spend', 'tour operator', 'cost per booking'] },
  { slug: 'agency-vs-freelancer-vs-in-house-ads', title: 'Agency vs freelancer vs in-house: who should run your ads?', summary: 'An honest comparison, including when hiring an agency like us is the wrong call.', topic: 'strategy', type: 'comparisons', date: '2026-08-18', minutes: 9, popularity: 80, keywords: ['hire', 'marketing team', 'outsourcing'] },
  { slug: 'track-lead-from-meta-ad-to-booked-trip-gohighlevel', title: 'How to track a lead from Meta ad to booked trip in GoHighLevel', summary: 'Step by step: UTMs, hidden fields, pipeline stages and sending the booking back to Meta.', topic: 'crm', type: 'howto', date: '2026-08-11', minutes: 14, popularity: 77, keywords: ['ghl', 'utm', 'offline conversions', 'pipeline', 'crm'] },
  { slug: 'meta-conversions-api-do-you-need-it', title: 'What is the Meta Conversions API, and do you actually need it?', summary: 'A plain-English explanation of CAPI, what it fixes, and who can safely skip it for now.', topic: 'tracking', type: 'howto', date: '2026-08-04', minutes: 8, popularity: 74, keywords: ['capi', 'pixel', 'server side tracking', 'ios'] },
  { slug: 'meta-lead-forms-vs-landing-pages', title: 'Meta lead forms vs landing pages: which gets more bookings?', summary: "Instant forms are cheap and fast. Landing pages qualify better. Here's how to test which one works for you.", topic: 'landing', type: 'comparisons', date: '2026-07-28', minutes: 10, popularity: 71, keywords: ['instant forms', 'lead ads', 'conversion rate', 'funnel'] },
  { slug: 'best-meta-ad-creative-travel-brands', title: 'The best Meta ad creative formats for travel brands in 2026', summary: "Founder-to-camera, customer footage, static proof ads and carousels. What's working in the accounts we manage right now.", topic: 'creative', type: 'reviews', date: '2026-07-21', minutes: 8, popularity: 69, keywords: ['creative', 'ugc', 'video ads', 'hooks', 'travel'] },
  { slug: 'is-gohighlevel-worth-it', title: 'Is GoHighLevel worth it for a travel or service business?', summary: 'The good, the bad and the slightly clunky. A review from people who use it every day.', topic: 'crm', type: 'reviews', date: '2026-07-14', minutes: 9, popularity: 66, keywords: ['ghl review', 'crm', 'automation'] },
  { slug: 'why-have-my-meta-ads-stopped-working', title: 'Why have my Meta ads suddenly stopped working?', summary: 'Creative fatigue, audience saturation, tracking breaks or seasonality. How to work out which one it is.', topic: 'creative', type: 'problems', date: '2026-07-07', minutes: 8, popularity: 72, keywords: ['creative fatigue', 'cpm', 'frequency', 'performance drop'] },
  { slug: 'how-long-do-meta-ads-take-to-work', title: 'How long does it take for Meta ads to start working?', summary: 'What the learning phase really means, and realistic milestones for the first 90 days.', topic: 'meta', type: 'howto', date: '2026-06-30', minutes: 6, popularity: 64, keywords: ['learning phase', 'timeline', 'expectations'] },
  { slug: 'good-cost-per-lead-travel-meta-ads', title: "What's a good cost per lead for a travel brand on Meta?", summary: 'Why benchmarks mislead, and the numbers worth comparing yourself against instead.', topic: 'meta', type: 'cost', date: '2026-06-23', minutes: 7, popularity: 62, keywords: ['cpl', 'benchmark', 'cost per lead', 'travel'] },
];

// ---------- helpers ----------
export const topicByKey = (k: TopicKey) => topics.find((t) => t.key === k)!;
export const typeByKey = (k: QuestionType) => questionTypes.find((t) => t.key === k)!;
export const articleUrl = (a: Article) => `${BLOG_PATH}${a.slug}/`;
export const topicUrl = (k: TopicKey) => `${KC_PATH}topics/${k}/`;
export const typeUrl = (k: QuestionType) => `${BLOG_PATH}?type=${k}`;

export const byNewest = [...articles].sort((a, b) => b.date.localeCompare(a.date));
export const byPopular = [...articles].sort((a, b) => b.popularity - a.popularity);

export function formatDate(iso: string) {
  return new Date(iso + 'T12:00:00').toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
}

/** Every search word must appear somewhere; title matches rank higher. */
export function searchArticles(query: string, limit = 6): Article[] {
  const terms = query.toLowerCase().split(/\s+/).filter((t) => t.length > 1);
  if (!terms.length) return [];
  return articles
    .map((a) => {
      const title = a.title.toLowerCase();
      const hay = [a.title, a.summary, topicByKey(a.topic).name, typeByKey(a.type).name, ...a.keywords].join(' ').toLowerCase();
      let score = 0;
      for (const t of terms) {
        if (!hay.includes(t)) return { a, score: 0 };
        score += title.includes(t) ? 3 : 1;
      }
      return { a, score };
    })
    .filter((r) => r.score > 0)
    .sort((x, y) => y.score - x.score)
    .slice(0, limit)
    .map((r) => r.a);
}
