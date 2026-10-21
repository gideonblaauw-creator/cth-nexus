/**
 * Static story-direction mockups — loads real ecosystem JSON, no invented entities.
 */
import Graph from 'graphology';
import Sigma from 'sigma';
import {
  chapterScene,
  computeChapterEdgeCounts,
  isChallengeId,
  isPolicyId,
  linkedActorsForChallenge,
} from '../../../story.mjs';
import { geoXY } from '../../../geo-utils.mjs';

export const DEFAULT_CHALLENGE = 'challenge:PE-2-agua';
export const DATA_BASE = '../../../data';

const CAT_COLOR = {
  startup: '#e87722',
  academia: '#0c498a',
  funder: '#669348',
  accelerator: '#69b5fa',
  government: '#264653',
  international: '#2a9d8f',
  corporate: '#64748b',
  default: '#94a3b8',
};

const EDGE_COLOR = {
  works_on_challenge: '#0c498a',
  suggested: '#ea580c',
  partner: '#669348',
  hosts: '#69b5fa',
  incubated: '#9dc384',
  cofunds: '#669348',
  default: '#cbd5e1',
};

let bundle = null;
let mapInstance = null;
let sigmaInstance = null;
let graph = null;
let state = {
  chapterIndex: 0,
  challengeId: DEFAULT_CHALLENGE,
  selectedId: 'pe-uqhu',
  constellationId: 'agua-uqhu',
  lang: 'es',
};

export async function loadBundle(base = DATA_BASE) {
  const [config, actors, relations, policyRelations, dataRelations] = await Promise.all([
    fetch(`${base}/story-chapters.json`).then((r) => r.json()),
    fetch(`${base}/actors.json`).then((r) => r.json()),
    fetch(`${base}/relations.json`).then((r) => r.json()),
    fetch(`${base}/policy_relations.json`).then((r) => r.json()).catch(() => []),
    fetch(`${base}/data_relations.json`).then((r) => r.json()).catch(() => []),
  ]);
  const byId = new Map(actors.map((a) => [a.id, a]));
  const policiesById = new Map();
  try {
    const policies = await fetch(`${base}/policies.json`).then((r) => r.json());
    policies.forEach((p) => policiesById.set(p.id, p));
  } catch {
    /* optional */
  }
  bundle = {
    config,
    actors,
    relations,
    policyRelations,
    dataRelations,
    byId,
    policiesById,
  };
  return bundle;
}

function t(obj) {
  if (!obj) return '';
  return obj[state.lang] || obj.en || obj.es || '';
}

function challengeLabel(id) {
  return t(bundle.config.challenges[id]?.label) || id;
}

function nameFor(id) {
  if (id.startsWith('challenge:')) return challengeLabel(id);
  if (id.startsWith('dataset:')) return t(bundle.config.datasets[id]?.label) || id;
  return bundle.byId.get(id)?.name || id;
}

function nodeColor(id) {
  if (id.startsWith('challenge:')) return '#2a9d8f';
  if (id === state.selectedId) return '#e87722';
  const a = bundle.byId.get(id);
  return CAT_COLOR[a?.category] || CAT_COLOR.default;
}

function hasGeo(a) {
  return a?.geo?.lat != null && a?.geo?.lng != null;
}

function sceneForCurrentChapter() {
  const { config, relations, byId, policyRelations, dataRelations, policiesById } = bundle;
  const chapter = config.chapters[state.chapterIndex];
  const opts = {
    constellationId: chapter?.id === 'partnerships' ? state.constellationId : null,
    policyRelations,
    policiesById,
    dataRelations,
    storyFocusChallenge: state.challengeId,
  };
  return chapterScene(state.chapterIndex, config, relations, byId, opts);
}

function edgeCounts() {
  return computeChapterEdgeCounts(bundle.config, bundle.relations, bundle.byId, bundle.policyRelations, {
    policiesById: bundle.policiesById,
    dataRelations: bundle.dataRelations,
    storyFocusChallenge: state.challengeId,
  });
}

function relationsForInspector() {
  const scene = sceneForCurrentChapter();
  const ids = scene.nodeIds || new Set();
  const rels = [];
  const push = (r, suggested = false) => {
    if (!ids.has(r.source) && !ids.has(r.target)) return;
    if (r.source !== state.selectedId && r.target !== state.selectedId) return;
    rels.push({ ...r, suggested });
  };
  (scene.realRels || []).forEach((r) => push(r, false));
  (scene.suggested || []).forEach((r) => push({ ...r, type: r.type || 'suggested' }, true));
  const seen = new Set();
  return rels.filter((r) => {
    const k = `${r.source}|${r.type}|${r.target}|${r.suggested}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  }).slice(0, 24);
}

function kpiSnapshot() {
  const scene = sceneForCurrentChapter();
  const linked = linkedActorsForChallenge(state.challengeId, bundle.relations);
  const nodeCount = scene.nodeIds?.size ?? 0;
  const edgeCount = (scene.realRels?.length ?? 0) + (scene.suggested?.length ?? 0);
  let datasets = 0;
  if (bundle.config.datasets) {
    datasets = Object.keys(bundle.config.datasets).length;
  }
  const counts = edgeCounts();
  const cap = counts.find((c) => c.chapter === 'capital')?.total ?? 0;
  return {
    actors: nodeCount,
    relations: edgeCount,
    datasets,
    capital: cap,
    linkedStartups: [...(linked || [])].filter((id) => bundle.byId.get(id)?.category === 'startup').length,
  };
}

function destroyGraph() {
  if (sigmaInstance) {
    sigmaInstance.kill();
    sigmaInstance = null;
  }
  graph = null;
}

function buildGraphFromScene(scene, container) {
  destroyGraph();
  graph = new Graph({ multi: true, type: 'directed' });
  const idSet = scene.nodeIds || new Set();
  const preset = scene.presetPositions;

  const addNode = (id, attrs) => {
    if (graph.hasNode(id)) return;
    graph.addNode(id, attrs);
  };

  idSet.forEach((id) => {
    if (isChallengeId(id) || isPolicyId(id)) return;
    const a = bundle.byId.get(id);
    if (!a) return;
    let pos = geoXY(a);
    if (preset?.has(id)) pos = preset.get(id).position || preset.get(id);
    addNode(id, {
      label: a.name.length > 36 ? `${a.name.slice(0, 35)}…` : a.name,
      x: pos.x,
      y: pos.y,
      size: id === state.selectedId ? 14 : 9,
      color: nodeColor(id),
    });
  });

  (scene.virtualNodes || []).forEach((vn) => {
    const pos = preset?.get(vn.id)?.position
      || (vn.geo ? geoXY({ geo: vn.geo }) : { x: 0, y: 0 });
    addNode(vn.id, {
      label: vn.label || nameFor(vn.id),
      x: pos.x,
      y: pos.y,
      size: vn.size || 12,
      color: vn.color || nodeColor(vn.id),
    });
  });

  (scene.realRels || []).forEach((r, i) => {
    if (!graph.hasNode(r.source) || !graph.hasNode(r.target)) return;
    const key = r.id || `e-${i}-${r.source}-${r.target}`;
    try {
      graph.addEdgeWithKey(key, r.source, r.target, {
        color: EDGE_COLOR[r.type] || EDGE_COLOR.default,
        size: 2,
      });
    } catch {
      /* duplicate */
    }
  });

  (scene.suggested || []).forEach((r, i) => {
    if (!graph.hasNode(r.source) || !graph.hasNode(r.target)) return;
    const key = r.id || `s-${i}-${r.source}-${r.target}`;
    try {
      graph.addEdgeWithKey(key, r.source, r.target, {
        color: EDGE_COLOR.suggested,
        size: 1.5,
        type: 'line',
      });
    } catch {
      /* duplicate */
    }
  });

  sigmaInstance = new Sigma(graph, container, {
    renderLabels: graph.order < 80,
    labelDensity: 0.08,
    enableEdgeEvents: true,
    defaultEdgeType: 'arrow',
    allowInvalidContainer: true,
  });
  sigmaInstance.on('clickNode', ({ node }) => {
    state.selectedId = node;
    refreshAll();
  });
}

const mapByContainer = new WeakMap();

function initMap(container, scene) {
  if (!container || !window.maplibregl) return;
  const mapCfg = scene?.map || bundle.config.chapters[state.chapterIndex]?.map;
  const center = mapCfg?.center || [-76.2, -12.8];
  const zoom = mapCfg?.zoom || 5;
  let map = mapByContainer.get(container);
  if (!map) {
    map = new maplibregl.Map({
      container,
      style: 'https://tiles.openfreemap.org/styles/liberty',
      center,
      zoom,
      attributionControl: true,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    mapByContainer.set(container, map);
    map.on('load', () => updateMapLayers(map, scene));
  } else {
    map.jumpTo({ center, zoom });
    if (map.isStyleLoaded()) updateMapLayers(map, scene);
    else map.once('load', () => updateMapLayers(map, scene));
  }
  mapInstance = map;
}

function updateMapLayers(map, scene) {
  if (!map) return;
  const ids = scene.nodeIds || new Set();
  const features = [];
  ids.forEach((id) => {
    if (id.startsWith('challenge:')) {
      const ch = bundle.config.challenges[id];
      if (ch?.geo) {
        features.push({
          type: 'Feature',
          properties: { id, sel: id === state.selectedId ? 1 : 0, color: '#2a9d8f' },
          geometry: { type: 'Point', coordinates: [ch.geo.lng, ch.geo.lat] },
        });
      }
      return;
    }
    const a = bundle.byId.get(id);
    if (!hasGeo(a)) return;
    features.push({
      type: 'Feature',
      properties: { id, sel: id === state.selectedId ? 1 : 0, color: nodeColor(id) },
      geometry: { type: 'Point', coordinates: [a.geo.lng, a.geo.lat] },
    });
  });
  const data = { type: 'FeatureCollection', features };
  const src = map.getSource('mock-actors');
  if (src) src.setData(data);
  else {
    map.addSource('mock-actors', { type: 'geojson', data });
    map.addLayer({
      id: 'mock-points',
      type: 'circle',
      source: 'mock-actors',
      paint: {
        'circle-radius': ['case', ['==', ['get', 'sel'], 1], 10, 7],
        'circle-color': ['get', 'color'],
        'circle-stroke-width': 2,
        'circle-stroke-color': '#fff',
      },
    });
  }
}

function renderInspector(el) {
  if (!el) return;
  const actor = bundle.byId.get(state.selectedId);
  if (!actor) {
    el.innerHTML = '<p class="meta">Selecciona un actor en el mapa o la red.</p>';
    return;
  }
  const rels = relationsForInspector();
  const role = actor.card?.ecosystem_role || actor.category || '';
  const desc = actor.card?.description || '';
  el.innerHTML = `
    <h2>${actor.name}</h2>
    <p class="meta">${role} · ${actor.city || ''} · ${actor.country || ''}</p>
    <p class="meta">${desc.slice(0, 280)}${desc.length > 280 ? '…' : ''}</p>
    <div class="section"><h3>Relaciones (${rels.length})</h3>
      <div class="rel-grid">${rels.map((r) => {
    const other = r.source === state.selectedId ? r.target : r.source;
    return `<div class="rel-row${r.suggested ? ' suggested' : ''}" data-id="${other}">
      <span class="rtype">${r.type}</span> → ${nameFor(other)}
    </div>`;
  }).join('') || '<span class="meta">Sin relaciones visibles en este capítulo.</span>'}
      </div>
    </div>`;
  el.querySelectorAll('.rel-row[data-id]').forEach((row) => {
    row.addEventListener('click', () => {
      state.selectedId = row.dataset.id;
      refreshAll();
    });
  });
}

function renderRail(el) {
  if (!el) return;
  const counts = edgeCounts();
  el.innerHTML = bundle.config.chapters.map((ch, i) => {
    const c = counts[i];
    const pending = ch.pending ? ' · <span style="color:#ea580c">pendiente</span>' : '';
    return `<div class="story-step${i === state.chapterIndex ? ' on' : ''}" data-idx="${i}">
      <h3>${t(ch.title)}</h3>
      <p>${t(ch.blurb)}</p>
      <div class="edge-count">${c?.total ?? 0} relaciones${pending}</div>
    </div>`;
  }).join('');
  el.querySelectorAll('.story-step').forEach((step) => {
    step.addEventListener('click', () => {
      state.chapterIndex = Number(step.dataset.idx);
      if (bundle.config.chapters[state.chapterIndex]?.id === 'partnerships') {
        const specs = bundle.config.constellations.filter((s) => s.challengeId === state.challengeId);
        state.constellationId = specs[0]?.id || state.constellationId;
      }
      refreshAll();
    });
  });
}

function renderTimeline(el) {
  if (!el) return;
  el.innerHTML = bundle.config.chapters.map((ch, i) => `
    <button type="button" class="timeline-step${i === state.chapterIndex ? ' on' : ''}" data-idx="${i}">
      <span class="num">${i + 1}</span>
      <span class="ttl">${t(ch.title).replace(/^\d+\s·\s*/, '')}</span>
    </button>`).join('');
  el.querySelectorAll('.timeline-step').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.chapterIndex = Number(btn.dataset.idx);
      refreshAll();
    });
  });
}

function renderConstellationPills(el) {
  if (!el) return;
  const specs = bundle.config.constellations.filter((s) => s.challengeId === state.challengeId);
  el.innerHTML = specs.map((s) => {
    const startup = nameFor(s.startupId);
    return `<button type="button" class="${s.id === state.constellationId ? 'on' : ''}" data-id="${s.id}">${startup}</button>`;
  }).join('');
  el.querySelectorAll('button').forEach((b) => {
    b.addEventListener('click', () => {
      state.constellationId = b.dataset.id;
      state.selectedId = specs.find((s) => s.id === b.dataset.id)?.startupId || state.selectedId;
      refreshAll();
    });
  });
}

function renderKpis(el) {
  if (!el) return;
  const k = kpiSnapshot();
  el.innerHTML = `
    <div class="kpi-tile"><div class="kpi-n">${k.actors}</div><div class="kpi-l">Actores visibles</div><div class="kpi-sub">${k.linkedStartups} startups en reto</div></div>
    <div class="kpi-tile"><div class="kpi-n">${k.relations}</div><div class="kpi-l">Relaciones (capítulo)</div></div>
    <div class="kpi-tile"><div class="kpi-n">${k.datasets}</div><div class="kpi-l">Datasets catalogados</div><div class="kpi-sub">MINAM pendiente curación</div></div>
    <div class="kpi-tile"><div class="kpi-n">${k.capital}</div><div class="kpi-l">Vínculos capital</div></div>`;
}

function renderRelationCards(el) {
  if (!el) return;
  const scene = sceneForCurrentChapter();
  const edges = [
    ...(scene.realRels || []).map((e) => ({ ...e, suggested: false })),
    ...(scene.suggested || []).map((e) => ({ ...e, suggested: true, type: e.type || 'suggested' })),
  ].slice(0, 12);
  el.innerHTML = edges.map((e) => `
    <article class="rel-card${e.suggested ? ' suggested' : ''}">
      <h4>${nameFor(e.source)} → ${nameFor(e.target)}</h4>
      <p><strong>${e.type || 'suggested'}</strong>${e.suggested ? ' · Suggested (no verificado)' : ''}</p>
    </article>`).join('') || '<p class="meta">Sin relaciones en este capítulo.</p>';
}

function renderBanner(el) {
  if (!el) return;
  el.textContent = t(bundle.config.banner);
}

let challengeSelectWired = false;

function wireChallengeSelect(select) {
  if (!select) return;
  select.innerHTML = Object.entries(bundle.config.challenges).map(([id]) =>
    `<option value="${id}"${id === state.challengeId ? ' selected' : ''}>${challengeLabel(id)}</option>`).join('');
  if (challengeSelectWired) return;
  challengeSelectWired = true;
  select.addEventListener('change', () => {
    state.challengeId = select.value;
    const specs = bundle.config.constellations.filter((s) => s.challengeId === state.challengeId);
    state.constellationId = specs[0]?.id || 'agua-uqhu';
    refreshAll();
  });
}

const hooks = {};

export function registerMockHooks(id, fn) {
  hooks[id] = fn;
}

function refreshAll() {
  const scene = sceneForCurrentChapter();
  document.querySelectorAll('[data-mock-map]').forEach((el) => initMap(el, scene));
  document.querySelectorAll('[data-mock-graph]').forEach((el) => buildGraphFromScene(scene, el));
  document.querySelectorAll('[data-mock-inspector]').forEach((el) => renderInspector(el));
  document.querySelectorAll('[data-mock-rail]').forEach((el) => renderRail(el));
  document.querySelectorAll('[data-mock-timeline]').forEach((el) => renderTimeline(el));
  document.querySelectorAll('[data-mock-kpis]').forEach((el) => renderKpis(el));
  document.querySelectorAll('[data-mock-rel-cards]').forEach((el) => renderRelationCards(el));
  document.querySelectorAll('[data-mock-constellations]').forEach((el) => renderConstellationPills(el));
  document.querySelectorAll('[data-mock-banner]').forEach((el) => renderBanner(el));
  const ch = bundle.config.chapters[state.chapterIndex];
  document.querySelectorAll('[data-mock-constellations]').forEach((el) => {
    el.classList.toggle('hidden', ch?.id !== 'partnerships');
    if (ch?.id === 'partnerships') renderConstellationPills(el);
  });
  Object.values(hooks).forEach((fn) => fn(state, bundle, scene));
}

export async function bootMockPage(options = {}) {
  const { direction = 'a', chapterIndex = 0, selectedId = 'pe-uqhu' } = options;
  state.chapterIndex = chapterIndex;
  if (selectedId) state.selectedId = selectedId;
  if (!state.constellationId) state.constellationId = 'agua-uqhu';
  if (!bundle) await loadBundle();
  document.body.dataset.mockDirection = direction;
  const banner = document.querySelector('[data-mock-banner]');
  if (banner) renderBanner(banner);
  wireChallengeSelect(document.getElementById('mock-challenge-select'));
  refreshAll();
  window.__mockRefresh = refreshAll;
}

/** Featured startups present in bundle for Water + Bosques constellations */
export function featuredStartupIds() {
  return ['pe-uqhu', 'pe-yakufil', 'pe-yakusmart'].filter((id) => bundle?.byId.has(id));
}

export function getState() {
  return { ...state };
}

export function getBundle() {
  return bundle;
}
