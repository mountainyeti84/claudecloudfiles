import { articles, questionTypes, typeUrl } from '../../data/knowledgeCentre';

/** They Ask, You Answer: the "Big 5" questions buyers ask before they buy. */
export default function QuestionTypes() {
  return (
    <section className="kc-section" aria-labelledby="kc-qtypes-title">
      <div className="kc-container">
        <div className="kc-head rv">
          <div>
            <p className="eyebrow">// BROWSE BY QUESTION</p>
            <h2 id="kc-qtypes-title">The questions you&rsquo;d ask<br />before hiring anyone</h2>
            <p className="kc-head__lede">Price, problems, comparisons, reviews and how-tos. If it&rsquo;s on your mind before you spend money, it&rsquo;s in here.</p>
          </div>
        </div>
        <div className="kc-qtypes">
          {questionTypes.map((q, i) => (
            <a key={q.key} href={typeUrl(q.key)} className="kc-qtype rv" data-rvd={i * 60 || undefined}>
              <span className="kc-qtype__icon" aria-hidden="true">{q.icon}</span>
              <strong>{q.name}</strong>
              <span>{q.blurb}</span>
              <em>{articles.filter((a) => a.type === q.key).length} answers &rarr;</em>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
