/* Nexus LATAM Ecosystem — D3 explore + D5 guided story */
import Graph from 'graphology';
import Sigma from 'sigma';
import {
  chapterScene,
  computeChapterEdgeCounts,
  isChallengeId,
} from './story.mjs';

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
    storyRailIntro: 'Recorrido staff: misma vista mapa + red + inspector. Capítulo 5 propone alianzas con aristas Suggested.',
    storyCounts: 'Conteo por capítulo',
    storySuggestedHint: 'Capítulo 5 puede proponer hub/startup/funder sugeridos; no sustituye relaciones verificadas.',
    storyChallengeMeta: 'Nodo reto (Canva)',
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
    storyRailIntro: 'Staff walkthrough: same map + network + inspector. Chapter 5 adds Suggested partnership edges.',
    storyCounts: 'Per-chapter edge counts',
    storySuggestedHint: 'Chapter 5 may suggest hub/startup/funder paths; not verified relationships.',
    storyChallengeMeta: 'Challenge node (Canva)',
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
let fa2Assign = null;

let viewMode = 'explore';
let storyConfig = null;
let storyChapter = 0;
let constellationId = null;
let constellationCloseup = false;
let storyScene = null;
let suggestedEdges = [];

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
      if (viewMode === 'story') renderStoryRail();
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
  document.querySelectorAll('.view-tab').forEach((btn) => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.viewTab;
      viewMode = tab;
      document.querySelectorAll('.view-tab').forEach((b) => b.classList.toggle('active', b === btn));
      $('#panel-explore').classList.toggle('hidden', tab === 'cards');
      $('#panel-cards').classList.toggle('hidden', tab !== 'cards');
      const storyOn = tab === 'story';
      document.body.classList.toggle('story-on', storyOn);
      $('#story-rail').classList.toggle('hidden', !storyOn);
      $('#story-banner').classList.toggle('hidden', !storyOn);
      $('#filter-bar').classList.toggle('hidden', tab === 'cards');
      $('#legend-bar').classList.toggle('hidden', tab === 'cards');
      if (storyOn) {
        renderStoryRail();
        renderStoryChapter();
      } else {
        clearSuggestedOverlay();
        renderAll();
      }
      if (tab === 'cards') renderCards(filteredActors());
      if (tab === 'explore' && sigma) sigma.refresh();
    });
  });
}

function geoXY(a) {
  const g = a.geo || { lat: 0, lng: 0 };
  return { x: (g.lng + 85) * 10, y: (-g.lat - 18) * 10 };
}

/** Lightweight ForceAtlas2-style layout (no Node deps); mirrors graphology FA2 pass. */
function runForceLayout(g, iterations) {
  const nodes = g.nodes();
  const pos = new Map(nodes.map((n) => [n, { x: g.getNodeAttribute(n, 'x'), y: g.getNodeAttribute(n, 'y') }]));
  const repulsion = 120;
  const gravity = 0.02;
  const cx = nodes.reduce((s, n) => s + pos.get(n).x, 0) / nodes.length;
  const cy = nodes.reduce((s, n) => s + pos.get(n).y, 0) / nodes.length;
  for (let it = 0; it < iterations; it += 1) {
    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i];
        const b = nodes[j];
        const pa = pos.get(a);
        const pb = pos.get(b);
        let dx = pa.x - pb.x;
        let dy = pa.y - pb.y;
        let d2 = dx * dx + dy * dy + 0.01;
        const f = repulsion / d2;
        dx *= f;
        dy *= f;
        pa.x += dx;
        pa.y += dy;
        pb.x -= dx;
        pb.y -= dy;
      }
    }
    g.forEachEdge((edge) => {
      const s = g.source(edge);
      const t = g.target(edge);
      const ps = pos.get(s);
      const pt = pos.get(t);
      const dx = pt.x - ps.x;
      const dy = pt.y - ps.y;
      ps.x += dx * 0.004;
      ps.y += dy * 0.004;
      pt.x -= dx * 0.004;
      pt.y -= dy * 0.004;
    });
    nodes.forEach((n) => {
      const p = pos.get(n);
      p.x += (cx - p.x) * gravity;
      p.y += (cy - p.y) * gravity;
      g.setNodeAttribute(n, 'x', p.x);
      g.setNodeAttribute(n, 'y', p.y);
    });
  }
}

function buildGraph(idSet, rels, opts = {}) {
  const {
    virtualNodes = [],
    presetPositions = null,
    storyLayout = false,
    storySuggested = [],
  } = opts;

  suggestedEdges = storySuggested;

  if (sigma) {
    sigma.kill();
    sigma = null;
  }
  graph = new Graph({ multi: true, type: 'directed' });

  const addNode = (id, attrs) => {
    if (graph.hasNode(id)) return;
    graph.addNode(id, attrs);
  };

  idSet.forEach((id) => {
    if (isChallengeId(id)) return;
    const a = byId.get(id);
    if (!a) return;
    let pos = layoutPositions.get(id) || geoXY(a);
    if (presetPositions?.has(id)) {
      pos = presetPositions.get(id).position || presetPositions.get(id);
    }
    const size = id === selected ? 14 : Math.min(12, 5 + (degree.get(id) || 0) * 0.65);
    addNode(id, {
      label: a.name.length > 24 ? `${a.name.slice(0, 22)}…` : a.name,
      x: pos.x,
      y: pos.y,
      size,
      color: nodeColor(id),
    });
  });

  virtualNodes.forEach((vn) => {
    const pos = presetPositions?.get(vn.id)?.position
      || (vn.geo ? geoXY({ geo: vn.geo }) : { x: 0, y: 0 });
    const lbl = vn.label?.length > 24 ? `${vn.label.slice(0, 22)}…` : (vn.label || vn.id);
    addNode(vn.id, {
      label: lbl,
      x: pos.x,
      y: pos.y,
      size: vn.size || 14,
      color: vn.color || '#2a9d8f',
    });
  });

  rels.filter((r) => !r.suggested).forEach((r, i) => {
    if (!graph.hasNode(r.source) || !graph.hasNode(r.target)) return;
    const key = r.id || `e-${i}-${r.source}-${r.target}-${r.type}`;
    try {
      graph.addEdgeWithKey(key, r.source, r.target, {
        type: r.type,
        color: EDGE_COLOR[r.type] || EDGE_COLOR.default,
        size: selected && (r.source === selected || r.target === selected) ? 2.2 : 2,
        suggested: false,
      });
    } catch {
      /* duplicate parallel */
    }
  });

  const runLayout = !storyLayout && !presetPositions && !reducedMotion && graph.order > 1;
  if (runLayout) {
    if (fa2Assign) {
      fa2Assign(graph, {
        iterations: Math.min(120, 40 + graph.order),
        settings: { gravity: 0.8, scalingRatio: 8, slowDown: 8 },
      });
    } else {
      runForceLayout(graph, Math.min(90, 30 + graph.order));
    }
    graph.forEachNode((node) => {
      layoutPositions.set(node, { x: graph.getNodeAttribute(node, 'x'), y: graph.getNodeAttribute(node, 'y') });
    });
  }

  sigma = new Sigma(graph, $('#eco-graph'), {
    renderLabels: graph.order < 120,
    labelDensity: 0.07,
    labelRenderedSizeThreshold: 8,
    enableEdgeEvents: true,
    defaultEdgeType: 'arrow',
    defaultNodeType: 'circle',
    renderEdgeLabels: false,
    zIndex: true,
    allowInvalidContainer: true,
  });

  sigma.on('clickNode', ({ node }) => selectActor(node));
  sigma.on('clickStage', () => clearSelection(false));
  sigma.on('afterRender', () => drawSuggestedOverlay());
  requestAnimationFrame(() => drawSuggestedOverlay());
}

function nodeColor(id) {
  if (isChallengeId(id)) return '#2a9d8f';
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

function actorsGeoJson(ids, virtualNodes = []) {
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
  virtualNodes.forEach((vn) => {
    if (!vn.geo || !ids.has(vn.id)) return;
    features.push({
      type: 'Feature',
      properties: {
        id: vn.id,
        sel: vn.id === selected ? 1 : 0,
        color: '#2a9d8f',
      },
      geometry: { type: 'Point', coordinates: [vn.geo.lng, vn.geo.lat] },
    });
  });
  return { type: 'FeatureCollection', features };
}

function updateMapLayers(scene = null) {
  if (!map || !mapReady) return;
  const ids = scene ? scene.nodeIds : visibleActorIds();
  const data = actorsGeoJson(ids, scene?.virtualNodes || []);

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
  const tr = t();
  if (isChallengeId(id) && storyConfig) {
    const meta = storyConfig.challenges[id];
    const linked = relations.filter((r) => r.target === id || r.source === id);
    const title = lang === 'EN' ? meta?.label?.en : meta?.label?.es;
    el.classList.remove('empty');
    el.innerHTML = `
      <div style="padding:14px">
        <h2>${esc(title || id)}</h2>
        <div class="meta">${tr.storyChallengeMeta || 'Challenge node'} · ${linked.length} works_on_challenge</div>
        <div class="section"><h3>${tr.typedRelations}</h3>
        ${linked.slice(0, 12).map((r) => {
      const o = byId.get(r.source);
      return `<div class="rel-row"><span class="rtype">${esc(r.type.replace(/_/g, '-'))}</span>${esc(o?.name || r.source)}</div>`;
    }).join('') || `<p class="meta">${tr.noRelations}</p>`}
        </div>
        <p class="meta" style="margin-top:8px">${esc(tr.storySuggestedHint || '')}</p>
      </div>`;
    return;
  }
  const a = byId.get(id);
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
  if (!byId.has(id) && !isChallengeId(id)) return;
  selected = id;
  $('#workspace').classList.remove('no-inspector');
  renderInspector(id);
  renderAll(false);
  if (isChallengeId(id) && storyConfig?.challenges[id]?.geo) {
    const g = storyConfig.challenges[id].geo;
    const opts = { center: [g.lng, g.lat], zoom: Math.max(map?.getZoom() || 5, 5.8) };
    if (map) {
      if (reducedMotion) map.jumpTo(opts);
      else map.flyTo({ ...opts, speed: 0.85, essential: true });
    }
  } else {
    flyToActor(byId.get(id));
  }
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
  if (viewMode === 'story') {
    renderStoryChapter();
    return;
  }
  const ids = visibleActorIds();
  const rels = visibleRelations(ids);
  updateStats(ids);
  updateMapLayers();
  if (rebuildLayout) buildGraph(ids, rels);
  else refreshGraphStyles();
  if (!$('#panel-cards').classList.contains('hidden')) renderCards(filteredActors());
}

function drawSuggestedOverlay() {
  const canvas = $('#eco-suggest-overlay');
  if (!canvas || !sigma || !graph) return;
  const host = $('#eco-graph');
  const rect = host.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.floor(rect.width * dpr);
  canvas.height = Math.floor(rect.height * dpr);
  canvas.style.width = `${rect.width}px`;
  canvas.style.height = `${rect.height}px`;
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, rect.width, rect.height);
  if (!suggestedEdges.length) return;

  suggestedEdges.forEach((e) => {
    if (!graph.hasNode(e.source) || !graph.hasNode(e.target)) return;
    const sAttr = graph.getNodeAttributes(e.source);
    const tAttr = graph.getNodeAttributes(e.target);
    const s = sigma.graphToViewport({ x: sAttr.x, y: sAttr.y });
    const tpos = sigma.graphToViewport({ x: tAttr.x, y: tAttr.y });
    if (!s || !tpos) return;
    ctx.save();
    ctx.setLineDash([7, 5]);
    ctx.strokeStyle = 'rgba(249, 115, 22, 0.85)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(s.x, s.y);
    ctx.lineTo(tpos.x, tpos.y);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#c2410c';
    ctx.font = '600 9px Open Sans, sans-serif';
    ctx.fillText('Suggested', (s.x + tpos.x) / 2 - 24, (s.y + tpos.y) / 2 - 4);
    ctx.restore();
  });
}

function clearSuggestedOverlay() {
  suggestedEdges = [];
  const canvas = $('#eco-suggest-overlay');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function flyToStoryMap(scene) {
  if (!map || !scene?.map) return;
  const m = scene.map;
  const opts = { center: m.center, zoom: m.zoom || 5 };
  if (reducedMotion) map.jumpTo(opts);
  else map.easeTo({ ...opts, duration: 700 });
}

function renderStoryRail() {
  if (!storyConfig) return;
  const rail = $('#story-rail');
  const tr = t();
  const banner = $('#story-banner');
  const bmsg = lang === 'EN' ? storyConfig.banner.en : storyConfig.banner.es;
  banner.innerHTML = `${esc(bmsg)} · <span class="suggested-tag">Suggested</span>`;

  rail.innerHTML = `<p class="meta" style="font-size:10px;margin:0 0 8px">${esc(tr.storyRailIntro || '')}</p>`;
  storyConfig.chapters.forEach((ch, idx) => {
    const step = document.createElement('div');
    step.className = `story-step${idx === storyChapter ? ' on' : ''}`;
    step.innerHTML = `<h3>${esc(lang === 'EN' ? ch.title.en : ch.title.es)}</h3><p>${esc(lang === 'EN' ? ch.blurb.en : ch.blurb.es)}</p>`;
    step.addEventListener('click', () => {
      storyChapter = idx;
      constellationId = null;
      constellationCloseup = false;
      renderStoryRail();
      renderStoryChapter();
    });
    rail.appendChild(step);
  });

  if (storyConfig.chapters[storyChapter]?.id === 'partnerships') {
    const row = document.createElement('div');
    row.className = 'story-constellation-row';
    storyConfig.constellations.forEach((c) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = `chip sm ${constellationId === c.id ? 'on' : ''}`;
      b.textContent = c.id;
      b.addEventListener('click', (ev) => {
        ev.stopPropagation();
        constellationId = c.id;
        constellationCloseup = true;
        renderStoryRail();
        renderStoryChapter();
      });
      row.appendChild(b);
    });
    rail.appendChild(row);
  }

  const counts = computeChapterEdgeCounts(storyConfig, relations, byId);
  window.__storyEdgeCounts = counts;
  const gaps = document.createElement('div');
  gaps.className = 'story-gaps';
  gaps.innerHTML = `<strong>${esc(tr.storyCounts || 'Edge counts')}</strong><br/>${counts.map((c) =>
    `${esc(c.title)}: ${c.real} real${c.suggested ? `, ${c.suggested} suggested` : ''}`,
  ).join('<br/>')}`;
  rail.appendChild(gaps);
}

function renderStoryChapter() {
  if (!storyConfig) return;
  storyScene = chapterScene(storyChapter, storyConfig, relations, byId, {
    constellationId,
    closeup: constellationCloseup,
  });
  const current = computeChapterEdgeCounts(storyConfig, relations, byId)[storyChapter];
  window.__storyChapterActive = {
    chapter: storyScene.chapter.id,
    real: current?.real ?? storyScene.realRels.length,
    suggested: current?.suggested ?? storyScene.suggested.length,
  };

  updateStats(storyScene.nodeIds);
  flyToStoryMap(storyScene);
  updateMapLayers(storyScene);
  const vNodes = (storyScene.virtualNodes || []).map((vn) => ({
    ...vn,
    label: lang === 'EN'
      ? (storyConfig.challenges[vn.id]?.label?.en || vn.label)
      : (storyConfig.challenges[vn.id]?.label?.es || vn.label),
  }));
  buildGraph(storyScene.nodeIds, storyScene.realRels, {
    virtualNodes: vNodes,
    presetPositions: storyScene.presetPositions,
    storyLayout: Boolean(storyScene.presetPositions),
    storySuggested: storyScene.suggested,
  });
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
  if (!window.__ecoReady) {
    window.__ecoReady = true;
    document.body.dataset.ecoReady = '1';
  }
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
  if (state === 'story' || bootParams.get('view') === 'story') {
    storyChapter = Math.min(4, Math.max(0, parseInt(bootParams.get('chapter') || '0', 10)));
    constellationId = bootParams.get('constellation') || null;
    constellationCloseup = bootParams.get('closeup') === '1';
    const tab = document.querySelector('[data-view-tab="story"]');
    if (tab) tab.click();
  }
}

async function loadData() {
  const [a, r, story] = await Promise.all([
    fetch('data/actors.json').then((res) => res.json()),
    fetch('data/relations.json').then((res) => res.json()),
    fetch('data/story-chapters.json').then((res) => res.json()),
  ]);
  storyConfig = story;
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
  window.addEventListener('resize', () => drawSuggestedOverlay());
}

async function main() {
  initBrand();
  initLang();
  initTabs();
  initAuthGate();
  bindControls();
  try {
    const mod = await import('https://esm.sh/graphology-layout-forceatlas2@0.10.1');
    fa2Assign = mod.default?.assign || mod.assign;
  } catch {
    fa2Assign = null;
  }
  initMap();
  await loadData();
  setTimeout(markReady, reducedMotion ? 400 : 1200);
}

main().catch((err) => {
  console.error(err);
  $('#inspector').innerHTML = `<p>Error: ${esc(err.message)}</p>`;
});
