/** Public, vetted relation sources only — no mail, tel, or internal Nexus links. */

export function isPublicSourceUrl(url) {
  if (!url || typeof url !== 'string') return false;
  const trimmed = url.trim();
  if (!/^https?:\/\//i.test(trimmed)) return false;
  if (/^(mailto|tel):/i.test(trimmed)) return false;
  if (/nexus\.cleantechhub\.net/i.test(trimmed)) return false;
  if (/localhost|127\.0\.0\.1/i.test(trimmed)) return false;
  return true;
}

export function isPublicVettedRelation(r) {
  return Boolean(r?.source_url && isPublicSourceUrl(r.source_url));
}

export function mergeVerifiedRelations(bundle) {
  const { relations, actorRelationsNorm } = bundle;
  const raw = [
    ...relations,
    ...actorRelationsNorm.map((r) => ({
      source: r.source,
      target: r.target,
      type: r.type,
      source_url: r.source_url,
      source_title: r.source_title,
      verified: true,
    })),
  ];
  const seen = new Set();
  return raw.filter((r) => {
    const key = `${r.source}|${r.target}|${r.type}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return isPublicVettedRelation(r);
  });
}

export function edgeKey(r) {
  return `${r.source}|${r.target}|${r.type}`;
}
