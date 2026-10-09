import { articles, byNewest, BLOG_PATH } from '../../data/knowledgeCentre';
import { ArticleCard, FeaturedArticle } from './ArticleCard';

export default function LatestAnswers() {
  const featured = articles.find((a) => a.featured) ?? byNewest[0];
  const latest = byNewest.filter((a) => a !== featured).slice(0, 6);
  return (
    <section className="kc-section" aria-labelledby="kc-latest-title">
      <div className="kc-container">
        <div className="kc-head rv">
          <div>
            <p className="eyebrow">// FROM THE BLOG</p>
            <h2 id="kc-latest-title">Latest answers</h2>
          </div>
          <a className="kc-link" href={BLOG_PATH}>See all {articles.length} articles</a>
        </div>
        <FeaturedArticle article={featured} />
        <div className="kc-cards">
          {latest.map((a, i) => <ArticleCard key={a.slug} article={a} delay={(i % 3) * 80} />)}
        </div>
      </div>
    </section>
  );
}
