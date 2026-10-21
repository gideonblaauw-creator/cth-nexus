import Graph from 'graphology';
import Sigma from 'sigma';
import { hasPlottableGeo, geoXY } from '../../../geo-utils.mjs';
import { journeyStepsForStartup, journeyPathEdges } from './journey-steps.mjs';
import { edgeKey, isPublicSourceUrl } from './public-source.mjs';
const PATH_COLOR = '#e87722';

const YAKUSMART_STAT = {
  stat: '12.000 m³',
  label: 'agua optimizada en operación (caso citado)',
  source_url: 'https://www.gob.pe/institucion/produce/noticias/1451346-startup-financiada-por-proinnovate-optimiza-el-riego-agricola-para-incrementar-el-valor-exportable-de-las-frutas',
  source_title: 'Produce — YakuSmart financiada por ProInnóvate',
};

function geoForActor(bundle, id) {
  if (id?.startsWith('challenge:')) {
    const ch = bundle.storyConfig.challenges[id];
    if (ch?.geo?.lat != null && ch?.geo?.lng != null) {
      return { lat: ch.geo.lat, lng: ch.geo.lng, plottable: true, label: ch.label?.es || id };
    }
    return { plottable: false };
  }
  if (id?.startsWith('dataset:')) {
    const ds = bundle.storyConfig.datasets?.[id];
    if (ds?.geo?.lat != null) {
      return { lat: ds.geo.lat, lng: ds.geo.lng, plottable: true, label: ds.label?.es || id };
    }
    return { plottable: false, label: ds?.label?.es || id };
  }
  const a = bundle.byId.get(id);
  if (!a) return { plottable: false };
  if (hasPlottableGeo(a)) {
    return {
      lat: a.geo.lat,
      lng: a.geo.lng,
      plottable: true,
      label: a.name,
      precision: a.geo.precision,
    };
  }
  return { plottable: false, label: a.name, actor: a };
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

  function actorIdsOnPath() {
    const ids = new Set([startupId]);
    steps.forEach((s) => { if (s.actorId) ids.add(s.actorId); });
    return ids;
  }

  function rebuildSteps() {
    steps = journeyStepsForStartup(startupId, bundle);
    pathEdges = journeyPathEdges(steps);
    if (activeStep >= steps.length) activeStep = 0;
  }

  function pathEdgeKeys() {
    return new Set(pathEdges.map((e) => edgeKey(e)));
  }

  function destroySigma() {
    if (sigma) {
      sigma.kill();
      sigma = null;
    }
    graph = null;
  }

  function buildSigma() {
    destroySigma();
    const container = els.graph;
    if (!container) return;
    graph = new Graph({ multi: true, type: 'directed' });
    const ids = actorIdsOnPath();
    const pathKeys = pathEdgeKeys();
    const preset = new Map();

    ids.forEach((id) => {
      if (id.startsWith('challenge:') || id.startsWith('dataset:')) {
        const g = geoForActor(bundle, id);
        const pos = g.plottable
          ? geoXY({ geo: { lat: g.lat, lng: g.lng, precision: 'city' } })
          : { x: 0, y: -40 };
        preset.set(id, pos);
        graph.addNode(id, {
          label: nameFor(bundle, id).slice(0, 36),
          x: pos.x,
          y: pos.y,
          size: 11,
          color: id.startsWith('challenge:') ? '#2a9d8f' : '#64748b',
        });
        return;
      }
      const a = bundle.byId.get(id);
      if (!a) return;
      const pos = geoXY(a);
      graph.addNode(id, {
        label: a.name.length > 32 ? `${a.name.slice(0, 31)}…` : a.name,
        x: pos.x,
        y: pos.y,
        size: id === startupId ? 14 : 10,
        color: id === startupId ? '#e87722' : '#0c498a',
      });
    });

    pathEdges.forEach((e, i) => {
      if (!graph.hasNode(e.source) || !graph.hasNode(e.target)) return;
      const key = `path-${i}-${edgeKey(e)}`;
      const hot = steps[activeStep]?.edge && edgeKey(steps[activeStep].edge) === edgeKey(e);
      try {
        graph.addEdgeWithKey(key, e.source, e.target, {
          color: hot ? PATH_COLOR : PATH_COLOR,
          size: hot ? 4 : 2.5,
          type: 'arrow',
        });
      } catch {
        /* duplicate */
      }
    });

    sigma = new Sigma(graph, container, {
      renderLabels: graph.order < 24,
      labelDensity: 0.12,
      enableEdgeEvents: true,
      defaultEdgeType: 'arrow',
      allowInvalidContainer: true,
    });

    sigma.on('clickNode', ({ node }) => {
      const idx = steps.findIndex((s) => s.actorId === node);
      if (idx >= 0) selectStep(idx);
    });
  }

  function updateMapLayers() {
    if (!map || !map.isStyleLoaded()) return;
    const ids = actorIdsOnPath();
    const features = [];
    ids.forEach((id) => {
      const g = geoForActor(bundle, id);
      if (!g.plottable) return;
      const stepIdx = steps.findIndex((s) => s.actorId === id);
      features.push({
        type: 'Feature',
        properties: {
          id,
          hot: stepIdx === activeStep ? 1 : 0,
          startup: id === startupId ? 1 : 0,
        },
        geometry: { type: 'Point', coordinates: [g.lng, g.lat] },
      });
    });
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
          'circle-radius': ['case', ['==', ['get', 'hot'], 1], 11, ['==', ['get', 'startup'], 1], 9, 7],
          'circle-color': [
            'case',
            ['==', ['get', 'hot'], 1],
            '#e87722',
            ['==', ['get', 'startup'], 1],
            '#e87722',
            '#0c498a',
          ],
          'circle-stroke-width': 2,
          'circle-stroke-color': '#fff',
        },
      });
    }
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
        panToStep(activeStep);
      });
    } else {
      updateMapLayers();
      panToStep(activeStep);
    }
  }

  function panToStep(idx) {
    const step = steps[idx];
    if (!step?.actorId || !map) return;
    const g = geoForActor(bundle, step.actorId);
    if (g.plottable) {
      map.flyTo({ center: [g.lng, g.lat], zoom: g.precision === 'address' ? 12 : 8, duration: 900 });
    } else if (g.plottable === false && bundle.byId.get(step.actorId)?.country === 'Peru') {
      map.flyTo({ center: [-76.2, -12.8], zoom: 5, duration: 600 });
    }
  }

  function renderUnknownList() {
    if (!els.unknown) return;
    const missing = [];
    actorIdsOnPath().forEach((id) => {
      const g = geoForActor(bundle, id);
      if (!g.plottable) {
        missing.push({ id, label: g.label || nameFor(bundle, id) });
      }
    });
    els.unknown.innerHTML = missing.length
      ? `<h4>Ubicación desconocida (sin pin)</h4><ul>${missing.map((m) =>
        `<li><strong>${m.label}</strong> <span class="meta">${m.id}</span></li>`).join('')}</ul>`
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
    panToStep(idx);
    buildSigma();
  }

  function refresh() {
    startupId = els.startup?.value || startupId;
    rebuildSteps();
    renderStat();
    renderRail();
    selectStep(activeStep);
    renderUnknownList();
    initMap();
  }

  els.startup?.addEventListener('change', () => {
    activeStep = 0;
    refresh();
  });

  refresh();
  return { refresh, selectStep };
}
