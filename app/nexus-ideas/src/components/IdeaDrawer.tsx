'use client';

import { useEffect, useState } from 'react';
import type { CleantechIdea } from '@/types/idea';
import { CATEGORY_STYLES, STAGE_STYLES, SECTOR_STYLES, TAXONOMY_NODES, SECTOR_LABELS, sectorFromCode } from '@/lib/ideaStyles';

// Drawer fetches deep fields from the API route on open
async function fetchDetail(pageId: number): Promise<Partial<CleantechIdea>> {
  const res = await fetch(`/ideas/api/ideas/${pageId}`);
  if (!res.ok) return {};
  return res.json();
}

function initials(name = '') {
  return name.split(' ').filter(Boolean).slice(0, 2).map(n => n[0]).join('');
}

function Section({ title, text }: { title: string; text?: string }) {
  if (!text?.trim()) return null;
  return (
    <div className="flex flex-col gap-1.5">
      <p className="text-[10px] font-bold tracking-wider uppercase text-cth-blue">{title}</p>
      <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">{text}</p>
    </div>
  );
}

interface Props {
  idea: CleantechIdea | null;
  onClose: () => void;
}

export function IdeaDrawer({ idea, onClose }: Props) {
  const [detail, setDetail] = useState<Partial<CleantechIdea>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!idea?.bookstack_page_id) { setDetail({}); return; }
    setLoading(true);
    fetchDetail(idea.bookstack_page_id)
      .then(setDetail)
      .finally(() => setLoading(false));
  }, [idea?.bookstack_page_id]);

  // Merge card-level fields with deep detail
  const m = { ...idea, ...detail } as CleantechIdea;

  return (
    <>
      {/* Overlay */}
      <div
        onClick={onClose}
        className={`fixed inset-0 bg-black/40 z-40 transition-opacity
                    ${idea ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
      />

      {/* Drawer panel */}
      <div className={`fixed right-0 top-0 bottom-0 w-full max-w-[680px] bg-white z-50
                       shadow-2xl flex flex-col transition-transform duration-200
                       ${idea ? 'translate-x-0' : 'translate-x-full'}`}>

        {/* Header */}
        <div className="bg-cth-blue p-6 flex-shrink-0">
          <div className="flex items-start gap-3">
            <span className="text-4xl flex-shrink-0 mt-1">{idea?.flag}</span>
            <div className="flex-1 min-w-0">
              <h2 className="text-white font-bold text-lg leading-snug">{idea?.startup_name}</h2>
              {m.founder && (
                <div className="flex items-center gap-2 mt-2">
                  <div className="w-7 h-7 rounded-full bg-white/20 border-2 border-white/30
                                  text-white text-xs font-bold flex items-center justify-center">
                    {initials(m.founder)}
                  </div>
                  <div>
                    <p className="text-cth-cyan text-sm font-semibold">{m.founder}</p>
                    <p className="text-white/60 text-xs">
                      {[m.city, m.country].filter(Boolean).join(', ')}
                    </p>
                  </div>
                </div>
              )}
            </div>
            <button onClick={onClose}
              className="w-8 h-8 rounded-lg bg-white/15 text-white flex items-center
                         justify-center hover:bg-white/25 transition-colors text-lg">
              &times;
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-4">
            <span className={`text-[10.5px] font-semibold px-2.5 py-0.5 rounded-full ${CATEGORY_STYLES[idea?.category ?? ''] ?? ''}`}>
              {idea?.category}
            </span>
            <span className={`text-[10.5px] font-semibold px-2.5 py-0.5 rounded-full ${STAGE_STYLES[idea?.stage ?? ''] ?? ''}`}>
              {idea?.stage}
            </span>
            {idea?.ct_taxonomy && (() => {
              const sector = sectorFromCode(idea.ct_taxonomy!);
              const sectorLabel = SECTOR_LABELS[sector] ?? sector.toUpperCase();
              const nodeLabel = TAXONOMY_NODES[idea.ct_taxonomy!] ?? idea.ct_taxonomy;
              return (
                <span className={`text-xs font-bold px-2.5 py-1 rounded border
                                  ${SECTOR_STYLES[sector] ?? 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                  {sectorLabel} &middot; {idea.ct_taxonomy} &mdash; {nodeLabel}
                </span>
              );
            })()}
            {idea?.impact_areas?.map(tag => (
              <span key={tag} className="text-[10.5px] font-semibold px-2.5 py-0.5
                                         rounded-full bg-white/20 text-white">{tag}</span>
            ))}
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-5">
          {loading && <p className="text-sm text-slate-400 animate-pulse">Loading details...</p>}
          <Section title="About"               text={m.description} />
          <hr className="border-slate-100" />
          <Section title="Climate Problem"     text={m.problem} />
          <hr className="border-slate-100" />
          <Section title="Solution"            text={m.solution} />
          <hr className="border-slate-100" />
          <Section title="Revenue Model"       text={m.revenue_model} />
          <hr className="border-slate-100" />
          <Section title="Target Market"       text={m.target_market} />
          <hr className="border-slate-100" />
          <Section title="Social Impact"       text={m.social_impact} />
          <hr className="border-slate-100" />
          <Section title="Demand Evidence"     text={m.demand_evidence} />
          <hr className="border-slate-100" />
          <Section title="Competitors"         text={m.competitors} />
          <hr className="border-slate-100" />
          <Section title="Founder Expertise"   text={m.expertise} />
          <hr className="border-slate-100" />
          <Section title="External Support"    text={m.external_support} />

          {(m.team_size || (m.funded && m.funded.toLowerCase() !== 'no')) && (
            <>
              <hr className="border-slate-100" />
              <div className="grid grid-cols-2 gap-4">
                {m.team_size && (
                  <Section title="Team"
                    text={`${m.team_size} person(s)${m.team_roles ? ' - ' + m.team_roles : ''}`} />
                )}
                {m.funded && m.funded.toLowerCase() !== 'no' && (
                  <Section title="Funding"
                    text={`${m.funded}${m.funding_amt ? ' - $' + m.funding_amt : ''}`} />
                )}
              </div>
            </>
          )}

          {m.website && m.website.length > 3 && (
            <>
              <hr className="border-slate-100" />
              <div className="flex flex-col gap-1.5">
                <p className="text-[10px] font-bold tracking-wider uppercase text-cth-blue">Website</p>
                <a href={m.website.startsWith('http') ? m.website : `https://${m.website}`}
                   target="_blank" rel="noopener noreferrer"
                   className="text-sm text-cth-blue hover:underline">{m.website}</a>
              </div>
            </>
          )}


        </div>
      </div>
    </>
  );
}
