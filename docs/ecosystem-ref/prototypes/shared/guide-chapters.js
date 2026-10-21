/** Guided partnership mode (D5v2 on D3 hybrid). */
window.NexusGuide = (function () {
  const CHAPTER_DEFS = [
    {
      id: 'challenges',
      num: 1,
      title: 'Nature challenges',
      titleEs: '1 · Retos de la naturaleza',
      blurb: 'Quién declara trabajo en retos (works_on_challenge). Sin aristas donor→reto tipadas aparte.',
      types: ['works_on_challenge'],
    },
    {
      id: 'policy',
      num: 2,
      title: 'Policy',
      titleEs: '2 · Política pública',
      blurb: 'Regulación y programas de gobierno.',
      types: ['regulates_layer', 'runs_program', 'oversees', 'runs_initiative', 'created', 'participates'],
    },
    {
      id: 'capital',
      num: 3,
      title: 'Capital',
      titleEs: '3 · Capital',
      blurb: 'Cofinanciamiento y capas de fondos.',
      types: ['cofunds', 'funds_layer'],
    },
    {
      id: 'hubs',
      num: 4,
      title: 'Hubs',
      titleEs: '4 · Hubs e incubación',
      blurb: 'Universidades, hubs REIN, incubación y alianzas.',
      types: ['hosts', 'incubated', 'accelerated', 'partner'],
    },
    {
      id: 'partnerships',
      num: 5,
      title: 'Partnerships',
      titleEs: '5 · Alianzas (construir partnerships)',
      blurb: 'Constelaciones reto-centradas: sólido = dato verificado; punteado = sugerido (no es relación real).',
      types: null,
    },
  ];

  const CHALLENGE_META = {
    'challenge:PE-1-bosques': {
      label: 'Bosques & Amazonía',
      labelEs: 'Reto: Bosques & Amazonía (PE)',
      country: 'Peru',
      geo: { lat: -10.2, lng: -74.5 },
    },
    'challenge:PE-2-agua': {
      label: 'Agua & cuencas',
      labelEs: 'Reto: Agua & cuencas (PE)',
      country: 'Peru',
      geo: { lat: -12.8, lng: -76.2 },
    },
  };

  const CONSTELLATIONS = [
    {
      id: 'agua-uqhu',
      challengeId: 'challenge:PE-2-agua',
      startupId: 'pe-uqhu',
      hubId: 'pe-emprende-up-climatech-rein-hub-peru',
      universityId: 'pe-universidad-del-pacifico',
      funderId: 'pe-profonanpe',
    },
    {
      id: 'agua-yakufil',
      challengeId: 'challenge:PE-2-agua',
      startupId: 'pe-yakufil',
      hubId: 'pe-emprende-up-climatech-rein-hub-peru',
      universityId: 'pe-universidad-del-pacifico',
      funderId: 'pe-amazonia-impact-ventures',
    },
    {
      id: 'bosques-yakusmart',
      challengeId: 'challenge:PE-1-bosques',
      startupId: 'pe-yakusmart',
      hubId: 'pe-emprende-up-climatech-rein-hub-peru',
      universityId: 'pe-universidad-del-pacifico',
      funderId: 'pe-amazonia-impact-ventures',
    },
  ];

  function isChallengeId(id) {
    return id && id.startsWith('challenge:');
  }

  function computeGapCounts(relations, byId) {
    const out = CHAPTER_DEFS.map((ch) => {
      const typeCounts = {};
      let total = 0;
      relations.forEach((r) => {
        if (ch.id === 'partnerships') return;
        if (ch.id === 'challenges') {
          if (r.type !== 'works_on_challenge') return;
          typeCounts[r.type] = (typeCounts[r.type] || 0) + 1;
          total += 1;
          return;
        }
        if (!ch.types.includes(r.type)) return;
        if (isChallengeId(r.source) || isChallengeId(r.target)) return;
        typeCounts[r.type] = (typeCounts[r.type] || 0) + 1;
        total += 1;
      });
      return { chapter: ch.id, title: ch.title, total, byType: typeCounts };
    });

    const funderToChallenge = relations.filter(
      (r) => r.type === 'works_on_challenge' && byId.get(r.source)?.category === 'funder',
    ).length;
    const fundedByType = relations.filter((r) => r.type === 'funded-by' || r.type === 'funded_by').length;
    const donorToStartup = relations.filter(
      (r) => (r.type === 'funded-by' || r.type === 'invested-in') && byId.has(r.source) && byId.has(r.target),
    ).length;

    out.push({
      chapter: 'gaps',
      title: 'Notable gaps',
      total: 0,
      byType: {
        'funder→challenge (works_on_challenge only)': funderToChallenge,
        'funded-by edges (any)': fundedByType,
        'donor→startup typed edges': donorToStartup,
        'incubated→challenge': 0,
      },
    });
    return out;
  }

  function realEdgeKey(a, b, type) {
    return [a, b].sort().join('|') + ':' + type;
  }

  function hasRealEdge(relations, a, b, type) {
    return relations.some(
      (r) => r.type === type && ((r.source === a && r.target === b) || (r.source === b && r.target === a)),
    );
  }

  function hasAnyRealEdge(relations, a, b) {
    return relations.some(
      (r) => (r.source === a && r.target === b) || (r.source === b && r.target === a),
    );
  }

  function buildConstellation(constellationId, relations, byId) {
    const spec = CONSTELLATIONS.find((c) => c.id === constellationId) || CONSTELLATIONS[0];
    const ids = new Set([
      spec.challengeId,
      spec.startupId,
      spec.hubId,
      spec.universityId,
      spec.funderId,
    ].filter(Boolean));

    const nodes = [];
    const edges = [];
    const center = CHALLENGE_META[spec.challengeId];

    nodes.push({
      id: spec.challengeId,
      label: center.labelEs,
      kind: 'challenge',
      size: 36,
      color: '#2a9d8f',
      position: { x: 0, y: 0 },
      geo: center.geo,
    });

    const orbit = [
      { id: spec.startupId, role: 'startup', angle: -Math.PI / 2, dist: 120 },
      { id: spec.hubId, role: 'hub', angle: 0.2, dist: 130 },
      { id: spec.universityId, role: 'university', angle: Math.PI, dist: 125 },
      { id: spec.funderId, role: 'funder', angle: Math.PI / 2, dist: 120 },
    ];

    orbit.forEach((o) => {
      if (!o.id) return;
      const a = byId.get(o.id);
      if (!a) return;
      nodes.push({
        id: o.id,
        label: a.name.length > 24 ? a.name.slice(0, 22) + '…' : a.name,
        kind: o.role,
        size: o.role === 'startup' ? 22 : 18,
        color: null,
        position: { x: Math.cos(o.angle) * o.dist, y: Math.sin(o.angle) * o.dist },
        geo: a.geo,
      });
    });

    relations.forEach((r, i) => {
      if (!ids.has(r.source) || !ids.has(r.target)) return;
      edges.push({
        id: 'real-' + i,
        source: r.source,
        target: r.target,
        type: r.type,
        suggested: false,
      });
    });

    const suggestions = [];
    function addSuggestion(source, target, reason) {
      if (!source || !target || source === target) return;
      if (hasAnyRealEdge(relations, source, target)) return;
      suggestions.push({ source, target, reason });
    }

    if (spec.startupId && !hasRealEdge(relations, spec.startupId, spec.challengeId, 'works_on_challenge')) {
      addSuggestion(spec.startupId, spec.challengeId, 'sector/country fit to challenge');
    }
    addSuggestion(spec.hubId, spec.startupId, 'hub incubation fit (same country)');
    addSuggestion(spec.funderId, spec.startupId, 'capital alignment (PE cleantech)');
    addSuggestion(spec.universityId, spec.startupId, 'academia–venture pathway');

    suggestions.forEach((s, i) => {
      edges.push({
        id: 'sug-' + i,
        source: s.source,
        target: s.target,
        type: 'suggested',
        suggested: true,
        label: 'Suggested',
      });
    });

    return { spec, nodes, edges, center };
  }

  function relationsForChapter(chapterId, relations) {
    const ch = CHAPTER_DEFS.find((c) => c.id === chapterId);
    if (!ch || ch.id === 'partnerships') return [];
    if (ch.id === 'challenges') {
      return relations.filter((r) => r.type === 'works_on_challenge');
    }
    return relations.filter(
      (r) => ch.types.includes(r.type) && !isChallengeId(r.source) && !isChallengeId(r.target),
    );
  }

  return {
    CHAPTER_DEFS,
    CHALLENGE_META,
    CONSTELLATIONS,
    isChallengeId,
    computeGapCounts,
    buildConstellation,
    relationsForChapter,
  };
})();
