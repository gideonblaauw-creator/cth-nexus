import {
  normalizeActorRelation,
  buildPeruWaterScene,
  CHALLENGE_ID,
  STARTUP_IDS,
} from './water-thread.mjs';

const DATA = '../../../data';
const MOCK_DATA = '../data';

export { CHALLENGE_ID, STARTUP_IDS, buildPeruWaterScene };

export async function loadWaterMockData(challengeId = CHALLENGE_ID) {
  const [
    storyConfig,
    actors,
    relations,
    policyRelations,
    dataRelations,
    actorRelBundle,
    relOverlay,
    storyOverlay,
    pullQuotes,
    policies,
  ] = await Promise.all([
    fetch(`${DATA}/story-chapters.json`).then((r) => r.json()),
    fetch(`${DATA}/actors.json`).then((r) => r.json()),
    fetch(`${DATA}/relations.json`).then((r) => r.json()),
    fetch(`${DATA}/policy_relations.json`).then((r) => r.json()).catch(() => []),
    fetch(`${DATA}/data_relations.json`).then((r) => r.json()).catch(() => []),
    fetch(`${MOCK_DATA}/actor_relations-water.json`).then((r) => r.json()),
    fetch(`${MOCK_DATA}/relations-overlay.json`).then((r) => r.json()),
    fetch(`${MOCK_DATA}/story-overlay.json`).then((r) => r.json()),
    fetch(`${MOCK_DATA}/pull-quotes.json`).then((r) => r.json()),
    fetch(`${DATA}/policies.json`).then((r) => r.json()).catch(() => []),
  ]);

  const mergedConfig = {
    ...storyConfig,
    challenges: { ...storyConfig.challenges, ...storyOverlay.challenges },
    constellations: [
      ...storyConfig.constellations,
      ...(storyOverlay.constellations || []).filter(
        (c) => !storyConfig.constellations.some((x) => x.id === c.id),
      ),
    ],
  };

  const mergedRelations = [...relations, ...relOverlay];
  const actorRelationsNorm = (actorRelBundle.relations || []).map(normalizeActorRelation);
  const byId = new Map(actors.map((a) => [a.id, a]));
  const policiesById = new Map((policies || []).map((p) => [p.id, p]));

  const bundle = {
    storyConfig: mergedConfig,
    relations: mergedRelations,
    policyRelations,
    dataRelations,
    actorRelationsNorm,
    byId,
    policiesById,
    pullQuotes,
    challengeId,
  };

  bundle.getScene = (chapterIndex) => buildPeruWaterScene(chapterIndex, bundle);
  return bundle;
}

export function challengeOptions(storyConfig, lang = 'es') {
  return Object.entries(storyConfig.challenges || {}).map(([id, meta]) => ({
    id,
    label: meta.label?.[lang] || meta.label?.en || id,
  }));
}

export function actorLabel(byId, id) {
  if (id.startsWith('challenge:')) return id;
  if (id.startsWith('policy:')) return id.replace(/^policy:/, '');
  if (id.startsWith('dataset:')) return id.replace(/^dataset:/, '');
  return byId.get(id)?.name || id;
}

export function actorCard(byId, id) {
  const a = byId.get(id);
  if (!a) return { id, name: id, role: '', description: '', website: null, linkedin: null, city: '' };
  return {
    id,
    name: a.name,
    role: a.card?.ecosystem_role || a.category || '',
    description: a.card?.description || '',
    website: a.website || null,
    linkedin: a.linkedin || null,
    city: a.city || '',
    category: a.category,
  };
}

/** Visual from actor fields only: favicon from website or typographic fallback id */
export function actorVisualUrl(actor) {
  if (actor?.website) {
    try {
      const host = new URL(actor.website).hostname;
      return `https://www.google.com/s2/favicons?domain=${host}&sz=128`;
    } catch {
      /* ignore */
    }
  }
  return null;
}

export function wireChallengeSelect(select, bundle, onChange) {
  if (!select) return;
  const opts = challengeOptions(bundle.storyConfig);
  select.innerHTML = opts.map((o) =>
    `<option value="${o.id}"${o.id === bundle.challengeId ? ' selected' : ''}>${o.label}</option>`).join('');
  select.addEventListener('change', () => {
    bundle.challengeId = select.value;
    onChange?.();
  });
}
