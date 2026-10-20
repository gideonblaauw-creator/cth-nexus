/** Shared loader for direction mockups (file:// or static server). */
export async function loadEcosystem(base = '../shared/') {
  const [actorsGeo, relations] = await Promise.all([
    fetch(base + 'actors-geo.json').then((r) => r.json()),
    fetch(base + '../prototype/data/relations.json').then((r) => r.json()),
  ]);
  const byId = new Map(actorsGeo.map((a) => [a.id, a]));
  return { actors: actorsGeo, relations, byId };
}

export const CC = { Peru: 'PE', 'El Salvador': 'SV', Colombia: 'CO' };

export const CAT_COLOR = {
  startup: '#e87722',
  accelerator: '#669348',
  funder: '#0c498a',
  government: '#6b4c9a',
  academia: '#2a9d8f',
  corporate: '#457b9d',
  international: '#f4a261',
  finance: '#264653',
  ngo_foundation: '#e76f51',
  chamber: '#8d99ae',
  media: '#bc6c25',
  default: '#5a7088',
};

export const EDGE_COLOR = {
  incubated: '#e87722',
  hosts: '#669348',
  partner: '#0c498a',
  cofunds: '#264653',
  runs_program: '#6b4c9a',
  works_on_challenge: '#2a9d8f',
  default: '#94a3b8',
};
