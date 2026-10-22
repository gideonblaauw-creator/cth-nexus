/* Nexus LATAM Ecosystem — D3 explore + D5 guided story */
import Graph from 'graphology';
import Sigma from 'sigma';
import {
  chapterScene,
  computeChapterEdgeCounts,
  isChallengeId,
  isDatasetId,
  isPolicyId,
  isPublicGraphRelation,
  datasetGeo,
  policyGeo,
} from './story.mjs';
import {
  actorCountryCode,
  countryBadgeCounts,
  countryBadgeGeoJson,
  geoXY,
  hasPlottableGeo,
  isLocationUnknown,
  redactPublicStreetText,
  visiblePlaceParts,
  visibleStreetAddress,
} from './geo-utils.mjs';
import { mountJourney } from './journey-view.mjs';
import { sourcedJourneyStartups } from './journey.mjs';

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const MAP_FONT_STACK = ['Noto Sans Regular'];

const COUNTRY_META = {
  PE: { key: 'Peru', flag: '🇵🇪' },
  SV: { key: 'El Salvador', flag: '🇸🇻' },
  CO: { key: 'Colombia', flag: '🇨🇴' },
  GT: { key: 'Guatemala', flag: '🇬🇹' },
  CR: { key: 'Costa Rica', flag: '🇨🇷' },
};

/** Fallback when `country` label drifts from COUNTRY_META (CO/PE bleed guard). */
const ID_PREFIX_COUNTRY = {
  pe: 'PE',
  sv: 'SV',
  co: 'CO',
  gt: 'GT',
  cr: 'CR',
};

const CATEGORY_KEYS = [
  'government', 'accelerator', 'international', 'funder', 'ngo_foundation',
  'academia', 'corporate', 'finance', 'chamber', 'startup', 'media', 'hub', 'mentor', 'program', 'policy',
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
  funding: '#264653',
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
  issues_policy: '#6b4c9a',
  addresses_challenge: '#2a9d8f',
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
    tabJourney: 'Camino de la startup',
    tabCards: 'Fichas de actores',
    tabStory: 'Historia guiada',
    journeyTitle: 'Camino de la startup',
    journeySub: 'Recorrido de la startup: reto, mapa con direcciones reales y red de relaciones públicas.',
    journeyChallenge: 'Área de reto',
    journeyStartup: 'Startup',
    journeyRail: 'Recorrido',
    journeyMap: 'Mapa (solo direcciones reales)',
    journeyGraph: 'Red · camino resaltado',
    journeyDataMap: 'Mapa de datos',
    journeyUnknown: 'Ubicación desconocida',
    journeyUnknownNone: 'Nada que listar en este recorrido.',
    journeyNoPublic: 'Sin fuente pública',
    journeyFactsTitle: 'Datos verificados de la startup',
    journeyFactLocation: 'Ubicación',
    journeyFactStat: 'Dato citado',
    journeySourcedTitle: 'Recorridos con fuente pública',
    storySourcedTitle: 'Startups con recorrido y fuente',
    storySourcedHint: 'Tienen al menos una relación pública con cita textual. Abre su camino.',
    storySourcedEmpty: 'Ninguna startup del catálogo tiene aún una relación pública.',
    journeyNoPin: 'Mapa: sin pin — ubicación desconocida (hace falta dirección a nivel de calle).',
    journeyEdge: 'Relación',
    journeySource: 'Fuente pública',
    journeyEmpty: 'Elige una startup para ver el recorrido.',
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
    hubPage: 'Hub REIN /hubs/',
    hubPagePending: 'Página hub pendiente',
    datasetPending: 'Conjunto de datos pendiente',
    mapLink: 'Ver en mapa',
    founded: 'Fundación',
    cardRole: 'Rol',
    relationsN: 'relaciones',
    typedRelations: 'Relaciones tipadas',
    noResults: 'Sin resultados con estos filtros.',
    noRelations: 'Sin relaciones en datos.',
    geoUnknownTitle: 'Ubicación en mapa pendiente',
    geoUnknownHint: 'Sin pin individual (sin dirección verificada con coordenadas). Listados aquí; agrupados por país en el mapa.',
    hqAbroad: 'Sede fuera del país',
    hqAbroadHint: 'La dirección verificada está fuera del país del actor en el catálogo.',
    storyRailIntro: 'Recorrido staff: misma vista mapa + red + inspector. Capítulo 5 propone alianzas con aristas Suggested.',
    storyCounts: 'Conteo por capítulo',
    storySuggestedHint: 'Capítulo 5 puede proponer hub/startup/funder sugeridos; no sustituye relaciones verificadas.',
    storyChallengeMeta: 'Nodo reto (Canva)',
    nexusCrossIdeas: 'Ideas Nexus',
    nexusCrossSolutions: 'Soluciones (/s/)',
    nexusCrossStartups: 'Startups en el reto',
    policyStartups: 'Startups relacionadas',
    challengePolicies: 'Políticas relacionadas',
    suggestedLabel: 'Sugerido',
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
    tabJourney: 'Startup journey',
    tabCards: 'Actor cards',
    tabStory: 'Guided story',
    journeyTitle: 'Startup journey',
    journeySub: 'Startup path: nature challenge, street-level map, and public relationship network.',
    journeyChallenge: 'Nature challenge',
    journeyStartup: 'Startup',
    journeyRail: 'Journey',
    journeyMap: 'Map (street addresses only)',
    journeyGraph: 'Network · highlighted path',
    journeyDataMap: 'Data map',
    journeyUnknown: 'Location unknown',
    journeyUnknownNone: 'Nothing to list on this journey.',
    journeyNoPublic: 'No public source',
    journeyFactsTitle: 'Verified facts for this startup',
    journeyFactLocation: 'Location',
    journeyFactStat: 'Cited figure',
    journeySourcedTitle: 'Journeys with a public source',
    storySourcedTitle: 'Startups with a sourced journey',
    storySourcedHint: 'At least one public relation with a verbatim quote. Open their path.',
    storySourcedEmpty: 'No catalog startup has a public relation yet.',
    journeyNoPin: 'Map: no pin — location unknown (a street-level address is required).',
    journeyEdge: 'Relation',
    journeySource: 'Public source',
    journeyEmpty: 'Choose a startup to see the journey.',
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
    hubPage: 'REIN hub /hubs/',
    hubPagePending: 'Hub page pending',
    datasetPending: 'Dataset pending',
    mapLink: 'View on map',
    founded: 'Founded',
    cardRole: 'Role',
    relationsN: 'relations',
    typedRelations: 'Typed relations',
    noResults: 'No results with these filters.',
    noRelations: 'No relations in data.',
    geoUnknownTitle: 'Map location pending',
    geoUnknownHint: 'No individual pin (no verified street address with coordinates). Listed here; grouped by country badge on the map.',
    hqAbroad: 'HQ abroad',
    hqAbroadHint: 'Verified address is outside this actor’s catalogue country.',
    storyRailIntro: 'Staff walkthrough: same map + network + inspector. Chapter 5 adds Suggested partnership edges.',
    storyCounts: 'Per-chapter edge counts',
    storySuggestedHint: 'Chapter 5 may suggest hub/startup/funder paths; not verified relationships.',
    storyChallengeMeta: 'Challenge node (Canva)',
    nexusCrossIdeas: 'Nexus ideas',
    nexusCrossSolutions: 'Solutions (/s/)',
    nexusCrossStartups: 'Startups on this challenge',
    policyStartups: 'Related startups',
    challengePolicies: 'Related policies',
    suggestedLabel: 'Suggested',
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
let pinPopup = null;
let pinTooltip = null;
let graph = null;
let sigma = null;
let layoutPositions = new Map();
let fa2Assign = null;

let viewMode = 'explore';
let storyConfig = null;
let nexusCrosslinks = null;
let policies = [];
let policiesById = new Map();
let policyRelations = [];
let dataRelations = [];
let storyChapter = 0;
let storyFocusCountry = null;
let constellationId = null;
let constellationCloseup = false;
let storyScene = null;
let suggestedEdges = [];
let journeyController = null;

const $ = (sel) => document.querySelector(sel);
const t = () => I18N[lang];

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

function countryCode(name) {
  if (!name) return null;
  const norm = String(name).normalize('NFD').replace(/\p{M}/gu, '').trim();
  const entry = Object.entries(COUNTRY_META).find(([, v]) => {
    const key = v.key.normalize('NFD').replace(/\p{M}/gu, '').trim();
    return key.toLowerCase() === norm.toLowerCase();
  });
  return entry ? entry[0] : null;
}

function normalizeCountryParam(raw) {
  if (!raw || raw === 'ALL') return null;
  const trimmed = String(raw).trim();
  const upper = trimmed.toUpperCase();
  if (upper in COUNTRY_META) return upper;
  const fromName = countryCode(trimmed);
  if (fromName) return fromName;
  const prefix = trimmed.toLowerCase().slice(0, 2);
  if (ID_PREFIX_COUNTRY[prefix]) return ID_PREFIX_COUNTRY[prefix];
  return upper.length === 2 ? upper : null;
}

function publicGraphRelations() {
  return relations.filter((r) => isPublicGraphRelation(r));
}

function computeDegrees() {
  degree = new Map();
  actors.forEach((a) => degree.set(a.id, 0));
  publicGraphRelations().forEach((r) => {
    if (degree.has(r.source)) degree.set(r.source, (degree.get(r.source) || 0) + 1);
    if (degree.has(r.target)) degree.set(r.target, (degree.get(r.target) || 0) + 1);
  });
}

function egoNodeSet(centerId, depth) {
  const keep = new Set([centerId]);
  for (let d = 0; d < depth; d += 1) {
    publicGraphRelations().forEach((r) => {
      if (keep.has(r.source)) keep.add(r.target);
      if (keep.has(r.target)) keep.add(r.source);
    });
  }
  return keep;
}

function filteredActors() {
  const q = searchQuery.trim().toLowerCase();
  return actors.filter((a) => {
    const cc = actorCountryCode(a);
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
  return publicGraphRelations().filter((r) => {
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
  if (viewMode === 'journey') {
    $('.ph-title').textContent = tr.journeyTitle;
    $('.ph-sub').textContent = tr.journeySub;
    document.title = lang === 'EN'
      ? 'Startup journey — CleantechHUB Nexus'
      : 'Camino de la startup — CleantechHUB Nexus';
  } else {
    document.title = 'Ecosistema LATAM — CleantechHUB Nexus';
  }
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
      if (viewMode === 'journey') journeyController?.refresh();
      else renderAll();
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
      activeCountry = normalizeCountryParam(btn.dataset.cc === 'ALL' ? null : btn.dataset.cc);
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

  const relTypes = [...new Set(publicGraphRelations().map((r) => r.type))].sort();
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
      const storyOn = tab === 'story';
      $('#panel-explore').classList.toggle('hidden', tab !== 'explore' && !storyOn);
      $('#panel-cards').classList.toggle('hidden', tab !== 'cards');
      $('#panel-journey').classList.toggle('hidden', tab !== 'journey');
      document.body.classList.toggle('story-on', storyOn);
      document.body.classList.toggle('journey-on', tab === 'journey');
      $('#story-rail').classList.toggle('hidden', !storyOn);
      $('#story-banner').classList.toggle('hidden', !storyOn);
      document.body.classList.toggle('cards-view', tab === 'cards');
      $('#legend-bar').classList.toggle('hidden', tab === 'cards' || tab === 'journey');
      applyI18n();
      if (tab === 'journey') {
        journeyController?.show();
      } else if (storyOn) {
        renderStoryRail();
        renderStoryChapter();
      } else if (tab === 'cards') {
        clearSuggestedOverlay();
        updateStats(new Set(filteredActors().map((a) => a.id)));
        renderCards(filteredActors());
      } else {
        clearSuggestedOverlay();
        renderAll();
      }
      if (tab === 'explore' && sigma) sigma.refresh();
      syncPinPopup();
    });
  });
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
    if (isChallengeId(id) || isPolicyId(id)) return;
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
  window.__ecoMap = map;
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
    .filter((a) => ids.has(a.id) && hasPlottableGeo(a))
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
  const badges = countryBadgeGeoJson(countryBadgeCounts(actors, ids));

  const apply = () => {
    if (!map.getSource('actors')) {
      map.addSource('actors', { type: 'geojson', data, cluster: true, clusterMaxZoom: 11, clusterRadius: 46 });
      map.addSource('country-badges', { type: 'geojson', data: badges });
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
        layout: {
          'text-field': '{point_count_abbreviated}',
          'text-size': 11,
          'text-font': MAP_FONT_STACK,
        },
        paint: { 'text-color': '#fff' },
      });
      map.addLayer({
        id: 'pins',
        type: 'circle',
        source: 'actors',
        filter: ['!', ['has', 'point_count']],
        paint: {
          'circle-radius': [
            'interpolate', ['linear'], ['zoom'],
            3, 3,
            8, ['case', ['==', ['get', 'sel'], 1], 10, 7],
          ],
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
        hidePinTooltip();
        selectActor(id);
      });
      map.on('mouseenter', 'pins', (e) => {
        map.getCanvas().style.cursor = 'pointer';
        const id = e.features?.[0]?.properties?.id;
        const actor = byId.get(id);
        if (!actor) return;
        const lngLat = e.features[0].geometry.coordinates;
        showPinTooltip(actor, lngLat);
      });
      map.on('mouseleave', 'pins', () => {
        map.getCanvas().style.cursor = '';
        hidePinTooltip();
      });
      map.addLayer({
        id: 'country-badges',
        type: 'symbol',
        source: 'country-badges',
        layout: {
          'text-field': ['concat', ['get', 'country'], ' · ', ['to-string', ['get', 'count']]],
          'text-size': 11,
          'text-anchor': 'center',
          'text-font': MAP_FONT_STACK,
        },
        paint: {
          'text-color': '#0c498a',
          'text-halo-color': '#fff',
          'text-halo-width': 2,
        },
      });
    } else {
      map.getSource('actors').setData(data);
      if (map.getSource('country-badges')) map.getSource('country-badges').setData(badges);
    }
  };
  apply();
  renderGeoUnknownPanel(ids);
  syncPinPopup();
}

function pinPopupHtml(actor) {
  const street = visibleStreetAddress(actor);
  const place = visiblePlaceParts(actor);
  const placeText = [place.city, place.country].filter(Boolean).join(', ');
  const streetHtml = street
    ? `<div class="eco-pin-address">${esc(street)}</div>`
    : '';
  const placeHtml = placeText
    ? `<div class="eco-pin-place">${esc(placeText)}</div>`
    : '';
  return `<div class="eco-pin-popup-body"><strong>${esc(actor.name)}</strong>${placeHtml}${streetHtml}</div>`;
}

function hidePinTooltip() {
  if (pinTooltip) pinTooltip.remove();
}

function showPinTooltip(actor, lngLat) {
  if (!map || !lngLat) return;
  const html = pinPopupHtml(actor);
  if (!pinTooltip) {
    pinTooltip = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false,
      className: 'eco-pin-tooltip',
      offset: 10,
      maxWidth: '240px',
    });
  }
  pinTooltip.setLngLat(lngLat).setHTML(html).addTo(map);
}

function syncPinPopup() {
  if (!map || !mapReady || viewMode !== 'explore') {
    if (pinPopup) pinPopup.remove();
    return;
  }
  const actor = selected ? byId.get(selected) : null;
  if (!actor || !hasPlottableGeo(actor)) {
    if (pinPopup) pinPopup.remove();
    return;
  }
  if (!pinPopup) {
    pinPopup = new maplibregl.Popup({
      closeButton: true,
      closeOnClick: false,
      className: 'eco-pin-popup',
      offset: 14,
      maxWidth: '260px',
      anchor: 'bottom',
    });
  }
  pinPopup.setLngLat([actor.geo.lng, actor.geo.lat]).setHTML(pinPopupHtml(actor)).addTo(map);
}

function crosslinkSection(title, items, tr) {
  if (!items?.length) return '';
  const rows = items.map((item) => {
    const sug = item.inferred
      ? `<span class="badge suggested">${esc(tr.suggestedLabel)}</span>`
      : '';
    return `<li><a href="${esc(item.href)}" target="_blank" rel="noopener">${esc(item.label)}</a> ${sug}</li>`;
  }).join('');
  return `<div class="section"><h3>${esc(title)}</h3><ul class="crosslink-list">${rows}</ul></div>`;
}

function flyToActor(a) {
  if (!map || !hasPlottableGeo(a)) return;
  const opts = { center: [a.geo.lng, a.geo.lat], zoom: Math.max(map.getZoom(), 5.4) };
  if (reducedMotion) map.jumpTo(opts);
  else map.flyTo({ ...opts, speed: 0.85, essential: true });
}

function renderInspector(id) {
  const el = $('#inspector');
  const tr = t();
  if (isPolicyId(id)) {
    const row = policiesById.get(id);
    const linked = [...publicGraphRelations(), ...policyRelations].filter((r) => r.source === id || r.target === id);
    const policyStartups = nexusCrosslinks?.byPolicy?.[id] || [];
    el.classList.remove('empty');
    el.innerHTML = `
      <div style="padding:14px">
        <h2>${esc(row?.name || id)}</h2>
        <div class="meta">${esc(row?.country || '')} · ${esc(row?.instrument || 'policy')} · ${linked.length} links</div>
        ${row?.source_url ? `<a class="secondary" href="${esc(row.source_url)}" target="_blank" rel="noopener">${tr.website}</a>` : ''}
        ${crosslinkSection(tr.policyStartups, policyStartups, tr)}
        <div class="section"><h3>${tr.typedRelations}</h3>
        ${linked.slice(0, 12).map((r) => {
      const otherId = r.source === id ? r.target : r.source;
      const other = byId.get(otherId);
      const oLabel = other?.name
        || (isChallengeId(otherId) ? (storyConfig?.challenges[otherId]?.label?.[lang === 'EN' ? 'en' : 'es'] || otherId) : otherId);
      return `<div class="rel-row"><span class="rtype">${esc(r.type.replace(/_/g, '-'))}</span>${esc(oLabel)}</div>`;
    }).join('') || `<p class="meta">${tr.noRelations}</p>`}
        </div>
      </div>`;
    return;
  }
  if (isDatasetId(id) && storyConfig?.datasets?.[id]) {
    const meta = storyConfig.datasets[id];
    const title = lang === 'EN' ? meta.label?.en : meta.label?.es;
    el.classList.remove('empty');
    el.innerHTML = `
      <div style="padding:14px">
        <h2>${esc(title || id)}</h2>
        <div class="meta">${esc(meta.country || '')} · ${meta.status === 'pending' ? esc(tr.datasetPending) : 'dataset'}</div>
        ${meta.source_url ? `<a class="secondary" href="${esc(meta.source_url)}" target="_blank" rel="noopener">${tr.website}</a>` : ''}
      </div>`;
    return;
  }
  if (isChallengeId(id) && storyConfig) {
    const meta = storyConfig.challenges[id];
    const linked = publicGraphRelations().filter((r) => r.target === id || r.source === id);
    const title = lang === 'EN' ? meta?.label?.en : meta?.label?.es;
    const panel = nexusCrosslinks?.byChallenge?.[id] || {};
    const relatedPolicies = policyRelations
      .filter((r) => r.source === id || r.target === id)
      .map((r) => (r.source === id ? r.target : r.source))
      .filter((pid) => isPolicyId(pid))
      .filter((pid, i, arr) => arr.indexOf(pid) === i)
      .map((pid) => {
        const row = policiesById.get(pid);
        const inferred = policyRelations.some(
          (r) => (r.source === pid || r.target === pid)
            && (r.source === id || r.target === id)
            && (r.suggested || r.verified === false),
        );
        return {
          label: row?.name || pid,
          href: `#policy-${pid}`,
          inferred,
          policyId: pid,
        };
      });
    const policySection = relatedPolicies.length
      ? `<div class="section"><h3>${esc(tr.challengePolicies)}</h3><ul class="crosslink-list">${relatedPolicies.map((p) => {
        const sug = p.inferred ? `<span class="badge suggested">${esc(tr.suggestedLabel)}</span>` : '';
        return `<li><button type="button" class="linkish" data-jump-policy="${esc(p.policyId)}">${esc(p.label)}</button> ${sug}</li>`;
      }).join('')}</ul></div>`
      : '';
    el.classList.remove('empty');
    el.innerHTML = `
      <div style="padding:14px">
        <h2>${esc(title || id)}</h2>
        <div class="meta">${tr.storyChallengeMeta || 'Challenge node'} · ${linked.length} works_on_challenge</div>
        ${policySection}
        ${crosslinkSection(tr.nexusCrossIdeas, panel.ideas, tr)}
        ${crosslinkSection(tr.nexusCrossSolutions, panel.solutions, tr)}
        ${crosslinkSection(tr.nexusCrossStartups, panel.startups, tr)}
        <div class="section"><h3>${tr.typedRelations}</h3>
        ${linked.slice(0, 12).map((r) => {
      const o = byId.get(r.source);
      const slug = o?.nexus?.card_slug;
      const name = o?.name || r.source;
      const label = slug && o?.category === 'startup'
        ? `<a href="/s/${esc(slug)}/" target="_blank" rel="noopener">${esc(name)}</a>`
        : esc(name);
      return `<div class="rel-row"><span class="rtype">${esc(r.type.replace(/_/g, '-'))}</span>${label}</div>`;
    }).join('') || `<p class="meta">${tr.noRelations}</p>`}
        </div>
        <p class="meta" style="margin-top:8px">${esc(tr.storySuggestedHint || '')}</p>
      </div>`;
    el.querySelectorAll('[data-jump-policy]').forEach((btn) => {
      btn.addEventListener('click', () => selectActor(btn.dataset.jumpPolicy));
    });
    return;
  }
  const a = byId.get(id);
  if (!a) return;
  el.classList.remove('empty');
  const cc = actorCountryCode(a);
  const flag = cc ? COUNTRY_META[cc].flag : '🌎';
  const rels = publicGraphRelations().filter((r) => r.source === id || r.target === id);
  const slug = a.nexus?.card_slug;

  const websiteRow = a.website
    ? `<a class="secondary" href="${esc(a.website.startsWith('http') ? a.website : `https://${a.website}`)}" target="_blank" rel="noopener">${tr.website}</a>`
    : `<span class="pending">${tr.websitePending}</span>`;

  const linkedinRow = a.linkedin
    ? `<a class="secondary" href="${esc(a.linkedin)}" target="_blank" rel="noopener">${tr.linkedin}</a>`
    : '';

  const nexusRow = slug
    ? `<a href="/s/${esc(slug)}/" target="_blank" rel="noopener">${tr.nexusCard}${esc(slug)}</a>`
    : (a.category === 'startup'
      ? `<span class="pending">${tr.nexusPending}</span>`
      : '');
  const hubSlug = a.nexus?.hub_slug;
  const hubRow = hubSlug
    ? `<a href="/hubs/${esc(hubSlug)}/" target="_blank" rel="noopener">${tr.hubPage}${esc(hubSlug)}</a>`
    : '';
  const roleText = redactPublicStreetText(a, cardField(a, 'ecosystem_role'));
  const descText = redactPublicStreetText(a, cardField(a, 'description'));
  const yearText = cardField(a, 'founding_year');
  const detailBits = [
    roleText ? `<p class="meta"><strong>${esc(tr.cardRole)}:</strong> ${esc(roleText)}</p>` : '',
    descText ? `<p class="meta">${esc(descText)}</p>` : '',
    yearText ? `<p class="meta"><strong>${esc(tr.founded)}:</strong> ${esc(String(yearText))}</p>` : '',
  ].filter(Boolean).join('');

  el.innerHTML = `
    <div style="padding:14px">
      <h2>${esc(a.name)}</h2>
      <div class="meta">${flag} ${esc(a.country)} · ${esc(tr.cats[a.category] || a.category)} · ${rels.length} ${tr.relationsN}</div>
      <div class="inspector-links">${websiteRow}${linkedinRow}${nexusRow}${hubRow}</div>
      ${detailBits}
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
  if (!byId.has(id) && !isChallengeId(id) && !isPolicyId(id)) return;
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
  } else if (isPolicyId(id)) {
    const row = policiesById.get(id);
    const g = row ? policyGeo(row) : null;
    if (g && map) {
      const opts = { center: [g.lng, g.lat], zoom: Math.max(map.getZoom(), 5.2) };
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
  hidePinTooltip();
  syncPinPopup();
  if (fullRender) renderAll(false);
}

function cardField(a, key) {
  return a.card?.[key] ?? a[key];
}

function renderCards(list) {
  const grid = $('#actor-grid');
  const tr = t();
  if (!list.length) {
    grid.innerHTML = `<div class="empty-grid">${tr.noResults}</div>`;
    return;
  }
  grid.innerHTML = list.map((a) => {
    const cc = actorCountryCode(a);
    const flag = cc ? COUNTRY_META[cc].flag : '🌎';
    const relN = degree.get(a.id) || 0;
    const catLabel = tr.cats[a.category] || a.category;
    const catColor = CAT_COLOR[a.category] || CAT_COLOR.default;
    const slug = a.nexus?.card_slug;
    const role = redactPublicStreetText(a, cardField(a, 'ecosystem_role'));
    const desc = redactPublicStreetText(a, cardField(a, 'description'));
    const year = cardField(a, 'founding_year');
    const place = visiblePlaceParts(a);
    const locParts = [place.city, place.country].filter(Boolean);
    let locLine = locParts.length ? locParts.map((x) => esc(x)).join(', ') : esc(a.country || '');
    if (a.geo?.hq_abroad) {
      locLine += ` <span class="hq-abroad-chip" title="${esc(tr.hqAbroadHint)}">${esc(tr.hqAbroad)}</span>`;
    }
    const website = a.website
      ? `<a class="link-btn" href="${esc(a.website.startsWith('http') ? a.website : `https://${a.website}`)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${tr.website}</a>`
      : '';
    const linkedin = a.linkedin
      ? `<a class="li-btn" href="${esc(a.linkedin)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${tr.linkedin}</a>`
      : '';
    const mapBtn = `<a class="map-btn" href="?actor=${esc(a.id)}" onclick="event.stopPropagation()">${tr.mapLink}</a>`;
    const nexus = slug
      ? `<a class="nexus-btn" href="/s/${esc(slug)}/" target="_blank" rel="noopener" onclick="event.stopPropagation()">${tr.nexusCard}</a>`
      : (a.category === 'startup'
        ? `<span class="pending-chip">${tr.nexusPending}</span>`
        : '');
    const hubSlug = a.nexus?.hub_slug;
    const hubLink = hubSlug
      ? `<a class="nexus-btn" href="/hubs/${esc(hubSlug)}/" target="_blank" rel="noopener" onclick="event.stopPropagation()">${tr.hubPage}</a>`
      : '';
    const yearBadge = year
      ? `<span class="badge badge-founded">${esc(tr.founded)} ${esc(String(year))}</span>`
      : '';
    const roleBlock = role ? `<p class="ac-role">${esc(role)}</p>` : '';
    const descBlock = desc ? `<p class="ac-desc">${esc(desc)}</p>` : '';
    return `
      <article class="actor-card${selected === a.id ? ' selected' : ''}" data-id="${esc(a.id)}" tabindex="0">
        <div class="ac-top">
          <div class="ac-icon" style="background:linear-gradient(135deg, ${catColor}, var(--deep-blue));">${esc(a.name.slice(0, 2).toUpperCase())}</div>
          <div class="ac-head">
            <div class="ac-name">${esc(a.name)}</div>
            <div class="ac-meta">${flag} ${locLine} · ${relN} ${tr.relationsN}</div>
          </div>
        </div>
        ${roleBlock}
        ${descBlock}
        <div class="ac-badges"><span class="badge">${esc(catLabel)}</span>${yearBadge}</div>
        <div class="ac-links">${[website, linkedin, mapBtn, nexus, hubLink].filter(Boolean).join('') || ''}</div>
      </article>`;
  }).join('');

  grid.querySelectorAll('.actor-card').forEach((card) => {
    const open = () => selectActor(card.dataset.id);
    card.addEventListener('click', open);
    card.addEventListener('keydown', (e) => { if (e.key === 'Enter') open(); });
  });
}

function renderGeoUnknownPanel(ids) {
  const el = $('#geo-unknown-panel');
  if (!el) return;
  const tr = t();
  const list = actors.filter((a) => ids.has(a.id) && isLocationUnknown(a));
  if (!list.length) {
    el.classList.add('hidden');
    el.innerHTML = '';
    return;
  }
  el.classList.remove('hidden');
  const byCountry = new Map();
  list.forEach((a) => {
    byCountry.set(a.country, (byCountry.get(a.country) || 0) + 1);
  });
  const summary = [...byCountry.entries()].map(([c, n]) => `${esc(c)} (${n})`).join(' · ');
  el.innerHTML = `
    <summary>${esc(tr.geoUnknownTitle)} (${list.length})</summary>
    <p class="geo-unknown-hint">${esc(tr.geoUnknownHint)}</p>
    <p class="geo-unknown-summary">${summary}</p>
    <ul class="geo-unknown-list">${list.slice(0, 40).map((a) =>
    `<li><button type="button" class="geo-unknown-item" data-id="${esc(a.id)}">${esc(a.name)}</button></li>`,
  ).join('')}${list.length > 40 ? `<li>… +${list.length - 40}</li>` : ''}</ul>`;
  el.querySelectorAll('.geo-unknown-item').forEach((btn) => {
    btn.addEventListener('click', () => selectActor(btn.dataset.id));
  });
}

function updateStats(ids) {
  $('#stat-actors').textContent = String(actors.length);
  $('#stat-relations').textContent = String(publicGraphRelations().length);
  $('#stat-visible').textContent = String(ids.size);
  $('#result-meta').textContent = `${ids.size} / ${actors.length}`;
}

function renderAll(rebuildLayout = true) {
  if (viewMode === 'story') {
    renderStoryChapter();
    return;
  }
  if (viewMode === 'journey') {
    journeyController?.refresh();
    return;
  }
  const ids = visibleActorIds();
  const rels = visibleRelations(ids);
  updateStats(ids);
  if (viewMode === 'cards') {
    renderCards(filteredActors());
    return;
  }
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
  const chNow = storyConfig.chapters[storyChapter];
  const storyCountries = chNow?.map?.countries || [];
  if (storyCountries.length > 1) {
    const row = document.createElement('div');
    row.className = 'chip-row story-country-row';
    row.style.marginBottom = '8px';
    const allLabel = lang === 'EN' ? 'All in chapter' : 'Todo el capítulo';
    const chips = [['', allLabel], ...storyCountries.map((cc) => [cc, COUNTRY_META[cc]?.flag ? `${COUNTRY_META[cc].flag} ${cc}` : cc])];
    chips.forEach(([cc, label]) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = `chip sm ${(cc === '' && !storyFocusCountry) || storyFocusCountry === cc ? 'on' : ''}`;
      b.textContent = label;
      b.addEventListener('click', () => {
        storyFocusCountry = cc || null;
        renderStoryRail();
        renderStoryChapter();
      });
      row.appendChild(b);
    });
    rail.appendChild(row);
  } else {
    storyFocusCountry = storyCountries[0] || storyFocusCountry;
  }
  storyConfig.chapters.forEach((ch, idx) => {
    const step = document.createElement('div');
    step.className = `story-step${idx === storyChapter ? ' on' : ''}`;
    step.innerHTML = `<h3>${esc(lang === 'EN' ? ch.title.en : ch.title.es)}</h3><p>${esc(lang === 'EN' ? ch.blurb.en : ch.blurb.es)}</p>`;
    step.addEventListener('click', () => {
      storyChapter = idx;
      constellationId = null;
      constellationCloseup = false;
      const codes = ch.map?.countries || [];
      storyFocusCountry = codes.length === 1 ? codes[0] : null;
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

  const counts = computeChapterEdgeCounts(storyConfig, relations, byId, policyRelations, {
    policiesById,
    dataRelations,
    storyFocusCountry,
  });
  window.__storyEdgeCounts = counts;
  const gaps = document.createElement('div');
  gaps.className = 'story-gaps';
  gaps.innerHTML = `<strong>${esc(tr.storyCounts || 'Edge counts')}</strong><br/>${counts.map((c) =>
    `${esc(c.title)}: ${c.real} real${c.suggested ? `, ${c.suggested} suggested` : ''}`,
  ).join('<br/>')}`;
  rail.appendChild(gaps);
  rail.appendChild(renderSourcedJourneyList());
}

function renderSourcedJourneyList() {
  const tr = t();
  const box = document.createElement('div');
  box.className = 'story-sourced';
  const rows = sourcedJourneyStartups({ actors, relations, storyConfig });
  if (!rows.length) {
    box.innerHTML = `<strong>${esc(tr.storySourcedTitle)}</strong><p class="meta">${esc(tr.storySourcedEmpty)}</p>`;
    return box;
  }
  const l = lang === 'EN' ? 'en' : 'es';
  box.innerHTML = `<strong>${esc(tr.storySourcedTitle)}</strong><p class="meta">${esc(tr.storySourcedHint)}</p><ul>${rows.map((row) => {
    const ch = String(row.challengeId).replace(/^challenge:/, '');
    const href = `?view=journey&challenge=${encodeURIComponent(ch)}&startup=${encodeURIComponent(row.id)}`;
    const clabel = storyConfig.challenges[row.challengeId]?.label?.[l] || '';
    return `<li><a href="${esc(href)}">${esc(row.name)}</a> <span class="meta">${esc(clabel)} · ${row.edgeCount}</span></li>`;
  }).join('')}</ul>`;
  return box;
}

function renderStoryChapter() {
  if (!storyConfig) return;
  storyScene = chapterScene(storyChapter, storyConfig, relations, byId, {
    constellationId,
    closeup: constellationCloseup,
    policyRelations,
    policiesById,
    dataRelations,
    storyFocusCountry,
  });
  const current = computeChapterEdgeCounts(storyConfig, relations, byId, policyRelations, {
    policiesById,
    dataRelations,
    storyFocusCountry,
  })[storyChapter];
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

function markReady() {
  if (!window.__ecoReady) {
    window.__ecoReady = true;
    document.body.dataset.ecoReady = '1';
  }
}

function applyDemoState() {
  const state = bootParams.get('state');
  const bootCountry = normalizeCountryParam(bootParams.get('country'));
  if (bootCountry) {
    activeCountry = bootCountry;
  }
  if (bootParams.get('view') === 'cards') {
    document.querySelector('[data-view-tab="cards"]')?.click();
  }
  if (bootCountry) {
    buildFilterChips();
    renderAll(false);
  }
  const bootView = bootParams.get('view');
  if (bootView === 'journey' || (!bootView && bootParams.get('challenge') && state !== 'story')) {
    document.querySelector('[data-view-tab="journey"]')?.click();
  }
  if (!state) return;
  if (state === 'filters') {
    activeCountry = normalizeCountryParam(bootParams.get('country')) || 'PE';
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
    storyChapter = Math.min(5, Math.max(0, parseInt(bootParams.get('chapter') || '0', 10)));
    constellationId = bootParams.get('constellation') || null;
    constellationCloseup = bootParams.get('closeup') === '1';
    const tab = document.querySelector('[data-view-tab="story"]');
    if (tab) tab.click();
  }
}

async function loadData() {
  const [a, r, story, pol, polRels, dataRels, cross] = await Promise.all([
    fetch('data/actors.json').then((res) => res.json()),
    fetch('data/relations.json').then((res) => res.json()),
    fetch('data/story-chapters.json').then((res) => res.json()),
    fetch('data/policies.json').then((res) => res.json()),
    fetch('data/policy_relations.json').then((res) => res.json()),
    fetch('data/data_relations.json').then((res) => res.json()),
    fetch('data/nexus-crosslinks.json').then((res) => (res.ok ? res.json() : null)).catch(() => null),
  ]);
  nexusCrosslinks = cross;
  storyConfig = story;
  policies = pol;
  policiesById = new Map(pol.map((p) => [p.id, p]));
  policyRelations = polRels;
  dataRelations = dataRels;
  actors = a;
  relations = r;
  byId = new Map(actors.map((x) => [x.id, x]));
  computeDegrees();
  activeRelTypes = new Set(publicGraphRelations().map((x) => x.type));
  buildFilterChips();
  journeyController = mountJourney({
    getActors: () => actors,
    getRelations: () => relations,
    getDataRelations: () => dataRelations,
    getStory: () => storyConfig,
    getLang: () => lang,
    t,
  });
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
