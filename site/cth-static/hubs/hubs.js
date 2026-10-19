(function () {
  const FLAGS = { CO: '🇨🇴', GT: '🇬🇹', PE: '🇵🇪', CR: '🇨🇷', MX: '🇲🇽' };
  const THEME = { CE: 'Circular', BIO: 'Bio', EN: 'Energy' };

  let lang = (localStorage.getItem('nexusEcoLang') || 'ES').toUpperCase();
  if (lang !== 'EN' && lang !== 'ES') lang = 'ES';

  let brand = (new URLSearchParams(location.search).get('brand') || localStorage.getItem('nexusBrand') || 'cth').toLowerCase();
  if (brand !== 'rein') brand = 'cth';

  const pageMode = document.body.dataset.hubPage || 'landing';
  const hubId = document.body.dataset.hubId || '';

  function t(obj) {
    if (!obj) return '';
    return obj[lang] || obj.ES || obj.EN || '';
  }

  function initBrandLangToolbar() {
    document.body.dataset.brand = brand === 'rein' ? 'rein' : 'cth';
    document.documentElement.lang = lang === 'EN' ? 'en' : 'es';
    document.querySelectorAll('[data-brand-btn]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.brandBtn === brand);
      btn.addEventListener('click', () => {
        brand = btn.dataset.brandBtn;
        localStorage.setItem('nexusBrand', brand);
        document.body.dataset.brand = brand === 'rein' ? 'rein' : 'cth';
        document.querySelectorAll('[data-brand-btn]').forEach((b) => b.classList.toggle('active', b.dataset.brandBtn === brand));
        document.querySelectorAll('[data-nav-brand-btn]').forEach((b) => b.classList.toggle('active', b.dataset.navBrandBtn === brand));
        document.dispatchEvent(new CustomEvent('nexus-brand-change', { detail: { brand } }));
      });
    });
    document.querySelectorAll('[data-lang-btn]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.langBtn === lang);
      btn.addEventListener('click', () => setLang(btn.dataset.langBtn));
    });
  }

  function setLang(l) {
    lang = l === 'EN' ? 'EN' : 'ES';
    localStorage.setItem('nexusEcoLang', lang);
    document.documentElement.lang = lang === 'EN' ? 'en' : 'es';
    document.querySelectorAll('[data-lang-btn]').forEach((btn) => btn.classList.toggle('active', btn.dataset.langBtn === lang));
    document.querySelectorAll('.lang-btn').forEach((btn) => btn.classList.toggle('active', btn.textContent.trim() === lang));
    if (window.__HUBS_DATA) renderAll(window.__HUBS_DATA);
  }

  window.__hubsSetLang = setLang;

  fetch('/hubs/hubs-data.json?v=20261019-hubs')
    .then((r) => r.json())
    .then(renderAll)
    .catch((err) => {
      const root = document.getElementById('hubs-root');
      if (root) root.innerHTML = `<p class="soon-banner">Failed to load hub data: ${err.message}</p>`;
    });

  initBrandLangToolbar();
})();
