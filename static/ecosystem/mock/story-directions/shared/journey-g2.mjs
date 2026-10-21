import Graph from 'graphology';
import Sigma from 'sigma';
import { hasPlottableGeo, COUNTRY_CAPITAL } from '../../../geo-utils.mjs';
import { journeyStepsForStartup, journeyPathEdges } from './journey-steps.mjs';
import { edgeKey, isPublicSourceUrl } from './public-source.mjs';

const PATH_COLOR = '#e87722';
const PATH_DIM = '#94a3b8';
const NODE_DEFAULT = 12;
const NODE_STARTUP = 14;
const NODE_ACTIVE = 18;

const YAKUSMART_STAT = {
  stat: '12.000 m³',
  label: 'agua optimizada en operación (caso citado)',
  source_url: 'https://www.gob.pe/institucion/produce/noticias/1451346-startup-financiada-por-proinnovate-optimiza-el-riego-agricola-para-incrementar-el-valor-exportable-de-las-frutas',
  source_title: 'Produce — YakuSmart financiada por ProInnóvate',
};

const PERU_MAP_BOUNDS = [[-81.5, -18.5], [-68.5, -0.5]];

function haversineKm(lat1, lng1, lat2, lng2) {
  const r = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a = Math.sin(dLat / 2) ** 2
    + Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) ** 2;
  return 2 * r * Math.asin(Math.sqrt(a));
}

/**
 * Map pins only for vetted actor addresses — never Canva challenge refs or bad geocodes.
 */
export function mapPinStatus(bundle, id) {
  if (id?.startsWith('challenge:')) {
    return {
      plottable: false,
      reason: 'Nodo reto (referencia Canva en -12.8,-76.2; no es sede verificada)',
    };
  }
  if (id?.startsWith('dataset:')) {
    const ds = bundle.storyConfig.datasets?.[id];
    if (ds?.status === 'pending' || ds?.geo?.lat == null) {
      return { plottable: false, reason: 'Dataset pendiente de curación' };
    }
    return {
      plottable: true,
      lat: ds.geo.lat,
      lng: ds.geo.lng,
      label: ds.label?.es || id,
      precision: 'city',
    };
  }
  const a = bundle.byId.get(id);
  if (!a) return { plottable: false, reason: 'Actor no encontrado' };
  if (!hasPlottableGeo(a)) {
    return { plottable: false, label: a.name, reason: `Sin geo address/city (${a.geo?.precision || 'missing'})` };
  }
  const addr = (a.geo.address || '').toLowerCase();
  if (/\bbogot[aá]\b/.test(addr) && a.country === 'Peru') {
    return {
      plottable: false,
      label: a.name,
      reason: 'Geocodificación inconsistente (dirección menciona Bogotá)',
    };
  }
  if (id === 'pe-cleantechhub') {
    return {
      plottable: false,
      label: a.name,
      reason: 'Sede Arequipa no verificada (OSM mezcló “Bogotá” en la dirección)',
    };
  }
  const lima = COUNTRY_CAPITAL.Peru;
  if (a.city && /lima/i.test(a.city) && haversineKm(a.geo.lat, a.geo.lng, lima.lat, lima.lng) > 120) {
    return {
      plottable: false,
      label: a.name,
      reason: `Ciudad declarada ${a.city} pero pin lejos de Lima (geo dudoso)`,
    };
  }
  return {
    plottable: true,
    lat: a.geo.lat,
    lng: a.geo.lng,
    label: a.name,
    precision: a.geo.precision,
    address: a.geo.address,
  };
}

function nameFor(bundle, id) {
  if (id?.startsWith('challenge:')) {
    return bundle.storyConfig.challenges[id]?.label?.es || id;
  }
  if (id?.startsWith('dataset:')) {
    return bundle.storyConfig.datasets[id]?.label?.es || id;
  }
  return bundle.byId.get(id)?.name || id;
}

function orderedPathIds(startupId, steps) {
  const ordered = [startupId];
  steps.forEach((s) => {
    if (s.actorId && !ordered.includes(s.actorId)) ordered.push(s.actorId);
  });
  return ordered;
}

function layoutPathPositions(ordered) {
  const positions = new Map();
  const n = ordered.length;
  const spread = Math.max(220, n * 52);
  ordered.forEach((id, i) => {
    const t = n <= 1 ? 0.5 : i / (n - 1);
    positions.set(id, {
      x: t * spread - spread / 2,
      y: Math.sin(t * Math.PI) * 36,
    });
  });
  return positions;
}

function fitSigmaCamera(sigma, padding = 0.2) {
  const graph = sigma.getGraph();
  if (graph.order === 0) return;
  const { width, height } = sigma.getDimensions();
  if (width < 4 || height < 4) return false;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  graph.forEachNode((_, attr) => {
    minX = Math.min(minX, attr.x);
    maxX = Math.max(maxX, attr.x);
    minY = Math.min(minY, attr.y);
    maxY = Math.max(maxY, attr.y);
  });
  const graphWidth = Math.max(maxX - minX, 80);
  const graphHeight = Math.max(maxY - minY, 40);
  const ratio = Math.max(
    graphWidth / width,
    graphHeight / height,
  ) * (1 + padding);
  sigma.getCamera().animate({
    x: (minX + maxX) / 2,
    y: (minY + maxY) / 2,
    ratio,
  }, { duration: 0 });
  sigma.refresh();
  return true;
}

function markGraphReady(container, graph) {
  if (!container) return;
  const n = graph?.order ?? 0;
  const e = graph?.size ?? 0;
  container.dataset.g2GraphNodes = String(n);
  container.dataset.g2GraphEdges = String(e);
  container.dispatchEvent(new CustomEvent('g2-sigma-ready', { detail: { nodes: n, edges: e } }));
}

export function bootJourneyG2(bundle, root) {
  const els = {
    rail: root.querySelector('[data-g2-rail]'),
    map: root.querySelector('[data-g2-map]'),
    graph: root.querySelector('[data-g2-graph]'),
    inspector: root.querySelector('[data-g2-inspector]'),
    unknown: root.querySelector('[data-g2-unknown]'),
    stat: root.querySelector('[data-g2-stat]'),
    startup: root.querySelector('#startup-select'),
  };

  let map = null;
  let sigma = null;
  let graph = null;
  let steps = [];
  let pathEdges = [];
  let activeStep = 0;
  let startupId = els.startup?.value || 'pe-yakusmart';
  let mapFitted = false;
  let sigmaResizeObserver = null;
  let sigmaBuildQueued = false;

  function graphContainerReady() {
    const el = els.graph;
    return el && el.offsetWidth >= 40 && el.offsetHeight >= 40;
  }

  function actorIdsOnPath() {
    const ids = new Set([startupId]);
    steps.forEach((s) => { if (s.actorId) ids.add(s.actorId); });
    return ids;
  }

  function activeActorId() {
    return steps[activeStep]?.actorId || null;
  }

  function rebuildSteps() {
    steps = journeyStepsForStartup(startupId, bundle);
    pathEdges = journeyPathEdges(steps);
    if (activeStep >= steps.length) activeStep = 0;
  }

  function destroySigma() {
    if (sigmaResizeObserver && els.graph) {
      sigmaResizeObserver.disconnect();
      sigmaResizeObserver = null;
    }
    if (sigma) {
      sigma.kill();
      sigma = null;
    }
    graph = null;
    if (els.graph) {
      delete els.graph.dataset.g2GraphNodes;
      delete els.graph.dataset.g2GraphEdges;
    }
  }

  function buildSigmaGraph() {
    const container = els.graph;
    if (!container || !graphContainerReady()) {
      queueSigmaBuild();
      return;
    }

    const ordered = orderedPathIds(startupId, steps);
    const positions = layoutPathPositions(ordered);
    const activeId = activeActorId();
    const activeEdgeKey = steps[activeStep]?.edge ? edgeKey(steps[activeStep].edge) : null;

    if (!sigma) {
      graph = new Graph({ multi: true, type: 'directed' });
      ordered.forEach((id) => {
        const pos = positions.get(id);
        const isStartup = id === startupId;
        const isActive = id === activeId;
        let color = '#0c498a';
        if (id.startsWith('challenge:')) color = '#2a9d8f';
        if (id.startsWith('dataset:')) color = '#64748b';
        if (isStartup || isActive) color = PATH_COLOR;
        graph.addNode(id, {
          label: nameFor(bundle, id),
          x: pos.x,
          y: pos.y,
          size: isActive ? NODE_ACTIVE : (isStartup ? NODE_STARTUP : NODE_DEFAULT),
          color,
        });
      });

      pathEdges.forEach((e, i) => {
        if (!graph.hasNode(e.source) || !graph.hasNode(e.target)) return;
        const key = `path-${i}-${edgeKey(e)}`;
        const hot = activeEdgeKey === edgeKey(e);
        try {
          graph.addEdgeWithKey(key, e.source, e.target, {
            color: hot ? PATH_COLOR : PATH_DIM,
            size: hot ? 3.5 : 1.8,
            type: 'arrow',
          });
        } catch {
          /* duplicate */
        }
      });

      sigma = new Sigma(graph, container, {
        renderLabels: true,
        labelDensity: 1,
        labelRenderedSizeThreshold: 0,
        enableEdgeEvents: true,
        defaultEdgeType: 'arrow',
        allowInvalidContainer: true,
        stagePadding: 24,
        renderEdgeLabels: false,
      });
      container.querySelectorAll('canvas').forEach((c) => {
        try {
          const gl = c.getContext('webgl2') || c.getContext('webgl');
          if (gl) gl.canvas.setAttribute('data-sigma-gl', '1');
        } catch {
          /* ignore */
        }
      });

      sigma.on('clickNode', ({ node }) => {
        const idx = steps.findIndex((s) => s.actorId === node);
        if (idx >= 0) selectStep(idx);
      });
      if (!sigmaResizeObserver && typeof ResizeObserver !== 'undefined') {
        sigmaResizeObserver = new ResizeObserver(() => {
          if (!sigma || !graphContainerReady()) return;
          fitSigmaCamera(sigma, 0.25);
          sigma.refresh();
          markGraphReady(container, graph);
        });
        sigmaResizeObserver.observe(container);
      }
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          fitSigmaCamera(sigma, 0.25);
          markGraphReady(container, graph);
        });
      });
    } else {
      graph = sigma.getGraph();
      ordered.forEach((id) => {
        const pos = positions.get(id);
        const isStartup = id === startupId;
        const isActive = id === activeId;
        if (!graph.hasNode(id)) return;
        graph.setNodeAttribute(id, 'x', pos.x);
        graph.setNodeAttribute(id, 'y', pos.y);
        graph.setNodeAttribute(id, 'size', isActive ? NODE_ACTIVE : (isStartup ? NODE_STARTUP : NODE_DEFAULT));
        graph.setNodeAttribute(id, 'color', (isStartup || isActive) ? PATH_COLOR : graph.getNodeAttribute(id, 'color'));
        graph.setNodeAttribute(id, 'label', nameFor(bundle, id));
      });
      graph.forEachEdge((edgeKeyId, _attrs, source, target) => {
        const ek = edgeKeyId.replace(/^path-\d+-/, '');
        const hot = activeEdgeKey && edgeKeyId.includes(activeEdgeKey);
        graph.setEdgeAttribute(edgeKeyId, 'color', hot ? PATH_COLOR : PATH_DIM);
        graph.setEdgeAttribute(edgeKeyId, 'size', hot ? 3.5 : 1.8);
      });
      sigma.refresh();
      fitSigmaCamera(sigma, 0.25);
      markGraphReady(container, graph);
    }
  }

  function queueSigmaBuild() {
    if (sigmaBuildQueued) return;
    sigmaBuildQueued = true;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        sigmaBuildQueued = false;
        buildSigmaGraph();
      });
    });
  }

  function buildSigma() {
    buildSigmaGraph();
  }

  function plottablePinFeatures() {
    const features = [];
    const activeId = activeActorId();
    actorIdsOnPath().forEach((id) => {
      const pin = mapPinStatus(bundle, id);
      if (!pin.plottable) return;
      features.push({
        type: 'Feature',
        properties: {
          id,
          hot: id === activeId ? 1 : 0,
          startup: id === startupId ? 1 : 0,
        },
        geometry: { type: 'Point', coordinates: [pin.lng, pin.lat] },
      });
    });
    return features;
  }

  function updateMapLayers() {
    if (!map || !map.isStyleLoaded()) return;
    const features = plottablePinFeatures();
    const data = { type: 'FeatureCollection', features };
    const src = map.getSource('g2-actors');
    if (src) src.setData(data);
    else {
      map.addSource('g2-actors', { type: 'geojson', data });
      map.addLayer({
        id: 'g2-points',
        type: 'circle',
        source: 'g2-actors',
        paint: {
          'circle-radius': [
            'case',
            ['==', ['get', 'hot'], 1],
            12,
            ['==', ['get', 'startup'], 1],
            8,
            7,
          ],
          'circle-color': [
            'case',
            ['==', ['get', 'hot'], 1],
            '#e87722',
            '#0c498a',
          ],
          'circle-stroke-width': ['case', ['==', ['get', 'hot'], 1], 3, 2],
          'circle-stroke-color': ['case', ['==', ['get', 'hot'], 1], '#fff7ed', '#fff'],
        },
      });
      map.addLayer({
        id: 'g2-hot-ring',
        type: 'circle',
        source: 'g2-actors',
        filter: ['==', ['get', 'hot'], 1],
        paint: {
          'circle-radius': 22,
          'circle-color': '#e87722',
          'circle-opacity': 0.2,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#e87722',
          'circle-stroke-opacity': 0.65,
        },
      });
    }
    if (map.getLayer('g2-hot-ring')) {
      map.setFilter('g2-hot-ring', ['==', ['get', 'hot'], 1]);
    }
  }

  function fitMapToPins() {
    if (!map) return;
    const features = plottablePinFeatures();
    if (!features.length) {
      map.fitBounds(PERU_MAP_BOUNDS, { padding: 40, duration: 0 });
      return;
    }
    if (features.length === 1) {
      const [lng, lat] = features[0].geometry.coordinates;
      map.fitBounds(
        [[lng - 2, lat - 2], [lng + 2, lat + 2]],
        { padding: 48, maxZoom: 6, duration: mapFitted ? 400 : 0 },
      );
    } else {
      const bounds = new window.maplibregl.LngLatBounds(
        features[0].geometry.coordinates,
        features[0].geometry.coordinates,
      );
      features.forEach((f) => bounds.extend(f.geometry.coordinates));
      map.fitBounds(bounds, {
        padding: 56,
        maxZoom: 6,
        duration: mapFitted ? 400 : 0,
      });
    }
    mapFitted = true;
  }

  function initMap() {
    const container = els.map;
    if (!container || !window.maplibregl) return;
    if (!map) {
      map = new maplibregl.Map({
        container,
        style: 'https://tiles.openfreemap.org/styles/liberty',
        center: [-76.2, -12.8],
        zoom: 5,
        attributionControl: true,
      });
      map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
      map.on('load', () => {
        updateMapLayers();
        fitMapToPins();
      });
    } else {
      updateMapLayers();
      fitMapToPins();
    }
  }

  function renderUnknownList() {
    if (!els.unknown) return;
    const missing = [];
    actorIdsOnPath().forEach((id) => {
      const pin = mapPinStatus(bundle, id);
      if (!pin.plottable) {
        missing.push({
          id,
          label: pin.label || nameFor(bundle, id),
          reason: pin.reason || 'Sin pin',
        });
      }
    });
    els.unknown.innerHTML = missing.length
      ? `<h4>Ubicación desconocida (sin pin)</h4><ul>${missing.map((m) =>
        `<li><strong>${m.label}</strong><br><span class="meta">${m.reason}</span></li>`).join('')}</ul>`
      : '<p class="meta">Todos los actores del camino tienen geo ploteable.</p>';
  }

  function renderStat() {
    if (!els.stat) return;
    if (startupId !== 'pe-yakusmart') {
      els.stat.classList.add('hidden');
      els.stat.innerHTML = '';
      return;
    }
    els.stat.classList.remove('hidden');
    els.stat.innerHTML = `
      <p class="g2-stat-line">
        <strong>${YAKUSMART_STAT.stat}</strong> ${YAKUSMART_STAT.label}
        — <a href="${YAKUSMART_STAT.source_url}" target="_blank" rel="noopener">${YAKUSMART_STAT.source_title}</a>
      </p>`;
  }

  function renderInspector(idx) {
    const step = steps[idx];
    if (!els.inspector || !step) return;
    const actorName = step.card?.name || nameFor(bundle, step.actorId);
    const pin = step.actorId ? mapPinStatus(bundle, step.actorId) : null;
    const mapNote = pin && !pin.plottable
      ? `<p class="meta">Mapa: sin pin — ${pin.reason}</p>`
      : '';
    const src = step.source_url && isPublicSourceUrl(step.source_url)
      ? `<p class="g2-source"><a href="${step.source_url}" target="_blank" rel="noopener">${step.source_title || 'Fuente pública verificada'}</a></p>`
      : '<p class="g2-source meta">Sin enlace público verificado para este paso.</p>';
    const edge = step.edge
      ? `<p class="meta">Arista: <code>${step.edge.type}</code> · ${nameFor(bundle, step.edge.source)} → ${nameFor(bundle, step.edge.target)}</p>`
      : '';
    els.inspector.innerHTML = `
      <h2>${step.title}</h2>
      <h3>${actorName}</h3>
      <p class="meta">${step.card?.role || ''}</p>
      <p>${(step.card?.description || '').slice(0, 400)}</p>
      ${mapNote}
      ${step.gap ? `<p class="g2-gap"><strong>Gap:</strong> ${step.gap}</p>` : ''}
      ${edge}
      ${src}`;
  }

  function renderRail() {
    if (!els.rail) return;
    els.rail.innerHTML = steps.map((s, i) => `
      <button type="button" class="g2-step${i === activeStep ? ' on' : ''}${s.gap ? ' gap' : ''}" data-idx="${i}">
        <span class="g2-step-k">${s.title}</span>
        <span class="g2-step-n">${s.card?.name || '—'}</span>
      </button>`).join('');
    els.rail.querySelectorAll('.g2-step').forEach((btn) => {
      btn.addEventListener('click', () => selectStep(Number(btn.dataset.idx)));
    });
  }

  function selectStep(idx) {
    activeStep = idx;
    renderRail();
    renderInspector(idx);
    updateMapLayers();
    buildSigma();
  }

  function refresh() {
    startupId = els.startup?.value || startupId;
    mapFitted = false;
    destroySigma();
    rebuildSteps();
    renderStat();
    renderRail();
    renderUnknownList();
    initMap();
    selectStep(activeStep);
  }

  els.startup?.addEventListener('change', () => {
    activeStep = 0;
    refresh();
  });

  refresh();
  return { refresh, selectStep, mapPinStatus: (id) => mapPinStatus(bundle, id), listMapPins: () => {
    const pins = [];
    actorIdsOnPath().forEach((id) => {
      const p = mapPinStatus(bundle, id);
      if (p.plottable) pins.push({ id, label: p.label || nameFor(bundle, id), lat: p.lat, lng: p.lng, precision: p.precision });
    });
    return pins;
  } };
}
