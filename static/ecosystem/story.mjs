/** Guided story (D5) logic — config-driven, used by ecosystem.mjs */

export function isChallengeId(id) {
  return Boolean(id && String(id).startsWith('challenge:'));
}

export function isPolicyId(id) {
  return Boolean(id && String(id).startsWith('policy:'));
}

export function isDatasetId(id) {
  return Boolean(id && String(id).startsWith('dataset:'));
}

const POLICY_COUNTRY_GEO = {
  Peru: { lat: -9.19, lng: -75.0152 },
  Colombia: { lat: 4.5709, lng: -74.2973 },
  'El Salvador': { lat: 13.7942, lng: -88.8965 },
};

const COUNTRY_CODE = {
  Peru: 'PE',
  Colombia: 'CO',
  'El Salvador': 'SV',
};

export function countryCode(countryName) {
  if (!countryName) return null;
  return COUNTRY_CODE[countryName] || null;
}

/** URL slug `PE-2-agua` or full id `challenge:PE-2-agua` → canonical challenge id. */
export function resolveChallengeParam(param, challenges = {}) {
  if (param == null || param === '' || String(param).toLowerCase() === 'all') return null;
  const raw = String(param).trim();
  const id = raw.startsWith('challenge:') ? raw : `challenge:${raw}`;
  if (challenges[id]) return id;
  const suffix = raw.replace(/^challenge:/, '');
  const match = Object.keys(challenges).find((k) => k === `challenge:${suffix}` || k.endsWith(`-${suffix}`));
  return match || null;
}

export function challengeSlug(challengeId) {
  return String(challengeId || '').replace(/^challenge:/, '');
}

/** Actors with a verified `works_on_challenge` edge to this challenge node. */
export function linkedActorsForChallenge(challengeId, relations) {
  if (!challengeId) return null;
  const linked = new Set();
  for (const r of relations || []) {
    if (r.type !== 'works_on_challenge') continue;
    if (r.target === challengeId) linked.add(r.source);
    if (r.source === challengeId) linked.add(r.target);
  }
  return linked;
}

export function relationMatchesChallengeFocus(r, challengeId, linked) {
  if (!challengeId || !linked) return true;
  if (r.source === challengeId || r.target === challengeId) return true;
  if (linked.has(r.source) || linked.has(r.target)) return true;
  return false;
}

function filterRelationsByChallenge(relations, chapter, challengeId, linked) {
  if (!challengeId || !linked) return relations;
  if (chapter?.id === 'challenges') {
    return relations.filter(
      (r) => r.target === challengeId || r.source === challengeId,
    );
  }
  return relations.filter((r) => relationMatchesChallengeFocus(r, challengeId, linked));
}

export function storyContext({
  byId,
  policiesById = new Map(),
  challenges = {},
  datasets = {},
}) {
  return { byId, policiesById, challenges, datasets };
}

export function entityCountryCode(id, ctx) {
  if (isChallengeId(id)) {
    return countryCode(ctx.challenges[id]?.country);
  }
  if (isPolicyId(id)) {
    return countryCode(ctx.policiesById.get(id)?.country);
  }
  if (isDatasetId(id)) {
    return countryCode(ctx.datasets[id]?.country);
  }
  const actor = ctx.byId.get(id);
  if (actor) {
    return countryCode(actor.country || actor.geo?.country);
  }
  return null;
}

export function relationSameCountry(r, ctx) {
  const cs = entityCountryCode(r.source, ctx);
  const ct = entityCountryCode(r.target, ctx);
  if (!cs || !ct) return true;
  return cs === ct;
}

export function chapterCountryCodes(chapter, storyFocusCc = null) {
  const codes = chapter?.map?.countries;
  if (!codes?.length) return null;
  if (storyFocusCc && codes.includes(storyFocusCc)) {
    return new Set([storyFocusCc]);
  }
  return new Set(codes);
}

function entityInChapterCountries(id, allowed, ctx) {
  if (!allowed) return true;
  const cc = entityCountryCode(id, ctx);
  if (!cc) return true;
  return allowed.has(cc);
}

export function relationAllowedInChapter(r, chapter, ctx, storyFocusCc = null) {
  const allowed = chapterCountryCodes(chapter, storyFocusCc);
  if (!entityInChapterCountries(r.source, allowed, ctx)) return false;
  if (!entityInChapterCountries(r.target, allowed, ctx)) return false;
  return relationSameCountry(r, ctx);
}

export function countCrossCountryGraphEdges(relations, ctx) {
  let n = 0;
  for (const r of relations || []) {
    if (!relationSameCountry(r, ctx)) n += 1;
  }
  return n;
}

export function countCrossCountryPolicyEdges(policyRelations, ctx) {
  let n = 0;
  for (const raw of policyRelations || []) {
    const r = normalizePolicyRelation(raw);
    if (r.type !== 'issues_policy' && r.type !== 'addresses_challenge') continue;
    if (!relationSameCountry(r, ctx)) n += 1;
  }
  return n;
}

export function policyGeo(policyRow) {
  const c = policyRow?.country;
  return POLICY_COUNTRY_GEO[c] || { lat: -10.5, lng: -74.5 };
}

export function datasetGeo(datasetRow) {
  if (datasetRow?.geo?.lat != null && datasetRow?.geo?.lng != null) {
    return datasetRow.geo;
  }
  const c = datasetRow?.country;
  return POLICY_COUNTRY_GEO[c] || { lat: -10.5, lng: -74.5 };
}

function endpointInGraph(id, byId) {
  if (isChallengeId(id) || isPolicyId(id) || isDatasetId(id)) return true;
  return byId.has(id);
}

function normalizePolicyRelation(r) {
  return {
    source: r.source,
    target: r.target,
    type: r.type,
    suggested: Boolean(r.suggested || r.verified === false),
    verified: r.verified !== false,
    source_url: r.source_url,
  };
}

export function dataRelationsForChapter(
  dataRelations,
  byId,
  chapter = null,
  ctx = null,
  storyFocusCc = null,
  storyFocusChallenge = null,
  linkedActors = null,
) {
  if (!dataRelations?.length) return [];
  const out = [];
  for (const raw of dataRelations) {
    const r = { ...raw, id: raw.id || `data-${raw.source}-${raw.target}-${raw.type}` };
    if (!endpointInGraph(r.source, byId) || !endpointInGraph(r.target, byId)) continue;
    if (chapter && ctx && !relationAllowedInChapter(r, chapter, ctx, storyFocusCc)) continue;
    if (storyFocusChallenge && linkedActors
      && !relationMatchesChallengeFocus(r, storyFocusChallenge, linkedActors)) continue;
    out.push(r);
  }
  return out;
}

export function policyRelationsForChapter(
  policyRelations,
  byId,
  chapter = null,
  ctx = null,
  storyFocusCc = null,
  storyFocusChallenge = null,
  linkedActors = null,
) {
  if (!policyRelations?.length) return { real: [], suggested: [] };
  const real = [];
  const suggested = [];
  for (const raw of policyRelations) {
    const r = normalizePolicyRelation(raw);
    if (!endpointInGraph(r.source, byId) || !endpointInGraph(r.target, byId)) continue;
    if (chapter && ctx && !relationAllowedInChapter(r, chapter, ctx, storyFocusCc)) continue;
    if (storyFocusChallenge && linkedActors
      && !relationMatchesChallengeFocus(r, storyFocusChallenge, linkedActors)) continue;
    if (r.suggested) suggested.push({ ...r, id: `pol-sug-${r.source}-${r.target}-${r.type}` });
    else real.push({ ...r, id: `pol-${r.source}-${r.target}-${r.type}` });
  }
  return { real, suggested };
}

export function hasAnyRealEdge(relations, a, b) {
  return relations.some(
    (r) => (r.source === a && r.target === b) || (r.source === b && r.target === a),
  );
}

export function hasRealEdge(relations, a, b, type) {
  return relations.some(
    (r) => r.type === type && ((r.source === a && r.target === b) || (r.source === b && r.target === a)),
  );
}

export function relationsForChapter(
  chapter,
  relations,
  byId = null,
  ctx = null,
  storyFocusCc = null,
  storyFocusChallenge = null,
  linkedActors = null,
) {
  if (!chapter || chapter.id === 'partnerships') return [];
  let base;
  if (chapter.id === 'challenges') {
    base = relations.filter((r) => r.type === 'works_on_challenge');
  } else {
    base = relations.filter(
      (r) => chapter.edgeTypes.includes(r.type)
        && !isChallengeId(r.source)
        && !isChallengeId(r.target)
        && !isPolicyId(r.source)
        && !isPolicyId(r.target)
        && !isDatasetId(r.source)
        && !isDatasetId(r.target),
    );
  }
  const linked = linkedActors
    ?? (storyFocusChallenge ? linkedActorsForChallenge(storyFocusChallenge, relations) : null);
  base = filterRelationsByChallenge(base, chapter, storyFocusChallenge, linked);
  if (!ctx || !byId) return base;
  return base.filter((r) => relationAllowedInChapter(r, chapter, ctx, storyFocusCc));
}

export function computeChapterEdgeCounts(
  config,
  relations,
  byId,
  policyRelations = [],
  options = {},
) {
  const ctx = storyContext({
    byId,
    policiesById: options.policiesById || new Map(),
    challenges: config.challenges,
    datasets: config.datasets || {},
  });
  const dataRelations = options.dataRelations || [];
  const storyFocusCc = options.storyFocusCountry || null;
  const storyFocusChallenge = options.storyFocusChallenge || null;
  const linkedActors = storyFocusChallenge
    ? linkedActorsForChallenge(storyFocusChallenge, relations)
    : null;
  const out = [];
  for (const ch of config.chapters) {
    if (ch.id === 'partnerships') {
      let real = 0;
      let suggested = 0;
      const specs = storyFocusChallenge
        ? config.constellations.filter((spec) => spec.challengeId === storyFocusChallenge)
        : config.constellations;
      for (const spec of specs) {
        const built = buildConstellation(spec, config, relations, byId, ctx, storyFocusCc);
        real += built.edges.filter((e) => !e.suggested).length;
        suggested += built.edges.filter((e) => e.suggested).length;
      }
      out.push({ chapter: ch.id, title: ch.title.en, real, suggested, total: real + suggested });
      continue;
    }
    if (ch.id === 'policy') {
      const pol = policyRelationsForChapter(
        policyRelations, byId, ch, ctx, storyFocusCc, storyFocusChallenge, linkedActors,
      );
      const rels = relationsForChapter(
        ch, relations, byId, ctx, storyFocusCc, storyFocusChallenge, linkedActors,
      );
      const real = rels.length + pol.real.length;
      const suggested = pol.suggested.length;
      const byType = rels.reduce((acc, r) => {
        acc[r.type] = (acc[r.type] || 0) + 1;
        return acc;
      }, {});
      pol.real.forEach((r) => { byType[r.type] = (byType[r.type] || 0) + 1; });
      pol.suggested.forEach((r) => { byType[r.type] = (byType[r.type] || 0) + 1; });
      out.push({
        chapter: ch.id,
        title: ch.title.en,
        real,
        suggested,
        total: real + suggested,
        byType,
      });
      continue;
    }
    if (ch.id === 'data') {
      const rels = relationsForChapter(
        ch, relations, byId, ctx, storyFocusCc, storyFocusChallenge, linkedActors,
      );
      const dataRels = dataRelationsForChapter(
        dataRelations, byId, ch, ctx, storyFocusCc, storyFocusChallenge, linkedActors,
      );
      const real = rels.length + dataRels.length;
      const byType = rels.reduce((acc, r) => {
        acc[r.type] = (acc[r.type] || 0) + 1;
        return acc;
      }, {});
      dataRels.forEach((r) => { byType[r.type] = (byType[r.type] || 0) + 1; });
      out.push({
        chapter: ch.id,
        title: ch.title.en,
        real,
        suggested: 0,
        total: real,
        byType,
        pending: Boolean(ch.pending),
      });
      continue;
    }
    const rels = relationsForChapter(
      ch, relations, byId, ctx, storyFocusCc, storyFocusChallenge, linkedActors,
    );
    out.push({
      chapter: ch.id,
      title: ch.title.en,
      real: rels.length,
      suggested: 0,
      total: rels.length,
      byType: rels.reduce((acc, r) => {
        acc[r.type] = (acc[r.type] || 0) + 1;
        return acc;
      }, {}),
    });
  }
  return out;
}

export function buildConstellation(spec, config, relations, byId, ctx = null, storyFocusCc = null) {
  const center = config.challenges[spec.challengeId];
  const ids = new Set([
    spec.challengeId,
    spec.startupId,
    spec.hubId,
    spec.universityId,
    spec.funderId,
  ].filter(Boolean));

  const nodes = [];
  const edges = [];

  nodes.push({
    id: spec.challengeId,
    label: center?.label?.es || spec.challengeId,
    kind: 'challenge',
    size: 14,
    color: '#2a9d8f',
    position: { x: 0, y: 0 },
    geo: center?.geo,
  });

  const orbit = [
    { id: spec.startupId, role: 'startup', angle: -Math.PI / 2, dist: 120 },
    { id: spec.hubId, role: 'hub', angle: 0.2, dist: 130 },
    { id: spec.universityId, role: 'university', angle: Math.PI, dist: 125 },
    { id: spec.funderId, role: 'funder', angle: Math.PI / 2, dist: 120 },
  ];

  const challengeCc = countryCode(center?.country);

  orbit.forEach((o) => {
    if (!o.id) return;
    const a = byId.get(o.id);
    if (!a) return;
    if (challengeCc && countryCode(a.country) !== challengeCc) return;
    nodes.push({
      id: o.id,
      label: a.name,
      kind: o.role,
      size: o.role === 'startup' ? 12 : 10,
      color: null,
      position: { x: Math.cos(o.angle) * o.dist, y: Math.sin(o.angle) * o.dist },
      geo: a.geo,
    });
  });

  relations.forEach((r, i) => {
    if (!ids.has(r.source) || !ids.has(r.target)) return;
    if (ctx && !relationSameCountry(r, ctx)) return;
    edges.push({
      id: `real-${spec.id}-${i}`,
      source: r.source,
      target: r.target,
      type: r.type,
      suggested: false,
    });
  });

  const suggestions = [];
  const addSuggestion = (source, target, reason) => {
    if (!source || !target || source === target) return;
    if (hasAnyRealEdge(relations, source, target)) return;
    suggestions.push({ source, target, reason });
  };

  if (spec.startupId && !hasRealEdge(relations, spec.startupId, spec.challengeId, 'works_on_challenge')) {
    addSuggestion(spec.startupId, spec.challengeId, 'challenge-fit');
  }
  addSuggestion(spec.hubId, spec.startupId, 'hub-country');
  addSuggestion(spec.funderId, spec.startupId, 'capital-alignment');
  addSuggestion(spec.universityId, spec.startupId, 'academia-pathway');

  suggestions.forEach((s, i) => {
    edges.push({
      id: `sug-${spec.id}-${i}`,
      source: s.source,
      target: s.target,
      type: 'suggested',
      suggested: true,
      label: 'Suggested',
      reason: s.reason,
    });
  });

  return { spec, nodes, edges, center };
}

export function chapterScene(chapterIndex, config, relations, byId, options = {}) {
  const chapter = config.chapters[chapterIndex];
  const {
    constellationId = null,
    closeup = false,
    policyRelations = [],
    policiesById = new Map(),
    dataRelations = [],
    storyFocusCountry = null,
    storyFocusChallenge = null,
  } = options;
  const ctx = storyContext({
    byId,
    policiesById,
    challenges: config.challenges,
    datasets: config.datasets || {},
  });
  const linkedActors = storyFocusChallenge
    ? linkedActorsForChallenge(storyFocusChallenge, relations)
    : null;

  if (chapter.id === 'partnerships') {
    let specs = closeup && constellationId
      ? config.constellations.filter((c) => c.id === constellationId)
      : config.constellations;
    if (storyFocusChallenge) {
      specs = specs.filter((spec) => spec.challengeId === storyFocusChallenge);
    }
    if (storyFocusCountry) {
      specs = specs.filter((spec) => {
        const ch = config.challenges[spec.challengeId];
        return countryCode(ch?.country) === storyFocusCountry;
      });
    }
    const xOff = closeup ? [0] : [-220, 0, 220];
    const nodeMap = new Map();
    const realRels = [];
    const suggested = [];

    specs.forEach((spec, idx) => {
      const built = buildConstellation(spec, config, relations, byId, ctx, storyFocusCountry);
      const ox = xOff[idx] || 0;
      built.nodes.forEach((n) => {
        if (!nodeMap.has(n.id)) {
          nodeMap.set(n.id, {
            ...n,
            position: { x: n.position.x + ox, y: n.position.y },
          });
        }
      });
      built.edges.forEach((e) => {
        const edge = { ...e, id: `${e.id}-${spec.id}` };
        if (e.suggested) suggested.push(edge);
        else realRels.push(edge);
      });
    });

    return {
      chapter,
      nodeIds: new Set(nodeMap.keys()),
      virtualNodes: [...nodeMap.values()].filter((n) => isChallengeId(n.id)),
      presetPositions: nodeMap,
      realRels,
      suggested,
      map: closeup && specs[0]
        ? { center: [config.challenges[specs[0].challengeId].geo.lng, config.challenges[specs[0].challengeId].geo.lat], zoom: 6.2 }
        : chapter.map,
    };
  }

  const chRels = relationsForChapter(
    chapter, relations, byId, ctx, storyFocusCountry, storyFocusChallenge, linkedActors,
  );
  const pol = chapter.id === 'policy'
    ? policyRelationsForChapter(
      policyRelations, byId, chapter, ctx, storyFocusCountry, storyFocusChallenge, linkedActors,
    )
    : { real: [], suggested: [] };
  const dataRels = chapter.id === 'data'
    ? dataRelationsForChapter(
      dataRelations, byId, chapter, ctx, storyFocusCountry, storyFocusChallenge, linkedActors,
    )
    : [];
  const nodeIds = new Set();
  [...chRels, ...pol.real, ...pol.suggested, ...dataRels].forEach((r) => {
    nodeIds.add(r.source);
    nodeIds.add(r.target);
  });
  if (chapter.id === 'challenges') {
    chRels.forEach((r) => nodeIds.add(r.target));
    if (storyFocusChallenge) nodeIds.add(storyFocusChallenge);
  }
  if (chapter.id === 'data' && config.datasets && !storyFocusChallenge) {
    const allowed = chapterCountryCodes(chapter, storyFocusCountry);
    Object.entries(config.datasets).forEach(([id, meta]) => {
      const cc = countryCode(meta?.country);
      if (!allowed || (cc && allowed.has(cc))) nodeIds.add(id);
    });
  }
  const virtualNodes = [];
  [...nodeIds].filter(isChallengeId).forEach((id) => {
    const meta = config.challenges[id];
    virtualNodes.push({
      id,
      label: meta?.label?.es || id,
      kind: 'challenge',
      size: 14,
      color: '#2a9d8f',
      geo: meta?.geo,
    });
  });
  [...nodeIds].filter(isPolicyId).forEach((id) => {
    const row = policiesById.get(id);
    virtualNodes.push({
      id,
      label: row?.name || id.replace(/^policy:/, ''),
      kind: 'policy',
      size: 12,
      color: '#6b4c9a',
      geo: policyGeo(row),
    });
  });
  [...nodeIds].filter(isDatasetId).forEach((id) => {
    const row = config.datasets?.[id];
    virtualNodes.push({
      id,
      label: row?.label?.es || id.replace(/^dataset:/, ''),
      kind: 'dataset',
      size: 11,
      color: '#457b9d',
      geo: datasetGeo(row),
      pending: row?.status === 'pending',
    });
  });

  return {
    chapter,
    nodeIds,
    virtualNodes,
    presetPositions: null,
    realRels: [...chRels, ...pol.real, ...dataRels],
    suggested: pol.suggested.map((r) => ({
      ...r,
      label: 'Suggested',
      reason: r.type,
    })),
    map: (() => {
      if (storyFocusChallenge && config.challenges[storyFocusChallenge]?.geo) {
        const g = config.challenges[storyFocusChallenge].geo;
        return {
          center: [g.lng, g.lat],
          zoom: Math.max(chapter.map?.zoom || 5, 5.6),
          countries: chapter.map?.countries,
        };
      }
      return chapter.map;
    })(),
  };
}
