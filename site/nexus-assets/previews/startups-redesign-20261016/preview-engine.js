/* Shared data + filter engine for startups redesign previews (2026-10-16) */
(function (global) {
  const FLAGS = { CO: '\u{1F1E8}\u{1F1F4}', MX: '\u{1F1F2}\u{1F1FD}', CL: '\u{1F1E8}\u{1F1F1}', PE: '\u{1F1F5}\u{1F1EA}', ES: '\u{1F1EA}\u{1F1F8}', PA: '\u{1F1F5}\u{1F1E6}', GT: '\u{1F1EC}\u{1F1F9}', CR: '\u{1F1E8}\u{1F1F7}', SV: '\u{1F1F8}\u{1F1FB}', INT: '\u{1F30D}' };
  const COUNTRY_LABEL = { CO: 'Colombia', MX: 'Mexico', CL: 'Chile', PE: 'Peru', ES: 'Spain', PA: 'Panama', GT: 'Guatemala', CR: 'Costa Rica', SV: 'El Salvador', INT: 'International' };
  const CT_SECTORS = [
    { id: 'AF', label: 'Agriculture & Food' },
    { id: 'EN', label: 'Energy' },
    { id: 'WA', label: 'Waste & Circular' },
    { id: 'WW', label: 'Water' },
    { id: 'TR', label: 'Transport' },
    { id: 'IC', label: 'Climate Tech / Data' },
    { id: 'XS', label: 'Cross-sector / Finance' },
    { id: 'IN', label: 'Industry' },
    { id: 'BU', label: 'Built Environment' },
    { id: 'EX', label: 'Other' },
  ];
  const PROGRAMS = ['CLAC21', 'CLAC22', 'CLAC23', 'CLAC24', 'CLAC25', 'CLP', 'CLP20', 'CLP25'];
  const STAGES = ['Pre-Seed', 'Seed', 'Pre-Series A', 'Series A', 'Series B+'];
  const THEMES = [{ id: 'CE', label: 'Circular' }, { id: 'BIO', label: 'Bioeconomy' }, { id: 'EN', label: 'Energy' }];

  const EPIC_ALLOWLIST_SLUGS = new Set([
    'curuba', 'amazoniko', 'e-wai', 'chumchum', 'o3-smart-cities', 'green-leaf', 'bio-natural-solutions',
    'communitylab', 'basilisco', 'reemade', 'xiclo', 'ecopoop', 'seos-energy', 'bioambientar', 'biogar',
    'gescol', 'matter-of-trust', 'cirkula',
  ]);
  const EPIC_SLUG_LEGACY = {
    'o3-smart-cities': 'O3 SMART CITIES', 'green-leaf': 'GREEN LEAF', 'bio-natural-solutions': 'BIO NATURAL SOLUTIONS',
    basilisco: 'BASÍLISCO', reemade: 'REEMADE', xiclo: 'XICLO', ecopoop: 'ECO POOP',
    'seos-energy': 'SEOS ENERGY SAS BIC', bioambientar: 'BIOAMBIENTAR', biogar: 'BIOGAR', gescol: 'GESCOL SAS BIC',
  };

  let S = [];
  let EPIC_CARDS = [];
  let IMD_CARDS = [];
  let CLP_CARDS = [];

  let epicOnly = new URLSearchParams(location.search).get('epic') === '1';
  let imdOnly = new URLSearchParams(location.search).get('imd_pe') === '1';
  let clpOnly = new URLSearchParams(location.search).get('clp26') === '1';
  if (epicOnly && imdOnly) imdOnly = false;
  if (clpOnly && (epicOnly || imdOnly)) clpOnly = false;

  let fProg = new Set();
  let fTheme = new Set();
  let fStage = new Set();
  let fCountry = new Set();
  let fCtSector = new Set();
  let webOnly = !epicOnly && !imdOnly && !clpOnly;
  let lang = 'EN';

  function normalizeProgram(p) {
    if (!p) return 'CLP';
    if (p === 'CLP26') return 'CLP';
    if (p === 'GIZ Growth Services') return 'CLP';
    return p;
  }
  function normalizeStage(st) {
    if (!st || st === '[PENDIENTE]' || st === 'Launched') return st === 'Launched' ? 'Seed' : st || 'Seed';
    if (st === 'Private Beta') return 'Pre-Seed';
    if (st === 'Public Beta') return 'Pre-Series A';
    return st;
  }
  function ctSector(s) {
    const id = s.ct1 || s.ct2 || '';
    if (!id || !id.startsWith('CT-')) return '';
    return id.split('-')[1] || '';
  }
  function legacyForSlug(slug, name, catalog) {
    const key = EPIC_SLUG_LEGACY[slug];
    if (key) return catalog.find((x) => x.n === key);
    return catalog.find((x) => x.n.toUpperCase() === String(name || '').toUpperCase());
  }
  function epicToCard(e, catalog) {
    const legacy = legacyForSlug(e.slug, e.name, catalog);
    const desc = e.desc_en || legacy?.d || `${e.name} — CleantechHUB portfolio startup.`;
    const descEs = e.desc_es || legacy?.ds || desc;
    return {
      slug: e.slug, n: e.name, p: normalizeProgram(e.program), c: e.country || 'CO', w: e.website,
      t: e.theme || legacy?.t || 'CE', st: normalizeStage(e.stage) || legacy?.st || 'Seed',
      d: desc, ds: descEs, ct1: e.ct1 || legacy?.ct1 || '', ct2: legacy?.ct2 || '', founder: e.founder, epic: true,
      youtube: e.youtube || '', onepager: e.onepager || '',
    };
  }
  function imdToCard(e) {
    const desc = e.desc_en || `${e.name} — Peru CTH program alumni.`;
    const descEs = e.desc_es || desc;
    return {
      slug: e.slug, n: e.name, p: normalizeProgram(e.program), c: e.country || 'PE', w: e.website,
      t: e.theme || 'BIO', st: normalizeStage(e.stage) || 'Seed',
      d: desc, ds: descEs, ct1: e.ct1 || '', ct2: '', founder: e.founder, imd: true,
      nexusPath: e.nexus_path || '', youtube: e.youtube || '', onepager: e.onepager || '',
    };
  }

  function syncSpecialQuery() {
    const next = new URLSearchParams(location.search);
    if (epicOnly) { next.set('epic', '1'); next.delete('imd_pe'); imdOnly = false; }
    else next.delete('epic');
    if (imdOnly) { next.set('imd_pe', '1'); next.delete('epic'); epicOnly = false; }
    else next.delete('imd_pe');
    if (epicOnly || imdOnly) clpOnly = false;
    if (clpOnly) { next.set('clp26', '1'); next.delete('epic'); next.delete('imd_pe'); }
    else next.delete('clp26');
    const qs = next.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
  }

  function setSpecialMode(mode) {
    if (mode === 'none' || !mode) {
      epicOnly = false;
      imdOnly = false;
      clpOnly = false;
    } else {
      epicOnly = mode === 'epic';
      imdOnly = mode === 'imd';
      clpOnly = mode === 'clp26';
    }
    if (epicOnly || imdOnly || clpOnly) webOnly = false;
    syncSpecialQuery();
  }

  function toggleSet(set, val) {
    if (set.has(val)) set.delete(val);
    else set.add(val);
  }

  function activeChips() {
    const chips = [];
    if (epicOnly) chips.push({ k: 'special', v: 'epic', label: 'Epic Angels' });
    if (imdOnly) chips.push({ k: 'special', v: 'imd', label: 'IMD Perú' });
    if (clpOnly) chips.push({ k: 'special', v: 'clp26', label: 'CLP26' });
    fProg.forEach((p) => chips.push({ k: 'prog', v: p, label: p }));
    fTheme.forEach((t) => chips.push({ k: 'theme', v: t, label: THEMES.find((x) => x.id === t)?.label || t }));
    fStage.forEach((s) => chips.push({ k: 'stage', v: s, label: s }));
    fCountry.forEach((c) => chips.push({ k: 'country', v: c, label: COUNTRY_LABEL[c] || c }));
    fCtSector.forEach((s) => chips.push({ k: 'ct', v: s, label: 'CT · ' + s }));
    if (webOnly && !epicOnly && !imdOnly && !clpOnly) chips.push({ k: 'web', v: '1', label: 'Web only' });
    return chips;
  }

  function removeChip(chip) {
    if (chip.k === 'special') setSpecialMode('none');
    else if (chip.k === 'prog') fProg.delete(chip.v);
    else if (chip.k === 'theme') fTheme.delete(chip.v);
    else if (chip.k === 'stage') fStage.delete(chip.v);
    else if (chip.k === 'country') fCountry.delete(chip.v);
    else if (chip.k === 'ct') fCtSector.delete(chip.v);
    else if (chip.k === 'web') webOnly = false;
  }

  function clearStandardFilters() {
    fProg.clear(); fTheme.clear(); fStage.clear(); fCountry.clear(); fCtSector.clear();
  }

  function filterList(base, q) {
    let list = base.slice();
    if (fProg.size) list = list.filter((s) => fProg.has(s.p));
    if (fTheme.size) list = list.filter((s) => fTheme.has(s.t));
    if (fStage.size) list = list.filter((s) => fStage.has(s.st));
    if (fCountry.size) list = list.filter((s) => fCountry.has(s.c));
    if (fCtSector.size) list = list.filter((s) => fCtSector.has(ctSector(s)));
    if (webOnly) list = list.filter((s) => s.w);
    if (q) {
      const qq = q.toLowerCase();
      list = list.filter((s) => s.n.toLowerCase().includes(qq) || (s.founder || '').toLowerCase().includes(qq));
    }
    return list;
  }

  function getFiltered(q) {
    if (epicOnly) return { list: filterList(EPIC_CARDS, q), total: EPIC_CARDS.length, mode: 'epic' };
    if (clpOnly) return { list: filterList(CLP_CARDS, q), total: CLP_CARDS.length, mode: 'clp26' };
    if (imdOnly) return { list: filterList(IMD_CARDS, q), total: IMD_CARDS.length, mode: 'imd' };
    let list = filterList(S, q);
    list = [...list].sort((a, b) => {
      if (!!a.w === !!b.w) return a.n.localeCompare(b.n);
      return a.w ? -1 : 1;
    });
    return { list, total: S.length, mode: 'portfolio' };
  }

  async function loadAll() {
    const core = await fetch('portfolio-core.json').then((r) => r.json());
    S = core.startups || [];
    const [epicRes, imdRes, clpRes] = await Promise.all([
      fetch('/nexus-assets/epic-angels-shareable.json?v=20261014-epic18').then((r) => r.json()),
      fetch('/nexus-assets/imd-peru-shareable.json?v=20260924-imd16').then((r) => r.json()),
      fetch('/nexus-assets/clp26-national-shareable.json?v=20261016-clp26').then((r) => r.json()),
    ]);
    EPIC_CARDS = (epicRes.startups || []).map((e) => epicToCard(e, S)).filter((s) => EPIC_ALLOWLIST_SLUGS.has(s.slug));
    IMD_CARDS = (imdRes.startups || []).map(imdToCard);
    CLP_CARDS = (clpRes.startups || []).map((e) => Object.assign(epicToCard(e, S), { epic: false, clp: true }));
  }

  function renderCard(s) {
    const flag = FLAGS[s.c] || '\u{1F30D}';
    const hasW = !!s.w;
    const desc = lang === 'ES' ? s.ds : s.d;
    const stk = { 'Pre-Seed': 'PS', Seed: 'S', 'Pre-Series A': 'PSA', 'Series A': 'SA', 'Series B+': 'SBP' }[s.st] || 'PS';
    const tShort = { CE: 'Circular', BIO: 'Bioeconomy', EN: 'Energy' };
    const sShort = { 'Pre-Seed': 'Pre-Seed', Seed: 'Seed', 'Pre-Series A': 'Pre-A', 'Series A': 'Ser. A', 'Series B+': 'Ser. B+' };
    const epicBadge = s.epic ? '<span class="badge epic">Epic Angels</span>' : '';
    const imdBadge = s.imd ? '<span class="badge imd">IMD · Perú</span>' : '';
    const ct1 = s.ct1 ? `<span class="badge ct" title="${s.ct1}">${s.ct1}</span>` : '';
    const webBtn = hasW
      ? `<a class="btn-site" href="https://${s.w}" target="_blank" rel="noopener">Visit ↗</a>`
      : '<span class="muted">No site</span>';
    const nexusHref = s.nexusPath || (s.slug ? '/s/' + s.slug : '');
    const nexusBtn = nexusHref ? `<a class="btn-nexus" href="${nexusHref}">Nexus ↗</a>` : '';
    return `<article class="card ${hasW ? '' : 'dim'}">
      <div class="card-bar bar-${s.p}"></div>
      <header class="card-head"><h3>${s.n}</h3><span class="flag">${flag}</span></header>
      <p class="card-desc">${desc}</p>
      <footer class="card-foot">${epicBadge}${imdBadge}
        <span class="badge prog">${s.p}</span>
        <span class="badge theme-${s.t}">${tShort[s.t] || s.t}</span>
        <span class="badge stage">${sShort[s.st] || s.st}</span>${ct1}
        <span class="card-actions">${nexusBtn}${webBtn}</span>
      </footer>
    </article>`;
  }

  global.NexusPreview = {
    FLAGS, COUNTRY_LABEL, CT_SECTORS, PROGRAMS, STAGES, THEMES,
    get state() {
      return { epicOnly, imdOnly, clpOnly, fProg, fTheme, fStage, fCountry, fCtSector, webOnly, lang, S, EPIC_CARDS, IMD_CARDS, CLP_CARDS };
    },
    setLang(l) { lang = l; },
    setSpecialMode, syncSpecialQuery, toggleSet, activeChips, removeChip, clearStandardFilters,
    getFiltered, loadAll, renderCard, ctSector,
    get webOnly() { return webOnly; },
    set webOnly(v) { webOnly = v; },
  };
})(window);
