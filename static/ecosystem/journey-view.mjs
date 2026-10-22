/** DOM, MapLibre, and Sigma for the live Startup journey view. */

import Graph from 'graphology';
import Sigma from 'sigma';
import {
  COUNTRY_MAP_BOUNDS,
  boxesOverlap,
  buildJourneyModel,
  challengeIdFromParam,
  entityName,
  graphLabelFor,
  isPublicHttpUrl,
  labelBox,
  labelPositionForIndex,
  sanitizePublicText,
  sourcedJourneyStartups,
  startupVerifiedFacts,
} from './journey.mjs';

const PATH_COLOR = '#e87722';
const NODE_COLOR = '#0c498a';
const CHALLENGE_COLOR = '#2a9d8f';

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

function countCanvasPaint(canvas) {
  if (!canvas) return 0;
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
  if (!gl) return -1;
  const w = canvas.width;
  const h = canvas.height;
  if (!w || !h) return 0;
  const pixels = new Uint8Array(w * h * 4);
  try {
    gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
  } catch {
    return -1;
  }
  let painted = 0;
  const step = 16;
  for (let i = 0; i < pixels.length; i += 4 * step) {
    if (pixels[i + 3] > 8 && (pixels[i] + pixels[i + 1] + pixels[i + 2]) > 12) painted += 1;
  }
  return painted * step;
}

export function mountJourney(deps) {
  const els = {
    challenge: document.getElementById('journey-challenge'),
    startup: document.getElementById('journey-startup'),
    stat: document.getElementById('journey-stat'),
    rail: document.getElementById('journey-rail'),
    map: document.getElementById('journey-map'),
    graph: document.getElementById('journey-graph'),
    inspector: document.getElementById('journey-inspector'),
    unknown: document.getElementById('journey-unknown'),
    dataList: document.getElementById('journey-data-list'),
    dataMap: document.getElementById('journey-data-map'),
  };

  const boot = new URLSearchParams(location.search);
  let challengeId = null;
  let startupId = boot.get('startup') || null;
  let activeStep = 0;
  let model = null;
  let map = null;
  let dataMap = null;
  let sigma = null;
  let graph = null;
  let booted = false;
  let labelOverlap = false;

  function lang() {
    return deps.getLang();
  }
  function tr() {
    return deps.t();
  }
  function story() {
    return deps.getStory();
  }

  function ensureChallenge() {
    const challenges = story()?.challenges || {};
    const fromUrl = challengeIdFromParam(boot.get('challenge'), challenges);
    const fromState = challengeIdFromParam(
      challengeId ? challengeId.replace(/^challenge:/, '') : null,
      challenges,
    );
    challengeId = fromState || fromUrl || (challenges['challenge:PE-2-agua'] ? 'challenge:PE-2-agua' : Object.keys(challenges)[0] || null);
  }

  function rebuildModel() {
    ensureChallenge();
    model = buildJourneyModel({
      actors: deps.getActors(),
      relations: deps.getRelations(),
      dataRelations: deps.getDataRelations(),
      storyConfig: story(),
      challengeId,
      startupId,
      lang: lang(),
    });
    startupId = model.startupId;
    if (activeStep >= model.steps.length) activeStep = 0;
  }

  function syncQuery() {
    const u = new URL(location.href);
    u.searchParams.set('view', 'journey');
    if (challengeId) u.searchParams.set('challenge', challengeId.replace(/^challenge:/, ''));
    if (startupId) u.searchParams.set('startup', startupId);
    history.replaceState(null, '', u);
  }

  function fillSelects() {
    const l = lang() === 'EN' ? 'en' : 'es';
    const challenges = story()?.challenges || {};
    if (els.challenge) {
      els.challenge.innerHTML = Object.entries(challenges).map(([id, meta]) => {
        const label = meta?.label?.[l] || id;
        return `<option value="${esc(id)}"${id === challengeId ? ' selected' : ''}>${esc(label)}</option>`;
      }).join('');
    }
    const byId = new Map(deps.getActors().map((a) => [a.id, a]));
    if (els.startup) {
      els.startup.innerHTML = (model?.startupIds || []).map((id) => {
        const name = byId.get(id)?.name || id;
        return `<option value="${esc(id)}"${id === startupId ? ' selected' : ''}>${esc(name)}</option>`;
      }).join('');
    }
  }

  function renderStat() {
    if (!els.stat) return;
    if (!model?.stat || !isPublicHttpUrl(model.stat.source_url)) {
      els.stat.classList.add('hidden');
      els.stat.innerHTML = '';
      return;
    }
    const l = lang() === 'EN' ? 'en' : 'es';
    els.stat.classList.remove('hidden');
    els.stat.innerHTML = `<p><strong>${esc(model.stat.stat)}</strong> ${esc(model.stat.label[l])} — <a href="${esc(model.stat.source_url)}" target="_blank" rel="noopener">${esc(model.stat.source_title[l])}</a></p>`;
  }

  function currentStartup() {
    return deps.getActors().find((actor) => actor.id === startupId) || null;
  }

  function factsForStartup() {
    return startupVerifiedFacts(currentStartup(), { stat: model?.stat });
  }

  function factsSummary(facts, copy) {
    let host = '';
    if (facts.website) {
      try {
        host = new URL(facts.website).host.replace(/^www\./, '');
      } catch {
        host = facts.website;
      }
    }
    const bits = [
      host || copy.websitePending,
      facts.location.status === 'address' ? facts.location.text : copy.journeyUnknown,
    ];
    if (facts.stat?.stat) bits.push(facts.stat.stat);
    return bits.join(' · ');
  }

  function renderRail() {
    if (!els.rail || !model) return;
    const copy = tr();
    const summary = factsSummary(factsForStartup(), copy);
    els.rail.innerHTML = model.steps.map((step, i) => `
      <button type="button" class="journey-step${i === activeStep ? ' on' : ''}${step.gap ? ' gap' : ''}" data-idx="${i}">
        <span class="journey-step-k">${esc(step.title)}</span>
        <span class="journey-step-n">${esc(step.actorName || summary)}</span>
      </button>`).join('');
    els.rail.querySelectorAll('.journey-step').forEach((btn) => {
      btn.addEventListener('click', () => selectStep(Number(btn.dataset.idx)));
    });
  }

  function sourceLink(edge) {
    if (!edge || !isPublicHttpUrl(edge.source_url)) return '';
    const label = edge.source_title || tr().journeySource;
    return `<p class="journey-source"><a href="${esc(edge.source_url)}" target="_blank" rel="noopener">${esc(label)}</a></p>`;
  }

  function renderFactsList(facts, copy) {
    const l = lang() === 'EN' ? 'en' : 'es';
    const web = facts.website
      ? `<li><span class="meta">${esc(copy.website)}</span> <a href="${esc(facts.website)}" target="_blank" rel="noopener">${esc(facts.website)}</a></li>`
      : `<li><span class="meta">${esc(copy.website)}</span> ${esc(copy.websitePending)}</li>`;
    const loc = facts.location.status === 'address'
      ? `<li><span class="meta">${esc(copy.journeyFactLocation)}</span> ${esc(facts.location.text)}</li>`
      : `<li><span class="meta">${esc(copy.journeyFactLocation)}</span> ${esc(copy.journeyUnknown)}</li>`;
    const stat = facts.stat
      ? `<li><span class="meta">${esc(copy.journeyFactStat)}</span> <strong>${esc(facts.stat.stat)}</strong> ${esc(facts.stat.label[l])} — <a href="${esc(facts.stat.source_url)}" target="_blank" rel="noopener">${esc(facts.stat.source_title[l])}</a></li>`
      : '';
    return `<h3>${esc(copy.journeyFactsTitle)}</h3><ul class="journey-facts">${web}${loc}${stat}</ul>`;
  }

  function renderSuggestions(copy) {
    const rows = sourcedJourneyStartups({
      actors: deps.getActors(),
      relations: deps.getRelations(),
      storyConfig: story(),
    }).filter((row) => row.challengeId === challengeId && row.id !== startupId);
    if (!rows.length) return '';
    const l = lang() === 'EN' ? 'en' : 'es';
    const items = rows.map((row) => {
      const label = story()?.challenges?.[row.challengeId]?.label?.[l] || row.challengeId;
      return `<li><button type="button" class="journey-suggest-btn" data-startup="${esc(row.id)}" data-challenge="${esc(row.challengeId)}">${esc(row.name)}</button> <span class="meta">${esc(label)} · ${row.edgeCount}</span></li>`;
    }).join('');
    return `<h3>${esc(copy.journeySourcedTitle)}</h3><ul class="journey-suggest">${items}</ul>`;
  }

  function bindSuggestions() {
    els.inspector?.querySelectorAll('.journey-suggest-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        challengeId = btn.dataset.challenge;
        startupId = btn.dataset.startup;
        activeStep = 0;
        render();
        syncQuery();
        show();
      });
    });
  }

  function renderInspector() {
    if (!els.inspector || !model) return;
    const step = model.steps[activeStep];
    const copy = tr();
    if (!step) {
      els.inspector.innerHTML = `<p class="meta">${esc(copy.journeyEmpty)}</p>`;
      return;
    }
    const byId = new Map(deps.getActors().map((a) => [a.id, a]));
    const pin = step.actorId ? model.nodes.includes(step.actorId) && model.pins.some((p) => p.id === step.actorId) : false;
    const mapNote = step.actorId && !pin
      ? `<p class="meta">${esc(copy.journeyNoPin)}</p>`
      : '';
    const quote = step.edge?.evidence
      ? `<blockquote class="journey-quote">${esc(sanitizePublicText(step.edge.evidence))}</blockquote>`
      : '';
    const extras = (step.extraEdges || []).map((edge) => sourceLink(edge)).join('');
    const desc = sanitizePublicText(step.description);
    const edgeLine = step.edge
      ? `<p class="meta">${esc(copy.journeyEdge)} <code>${esc(step.edge.type)}</code> · ${esc(entityName(step.edge.source, byId, story(), lang()))} → ${esc(entityName(step.edge.target, byId, story(), lang()))}</p>`
      : '';
    const gapBlock = step.gap
      ? `<p class="journey-gap">${esc(step.gap)}</p>${renderFactsList(factsForStartup(), copy)}${renderSuggestions(copy)}`
      : '';
    els.inspector.innerHTML = `
      <h2>${esc(step.title)}</h2>
      <h3>${esc(step.actorName || factsForStartup().name || copy.journeyFactsTitle)}</h3>
      ${step.role ? `<p class="meta">${esc(step.role)}</p>` : ''}
      ${desc ? `<p>${esc(desc)}</p>` : ''}
      ${gapBlock}
      ${mapNote}
      ${edgeLine}
      ${quote}
      ${sourceLink(step.edge)}
      ${extras}`;
    bindSuggestions();
  }

  function renderUnknown() {
    if (!els.unknown || !model) return;
    const copy = tr();
    if (!model.unknown.length) {
      els.unknown.innerHTML = `<h4>${esc(copy.journeyUnknown)}</h4><p class="meta">${esc(copy.journeyUnknownNone)}</p>`;
      return;
    }
    els.unknown.innerHTML = `<h4>${esc(copy.journeyUnknown)}</h4><ul>${model.unknown.map((row) =>
      `<li><strong>${esc(row.label)}</strong><br><span class="meta">${esc(copy.journeyUnknown)}</span></li>`,
    ).join('')}</ul>`;
  }

  function renderDataList() {
    if (!els.dataList || !model) return;
    const copy = tr();
    const l = lang() === 'EN' ? 'en' : 'es';
    const items = model.dataRows.map((row) => {
      const label = typeof row.label === 'string' ? row.label : (row.label?.[l] || row.id);
      const link = row.source_url
        ? `<a href="${esc(row.source_url)}" target="_blank" rel="noopener">${esc(copy.journeySource)}</a>`
        : '';
      return `<li><strong>${esc(label)}</strong> — ${esc(copy.journeyUnknown)} ${link}</li>`;
    }).join('');
    els.dataList.innerHTML = items
      ? `<ul>${items}</ul>`
      : `<p class="meta">${esc(copy.journeyUnknownNone)}</p>`;
  }

  function countryBounds() {
    return COUNTRY_MAP_BOUNDS[model?.country] || COUNTRY_MAP_BOUNDS.Peru;
  }

  function pinFeatures() {
    const activeId = model?.steps?.[activeStep]?.actorId || null;
    return (model?.pins || []).map((pin) => ({
      type: 'Feature',
      properties: {
        id: pin.id,
        hot: pin.id === activeId ? 1 : 0,
        startup: pin.id === startupId ? 1 : 0,
      },
      geometry: { type: 'Point', coordinates: [pin.lng, pin.lat] },
    }));
  }

  function fitMap(target) {
    if (!target) return;
    const features = pinFeatures();
    const bounds = countryBounds();
    if (!features.length) {
      target.fitBounds(bounds, { padding: 32, duration: 0 });
      return;
    }
    if (features.length === 1) {
      const [lng, lat] = features[0].geometry.coordinates;
      target.fitBounds([[lng - 2.2, lat - 2.2], [lng + 2.2, lat + 2.2]], { padding: 40, maxZoom: 6, duration: 0 });
      return;
    }
    const box = new window.maplibregl.LngLatBounds(features[0].geometry.coordinates, features[0].geometry.coordinates);
    features.forEach((f) => box.extend(f.geometry.coordinates));
    target.fitBounds(box, { padding: 48, maxZoom: 6, duration: 0 });
  }

  function updateMapLayers() {
    if (!map || !map.isStyleLoaded()) return;
    const data = { type: 'FeatureCollection', features: pinFeatures() };
    const src = map.getSource('journey-actors');
    if (!src) {
      map.addSource('journey-actors', { type: 'geojson', data });
      map.addLayer({
        id: 'journey-hot-ring',
        type: 'circle',
        source: 'journey-actors',
        filter: ['==', ['get', 'hot'], 1],
        paint: {
          'circle-radius': 18,
          'circle-color': PATH_COLOR,
          'circle-opacity': 0.18,
          'circle-stroke-width': 2,
          'circle-stroke-color': PATH_COLOR,
        },
      });
      map.addLayer({
        id: 'journey-points',
        type: 'circle',
        source: 'journey-actors',
        paint: {
          'circle-radius': ['case', ['==', ['get', 'hot'], 1], 8, 6],
          'circle-color': ['case', ['==', ['get', 'hot'], 1], PATH_COLOR, NODE_COLOR],
          'circle-stroke-width': 2,
          'circle-stroke-color': '#ffffff',
        },
      });
      map.on('click', 'journey-points', (e) => {
        const id = e.features?.[0]?.properties?.id;
        const idx = model.steps.findIndex((s) => s.actorId === id);
        if (idx >= 0) selectStep(idx);
      });
    } else {
      src.setData(data);
    }
    fitMap(map);
  }

  // MapLibre uses `clientWidth || 400` when the box is still 0, then skips the
  // first ResizeObserver event. Creating the map before layout leaves a 400px canvas.
  function mapBoxReady(el) {
    return Boolean(el && el.clientWidth >= 40 && el.clientHeight >= 40);
  }

  let layoutWatch = false;
  let resizeQueued = false;

  function resizeLiveMaps() {
    if (map && mapBoxReady(els.map)) map.resize();
    if (dataMap && mapBoxReady(els.dataMap)) {
      dataMap.resize();
      if (dataMap.isStyleLoaded()) {
        dataMap.fitBounds(countryBounds(), { padding: 24, duration: 0 });
        els.dataMap.dataset.journeyDataPins = '0';
      }
    }
  }

  function scheduleMapResize() {
    if (resizeQueued) return;
    resizeQueued = true;
    requestAnimationFrame(() => {
      resizeQueued = false;
      resizeLiveMaps();
    });
  }

  function watchMapLayout() {
    if (layoutWatch) return;
    layoutWatch = true;
    if (typeof ResizeObserver !== 'undefined') {
      const ro = new ResizeObserver(() => scheduleMapResize());
      if (els.map) ro.observe(els.map);
      if (els.dataMap) ro.observe(els.dataMap);
    }
    window.addEventListener('resize', scheduleMapResize);
  }

  function initMap() {
    if (!els.map || !window.maplibregl || map || !mapBoxReady(els.map)) return;
    const bounds = countryBounds();
    map = new window.maplibregl.Map({
      container: els.map,
      style: 'https://tiles.openfreemap.org/styles/liberty',
      bounds,
      fitBoundsOptions: { padding: 32 },
      attributionControl: true,
    });
    map.addControl(new window.maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    map.on('load', () => {
      if (mapBoxReady(els.map)) map.resize();
      updateMapLayers();
    });
  }

  function initDataMap() {
    if (!els.dataMap || !window.maplibregl || dataMap || !mapBoxReady(els.dataMap)) return;
    dataMap = new window.maplibregl.Map({
      container: els.dataMap,
      style: 'https://tiles.openfreemap.org/styles/liberty',
      bounds: countryBounds(),
      fitBoundsOptions: { padding: 24 },
      attributionControl: true,
      interactive: true,
    });
    dataMap.on('load', () => {
      resizeLiveMaps();
      if (els.dataMap) els.dataMap.dataset.journeyDataPins = '0';
    });
  }

  function measureLabelOverlap() {
    if (!sigma || !graph) return false;
    const boxes = [];
    let index = 0;
    graph.forEachNode((id, attr) => {
      const vp = sigma.graphToViewport({ x: attr.x, y: attr.y });
      const position = attr.labelPosition || labelPositionForIndex(index);
      boxes.push(labelBox(vp, attr.label || '', position, 10));
      index += 1;
    });
    labelOverlap = boxesOverlap(boxes, 0);
    if (els.graph) els.graph.dataset.journeyLabelOverlap = labelOverlap ? '1' : '0';
    return labelOverlap;
  }

  function fitSigma() {
    if (!sigma) return;
    sigma.resize();
    const camera = sigma.getCamera();
    camera.setState({ x: 0.5, y: 0.5, ratio: 1.05, angle: 0 });
    sigma.refresh();
    measureLabelOverlap();
  }

  function markGraph() {
    if (!els.graph || !graph) return;
    const canvas = els.graph.querySelector('canvas');
    const painted = countCanvasPaint(canvas);
    els.graph.dataset.journeyGraphNodes = String(graph.order);
    els.graph.dataset.journeyGraphEdges = String(graph.size);
    els.graph.dataset.journeyGraphPainted = String(Math.max(0, painted));
    measureLabelOverlap();
    const ready = graph.order > 0 && canvas && canvas.width > 0;
    if (ready) document.body.dataset.journeyReady = '1';
  }

  function destroySigma() {
    if (sigma) {
      sigma.kill();
      sigma = null;
    }
    graph = null;
  }

  function buildSigma() {
    const container = els.graph;
    if (!container || !model) return;
    if (container.offsetWidth < 40 || container.offsetHeight < 40) {
      requestAnimationFrame(buildSigma);
      return;
    }
    destroySigma();
    graph = new Graph({ multi: false, type: 'directed' });
    const activeId = model.steps[activeStep]?.actorId || startupId;
    const activeEdgeKey = model.steps[activeStep]?.edge
      ? `${model.steps[activeStep].edge.source}|${model.steps[activeStep].edge.target}|${model.steps[activeStep].edge.type}`
      : '';
    model.nodes.forEach((id, i) => {
      const byId = new Map(deps.getActors().map((a) => [a.id, a]));
      const full = entityName(id, byId, story(), lang());
      const isActive = id === activeId;
      let color = NODE_COLOR;
      if (String(id).startsWith('challenge:')) color = CHALLENGE_COLOR;
      if (isActive || id === startupId) color = PATH_COLOR;
      graph.addNode(id, {
        label: graphLabelFor(full),
        x: i * 240,
        y: i % 2 === 0 ? -28 : 28,
        size: isActive ? 16 : 12,
        color,
        labelPosition: labelPositionForIndex(i),
        labelVisibility: 'visible',
        labelSize: 12,
      });
    });
    model.edges.forEach((edge) => {
      if (!graph.hasNode(edge.source) || !graph.hasNode(edge.target)) return;
      const key = `${edge.source}|${edge.target}|${edge.type}`;
      const hot = key === activeEdgeKey;
      if (graph.hasEdge(edge.source, edge.target)) return;
      graph.addEdgeWithKey(key, edge.source, edge.target, {
        color: hot ? PATH_COLOR : '#94a3b8',
        size: hot ? 3.5 : 2,
        type: 'line',
        sourceUrl: edge.source_url,
      });
    });
    sigma = new Sigma(graph, container, {
      settings: {
        renderLabels: true,
        labelDensity: 2,
        labelRenderedSizeThreshold: 0,
        labelGridCellSize: 8,
        stagePadding: 48,
      },
      nodeReducer: (_key, _data, attrs) => ({
        labelPosition: attrs.labelPosition || 'above',
        labelVisibility: 'visible',
        labelSize: 12,
        labelColor: '#0c498a',
      }),
    });
    sigma.on('clickNode', ({ node }) => {
      const idx = model.steps.findIndex((s) => s.actorId === node);
      if (idx >= 0) selectStep(idx);
      else if (node === startupId) selectStep(0);
    });
    sigma.on('afterRender', () => {
      measureLabelOverlap();
      markGraph();
    });
    requestAnimationFrame(() => {
      fitSigma();
      markGraph();
    });
  }

  function paintMaps() {
    if (map && mapBoxReady(els.map)) map.resize();
    if (map && map.isStyleLoaded()) updateMapLayers();
    else if (map) map.once('load', () => updateMapLayers());
    if (dataMap && mapBoxReady(els.dataMap)) {
      dataMap.resize();
      if (dataMap.isStyleLoaded()) {
        dataMap.fitBounds(countryBounds(), { padding: 24, duration: 0 });
        if (els.dataMap) els.dataMap.dataset.journeyDataPins = '0';
      }
    }
  }

  function render() {
    rebuildModel();
    fillSelects();
    renderStat();
    renderRail();
    renderInspector();
    renderUnknown();
    renderDataList();
    paintMaps();
    if (booted) buildSigma();
    publish();
  }

  function selectStep(idx) {
    if (!model || idx < 0 || idx >= model.steps.length) return;
    activeStep = idx;
    renderRail();
    renderInspector();
    paintMaps();
    if (sigma && graph) {
      const activeId = model.steps[activeStep]?.actorId || startupId;
      const activeEdgeKey = model.steps[activeStep]?.edge
        ? `${model.steps[activeStep].edge.source}|${model.steps[activeStep].edge.target}|${model.steps[activeStep].edge.type}`
        : '';
      graph.forEachNode((id) => {
        const hot = id === activeId || (id === startupId && !model.steps[activeStep]?.actorId);
        graph.setNodeAttribute(id, 'color', hot ? PATH_COLOR : (String(id).startsWith('challenge:') ? CHALLENGE_COLOR : NODE_COLOR));
        graph.setNodeAttribute(id, 'size', hot ? 16 : 12);
      });
      graph.forEachEdge((key) => {
        const hot = key === activeEdgeKey;
        graph.setEdgeAttribute(key, 'color', hot ? PATH_COLOR : '#94a3b8');
        graph.setEdgeAttribute(key, 'size', hot ? 3.5 : 2);
      });
      sigma.refresh();
      measureLabelOverlap();
    }
    publish();
  }

  function publish() {
    const api = {
      get model() { return model; },
      listMapPins: () => (model?.pins || []).map((p) => ({ ...p })),
      listUnknown: () => (model?.unknown || []).map((p) => ({ ...p })),
      listEdges: () => (model?.edges || []).map((e) => ({ ...e })),
      listDataRows: () => (model?.dataRows || []).map((r) => ({ ...r, label: { ...r.label } })),
      dataPinCount: () => 0,
      labelOverlap: () => (els.graph?.dataset.journeyLabelOverlap === '1'),
      challengeId: () => challengeId,
      startupId: () => startupId,
      selectStep,
      refresh: render,
    };
    window.__journey = api;
    return api;
  }

  els.challenge?.addEventListener('change', () => {
    challengeId = els.challenge.value;
    startupId = null;
    activeStep = 0;
    render();
    syncQuery();
    show();
  });
  els.startup?.addEventListener('change', () => {
    startupId = els.startup.value;
    activeStep = 0;
    render();
    syncQuery();
    show();
  });

  function show() {
    syncQuery();
    const bootVisuals = () => {
      const panel = document.getElementById('panel-journey');
      if (!panel || panel.classList.contains('hidden')) return;
      if (!window.maplibregl || !mapBoxReady(els.map) || !mapBoxReady(els.dataMap)) {
        requestAnimationFrame(bootVisuals);
        return;
      }
      if (!booted) {
        booted = true;
        initMap();
        initDataMap();
        watchMapLayout();
      }
      resizeLiveMaps();
      buildSigma();
      paintMaps();
    };
    requestAnimationFrame(bootVisuals);
  }

  render();
  return { show, refresh: render, selectStep, publish };
}
