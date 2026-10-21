import Graph from 'graphology';
import Sigma from 'sigma';
import { hasPlottableGeo, geoXY } from '../../geo-utils.mjs';
import {
  buildPeruWaterScene,
  buildChapterReports,
  edgeSourceList,
  isChallengeId,
  isPolicyId,
  isDatasetId,
  normalizeActorRelation,
} from './peru-water-thread.mjs';
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const MAP_FONT_STACK = ['Noto Sans Regular'];

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
  hub: '#669348',
  default: '#5a7088',
};

const EDGE_COLOR = {
  works_on_challenge: '#2a9d8f',
  hosts: '#669348',
  cofunds: '#264653',
  funds_layer: '#0c498a',
  partner: '#e87722',
  incubated: '#e87722',
  issues_policy: '#6b4c9a',
  addresses_challenge: '#2a9d8f',
  funding: '#264653',
  program_participation: '#6b4c9a',
  partnership: '#e87722',
  default: '#94a3b8',
};

const I18N = {
  ES: {
    title: 'Peru Water Challenge — historia guiada',
    sub: 'Hilo único challenge:PE-2-agua · seis capítulos · datos reales del repo.',
    actors: 'Actores',
    verified: 'Verificadas',
    suggested: 'Suggested',
    map: 'Mapa Perú',
    network: 'Red del capítulo',
    gapsTitle: 'Brechas (gaps)',
    sourcesTitle: 'Fuentes — aristas verificadas',
    noSources: 'Sin URL de fuente en este capítulo.',
    banner: 'Modo guiado MOCK · Líneas punteadas = Suggested (no verificadas)',
  },
  EN: {
    title: 'Peru Water Challenge — guided story',
    sub: 'Single thread challenge:PE-2-agua · six chapters · real repo data only.',
    actors: 'Actors',
    verified: 'Verified',
    suggested: 'Suggested',
    map: 'Peru map',
    network: 'Chapter network',
    gapsTitle: 'Gaps',
    sourcesTitle: 'Sources — verified edges',
    noSources: 'No source URLs in this chapter.',
    banner: 'MOCK guided mode · Dashed lines = Suggested (unverified)',
  },
};

let lang = 'ES';
let storyConfig;
let actors;
let relations;
let policyRelations;
let dataRelations;
let byId;
let policiesById;
let actorRelationsNorm;
let storyChapter = 0;
let storyScene;
let map;
let mapReady = false;
let sigma;
let graph;
let suggestedEdges = [];
let fa2Assign = null;

const bootParams = new URLSearchParams(window.location.search);
storyChapter = Math.min(5, Math.max(0, parseInt(bootParams.get('chapter') || '0', 10)));

const $ = (sel) => document.querySelector(sel);
const t = () => I18N[lang];

function esc(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function nodeColor(id) {
  if (isChallengeId(id)) return '#2a9d8f';
  const a = byId.get(id);
  return CAT_COLOR[a?.category] || CAT_COLOR.default;
}

function initLang() {
  document.querySelectorAll('[data-lang-btn]').forEach((btn) => {
    btn.addEventListener('click', () => {
      lang = btn.dataset.langBtn;
      document.querySelectorAll('[data-lang-btn]').forEach((b) => b.classList.toggle('active', b.dataset.langBtn === lang));
      document.querySelectorAll('[data-i18n]').forEach((el) => {
        const key = el.dataset.i18n;
        if (I18N[lang][key]) el.textContent = I18N[lang][key];
      });
      renderStoryRail();
      renderChapter();
    });
  });
}

function dataBundle() {
  return {
    storyConfig,
    relations,
    policyRelations,
    dataRelations,
    actorRelationsNorm,
    byId,
    policiesById,
  };
}

function renderStoryRail() {
  const rail = $('#story-rail');
  const tr = t();
  $('#story-banner').innerHTML = `${esc(tr.banner)} · <span class="suggested-tag">Suggested</span>`;
  rail.innerHTML = '';
  storyConfig.chapters.forEach((ch, idx) => {
    const step = document.createElement('div');
    step.className = `story-step${idx === storyChapter ? ' on' : ''}`;
    step.innerHTML = `<h3>${esc(lang === 'EN' ? ch.title.en : ch.title.es)}</h3><p>${esc(lang === 'EN' ? ch.blurb.en : ch.blurb.es)}</p>`;
    step.addEventListener('click', () => {
      storyChapter = idx;
      const url = new URL(window.location.href);
      url.searchParams.set('chapter', String(idx));
      window.history.replaceState({}, '', url);
      renderStoryRail();
      renderChapter();
    });
    rail.appendChild(step);
  });
}

function runForceLayout(g, iterations) {
  const nodes = g.nodes();
  const pos = new Map(nodes.map((n) => [n, { x: (Math.random() - 0.5) * 100, y: (Math.random() - 0.5) * 100 }]));
  const cx = 0;
  const cy = 0;
  for (let it = 0; it < iterations; it += 1) {
    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i];
        const b = nodes[j];
        const pa = pos.get(a);
        const pb = pos.get(b);
        let dx = pb.x - pa.x;
        let dy = pb.y - pa.y;
        let d = Math.sqrt(dx * dx + dy * dy) || 0.01;
        const rep = 800 / (d * d);
        dx = (dx / d) * rep;
        dy = (dy / d) * rep;
        pa.x -= dx;
        pa.y -= dy;
        pb.x += dx;
        pb.y += dy;
      }
    }
    g.forEachEdge((edge) => {
      const s = g.source(edge);
      const tId = g.target(edge);
      const ps = pos.get(s);
      const pt = pos.get(tId);
      const dx = pt.x - ps.x;
      const dy = pt.y - ps.y;
      ps.x += dx * 0.006;
      ps.y += dy * 0.006;
      pt.x -= dx * 0.006;
      pt.y -= dy * 0.006;
    });
    nodes.forEach((n) => {
      const p = pos.get(n);
      p.x += (cx - p.x) * 0.02;
      p.y += (cy - p.y) * 0.02;
      g.setNodeAttribute(n, 'x', p.x);
      g.setNodeAttribute(n, 'y', p.y);
    });
  }
}

function buildGraph(scene) {
  const { nodeIds, realRels, virtualNodes, presetPositions, storyLayout } = scene;
  suggestedEdges = scene.suggested || [];

  if (sigma) {
    sigma.kill();
    sigma = null;
  }
  graph = new Graph({ multi: true, type: 'directed' });

  const addNode = (id, attrs) => {
    if (graph.hasNode(id)) return;
    graph.addNode(id, attrs);
  };

  nodeIds.forEach((id) => {
    if (isChallengeId(id) || isPolicyId(id) || isDatasetId(id)) return;
    const a = byId.get(id);
    if (!a) return;
    let pos = geoXY(a);
    if (presetPositions?.get(id)) {
      pos = presetPositions.get(id).position || presetPositions.get(id);
    }
    addNode(id, {
      label: a.name.length > 26 ? `${a.name.slice(0, 24)}…` : a.name,
      x: pos.x,
      y: pos.y,
      size: 10,
      color: nodeColor(id),
    });
  });

  (virtualNodes || []).forEach((vn) => {
    if (!nodeIds.has(vn.id)) return;
    const pos = presetPositions?.get(vn.id)?.position
      || (vn.geo ? geoXY({ geo: vn.geo }) : { x: 0, y: 0 });
    const label = lang === 'EN'
      ? (storyConfig.challenges[vn.id]?.label?.en || vn.label)
      : (storyConfig.challenges[vn.id]?.label?.es || vn.label);
    addNode(vn.id, {
      label: label?.length > 26 ? `${label.slice(0, 24)}…` : (label || vn.id),
      x: pos.x,
      y: pos.y,
      size: vn.size || 12,
      color: vn.color || '#2a9d8f',
    });
  });

  realRels.filter((r) => !r.suggested).forEach((r, i) => {
    if (!graph.hasNode(r.source) || !graph.hasNode(r.target)) return;
    const key = r.id || `e-${i}`;
    try {
      graph.addEdgeWithKey(key, r.source, r.target, {
        type: r.type,
        color: EDGE_COLOR[r.type] || EDGE_COLOR.default,
        size: 2,
      });
    } catch {
      /* parallel */
    }
  });

  const runLayout = !storyLayout && !presetPositions && graph.order > 1;
  if (runLayout) {
    if (fa2Assign) {
      fa2Assign(graph, { iterations: 80, settings: { gravity: 0.9, scalingRatio: 10 } });
    } else {
      runForceLayout(graph, 70);
    }
  }

  sigma = new Sigma(graph, $('#eco-graph'), {
    renderLabels: graph.order < 80,
    labelDensity: 0.08,
    enableEdgeEvents: false,
    defaultEdgeType: 'arrow',
    allowInvalidContainer: true,
  });
  sigma.on('afterRender', () => drawSuggestedOverlay());
  requestAnimationFrame(() => drawSuggestedOverlay());
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
    const label = e.reason ? `Suggested · ${e.reason}` : 'Suggested';
    ctx.fillText(label, (s.x + tpos.x) / 2 - 36, (s.y + tpos.y) / 2 - 4);
    ctx.restore();
  });
}

function actorsGeoJson(scene) {
  const ids = scene.nodeIds;
  const features = actors
    .filter((a) => ids.has(a.id) && hasPlottableGeo(a))
    .map((a) => ({
      type: 'Feature',
      properties: { id: a.id, color: nodeColor(a.id) },
      geometry: { type: 'Point', coordinates: [a.geo.lng, a.geo.lat] },
    }));
  (scene.virtualNodes || []).forEach((vn) => {
    if (!ids.has(vn.id) || !vn.geo) return;
    features.push({
      type: 'Feature',
      properties: { id: vn.id, color: vn.color || '#2a9d8f' },
      geometry: { type: 'Point', coordinates: [vn.geo.lng, vn.geo.lat] },
    });
  });
  return { type: 'FeatureCollection', features };
}

function updateMap(scene) {
  if (!map || !mapReady) return;
  const data = actorsGeoJson(scene);
  if (!map.getSource('actors')) {
    map.addSource('actors', { type: 'geojson', data });
    map.addLayer({
      id: 'pins',
      type: 'circle',
      source: 'actors',
      paint: {
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, 5, 8, 9],
        'circle-color': ['get', 'color'],
        'circle-stroke-width': 1.5,
        'circle-stroke-color': '#fff',
      },
    });
  } else {
    map.getSource('actors').setData(data);
  }
  const m = scene.map;
  if (m?.center) {
    const opts = { center: m.center, zoom: m.zoom || 5.2 };
    if (reducedMotion) map.jumpTo(opts);
    else map.easeTo({ ...opts, duration: 600 });
  }
}

function renderInspector(scene) {
  const tr = t();
  const cap = lang === 'EN' ? scene.caption.en : scene.caption.es;
  $('#mock-caption').textContent = cap;
  const gapsEl = $('#mock-gaps');
  if (scene.gaps?.length) {
    gapsEl.innerHTML = `<strong>${esc(tr.gapsTitle)}</strong><ul>${scene.gaps.map((g) => `<li>${esc(g)}</li>`).join('')}</ul>`;
  } else {
    gapsEl.innerHTML = '';
  }
  const sources = edgeSourceList(scene.realRels);
  const srcEl = $('#mock-sources');
  if (!sources.length) {
    srcEl.innerHTML = `<h3>${esc(tr.sourcesTitle)}</h3><p class="meta">${esc(tr.noSources)}</p>`;
  } else {
    srcEl.innerHTML = `<h3>${esc(tr.sourcesTitle)}</h3><ul>${sources.map((s) =>
      `<li><span class="meta">${esc(s.edge)}</span> — <a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a></li>`,
    ).join('')}</ul>`;
  }
}

function updateStats(scene) {
  const actorCount = [...scene.nodeIds].filter((id) => !isPolicyId(id) && !isDatasetId(id)).length;
  $('#stat-actors').textContent = String(actorCount);
  $('#stat-verified').textContent = String(scene.realRels.length);
  $('#stat-suggested').textContent = String(scene.suggested.length);
}

function renderChapter() {
  storyScene = buildPeruWaterScene(storyChapter, dataBundle());
  updateStats(storyScene);
  renderInspector(storyScene);
  updateMap(storyScene);
  buildGraph(storyScene);
  window.__mockPeruWaterReady = true;
  window.__mockPeruWaterScene = storyScene;
  window.__mockChapterReports = buildChapterReports(dataBundle());
}

function initMap() {
  map = new maplibregl.Map({
    container: 'eco-map',
    style: 'https://tiles.openfreemap.org/styles/liberty',
    center: [-76.2, -12.8],
    zoom: 5.2,
    attributionControl: true,
    fadeDuration: reducedMotion ? 0 : 300,
  });
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
  map.on('load', () => {
    mapReady = true;
    renderChapter();
  });
}

async function loadData() {
  const base = '../../data/';
  const [a, r, actorR, story, pol, polRels, dataRels] = await Promise.all([
    fetch(`${base}actors.json`).then((res) => res.json()),
    fetch(`${base}relations.json`).then((res) => res.json()),
    fetch(`${base}actor_relations.json`).then((res) => (res.ok ? res.json() : { relations: [] })),
    fetch(`${base}story-chapters.json`).then((res) => res.json()),
    fetch(`${base}policies.json`).then((res) => res.json()),
    fetch(`${base}policy_relations.json`).then((res) => res.json()),
    fetch(`${base}data_relations.json`).then((res) => res.json()),
  ]);
  storyConfig = story;
  actors = a;
  relations = r;
  policyRelations = polRels;
  dataRelations = dataRels;
  policiesById = new Map(pol.map((p) => [p.id, p]));
  actorRelationsNorm = (actorR.relations || []).map(normalizeActorRelation);
  byId = new Map(actors.map((x) => [x.id, x]));
}

async function main() {
  initLang();
  try {
    const mod = await import('https://esm.sh/graphology-layout-forceatlas2@0.10.1');
    fa2Assign = mod.default?.assign || mod.assign;
  } catch {
    fa2Assign = null;
  }
  initMap();
  await loadData();
  renderStoryRail();
  if (mapReady) renderChapter();
  window.addEventListener('resize', () => drawSuggestedOverlay());
}

main().catch((err) => {
  console.error(err);
  $('#inspector').innerHTML = `<p>Error: ${esc(err.message)}</p>`;
});
