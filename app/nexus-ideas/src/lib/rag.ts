// lib/rag.ts — Client-side RAG query via server-side proxy
// The proxy at /api/rag injects the JWT secret — no credentials leave the server

import type { IdeaFilter, RagQueryResponse } from '@/types/idea';

export async function queryIdeas(
  query: string,
  filter: IdeaFilter,
  history: Array<{ role: string; content: string }>,
): Promise<RagQueryResponse> {
  const res = await fetch('/ideas/api/rag', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      filters: {
        ...(filter.countries[0] && { country: filter.countries[0] }),
        ...(filter.categories[0] && { category: filter.categories[0] }),
        ...(filter.stages[0] && { stage: filter.stages[0] }),
      },
      top_k: 5,
      conversation_history: history.slice(-6),
    }),
  });

  if (!res.ok) throw new Error(`RAG endpoint returned ${res.status}`);
  return res.json();
}
