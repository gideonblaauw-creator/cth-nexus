// app/api/rag/route.ts — Server-side proxy to RAG API
// Injects NEXUS_JWT_SECRET on the server so it never reaches the browser

import { NextRequest, NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';

const RAG_URL = process.env.NEXT_PUBLIC_RAG_ENDPOINT ?? 'https://api.cleantechhub.net/rag/ideas/query';
const JWT_SECRET = process.env.NEXUS_JWT_SECRET ?? '';

function makeToken(): string {
  if (!JWT_SECRET) return '';
  return jwt.sign({ sub: 'nexus-frontend' }, JWT_SECRET, { expiresIn: '5m' });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const token = makeToken();

    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(RAG_URL, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const text = await res.text();
      console.error('RAG API error:', res.status, text);
      return NextResponse.json({ error: 'RAG API error' }, { status: res.status });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (err) {
    console.error('RAG proxy error:', err);
    return NextResponse.json({ error: 'RAG proxy error' }, { status: 502 });
  }
}
