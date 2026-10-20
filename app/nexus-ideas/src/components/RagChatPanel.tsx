'use client';

import { useState, useRef, useEffect } from 'react';
import { queryIdeas } from '@/lib/rag';
import { useHighlight } from '@/store/ideaHighlight';
import type { CleantechIdea, IdeaFilter, RagQueryResponse } from '@/types/idea';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  ideas?: CleantechIdea[];
}

const STARTERS = [
  'Water tech ideas at prototype stage',
  'Who is working on circular economy in Peru?',
  'Launched startups with a subscription model',
];

interface Props {
  activeFilter: IdeaFilter;
  onIdeaClick: (idea: CleantechIdea) => void;
}

export function RagChatPanel({ activeFilter, onIdeaClick }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const { set: setHighlighted } = useHighlight();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function send(text?: string) {
    const q = (text ?? input).trim();
    if (!q || loading) return;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: q }]);
    setLoading(true);

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      const res: RagQueryResponse = await queryIdeas(q, activeFilter, history);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.answer,
        ideas: res.ideas,
      }]);
      if (res.highlighted_ids?.length) {
        setHighlighted(res.highlighted_ids);
      }
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Could not reach the RAG endpoint. Check the OVH VPS service is running.',
      }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`flex flex-col bg-white border-l border-slate-200 transition-all duration-200
                     ${collapsed ? 'w-10' : 'w-80'} flex-shrink-0`}>

      {/* Toggle bar */}
      <button onClick={() => setCollapsed(!collapsed)}
        className="h-12 flex items-center justify-center gap-2 px-3 border-b border-slate-200
                   text-xs font-semibold text-slate-500 hover:bg-slate-50 flex-shrink-0">
        {collapsed ? (
          <span title="Open AI chat">AI</span>
        ) : (
          <>
            <span>Ask AI</span>
            <span className="ml-auto text-slate-300">&times;</span>
          </>
        )}
      </button>

      {!collapsed && (
        <>
          {/* Starter prompts */}
          {messages.length === 0 && (
            <div className="p-4">
              <p className="text-xs font-semibold text-slate-600 mb-2">Try asking...</p>
              {STARTERS.map(s => (
                <button key={s} onClick={() => send(s)}
                  className="block w-full text-left text-xs text-slate-400 hover:text-cth-blue
                             py-1 leading-relaxed transition-colors">
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-3">
            {messages.map((msg, i) => (
              <div key={i} className={`flex flex-col gap-2 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`text-xs rounded-lg px-3 py-2 max-w-[95%] leading-relaxed whitespace-pre-line
                  ${msg.role === 'user' ? 'bg-cth-blue text-white' : 'bg-slate-100 text-slate-700'}`}>
                  {msg.content}
                </div>
                {/* Cited ideas — clicking opens same IdeaDrawer as card grid */}
                {msg.ideas?.map(idea => (
                  <button key={idea.id} onClick={() => onIdeaClick(idea)}
                    className="text-left text-[10.5px] font-semibold px-2.5 py-1.5 rounded-lg
                               border border-cth-blue/20 bg-blue-50 text-cth-blue
                               hover:bg-blue-100 transition-colors w-full">
                    {idea.flag} {idea.startup_name}
                    {idea.founder && (
                      <span className="text-slate-400 font-normal"> - {idea.founder}</span>
                    )}
                  </button>
                ))}
              </div>
            ))}
            {loading && <p className="text-xs text-slate-400 px-1 animate-pulse">Searching ideas...</p>}
            <div ref={endRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t border-slate-200 flex gap-2">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
              placeholder="Ask about ideas..."
              className="flex-1 text-xs border border-slate-200 rounded-lg px-3 py-2
                         focus:outline-none focus:border-cth-blue bg-slate-50"
            />
            <button
              onClick={() => send()}
              disabled={loading || !input.trim()}
              className="px-3 py-2 bg-cth-blue text-white text-xs rounded-lg
                         hover:bg-cth-blue/90 disabled:opacity-40 transition-colors"
            >
              Send
            </button>
          </div>
        </>
      )}
    </div>
  );
}
