import { articles, topicByKey, articleUrl } from '../../data/knowledgeCentre';

export default function StartHere() {
  const picks = articles.filter((a) => a.startHere).sort((a, b) => a.startHere! - b.startHere!);
  return (
    <section className="kc-section kc-section--tight" aria-labelledby="kc-start-title">
      <div className="kc-container">
        <div className="kc-head rv">
          <div>
            <p className="eyebrow">// NEW HERE?</p>
            <h2 id="kc-start-title">Start with these three</h2>
          </div>
        </div>
        <div className="kc-start">
          {picks.map((a, i) => (
            <a key={a.slug} href={articleUrl(a)} className={`kc-start__card kc-${topicByKey(a.topic).gradient} rv`} data-rvd={i * 90 || undefined}>
              <span className="kc-start__num">START HERE · 0{i + 1}</span>
              <h3>{a.title}</h3>
              <p>{a.summary}</p>
              <span className="kc-link kc-link--light">Read the answer</span>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
