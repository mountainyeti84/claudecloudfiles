import { useEffect } from 'react';

interface SeoOptions {
  title: string;
  description: string;
  /** path only, e.g. "/resources/" */
  path: string;
  /** schema.org JSON-LD graph for this page */
  jsonLd?: object;
  ogImage?: string;
}

const SITE_URL = 'https://www.adsyeti.com';

function setMeta(attr: 'name' | 'property', key: string, value: string) {
  let el = document.head.querySelector<HTMLMetaElement>(`meta[${attr}="${key}"]`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute(attr, key);
    document.head.appendChild(el);
  }
  el.content = value;
}

/**
 * Sets the title, description, canonical, Open Graph tags and JSON-LD for a
 * page in this single-page app, then restores the homepage values on leave.
 * No extra packages needed.
 */
export function useSeo({ title, description, path, jsonLd, ogImage }: SeoOptions) {
  useEffect(() => {
    const prevTitle = document.title;
    const prevDesc = document.head.querySelector<HTMLMetaElement>('meta[name="description"]')?.content ?? '';
    const url = SITE_URL + path;

    document.title = title;
    setMeta('name', 'description', description);
    setMeta('property', 'og:title', title);
    setMeta('property', 'og:description', description);
    setMeta('property', 'og:url', url);
    if (ogImage) setMeta('property', 'og:image', SITE_URL + ogImage);

    let canonical = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]');
    const createdCanonical = !canonical;
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.rel = 'canonical';
      document.head.appendChild(canonical);
    }
    const prevCanonical = canonical.href;
    canonical.href = url;

    let script: HTMLScriptElement | null = null;
    if (jsonLd) {
      script = document.createElement('script');
      script.type = 'application/ld+json';
      script.dataset.kc = 'true';
      script.textContent = JSON.stringify(jsonLd);
      document.head.appendChild(script);
    }

    return () => {
      document.title = prevTitle;
      setMeta('name', 'description', prevDesc);
      setMeta('property', 'og:title', prevTitle);
      setMeta('property', 'og:description', prevDesc);
      if (createdCanonical) canonical?.remove();
      else if (canonical) canonical.href = prevCanonical;
      script?.remove();
    };
  }, [title, description, path, jsonLd, ogImage]);
}

export { SITE_URL };
