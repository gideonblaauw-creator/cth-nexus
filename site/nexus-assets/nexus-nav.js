/* ══════════════════════════════════════════════════════
   NEXUS NAV INJECTOR — with mobile hamburger
   Add <script src="/nexus-assets/nexus-nav.js"></script>
   before </body>. Set data-nexus-page on <body> tag.
   ══════════════════════════════════════════════════════ */
(function () {
  const pages = [
    { id: 'home',      label: 'Inicio',     href: '/p/home' },
    { id: 'ideas',     label: 'Ideas',      href: '/ideas' },
    { id: 'startups',  label: 'Startups',   href: '/p/startup-portfolio' },
    { id: 'mentors',   label: 'Mentores',   href: '/mentor-directory' },
    { id: 'hubs',      label: 'Hubs',       labelEn: 'Hubs', href: '/hubs/' },
    { id: 'investors', label: 'Inversores', labelEn: 'Investors', href: '/investors', gated: true },
    { id: 'funders',   label: 'Funders',    href: '/p/funders', gated: true },
    { id: 'ecosystem', label: 'Ecosistema', labelEn: 'Ecosystem', href: '/ecosystem', gated: true },
  ];

  const active = document.body.dataset.nexusPage || 'home';

  let lang = (localStorage.getItem('nexusEcoLang') || 'ES').toUpperCase();
  if (lang !== 'EN' && lang !== 'ES') lang = 'ES';

  let brand = (new URLSearchParams(location.search).get('brand') || localStorage.getItem('nexusBrand') || 'cth').toLowerCase();
  if (brand !== 'rein') brand = 'cth';

  function navLabel(p) {
    if (lang === 'EN' && p.labelEn) return p.labelEn;
    return p.label;
  }

  function applyBrand() {
    document.body.dataset.brand = brand === 'rein' ? 'rein' : 'cth';
    document.querySelectorAll('[data-nav-brand-btn]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.navBrandBtn === brand);
    });
  }

  function setBrand(next) {
    brand = next === 'rein' ? 'rein' : 'cth';
    localStorage.setItem('nexusBrand', brand);
    applyBrand();
    document.querySelectorAll('[data-brand-btn]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.brandBtn === brand);
    });
    document.dispatchEvent(new CustomEvent('nexus-brand-change', { detail: { brand } }));
  }

  function setLang(next) {
    lang = next === 'EN' ? 'EN' : 'ES';
    localStorage.setItem('nexusEcoLang', lang);
    document.documentElement.lang = lang === 'EN' ? 'en' : 'es';
    const allLangBtns = [
      ...document.querySelectorAll('.nexus-nav .lang-btn'),
      ...document.querySelectorAll('.nav-mobile-menu .lang-btn'),
    ];
    allLangBtns.forEach((b) => b.classList.toggle('active', b.textContent.trim() === lang));
    document.querySelectorAll('[data-lang-btn]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.langBtn === lang);
    });
    pages.forEach((p) => {
      document.querySelectorAll(`a.nav-link[href="${p.href}"]`).forEach((a) => { a.textContent = navLabel(p); });
      document.querySelectorAll(`a.nav-mobile-link[href="${p.href}"]`).forEach((a) => { a.textContent = navLabel(p); });
    });
    document.dispatchEvent(new CustomEvent('nexus-lang-change', { detail: { lang } }));
  }

  applyBrand();

  /* ── Styles (injected once) ── */
  const style = document.createElement('style');
  style.textContent = `
    .nexus-nav {
      background: #0C498A;
      height: 52px;
      display: flex;
      align-items: center;
      padding: 0 20px;
      position: sticky;
      top: 0;
      z-index: 200;
      box-shadow: 0 2px 12px rgba(12,73,138,.25);
    }
    .nav-brand {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-right: 24px;
      text-decoration: none;
      flex-shrink: 0;
    }
    .nav-logo-mark {
      font-size: 15px;
      font-weight: 800;
      color: #B2EEFA;
      letter-spacing: -.4px;
      line-height: 1;
      font-family: 'Open Sans', 'PT Sans', sans-serif;
    }
    .nav-logo-mark em { color: #9DC384; font-style: normal; }
    .nav-nexus-pill {
      background: rgba(178,238,250,.15);
      border: 1px solid rgba(178,238,250,.3);
      color: #B2EEFA;
      font-size: 9px;
      font-weight: 800;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      padding: 2px 7px;
      border-radius: 4px;
    }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 2px;
      flex: 1;
    }
    .nav-link {
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      color: rgba(255,255,255,.55);
      cursor: pointer;
      transition: all .15s;
      letter-spacing: .2px;
      text-decoration: none;
      white-space: nowrap;
      font-family: 'Open Sans', 'PT Sans', sans-serif;
    }
    .nav-link:hover { color: #fff; background: rgba(255,255,255,.08); }
    .nav-link.active { color: #B2EEFA; background: rgba(178,238,250,.12); }
    .nav-link.gated { color: rgba(255,255,255,.72); }
    .nav-link.gated::after {
      content: '🔒';
      font-size: 9px;
      margin-left: 4px;
      opacity: .85;
    }
    .nav-mobile-link.gated::after {
      content: ' 🔒';
      font-size: 11px;
      opacity: .75;
    }

    .nav-right {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-left: auto;
      flex-shrink: 0;
    }
    .nav-brand-toggle {
      display: flex;
      background: rgba(255,255,255,.12);
      border-radius: 16px;
      padding: 2px;
      gap: 1px;
    }
    .nav-brand-btn {
      padding: 3px 8px;
      border-radius: 13px;
      font-size: 9px;
      font-weight: 800;
      letter-spacing: .4px;
      cursor: pointer;
      color: rgba(255,255,255,.45);
      transition: all .15s;
      border: none;
      background: transparent;
      font-family: 'Open Sans', 'PT Sans', sans-serif;
    }
    .nav-brand-btn.active { background: #fff; color: #0C498A; }
    body[data-brand="rein"] .nav-brand-btn.active { color: #1B4332; }
    .lang-toggle {
      display: flex;
      background: rgba(255,255,255,.1);
      border-radius: 16px;
      padding: 2px;
      gap: 1px;
    }
    .lang-btn {
      padding: 3px 10px;
      border-radius: 13px;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: .5px;
      cursor: pointer;
      color: rgba(255,255,255,.45);
      transition: all .15s;
      border: none;
      background: transparent;
      font-family: 'Open Sans', 'PT Sans', sans-serif;
    }
    .lang-btn.active { background: #fff; color: #0C498A; }
    .nav-avatar {
      width: 30px; height: 30px;
      border-radius: 50%;
      background: #669348;
      display: flex; align-items: center; justify-content: center;
      font-size: 11px; font-weight: 800;
      color: #fff;
      border: 2px solid rgba(255,255,255,.2);
      cursor: pointer;
      font-family: 'Open Sans', 'PT Sans', sans-serif;
    }

    .nav-hamburger {
      display: none;
      background: transparent;
      border: none;
      cursor: pointer;
      padding: 8px;
      margin-left: auto;
      flex-direction: column;
      gap: 5px;
      align-items: center;
      justify-content: center;
      width: 44px;
      height: 44px;
      border-radius: 8px;
      transition: background .15s;
    }
    .nav-hamburger:hover { background: rgba(255,255,255,.1); }
    .nav-hamburger span {
      display: block;
      width: 20px;
      height: 2px;
      background: rgba(255,255,255,.8);
      border-radius: 2px;
      transition: all .2s;
    }
    .nav-hamburger.open span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
    .nav-hamburger.open span:nth-child(2) { opacity: 0; }
    .nav-hamburger.open span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

    .nav-mobile-menu {
      display: none;
      position: fixed;
      top: 52px;
      left: 0; right: 0;
      background: #0C498A;
      z-index: 199;
      border-top: 1px solid rgba(178,238,250,.1);
      box-shadow: 0 8px 24px rgba(12,73,138,.4);
      flex-direction: column;
    }
    .nav-mobile-menu.open { display: flex; }
    .nav-mobile-link {
      display: block;
      padding: 0 20px;
      height: 52px;
      line-height: 52px;
      font-size: 14px;
      font-weight: 700;
      color: rgba(255,255,255,.65);
      text-decoration: none;
      border-left: 4px solid transparent;
      border-bottom: 1px solid rgba(178,238,250,.07);
      transition: all .15s;
      font-family: 'Open Sans', 'PT Sans', sans-serif;
    }
    .nav-mobile-link:last-child { border-bottom: none; }
    .nav-mobile-link:hover { color: #fff; background: rgba(255,255,255,.06); }
    .nav-mobile-link.active {
      color: #B2EEFA;
      border-left-color: #B2EEFA;
      background: rgba(178,238,250,.08);
    }

    .nav-mobile-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 20px;
      border-top: 1px solid rgba(178,238,250,.12);
      gap: 10px;
      flex-wrap: wrap;
    }
    .nav-mobile-footer .lang-toggle,
    .nav-mobile-footer .nav-brand-toggle {
      display: flex;
      background: rgba(255,255,255,.1);
      border-radius: 16px;
      padding: 2px;
      gap: 1px;
    }
    .nav-mobile-footer .lang-btn,
    .nav-mobile-footer .nav-brand-btn {
      padding: 5px 14px;
      border-radius: 13px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .5px;
      cursor: pointer;
      color: rgba(255,255,255,.45);
      transition: all .15s;
      border: none;
      background: transparent;
      font-family: 'Open Sans', 'PT Sans', sans-serif;
    }
    .nav-mobile-footer .lang-btn.active,
    .nav-mobile-footer .nav-brand-btn.active { background: #fff; color: #0C498A; }
    .nav-mobile-footer .nav-avatar {
      width: 32px; height: 32px;
      border-radius: 50%;
      background: #669348;
      display: flex; align-items: center; justify-content: center;
      font-size: 12px; font-weight: 800;
      color: #fff;
      border: 2px solid rgba(255,255,255,.2);
    }

    @media (max-width: 720px) {
      .nav-links { display: none !important; }
      .nav-right  { display: none !important; }
      .nav-hamburger { display: flex !important; }
    }
    @media (min-width: 721px) {
      .nav-mobile-menu { display: none !important; }
    }
  `;
  document.head.appendChild(style);

  const brandToggleHtml = `
    <div class="nav-brand-toggle" aria-label="Brand">
      <button type="button" class="nav-brand-btn${brand === 'cth' ? ' active' : ''}" data-nav-brand-btn="cth">CTH</button>
      <button type="button" class="nav-brand-btn${brand === 'rein' ? ' active' : ''}" data-nav-brand-btn="rein">REIN</button>
    </div>`;

  const nav = document.createElement('nav');
  nav.className = 'nexus-nav';
  nav.innerHTML = `
    <a class="nav-brand" href="/p/home">
      <span class="nav-logo-mark">Cleantech<em>HUB</em></span>
      <span class="nav-nexus-pill">NEXUS</span>
    </a>

    <div class="nav-links">
      ${pages.map(p => `
        <a class="nav-link${p.gated ? ' gated' : ''}${p.id === active ? ' active' : ''}" href="${p.href}" title="${p.gated ? 'Solo staff CTH (@cleantechhub.net) / CTH staff only' : ''}">${navLabel(p)}</a>
      `).join('')}
    </div>

    <div class="nav-right">
      ${brandToggleHtml}
      <div class="lang-toggle">
        <button class="lang-btn${lang === 'ES' ? ' active' : ''}">ES</button>
        <button class="lang-btn${lang === 'EN' ? ' active' : ''}">EN</button>
      </div>
      <div class="nav-avatar" title="Gideon Blaauw — CTH Team">GB</div>
    </div>

    <button class="nav-hamburger" aria-label="Menú" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
  `;

  const menu = document.createElement('div');
  menu.className = 'nav-mobile-menu';
  menu.innerHTML = pages.map(p => `
    <a class="nav-mobile-link${p.gated ? ' gated' : ''}${p.id === active ? ' active' : ''}" href="${p.href}" title="${p.gated ? 'Solo staff CTH (@cleantechhub.net) / CTH staff only' : ''}">${navLabel(p)}</a>
  `).join('') + `
    <div class="nav-mobile-footer">
      ${brandToggleHtml}
      <div class="lang-toggle">
        <button class="lang-btn${lang === 'ES' ? ' active' : ''}">ES</button>
        <button class="lang-btn${lang === 'EN' ? ' active' : ''}">EN</button>
      </div>
      <div class="nav-avatar" title="Gideon Blaauw — CTH Team">GB</div>
    </div>
  `;

  document.body.insertBefore(nav, document.body.firstChild);
  document.body.insertBefore(menu, nav.nextSibling);

  const burger = nav.querySelector('.nav-hamburger');
  burger.addEventListener('click', () => {
    const isOpen = menu.classList.toggle('open');
    burger.classList.toggle('open', isOpen);
    burger.setAttribute('aria-expanded', isOpen);
  });

  document.addEventListener('click', (e) => {
    if (!nav.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.remove('open');
      burger.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
    }
  });

  document.querySelectorAll('[data-nav-brand-btn]').forEach((btn) => {
    btn.addEventListener('click', () => setBrand(btn.dataset.navBrandBtn));
  });

  const allLangBtns = [
    ...nav.querySelectorAll('.lang-btn'),
    ...menu.querySelectorAll('.lang-btn'),
  ];
  allLangBtns.forEach(btn => {
    btn.addEventListener('click', () => setLang(btn.textContent.trim()));
  });

  document.documentElement.lang = lang === 'EN' ? 'en' : 'es';
})();
