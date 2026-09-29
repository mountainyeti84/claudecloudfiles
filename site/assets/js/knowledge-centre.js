/* Ads Yeti Knowledge Centre: progressive enhancement only.
   Every article link, heading and card is in the HTML, so search engines and
   AI crawlers get the full page without running this file. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------- Main menu: Resources mega menu + mobile toggle ---------- */
  var toggle = $(".nav-toggle");
  var nav = $(".nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("nav--open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }
  $$(".nav__item--has-mega").forEach(function (item) {
    var btn = $(".nav__link", item);
    var hoverable = window.matchMedia("(hover: hover) and (min-width: 981px)");
    var setOpen = function (open) {
      item.classList.toggle("nav__item--open", open);
      btn.setAttribute("aria-expanded", String(open));
    };
    btn.addEventListener("click", function () { setOpen(!item.classList.contains("nav__item--open")); });
    item.addEventListener("mouseenter", function () { if (hoverable.matches) setOpen(true); });
    item.addEventListener("mouseleave", function () { if (hoverable.matches) setOpen(false); });
    item.addEventListener("keydown", function (e) { if (e.key === "Escape") { setOpen(false); btn.focus(); } });
    document.addEventListener("click", function (e) { if (!item.contains(e.target)) setOpen(false); });
  });

  /* ---------- Instant search (hero + header) ---------- */
  var indexPromise = null;
  function loadIndex() {
    if (!indexPromise) {
      indexPromise = fetch("/resources/search-index.json")
        .then(function (r) { return r.json(); })
        .catch(function () { return []; });
    }
    return indexPromise;
  }
  function escapeHtml(s) { return s.replace(/[&<>"']/g, function (c) { return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]; }); }
  function highlight(text, terms) {
    var out = escapeHtml(text);
    terms.forEach(function (t) {
      if (t.length < 2) return;
      out = out.replace(new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>");
    });
    return out;
  }
  function score(item, terms) {
    var title = item.title.toLowerCase();
    var hay = (item.title + " " + item.summary + " " + item.topic + " " + item.type + " " + (item.keywords || []).join(" ")).toLowerCase();
    var s = 0;
    for (var i = 0; i < terms.length; i++) {
      if (hay.indexOf(terms[i]) === -1) return 0; // every word must match somewhere
      s += title.indexOf(terms[i]) !== -1 ? 3 : 1;
    }
    return s;
  }
  $$("[data-search]").forEach(function (form) {
    var input = $("input", form);
    var list = $(".search__results", form);
    var active = -1;
    var render = function () {
      var q = input.value.trim().toLowerCase();
      if (q.length < 2) { list.hidden = true; input.setAttribute("aria-expanded", "false"); return; }
      loadIndex().then(function (items) {
        var terms = q.split(/\s+/).filter(Boolean);
        var hits = items.map(function (it) { return { it: it, s: score(it, terms) }; })
          .filter(function (h) { return h.s > 0; })
          .sort(function (a, b) { return b.s - a.s; })
          .slice(0, 6);
        active = -1;
        list.innerHTML = hits.length
          ? hits.map(function (h, i) {
              return '<li role="option" id="sr-' + i + '"><a href="' + h.it.url + '">' + highlight(h.it.title, terms) +
                "<small>" + escapeHtml(h.it.topic) + " · " + escapeHtml(h.it.type) + "</small></a></li>";
            }).join("")
          : '<li class="search__empty">No answer yet. <a href="#ask">Ask the Yeti</a> and we\'ll write it.</li>';
        list.hidden = false;
        input.setAttribute("aria-expanded", "true");
      });
    };
    input.addEventListener("focus", loadIndex, { once: true });
    input.addEventListener("input", render);
    input.addEventListener("keydown", function (e) {
      var links = $$("a[href]:not([href='#ask'])", list);
      if (!links.length) return;
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        active = (active + (e.key === "ArrowDown" ? 1 : -1) + links.length) % links.length;
        links.forEach(function (a, i) { a.setAttribute("aria-selected", String(i === active)); });
        input.setAttribute("aria-activedescendant", "sr-" + active);
      } else if (e.key === "Enter" && active > -1) {
        e.preventDefault(); window.location.href = links[active].href;
      } else if (e.key === "Escape") { list.hidden = true; }
    });
    document.addEventListener("click", function (e) { if (!form.contains(e.target)) list.hidden = true; });
    // With no JS the form submits ?q= to the blog archive, which filters on load.
  });

  /* ---------- Archive filters (blog + topic pages) ---------- */
  var grid = $("[data-filter-grid]");
  if (grid) {
    var cards = $$(".card", grid);
    var chips = $$("[data-filter-topic]");
    var typeSelect = $("[data-filter-type]");
    var sortSelect = $("[data-sort]");
    var textInput = $("[data-filter-text]");
    var countEl = $("[data-results-count]");
    var emptyEl = $("[data-no-results]");
    var moreBtn = $("[data-load-more]");
    var pageSize = 9, shown = pageSize;
    var state = { topic: "all", type: "all", q: "" };

    var params = new URLSearchParams(location.search);
    if (params.get("topic")) state.topic = params.get("topic");
    if (params.get("type")) state.type = params.get("type");
    if (params.get("q")) state.q = params.get("q").toLowerCase();
    if (textInput && state.q) textInput.value = params.get("q");
    if (typeSelect) typeSelect.value = state.type;

    var apply = function (resetPaging) {
      if (resetPaging) shown = pageSize;
      chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.filterTopic === state.topic)); });
      if (sortSelect) {
        var key = sortSelect.value;
        cards.sort(function (a, b) {
          if (key === "popular") return (+b.dataset.popularity) - (+a.dataset.popularity);
          if (key === "quick") return (+a.dataset.minutes) - (+b.dataset.minutes);
          return b.dataset.date.localeCompare(a.dataset.date);
        }).forEach(function (c) { grid.appendChild(c); });
      }
      var matched = cards.filter(function (c) {
        var okTopic = state.topic === "all" || c.dataset.topic === state.topic;
        var okType = state.type === "all" || c.dataset.type === state.type;
        var okText = !state.q || c.textContent.toLowerCase().indexOf(state.q) !== -1;
        return okTopic && okType && okText;
      });
      cards.forEach(function (c) { c.hidden = true; });
      matched.slice(0, shown).forEach(function (c) { c.hidden = false; });
      if (countEl) countEl.textContent = matched.length + (matched.length === 1 ? " answer" : " answers");
      if (emptyEl) emptyEl.hidden = matched.length > 0;
      if (moreBtn) moreBtn.parentElement.hidden = matched.length <= shown;

      var p = new URLSearchParams();
      if (state.topic !== "all") p.set("topic", state.topic);
      if (state.type !== "all") p.set("type", state.type);
      if (state.q) p.set("q", state.q);
      history.replaceState(null, "", location.pathname + (p.toString() ? "?" + p : ""));
    };
    chips.forEach(function (c) { c.addEventListener("click", function () { state.topic = c.dataset.filterTopic; apply(true); }); });
    if (typeSelect) typeSelect.addEventListener("change", function () { state.type = typeSelect.value; apply(true); });
    if (sortSelect) sortSelect.addEventListener("change", function () { apply(true); });
    if (textInput) textInput.addEventListener("input", function () { state.q = textInput.value.trim().toLowerCase(); apply(true); });
    if (moreBtn) moreBtn.addEventListener("click", function () { shown += pageSize; apply(false); });
    apply(true);
  }

  /* ---------- Article: reading progress, TOC highlight, copy link ---------- */
  var article = $("[data-article]");
  if (article) {
    var bar = $(".progress");
    var onScroll = function () {
      var r = article.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      var pct = total > 0 ? Math.min(100, Math.max(0, (-r.top / total) * 100)) : 0;
      if (bar) bar.style.width = pct + "%";
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    var tocLinks = $$(".toc a");
    if ("IntersectionObserver" in window && tocLinks.length) {
      var byId = {};
      tocLinks.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting && byId[en.target.id]) {
            tocLinks.forEach(function (a) { a.classList.remove("is-active"); });
            byId[en.target.id].classList.add("is-active");
          }
        });
      }, { rootMargin: "-20% 0px -70% 0px" });
      $$("h2[id]", article).forEach(function (h) { io.observe(h); });
    }
  }
  $$("[data-copy-link]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (navigator.clipboard) navigator.clipboard.writeText(location.href);
      btn.textContent = "✓";
      setTimeout(function () { btn.textContent = "🔗"; }, 1500);
    });
  });

  /* ---------- Topic/article counts in the hero, from the markup ---------- */
  $$("[data-count]").forEach(function (el) {
    var n = $$(el.dataset.count).length;
    if (n) el.textContent = n;
  });
})();
