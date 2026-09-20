(function () {
  'use strict';

  document.querySelectorAll('.nav-logo, .footer-brand').forEach(function (logo) {
    logo.textContent = 'merós';
    logo.setAttribute('aria-label', 'Meros Gallery');
  });

  var menu = document.querySelector('.nav-overlay');
  var menuLinks = menu && menu.querySelector('.nav-overlay-links');
  var mainHero = document.querySelector('main > .hero:first-child, main > .art-hero:first-child');
  if (!mainHero) document.body.classList.add('page--light-nav');
  if (menu && menuLinks) {
    Array.prototype.forEach.call(menuLinks.querySelectorAll('a'), function (link, index) {
      var marker = link.querySelector('.nav-overlay-index');
      if (marker) marker.textContent = String(index + 1).padStart(2, '0');
    });

    var preferences = document.createElement('div');
    preferences.className = 'meros-preferences';
    preferences.innerHTML =
      '<label>Язык<select id="siteLanguage" aria-label="Язык сайта"><option value="ru">RU</option><option value="en">ENG</option></select></label>' +
      '<label>Валюта<select id="siteCurrency" aria-label="Валюта"><option>UZS</option><option>USD</option><option>EUR</option></select></label>';
    menuLinks.insertAdjacentElement('afterend', preferences);

    ['siteLanguage', 'siteCurrency'].forEach(function (id) {
      var select = document.getElementById(id);
      var key = 'meros-' + id;
      var stored = window.localStorage.getItem(key);
      if (stored) select.value = stored;
      select.addEventListener('change', function () {
        window.localStorage.setItem(key, select.value);
        document.documentElement.setAttribute('data-' + id.replace('site', '').toLowerCase(), select.value);
      });
    });

    menu.addEventListener('click', function (event) {
      if (event.target !== menu) return;
      var close = document.getElementById('menuCloseBtn');
      if (close) close.click();
    });

    var trigger = document.getElementById('menuBtn');
    var closeButton = document.getElementById('menuCloseBtn');
    if (trigger && closeButton) {
      trigger.addEventListener('click', function () {
        closeButton.focus({ preventScroll: true });
      });
      closeButton.addEventListener('click', function () { trigger.focus(); });
      menu.addEventListener('keydown', function (event) {
        if (event.key !== 'Tab') return;
        var focusable = Array.prototype.slice.call(menu.querySelectorAll('a, button, select'));
        if (!focusable.length) return;
        var first = focusable[0];
        var last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      });
    }
  }

  /* Horizontal rails (product carousels, category hero, Art page). One handler
     for every [data-rail] block: prev/next buttons, counter and progress line. */
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('[data-rail]').forEach(function (rail) {
    var track = rail.querySelector('[data-rail-track]');
    if (!track) return;
    var prev = rail.querySelector('[data-rail-prev]');
    var next = rail.querySelector('[data-rail-next]');
    var current = rail.querySelector('[data-rail-current]');
    var progress = rail.querySelector('[data-rail-progress]');
    var ticking = false;

    function step() {
      var first = track.firstElementChild;
      if (!first) return track.clientWidth;
      var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      return first.getBoundingClientRect().width + gap;
    }
    function update() {
      ticking = false;
      var max = track.scrollWidth - track.clientWidth;
      var pos = track.scrollLeft;
      if (prev) prev.disabled = pos <= 2;
      if (next) next.disabled = pos >= max - 2;
      if (progress) progress.style.width = (max > 0 ? Math.max(8, pos / max * 100) : 100) + '%';
      if (current) current.textContent = String(Math.round(pos / step()) + 1).padStart(2, '0');
    }
    function go(direction) {
      track.scrollBy({ left: direction * step(), behavior: reduceMotion ? 'auto' : 'smooth' });
    }
    if (prev) prev.addEventListener('click', function () { go(-1); });
    if (next) next.addEventListener('click', function () { go(1); });
    track.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  /* Text motion. Headlines rise word by word out of a mask, body paragraphs
     lift in softly, section labels settle from wide tracking. Nothing runs
     for prefers-reduced-motion or without IntersectionObserver; the
     `js-motion` class is what hides text, so it can never stay invisible. */
  if (!reduceMotion && 'IntersectionObserver' in window) {
    var headingSelector = [
      'main h1', 'main h2', '.hero-title', '.news-detail-title', '.cat-hero-name',
      '.art-hero-title', '.founder-editorial-head h2', '.quote-editorial-copy blockquote',
      '.space-editorial-copy h3'
    ].join(',');
    var headings = Array.prototype.filter.call(document.querySelectorAll(headingSelector), function (el) {
      return !el.classList.contains('visually-hidden') && !el.closest('[data-reveal="mask"]') && !el.closest('.nav-overlay');
    });

    var wordIndex;
    function splitWords(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var parts = child.nodeValue.split(/(\s+)/);
          var frag = document.createDocumentFragment();
          parts.forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var outer = document.createElement('span');
            outer.className = 'word';
            outer.setAttribute('aria-hidden', 'true');
            var inner = document.createElement('span');
            inner.textContent = part;
            inner.style.setProperty('--i', Math.min(wordIndex++, 14));
            outer.appendChild(inner);
            frag.appendChild(outer);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1 && child.tagName !== 'BR') {
          splitWords(child);
        }
      });
    }
    headings.forEach(function (heading) {
      var label = heading.textContent.replace(/\s+/g, ' ').trim();
      if (!label) return;
      heading.setAttribute('aria-label', label);
      wordIndex = 0;
      splitWords(heading);
      heading.classList.add('split-heading');
    });

    var rising = Array.prototype.filter.call(document.querySelectorAll('main .body, main .body-lg, main .hero-tagline, main .cat-hero-desc'), function (el) {
      return !el.closest('[data-reveal]');
    });
    rising.forEach(function (el) { el.classList.add('text-rise'); });
    var labels = document.querySelectorAll('main .eyebrow');
    labels.forEach(function (el) { el.classList.add('label-settle'); });

    document.documentElement.classList.add('js-motion');
    var textObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        textObserver.unobserve(entry.target);
      });
    }, { threshold: 0.2, rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.split-heading, .text-rise, .label-settle').forEach(function (el) { textObserver.observe(el); });
  }

  document.querySelectorAll('form[action="#"]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var submit = form.querySelector('[type="submit"]');
      if (!submit) return;
      submit.textContent = 'Заявка подготовлена';
      submit.setAttribute('aria-live', 'polite');
    });
  });
})();
