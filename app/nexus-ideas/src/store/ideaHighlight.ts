// store/ideaHighlight.ts — Zustand store bridging RAG chat citations to card grid highlighting

import { create } from 'zustand';

interface HighlightStore {
  ids: Set<number>;
  set: (ids: number[]) => void;
  clear: () => void;
}

export const useHighlight = create<HighlightStore>(set => ({
  ids: new Set(),
  set: (ids) => {
    set({ ids: new Set(ids) });
    // Auto-clear after 8 seconds so highlights don't persist forever
    setTimeout(() => set({ ids: new Set() }), 8000);
  },
  clear: () => set({ ids: new Set() }),
}));
