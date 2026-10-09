import { useRef } from 'react';
import { useSeo, SITE_URL } from '../hooks/useSeo';
import { useReveal } from '../hooks/useReveal';
import { byNewest, articleUrl, KC_PATH, BLOG_PATH } from '../data/knowledgeCentre';
import KcHero from '../components/knowledge-centre/KcHero';
import StartHere from '../components/knowledge-centre/StartHere';
import QuestionTypes from '../components/knowledge-centre/QuestionTypes';
import TopicGrid from '../components/knowledge-centre/TopicGrid';
import LatestAnswers from '../components/knowledge-centre/LatestAnswers';
import NewsletterStrip from '../components/knowledge-centre/NewsletterStrip';
import AskTheYeti from '../components/knowledge-centre/AskTheYeti';
import '../styles/knowledge-centre.css';

const jsonLd = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'Organization', '@id': `${SITE_URL}/#organization`, name: 'Ads Yeti', url: `${SITE_URL}/`,
      email: 'andy@adsyeti.com', sameAs: ['https://www.linkedin.com/in/andymooreevertrek/'],
    },
    {
      '@type': 'WebSite', '@id': `${SITE_URL}/#website`, url: `${SITE_URL}/`, name: 'Ads Yeti', publisher: { '@id': `${SITE_URL}/#organization` },
      potentialAction: { '@type': 'SearchAction', target: { '@type': 'EntryPoint', urlTemplate: `${SITE_URL}${BLOG_PATH}?q={search_term_string}` }, 'query-input': 'required name=search_term_string' },
    },
    {
      '@type': 'CollectionPage', '@id': `${SITE_URL}${KC_PATH}`, url: `${SITE_URL}${KC_PATH}`, name: 'Ads Yeti Knowledge Centre', inLanguage: 'en-GB',
      description: 'Honest answers to the questions founders ask about Meta ads, tracking, pricing and turning leads into bookings.',
      isPartOf: { '@id': `${SITE_URL}/#website` },
      mainEntity: {
        '@type': 'ItemList', name: 'Latest articles',
        itemListElement: byNewest.map((a, i) => ({ '@type': 'ListItem', position: i + 1, url: SITE_URL + articleUrl(a), name: a.title })),
      },
    },
    {
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: `${SITE_URL}/` },
        { '@type': 'ListItem', position: 2, name: 'Resources', item: `${SITE_URL}${KC_PATH}` },
      ],
    },
  ],
};

export default function KnowledgeCentre() {
  const root = useRef<HTMLDivElement>(null);
  useReveal(root);
  useSeo({
    title: 'Resources: The Ads Yeti Knowledge Centre | Meta Ads Questions Answered',
    description: 'Honest answers to the questions founders ask about Meta ads, tracking, pricing and turning leads into bookings. From Andy Moore and the Ads Yeti team.',
    path: KC_PATH,
    ogImage: '/kc/yeti-wave.webp',
    jsonLd,
  });

  return (
    <div className="kc" ref={root}>
      <KcHero />
      <StartHere />
      <QuestionTypes />
      <TopicGrid />
      <LatestAnswers />
      <NewsletterStrip />
      <AskTheYeti />
    </div>
  );
}
