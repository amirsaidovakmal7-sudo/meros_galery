(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cartLink = document.getElementById('navCartLink');
  var cartBadge = document.getElementById('navCartBadge');

  var live = document.createElement('span');
  live.className = 'cart-sr-only';
  live.setAttribute('role', 'status');
  document.body.appendChild(live);

  function ease(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function lerp(a, b, t) { return a + (b - a) * t; }

  /* ---------- the flight: a quadratic arc from the photo to the cart icon ---------- */

  function fly(photo) {
    return new Promise(function (resolve) {
      var target = cartLink && (cartLink.querySelector('svg') || cartLink);
      if (reduced || !photo || !target || !photo.animate) return resolve();

      var from = photo.getBoundingClientRect();
      var to = target.getBoundingClientRect();
      if (!from.width || !from.height) return resolve();

      var clone = photo.cloneNode(false);
      clone.removeAttribute('id');
      clone.removeAttribute('srcset');
      clone.className = 'cart-fly';
      clone.setAttribute('aria-hidden', 'true');
      clone.style.left = from.left + 'px';
      clone.style.top = from.top + 'px';
      clone.style.width = from.width + 'px';
      clone.style.height = from.height + 'px';
      document.body.appendChild(clone);

      var p0 = { x: from.left + from.width / 2, y: from.top + from.height / 2 };
      var p2 = { x: to.left + to.width / 2, y: to.top + to.height / 2 };
      // Control point sits above the start and toward the cart: the item lifts
      // first, then curves into the icon instead of sliding in a straight line.
      var p1 = { x: lerp(p0.x, p2.x, .12), y: Math.min(p0.y, p2.y) - Math.max(60, Math.abs(p0.y - p2.y) * .18) };

      var big = Math.max(from.width, from.height);
      var thumb = Math.min(1, 150 / big);   // shrinks to a small card first…
      var tiny = Math.min(1, 22 / big);     // …then to the size of the icon
      var steps = 28;
      var frames = [];

      for (var i = 0; i <= steps; i++) {
        var t = i / steps;
        var e = ease(t);
        var u = 1 - e;
        var x = u * u * p0.x + 2 * u * e * p1.x + e * e * p2.x;
        var y = u * u * p0.y + 2 * u * e * p1.y + e * e * p2.y;
        var scale = t < .3 ? lerp(1, thumb, ease(t / .3)) : lerp(thumb, tiny, ease((t - .3) / .7));
        var rot = -14 * Math.sin(Math.PI * Math.min(1, t * 1.15));
        frames.push({
          transform: 'translate(' + (x - p0.x) + 'px,' + (y - p0.y) + 'px) rotate(' + rot + 'deg) scale(' + scale + ')',
          opacity: t > .9 ? 1 - (t - .9) * 10 : 1,
          borderRadius: t < .3 ? '2px' : Math.round(lerp(2, 60, (t - .3) / .7)) + '%',
          offset: t
        });
      }

      var anim = clone.animate(frames, { duration: 900, easing: 'linear', fill: 'forwards' });
      var done = function () { clone.remove(); resolve(); };
      anim.onfinish = done;
      anim.oncancel = done;
    });
  }

  /* ---------- the landing: icon squash + badge pop ---------- */

  function retrigger(el, cls) {
    el.classList.remove(cls);
    void el.offsetWidth;
    el.classList.add(cls);
  }

  function land(count) {
    if (cartBadge && typeof count === 'number') {
      cartBadge.textContent = count;
      cartBadge.hidden = count < 1;
      retrigger(cartBadge, 'is-pop');
    }
    if (cartLink && !reduced) retrigger(cartLink, 'is-catching');
  }

  function readBadge(html) {
    var doc = new DOMParser().parseFromString(html, 'text/html');
    var badge = doc.getElementById('navCartBadge');
    return badge ? parseInt(badge.textContent, 10) || 0 : null;
  }

  function sourcePhoto(form) {
    var scope = form.closest('section') || document;
    var track = scope.querySelector('.story-carousel-track');
    if (track) {
      var left = track.getBoundingClientRect().left;
      var best = null;
      var bestDist = Infinity;
      track.querySelectorAll('img').forEach(function (img) {
        var dist = Math.abs(img.getBoundingClientRect().left - left);
        if (dist < bestDist) { bestDist = dist; best = img; }
      });
      if (best) return best;
    }
    return scope.querySelector('img');
  }

  function setButton(btn, label, state) {
    btn.textContent = label;
    btn.classList.toggle('is-added', state === 'added');
    btn.classList.toggle('is-failed', state === 'failed');
    live.textContent = state ? label : '';
  }

  /* ---------- add-to-cart forms ---------- */

  document.querySelectorAll('.add-to-cart-form').forEach(function (form) {
    var input = form.querySelector('.qty-input');
    var minus = form.querySelector('.qty-minus');
    var plus = form.querySelector('.qty-plus');
    var button = form.querySelector('[type="submit"]');
    var idleLabel = button ? button.textContent : '';

    function clamp(v) {
      var max = parseInt(input.getAttribute('max'), 10) || 1;
      return Math.max(1, Math.min(max, isNaN(v) ? 1 : v));
    }
    if (input) {
      if (minus) minus.addEventListener('click', function () { input.value = clamp(parseInt(input.value, 10) - 1); });
      if (plus) plus.addEventListener('click', function () { input.value = clamp(parseInt(input.value, 10) + 1); });
      input.addEventListener('change', function () { input.value = clamp(parseInt(input.value, 10)); });
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (!button || button.getAttribute('aria-disabled') === 'true') return;
      button.setAttribute('aria-disabled', 'true');

      var flight = fly(sourcePhoto(form));
      var request = fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        credentials: 'same-origin',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      }).then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.text();
      }).then(readBadge);

      Promise.all([flight, request]).then(function (result) {
        land(result[1]);
        setButton(button, 'Добавлено в корзину', 'added');
      }).catch(function (error) {
        console.error('Не удалось добавить в корзину:', error);
        setButton(button, 'Не удалось добавить', 'failed');
      }).then(function () {
        setTimeout(function () {
          setButton(button, idleLabel, '');
          button.removeAttribute('aria-disabled');
        }, 2000);
      });
    });
  });

  /* ---------- cart page ---------- */

  function digits(text) {
    var d = String(text || '').replace(/[^\d]/g, '');
    return d ? parseInt(d, 10) : NaN;
  }
  function money(n) { return n.toLocaleString('ru-RU') + ' сум'; }

  var rows = document.querySelectorAll('.cart-row');
  if (rows.length) {
    var total = 0;
    rows.forEach(function (row) {
      var unit = digits(row.getAttribute('data-price'));
      var qty = parseInt(row.getAttribute('data-amount'), 10) || 0;
      if (isNaN(unit)) return;
      var sub = unit * qty;
      total += sub;
      var unitEl = row.querySelector('.cart-row-unit-price');
      var subEl = row.querySelector('.cart-row-subtotal');
      if (unitEl) unitEl.textContent = money(unit);
      if (subEl) subEl.textContent = money(sub);
    });
    document.querySelectorAll('[data-cart-total]').forEach(function (el) { el.textContent = money(total); });

    document.querySelectorAll('.cart-row-remove').forEach(function (link) {
      link.addEventListener('click', function (event) {
        if (reduced) return;
        event.preventDefault();
        var row = link.closest('.cart-row');
        if (row) row.classList.add('is-removing');
        setTimeout(function () { window.location.href = link.href; }, 320);
      });
    });
  }
})();
