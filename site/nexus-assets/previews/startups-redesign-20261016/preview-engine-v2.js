/* Option B v2 — deduped universe + program type / cohort facets */
(function (global) {
  const FLAGS = { CO: '\u{1F1E8}\u{1F1F4}', MX: '\u{1F1F2}\u{1F1FD}', CL: '\u{1F1E8}\u{1F1F1}', PE: '\u{1F1F5}\u{1F1EA}', ES: '\u{1F1EA}\u{1F1F8}', PA: '\u{1F1F5}\u{1F1E6}', GT: '\u{1F1EC}\u{1F1F9}', CR: '\u{1F1E8}\u{1F1F7}', SV: '\u{1F1F8}\u{1F1FB}', INT: '\u{1F30D}' };
  const COUNTRY_LABEL = { CO: 'Colombia', MX: 'Mexico', CL: 'Chile', PE: 'Peru', ES: 'Spain', PA: 'Panama', GT: 'Guatemala', CR: 'Costa Rica', SV: 'El Salvador', INT: 'International' };
  const CLP26_COUNTRIES = ['CO', 'PE', 'SV', 'GT', 'CR', 'MX'];
  const CT_SECTORS = [
    { id: 'AF', label: 'Agriculture & Food' }, { id: 'EN', label: 'Energy' }, { id: 'WA', label: 'Waste & Circular' },
    { id: 'WW', label: 'Water' }, { id: 'TR', label: 'Transport' }, { id: 'IC', label: 'Climate Tech / Data' },
    { id: 'XS', label: 'Cross-sector / Finance' }, { id: 'IN', label: 'Industry' }, { id: 'BU', label: 'Built Environment' },
    { id: 'EX', label: 'Other' },
  ];
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

  const COHORT_LABELS = {
    CLAC21: "CLAC '21", CLAC22: "CLAC '22", CLAC23: "CLAC '23", CLAC24: "CLAC '24", CLAC25: "CLAC '25",
    CLP: 'CLP (historical cohort)', CLP20: "CLP '20", CLP25: "CLP '25",
    'CLP26-CO': 'CLP 2026 · Colombia', 'CLP26-PE': 'CLP 2026 · Peru', 'CLP26-SV': 'CLP 2026 · El Salvador',
    'CLP26-GT': 'CLP 2026 · Guatemala', 'CLP26-CR': 'CLP 2026 · Costa Rica', 'CLP26-MX': 'CLP 2026 · Mexico',
    'IMD-PE': 'IMD · Perú · CTH', GIZ: 'GIZ Growth Services',
  };

  const PROGRAM_TAXONOMY = [
    {
      id: 'clac', label: 'CLAC accelerator', description: 'CLAC accelerator cohorts',
      cohorts: ['CLAC21', 'CLAC22', 'CLAC23', 'CLAC24', 'CLAC25'],
    },
    {
      id: 'clp', label: 'ClimateLaunchpad (competition)', description: 'CLP national & regional competition cohorts',
      cohorts: ['CLP', 'CLP20', 'CLP25'],
      nested: {
        label: 'CLP 2026 national', cohorts: CLP26_COUNTRIES.map((c) => 'CLP26-' + c),
      },
    },
    {
      id: 'partner', label: 'Partner / corporate programs', description: 'Curated partner program alumni',
      cohorts: ['IMD-PE', 'GIZ'],
    },
  ];

  let UNIFIED = [];
  let EPIC_CARDS = [];
  let IMD_CARDS = [];
  let CLP_CARDS = [];
  let STATS = {};

  let epicOnly = new URLSearchParams(location.search).get('epic') === '1';
  let imdOnly = new URLSearchParams(location.search).get('imd_pe') === '1';
  let clpOnly = new URLSearchParams(location.search).get('clp26') === '1';
  if (epicOnly && imdOnly) imdOnly = false;
  if (clpOnly && (epicOnly || imdOnly)) clpOnly = false;

  let fCohort = new Set();
  let fTheme = new Set();
  let fStage = new Set();
  let fCountry = new Set();
  let fCtSector = new Set();
  let webOnly = !epicOnly && !imdOnly && !clpOnly;
  let lang = 'EN';

  function normName(n) { return String(n || '').trim().toUpperCase().replace(/\s+/g, ' '); }
  function slugify(s) {
    return String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  }
  function coreSlugFromName(n) {
    for (const [slug, name] of Object.entries(EPIC_SLUG_LEGACY)) { if (name === n) return slug; }
    return slugify(n);
  }
  function normalizeStage(st) {
    if (!st || st === '[PENDIENTE]' || st === 'Launched') return st === 'Launched' ? 'Seed' : st || 'Seed';
    if (st === 'Private Beta') return 'Pre-Seed';
    if (st === 'Public Beta') return 'Pre-Series A';
    if (st === 'Ideation' || st === 'Sketches') return 'Pre-Seed';
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

  function cohortsForRow(row) {
    const c = [];
    if (row.src === 'imd') c.push('IMD-PE');
    const program = row.program || (row.src === 'clp26' ? 'CLP26' : '');
    if (program === 'GIZ Growth Services') c.push('GIZ');
    else if (program === 'CLP26') c.push('CLP26-' + (row.country || 'CO'));
    else if (program) c.push(program);
    return c;
  }

  function mergeRecord(existing, row, card) {
    if (!existing) return card;
    cohortsForRow(row).forEach((x) => existing.cohorts.add(x));
    if (card.cohorts) card.cohorts.forEach((x) => existing.cohorts.add(x));
    if (row.src === 'core' || (!existing.n && card.n)) Object.assign(existing, card);
    if (row.src === 'core') { existing.d = card.d; existing.ds = card.ds; existing.p = card.p; }
    if (row.src === 'epic') existing.epic = true;
    if (row.src === 'imd') existing.imd = true;
    if (row.src === 'clp26') existing.clp26 = true;
    if (card.w && !existing.w) existing.w = card.w;
    if (card.ct1 && !existing.ct1) existing.ct1 = card.ct1;
    if (card.ct2 && !existing.ct2) existing.ct2 = card.ct2;
    if (card.onepager && !existing.onepager) existing.onepager = card.onepager;
    if (card.nexusPath && !existing.nexusPath) existing.nexusPath = card.nexusPath;
    existing.slug = existing.slug || card.slug;
    return existing;
  }

  function rowToPartial(row, catalog) {
    if (row.src === 'core') {
      const x = row.raw;
      return {
        slug: coreSlugFromName(x.n), n: x.n, p: x.p, c: x.c, w: x.w, t: x.t, st: normalizeStage(x.st),
        d: x.d, ds: x.ds, ct1: x.ct1 || '', ct2: x.ct2 || '', cohorts: new Set(cohortsForRow(row)),
      };
    }
    const legacy = legacyForSlug(row.slug, row.name, catalog);
    const desc = row.raw.desc_en || legacy?.d || `${row.name} — CleantechHUB portfolio startup.`;
    const descEs = row.raw.desc_es || legacy?.ds || desc;
    const website = row.raw.website || legacy?.w || '';
    return {
      slug: row.slug, n: row.name, p: legacy?.p || row.program || 'CLP', c: row.country || 'CO',
      w: website && !String(website).startsWith('http') ? website.replace(/^https?:\/\//, '') : website,
      t: row.raw.theme || legacy?.t || 'CE', st: normalizeStage(row.raw.stage) || legacy?.st || 'Seed',
      d: desc, ds: descEs, ct1: row.raw.ct1 || legacy?.ct1 || '', ct2: legacy?.ct2 || '',
      founder: row.raw.founder, epic: row.src === 'epic', imd: row.src === 'imd', clp26: row.src === 'clp26',
      nexusPath: row.raw.nexus_path || '', youtube: row.raw.youtube || '', onepager: row.raw.onepager || '',
      cohorts: new Set(cohortsForRow(row)),
    };
  }

  function buildUnified(core, epicRows, imdRows, clpRows) {
    const parent = new Map();
    function find(k) {
      if (!parent.has(k)) parent.set(k, k);
      if (parent.get(k) !== k) parent.set(k, find(parent.get(k)));
      return parent.get(k);
    }
    function unite(a, b) { const ra = find(a); const rb = find(b); if (ra !== rb) parent.set(rb, ra); }

    const rows = [];
    core.forEach((x) => rows.push({ src: 'core', slug: coreSlugFromName(x.n), name: x.n, program: x.p, country: x.c, raw: x }));
    epicRows.forEach((x) => rows.push({ src: 'epic', slug: x.slug, name: x.name, program: x.program, country: x.country, raw: x }));
    imdRows.forEach((x) => rows.push({ src: 'imd', slug: x.slug, name: x.name, program: x.program, country: x.country, raw: x }));
    clpRows.forEach((x) => rows.push({ src: 'clp26', slug: x.slug, name: x.name, program: x.program, country: x.country, raw: x }));

    rows.forEach((r) => unite('slug:' + r.slug.toLowerCase(), 'name:' + normName(r.name)));

    const groups = new Map();
    rows.forEach((r) => {
      const root = find('slug:' + r.slug.toLowerCase());
      if (!groups.has(root)) groups.set(root, []);
      groups.get(root).push(r);
    });

    const unified = [];
    groups.forEach((members) => {
      let rec = null;
      members.forEach((row) => {
        const partial = rowToPartial(row, core);
        if (!rec) rec = partial;
        else mergeRecord(rec, row, partial);
      });
      if (rec) {
        rec.cohorts = rec.cohorts || new Set();
        members.forEach((row) => cohortsForRow(row).forEach((c) => rec.cohorts.add(c)));
        rec.programType = primaryProgramType(rec);
        rec.programCohortLabel = primaryCohortLabel(rec);
        unified.push(rec);
      }
    });
    unified.sort((a, b) => a.n.localeCompare(b.n));
    return unified;
  }

  function primaryProgramType(card) {
    const cs = [...card.cohorts];
    if (cs.some((c) => c.startsWith('CLAC'))) return 'CLAC accelerator';
    if (cs.some((c) => c.startsWith('CLP'))) return 'ClimateLaunchpad';
    if (cs.includes('IMD-PE') || cs.includes('GIZ')) return 'Partner program';
    return 'CleantechHUB portfolio';
  }

  function primaryCohortLabel(card) {
    const order = ['CLAC25', 'CLAC24', 'CLAC23', 'CLAC22', 'CLAC21', 'CLP26-CO', 'CLP26-PE', 'CLP26-SV', 'CLP26-GT', 'CLP26-CR', 'CLP26-MX', 'CLP25', 'CLP20', 'CLP', 'IMD-PE', 'GIZ'];
    for (const id of order) { if (card.cohorts.has(id)) return COHORT_LABELS[id] || id; }
    const any = [...card.cohorts][0];
    return any ? (COHORT_LABELS[any] || any) : (card.p || '—');
  }

  function cohortCounts(cards) {
    const m = new Map();
    cards.forEach((s) => { s.cohorts.forEach((c) => m.set(c, (m.get(c) || 0) + 1)); });
    return m;
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
    history.replaceState(null, '', location.pathname + (next.toString() ? '?' + next.toString() : ''));
  }

  function setSpecialMode(mode) {
    if (mode === 'none' || !mode) { epicOnly = false; imdOnly = false; clpOnly = false; }
    else { epicOnly = mode === 'epic'; imdOnly = mode === 'imd'; clpOnly = mode === 'clp26'; }
    if (epicOnly || imdOnly || clpOnly) webOnly = false;
    syncSpecialQuery();
  }

  function toggleSet(set, val) { if (set.has(val)) set.delete(val); else set.add(val); }

  function activeChips() {
    const chips = [];
    if (epicOnly) chips.push({ k: 'special', v: 'epic', label: 'Epic Angels' });
    if (imdOnly) chips.push({ k: 'special', v: 'imd', label: 'IMD Perú' });
    if (clpOnly) chips.push({ k: 'special', v: 'clp26', label: 'CLP26 national list' });
    fCohort.forEach((c) => chips.push({ k: 'cohort', v: c, label: COHORT_LABELS[c] || c }));
    fTheme.forEach((t) => chips.push({ k: 'theme', v: t, label: THEMES.find((x) => x.id === t)?.label || t }));
    fStage.forEach((s) => chips.push({ k: 'stage', v: s, label: s }));
    fCountry.forEach((c) => chips.push({ k: 'country', v: c, label: COUNTRY_LABEL[c] || c }));
    fCtSector.forEach((s) => chips.push({ k: 'ct', v: s, label: 'CT · ' + s }));
    if (webOnly && !epicOnly && !imdOnly && !clpOnly) chips.push({ k: 'web', v: '1', label: 'Web only' });
    return chips;
  }

  function removeChip(chip) {
    if (chip.k === 'special') setSpecialMode('none');
    else if (chip.k === 'cohort') fCohort.delete(chip.v);
    else if (chip.k === 'theme') fTheme.delete(chip.v);
    else if (chip.k === 'stage') fStage.delete(chip.v);
    else if (chip.k === 'country') fCountry.delete(chip.v);
    else if (chip.k === 'ct') fCtSector.delete(chip.v);
    else if (chip.k === 'web') webOnly = false;
  }

  function clearStandardFilters() {
    fCohort.clear(); fTheme.clear(); fStage.clear(); fCountry.clear(); fCtSector.clear();
  }

  function filterList(base, q) {
    let list = base.slice();
    if (fCohort.size) list = list.filter((s) => [...fCohort].some((c) => s.cohorts.has(c)));
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
    if (epicOnly) return { list: filterList(EPIC_CARDS, q), total: EPIC_CARDS.length, mode: 'epic', universe: UNIFIED.length };
    if (clpOnly) return { list: filterList(CLP_CARDS, q), total: CLP_CARDS.length, mode: 'clp26', universe: UNIFIED.length };
    if (imdOnly) return { list: filterList(IMD_CARDS, q), total: IMD_CARDS.length, mode: 'imd', universe: UNIFIED.length };
    const list = filterList(UNIFIED, q).sort((a, b) => {
      if (!!a.w === !!b.w) return a.n.localeCompare(b.n);
      return a.w ? -1 : 1;
    });
    return { list, total: UNIFIED.length, mode: 'portfolio', universe: UNIFIED.length };
  }

  async function loadAll() {
    const core = await fetch('portfolio-core.json').then((r) => r.json());
    const S = core.startups || [];
    const [epicRes, imdRes, clpRes] = await Promise.all([
      fetch('/nexus-assets/epic-angels-shareable.json?v=20261014-epic18').then((r) => r.json()),
      fetch('/nexus-assets/imd-peru-shareable.json?v=20260924-imd16').then((r) => r.json()),
      fetch('/nexus-assets/clp26-national-shareable.json?v=20261016-clp26').then((r) => r.json()),
    ]);
    const epicRows = epicRes.startups || [];
    const imdRows = imdRes.startups || [];
    const clpRows = clpRes.startups || [];

    UNIFIED = buildUnified(S, epicRows, imdRows, clpRows);
    const counts = cohortCounts(UNIFIED);

    EPIC_CARDS = UNIFIED.filter((s) => s.epic && EPIC_ALLOWLIST_SLUGS.has(s.slug));
    IMD_CARDS = UNIFIED.filter((s) => s.imd);
    CLP_CARDS = UNIFIED.filter((s) => s.clp26);

    const withWeb = UNIFIED.filter((s) => s.w).length;
    STATS = {
      uniqueStartups: UNIFIED.length,
      corePortfolioRows: S.length,
      clp26NationalFile: clpRows.length,
      epicShareable: epicRows.filter((e) => EPIC_ALLOWLIST_SLUGS.has(e.slug)).length,
      imdShareable: imdRows.length,
      naiveSumAllFiles: S.length + epicRows.length + imdRows.length + clpRows.length,
      wrongCorePlusClp26: S.length + clpRows.length,
      withWebsite: withWeb,
      cohortCounts: Object.fromEntries(counts),
      uniqueInAnyClp26Cohort: UNIFIED.filter((s) => [...s.cohorts].some((c) => c.startsWith('CLP26-'))).length,
    };
  }

  function renderCard(s) {
    const flag = FLAGS[s.c] || '\u{1F30D}';
    const hasW = !!s.w;
    const desc = lang === 'ES' ? s.ds : s.d;
    const tShort = { CE: 'Circular', BIO: 'Bioeconomy', EN: 'Energy' };
    const sShort = { 'Pre-Seed': 'Pre-Seed', Seed: 'Seed', 'Pre-Series A': 'Pre-A', 'Series A': 'Ser. A', 'Series B+': 'Ser. B+' };
    const epicBadge = s.epic ? '<span class="badge epic">Epic Angels</span>' : '';
    const imdBadge = s.imd ? '<span class="badge imd">IMD · Perú</span>' : '';
    const ct1 = s.ct1 ? `<span class="badge ct" title="${s.ct1}">${s.ct1}</span>` : '';
    const webBtn = hasW
      ? `<a class="btn-site" href="https://${String(s.w).replace(/^https?:\/\//, '')}" target="_blank" rel="noopener">Visit ↗</a>`
      : '<span class="muted">No site</span>';
    const nexusHref = s.nexusPath || (s.slug ? '/s/' + s.slug : '');
    const nexusBtn = nexusHref ? `<a class="btn-nexus" href="${nexusHref}">Nexus ↗</a>` : '';
    return `<article class="card ${hasW ? '' : 'dim'}">
      <div class="card-bar bar-${(s.p || 'CLP').replace(/\s+/g, '')}"></div>
      <div class="card-program-line"><span class="ptype">${s.programType}</span><span class="pcohort">${s.programCohortLabel}</span></div>
      <header class="card-head"><h3>${s.n}</h3><span class="flag">${flag}</span></header>
      <p class="card-desc">${desc}</p>
      <footer class="card-foot">${epicBadge}${imdBadge}
        <span class="badge theme-${s.t}">${tShort[s.t] || s.t}</span>
        <span class="badge stage">${sShort[s.st] || s.st}</span>${ct1}
        <span class="card-actions">${nexusBtn}${webBtn}</span>
      </footer>
    </article>`;
  }

  global.NexusPreviewV2 = {
    FLAGS, COUNTRY_LABEL, CT_SECTORS, STAGES, THEMES, COHORT_LABELS, PROGRAM_TAXONOMY,
    get state() {
      return { epicOnly, imdOnly, clpOnly, fCohort, fTheme, fStage, fCountry, fCtSector, webOnly, UNIFIED, STATS };
    },
    get STATS() { return STATS; },
    setLang(l) { lang = l; },
    setSpecialMode, toggleSet, activeChips, removeChip, clearStandardFilters,
    getFiltered, loadAll, renderCard, ctSector, cohortCounts,
    get webOnly() { return webOnly; },
    set webOnly(v) { webOnly = v; },
  };
})(window);
