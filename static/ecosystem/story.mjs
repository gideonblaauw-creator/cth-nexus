/** Guided story (D5) logic — config-driven, used by ecosystem.mjs */

export function isChallengeId(id) {
  return Boolean(id && String(id).startsWith('challenge:'));
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

export function relationsForChapter(chapter, relations) {
  if (!chapter || chapter.id === 'partnerships') return [];
  if (chapter.id === 'challenges') {
    return relations.filter((r) => r.type === 'works_on_challenge');
  }
  return relations.filter(
    (r) => chapter.edgeTypes.includes(r.type)
      && !isChallengeId(r.source)
      && !isChallengeId(r.target),
  );
}

export function computeChapterEdgeCounts(config, relations, byId) {
  const out = [];
  for (const ch of config.chapters) {
    if (ch.id === 'partnerships') {
      let real = 0;
      let suggested = 0;
      for (const spec of config.constellations) {
        const built = buildConstellation(spec, config, relations, byId);
        real += built.edges.filter((e) => !e.suggested).length;
        suggested += built.edges.filter((e) => e.suggested).length;
      }
      out.push({ chapter: ch.id, title: ch.title.en, real, suggested, total: real + suggested });
      continue;
    }
    const rels = relationsForChapter(ch, relations);
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

export function buildConstellation(spec, config, relations, byId) {
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

  orbit.forEach((o) => {
    if (!o.id) return;
    const a = byId.get(o.id);
    if (!a) return;
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
  const { constellationId = null, closeup = false } = options;

  if (chapter.id === 'partnerships') {
    const specs = closeup && constellationId
      ? config.constellations.filter((c) => c.id === constellationId)
      : config.constellations;
    const xOff = closeup ? [0] : [-220, 0, 220];
    const nodeMap = new Map();
    const realRels = [];
    const suggested = [];

    specs.forEach((spec, idx) => {
      const built = buildConstellation(spec, config, relations, byId);
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

  const chRels = relationsForChapter(chapter, relations);
  const nodeIds = new Set();
  chRels.forEach((r) => {
    nodeIds.add(r.source);
    nodeIds.add(r.target);
  });
  if (chapter.id === 'challenges') {
    chRels.forEach((r) => nodeIds.add(r.target));
  }

  const virtualNodes = [...nodeIds]
    .filter(isChallengeId)
    .map((id) => {
      const meta = config.challenges[id];
      return {
        id,
        label: meta?.label?.es || id,
        kind: 'challenge',
        size: 14,
        color: '#2a9d8f',
        geo: meta?.geo,
      };
    });

  return {
    chapter,
    nodeIds,
    virtualNodes,
    presetPositions: null,
    realRels: chRels,
    suggested: [],
    map: chapter.map,
  };
}
