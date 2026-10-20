'use client';

import type { CleantechIdea } from '@/types/idea';
import { CATEGORY_STYLES, STAGE_STYLES, SECTOR_STYLES, TAXONOMY_NODES, sectorFromCode } from '@/lib/ideaStyles';

function initials(name: string) {
  return name.split(' ').filter(Boolean).slice(0, 2).map(n => n[0].toUpperCase()).join('');
}

interface Props {
  idea: CleantechIdea;
  highlighted?: boolean;
  onClick: () => void;
}

export function IdeaCard({ idea, highlighted, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      className={[
        'bg-white rounded-xl border p-4 cursor-pointer flex flex-col gap-3',
        'transition-all duration-150 hover:border-cth-blue hover:shadow-lg hover:-translate-y-px',
        highlighted
          ? 'ring-2 ring-cth-blue border-cth-blue'
          : 'border-slate-200',
      ].join(' ')}
    >
      {/* Startup name + founder + flag */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="font-bold text-slate-800 text-sm leading-snug">{idea.startup_name}</p>
          {idea.founder && (
            <div className="flex items-center gap-1.5 mt-1">
              <span className="w-5 h-5 rounded-full bg-gradient-to-br from-sky-400 to-emerald-600
                               text-white text-[9px] font-bold flex items-center justify-center flex-shrink-0">
                {initials(idea.founder)}
              </span>
              <span className="text-xs text-slate-400">{idea.founder}</span>
            </div>
          )}
        </div>
        <span className="text-2xl flex-shrink-0" title={idea.country}>{idea.flag}</span>
      </div>

      {idea.ct_taxonomy && (
        <span className={`self-start text-[10px] font-bold px-2 py-0.5 rounded border
                          ${SECTOR_STYLES[sectorFromCode(idea.ct_taxonomy)] ?? 'bg-slate-100 text-slate-600 border-slate-200'}`}>
          {TAXONOMY_NODES[idea.ct_taxonomy] ?? idea.ct_taxonomy}
        </span>
      )}

      {/* Description */}
      <p className="text-xs text-slate-500 leading-relaxed line-clamp-3">{idea.description}</p>

      {/* Badges */}
      <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100 mt-auto">
        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${CATEGORY_STYLES[idea.category] ?? ''}`}>
          {idea.category}
        </span>
        {idea.impact_areas.slice(0, 2).map(tag => (
          <span key={tag} className="text-[10px] font-semibold px-2 py-0.5 rounded-full
                                     bg-slate-100 text-slate-500 border border-slate-200">
            {tag}
          </span>
        ))}
        <span className={`ml-auto text-[10px] font-semibold px-2 py-0.5 rounded-full ${STAGE_STYLES[idea.stage] ?? ''}`}>
          {idea.stage}
        </span>
      </div>

      {idea.city && <p className="text-[10.5px] text-slate-400">{idea.city}</p>}
    </div>
  );
}
