// app/api/ideas/route.ts — Server-side proxy to BookStack API
// Keeps BookStack credentials out of the browser

import { NextRequest, NextResponse } from 'next/server';
import { fetchIdeasPage, searchIdeas } from '@/lib/bookstack';

export async function GET(req: NextRequest) {
  const params = req.nextUrl.searchParams;
  const q = params.get('q') ?? '';
  const offset = parseInt(params.get('offset') ?? '0');
  const count = parseInt(params.get('count') ?? '48');

  try {
    if (q) {
      const ideas = await searchIdeas(q);
      return NextResponse.json({ ideas, total: ideas.length });
    }

    const taxonomy = params.get('taxonomy') ?? '';

    const filter = {
      countries: params.get('country') ? [params.get('country')!] : [],
      categories: params.get('category') ? [params.get('category')! as any] : [],
      impactAreas: [],
      stages: params.get('stage') ? [params.get('stage')! as any] : [],
      taxonomies: [] as string[],
      query: '',
    };

    const result = await fetchIdeasPage(offset, count, filter);

    // Client-side sector filtering: taxonomy param is a sector code like 'af'
    if (taxonomy) {
      const prefix = `CT-${taxonomy.toUpperCase()}-`;
      result.ideas = result.ideas.filter(i => i.ct_taxonomy?.startsWith(prefix));
      result.total = result.ideas.length;
    }

    return NextResponse.json(result);
  } catch (err) {
    console.error('BookStack API error:', err);
    return NextResponse.json({ error: 'BookStack API error' }, { status: 502 });
  }
}
