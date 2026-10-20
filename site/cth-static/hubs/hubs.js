(function () {
  const FLAGS = { CO: '🇨🇴', GT: '🇬🇹', PE: '🇵🇪', CR: '🇨🇷', SV: '🇸🇻' };
  const HUBMAP_TITLE = { ES: 'HubMap', EN: 'HubMap' };
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
    return '<div id="hub-leaflet-map" class="hub-leaflet-map" role="application" aria-label="HubMap"></div>';
  }

  function liBtn(linkedin) {
    return `<a class="li-btn hub-li-btn" href="${linkedin}" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 114.126 0 2.063 2.063 0 01-2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>LinkedIn</a>`;
  }

  function avatarClass(initials) {
    const n = (initials || '?').charCodeAt(0) || 0;
    return `av-${n % 10}`;
  }

  function renderPeople(hub) {
    const people = hub.people || [];
    if (!people.length) {
      if (hub.peoplePending) {
        return `<div class="hub-people-pending">${lang === 'ES' ? 'Equipo del hub: PENDIENTE (confirmar representantes locales).' : 'Hub team: PENDING (local leads to be confirmed).'}</div>`;
      }
      return '';
    }
    const cards = people.map((p, idx) => {
      const role = t(p.role);
      const org = t(p.org);
      const pendingPhoto = p.photoPending || !p.photo;
      const avInner = pendingPhoto
        ? `<span class="hub-people-pending-tag">${lang === 'ES' ? 'PENDIENTE' : 'PENDING'}</span>${p.initials || '?'}`
        : `<img src="${p.photo}" alt="" loading="lazy"/>`;
      return `<article class="mentor-card hub-people-card">
        <div class="card-top">
          <div class="avatar ${avatarClass(p.initials)}" data-idx="${idx}">${avInner}</div>
          <div class="card-info">
            <div class="card-name">${p.name}</div>
            <div class="card-role" title="${role}">${role}</div>
          </div>
        </div>
        <div class="card-body"><div class="card-desc">${org}</div></div>
        <div class="card-footer">${liBtn(p.linkedin)}</div>
      </article>`;
    }).join('');
    return `<div class="hub-people-section"><h3 class="hub-people-head">${lang === 'ES' ? 'Equipo del hub' : 'Hub team'}</h3><div class="hub-people-grid">${cards}</div></div>`;
  }

  function renderOrgBar(hub) {
    const site = hub.website;
    if (!site) return '';
    const label = lang === 'ES' ? 'Sitio web de la organización' : 'Organisation website';
    return `<div class="hub-org-bar"><span class="hub-org-label">${label}</span><a href="${site}" target="_blank" rel="noopener">${site.replace(/^https?:\/\//, '')} ↗</a></div>`;
  }

  function renderEcosystemMap(hub) {
    const m = hub.ecosystemMap;
    if (!m) return '';
    const label = t(m.label);
    if (m.pending || !m.href) {
      return `<div class="hub-eco-map pending"><strong>${label}</strong><span>${t(m.note) || (lang === 'ES' ? 'Enlace público PENDIENTE.' : 'Public link PENDING.')}</span></div>`;
    }
    const note = t(m.note);
    return `<div class="hub-eco-map"><a href="${m.href}" target="_blank" rel="noopener">${label} ↗</a>${note ? `<span class="hub-eco-map-note">${note}</span>` : ''}</div>`;
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
    const links = (hub.links || []).filter((l) => l.href !== hub.website).map((l) => `<a href="${l.href}" target="_blank" rel="noopener">${t(l.label)} ↗</a>`).join('');
    const more = compact ? `<div class="hub-actions"><a href="${detailHref}">${lang === 'ES' ? 'Abrir hub →' : 'Open hub →'}</a></div>` : `<div class="hub-actions">${links}<a class="secondary" href="/hubs/">${lang === 'ES' ? 'HubMap' : 'HubMap'}</a></div>`;

    return `<section class="hub-scroll-section" id="${hub.id}" data-hub-section="${hub.id}">
      <div class="hub-card-head"><div><h2>${t(hub.name)}</h2><div class="hub-meta">${t(hub.short)} · ${FLAGS[hub.country] || ''}</div></div></div>
      ${renderOrgBar(hub)}
      <p class="hub-tagline">${t(hub.tagline)}</p>
      <p class="hub-about">${t(hub.about)}</p>
      ${compact ? '' : renderPeople(hub)}
      ${compact ? '' : renderEcosystemMap(hub)}
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
        <div class="hub-hero-eyebrow">CleantechHUB Nexus · REIN</div>
        <h1 class="hub-hero-title">${HUBMAP_TITLE[lang]}</h1>
        <p class="hub-hero-sub">${lang === 'ES' ? 'Mapa Leaflet de hubs REIN, perfiles por país, equipos, media verificada y startups ClimateLaunchpad.' : 'Leaflet map of REIN hubs, country profiles, teams, verified media, and ClimateLaunchpad startups.'}</p>
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
    document.title = `${t(hub.name)} — HubMap · Nexus`;
  }

  function applyHubMapMeta() {
    const title = `${HUBMAP_TITLE[lang]} — CleantechHUB Nexus`;
    if (pageMode === 'landing') document.title = title;
    const meta = document.querySelector('meta[name="description"]');
    if (meta && pageMode === 'landing') {
      meta.content = lang === 'ES'
        ? 'HubMap — explorador de hubs REIN con mapa OpenStreetMap, equipos y startups ClimateLaunchpad.'
        : 'HubMap — REIN hub explorer with OpenStreetMap, teams, and ClimateLaunchpad startups.';
    }
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
    applyHubMapMeta();
    if (pageMode === 'detail') renderDetail(data, hubId);
    else renderLanding(data);
    document.querySelectorAll('[data-i18n-hubs-title]').forEach((el) => {
      el.textContent = lang === 'ES' ? el.dataset.i18nHubsTitleEs : el.dataset.i18nHubsTitleEn;
    });
  }

  initBrandLangToolbar();

  fetch('/hubs/hubs-data.json?v=20261020-hubmap-c')
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
