import { useEffect, useId, useMemo, useRef, useState } from 'react';
import type { FormEvent, KeyboardEvent, ReactNode } from 'react';
import { searchArticles, articleUrl, topicByKey, typeByKey, BLOG_PATH } from '../../data/knowledgeCentre';

function highlight(text: string, query: string): ReactNode {
  const terms = query.toLowerCase().split(/\s+/).filter((t) => t.length > 1);
  if (!terms.length) return text;
  const re = new RegExp(`(${terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'ig');
  return text.split(re).map((part, i) => (i % 2 ? <mark key={i}>{part}</mark> : part));
}

interface Props {
  placeholder?: string;
}

/** Instant, as-you-type search over the Knowledge Centre (combobox pattern). */
export default function KcSearch({ placeholder = 'Ask a question, e.g. “why is my cost per lead so high?”' }: Props) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const wrapRef = useRef<HTMLFormElement>(null);
  const listId = useId();

  const results = useMemo(() => (query.trim().length >= 2 ? searchArticles(query) : []), [query]);
  const showList = open && query.trim().length >= 2;

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (!wrapRef.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('click', onDoc);
    return () => document.removeEventListener('click', onDoc);
  }, []);

  const go = (href: string) => {
    window.location.href = href;
  };

  const onKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') return setOpen(false);
    if (!results.length) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      setOpen(true);
      setActive((i) => (i + (e.key === 'ArrowDown' ? 1 : -1) + results.length) % results.length);
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    const pick = results[active > -1 ? active : 0];
    if (pick) go(articleUrl(pick));
    else if (query.trim()) go(`${BLOG_PATH}?q=${encodeURIComponent(query.trim())}`);
  };

  return (
    <form className="kc-search" role="search" ref={wrapRef} onSubmit={onSubmit}>
      <label className="kc-vh" htmlFor={`${listId}-input`}>Search the Knowledge Centre</label>
      <div className="kc-search__field">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" strokeWidth="2" />
          <path d="M20 20l-4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
        <input
          id={`${listId}-input`}
          className="kc-search__input"
          type="search"
          autoComplete="off"
          placeholder={placeholder}
          value={query}
          role="combobox"
          aria-expanded={showList}
          aria-controls={listId}
          aria-autocomplete="list"
          aria-activedescendant={active > -1 ? `${listId}-${active}` : undefined}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); setActive(-1); }}
          onFocus={() => setOpen(true)}
          onKeyDown={onKeyDown}
        />
        <button className="btn kc-search__btn" type="submit">Search</button>
      </div>
      {showList && (
        <ul className="kc-search__results" id={listId} role="listbox">
          {results.length ? (
            results.map((a, i) => (
              <li key={a.slug} id={`${listId}-${i}`} role="option" aria-selected={i === active}>
                <a href={articleUrl(a)} className={i === active ? 'is-active' : undefined}>
                  {highlight(a.title, query)}
                  <small>{topicByKey(a.topic).name} · {typeByKey(a.type).name}</small>
                </a>
              </li>
            ))
          ) : (
            <li className="kc-search__empty">
              No answer yet. <a href="#ask">Ask the Yeti</a> and we&rsquo;ll write it.
            </li>
          )}
        </ul>
      )}
    </form>
  );
}
