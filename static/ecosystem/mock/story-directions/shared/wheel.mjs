import { actorLabel } from './water-loader.mjs';

export function renderWheel(svg, bundle, maxRing) {
  const width = svg.clientWidth || 900;
  const height = svg.clientHeight || 640;
  const cx = width / 2;
  const cy = height / 2;
  const rings = bundle.storyConfig.chapters.length;
  const maxR = Math.min(width, height) * 0.42;
  const nodeMap = new Map();

  for (let ri = 0; ri < maxRing; ri += 1) {
    const scene = bundle.getScene(ri);
    const ids = [...scene.nodeIds].filter((id) => !id.startsWith('dataset:'));
    const r = maxR * ((ri + 1) / (rings + 0.5));
    ids.forEach((id, i) => {
      if (nodeMap.has(id)) return;
      const angle = (i / Math.max(ids.length, 1)) * Math.PI * 2 - Math.PI / 2;
      nodeMap.set(id, {
        id,
        x: cx + Math.cos(angle) * r,
        y: cy + Math.sin(angle) * r,
        ring: ri,
        label: actorLabel(bundle.byId, id),
      });
    });
  }

  const challenge = bundle.storyConfig.challenges['challenge:PE-2-agua'];
  const parts = [];
  parts.push(`<rect width="100%" height="100%" fill="#f8fafc"/>`);
  for (let ri = 0; ri < maxRing; ri += 1) {
    const r = maxR * ((ri + 1) / (rings + 0.5));
    parts.push(`<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#d1e3f8" stroke-width="1.5"/>`);
    const t = bundle.storyConfig.chapters[ri]?.title?.es || '';
    parts.push(`<text x="${cx + r - 8}" y="${cy - 4}" font-size="9" fill="#94a3b8" text-anchor="end">${escapeHtml(t.replace(/^\d+\s·\s*/, ''))}</text>`);
  }
  parts.push(`<circle cx="${cx}" cy="${cy}" r="36" fill="#2a9d8f"/>`);
  parts.push(`<text x="${cx}" y="${cy + 4}" text-anchor="middle" fill="#fff" font-size="10" font-weight="700">Agua PE</text>`);

  [...nodeMap.values()].forEach((n) => {
    parts.push(`<g class="wheel-node" data-id="${escapeAttr(n.id)}" style="cursor:pointer">
      <circle cx="${n.x}" cy="${n.y}" r="9" fill="#0c498a" stroke="#fff" stroke-width="2"/>
      <text x="${n.x}" y="${n.y + 20}" text-anchor="middle" font-size="8" fill="#0c498a">${escapeHtml(trunc(n.label, 16))}</text>
    </g>`);
  });

  svg.innerHTML = parts.join('');
}

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
}
function escapeAttr(s) {
  return escapeHtml(s);
}
function trunc(s, n) {
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
}
