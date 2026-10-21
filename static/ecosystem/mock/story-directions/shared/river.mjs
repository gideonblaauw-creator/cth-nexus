import { actorLabel } from './water-loader.mjs';

const CHAPTERS = ['challenges', 'policy', 'hubs', 'data', 'partnerships', 'capital'];
const COL_W = 180;

export function buildRiverModel(bundle) {
  const nodeChapter = new Map();
  const nodes = new Map();
  CHAPTERS.forEach((chId, col) => {
    const scene = bundle.getScene(col);
    [...(scene.nodeIds || [])].forEach((id) => {
      if (!nodeChapter.has(id)) nodeChapter.set(id, col);
      if (!nodes.has(id)) {
        nodes.set(id, {
          id,
          col,
          label: actorLabel(bundle.byId, id),
          kind: id.startsWith('challenge:') ? 'challenge' : 'actor',
        });
      }
    });
  });

  const links = [];
  const addLink = (e, suggested) => {
    const s = e.source;
    const t = e.target;
    if (!nodes.has(s) || !nodes.has(t)) return;
    const sc = nodeChapter.get(s) ?? 0;
    const tc = nodeChapter.get(t) ?? 0;
    if (sc > tc) return;
    links.push({ source: s, target: t, type: e.type, suggested, sc, tc });
  };

  CHAPTERS.forEach((_, col) => {
    const scene = bundle.getScene(col);
    (scene.realRels || []).forEach((e) => addLink(e, false));
    (scene.suggested || []).forEach((e) => addLink(e, true));
  });

  return { nodes: [...nodes.values()], links, chapters: CHAPTERS };
}

export function renderRiver(svg, model, bundle, hoverId = null) {
  const width = svg.clientWidth || 1200;
  const height = svg.clientHeight || 600;
  const cols = model.chapters.length;
  const margin = { top: 36, bottom: 24, left: 24, right: 140 };
  const innerW = width - margin.left - margin.right;
  const colX = (c) => margin.left + (c + 0.5) * (innerW / cols);

  const byCol = Array.from({ length: cols }, () => []);
  model.nodes.forEach((n) => byCol[n.col].push(n));
  byCol.forEach((list, c) => {
    list.sort((a, b) => a.label.localeCompare(b.label));
    list.forEach((n, i) => {
      n.x = colX(c);
      n.y = margin.top + ((i + 1) / (list.length + 1)) * (height - margin.top - margin.bottom);
    });
  });
  const nodePos = new Map(model.nodes.map((n) => [n.id, n]));

  const connected = new Set();
  if (hoverId) {
    connected.add(hoverId);
    model.links.forEach((l) => {
      if (l.source === hoverId || l.target === hoverId) {
        connected.add(l.source);
        connected.add(l.target);
      }
    });
    // extend one hop for path feel
    model.links.forEach((l) => {
      if (connected.has(l.source)) connected.add(l.target);
      if (connected.has(l.target)) connected.add(l.source);
    });
  }

  const parts = [];
  parts.push(`<rect width="100%" height="100%" fill="#fafcfe"/>`);
  model.chapters.forEach((ch, i) => {
    const titles = bundle.storyConfig.chapters[i]?.title?.es || ch;
    parts.push(`<text class="col-label" x="${colX(i)}" y="20" text-anchor="middle">${escapeHtml(titles.replace(/^\d+\s·\s*/, ''))}</text>`);
  });

  model.links.forEach((l) => {
    const a = nodePos.get(l.source);
    const b = nodePos.get(l.target);
    if (!a || !b) return;
    const dim = hoverId && !connected.has(l.source) && !connected.has(l.target);
    const cls = l.suggested ? 'band-suggested' : 'band-verified';
    const op = dim ? 0.08 : 1;
    const mx = (a.x + b.x) / 2;
    parts.push(`<path class="${cls}" style="opacity:${op}" d="M ${a.x} ${a.y} C ${mx} ${a.y}, ${mx} ${b.y}, ${b.x} ${b.y}"/>`);
  });

  model.nodes.forEach((n) => {
    const dim = hoverId && !connected.has(n.id);
    const hot = hoverId === n.id;
    const r = n.kind === 'challenge' ? 11 : 8;
    const fill = n.kind === 'challenge' ? '#2a9d8f' : '#0c498a';
    parts.push(`<g class="river-node" data-id="${escapeAttr(n.id)}">
      <circle class="node-circle${dim ? ' dim' : ''}${hot ? ' hot' : ''}" cx="${n.x}" cy="${n.y}" r="${r}" fill="${fill}"/>
      <text class="node-label" x="${n.x}" y="${n.y + 18}" text-anchor="middle">${escapeHtml(trunc(n.label, 22))}</text>
    </g>`);
  });

  svg.innerHTML = parts.join('');
}

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
}
function escapeAttr(s) {
  return escapeHtml(s);
}
function trunc(s, n) {
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
}

export function renderLocator(el, bundle) {
  const g = bundle.storyConfig.challenges['challenge:PE-2-agua']?.geo;
  if (!el || !g) return;
  const x = 50 + (g.lng + 81) * 2.2;
  const y = 55 - (g.lat + 18) * 2.5;
  el.innerHTML = `<div class="locator-map" aria-label="Locator Perú"><span class="dot" style="left:${x}%;top:${y}%"></span><span class="lbl">PE · Agua</span></div>`;
}
