// app/api/ideas/[pageId]/route.ts — Fetch full idea detail from BookStack
// Used by IdeaDrawer to get deep fields (problem, solution, etc.)

import { NextRequest, NextResponse } from 'next/server';
import { fetchIdeaDetail } from '@/lib/bookstack';

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ pageId: string }> }
) {
  const { pageId } = await params;
  const id = parseInt(pageId);
  if (!id || isNaN(id)) {
    return NextResponse.json({ error: 'Invalid page ID' }, { status: 400 });
  }

  try {
    const detail = await fetchIdeaDetail(id);
    return NextResponse.json(detail);
  } catch (err) {
    console.error(`BookStack detail error for page ${id}:`, err);
    return NextResponse.json({ error: 'Failed to fetch idea detail' }, { status: 502 });
  }
}
