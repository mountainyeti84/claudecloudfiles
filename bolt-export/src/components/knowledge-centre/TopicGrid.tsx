import { articles, topics, topicUrl } from '../../data/knowledgeCentre';

/** Cream "paper" panel, same as the homepage Services and Calculator sections. */
export default function TopicGrid() {
  return (
    <section className="kc-paper-wrap" aria-labelledby="kc-topics-title">
      <div className="kc-paper rv">
        <div className="kc-glow kc-glow--1" aria-hidden="true" />
        <div className="kc-glow kc-glow--2" aria-hidden="true" />
        <div className="kc-container">
          <div className="kc-head">
            <div>
              <p className="eyebrow">// BROWSE BY TOPIC</p>
              <h2 id="kc-topics-title">From the ad to the booking</h2>
              <p className="kc-head__lede">We follow the whole journey, so the Knowledge Centre does too: ad, lead, follow-up, conversation, customer.</p>
            </div>
          </div>
          <div className="kc-topics">
            {topics.map((t) => (
              <a key={t.key} href={topicUrl(t.key)} className="kc-topic">
                <span className={`kc-topic__icon kc-${t.gradient}`} aria-hidden="true">{t.icon}</span>
                <span>
                  <h3>{t.name}</h3>
                  <p>{t.blurb}</p>
                  <small>{articles.filter((a) => a.topic === t.key).length} articles &rarr;</small>
                </span>
              </a>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
