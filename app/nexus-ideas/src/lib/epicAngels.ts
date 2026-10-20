import type { CleantechIdea } from '@/types/idea';
import curatedData from '@/data/epic-angels-curated.json';

export type EpicConfidence = 'strong' | 'provisional';
export type WomenClevelStatus = 'confirmed' | 'PENDIENTE';

export interface EpicCuratedEntry {
  startup_name: string;
  aliases?: string[];
  app_id?: string;
  slug?: string;
  bookstack_page_id?: number;
  fit_note: string;
  confidence: EpicConfidence;
  women_clevel_status: WomenClevelStatus;
  source: string;
  website?: string;
  website_verified?: boolean;
  shareable?: boolean;
  website_verify_status?: string;
  website_verify_note?: string;
  website_final_url?: string;
}

export const EPIC_ANGELS_CURATED = curatedData as EpicCuratedEntry[];

/** APC-facing list: verified company website only (see Archive/apc-share-list.json). */
export const EPIC_SHAREABLE_CURATED = EPIC_ANGELS_CURATED.filter(e => e.shareable);

export const EPIC_SHAREABLE_COUNT = EPIC_SHAREABLE_CURATED.length;

/** Normalize for accent/spacing/punctuation-insensitive matching. */
export function normalizeIdeaName(name: string): string {
  return name
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function namesForEntry(entry: EpicCuratedEntry): string[] {
  return [entry.startup_name, ...(entry.aliases ?? [])].map(normalizeIdeaName);
}

export function matchesEpicCurated(idea: CleantechIdea, entry: EpicCuratedEntry): boolean {
  if (entry.app_id && idea.app_id && entry.app_id === idea.app_id) return true;
  if (entry.bookstack_page_id && idea.bookstack_page_id === entry.bookstack_page_id) return true;
  if (entry.slug && idea.bookstack_page_url?.includes(entry.slug)) return true;

  const ideaNorm = normalizeIdeaName(idea.startup_name);
  for (const nameNorm of namesForEntry(entry)) {
    if (!nameNorm) continue;
    if (ideaNorm === nameNorm) return true;
    // Idea name contains alias (e.g. CLIMATIK within BARUK COMPANY BIO CLIMATIK SAS)
    if (nameNorm.length >= 4 && ideaNorm.includes(nameNorm)) return true;
  }
  return false;
}

export function filterEpicAngelsIdeas(ideas: CleantechIdea[]): CleantechIdea[] {
  return ideas.filter(idea => EPIC_ANGELS_CURATED.some(entry => matchesEpicCurated(idea, entry)));
}

export function isEpicAngelsIdea(idea: CleantechIdea): boolean {
  return EPIC_ANGELS_CURATED.some(entry => matchesEpicCurated(idea, entry));
}

export function getEpicCuratedEntry(idea: CleantechIdea): EpicCuratedEntry | undefined {
  return EPIC_ANGELS_CURATED.find(entry => matchesEpicCurated(idea, entry));
}
