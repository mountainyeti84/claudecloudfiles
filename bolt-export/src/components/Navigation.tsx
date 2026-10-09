import { useEffect, useRef, useState } from 'react';
import { useWizard } from '../context/WizardContext';
import { topics, topicUrl, KC_PATH, BLOG_PATH } from '../data/knowledgeCentre';
import '../styles/nav-resources.css';

export default function Navigation() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [resOpen, setResOpen] = useState(false);
  const resRef = useRef<HTMLLIElement>(null);
  const { openWizard } = useWizard();
  const onResources = typeof window !== 'undefined' && window.location.pathname.startsWith(KC_PATH);
  const close = () => { setMenuOpen(false); setResOpen(false); };

  useEffect(() => {
    const onDoc = (e: MouseEvent) => { if (!resRef.current?.contains(e.target as Node)) setResOpen(false); };
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setResOpen(false); };
    document.addEventListener('click', onDoc);
    document.addEventListener('keydown', onKey);
    return () => { document.removeEventListener('click', onDoc); document.removeEventListener('keydown', onKey); };
  }, []);

  const hoverable = () => window.matchMedia('(hover: hover) and (min-width: 761px)').matches;

  return (
    <nav className="nav" aria-label="Main">
      <a className="logo" href="/#top" aria-label="Ads Yeti home">
        <img src="/untitled_design_(24).png" alt="Ads Yeti" />
      </a>
      <ul className={`nav-links${menuOpen ? ' open' : ''}`} id="navLinks">
        <li><a href="/#work" onClick={close}>Client work</a></li>
        <li><a href="/#services" onClick={close}>Services</a></li>
        <li><a href="/#about" onClick={close}>Why us</a></li>
        <li
          ref={resRef}
          className={`nav-res${resOpen ? ' is-open' : ''}`}
          onMouseEnter={() => hoverable() && setResOpen(true)}
          onMouseLeave={() => hoverable() && setResOpen(false)}
        >
          <button
            type="button"
            className={`nav-res__btn${onResources ? ' is-current' : ''}`}
            aria-expanded={resOpen}
            aria-controls="nav-res-panel"
            onClick={() => setResOpen((o) => !o)}
          >
            Resources
            <svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </button>
          <div className="nav-res__panel" id="nav-res-panel">
            <div className="nav-res__col">
              <p className="nav-res__label">// Resources</p>
              <a className="nav-res__link" href={KC_PATH} onClick={close}>
                <span className="nav-res__icon" aria-hidden="true">🏔️</span>
                <span><strong>Knowledge Centre</strong><small>Every question we get asked, answered honestly.</small></span>
              </a>
              <a className="nav-res__link" href={BLOG_PATH} onClick={close}>
                <span className="nav-res__icon" aria-hidden="true">📝</span>
                <span><strong>Blog</strong><small>All articles, filterable by topic and question.</small></span>
              </a>
              <a className="nav-res__link" href="/meta-ads-diagnostic-tool/" onClick={close}>
                <span className="nav-res__icon" aria-hidden="true">🩺</span>
                <span><strong>Ad Insights Tool</strong><small>Free diagnostic for your Meta ads account.</small></span>
              </a>
              <p className="nav-res__label">// Topics</p>
              <div className="nav-res__topics">
                {topics.map((t) => (
                  <a key={t.key} className={`nav-res__topic kc-dot-${t.key}`} href={topicUrl(t.key)} onClick={close}>
                    <i aria-hidden="true" />{t.name}
                  </a>
                ))}
              </div>
            </div>
            <a className="nav-res__feature" href={`${BLOG_PATH}why-facebook-ads-get-leads-but-no-sales/`} onClick={close}>
              <span className="nav-res__label">// Start here</span>
              <strong>Why are my Facebook ads getting leads but no sales?</strong>
              <span>The most common problem we see, and where to look first.</span>
              <em>Read the answer &rarr;</em>
              <img src="/kc/yeti-point.webp" alt="" width={190} height={121} loading="lazy" />
            </a>
          </div>
        </li>
        <li><a href="/#contact" onClick={close}>Contact</a></li>
        <li><a href="/meta-ads-diagnostic-tool/" onClick={close}>Ad Insights Tool</a></li>
      </ul>
      <button className="btn" onClick={openWizard}>
        Let's Chat <span className="arr">&rarr;</span>
      </button>
      <button
        className="burger"
        aria-expanded={menuOpen}
        aria-controls="navLinks"
        aria-label="Menu"
        onClick={() => setMenuOpen(!menuOpen)}
      >
        <span></span>
        <span></span>
      </button>
    </nav>
  );
}
