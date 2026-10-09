import { useRef } from 'react';
import { useReveal } from '../hooks/useReveal';
import { useSeo } from '../hooks/useSeo';
import { KC_PATH } from '../data/knowledgeCentre';
import AskTheYeti from '../components/knowledge-centre/AskTheYeti';
import '../styles/knowledge-centre.css';

/**
 * Temporary page for Knowledge Centre URLs that don't exist yet (articles,
 * topics, the blog archive). Replace route by route as those pages are built.
 */
export default function KcComingSoon() {
  const root = useRef<HTMLDivElement>(null);
  useReveal(root);
  useSeo({ title: 'Coming soon | Ads Yeti Knowledge Centre', description: "We're still writing this one.", path: window.location.pathname });
  return (
    <div className="kc" ref={root}>
      <section className="kc-soon">
        <img src="/kc/yeti-dizzy.webp" alt="" width={480} height={467} />
        <p className="eyebrow">// STILL WRITING THIS ONE</p>
        <h1>The Yeti&rsquo;s halfway through this answer.</h1>
        <p>It&rsquo;ll be up soon. In the meantime, have a look around the Knowledge Centre or ask us directly.</p>
        <a className="btn" href={KC_PATH}>Back to the Knowledge Centre <span className="arr">&rarr;</span></a>
      </section>
      <AskTheYeti />
    </div>
  );
}
