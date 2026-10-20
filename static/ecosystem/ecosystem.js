/* Nexus LATAM Ecosystem — static data explorer */
(function () {
  'use strict';

  const COUNTRY_META = {
    PE: { key: 'Peru', flag: '🇵🇪', empty: false },
    SV: { key: 'El Salvador', flag: '🇸🇻', empty: false },
    CO: { key: 'Colombia', flag: '🇨🇴', empty: false },
    GT: { key: 'Guatemala', flag: '🇬🇹', empty: true },
    CR: { key: 'Costa Rica', flag: '🇨🇷', empty: true },
  };

  const CATEGORY_KEYS = [
    'government', 'accelerator', 'international', 'funder', 'ngo_foundation',
    'academia', 'corporate', 'finance', 'chamber', 'startup', 'media',
  ];

  const SECTOR_MAP = {
    corporate: 'private', startup: 'private', finance: 'private', chamber: 'private', accelerator: 'private',
    government: 'gov',
    ngo_foundation: 'civil', academia: 'civil', media: 'civil',
    international: 'intl',
  };

  const I18N = {
    ES: {
      title: 'Mapa del ecosistema LATAM',
      sub: 'Actores de Perú, El Salvador y Colombia extraídos de mapas Canva REIN/CTH. Guatemala y Costa Rica: mapeo en preparación.',
      actors: 'Actores', relations: 'Relaciones', countries: 'Países',
      map: 'Mapa interactivo', clickCountry: 'Clic en un país para enfocar',
      emptyMap: 'Mapeo en preparación — aún no hay actores georreferenciados para este país.',
      filters: 'Filtros', search: 'Buscar organización…',
      minRel: 'Mín. relaciones', allCountries: 'Todos',
      sectors: { private: 'Privado', gov: 'Gobierno', civil: 'Sociedad Civil y Academia', intl: 'Internacional' },
      cats: {
        government: 'Gobierno', accelerator: 'Aceleradoras', international: 'Internacional',
        funder: 'Fondos', ngo_foundation: 'ONG', academia: 'Academia', corporate: 'Corporativos',
        finance: 'Finanzas', chamber: 'Cámaras', startup: 'Startups', media: 'Medios',
      },
      chartCat: 'Actores por categoría', chartCompare: 'Comparación por país',
      network: 'Red de relaciones', noResults: 'Sin resultados con estos filtros.',
      website: 'Sitio web', websitePending: 'Sitio PENDIENTE',
      linkedin: 'LinkedIn', linkedinPending: 'LinkedIn PENDIENTE',
      nexusCard: 'Ficha Nexus', nexusPending: 'Ficha Nexus pendiente',
      relationsN: 'relaciones',
    },
    EN: {
      title: 'LATAM ecosystem map',
      sub: 'Actors from Peru, El Salvador, and Colombia (Canva actor maps). Guatemala and Costa Rica: mapping in progress.',
      actors: 'Actors', relations: 'Relations', countries: 'Countries',
      map: 'Interactive map', clickCountry: 'Click a country to focus',
      emptyMap: 'Mapping in progress — no georeferenced actors for this country yet.',
      filters: 'Filters', search: 'Search organization…',
      minRel: 'Min. relations', allCountries: 'All',
      sectors: { private: 'Private', gov: 'Government', civil: 'Civil Society & Academia', intl: 'International' },
      cats: {
        government: 'Government', accelerator: 'Accelerators', international: 'International',
        funder: 'Funders', ngo_foundation: 'NGOs', academia: 'Academia', corporate: 'Corporates',
        finance: 'Finance', chamber: 'Chambers', startup: 'Startups', media: 'Media',
      },
      chartCat: 'Actors by category', chartCompare: 'Country comparison',
      network: 'Relations network', noResults: 'No results with these filters.',
      website: 'Website', websitePending: 'Website PENDING',
      linkedin: 'LinkedIn', linkedinPending: 'LinkedIn PENDING',
      nexusCard: 'Nexus profile', nexusPending: 'Nexus profile pending',
      relationsN: 'relations',
    },
  };

  const bootParams = new URLSearchParams(location.search);
  let lang = bootParams.get('lang') || localStorage.getItem('nexusEcoLang') || 'ES';
  if (lang !== 'EN' && lang !== 'ES') lang = 'ES';
  let brand = bootParams.get('brand') || localStorage.getItem('nexusBrand') || 'cth';
  if (brand !== 'rein' && brand !== 'cth') brand = 'cth';
  let actors = [];
  let relations = [];
  let degree = new Map();
  let activeCountry = null;
  let activeCategories = new Set(CATEGORY_KEYS);
  let activeSectors = new Set(['private', 'gov', 'civil', 'intl']);
  let minRelations = 0;
  let searchQuery = '';
  let chartCat = null;
  let chartCompare = null;
  let network = null;

  const $ = (sel) => document.querySelector(sel);
  const t = () => I18N[lang];

  function initBrand() {
    const params = new URLSearchParams(location.search);
    if (params.get('brand') === 'rein') brand = 'rein';
    document.body.dataset.brand = brand === 'rein' ? 'rein' : 'cth';
    document.querySelectorAll('[data-brand-btn]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.brandBtn === brand);
      btn.addEventListener('click', () => {
        brand = btn.dataset.brandBtn;
        localStorage.setItem('nexusBrand', brand);
        document.body.dataset.brand = brand === 'rein' ? 'rein' : 'cth';
        document.querySelectorAll('[data-brand-btn]').forEach((b) => b.classList.toggle('active', b.dataset.brandBtn === brand));
      });
    });
  }

  function initLang() {
    document.querySelectorAll('[data-lang-btn]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.langBtn === lang);
      btn.addEventListener('click', () => setLang(btn.dataset.langBtn));
    });
    applyI18n();
  }

  function setLang(l) {
    lang = l;
    localStorage.setItem('nexusEcoLang', l);
    document.documentElement.lang = l === 'EN' ? 'en' : 'es';
    document.querySelectorAll('[data-lang-btn]').forEach((btn) => btn.classList.toggle('active', btn.dataset.langBtn === lang));
    applyI18n();
    buildFilterChips();
    render();
  }

  function applyI18n() {
    const tr = t();
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const key = el.dataset.i18n;
      if (tr[key]) el.textContent = tr[key];
    });
    $('#search-input').placeholder = tr.search;
    $('#min-rel-label').textContent = tr.minRel;
  }

  function countryCode(name) {
    const entry = Object.entries(COUNTRY_META).find(([, v]) => v.key === name);
    return entry ? entry[0] : null;
  }

  function computeDegrees() {
    degree = new Map();
    actors.forEach((a) => degree.set(a.id, 0));
    relations.forEach((r) => {
      if (degree.has(r.source)) degree.set(r.source, (degree.get(r.source) || 0) + 1);
      if (degree.has(r.target)) degree.set(r.target, (degree.get(r.target) || 0) + 1);
    });
  }

  function filteredActors() {
    const q = searchQuery.trim().toLowerCase();
    return actors.filter((a) => {
      const cc = countryCode(a.country);
      if (activeCountry && cc !== activeCountry) return false;
      if (!activeCategories.has(a.category)) return false;
      const sec = SECTOR_MAP[a.category] || 'private';
      if (!activeSectors.has(sec)) return false;
      if ((degree.get(a.id) || 0) < minRelations) return false;
      if (q) {
        const hay = `${a.name} ${a.city || ''} ${a.country} ${a.notes || ''}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }

  function esc(s) {
    return String(s || '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  function websiteLink(a) {
    const tr = t();
    if (a.website) {
      const href = a.website.startsWith('http') ? a.website : `https://${a.website}`;
      return `<a class="link-btn" href="${esc(href)}" target="_blank" rel="noopener">${tr.website}</a>`;
    }
    return `<span class="link-btn muted">${tr.websitePending}</span>`;
  }

  function linkedinLink(a) {
    const tr = t();
    if (a.type === 'person') {
      if (a.linkedin) {
        return `<a class="li-btn" href="${esc(a.linkedin)}" target="_blank" rel="noopener">${tr.linkedin}</a>`;
      }
      return `<span class="li-btn pending">${tr.linkedinPending}</span>`;
    }
    return '';
  }

  function startupExtras(a) {
    const tr = t();
    if (a.category !== 'startup') return '';
    if (a.has_nexus_card && a.nexus_slug) {
      return `<a class="nexus-btn" href="/s/${esc(a.nexus_slug)}" target="_blank" rel="noopener">${tr.nexusCard}</a>`;
    }
    return `<span class="pending-chip">${tr.nexusPending}</span>`;
  }

  function renderCards(list) {
    const grid = $('#actor-grid');
    const tr = t();
    if (!list.length) {
      grid.innerHTML = `<div class="empty-grid" style="grid-column:1/-1">${tr.noResults}</div>`;
      return;
    }
    grid.innerHTML = list.map((a) => {
      const cc = countryCode(a.country);
      const flag = cc ? COUNTRY_META[cc].flag : '🌎';
      const relN = degree.get(a.id) || 0;
      const catLabel = tr.cats[a.category] || a.category;
      const isStartup = a.category === 'startup';
      return `
        <article class="actor-card${isStartup ? ' startup-card' : ''}" data-id="${esc(a.id)}">
          <div class="ac-top">
            <div class="ac-icon">${esc(a.name.slice(0, 2).toUpperCase())}</div>
            <div>
              <div class="ac-name">${esc(a.name)}</div>
              <div class="ac-meta">${flag} ${esc(a.country)}${a.city ? ` · ${esc(a.city)}` : ''} · ${relN} ${tr.relationsN}</div>
            </div>
          </div>
          <div class="ac-badges">
            <span class="badge${isStartup ? ' cat-startup' : ''}">${esc(catLabel)}</span>
            <span class="badge">${esc(tr.sectors[SECTOR_MAP[a.category] || 'private'])}</span>
          </div>
          ${a.notes ? `<p class="ac-notes">${esc(a.notes)}</p>` : ''}
          <div class="ac-links">
            ${websiteLink(a)}
            ${linkedinLink(a)}
            ${startupExtras(a)}
          </div>
        </article>`;
    }).join('');
  }

  function updateStats(list) {
    $('#stat-actors').textContent = String(list.length);
    $('#stat-relations').textContent = String(relations.length);
    const countries = new Set(list.map((a) => a.country));
    $('#stat-countries').textContent = String(countries.size);
    $('#result-meta').textContent = `${list.length} / ${actors.length}`;
  }

  function renderCharts(list) {
    const tr = t();
    const byCat = {};
    CATEGORY_KEYS.forEach((k) => { byCat[k] = 0; });
    list.forEach((a) => { byCat[a.category] = (byCat[a.category] || 0) + 1; });

    const catLabels = CATEGORY_KEYS.map((k) => tr.cats[k]);
    const catData = CATEGORY_KEYS.map((k) => byCat[k]);

    if (chartCat) chartCat.destroy();
    chartCat = new Chart($('#chart-category'), {
      type: 'bar',
      data: {
        labels: catLabels,
        datasets: [{ label: tr.chartCat, data: catData, backgroundColor: 'rgba(12,73,138,.75)' }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { font: { size: 9 }, maxRotation: 45 } }, y: { beginAtZero: true, ticks: { precision: 0 } } },
      },
    });

    const countryOrder = ['Peru', 'El Salvador', 'Colombia', 'Guatemala', 'Costa Rica'];
    const countryCounts = countryOrder.map((c) => list.filter((a) => a.country === c).length);
    const mappedCounts = countryOrder.map((c) => actors.filter((a) => a.country === c).length);

    if (chartCompare) chartCompare.destroy();
    chartCompare = new Chart($('#chart-compare'), {
      type: 'bar',
      data: {
        labels: countryOrder,
        datasets: [
          { label: lang === 'ES' ? 'Filtrados' : 'Filtered', data: countryCounts, backgroundColor: 'rgba(102,147,72,.85)' },
          { label: lang === 'ES' ? 'Total mapeado' : 'Mapped total', data: mappedCounts, backgroundColor: 'rgba(105,181,250,.55)' },
        ],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
      },
    });
  }

  function renderNetwork(list) {
    const ids = new Set(list.map((a) => a.id));
    const edges = relations.filter((r) => ids.has(r.source) && ids.has(r.target));
    const nodes = list.map((a) => ({
      id: a.id,
      label: a.name.length > 22 ? `${a.name.slice(0, 20)}…` : a.name,
      title: a.name,
      group: a.category,
    }));

    const container = document.getElementById('network-graph');
    if (network) {
      network.setData({ nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges.map((e) => ({ from: e.source, to: e.target, title: e.type || '' }))) });
      return;
    }
    network = new vis.Network(container, {
      nodes: new vis.DataSet(nodes),
      edges: new vis.DataSet(edges.map((e) => ({ from: e.source, to: e.target, arrows: 'to', color: { color: '#94A3B8' } }))),
    }, {
      physics: { stabilization: true, barnesHut: { gravitationalConstant: -8000 } },
      interaction: { hover: true },
    });
  }

  function setCountry(cc) {
    activeCountry = activeCountry === cc ? null : cc;
    document.querySelectorAll('.map-country').forEach((el) => {
      el.classList.toggle('active', el.dataset.cc === activeCountry);
    });
    const meta = activeCountry ? COUNTRY_META[activeCountry] : null;
    const emptyMsg = $('#map-empty-msg');
    if (meta && meta.empty) {
      emptyMsg.textContent = t().emptyMap;
      emptyMsg.classList.add('visible');
    } else {
      emptyMsg.classList.remove('visible');
    }
    render();
  }

  function bindMap() {
    document.querySelectorAll('.map-country').forEach((el) => {
      el.addEventListener('click', () => setCountry(el.dataset.cc));
    });
  }

  function mountLeafletMap() {
    if (!window.NexusLatamMap) return;
    window.NexusLatamMap.mountEcosystemMap('eco-leaflet-map', filteredActors(), (countryName) => {
      const cc = countryCode(countryName);
      if (cc) setCountry(cc);
    });
  }

  function buildFilterChips() {
    const tr = t();
    const catRow = $('#cat-chips');
    catRow.innerHTML = CATEGORY_KEYS.map((k) =>
      `<button type="button" class="chip cat ${activeCategories.has(k) ? 'on' : ''}" data-cat="${k}">${esc(tr.cats[k])}</button>`
    ).join('');
    catRow.querySelectorAll('.chip').forEach((btn) => {
      btn.addEventListener('click', () => {
        const k = btn.dataset.cat;
        if (activeCategories.has(k)) activeCategories.delete(k); else activeCategories.add(k);
        btn.classList.toggle('on');
        render();
      });
    });

    const secRow = $('#sector-chips');
    secRow.innerHTML = Object.keys(tr.sectors).map((k) =>
      `<button type="button" class="chip sector ${activeSectors.has(k) ? 'on' : ''}" data-sector="${k}">${esc(tr.sectors[k])}</button>`
    ).join('');
    secRow.querySelectorAll('.chip').forEach((btn) => {
      btn.addEventListener('click', () => {
        const k = btn.dataset.sector;
        if (activeSectors.has(k)) activeSectors.delete(k); else activeSectors.add(k);
        btn.classList.toggle('on');
        render();
      });
    });
  }

  function render() {
    const list = filteredActors();
    updateStats(list);
    renderCards(list);
    renderCharts(list);
    renderNetwork(list);
    if (window.NexusLatamMap) {
      window.NexusLatamMap.renderEcosystemMarkers('eco-leaflet-map', list);
    }
  }

  function initAuthGate() {
    const host = location.hostname;
    const isLocal = host === 'localhost' || host === '127.0.0.1' || location.search.includes('preview=1');
    if (isLocal) return;
    fetch('/nexus-auth/api/me', { credentials: 'include' })
      .then((r) => {
        if (r.ok) return;
        const next = encodeURIComponent(location.pathname + location.search);
        location.href = `/nexus-auth/?next=${next}`;
      })
      .catch(() => {});
  }

  async function loadData() {
    const [a, r] = await Promise.all([
      fetch('data/actors.json').then((res) => res.json()),
      fetch('data/relations.json').then((res) => res.json()),
    ]);
    actors = a;
    relations = r;
    computeDegrees();
    buildFilterChips();
    bindMap();
    mountLeafletMap();
    $('#search-input').addEventListener('input', (e) => { searchQuery = e.target.value; render(); });
    $('#min-rel').addEventListener('input', (e) => {
      minRelations = Number(e.target.value) || 0;
      $('#min-rel-val').textContent = String(minRelations);
      render();
    });
    $('#clear-country').addEventListener('click', () => { activeCountry = null; document.querySelectorAll('.map-country').forEach((el) => el.classList.remove('active')); $('#map-empty-msg').classList.remove('visible'); render(); });
    render();
  }

  initBrand();
  initLang();
  initAuthGate();
  loadData().catch((err) => {
    console.error(err);
    $('#actor-grid').innerHTML = `<div class="empty-grid">Error loading data: ${esc(err.message)}</div>`;
  });
})();
