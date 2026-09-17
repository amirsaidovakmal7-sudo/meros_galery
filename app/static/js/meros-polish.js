(function () {
  'use strict';

  document.querySelectorAll('.nav-logo, .footer-brand').forEach(function (logo) {
    logo.textContent = 'merós';
    logo.setAttribute('aria-label', 'Meros Gallery');
  });

  var menu = document.querySelector('.nav-overlay');
  var menuLinks = menu && menu.querySelector('.nav-overlay-links');
  var mainHero = document.querySelector('main > .hero:first-child');
  if (!mainHero) document.body.classList.add('page--light-nav');
  if (menu && menuLinks) {
    if (!menuLinks.querySelector('[href="/collaborations"]')) {
      var collaborations = document.createElement('a');
      collaborations.href = '/collaborations';
      collaborations.innerHTML = '<span class="nav-overlay-index">05</span>Коллаборации';
      var news = menuLinks.querySelector('[href="/news"]');
      menuLinks.insertBefore(collaborations, news || null);
    }

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

  document.querySelectorAll('.footer-col').forEach(function (column) {
    var heading = column.querySelector('h4');
    if (!heading || heading.textContent.trim() !== 'Навигация') return;
    column.innerHTML = '<h4>Навигация</h4>' +
      '<a href="/">Главная</a><a href="/about">О нас</a><a href="/events">Ивенты</a>' +
      '<a href="/shop">Магазин</a><a href="/collaborations">Коллаборации</a><a href="/news">Новости</a>';
  });

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
