/** Peru Water (PE-2-agua) single-thread story — data-only scene builder */

export const CHALLENGE_ID = 'challenge:PE-2-agua';
export const STARTUP_IDS = ['pe-uqhu', 'pe-yakufil'];

const HUB_TYPES = new Set(['hosts', 'incubated', 'accelerated', 'partner']);
const DATA_TYPES = new Set(['published_dataset', 'uses_dataset', 'cites_dataset', 'evidence_from']);
const CAPITAL_TYPES = new Set(['cofunds', 'funds_layer']);
const POLICY_CHAPTER_GRAPH_TYPES = new Set([
  'regulates_layer', 'runs_program', 'oversees', 'runs_initiative', 'created', 'participates',
]);

export function normalizeActorRelation(r) {
  return {
    source: r.from_id,
    target: r.to_id,
    type: r.type,
    source_url: r.source_url,
    source_title: r.source_title,
    verified: true,
    bundle: 'actor_relations',
    id: `ar-${r.from_id}-${r.to_id}-${r.type}`,
  };
}

export function isChallengeId(id) {
  return Boolean(id && String(id).startsWith('challenge:'));
}

export function isPolicyId(id) {
  return Boolean(id && String(id).startsWith('policy:'));
}

export function isDatasetId(id) {
  return Boolean(id && String(id).startsWith('dataset:'));
}

function pe2Constellations(storyConfig) {
  return (storyConfig.constellations || []).filter((c) => c.challengeId === CHALLENGE_ID);
}

function challengeWorksOn(relations) {
  return relations.filter((r) => r.type === 'works_on_challenge' && r.target === CHALLENGE_ID);
}

function actorName(byId, id) {
  if (isChallengeId(id)) return id;
  if (isPolicyId(id)) return id;
  return byId.get(id)?.name || id;
}

function hasEdge(relations, a, b, type = null) {
  return relations.some((r) => {
    const match = (r.source === a && r.target === b) || (r.source === b && r.target === a);
    if (!match) return false;
    return type ? r.type === type : true;
  });
}

function mergeVerifiedEdges(...lists) {
  const seen = new Set();
  const out = [];
  for (const list of lists) {
    for (const e of list) {
      const key = `${e.source}|${e.target}|${e.type}|${e.bundle || 'relations'}`;
      if (seen.has(key)) continue;
      seen.add(key);
      out.push(e);
    }
  }
  return out;
}

function endpointsFromEdges(edges) {
  const ids = new Set();
  edges.forEach((e) => {
    ids.add(e.source);
    ids.add(e.target);
  });
  return ids;
}

function policyVirtualNode(id, policiesById, storyConfig) {
  const row = policiesById.get(id);
  return {
    id,
    label: row?.name || id.replace(/^policy:/, ''),
    kind: 'policy',
    size: 12,
    color: '#6b4c9a',
    geo: row?.geo || { lat: -12.0952, lng: -77.0599 },
  };
}

function challengeVirtualNode(storyConfig) {
  const meta = storyConfig.challenges[CHALLENGE_ID];
  return {
    id: CHALLENGE_ID,
    label: meta?.label?.es || CHALLENGE_ID,
    kind: 'challenge',
    size: 14,
    color: '#2a9d8f',
    geo: meta?.geo,
  };
}

function constellationSuggestions(spec, relations, combinedRels) {
  const suggestions = [];
  const add = (source, target, reason) => {
    if (!source || !target || source === target) return;
    if (hasEdge(combinedRels, source, target)) return;
    suggestions.push({
      source,
      target,
      type: 'suggested',
      suggested: true,
      label: 'Suggested',
      reason,
      id: `sug-${source}-${target}`,
    });
  };
  if (spec.startupId && !hasEdge(combinedRels, spec.startupId, spec.challengeId, 'works_on_challenge')) {
    add(spec.startupId, spec.challengeId, 'challenge-fit');
  }
  add(spec.hubId, spec.startupId, 'hub-country');
  add(spec.funderId, spec.startupId, 'capital-alignment');
  add(spec.universityId, spec.startupId, 'academia-pathway');
  return suggestions;
}

const CAPTIONS = {
  challenges: {
    es: 'Seis actores del grafo declaran trabajo verificado en el reto Agua & cuencas (PE), incluidas las startups UQHU y Yakufil junto a agencias de agua y clima. El nodo de reto es referencia del mapa Canva, no una organización.',
    en: 'Six graph actors declare verified work on the Water & basins challenge (PE), including startups UQHU and Yakufil alongside water and climate agencies. The challenge node is a Canva map reference, not an organization.',
  },
  policy: {
    es: 'ANA y SUNASS enlazan políticas verificadas (`issues_policy`); otras políticas aparecen como `addresses_challenge` sugerido hacia el reto de agua. INAIGEM y SENAMHI no tienen `issues_policy` en el dataset actual.',
    en: 'ANA and SUNASS link verified policies (`issues_policy`); other policies appear as suggested `addresses_challenge` links to the water challenge. INAIGEM and SENAMHI have no `issues_policy` rows in the current dataset.',
  },
  hubs: {
    es: 'Yakufil tiene incubación verificada vía JAKU Emprende UNSA (`actor_relations.json`); UQHU aún no tiene arista de hub en el grafo. Las líneas punteadas hacia ClimaTech REIN/UP siguen solo donde no hay evidencia verificada.',
    en: 'Yakufil has verified incubation via JAKU Emprende UNSA (`actor_relations.json`); UQHU still has no hub edge in the graph. Dashed lines toward ClimaTech REIN/UP remain only where no verified evidence exists.',
  },
  data: {
    es: 'No hay `published_dataset` / `uses_dataset` en el grafo ni filas en `data_relations.json` para actores del hilo. El dataset MINAM datosabiertos permanece marcado como pendiente de curación.',
    en: 'There are no `published_dataset` / `uses_dataset` graph edges and `data_relations.json` is empty for thread actors. The MINAM open-data dataset stays marked pending curation.',
  },
  partnerships: {
    es: 'Constelación reto-centrada (UQHU y Yakufil): aristas sólidas desde `relations.json` y `actor_relations.json` verificadas; líneas punteadas etiquetadas Suggested con su motivo cuando falta evidencia.',
    en: 'Challenge-centered constellation (UQHU & Yakufil): solid edges from verified `relations.json` and `actor_relations.json`; dashed lines labeled Suggested with reason when evidence is missing.',
  },
  capital: {
    es: 'Yakufil muestra financiamiento verificado (Startup Perú 9G / ProInnóvate y premio Caja Arequipa). UQHU aún no tiene arista de capital en fuentes públicas vinculadas; los fondos de la constelación bosques no aplican a agua.',
    en: 'Yakufil shows verified capital (Startup Perú 9G / ProInnóvate and Caja Arequipa prize). UQHU still has no capital edge in linked public sources; constellation forest funders do not apply to water.',
  },
};

export function buildChapterReports(data) {
  const reports = [];
  for (let i = 0; i < 6; i += 1) {
    const scene = buildPeruWaterScene(i, data);
    reports.push({
      chapter: scene.chapter.id,
      title: scene.chapter.title.en,
      actorsShown: [...scene.nodeIds].filter((id) => !isPolicyId(id) && !isDatasetId(id) && !isChallengeId(id)),
      policyNodes: [...scene.nodeIds].filter(isPolicyId),
      verifiedEdges: scene.realRels.length,
      suggestedEdges: scene.suggested.length,
      gaps: scene.gaps,
      counts: scene.counts,
    });
  }
  return reports;
}

function applyChapterToCumulative(chapterId, cumulative, ctx) {
  const {
    storyConfig,
    relations,
    policyRelations,
    actorRelationsNorm,
    dataRelations,
    byId,
  } = ctx;
  const combinedGraph = [...relations, ...actorRelationsNorm];

  if (chapterId === 'challenges') {
    challengeWorksOn(relations).forEach((r) => {
      cumulative.add(r.source);
      cumulative.add(r.target);
    });
    cumulative.add(CHALLENGE_ID);
    return;
  }
  if (chapterId === 'policy') {
    policyRelations.forEach((raw) => {
      if (raw.type === 'issues_policy' && cumulative.has(raw.source)) {
        cumulative.add(raw.target);
        cumulative.add(raw.source);
      }
      if (raw.type === 'addresses_challenge' && raw.target === CHALLENGE_ID) {
        cumulative.add(raw.source);
      }
    });
    relations.forEach((r) => {
      if (!POLICY_CHAPTER_GRAPH_TYPES.has(r.type)) return;
      if (cumulative.has(r.source) && cumulative.has(r.target)) {
        cumulative.add(r.source);
        cumulative.add(r.target);
      }
    });
    return;
  }
  if (chapterId === 'hubs') {
    STARTUP_IDS.forEach((sid) => {
      relations.forEach((r) => {
        if (!HUB_TYPES.has(r.type)) return;
        if (r.source !== sid && r.target !== sid) return;
        cumulative.add(r.source);
        cumulative.add(r.target);
      });
      actorRelationsNorm.forEach((r) => {
        if (r.type !== 'hub_startup') return;
        if (r.source !== sid && r.target !== sid) return;
        cumulative.add(r.source);
        cumulative.add(r.target);
      });
    });
    pe2Constellations(storyConfig).forEach((spec) => {
      cumulative.add(spec.hubId);
      cumulative.add(spec.universityId);
    });
    return;
  }
  if (chapterId === 'data') {
    cumulative.add('dataset:pe-minam-datosabiertos-pending');
    return;
  }
  if (chapterId === 'partnerships') {
    pe2Constellations(storyConfig).forEach((spec) => {
      Object.values(spec).forEach((v) => {
        if (typeof v === 'string' && (v.startsWith('pe-') || isChallengeId(v))) cumulative.add(v);
      });
    });
    return;
  }
  if (chapterId === 'capital') {
    relations.forEach((r) => {
      if (!CAPITAL_TYPES.has(r.type)) return;
      if (cumulative.has(r.source) || cumulative.has(r.target)) {
        cumulative.add(r.source);
        cumulative.add(r.target);
      }
    });
    actorRelationsNorm.forEach((r) => {
      if (!cumulative.has(r.source) && !cumulative.has(r.target)) return;
      const isFunder = (id) => byId.get(id)?.category === 'funder';
      if ((isFunder(r.source) || isFunder(r.target)) && (r.type === 'funding' || r.type === 'program_participation')) {
        cumulative.add(r.source);
        cumulative.add(r.target);
      }
    });
  }
}

function cumulativeThrough(chapterIndex, data) {
  const cumulative = new Set();
  for (let i = 0; i < chapterIndex; i += 1) {
    applyChapterToCumulative(data.storyConfig.chapters[i].id, cumulative, data);
  }
  return cumulative;
}

export function buildPeruWaterScene(chapterIndex, data) {
  const {
    storyConfig,
    relations,
    policyRelations,
    actorRelationsNorm,
    dataRelations,
    byId,
    policiesById,
  } = data;

  const chapter = storyConfig.chapters[chapterIndex];
  const combinedGraph = [...relations, ...actorRelationsNorm];
  const ch1Edges = challengeWorksOn(relations).map((r) => ({
    ...r,
    verified: true,
    bundle: 'relations',
    id: `rel-${r.source}-${r.target}-${r.type}`,
  }));
  const threadAfterCh1 = endpointsFromEdges(ch1Edges);
  threadAfterCh1.add(CHALLENGE_ID);

  const gaps = [];
  const virtualNodes = [challengeVirtualNode(storyConfig)];

  if (chapter.id === 'challenges') {
    const nodeIds = new Set(threadAfterCh1);
    return finalizeScene({
      chapter,
      chapterIndex,
      nodeIds,
      virtualNodes,
      realRels: ch1Edges,
      suggested: [],
      gaps,
      map: chapter.map,
      counts: {
        actors: nodeIds.size - 1,
        policies: 0,
        datasets: 0,
        verified: ch1Edges.length,
        suggested: 0,
      },
    });
  }

  const cumulative = cumulativeThrough(chapterIndex, data);
  ch1Edges.forEach((e) => {
    cumulative.add(e.source);
    cumulative.add(e.target);
  });
  cumulative.add(CHALLENGE_ID);

  if (chapter.id === 'policy') {
    const verified = [];
    const suggested = [];
    policyRelations.forEach((raw) => {
      const r = { ...raw, id: `pol-${raw.source}-${raw.target}-${raw.type}` };
      if (r.type === 'issues_policy' && cumulative.has(r.source)) {
        verified.push({ ...r, verified: true, bundle: 'policy_relations' });
        cumulative.add(r.target);
      }
      if (r.type === 'addresses_challenge' && r.target === CHALLENGE_ID) {
        suggested.push({
          ...r,
          suggested: true,
          label: 'Suggested',
          reason: 'addresses_challenge',
          bundle: 'policy_relations',
        });
        cumulative.add(r.source);
      }
    });
    relations.forEach((r) => {
      if (!POLICY_CHAPTER_GRAPH_TYPES.has(r.type)) return;
      if (!cumulative.has(r.source) || !cumulative.has(r.target)) return;
      verified.push({ ...r, verified: true, bundle: 'relations', id: `rel-${r.source}-${r.target}-${r.type}` });
    });
    const inaigemSenamhi = ['pe-inaigem', 'pe-senamhi'].filter((id) => cumulative.has(id));
    if (inaigemSenamhi.length) {
      gaps.push(`No issues_policy rows for: ${inaigemSenamhi.join(', ')}`);
    }
    [...verified, ...suggested].forEach((e) => {
      cumulative.add(e.source);
      cumulative.add(e.target);
    });
    const policyIds = new Set();
    verified.forEach((e) => {
      if (isPolicyId(e.target)) policyIds.add(e.target);
      if (isPolicyId(e.source)) policyIds.add(e.source);
    });
    policyIds.forEach((pid) => {
      virtualNodes.push(policyVirtualNode(pid, policiesById, storyConfig));
    });
    return finalizeScene({
      chapter,
      chapterIndex,
      nodeIds: cumulative,
      virtualNodes,
      realRels: verified,
      suggested,
      gaps,
      map: chapter.map,
      counts: countScene(cumulative, verified, suggested, virtualNodes),
    });
  }

  if (chapter.id === 'hubs') {
    const verified = [];
    const suggested = [];
    STARTUP_IDS.forEach((sid) => {
      relations.forEach((r) => {
        if (!HUB_TYPES.has(r.type)) return;
        if (r.source !== sid && r.target !== sid) return;
        verified.push({ ...r, verified: true, bundle: 'relations', id: `rel-${r.source}-${r.target}-${r.type}` });
      });
      actorRelationsNorm.forEach((r) => {
        if (r.type !== 'hub_startup') return;
        if (r.source !== sid && r.target !== sid) return;
        verified.push({ ...r, verified: true, bundle: 'actor_relations' });
      });
    });
    if (!verified.some((e) => e.source === 'pe-uqhu' || e.target === 'pe-uqhu')) {
      gaps.push('No verified hub/incubation edge touching pe-uqhu');
    }
    pe2Constellations(storyConfig).forEach((spec) => {
      constellationSuggestions(spec, relations, mergeVerifiedEdges(relations, actorRelationsNorm)).forEach((s) => {
        if (HUB_TYPES.has('partner') || s.reason === 'hub-country' || s.reason === 'academia-pathway') {
          if (s.reason === 'capital-alignment') return;
          suggested.push(s);
          cumulative.add(spec.hubId);
          cumulative.add(spec.universityId);
        }
      });
    });
    mergeVerifiedEdges(verified).forEach((e) => {
      cumulative.add(e.source);
      cumulative.add(e.target);
    });
    return finalizeScene({
      chapter,
      chapterIndex,
      nodeIds: cumulative,
      virtualNodes,
      realRels: verified,
      suggested,
      gaps,
      map: chapter.map,
      counts: countScene(cumulative, verified, suggested, virtualNodes),
    });
  }

  if (chapter.id === 'data') {
    const verified = [];
    relations.forEach((r) => {
      if (!DATA_TYPES.has(r.type)) return;
      if (!cumulative.has(r.source) && !cumulative.has(r.target)) return;
      verified.push({ ...r, verified: true, bundle: 'relations', id: `rel-${r.source}-${r.target}-${r.type}` });
    });
    if (dataRelations?.length) {
      dataRelations.forEach((r) => {
        if (!cumulative.has(r.source) && !cumulative.has(r.target)) return;
        verified.push({ ...r, verified: true, bundle: 'data_relations', id: `data-${r.source}-${r.target}` });
      });
    } else {
      gaps.push('data_relations.json is empty');
    }
    if (!verified.length) {
      gaps.push('No published_dataset / uses_dataset edges for thread actors in relations.json');
    }
    const pendingId = 'dataset:pe-minam-datosabiertos-pending';
    if (storyConfig.datasets?.[pendingId]) {
      cumulative.add(pendingId);
      virtualNodes.push({
        id: pendingId,
        label: storyConfig.datasets[pendingId].label?.es || pendingId,
        kind: 'dataset',
        size: 11,
        color: '#457b9d',
        geo: storyConfig.datasets[pendingId].geo,
        pending: true,
      });
      gaps.push('MINAM datosabiertos dataset node is pending curation');
    }
    return finalizeScene({
      chapter,
      chapterIndex,
      nodeIds: cumulative,
      virtualNodes,
      realRels: verified,
      suggested: [],
      gaps,
      map: chapter.map,
      counts: countScene(cumulative, verified, [], virtualNodes),
    });
  }

  if (chapter.id === 'partnerships') {
    const specs = pe2Constellations(storyConfig);
    const constellationIds = new Set();
    specs.forEach((spec) => {
      Object.values(spec).forEach((v) => {
        if (typeof v === 'string' && (v.startsWith('pe-') || isChallengeId(v))) constellationIds.add(v);
      });
    });
    cumulative.forEach((id) => constellationIds.add(id));
    const verified = [];
    relations.forEach((r) => {
      if (!constellationIds.has(r.source) || !constellationIds.has(r.target)) return;
      verified.push({ ...r, verified: true, bundle: 'relations', id: `rel-${r.source}-${r.target}-${r.type}` });
    });
    actorRelationsNorm.forEach((r) => {
      if (!constellationIds.has(r.source) || !constellationIds.has(r.target)) return;
      verified.push(r);
    });
    const suggested = [];
    specs.forEach((spec) => {
      constellationSuggestions(spec, relations, mergeVerifiedEdges(verified, actorRelationsNorm)).forEach((s) => {
        suggested.push(s);
      });
    });
    const presetPositions = new Map();
    const cx = 0;
    specs.forEach((spec, idx) => {
      const ox = specs.length > 1 ? (idx === 0 ? -160 : 160) : 0;
      const orbit = [
        { id: spec.startupId, angle: -Math.PI / 2, dist: 110 },
        { id: spec.hubId, angle: 0.2, dist: 125 },
        { id: spec.universityId, angle: Math.PI, dist: 120 },
        { id: spec.funderId, angle: Math.PI / 2, dist: 115 },
      ];
      presetPositions.set(spec.challengeId, { position: { x: ox, y: 0 } });
      orbit.forEach((o) => {
        if (!o.id) return;
        presetPositions.set(o.id, {
          position: { x: ox + Math.cos(o.angle) * o.dist, y: Math.sin(o.angle) * o.dist },
        });
      });
    });
    virtualNodes[0] = challengeVirtualNode(storyConfig);
    return finalizeScene({
      chapter,
      chapterIndex,
      nodeIds: constellationIds,
      virtualNodes,
      realRels: mergeVerifiedEdges(verified),
      suggested,
      gaps,
      map: { center: [-76.2, -12.8], zoom: 5.4 },
      presetPositions,
      storyLayout: true,
      counts: countScene(constellationIds, mergeVerifiedEdges(verified), suggested, virtualNodes),
    });
  }

  if (chapter.id === 'capital') {
    const verified = [];
    const isFunder = (id) => byId.get(id)?.category === 'funder';
    const touchesStartup = (r, sid) => r.source === sid || r.target === sid;
    relations.forEach((r) => {
      if (!CAPITAL_TYPES.has(r.type)) return;
      if (!STARTUP_IDS.some((sid) => touchesStartup(r, sid))) return;
      verified.push({ ...r, verified: true, bundle: 'relations', id: `rel-${r.source}-${r.target}-${r.type}` });
    });
    actorRelationsNorm.forEach((r) => {
      if (r.type !== 'funding') return;
      if (!STARTUP_IDS.some((sid) => touchesStartup(r, sid))) return;
      verified.push({ ...r, verified: true, bundle: 'actor_relations' });
    });
    mergeVerifiedEdges(verified).forEach((e) => {
      cumulative.add(e.source);
      cumulative.add(e.target);
    });
    STARTUP_IDS.forEach((sid) => {
      const hasCapital = verified.some((e) => touchesStartup(e, sid)
        && (e.type === 'funding' || e.type === 'cofunds' || e.type === 'funds_layer'
          || isFunder(e.source) || isFunder(e.target)
          || e.source === 'pe-proinnovate-startup-peru' || e.target === 'pe-proinnovate-startup-peru'));
      if (!hasCapital) gaps.push(`No verified capital/funding edge to startup ${sid}`);
    });
    if (!verified.length) {
      gaps.push('No verified cofunds/funds_layer/funding edges for water-thread startups');
    }
    return finalizeScene({
      chapter,
      chapterIndex,
      nodeIds: cumulative,
      virtualNodes,
      realRels: verified,
      suggested: [],
      gaps,
      map: chapter.map,
      counts: countScene(cumulative, verified, [], virtualNodes),
    });
  }

  return finalizeScene({
    chapter,
    chapterIndex,
    nodeIds: cumulative,
    virtualNodes,
    realRels: [],
    suggested: [],
    gaps: ['Unknown chapter'],
    map: chapter.map,
    counts: { actors: 0, policies: 0, datasets: 0, verified: 0, suggested: 0 },
  });
}

function countScene(nodeIds, verified, suggested, virtualNodes) {
  return {
    actors: [...nodeIds].filter((id) => !isPolicyId(id) && !isDatasetId(id) && !isChallengeId(id)).length,
    policies: [...nodeIds].filter(isPolicyId).length,
    datasets: [...nodeIds].filter(isDatasetId).length,
    verified: verified.length,
    suggested: suggested.length,
  };
}

function finalizeScene(scene) {
  const cap = CAPTIONS[scene.chapter.id] || { es: '', en: '' };
  return {
    ...scene,
    caption: cap,
    cumulativeActorIds: [...scene.nodeIds],
  };
}

export function edgeSourceList(edges) {
  return edges
    .filter((e) => e.verified && e.source_url)
    .map((e) => ({
      edge: `${e.source} → ${e.target} (${e.type})`,
      url: e.source_url,
      title: e.source_title || e.source_url,
    }));
}
