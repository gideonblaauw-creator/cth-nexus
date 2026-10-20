/* Nexus LATAM Ecosystem — Direction 3: MapLibre + sigma.js 4 */
import Graph from 'graphology';
import Sigma from 'sigma';
import forceAtlas2 from 'graphology-layout-forceatlas2';

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const COUNTRY_META = {
  PE: { key: 'Peru', flag: '🇵🇪' },
  SV: { key: 'El Salvador', flag: '🇸🇻' },
  CO: { key: 'Colombia', flag: '🇨🇴' },
  GT: { key: 'Guatemala', flag: '🇬🇹' },
  CR: { key: 'Costa Rica', flag: '🇨🇷' },
};

const CATEGORY_KEYS = [
  'government', 'accelerator', 'international', 'funder', 'ngo_foundation',
  'academia', 'corporate', 'finance', 'chamber', 'startup', 'media', 'hub', 'mentor', 'program',
];

const CAT_COLOR = {
  startup: '#e87722',
  accelerator: '#669348',
  funder: '#0c498a',
  government: '#6b4c9a',
  academia: '#2a9d8f',
  corporate: '#457b9d',
  international: '#f4a261',
  finance: '#264653',
  ngo_foundation: '#e76f51',
  chamber: '#8d99ae',
  media: '#bc6c25',
  hub: '#669348',
  mentor: '#457b9d',
  program: '#6b4c9a',
  default: '#5a7088',
};

const EDGE_COLOR = {
  works_on_challenge: '#2a9d8f',
  hosts: '#669348',
  runs_program: '#6b4c9a',
  cofunds: '#264653',
  funds_layer: '#0c498a',
  regulates_layer: '#6b4c9a',
  partner: '#e87722',
  incubated: '#e87722',
  accelerated: '#e87722',
  part_of_group: '#457b9d',
  participates: '#8d99ae',
  owns: '#264653',
  created: '#5a7088',
  runs_initiative: '#6b4c9a',
  part_of_network: '#457b9d',
  oversees: '#6b4c9a',
  default: '#94a3b8',
};

const I18N = {
  ES: {
    title: 'Mapa del ecosistema LATAM',
    sub: 'Mapa geográfico y red de relaciones vinculados — Perú, El Salvador y Colombia.',
    actors: 'Actores',
    relations: 'Relaciones',
    visible: 'Visibles',
    tabExplore: 'Explorar mapa + red',
    tabCards: 'Fichas de actores',
    tabStory: 'Historia guiada',
    map: 'Mapa LATAM',
    network: 'Red de relaciones',
    filters: 'Tipo actor',
    country: 'País',
    edgeTypes: 'Tipo relación',
    allCountries: 'Todos',
    search: 'Buscar organización…',
    ego: 'Ego',
    inspectorEmpty: 'Selecciona un actor en el mapa o la red.',
    website: 'Sitio web',
    websitePending: 'Sitio PENDIENTE',
    linkedin: 'LinkedIn',
    linkedinPending: 'LinkedIn PENDIENTE',
    nexusCard: 'Ficha Nexus /s/',
    nexusPending: 'Ficha Nexus pendiente',
    relationsN: 'relaciones',
    typedRelations: 'Relaciones tipadas',
    noResults: 'Sin resultados con estos filtros.',
    noRelations: 'Sin relaciones en datos.',
    cats: {
      government: 'Gobierno', accelerator: 'Aceleradora', international: 'Internacional',
      funder: 'Fondo', ngo_foundation: 'ONG', academia: 'Academia', corporate: 'Corporativo',
      finance: 'Finanzas', chamber: 'Cámara', startup: 'Startup', media: 'Medios',
      hub: 'Hub', mentor: 'Mentor', program: 'Programa',
    },
  },
  EN: {
    title: 'LATAM ecosystem map',
    sub: 'Linked geographic map and relationship network — Peru, El Salvador, Colombia.',
    actors: 'Actors',
    relations: 'Relations',
    visible: 'Visible',
    tabExplore: 'Explore map + network',
    tabCards: 'Actor cards',
    tabStory: 'Guided story',
    map: 'LATAM map',
    network: 'Relationship network',
    filters: 'Actor type',
    country: 'Country',
    edgeTypes: 'Relation type',
    allCountries: 'All',
    search: 'Search organization…',
    ego: 'Ego',
    inspectorEmpty: 'Select an actor on the map or network.',
    website: 'Website',
    websitePending: 'Website PENDING',
    linkedin: 'LinkedIn',
    linkedinPending: 'LinkedIn PENDING',
    nexusCard: 'Nexus profile /s/',
    nexusPending: 'Nexus profile pending',
    relationsN: 'relations',
    typedRelations: 'Typed relations',
    noResults: 'No results with these filters.',
    noRelations: 'No relations in data.',
    cats: {
      government: 'Government', accelerator: 'Accelerator', international: 'International',
      funder: 'Funder', ngo_foundation: 'NGO', academia: 'Academia', corporate: 'Corporate',
      finance: 'Finance', chamber: 'Chamber', startup: 'Startup', media: 'Media',
      hub: 'Hub', mentor: 'Mentor', program: 'Program',
    },
  },
};

const bootParams = new URLSearchParams(location.search);
let lang = bootParams.get('lang') || localStorage.getItem('nexusEcoLang') || 'ES';
if (lang !== 'EN' && lang !== 'ES') lang = 'ES';
let brand = bootParams.get('brand') || localStorage.getItem('nexusBrand') || 'cth';

let actors = [];
let relations = [];
let byId = new Map();
let degree = new Map();
let activeCountry = null;
let activeCategories = new Set(CATEGORY_KEYS);
let activeRelTypes = new Set();
let searchQuery = '';
let selected = null;
let egoOn = false;
let egoDepth = 2;

let map = null;
let mapReady = false;
let graph = null;
let sigma = null;
let layoutPositions = new Map();

const $ = (sel) => document.querySelector(sel);
const t = () => I18N[lang];

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
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

function egoNodeSet(centerId, depth) {
  const keep = new Set([centerId]);
  for (let d = 0; d < depth; d += 1) {
    relations.forEach((r) => {
      if (keep.has(r.source)) keep.add(r.target);
      if (keep.has(r.target)) keep.add(r.source);
    });
  }
  return keep;
}

function filteredActors() {
  const q = searchQuery.trim().toLowerCase();
  return actors.filter((a) => {
    const cc = countryCode(a.country);
    if (activeCountry && cc !== activeCountry) return false;
    if (!activeCategories.has(a.category)) return false;
    if (q && !a.name.toLowerCase().includes(q)) return false;
    return true;
  });
}

function visibleActorIds() {
  let ids = new Set(filteredActors().map((a) => a.id));
  if (egoOn && selected) {
    const ego = egoNodeSet(selected, egoDepth);
    ids = new Set([...ids].filter((id) => ego.has(id)));
  }
  return ids;
}

function visibleRelations(ids) {
  return relations.filter((r) => {
    if (!activeRelTypes.has(r.type)) return false;
    return ids.has(r.source) && ids.has(r.target);
  });
}

function initBrand() {
  document.body.dataset.brand = brand === 'rein' ? 'rein' : 'cth';
  document.querySelectorAll('[data-brand-btn]').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.brandBtn === brand);
    btn.addEventListener('click', () => {
      brand = btn.dataset.brandBtn;
      localStorage.setItem('nexusBrand', brand);
      document.body.dataset.brand = brand === 'rein' ? 'rein' : 'cth';
      document.querySelectorAll('[data-brand-btn]').forEach((b) => b.classList.toggle('active', b.dataset.brandBtn === brand));
      refreshGraphStyles();
    });
  });
}

function applyI18n() {
  const tr = t();
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.dataset.i18n;
    if (tr[key]) el.textContent = tr[key];
  });
  $('#search-input').placeholder = tr.search;
}

function initLang() {
  document.documentElement.lang = lang === 'EN' ? 'en' : 'es';
  document.querySelectorAll('[data-lang-btn]').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.langBtn === lang);
    btn.addEventListener('click', () => {
      lang = btn.dataset.langBtn;
      localStorage.setItem('nexusEcoLang', lang);
      document.documentElement.lang = lang === 'EN' ? 'en' : 'es';
      document.querySelectorAll('[data-lang-btn]').forEach((b) => b.classList.toggle('active', b.dataset.langBtn === lang));
      applyI18n();
      buildFilterChips();
      renderAll();
    });
  });
  applyI18n();
}

function buildFilterChips() {
  const tr = t();
  const countries = [
    ['ALL', tr.allCountries],
    ['PE', '🇵🇪 PE'],
    ['SV', '🇸🇻 SV'],
    ['CO', '🇨🇴 CO'],
  ];
  const cRow = $('#country-chips');
  cRow.innerHTML = countries.map(([cc, label]) =>
    `<button type="button" class="chip ${(!activeCountry && cc === 'ALL') || activeCountry === cc ? 'on' : ''}" data-cc="${cc}">${esc(label)}</button>`,
  ).join('');
  cRow.querySelectorAll('.chip').forEach((btn) => {
    btn.addEventListener('click', () => {
      activeCountry = btn.dataset.cc === 'ALL' ? null : btn.dataset.cc;
      buildFilterChips();
      renderAll();
    });
  });

  const catRow = $('#cat-chips');
  const cats = [...new Set(actors.map((a) => a.category))].sort();
  catRow.innerHTML = cats.map((k) =>
    `<button type="button" class="chip ${activeCategories.has(k) ? 'on' : 'off'}" data-cat="${esc(k)}">${esc(tr.cats[k] || k)}</button>`,
  ).join('');
  catRow.querySelectorAll('.chip').forEach((btn) => {
    btn.addEventListener('click', () => {
      const k = btn.dataset.cat;
      if (activeCategories.has(k)) activeCategories.delete(k); else activeCategories.add(k);
      btn.classList.toggle('on', activeCategories.has(k));
      btn.classList.toggle('off', !activeCategories.has(k));
      renderAll();
    });
  });

  const relTypes = [...new Set(relations.map((r) => r.type))].sort();
  if (!activeRelTypes.size) activeRelTypes = new Set(relTypes);
  const rRow = $('#rel-chips');
  rRow.innerHTML = relTypes.map((rt) =>
    `<button type="button" class="chip ${activeRelTypes.has(rt) ? 'on' : 'off'}" data-rel="${esc(rt)}">${esc(rt.replace(/_/g, '-'))}</button>`,
  ).join('');
  rRow.querySelectorAll('.chip').forEach((btn) => {
    btn.addEventListener('click', () => {
      const rt = btn.dataset.rel;
      if (activeRelTypes.has(rt)) activeRelTypes.delete(rt); else activeRelTypes.add(rt);
      btn.classList.toggle('on', activeRelTypes.has(rt));
      btn.classList.toggle('off', !activeRelTypes.has(rt));
      renderAll();
    });
  });

  const legend = $('#legend-bar');
  legend.innerHTML = relTypes.map((rt) =>
    `<span><i style="background:${EDGE_COLOR[rt] || EDGE_COLOR.default}"></i>${esc(rt.replace(/_/g, '-'))}</span>`,
  ).join('');
}

function initTabs() {
  document.querySelectorAll('.view-tab:not([disabled])').forEach((btn) => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.viewTab;
      document.querySelectorAll('.view-tab').forEach((b) => b.classList.toggle('active', b === btn));
      $('#panel-explore').classList.toggle('hidden', tab !== 'explore');
      $('#panel-cards').classList.toggle('hidden', tab !== 'cards');
      $('#filter-bar').classList.toggle('hidden', tab !== 'explore');
      $('#legend-bar').classList.toggle('hidden', tab !== 'explore');
      if (tab === 'cards') renderCards(filteredActors());
      if (tab === 'explore' && sigma) sigma.refresh();
    });
  });
}

function geoXY(a) {
  const g = a.geo || { lat: 0, lng: 0 };
  return { x: (g.lng + 85) * 10, y: (-g.lat - 18) * 10 };
}

function buildGraph(ids, rels) {
  if (sigma) {
    sigma.kill();
    sigma = null;
  }
  graph = new Graph({ multi: false, type: 'directed' });

  ids.forEach((id) => {
    const a = byId.get(id);
    if (!a) return;
    const pos = layoutPositions.get(id) || geoXY(a);
    const size = id === selected ? 14 : Math.min(12, 5 + (degree.get(id) || 0) * 0.65);
    graph.addNode(id, {
      label: a.name.length > 24 ? `${a.name.slice(0, 22)}…` : a.name,
      x: pos.x,
      y: pos.y,
      size,
      color: nodeColor(id),
    });
  });

  rels.forEach((r, i) => {
    if (!graph.hasNode(r.source) || !graph.hasNode(r.target)) return;
    const key = r.id || `e-${i}-${r.source}-${r.target}`;
    if (graph.hasEdge(r.source, r.target)) return;
    try {
      graph.addEdgeWithKey(key, r.source, r.target, {
        type: r.type,
        color: edgeColor(r),
        size: selected && (r.source === selected || r.target === selected) ? 2.2 : 1,
      });
    } catch {
      /* parallel edge */
    }
  });

  if (!reducedMotion && graph.order > 0) {
    const fa2 = forceAtlas2.default || forceAtlas2;
    fa2.assign(graph, {
      iterations: Math.min(120, 40 + graph.order),
      settings: { gravity: 0.8, scalingRatio: 8, slowDown: 8 },
    });
    graph.forEachNode((node) => {
      layoutPositions.set(node, { x: graph.getNodeAttribute(node, 'x'), y: graph.getNodeAttribute(node, 'y') });
    });
  }

  sigma = new Sigma(graph, $('#eco-graph'), {
    renderLabels: graph.order < 120,
    labelDensity: 0.07,
    labelRenderedSizeThreshold: 8,
    enableEdgeEvents: true,
    defaultEdgeType: 'line',
    defaultNodeType: 'circle',
    zIndex: true,
    allowInvalidContainer: true,
  });

  sigma.on('clickNode', ({ node }) => selectActor(node));
  sigma.on('clickStage', () => clearSelection(false));
}

function nodeColor(id) {
  if (id === selected) return '#e87722';
  const a = byId.get(id);
  return CAT_COLOR[a?.category] || CAT_COLOR.default;
}

function edgeColor(r) {
  if (egoOn && selected && r.source !== selected && r.target !== selected) return '#e2e8f0';
  return EDGE_COLOR[r.type] || EDGE_COLOR.default;
}

function refreshGraphStyles() {
  if (!graph || !sigma) return;
  graph.forEachNode((node) => {
    graph.setNodeAttribute(node, 'color', nodeColor(node));
    graph.setNodeAttribute(node, 'size', node === selected ? 14 : Math.min(12, 5 + (degree.get(node) || 0) * 0.65));
  });
  graph.forEachEdge((edge) => {
    const attr = graph.getEdgeAttributes(edge);
    graph.setEdgeAttribute(edge, 'color', edgeColor({ source: graph.source(edge), target: graph.target(edge), type: attr.type }));
  });
  sigma.refresh();
}

function initMap() {
  map = new maplibregl.Map({
    container: 'eco-map',
    style: 'https://tiles.openfreemap.org/styles/liberty',
    center: [-74.2, -8.2],
    zoom: 3.35,
    attributionControl: true,
    fadeDuration: reducedMotion ? 0 : 300,
  });
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
  map.on('load', () => {
    mapReady = true;
    updateMapLayers();
    markReady();
  });
  map.on('error', (e) => {
    console.warn('MapLibre error', e?.error?.message || e);
  });
}

function actorsGeoJson(ids) {
  const features = actors
    .filter((a) => ids.has(a.id) && a.geo)
    .map((a) => ({
      type: 'Feature',
      properties: {
        id: a.id,
        sel: a.id === selected ? 1 : 0,
        color: nodeColor(a.id),
      },
      geometry: { type: 'Point', coordinates: [a.geo.lng, a.geo.lat] },
    }));
  return { type: 'FeatureCollection', features };
}

function updateMapLayers() {
  if (!map || !mapReady) return;
  const ids = visibleActorIds();
  const data = actorsGeoJson(ids);

  const apply = () => {
    if (!map.getSource('actors')) {
      map.addSource('actors', { type: 'geojson', data, cluster: true, clusterMaxZoom: 11, clusterRadius: 46 });
      map.addLayer({
        id: 'clusters',
        type: 'circle',
        source: 'actors',
        filter: ['has', 'point_count'],
        paint: {
          'circle-color': ['step', ['get', 'point_count'], '#69b5fa', 20, '#0c498a', 60, '#264653'],
          'circle-radius': ['step', ['get', 'point_count'], 14, 20, 18, 60, 22],
          'circle-stroke-width': 2,
          'circle-stroke-color': '#fff',
        },
      });
      map.addLayer({
        id: 'cluster-count',
        type: 'symbol',
        source: 'actors',
        filter: ['has', 'point_count'],
        layout: { 'text-field': '{point_count_abbreviated}', 'text-size': 11 },
        paint: { 'text-color': '#fff' },
      });
      map.addLayer({
        id: 'pins',
        type: 'circle',
        source: 'actors',
        filter: ['!', ['has', 'point_count']],
        paint: {
          'circle-radius': ['case', ['==', ['get', 'sel'], 1], 9, ['interpolate', ['linear'], ['zoom'], 3, 3, 8, 7]],
          'circle-color': ['get', 'color'],
          'circle-opacity': selected ? 0.45 : 0.82,
          'circle-stroke-width': ['case', ['==', ['get', 'sel'], 1], 2, 1],
          'circle-stroke-color': '#fff',
        },
      });
      map.on('click', 'clusters', (e) => {
        const f = e.features[0];
        map.getSource('actors').getClusterExpansionZoom(f.properties.cluster_id, (err, zoom) => {
          if (err) return;
          map.easeTo({ center: f.geometry.coordinates, zoom, duration: reducedMotion ? 0 : 500 });
        });
      });
      map.on('click', 'pins', (e) => {
        const id = e.features[0].properties.id;
        selectActor(id);
      });
      map.on('mouseenter', 'pins', () => { map.getCanvas().style.cursor = 'pointer'; });
      map.on('mouseleave', 'pins', () => { map.getCanvas().style.cursor = ''; });
    } else {
      map.getSource('actors').setData(data);
    }
  };
  apply();
}

function flyToActor(a) {
  if (!map || !a?.geo) return;
  const opts = { center: [a.geo.lng, a.geo.lat], zoom: Math.max(map.getZoom(), 5.4) };
  if (reducedMotion) map.jumpTo(opts);
  else map.flyTo({ ...opts, speed: 0.85, essential: true });
}

function renderInspector(id) {
  const el = $('#inspector');
  const a = byId.get(id);
  const tr = t();
  if (!a) return;
  el.classList.remove('empty');
  const cc = countryCode(a.country);
  const flag = cc ? COUNTRY_META[cc].flag : '🌎';
  const rels = relations.filter((r) => r.source === id || r.target === id);
  const slug = a.nexus?.card_slug;

  const websiteRow = a.website
    ? `<a class="secondary" href="${esc(a.website.startsWith('http') ? a.website : `https://${a.website}`)}" target="_blank" rel="noopener">${tr.website}</a>`
    : `<span class="pending">${tr.websitePending}</span>`;

  const isPerson = a.type === 'person' || a.category === 'mentor';
  const linkedinRow = isPerson
    ? (a.linkedin
      ? `<a class="secondary" href="${esc(a.linkedin)}" target="_blank" rel="noopener">${tr.linkedin}</a>`
      : `<span class="pending">${tr.linkedinPending}</span>`)
    : '';

  const nexusRow = slug
    ? `<a href="/s/${esc(slug)}" target="_blank" rel="noopener">${tr.nexusCard}${esc(slug)}</a>`
    : `<span class="pending">${tr.nexusPending}</span>`;

  el.innerHTML = `
    <div style="padding:14px">
      <h2>${esc(a.name)}</h2>
      <div class="meta">${flag} ${esc(a.country)} · ${esc(tr.cats[a.category] || a.category)} · ${rels.length} ${tr.relationsN}</div>
      <div class="inspector-links">${websiteRow}${linkedinRow}${nexusRow}</div>
      <div class="section">
        <h3>${tr.typedRelations}</h3>
        ${rels.slice(0, 16).map((r) => {
    const otherId = r.source === id ? r.target : r.source;
    const other = byId.get(otherId);
    const dir = r.source === id ? '→' : '←';
    return `<div class="rel-row" data-jump="${esc(otherId)}"><span class="rtype">${esc(r.type.replace(/_/g, '-'))}</span>${dir} ${esc(other?.name || otherId)}</div>`;
  }).join('') || `<p class="meta">${tr.noRelations}</p>`}
      </div>
    </div>`;

  el.querySelectorAll('[data-jump]').forEach((row) => {
    row.addEventListener('click', () => selectActor(row.dataset.jump));
  });
}

function selectActor(id) {
  if (!byId.has(id)) return;
  selected = id;
  $('#workspace').classList.remove('no-inspector');
  renderInspector(id);
  renderAll(false);
  flyToActor(byId.get(id));
  document.querySelectorAll('.actor-card').forEach((c) => c.classList.toggle('selected', c.dataset.id === id));
}

function clearSelection(fullRender = true) {
  selected = null;
  $('#workspace').classList.add('no-inspector');
  $('#inspector').classList.add('empty');
  $('#inspector').innerHTML = `<p class="inspector-empty">${esc(t().inspectorEmpty)}</p>`;
  if (fullRender) renderAll(false);
}

function renderCards(list) {
  const grid = $('#actor-grid');
  const tr = t();
  if (!list.length) {
    grid.innerHTML = `<div class="empty-grid">${tr.noResults}</div>`;
    return;
  }
  grid.innerHTML = list.map((a) => {
    const cc = countryCode(a.country);
    const flag = cc ? COUNTRY_META[cc].flag : '🌎';
    const relN = degree.get(a.id) || 0;
    const catLabel = tr.cats[a.category] || a.category;
    const slug = a.nexus?.card_slug;
    const website = a.website
      ? `<a class="link-btn" href="${esc(a.website.startsWith('http') ? a.website : `https://${a.website}`)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${tr.website}</a>`
      : `<span class="link-btn muted">${tr.websitePending}</span>`;
    const nexus = slug
      ? `<a class="nexus-btn" href="/s/${esc(slug)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${tr.nexusCard}</a>`
      : `<span class="pending-chip">${tr.nexusPending}</span>`;
    return `
      <article class="actor-card${selected === a.id ? ' selected' : ''}" data-id="${esc(a.id)}" tabindex="0">
        <div class="ac-top">
          <div class="ac-icon">${esc(a.name.slice(0, 2).toUpperCase())}</div>
          <div>
            <div class="ac-name">${esc(a.name)}</div>
            <div class="ac-meta">${flag} ${esc(a.country)} · ${relN} ${tr.relationsN}</div>
          </div>
        </div>
        <div class="ac-badges"><span class="badge">${esc(catLabel)}</span></div>
        <div class="ac-links">${website}${nexus}</div>
      </article>`;
  }).join('');

  grid.querySelectorAll('.actor-card').forEach((card) => {
    const open = () => {
      selectActor(card.dataset.id);
      document.querySelector('[data-view-tab="explore"]').click();
    };
    card.addEventListener('click', open);
    card.addEventListener('keydown', (e) => { if (e.key === 'Enter') open(); });
  });
}

function updateStats(ids) {
  $('#stat-actors').textContent = String(actors.length);
  $('#stat-relations').textContent = String(relations.length);
  $('#stat-visible').textContent = String(ids.size);
  $('#result-meta').textContent = `${ids.size} / ${actors.length}`;
}

function renderAll(rebuildLayout = true) {
  const ids = visibleActorIds();
  const rels = visibleRelations(ids);
  updateStats(ids);
  updateMapLayers();
  if (rebuildLayout) buildGraph(ids, rels);
  else refreshGraphStyles();
  if (!$('#panel-cards').classList.contains('hidden')) renderCards(filteredActors());
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

function markReady() {
  if (!window.__ecoReady) window.__ecoReady = true;
}

function applyDemoState() {
  const state = bootParams.get('state');
  if (!state) return;
  if (state === 'filters') {
    activeCountry = bootParams.get('country') || 'PE';
    activeCategories = new Set((bootParams.get('cats') || 'accelerator,government,funder').split(','));
    buildFilterChips();
  }
  if (state === 'selected' || state === 'mobile') {
    selectActor(bootParams.get('actor') || 'pe-emprende-up-climatech-rein-hub-peru');
  }
  if (state === 'ego') {
    egoOn = true;
    egoDepth = parseInt(bootParams.get('depth') || '2', 10);
    $('#ego-toggle').checked = true;
    $('#ego-depth').value = String(egoDepth);
    $('#ego-hint').textContent = `Ego ${egoDepth}-hop`;
    $('#ego-hint').classList.remove('hidden');
    selectActor(bootParams.get('actor') || 'pe-emprende-up-climatech-rein-hub-peru');
  }
  if (bootParams.get('mobile') === '1') document.body.classList.add('mobile-layout');
}

async function loadData() {
  const [a, r] = await Promise.all([
    fetch('data/actors.json').then((res) => res.json()),
    fetch('data/relations.json').then((res) => res.json()),
  ]);
  actors = a;
  relations = r;
  byId = new Map(actors.map((x) => [x.id, x]));
  computeDegrees();
  activeRelTypes = new Set(relations.map((x) => x.type));
  buildFilterChips();
  renderAll();
  applyDemoState();
}

function bindControls() {
  $('#search-input').addEventListener('input', (e) => {
    searchQuery = e.target.value;
    renderAll();
  });
  $('#ego-toggle').addEventListener('change', (e) => {
    egoOn = e.target.checked;
    $('#ego-hint').classList.toggle('hidden', !egoOn);
    $('#ego-hint').textContent = egoOn ? `Ego ${egoDepth}-hop` : '';
    renderAll();
  });
  $('#ego-depth').addEventListener('change', (e) => {
    egoDepth = parseInt(e.target.value, 10);
    $('#ego-hint').textContent = egoOn ? `Ego ${egoDepth}-hop` : '';
    if (egoOn) renderAll();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') clearSelection();
  });
}

async function main() {
  initBrand();
  initLang();
  initTabs();
  initAuthGate();
  bindControls();
  initMap();
  await loadData();
  setTimeout(markReady, reducedMotion ? 400 : 1200);
}

main().catch((err) => {
  console.error(err);
  $('#inspector').innerHTML = `<p>Error: ${esc(err.message)}</p>`;
});
