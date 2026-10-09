import { useEffect } from 'react';
import type { RefObject } from 'react';

/**
 * Same scroll-reveal as the homepage (adds .in-view to .rv elements), scoped to
 * one page so it also works after client-side navigation.
 */
export function useReveal(root: RefObject<HTMLElement>) {
  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) {
            const d = +(en.target.getAttribute('data-rvd') || 0);
            if (d) setTimeout(() => en.target.classList.add('in-view'), d);
            else en.target.classList.add('in-view');
            io.unobserve(en.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    el.querySelectorAll('.rv').forEach((n) => io.observe(n));
    return () => io.disconnect();
  }, [root]);
}
