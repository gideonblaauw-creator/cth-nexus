'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
import { useIdeaFilter } from '@/hooks/useIdeaFilter';
import { useHighlight } from '@/store/ideaHighlight';
import { FilterSidebar } from '@/components/FilterSidebar';
import { IdeaCard } from '@/components/IdeaCard';
import { IdeaDrawer } from '@/components/IdeaDrawer';
import { RagChatPanel } from '@/components/RagChatPanel';
import type { CleantechIdea } from '@/types/idea';
const PAGE_SIZE = 48;

function IdeaBrowserContent() {
  const { filter, toggle, setQuery, reset, hasActiveFilters } = useIdeaFilter();
  const { ids: highlightedIds } = useHighlight();

  const [ideas, setIdeas]       = useState<CleantechIdea[]>([]);
  const [total, setTotal]       = useState(0);
  const [offset, setOffset]     = useState(0);
  const [loading, setLoading]   = useState(false);
  const [selected, setSelected] = useState<CleantechIdea | null>(null);

  const load = useCallback(async (fresh = false) => {
    setLoading(true);
    const off = fresh ? 0 : offset;
    try {
      const baseParams = {
        ...(filter.query && { q: filter.query }),
        ...(filter.countries[0] && { country: filter.countries[0] }),
        ...(filter.categories[0] && { category: filter.categories[0] }),
        ...(filter.stages[0] && { stage: filter.stages[0] }),
        ...(filter.taxonomies[0] && { taxonomy: filter.taxonomies[0] }),
      };

      const params = new URLSearchParams({
        offset: String(off),
        count: String(PAGE_SIZE),
        ...baseParams,
      });
      const res = await fetch(`/ideas/api/ideas?${params}`);
      const data = await res.json();
      const fetchedIdeas: CleantechIdea[] = data.ideas ?? [];
      const catalogTotal = data.total ?? fetchedIdeas.length;

      let nextIdeas = fetchedIdeas;
      if (filter.impactAreas.length) {
        nextIdeas = nextIdeas.filter(i =>
          filter.impactAreas.some(a => i.impact_areas.includes(a))
        );
      }

      if (!fresh) {
        setIdeas(prev => [...prev, ...nextIdeas]);
      } else {
        setIdeas(nextIdeas);
      }

      setTotal(catalogTotal);
      setOffset(fresh ? PAGE_SIZE : off + PAGE_SIZE);
    } catch (err) {
      console.error('Failed to load ideas:', err);
    } finally {
      setLoading(false);
    }
  }, [filter, offset]);

  // Reload when filters change
  useEffect(() => { load(true); },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(filter)]);

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Filter sidebar */}
      <FilterSidebar
        filter={filter}
        onToggle={toggle}
        onSearch={setQuery}
        onReset={reset}
        hasActiveFilters={hasActiveFilters}
      />

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Stats bar */}
        <div className="flex items-center gap-3 px-6 py-3 border-b border-slate-200 bg-white flex-shrink-0">
          <span className="text-sm text-slate-500">
            <strong className="text-slate-800">{ideas.length}</strong> / {total} ideas
          </span>
          <span className="text-xs text-slate-400">ClimateLaunchpad 2026</span>
        </div>

        {/* Card grid */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {ideas.map(idea => (
              <IdeaCard
                key={idea.app_id}
                idea={idea}
                highlighted={highlightedIds.has(idea.id)}
                onClick={() => setSelected(idea)}
              />
            ))}
          </div>

          {ideas.length < total && !filter.query && (
            <button onClick={() => load(false)} disabled={loading}
              className="mt-6 w-full py-3 border border-slate-200 rounded-xl text-sm text-slate-500
                         hover:border-cth-blue hover:text-cth-blue transition-colors">
              {loading ? 'Loading...' : `Load more (${total - ideas.length} remaining)`}
            </button>
          )}

          {!loading && ideas.length === 0 && (
            <div className="text-center py-20 text-slate-400">
              <p className="text-lg">No ideas found</p>
              <p className="text-sm mt-1">Try adjusting your filters</p>
            </div>
          )}
        </div>
      </div>

      {/* RAG chat panel */}
      <RagChatPanel
        activeFilter={filter}
        onIdeaClick={setSelected}
      />

      {/* Drawer — shared between grid and RAG citations */}
      <IdeaDrawer idea={selected} onClose={() => setSelected(null)} />
    </div>
  );
}

export default function IdeaBrowserPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-screen text-slate-400">Loading...</div>}>
      <IdeaBrowserContent />
    </Suspense>
  );
}
