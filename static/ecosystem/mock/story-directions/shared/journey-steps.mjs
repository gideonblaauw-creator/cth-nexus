import { actorCard, actorLabel } from './water-loader.mjs';

const STEPS = [
  { key: 'challenge', title: 'Reto de naturaleza', titleEn: 'Nature challenge' },
  { key: 'policy', title: 'Política / agencia', titleEn: 'Policy' },
  { key: 'hubs', title: 'Hub / incubación', titleEn: 'Hubs' },
  { key: 'data', title: 'Datos y evidencia', titleEn: 'Data' },
  { key: 'partnerships', title: 'Alianzas', titleEn: 'Partnerships' },
  { key: 'capital', title: 'Capital', titleEn: 'Capital' },
];

export function journeyStepsForStartup(startupId, bundle) {
  const { byId, relations, actorRelationsNorm, storyConfig } = bundle;
  const challengeId = 'challenge:PE-2-agua';
  const steps = [];

  const verified = [...relations, ...actorRelationsNorm.map((r) => ({
    source: r.source,
    target: r.target,
    type: r.type,
    source_url: r.source_url,
    source_title: r.source_title,
    verified: true,
  }))];

  const touch = (r) => r.source === startupId || r.target === startupId;
  const other = (r) => (r.source === startupId ? r.target : r.source);

  // Challenge
  const woc = verified.find((r) => r.type === 'works_on_challenge' && r.source === startupId && r.target === challengeId)
    || verified.find((r) => r.type === 'works_on_challenge' && touch(r));
  steps.push({
    ...STEPS[0],
    actorId: challengeId,
    card: {
      name: storyConfig.challenges[challengeId]?.label?.es || 'PE-2-agua',
      role: 'Nodo reto (referencia Canva)',
      description: storyConfig.chapters[0]?.blurb?.es || '',
      website: null,
    },
    source_url: woc?.source_url,
    source_title: woc?.source_title,
    gap: !woc ? 'Sin works_on_challenge verificado en mock' : null,
  });

  // Policy — agency linked to challenge or startup
  const policyEdge = verified.find((r) =>
    (r.type === 'issues_policy' || r.type === 'regulates_layer' || r.type === 'runs_program')
    && (touch(r) || r.target === challengeId));
  const policyId = policyEdge ? other(policyEdge) : null;
  if (startupId === 'pe-uqhu') {
    steps.push({
      ...STEPS[1],
      actorId: 'pe-ana-autoridad-nacional-del-agua',
      card: actorCard(byId, 'pe-ana-autoridad-nacional-del-agua'),
      source_url: null,
      source_title: 'Agencia en grafo works_on_challenge (sin issues_policy UQHU en bundle)',
      gap: 'Sin arista policy verificada dedicada a UQHU',
    });
  } else {
    steps.push({
      ...STEPS[1],
      actorId: policyId || 'pe-produce-ministerio-de-la-produccion',
      card: actorCard(byId, policyId || 'pe-produce-ministerio-de-la-produccion'),
      source_url: policyEdge?.source_url,
      source_title: policyEdge?.source_title,
      gap: policyEdge ? null : 'Contexto vía Produce/ProInnóvate en hubs/capital',
    });
  }

  // Hubs
  const hubTypes = new Set(['hosts', 'incubated', 'accelerated', 'partner', 'hub_startup', 'program_participation']);
  const hubEdges = verified.filter((r) => hubTypes.has(r.type) && touch(r));
  const hubPick = hubEdges.find((r) => r.type === 'hub_startup' || r.type === 'program_participation') || hubEdges[0];
  steps.push({
    ...STEPS[2],
    actorId: hubPick ? other(hubPick) : null,
    card: hubPick ? actorCard(byId, other(hubPick)) : { name: 'PENDIENTE', role: '', description: '' },
    source_url: hubPick?.source_url,
    source_title: hubPick?.source_title,
    gap: hubPick ? null : `Sin hub verificado para ${actorLabel(byId, startupId)}`,
    extra: hubEdges.slice(0, 3).map((e) => ({
      label: `${e.type} → ${actorLabel(byId, other(e))}`,
      url: e.source_url,
    })),
  });

  // Data
  const dataEdge = verified.find((r) =>
    (r.type === 'published_dataset' || r.type === 'uses_dataset') && touch(r));
  steps.push({
    ...STEPS[3],
    actorId: dataEdge ? other(dataEdge) : 'dataset:pe-minam-datosabiertos-pending',
    card: dataEdge
      ? actorCard(byId, other(dataEdge))
      : {
        name: 'MINAM · Datos Abiertos (PE) — pendiente',
        role: 'Dataset',
        description: 'Nodo pendiente de curación en story-chapters.json',
      },
    source_url: dataEdge?.source_url,
    gap: dataEdge ? null : 'Sin uses_dataset / published_dataset verificado para esta startup',
  });

  // Partnerships
  const partnerEdge = verified.find((r) =>
    (r.type === 'co_organized_event' || r.type === 'partner') && touch(r));
  steps.push({
    ...STEPS[4],
    actorId: partnerEdge ? other(partnerEdge) : 'pe-cleantechhub',
    card: partnerEdge ? actorCard(byId, other(partnerEdge)) : actorCard(byId, 'pe-cleantechhub'),
    source_url: partnerEdge?.source_url,
    source_title: partnerEdge?.source_title,
    gap: partnerEdge ? null : 'Alianza sugerida / no verificada en actor_relations',
  });

  // Capital
  const capEdge = verified.find((r) =>
    (r.type === 'funding' || r.type === 'cofunds') && touch(r));
  steps.push({
    ...STEPS[5],
    actorId: capEdge ? other(capEdge) : null,
    card: capEdge ? actorCard(byId, other(capEdge)) : { name: 'PENDIENTE', role: 'Capital', description: '' },
    source_url: capEdge?.source_url,
    source_title: capEdge?.source_title,
    gap: capEdge ? null : `Sin funding/cofunds verificado (${startupId === 'pe-uqhu' ? 'UQHU' : 'revisar CSV'})`,
  });

  return steps;
}
