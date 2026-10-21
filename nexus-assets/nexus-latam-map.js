/** Shared Leaflet LATAM map helpers for Nexus hubs + ecosystem. */
(function (global) {
  'use strict';

  const TILE = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  const ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';

  const COUNTRY_CENTROID = {
    Peru: [-9.19, -75.015],
    Colombia: [4.571, -74.297],
    'El Salvador': [13.794, -88.897],
    Guatemala: [15.784, -90.231],
    'Costa Rica': [9.749, -83.753],
    Mexico: [23.635, -102.553],
  };

  function hashJitter(id, scale) {
    let h = 0;
    for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) | 0;
    const a = ((h & 0xffff) / 0xffff - 0.5) * scale;
    const b = (((h >> 16) & 0xffff) / 0xffff - 0.5) * scale;
    return [a, b];
  }

  function whenLeaflet(cb, tries) {
    if (global.L) {
      cb(global.L);
      return;
    }
    if (tries <= 0) return;
    setTimeout(() => whenLeaflet(cb, tries - 1), 50);
  }

  function baseMap(container, opts) {
    const map = global.L.map(container, {
      scrollWheelZoom: opts.scrollWheelZoom !== false,
      zoomControl: true,
      attributionControl: true,
    });
    global.L.tileLayer(TILE, { maxZoom: 18, attribution: ATTR }).addTo(map);
    map.fitBounds(opts.bounds || [
      [-56, -118],
      [32, -34],
    ], { padding: [24, 24] });
    return map;
  }

  function hubLatLng(hub) {
    if (hub.geo && typeof hub.geo.lat === 'number' && typeof hub.geo.lng === 'number') {
      return [hub.geo.lat, hub.geo.lng];
    }
    const fallback = {
      externado: [4.6287, -74.0647],
      landivar: [14.6349, -90.5069],
      'emprende-up': [-12.0464, -77.0428],
      utec: [9.9369, -84.0219],
      lci: [19.4326, -99.1332],
    };
    return fallback[hub.id] || [0, -70];
  }

  function mountHubMap(containerId, hubs, onSelect) {
    whenLeaflet((L) => {
      const el = document.getElementById(containerId);
      if (!el || el.dataset.leafletMounted) return;
      el.dataset.leafletMounted = '1';
      el.innerHTML = '';
      const map = baseMap(el, { scrollWheelZoom: false });
      const markers = [];
      hubs.forEach((hub) => {
        const soon = hub.status === 'soon';
        const latlng = hubLatLng(hub);
        const marker = L.circleMarker(latlng, {
          radius: soon ? 7 : 10,
          color: '#fff',
          weight: 2,
          fillColor: soon ? '#94A3B8' : '#669348',
          fillOpacity: 0.95,
        }).addTo(map);
        marker.bindTooltip(hub.name?.ES || hub.name?.EN || hub.id, { direction: 'top' });
        marker.on('click', () => onSelect(hub));
        marker.hubId = hub.id;
        markers.push(marker);
      });
      map.on('click', () => onSelect(null));
      el._nexusMap = map;
      el._nexusMarkers = markers;
    }, 80);
  }

  function setActiveHubMarker(containerId, hubId) {
    const el = document.getElementById(containerId);
    if (!el || !el._nexusMarkers) return;
    el._nexusMarkers.forEach((m) => {
      const active = m.hubId === hubId;
      m.setStyle({
        radius: active ? 12 : (m.options.fillColor === '#94A3B8' ? 7 : 10),
        weight: active ? 3 : 2,
      });
    });
  }

  function actorLatLng(actor) {
    const g = actor.geo;
    if (g && typeof g.lat === 'number' && typeof g.lng === 'number') {
      if (g.precision === 'address' || g.precision === 'city') {
        return [g.lat, g.lng];
      }
    }
    return null;
  }

  function mountEcosystemMap(containerId, actors, onCountry) {
    whenLeaflet((L) => {
      const el = document.getElementById(containerId);
      if (!el || el.dataset.leafletMounted) return;
      el.dataset.leafletMounted = '1';
      el.innerHTML = '';
      const map = baseMap(el, {});
      const layer = L.layerGroup().addTo(map);
      el._nexusEcoLayer = layer;
      el._nexusEcoMap = map;
      el._nexusEcoOnCountry = onCountry;
      renderEcosystemMarkers(containerId, actors);
    }, 80);
  }

  function renderEcosystemMarkers(containerId, actors) {
    const el = document.getElementById(containerId);
    if (!el || !el._nexusEcoLayer || !global.L) return;
    const L = global.L;
    el._nexusEcoLayer.clearLayers();
    actors.forEach((a) => {
      const latlng = actorLatLng(a);
      if (!latlng) return;
      const m = L.circleMarker(latlng, {
        radius: 5,
        color: '#0C498A',
        weight: 1,
        fillColor: a.category === 'startup' ? '#669348' : '#69B5FA',
        fillOpacity: 0.85,
      });
      m.bindTooltip(a.name, { direction: 'top', opacity: 0.95 });
      m.on('click', () => {
        if (el._nexusEcoOnCountry) el._nexusEcoOnCountry(a.country);
      });
      el._nexusEcoLayer.addLayer(m);
    });
  }

  global.NexusLatamMap = {
    mountHubMap,
    setActiveHubMarker,
    mountEcosystemMap,
    renderEcosystemMarkers,
    actorLatLng,
    hubLatLng,
  };
})(typeof window !== 'undefined' ? window : globalThis);
