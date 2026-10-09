import { useState } from 'react';
import type { FormEvent } from 'react';
import { submitContact } from '../../lib/submitContact';

/**
 * "They Ask, You Answer" in action: visitors send the questions we haven't
 * answered yet. Styled like the homepage contact card, with the peeking Yeti.
 */
export default function AskTheYeti() {
  const [question, setQuestion] = useState('');
  const [email, setEmail] = useState('');
  const [state, setState] = useState<'idle' | 'sending' | 'done' | 'error'>('idle');

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setState('sending');
    try {
      await submitContact({
        name: 'Knowledge Centre question',
        email,
        primaryChallenge: 'kc-question',
        message: `Question for the Knowledge Centre:\n${question}\n(Sent from ${window.location.pathname})`,
      });
      setState('done');
    } catch {
      setState('error');
    }
  };

  return (
    <section className="kc-section kc-ask-wrap" id="ask" aria-labelledby="kc-ask-title">
      <div className="kc-ask rv">
        <div className="g-blob b1" style={{ width: '55%', opacity: 0.35 }} aria-hidden="true" />
        <div className="g-blob b4" style={{ width: '45%', opacity: 0.35 }} aria-hidden="true" />
        <div className="kc-ask__body">
          <p className="eyebrow on-dark">// ASK THE YETI</p>
          <h2 id="kc-ask-title">Can&rsquo;t find your answer? <span className="kc-grad">Ask us.</span></h2>
          <p>
            If you&rsquo;re wondering about it, other founders probably are too. Send us your question about ads, tracking or leads and we&rsquo;ll answer it here, honestly, even if the honest answer is &ldquo;you don&rsquo;t need an agency for that&rdquo;.
          </p>
          {state === 'done' ? (
            <div className="kc-ask__done" role="status">
              <strong>Got it, cheers!</strong> We&rsquo;ll email you when your answer goes live.
            </div>
          ) : (
            <form onSubmit={onSubmit}>
              <label className="kc-vh" htmlFor="kc-ask-q">Your question</label>
              <textarea id="kc-ask-q" required placeholder="What would you like to know?" value={question} onChange={(e) => setQuestion(e.target.value)} />
              <label className="kc-vh" htmlFor="kc-ask-email">Your email</label>
              <input id="kc-ask-email" type="email" required placeholder="Your email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <button className="btn" type="submit" disabled={state === 'sending'}>
                {state === 'sending' ? 'Sending…' : <>Send my question <span className="arr">&rarr;</span></>}
              </button>
              {state === 'error' && <p className="kc-form-error" role="alert">That didn&rsquo;t go through. Try again, or email andy@adsyeti.com.</p>}
            </form>
          )}
          <small className="kc-ask__fine">We&rsquo;ll email you when it&rsquo;s answered. We never share your details.</small>
        </div>
        <img className="kc-ask__yeti" src="/kc/yeti-peek.webp" alt="" width={560} height={447} loading="lazy" />
      </div>
    </section>
  );
}
