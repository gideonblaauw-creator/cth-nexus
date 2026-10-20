import type { CleantechIdea } from '@/types/idea';
import curatedData from '@/data/imd-peru-curated.json';

export interface ImdPeruCuratedEntry {
  slug: string;
  name: string;
  country: string;
  website?: string;
  program: string;
  theme: string;
  stage: string;
  founder?: string;
  shareable?: boolean;
  nexus_path?: string;
  ct1?: string;
  desc_en?: string;
  desc_es?: string;
}

export const IMD_PERU_CURATED = curatedData as ImdPeruCuratedEntry[];

/** Live filter allowlist: Archive shareable rows only (HardTech excluded). */
export const IMD_PERU_SHAREABLE = IMD_PERU_CURATED.filter(e => e.shareable !== false);

export const IMD_PERU_SHAREABLE_COUNT = IMD_PERU_SHAREABLE.length;

export function normalizeIdeaName(name: string): string {
  return name
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function slugTail(path?: string): string {
  if (!path) return '';
  const parts = path.replace(/^\/+/, '').split('/');
  return parts[parts.length - 1] ?? '';
}

export function matchesImdPeruCurated(idea: CleantechIdea, entry: ImdPeruCuratedEntry): boolean {
  const entrySlug = entry.slug || slugTail(entry.nexus_path);
  if (entrySlug && idea.bookstack_page_url?.includes(entrySlug)) return true;

  const ideaNorm = normalizeIdeaName(idea.startup_name);
  const entryNorm = normalizeIdeaName(entry.name);
  if (ideaNorm === entryNorm) return true;
  if (entryNorm.length >= 4 && ideaNorm.includes(entryNorm)) return true;
  return false;
}

export function filterImdPeruIdeas(ideas: CleantechIdea[]): CleantechIdea[] {
  return ideas.filter(idea => IMD_PERU_SHAREABLE.some(entry => matchesImdPeruCurated(idea, entry)));
}

export function isImdPeruIdea(idea: CleantechIdea): boolean {
  return IMD_PERU_SHAREABLE.some(entry => matchesImdPeruCurated(idea, entry));
}
