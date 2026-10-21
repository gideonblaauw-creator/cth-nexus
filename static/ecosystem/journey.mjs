/** Startup journey (Camino de la startup) — live data rules.
 * Pins: precision=address and a street address string. No city/country centroids.
 * Graph edges: isPublicGraphRelation only (verified source + verbatim evidence).
 */

import { isChallengeId, isDatasetId, isPublicGraphRelation } from './story.mjs';
import { hasPlottableGeo } from './geo-utils.mjs';

const BLOCKED_URL = /drive\.google|docs\.google|canva\.com|^mailto:|^tel:/i;

export const JOURNEY_STEP_DEFS = [
  {
    key: 'challenge',
    types: ['works_on_challenge'],
    title: { es: 'Reto de naturaleza', en: 'Nature challenge' },
    gap: {
      es: 'Sin works_on_challenge público (la fuente nombra a los dos actores y trae cita textual).',
      en: 'No public works_on_challenge (source must name both actors and include a verbatim quote).',
    },
  },
  {
    key: 'policy',
    types: ['runs_program', 'regulates_layer', 'issues_policy', 'oversees', 'created', 'runs_initiative'],
    title: { es: 'Política / agencia', en: 'Policy / agency' },
    gap: {
      es: 'Sin relación pública de política para esta startup.',
      en: 'No public policy relation for this startup.',
    },
  },
  {
    key: 'hubs',
    types: ['hosts', 'incubated', 'accelerated', 'program_participation', 'hub_startup'],
    title: { es: 'Hub / incubación', en: 'Hub / incubation' },
    gap: {
      es: 'Sin relación pública de hub o incubación para esta startup.',
      en: 'No public hub or incubation relation for this startup.',
    },
  },
  {
    key: 'data',
    types: ['published_dataset', 'uses_dataset', 'cites_dataset', 'evidence_from'],
    title: { es: 'Datos y evidencia', en: 'Data & evidence' },
    gap: {
      es: 'Sin relación pública de datos para esta startup.',
      en: 'No public data relation for this startup.',
    },
  },
  {
    key: 'partnerships',
    types: ['partner', 'co_organized_event', 'part_of_network', 'participates'],
    title: { es: 'Alianzas', en: 'Partnerships' },
    gap: {
      es: 'Sin alianza pública para esta startup.',
      en: 'No public partnership for this startup.',
    },
  },
  {
    key: 'capital',
    types: ['cofunds', 'funds_layer', 'funding', 'owns'],
    title: { es: 'Capital', en: 'Capital' },
    gap: {
      es: 'Sin relación pública de capital para esta startup.',
      en: 'No public capital relation for this startup.',
    },
  },
];

/** Approved public stat from the G2 mock — not a graph edge. */
export const YAKUSMART_STAT = {
  stat: '12.000 m³',
  label: {
    es: 'agua optimizada en operación (caso citado)',
    en: 'water optimized in operation (cited case)',
  },
  source_url: 'https://www.gob.pe/institucion/produce/noticias/1451346-startup-financiada-por-proinnovate-optimiza-el-riego-agricola-para-incrementar-el-valor-exportable-de-las-frutas',
  source_title: {
    es: 'Produce — YakuSmart financiada por ProInnóvate',
    en: 'Produce — YakuSmart funded by ProInnóvate',
  },
};

export const COUNTRY_MAP_BOUNDS = {
  Peru: [[-81.5, -18.5], [-68.5, -0.5]],
  'El Salvador': [[-90.2, 13.05], [-87.65, 14.45]],
  Colombia: [[-79.1, -4.3], [-66.8, 12.6]],
};

const LANG = (lang) => (lang === 'EN' ? 'en' : 'es');

export function isPublicHttpUrl(url) {
  if (!url || typeof url !== 'string') return false;
  const trimmed = url.trim();
  if (BLOCKED_URL.test(trimmed)) return false;
  try {
    const u = new URL(trimmed);
    return u.protocol === 'https:' || u.protocol === 'http:';
  } catch {
    return false;
  }
}

/** Displayable public graph edge: strict helper plus a public http(s) source. */
export function isJourneyEdge(relation) {
  return Boolean(
    isPublicGraphRelation(relation)
    && isPublicHttpUrl(relation.source_url)
    && String(relation.evidence || '').trim(),
  );
}

/**
 * Street pin only. City/country precision, missing coordinates, missing street
 * text, and the known Bogotá-in-Peru geocode are not pins.
 */
export function streetPinFor(actor) {
  if (!actor || !hasPlottableGeo(actor)) return null;
  const g = actor.geo;
  const address = String(g.address || '').trim();
  if (!address) return null;
  if (!Number.isFinite(Number(g.lat)) || !Number.isFinite(Number(g.lng))) return null;
  const country = actor.country || g.country;
  if (country === 'Peru' && /bogot[aá]/i.test(address)) return null;
  return {
    lat: Number(g.lat),
    lng: Number(g.lng),
    precision: 'address',
    label: actor.name,
  };
}

export function shortJourneyLabel(name, max = 14) {
  const s = String(name || '').replace(/\s+/g, ' ').trim();
  if (s.length <= max) return s;
  return `${s.slice(0, max - 1)}…`;
}

export function graphLabelFor(name) {
  const stripped = String(name || '')
    .replace(/^Reto:\s*/i, '')
    .replace(/^Challenge:\s*/i, '')
    .replace(/\s*\([A-Z]{2}\)\s*$/, '')
    .trim();
  return shortJourneyLabel(stripped, 14);
}

/** Alternate above/below so adjacent screen-space labels do not share a baseline. */
export function labelPositionForIndex(index) {
  return index % 2 === 0 ? 'above' : 'below';
}

export function labelBox(vp, label, position, nodeRadius = 9) {
  const width = Math.max(18, Math.ceil(String(label || '').length * 7.4));
  const height = 14;
  const margin = 6;
  if (position === 'above') {
    return { x: vp.x - width / 2, y: vp.y - nodeRadius - margin - height, w: width, h: height };
  }
  if (position === 'below') {
    return { x: vp.x - width / 2, y: vp.y + nodeRadius + margin, w: width, h: height };
  }
  return { x: vp.x + nodeRadius + margin, y: vp.y - height / 2, w: width, h: height };
}

export function boxesOverlap(boxes, gap = 1) {
  for (let i = 0; i < boxes.length; i += 1) {
    for (let j = i + 1; j < boxes.length; j += 1) {
      const a = boxes[i];
      const b = boxes[j];
      if (a.x < b.x + b.w + gap && a.x + a.w + gap > b.x && a.y < b.y + b.h + gap && a.y + a.h + gap > b.y) {
        return true;
      }
    }
  }
  return false;
}

/** Horizontal fit used by the journey graph, then above/below labels. */
export function fittedLabelBoxes(labels, viewportWidth, viewportHeight, nodeRadius = 9) {
  const n = labels.length;
  const pad = 48;
  const y = viewportHeight / 2;
  const boxes = labels.map((label, i) => {
    const x = n <= 1 ? viewportWidth / 2 : pad + ((viewportWidth - pad * 2) * i) / (n - 1);
    const position = labelPositionForIndex(i);
    return { label, position, ...labelBox({ x, y }, label, position, nodeRadius) };
  });
  return { boxes, overlap: boxesOverlap(boxes) };
}

export function challengeIdFromParam(raw, challenges) {
  if (!raw || !challenges) return null;
  const id = String(raw).startsWith('challenge:') ? String(raw) : `challenge:${raw}`;
  return challenges[id] ? id : null;
}

export function entityName(id, byId, storyConfig, lang) {
  const l = LANG(lang);
  if (!id) return '';
  if (isChallengeId(id)) return storyConfig?.challenges?.[id]?.label?.[l] || id;
  if (isDatasetId(id)) return storyConfig?.datasets?.[id]?.label?.[l] || id;
  return byId.get(id)?.name || id;
}

function otherEnd(relation, startupId) {
  return relation.source === startupId ? relation.target : relation.source;
}

function publicEdge(relation) {
  return {
    source: relation.source,
    target: relation.target,
    type: relation.type,
    verified: true,
    source_url: relation.source_url,
    source_title: relation.source_title || '',
    evidence: String(relation.evidence || '').trim(),
  };
}

export function publicRelations(relations) {
  return (relations || []).filter(isJourneyEdge);
}

export function startupsForChallenge(actors, relations, storyConfig, challengeId) {
  const list = actors || [];
  const byId = new Map(list.map((a) => [a.id, a]));
  const challenge = storyConfig?.challenges?.[challengeId];
  const country = challenge?.country;
  const ids = [];
  const push = (id) => {
    if (!id || ids.includes(id)) return;
    const actor = byId.get(id);
    if (!actor || actor.category !== 'startup') return;
    ids.push(id);
  };

  publicRelations(relations).forEach((r) => {
    if (r.type !== 'works_on_challenge') return;
    if (r.target === challengeId) push(r.source);
    if (r.source === challengeId) push(r.target);
  });

  (storyConfig?.constellations || [])
    .filter((c) => c.challengeId === challengeId)
    .forEach((c) => push(c.startupId));

  list
    .filter((a) => a.category === 'startup' && (!country || a.country === country))
    .map((a) => a.id)
    .sort()
    .forEach(push);

  return ids;
}

export function journeyStepsForStartup({
  startupId,
  challengeId,
  relations,
  byId,
  storyConfig,
  lang,
}) {
  const incident = publicRelations(relations).filter(
    (r) => r.source === startupId || r.target === startupId,
  );
  const used = new Set();

  return JOURNEY_STEP_DEFS.map((def) => {
    let matches = incident.filter((r) => def.types.includes(r.type) && !used.has(edgeKey(r)));
    if (def.key === 'challenge' && challengeId) {
      const preferred = matches.filter((r) => r.source === challengeId || r.target === challengeId);
      if (preferred.length) matches = preferred;
    }
    const edge = matches[0] ? publicEdge(matches[0]) : null;
    matches.forEach((r) => used.add(edgeKey(r)));
    const actorId = edge ? otherEnd(edge, startupId) : null;
    const actor = actorId ? byId.get(actorId) : null;
    return {
      key: def.key,
      title: def.title[LANG(lang)] || def.title.es,
      gap: edge ? null : (def.gap[LANG(lang)] || def.gap.es),
      actorId,
      actorName: actorId ? entityName(actorId, byId, storyConfig, lang) : null,
      role: actor?.card?.ecosystem_role || actor?.category || '',
      description: actor?.card?.description || '',
      edge,
      extraEdges: matches.slice(1).map(publicEdge),
    };
  });
}

export function edgeKey(edge) {
  if (!edge) return '';
  return `${edge.source}|${edge.target}|${edge.type}`;
}

export function journeyPathEdges(steps) {
  const out = [];
  const seen = new Set();
  (steps || []).forEach((step) => {
    [step.edge, ...(step.extraEdges || [])].forEach((edge) => {
      if (!edge) return;
      const key = edgeKey(edge);
      if (seen.has(key)) return;
      seen.add(key);
      out.push(edge);
    });
  });
  return out;
}

export function graphNodeIds(startupId, steps) {
  const ids = [];
  const push = (id) => {
    if (id && !ids.includes(id)) ids.push(id);
  };
  push(startupId);
  (steps || []).forEach((step) => {
    if (step.edge) push(step.actorId);
    (step.extraEdges || []).forEach((edge) => {
      push(edge.source);
      push(edge.target);
    });
  });
  return ids;
}

export function pinStatusFor(id, byId) {
  if (isChallengeId(id)) {
    return { id, plottable: false, reason: 'challenge' };
  }
  if (isDatasetId(id)) {
    return { id, plottable: false, reason: 'dataset' };
  }
  const actor = byId.get(id);
  if (!actor) return { id, plottable: false, reason: 'missing' };
  const pin = streetPinFor(actor);
  if (!pin) return { id, plottable: false, reason: 'unknown', label: actor.name };
  return { id, plottable: true, reason: null, ...pin };
}

export function dataMapRows(storyConfig, challengeId, dataRelations) {
  const challenge = storyConfig?.challenges?.[challengeId];
  const country = challenge?.country;
  const rows = [];
  Object.entries(storyConfig?.datasets || {}).forEach(([id, meta]) => {
    if (country && meta?.country && meta.country !== country) return;
    const source = isPublicHttpUrl(meta?.source_url) ? meta.source_url : null;
    rows.push({
      id,
      label: meta?.label || { es: id, en: id },
      country: meta?.country || '',
      status: meta?.status || '',
      plottable: false,
      source_url: source,
    });
  });
  publicRelations(dataRelations).forEach((r) => {
    if (!['published_dataset', 'uses_dataset', 'cites_dataset', 'evidence_from'].includes(r.type)) return;
    rows.push({
      id: `rel-${edgeKey(r)}`,
      label: { es: r.type, en: r.type },
      plottable: false,
      source_url: r.source_url,
      edge: publicEdge(r),
    });
  });
  return rows;
}

export function buildJourneyModel({
  actors,
  relations,
  dataRelations,
  storyConfig,
  challengeId,
  startupId,
  lang,
}) {
  const byId = new Map((actors || []).map((a) => [a.id, a]));
  const startupIds = startupsForChallenge(actors, relations, storyConfig, challengeId);
  const resolvedStartup = startupIds.includes(startupId) ? startupId : (startupIds[0] || null);
  const steps = resolvedStartup
    ? journeyStepsForStartup({
      startupId: resolvedStartup,
      challengeId,
      relations,
      byId,
      storyConfig,
      lang,
    })
    : [];
  const edges = journeyPathEdges(steps);
  const nodes = graphNodeIds(resolvedStartup, steps);
  const pins = nodes
    .map((id) => pinStatusFor(id, byId))
    .filter((p) => p.plottable);
  const unknown = nodes
    .map((id) => {
      const status = pinStatusFor(id, byId);
      if (status.plottable) return null;
      return {
        id,
        label: entityName(id, byId, storyConfig, lang),
        reason: status.reason,
      };
    })
    .filter(Boolean);
  const stat = resolvedStartup === 'pe-yakusmart' ? YAKUSMART_STAT : null;
  return {
    challengeId,
    startupId: resolvedStartup,
    startupIds,
    steps,
    edges,
    nodes,
    pins,
    unknown,
    dataRows: dataMapRows(storyConfig, challengeId, dataRelations),
    stat,
    country: storyConfig?.challenges?.[challengeId]?.country || null,
  };
}

export function sanitizePublicText(value) {
  return String(value || '')
    .replace(/https?:\/\/[^\s)]+/g, (url) => (isPublicHttpUrl(url) ? url : ''))
    .replace(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/g, '')
    .replace(/\+?\d[\d\s().-]{8,}\d/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 420);
}
