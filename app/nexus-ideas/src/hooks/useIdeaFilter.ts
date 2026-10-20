// hooks/useIdeaFilter.ts — URL params = single source of truth (shareable via link)

'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import type { IdeaFilter, CleanCategory, ImpactArea, IdeaStage } from '@/types/idea';

export function useIdeaFilter() {
  const params = useSearchParams();
  const router = useRouter();

  const filter: IdeaFilter = {
    countries:   params.getAll('country'),
    categories:  params.getAll('category') as CleanCategory[],
    impactAreas: params.getAll('impact') as ImpactArea[],
    stages:      params.getAll('stage') as IdeaStage[],
    taxonomies:  params.getAll('taxonomy'),
    query:       params.get('q') ?? '',
  };

  function toggle(key: string, value: string) {
    const next = new URLSearchParams(params.toString());

    const existing = next.getAll(key);
    next.delete(key);
    if (existing.includes(value)) {
      existing.filter(v => v !== value).forEach(v => next.append(key, v));
    } else {
      [...existing, value].forEach(v => next.append(key, v));
    }
    router.push(`?${next.toString()}`);
  }

  function setQuery(q: string) {
    const next = new URLSearchParams(params.toString());
    q ? next.set('q', q) : next.delete('q');
    router.push(`?${next.toString()}`);
  }

  function reset() {
    router.push('?');
  }

  const hasActiveFilters = !!(
    filter.countries.length || filter.categories.length ||
    filter.impactAreas.length || filter.stages.length ||
    filter.taxonomies.length || filter.query
  );

  return { filter, toggle, setQuery, reset, hasActiveFilters };
}
