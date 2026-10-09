import { useState } from 'react';
import type { FormEvent } from 'react';
import { submitContact } from '../../lib/submitContact';

export default function NewsletterStrip() {
  const [email, setEmail] = useState('');
  const [state, setState] = useState<'idle' | 'sending' | 'done' | 'error'>('idle');

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setState('sending');
    try {
      await submitContact({ name: 'Knowledge Centre subscriber', email, primaryChallenge: 'kc-newsletter', message: 'Subscribe me to new Knowledge Centre answers.\n(Sent from /resources/)' });
      setState('done');
    } catch {
      setState('error');
    }
  };

  return (
    <div className="kc-container">
      <div className="kc-newsletter rv">
        <div>
          <h3>New answers, once a fortnight</h3>
          <p>One useful email. No fluff, and unsubscribing takes one click.</p>
        </div>
        {state === 'done' ? (
          <p className="kc-newsletter__done" role="status">Lovely, you&rsquo;re on the list. 🏔️</p>
        ) : (
          <form onSubmit={onSubmit}>
            <label className="kc-vh" htmlFor="kc-nl-email">Email address</label>
            <input id="kc-nl-email" type="email" required placeholder="you@company.co.uk" value={email} onChange={(e) => setEmail(e.target.value)} />
            <button className="btn" type="submit" disabled={state === 'sending'}>{state === 'sending' ? 'Sending…' : 'Subscribe'}</button>
            {state === 'error' && <p className="kc-form-error" role="alert">That didn&rsquo;t go through. Mind trying again?</p>}
          </form>
        )}
      </div>
    </div>
  );
}
