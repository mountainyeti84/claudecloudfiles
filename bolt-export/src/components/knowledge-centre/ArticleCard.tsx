import type { Article, TopicKey } from '../../data/knowledgeCentre';
import { topicByKey, typeByKey, articleUrl, topicUrl, formatDate } from '../../data/knowledgeCentre';

/** Gradient thumbnail in the homepage's service-card style. Set article.image to use a photo instead. */
export function Thumb({ article }: { article: Article }) {
  const t = topicByKey(article.topic);
  return (
    <div className={`kc-thumb kc-${t.gradient}`} aria-hidden="true">
      <span className="kc-thumb__q">{typeByKey(article.type).name}</span>
      <span className="kc-thumb__icon">{t.icon}</span>
      {article.image && <img src={article.image} alt="" loading="lazy" />}
    </div>
  );
}

export function TopicTag({ topic, link = true }: { topic: TopicKey; link?: boolean }) {
  const t = topicByKey(topic);
  const inner = (<><i aria-hidden="true" />{t.name}</>);
  return link
    ? <a className={`kc-tag kc-dot-${topic}`} href={topicUrl(topic)}>{inner}</a>
    : <span className={`kc-tag kc-dot-${topic}`}>{inner}</span>;
}

export function ArticleCard({ article, delay = 0 }: { article: Article; delay?: number }) {
  return (
    <article className="kc-card rv" data-rvd={delay || undefined}>
      <Thumb article={article} />
      <div className="kc-card__body">
        <div className="kc-tags"><TopicTag topic={article.topic} /></div>
        <h3><a href={articleUrl(article)}>{article.title}</a></h3>
        <p>{article.summary}</p>
        <div className="kc-meta">
          <time dateTime={article.date}>{formatDate(article.date)}</time>
          <span className="kc-meta__dot">{article.minutes} min read</span>
        </div>
      </div>
    </article>
  );
}

export function FeaturedArticle({ article }: { article: Article }) {
  return (
    <a className="kc-featured rv" href={articleUrl(article)}>
      <Thumb article={article} />
      <div className="kc-featured__body">
        <div className="kc-tags">
          <TopicTag topic={article.topic} link={false} />
          <span className="kc-tag kc-tag--plain">Most read</span>
        </div>
        <h3>{article.title}</h3>
        <p>{article.summary}</p>
        <div className="kc-meta"><span>By Andy Moore</span><span className="kc-meta__dot">{article.minutes} min read</span></div>
        <span className="kc-link">Read the answer</span>
      </div>
    </a>
  );
}
