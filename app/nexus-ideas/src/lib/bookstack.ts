// lib/bookstack.ts — Server-side BookStack API client
// Called from Next.js Server Components or Route Handlers
//
// IMPORTANT: BookStack's /api/pages endpoint does NOT return tags.
// We use /api/search with tag filters instead — it returns tags with results.

import type { CleantechIdea, CleanCategory, ImpactArea, IdeaFilter, IdeaStage } from '@/types/idea';

const BS_BASE = process.env.BOOKSTACK_URL ?? 'https://wiki.cleantechhub.net';
const BS_API = `${BS_BASE}/api`;
// No /v1/ prefix — /api/pages not /api/v1/pages (405 otherwise)
const BS_AUTH = `Token ${process.env.BOOKSTACK_TOKEN_ID}:${process.env.BOOKSTACK_TOKEN_SECRET}`;
const BOOK_ID = process.env.BOOKSTACK_BOOK_ID ?? '621';

const bsHeaders = { Authorization: BS_AUTH, 'Content-Type': 'application/json' };

interface BSTag { name: string; value: string; order?: number }
interface BSSearchResult {
  id: number; name: string; slug: string; book_id: number;
  chapter_id: number; tags: BSTag[]; created_at: string;
  updated_at: string; url: string; type: string; preview_html?: string;
}

const COUNTRY_FLAGS: Record<string, string> = {
  'Costa Rica': '🇨🇷',
  'El Salvador': '🇸🇻',
  'Guatemala': '🇬🇹',
  'Colombia': '🇨🇴',
  'Honduras': '🇭🇳',
  'México': '🇲🇽',
  'Nicaragua': '🇳🇮',
  'Panamá': '🇵🇦',
  'Peru': '🇵🇪',
};

const STAGE_ORDER: Record<string, number> = {
  'Ideation': 0, 'Sketches': 1, 'Prototype': 2,
  'Private Beta': 3, 'Public Beta': 4, 'Pre-orders': 5, 'Launched': 6,
};

function tag(tags: BSTag[], name: string): string {
  return tags.find(t => t.name === name)?.value ?? '';
}

function mapSearchResult(p: BSSearchResult): CleantechIdea {
  const tags = p.tags ?? [];
  const country = tag(tags, 'country');
  const stage = tag(tags, 'stage') as IdeaStage;

  return {
    id:             parseInt(tag(tags, 'app_id')) || p.id,
    app_id:         tag(tags, 'app_id'),
    source:         tag(tags, 'source'),
    founder:        tag(tags, 'founder'), // synced from wiki **Founder:** meta via ingest pipeline
    startup_name:   p.name.split(' · ')[0].trim(),
    country,
    city:           '',  // Available in page markdown — loaded on drawer open
    flag:           COUNTRY_FLAGS[country] ?? '',
    description:    '',  // Available in page markdown — loaded on drawer open
    category:       tag(tags, 'category') as CleanCategory,
    impact_areas:   [],  // Available in page markdown — loaded on drawer open
    stage,
    ct_taxonomy:    tag(tags, 'ct_taxonomy') || undefined,
    stage_order:    STAGE_ORDER[stage] ?? 7,
    team_size:      '',
    funded:         '',
    funding_amt:    '',
    website:        '',
    // Deep fields: empty on list — fetched on drawer open
    problem: '', solution: '', revenue_model: '', target_market: '',
    social_impact: '', demand_evidence: '', competitors: '',
    expertise: '', external_support: '', team_roles: '',
    bookstack_page_id:  p.id,
    bookstack_page_url: `${BS_BASE}/books/idea-browser/page/${p.slug}`,
    ingested_at: p.created_at,
  };
}

// ── List / filter (search API — returns tags) ──
export async function fetchIdeasPage(
  offset = 0,
  count = 48,
  filter: Partial<IdeaFilter> = {}
): Promise<{ ideas: CleantechIdea[]; total: number }> {
  // Build search query: base filter ensures only idea pages (tagged with app_id)
  let query = '{type:page} [app_id]';

  // Apply tag-based filters (BookStack search supports multiple [tag=value] — combined with AND)
  if (filter.countries?.length === 1)       query += ` [country=${filter.countries[0]}]`;
  if (filter.categories?.length === 1)      query += ` [category=${filter.categories[0]}]`;
  if (filter.stages?.length === 1)          query += ` [stage=${filter.stages[0]}]`;

  // Search API uses 1-indexed page param
  const page = Math.floor(offset / count) + 1;

  const params = new URLSearchParams({
    query,
    count: String(count),
    page: String(page),
  });

  const res = await fetch(`${BS_API}/search?${params}`, {
    headers: bsHeaders,
    next: { revalidate: 300 }, // cache 5 min
  });

  if (!res.ok) throw new Error(`BookStack API ${res.status}: ${await res.text()}`);
  const json = await res.json();
  const results = (json.data as BSSearchResult[]);
  return { ideas: results.map(mapSearchResult), total: json.total };
}

// ── Full-text search ──
export async function searchIdeas(query: string): Promise<CleantechIdea[]> {
  const params = new URLSearchParams({
    query: `${query} {type:page} [app_id]`,
    count: '30',
  });

  const res = await fetch(`${BS_API}/search?${params}`, {
    headers: bsHeaders,
    next: { revalidate: 60 },
  });

  if (!res.ok) throw new Error(`BookStack search ${res.status}`);
  const json = await res.json();
  return (json.data as BSSearchResult[]).map(mapSearchResult);
}

// ── Full detail for drawer (fetch on open) ──
// Extracts markdown sections AND header metadata lines not available in list view
function extractSection(md: string, heading: string): string {
  const regex = new RegExp(`## ${heading}\\n([\\s\\S]*?)(?=\\n## |$)`);
  return regex.exec(md)?.[1]?.trim() ?? '';
}

function extractMeta(md: string, label: string): string {
  // Matches lines like "**Country:** Costa Rica · San José"
  const regex = new RegExp(`\\*\\*${label}:\\*\\*\\s*(.+)`);
  return regex.exec(md)?.[1]?.trim() ?? '';
}

/** Fetch a single idea page by BookStack page id (search API shape). */
export async function fetchIdeaByPageId(pageId: number): Promise<CleantechIdea | null> {
  const res = await fetch(`${BS_API}/pages/${pageId}`, {
    headers: bsHeaders,
    next: { revalidate: 300 },
  });
  if (!res.ok) return null;
  const p = await res.json();
  const tags: BSTag[] = p.tags ?? [];
  const country = tag(tags, 'country');
  const stage = tag(tags, 'stage') as IdeaStage;
  return {
    id:             parseInt(tag(tags, 'app_id')) || p.id,
    app_id:         tag(tags, 'app_id'),
    source:         tag(tags, 'source'),
    founder:        tag(tags, 'founder'),
    startup_name:   (p.name as string).split(' · ')[0].trim(),
    country,
    city:           '',
    flag:           COUNTRY_FLAGS[country] ?? '',
    description:    '',
    category:       tag(tags, 'category') as CleanCategory,
    impact_areas:   [],
    stage,
    ct_taxonomy:    tag(tags, 'ct_taxonomy') || undefined,
    stage_order:    STAGE_ORDER[stage] ?? 7,
    team_size:      '',
    funded:         '',
    funding_amt:    '',
    website:        '',
    problem: '', solution: '', revenue_model: '', target_market: '',
    social_impact: '', demand_evidence: '', competitors: '',
    expertise: '', external_support: '', team_roles: '',
    bookstack_page_id:  p.id,
    bookstack_page_url: `${BS_BASE}/books/idea-browser/page/${p.slug}`,
    ingested_at: p.created_at,
  };
}

/** Epic Angels: fetch only curated allowlist pages (no full-catalog scan). */
export async function fetchEpicCuratedIdeas(pageIds: number[]): Promise<CleantechIdea[]> {
  const results = await Promise.all(pageIds.map(id => fetchIdeaByPageId(id)));
  return results.filter((i): i is CleantechIdea => i !== null);
}

export async function fetchIdeaDetail(pageId: number): Promise<Partial<CleantechIdea>> {
  const res = await fetch(`${BS_API}/pages/${pageId}`, {
    headers: bsHeaders,
    next: { revalidate: 600 },
  });

  if (!res.ok) throw new Error(`BookStack page ${res.status}`);
  const p = await res.json();
  const md: string = p.markdown ?? '';

  // Extract city from "**Country:** Costa Rica · San José" line
  const countryLine = extractMeta(md, 'Country');
  const city = countryLine.includes('·') ? countryLine.split('·')[1]?.trim() : '';

  // Extract impact areas from "**Impact Areas:** Energy, Agriculture"
  const impactRaw = extractMeta(md, 'Impact Areas');
  const impact_areas = impactRaw ? impactRaw.split(',').map(s => s.trim()).filter(Boolean) as ImpactArea[] : [];

  const founderMeta = extractMeta(md, 'Founder');
  const founderSection = extractSection(md, 'Founder');
  const founder = tag(p.tags ?? [], 'founder')
    || (founderMeta.startsWith('[PENDIENTE]') ? '' : founderMeta)
    || (founderSection.startsWith('[PENDIENTE]') ? '' : founderSection);

  return {
    founder,
    city,
    description:      extractSection(md, 'Elevator Pitch'),
    impact_areas,
    team_size:        extractMeta(md, 'Team Size'),
    website:          extractMeta(md, 'Website').replace('—', ''),
    problem:          extractSection(md, 'Climate Problem'),
    solution:         extractSection(md, 'Solution'),
    revenue_model:    extractSection(md, 'Revenue Model'),
    target_market:    extractSection(md, 'Target Market'),
    social_impact:    extractSection(md, 'Social Impact'),
    demand_evidence:  extractSection(md, 'Demand Evidence'),
    competitors:      extractSection(md, 'Competitors'),
    expertise:        extractSection(md, 'Founder Expertise'),
    external_support: extractSection(md, 'External Support'),
    team_roles:       extractSection(md, 'Team'),
  };
}
