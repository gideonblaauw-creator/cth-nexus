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

  function mapShell() {
    return '<div id="hub-leaflet-map" class="hub-leaflet-map" role="application" aria-label="LATAM hub map"></div>';
  }

  function renderVideos(videos) {
    if (!videos || !videos.length) return '';
    return `<div class="hub-videos">${videos.map((v) => {
      const title = t(v.title);
      const cap = t(v.caption);
      if (v.pending || !v.youtubeId) {
        return `<div class="video-block"><h3>${title}</h3><p class="video-caption">${cap}</p><div class="video-facade pending"><div class="video-pending-label">${lang === 'ES' ? 'Video pendiente' : 'Video pending'}</div></div></div>`;
      }
      const thumb = `https://i.ytimg.com/vi/${v.youtubeId}/hqdefault.jpg`;
      return `<div class="video-block"><h3>${title}</h3><p class="video-caption">${cap}</p>
        <div class="video-facade" data-youtube-id="${v.youtubeId}" data-title="${title.replace(/"/g, '&quot;')}">
          <img src="${thumb}" alt="" loading="lazy"/>
          <button type="button" class="video-play" aria-label="Play"><span>▶</span></button>
        </div></div>`;
    }).join('')}</div>`;
  }

  function bindVideoFacades(root) {
    root.querySelectorAll('.video-facade[data-youtube-id]').forEach((facade) => {
      const play = () => {
        const id = facade.dataset.youtubeId;
        const title = facade.dataset.title || 'YouTube video';
        facade.outerHTML = `<div class="video-iframe-wrap"><iframe src="https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0" title="${title}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>`;
      };
      facade.addEventListener('click', play);
      facade.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); play(); } });
    });
  }

  function startupCard(s) {
    const href = s.onepager ? `/s/${s.onepager}` : (s.slug ? `/s/${s.slug}` : '#');
    const desc = (lang === 'ES' ? s.desc_es : s.desc_en) || (lang === 'ES' ? s.desc_en : s.desc_es) || '';
    const theme = THEME[s.theme] || s.theme || 'CLP';
    return `<a class="hub-startup-card" href="${href}">
      <div class="name">${s.name}</div>
      <div class="desc">${desc || (lang === 'ES' ? 'Startup ClimateLaunchpad — perfil en Nexus.' : 'ClimateLaunchpad startup — Nexus profile.')}</div>
      <div class="meta"><span class="badge">${theme}</span><span class="badge">${s.stage || 'CLP26'}</span></div>
      <div class="go">${lang === 'ES' ? 'Ver one-pager →' : 'View one-pager →'}</div>
    </a>`;
  }

  function chartCanvasId(hub, suffix) {
    return `chart-${hub.id}-${suffix}`;
  }

  function renderInteractive(hub, root) {
    if (!hub.interactive || !hub.startups || !hub.startups.length) return;
    const id = chartCanvasId(hub, 'main');
    const panel = root.querySelector(`[data-interactive="${hub.id}"]`);
    if (!panel) return;
    panel.innerHTML = `<div class="hub-panel"><div class="hub-panel-h">${t(hub.interactive.title)}</div><div class="hub-chart-wrap"><canvas id="${id}"></canvas></div></div>`;
    const canvas = document.getElementById(id);
    if (!canvas || typeof Chart === 'undefined') return;
    const type = hub.interactive.type;
    let labels = [];
    let values = [];
    if (type === 'stage-chart') {
      const counts = {};
      hub.startups.forEach((s) => { const k = s.stage || 'Unknown'; counts[k] = (counts[k] || 0) + 1; });
      labels = Object.keys(counts);
      values = Object.values(counts);
    } else {
      const counts = {};
      hub.startups.forEach((s) => { const k = s.theme || 'CE'; counts[k] = (counts[k] || 0) + 1; });
      labels = Object.keys(counts);
      values = Object.values(counts);
    }
    new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{ data: values, backgroundColor: ['#0C498A', '#669348', '#69B5FA', '#9DC384', '#475569'] }],
      },
      options: { plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } } }, maintainAspectRatio: false },
    });
  }

  function renderHubSection(hub, { compact }) {
    if (hub.status === 'soon') {
      return `<section class="hub-scroll-section" id="${hub.id}" data-hub-section="${hub.id}">
        <div class="hub-card-head"><div><h2>${t(hub.name)}</h2><div class="hub-meta">${t(hub.short)}</div></div></div>
        <div class="soon-banner">${t(hub.tagline)}</div>
      </section>`;
    }
    const kpis = (hub.kpis || []).map((k) => `<div class="hub-kpi"><div class="hub-kpi-n">${k.value}</div><div class="hub-kpi-l">${t(k.label)}</div></div>`).join('');
    const focus = (hub.focusAreas && hub.focusAreas[lang] || []).map((f) => `<span>${f}</span>`).join('');
    const gallery = (hub.images || []).map((im) => `<figure><img src="${im.src}" alt="" loading="lazy"/><figcaption>${t(im.caption)}</figcaption></figure>`).join('');
    const startups = (hub.startups || []).map(startupCard).join('');
    const detailHref = `/hubs/${hub.slug}/`;
    const links = (hub.links || []).map((l) => `<a href="${l.href}" target="_blank" rel="noopener">${t(l.label)} ↗</a>`).join('');
    const more = compact ? `<div class="hub-actions"><a href="${detailHref}">${lang === 'ES' ? 'Abrir hub →' : 'Open hub →'}</a></div>` : links ? `<div class="hub-actions">${links}<a class="secondary" href="/hubs/">${lang === 'ES' ? 'Mapa REIN' : 'REIN map'}</a></div>` : '';

    return `<section class="hub-scroll-section" id="${hub.id}" data-hub-section="${hub.id}">
      <div class="hub-card-head"><div><h2>${t(hub.name)}</h2><div class="hub-meta">${t(hub.short)} · ${FLAGS[hub.country] || ''}</div></div></div>
      <p class="hub-tagline">${t(hub.tagline)}</p>
      <p class="hub-about">${t(hub.about)}</p>
      <div class="hub-kpi-row">${kpis}</div>
      <div class="hub-focus-list">${focus}</div>
      <div class="hub-media-grid">
        <div class="hub-gallery">${gallery}</div>
        <div data-interactive="${hub.id}"></div>
      </div>
      ${renderVideos(hub.videos)}
      <div class="hub-startups-head"><h3>${t(hub.startupsLabel)}</h3><span>${hub.startups.length} CLP26</span></div>
      <div class="hub-startup-grid">${startups}</div>
      ${more}
    </section>`;
  }

  function renderLanding(data) {
    const root = document.getElementById('hubs-root');
    if (!root) return;
    const hubs = data.hubs;
    const rail = hubs.map((h) => {
      const soon = h.status === 'soon';
      const href = soon ? `#${h.id}` : `/hubs/${h.slug}/`;
      return `<a href="${href}" class="${soon ? 'soon' : ''}" data-rail="${h.id}">${t(h.name)}${soon ? ' · próx.' : ''}</a>`;
    }).join('');

    root.innerHTML = `
      <div class="hub-hero">
        <div class="hub-hero-eyebrow">REIN Hubs · Nexus</div>
        <h1 class="hub-hero-title">${lang === 'ES' ? 'Mapa de hubs climáticos LATAM' : 'LATAM climate hub map'}</h1>
        <p class="hub-hero-sub">${lang === 'ES' ? 'Direction C — mapa primero, rail de hubs y scroll editorial con KPIs, media e startups ClimateLaunchpad por país.' : 'Direction C — map-first hub rail and editorial scroll with KPIs, media, and ClimateLaunchpad startups by country.'}</p>
        <div class="hub-map-wrap">${mapShell()}</div>
      </div>
      <nav class="hub-rail" aria-label="Hubs">${rail}</nav>
      ${hubs.map((h) => renderHubSection(h, { compact: true })).join('')}
    `;

    bindMapAndRail(root, hubs);
    if (window.NexusLatamMap) {
      window.NexusLatamMap.mountHubMap('hub-leaflet-map', hubs, (hub) => {
        if (!hub) return;
        if (hub.status === 'soon') {
          document.getElementById(hub.id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          return;
        }
        location.href = `/hubs/${hub.slug}/`;
      });
    }
    hubs.filter((h) => h.status !== 'soon').forEach((h) => renderInteractive(h, root));
    bindVideoFacades(root);
  }

  function renderDetail(data, id) {
    const root = document.getElementById('hubs-root');
    const hub = data.hubs.find((h) => h.id === id || h.slug === id);
    if (!root || !hub) return;
    root.innerHTML = renderHubSection(hub, { compact: false });
    renderInteractive(hub, root);
    bindVideoFacades(root);
    document.title = `${t(hub.name)} — REIN Hubs · Nexus`;
  }

  function bindMapAndRail(root, hubs) {
    const activate = (id) => {
      root.querySelectorAll('.hub-rail a[data-rail]').forEach((a) => a.classList.toggle('active', a.dataset.rail === id));
      if (window.NexusLatamMap) window.NexusLatamMap.setActiveHubMarker('hub-leaflet-map', id);
    };
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) activate(en.target.dataset.hubSection);
      });
    }, { rootMargin: '-40% 0px -45% 0px', threshold: 0.01 });
    root.querySelectorAll('[data-hub-section]').forEach((sec) => obs.observe(sec));
  }

  function renderAll(data) {
    window.__HUBS_DATA = data;
    if (pageMode === 'detail') renderDetail(data, hubId);
    else renderLanding(data);
    document.querySelectorAll('[data-i18n-hubs-title]').forEach((el) => {
      el.textContent = lang === 'ES' ? el.dataset.i18nHubsTitleEs : el.dataset.i18nHubsTitleEn;
    });
  }

  initBrandLangToolbar();

  fetch('/hubs/hubs-data.json?v=20261019-hubs')
    .then((r) => r.json())
    .then(renderAll)
    .catch((err) => {
      const root = document.getElementById('hubs-root');
      if (root) root.innerHTML = `<p class="soon-banner">Failed to load hub data: ${err.message}</p>`;
    });

  document.addEventListener('nexus-lang-change', (e) => {
    if (e.detail && e.detail.lang) setLang(e.detail.lang);
  });
  document.addEventListener('nexus-brand-change', (e) => {
    if (!e.detail || !e.detail.brand) return;
    brand = e.detail.brand === 'rein' ? 'rein' : 'cth';
    document.body.dataset.brand = brand === 'rein' ? 'rein' : 'cth';
    document.querySelectorAll('[data-brand-btn]').forEach((b) => b.classList.toggle('active', b.dataset.brandBtn === brand));
  });
})();
