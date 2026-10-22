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

const NAME_TO_CC = {
  peru: 'PE',
  'el salvador': 'SV',
  colombia: 'CO',
  guatemala: 'GT',
  'costa rica': 'CR',
};

const PREFIX_CC = {
  pe: 'PE',
  sv: 'SV',
  co: 'CO',
  gt: 'GT',
  cr: 'CR',
};

function foldCountry(value) {
  return String(value || '').normalize('NFD').replace(/\p{M}/gu, '').trim().toLowerCase();
}

/** Catalogue country: name first, then id prefix (co-… is CO). */
export function actorCountryCode(actor) {
  const folded = foldCountry(actor?.country);
  if (NAME_TO_CC[folded]) return NAME_TO_CC[folded];
  if (folded.length === 2 && PREFIX_CC[folded]) return folded.toUpperCase();
  const prefix = String(actor?.id || '').split('-')[0]?.toLowerCase();
  return PREFIX_CC[prefix] || null;
}

/**
 * Street line for popups, cards, and tooltips.
 * Colombia keeps the pin coordinates and omits the street text.
 */
export function visibleStreetAddress(actor) {
  if (actorCountryCode(actor) === 'CO') return '';
  return String(actor?.geo?.address || '').trim();
}

/** City / country labels. Colombia city text loses an embedded street line. */
export function visiblePlaceParts(actor) {
  let city = String(actor?.city || '').trim();
  const country = String(actor?.country || '').trim();
  if (actorCountryCode(actor) === 'CO') {
    const street = String(actor?.geo?.address || '').trim();
    if (street && city.includes(street)) {
      city = city.replace(street, '').replace(/^[\s,;·-]+|[\s,;·-]+$/g, '').trim();
    }
  }
  return { city, country };
}

const STREET_FIELD = /^\s*(?:\|?\s*|[-*]\s*)?(?:\*\*)?(?:direcci[oó]n|address|street(?:\s+address)?)(?:\*\*)?\s*[:|]/i;

/** Drop street-address text from rendered copy when the actor is CO. */
export function redactPublicStreetText(actor, text) {
  const raw = text == null ? '' : String(text);
  if (actorCountryCode(actor) !== 'CO') return raw;
  const street = String(actor?.geo?.address || '').trim();
  const lines = raw.split('\n').filter((line) => !STREET_FIELD.test(line.replace(/\*/g, '')));
  let out = lines.join('\n');
  if (street) out = out.split(street).join('');
  return out.replace(/[ \t]{2,}/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
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
