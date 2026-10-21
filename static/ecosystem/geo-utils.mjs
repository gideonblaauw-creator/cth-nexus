/** Map geo rules: plot verified street address only; city/country/unknown → no pin. */

export const COUNTRY_CAPITAL = {
  Peru: { lat: -12.0464, lng: -77.0428 },
  'El Salvador': { lat: 13.6929, lng: -89.2182 },
  Colombia: { lat: 4.711, lng: -74.0721 },
  Guatemala: { lat: 14.6349, lng: -90.5069 },
  'Costa Rica': { lat: 9.9281, lng: -84.0907 },
};

export function geoPrecision(actor) {
  const g = actor?.geo;
  if (!g) return 'missing';
  return g.precision || (g.lat != null ? 'legacy' : 'missing');
}

/** True when MapLibre may show an individual pin at geo.lat/lng. */
export function hasPlottableGeo(actor) {
  const g = actor?.geo;
  if (!g || g.lat == null || g.lng == null) return false;
  return g.precision === 'address';
}

export function isLocationUnknown(actor) {
  return !hasPlottableGeo(actor);
}

/** Graph layout coordinates (not map pins for non-plottable). */
export function geoXY(actor) {
  const g = actor?.geo;
  if (hasPlottableGeo(actor)) {
    return { x: (g.lng + 85) * 10, y: (-g.lat - 18) * 10 };
  }
  const cap = COUNTRY_CAPITAL[actor?.country] || { lat: -15, lng: -60 };
  return { x: (cap.lng + 85) * 10, y: (-cap.lat - 18) * 10 };
}

export function countryBadgeCounts(actors, idSet) {
  const counts = new Map();
  actors.forEach((a) => {
    if (!idSet.has(a.id) || hasPlottableGeo(a)) return;
    const c = a.country || 'Unknown';
    counts.set(c, (counts.get(c) || 0) + 1);
  });
  return counts;
}

export function countryBadgeGeoJson(counts) {
  const features = [];
  counts.forEach((n, country) => {
    const cap = COUNTRY_CAPITAL[country];
    if (!cap || n <= 0) return;
    features.push({
      type: 'Feature',
      properties: {
        kind: 'country-badge',
        country,
        count: n,
        label: `${country} (${n})`,
      },
      geometry: { type: 'Point', coordinates: [cap.lng, cap.lat] },
    });
  });
  return { type: 'FeatureCollection', features };
}
