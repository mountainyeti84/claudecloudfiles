import KcSearch from './KcSearch';
import { articles, topics, byPopular, articleUrl } from '../../data/knowledgeCentre';

export default function KcHero() {
  const popular = byPopular.slice(0, 3);
  return (
    <header className="kc-hero">
      <div className="kc-hero__card">
        {/* same drifting gradient blobs + grain as the homepage hero */}
        <div className="g-wrap" aria-hidden="true">
          <div className="g-blob b1" /><div className="g-blob b2" /><div className="g-blob b3" /><div className="g-blob b4" />
          <div className="grain" />
        </div>

        <div className="kc-hero__inner">
          <nav className="kc-crumbs" aria-label="Breadcrumb">
            <ol>
              <li><a href="/">Home</a></li>
              <li><span aria-current="page">Resources</span></li>
            </ol>
          </nav>
          <p className="eyebrow kc-hero__eyebrow">// THE ADS YETI KNOWLEDGE CENTRE</p>
          <h1>Ask us anything about Meta ads. We&rsquo;ll answer it honestly.</h1>
          <p className="kc-hero__lede">
            Straight answers to the questions founders ask us about ads, tracking and turning leads into bookings, including the ones most agencies would rather you didn&rsquo;t ask.
          </p>

          <KcSearch />

          <div className="kc-popular">
            <span>Popular:</span>
            {popular.map((a) => (
              <a key={a.slug} href={articleUrl(a)}>{a.title}</a>
            ))}
          </div>

          <dl className="kc-hero__stats">
            <div><dt>answers</dt><dd>{articles.length}</dd></div>
            <div><dt>topics</dt><dd>{topics.length}</dd></div>
            <div><dt>sales pitches in disguise</dt><dd>0</dd></div>
          </dl>
        </div>

        <div className="kc-hero__yeti" aria-hidden="true">
          <img src="/kc/yeti-wave.webp" alt="" width={640} height={570} />
        </div>
      </div>
    </header>
  );
}
