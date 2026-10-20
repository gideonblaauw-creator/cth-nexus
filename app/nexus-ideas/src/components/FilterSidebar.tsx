'use client';

import { useEffect, useState } from 'react';
import type { IdeaFilter, CleanCategory, ImpactArea, IdeaStage, CTSector } from '@/types/idea';
import { SECTOR_LABELS, SECTOR_COLORS } from '@/lib/ideaStyles';
const CATEGORIES: CleanCategory[] = [
  'Food & Agriculture', 'Clean Industry', 'Air & Environment',
  'Efficiency', 'Water', 'Clean Energy', 'Transportation', 'Energy Storage',
];
const IMPACTS: ImpactArea[] = ['Circular Economy', 'Nature-Based', 'Mitigation', 'Adaptation'];
const STAGES: IdeaStage[] = ['Ideation', 'Sketches', 'Prototype', 'Private Beta', 'Public Beta', 'Pre-orders', 'Launched'];
const SECTORS: CTSector[] = ['af', 'bu', 'en', 'ic', 'in', 'tr', 'wa', 'ww', 'xs'];
const COUNTRIES = ['Colombia', 'Costa Rica', 'El Salvador', 'Guatemala', 'Honduras', 'México', 'Nicaragua', 'Panamá', 'Peru'];

interface Props {
  filter: IdeaFilter;
  onToggle: (key: string, value: string) => void;
  onSearch: (q: string) => void;
  onReset: () => void;
  hasActiveFilters: boolean;
}

function FilterPill({ label, active, color, onClick }: {
  label: string; active: boolean; color?: string; onClick: () => void;
}) {
  return (
    <button onClick={onClick}
      className={`flex items-center gap-2 w-full px-2.5 py-1.5 rounded-lg text-xs text-left
                  transition-colors ${active ? 'bg-cth-blue text-white font-semibold' : 'hover:bg-slate-50 text-slate-700'}`}>
      {color && <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />}
      <span className="flex-1">{label}</span>
    </button>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-4">
      <p className="text-[10px] font-bold tracking-widest uppercase text-slate-400 mb-2">{label}</p>
      <div className="flex flex-col gap-0.5">{children}</div>
    </div>
  );
}

export function FilterSidebar({ filter, onToggle, onSearch, onReset, hasActiveFilters }: Props) {
  const [q, setQ] = useState(filter.query);

  useEffect(() => {
    const t = setTimeout(() => onSearch(q), 300);
    return () => clearTimeout(t);
  }, [q, onSearch]);

  return (
    <aside className="w-64 flex-shrink-0 bg-white border-r border-slate-200 overflow-y-auto p-4">
      <div className="mb-5">
        <p className="text-[10px] font-bold tracking-widest uppercase text-slate-400 mb-2">Search</p>
        <input
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="Startups, keywords..."
          className="w-full text-xs border border-slate-200 rounded-lg px-3 py-2
                     focus:outline-none focus:border-cth-blue bg-slate-50"
        />
      </div>

      <hr className="border-slate-100 mb-4" />

      <Section label="Country">
        {COUNTRIES.map(c => (
          <FilterPill key={c} label={c} active={filter.countries.includes(c)}
            onClick={() => onToggle('country', c)} />
        ))}
      </Section>

      <hr className="border-slate-100 mb-4" />

      <Section label="Category">
        {CATEGORIES.map(c => (
          <FilterPill key={c} label={c} active={filter.categories.includes(c)}
            onClick={() => onToggle('category', c)} />
        ))}
      </Section>

      <hr className="border-slate-100 mb-4" />

      <Section label="CTH Taxonomy">
        {SECTORS.map(s => (
          <FilterPill key={s} label={SECTOR_LABELS[s]} active={filter.taxonomies.includes(s)}
            color={SECTOR_COLORS[s]}
            onClick={() => onToggle('taxonomy', s)} />
        ))}
      </Section>

      <hr className="border-slate-100 mb-4" />

      <Section label="Impact Area">
        {IMPACTS.map(i => (
          <FilterPill key={i} label={i} active={filter.impactAreas.includes(i)}
            onClick={() => onToggle('impact', i)} />
        ))}
      </Section>

      <hr className="border-slate-100 mb-4" />

      <Section label="Stage">
        {STAGES.map(s => (
          <FilterPill key={s} label={s} active={filter.stages.includes(s)}
            onClick={() => onToggle('stage', s)} />
        ))}
      </Section>

      {hasActiveFilters && (
        <button onClick={onReset}
          className="mt-2 w-full py-2 border border-slate-200 rounded-lg text-xs font-semibold
                     text-slate-500 hover:border-cth-blue hover:text-cth-blue transition-colors">
          Clear all filters
        </button>
      )}
    </aside>
  );
}
