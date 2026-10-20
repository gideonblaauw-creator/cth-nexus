(function(){var s=document.createElement('style');s.textContent='.step{display:none!important}.step.active{display:block!important}.error-msg{display:none}';document.head.appendChild(s)})();

const VPS_ENDPOINT = 'https://agents.cleantechhub.net/seo/calculator-lead';

const PRODUCTS = [
  {
    name: "Bancolombia Línea Verde PYME",
    bank: "Bancolombia",
    icon: "🟢",
    range: "$50M – $3B COP",
    rate: "DTF + 2-4% E.A.",
    term: "Hasta 10 años",
    sectors: ["energia","transporte","industria","construccion","otro","circular"],
    minRevenue: 500000000,
    tags: ["Crédito directo", "Gran cobertura"]
  },
  {
    name: "Davivienda Crédito Verde",
    bank: "Davivienda",
    icon: "🏦",
    range: "$30M – $1B COP",
    rate: "IBR + 3-5% E.A.",
    term: "Hasta 7 años",
    sectors: ["energia","agro","industria","otro","circular"],
    minRevenue: 200000000,
    tags: ["PYME amigable", "Agro y energía"]
  },
  {
    name: "Bancóldex Sostenibilidad",
    bank: "Bancóldex",
    icon: "🌱",
    range: "$20M – $2B COP",
    rate: "Tasa preferencial",
    term: "Hasta 10 años",
    sectors: ["energia","transporte","industria","construccion","agro","otro","circular"],
    minRevenue: 0,
    tags: ["Todos los tamaños", "Tasa preferencial"]
  },
  {
    name: "FNG Garantía Verde",
    bank: "Fondo Nacional de Garantías",
    icon: "🛡️",
    range: "Hasta 90% de cobertura",
    rate: "Comisión 1-2% anual",
    term: "Según crédito principal",
    sectors: ["energia","transporte","industria","construccion","agro","otro","circular"],
    minRevenue: 0,
    tags: ["Sin historial OK", "Complementario"]
  },
  {
    name: "Finagro Crédito Ecológico",
    bank: "Finagro",
    icon: "🌾",
    range: "$10M – $500M COP",
    rate: "DTF + 1-2% E.A.",
    term: "Hasta 15 años",
    sectors: ["agro"],
    minRevenue: 0,
    tags: ["Sector agro", "Plazo largo"]
  },
  {
    name: "Banco Agrario Línea Verde",
    bank: "Banco Agrario",
    icon: "🌿",
    range: "$5M – $300M COP",
    rate: "Tasa subsidiada",
    term: "Hasta 12 años",
    sectors: ["agro"],
    minRevenue: 0,
    tags: ["Rural", "Tasa subsidiada"]
  },
  {
    name: "BID Invest Green Finance",
    bank: "Banco Interamericano / BID",
    icon: "🌍",
    range: "$500M COP+",
    rate: "SOFR + 3-4%",
    term: "Hasta 15 años",
    sectors: ["energia","transporte","industria"],
    minRevenue: 5000000000,
    tags: ["Empresas medianas-grandes", "USD / COP"]
  }
];

const RANGES = [
  { max: 100000000,   label: "$10M – $100M COP" },
  { max: 500000000,   label: "$50M – $500M COP" },
  { max: 1500000000,  label: "$100M – $1.5B COP" },
  { max: 5000000000,  label: "$500M – $3B COP" },
  { max: Infinity,    label: "$1B – $10B COP" }
];

function getRange(revenue) {
  return RANGES.find(r => revenue <= r.max)?.label || "$1B – $10B COP";
}

function matchProducts(sector, revenue, project) {
  let matched = PRODUCTS.filter(p =>
    p.sectors.includes(sector) && parseFloat(revenue) >= p.minRevenue
  );
  // Boost agro products for agro sector
  if (sector === 'agro') {
    matched = matched.sort((a,b) => (a.bank.includes('Finagro') || a.bank.includes('Agrario') ? -1 : 1));
  }
  // Always include Bancóldex as fallback
  if (!matched.find(p => p.bank.includes('Bancóldex'))) {
    const bancoldex = PRODUCTS.find(p => p.bank.includes('Bancóldex'));
    if (bancoldex) matched.push(bancoldex);
  }
  return matched.slice(0, 3);
}

function goToStep(n) {
  document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
  document.getElementById('step-' + n).classList.add('active');
  document.getElementById('progress').style.width = (n / 4 * 100) + '%';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function goToStep2() {
  const sector = document.getElementById('sector').value;
  const revenue = document.getElementById('revenue').value;
  let valid = true;
  if (!sector) { document.getElementById('err-sector').style.display = 'block'; valid = false; }
  else document.getElementById('err-sector').style.display = 'none';
  if (!revenue) { document.getElementById('err-revenue').style.display = 'block'; valid = false; }
  else document.getElementById('err-revenue').style.display = 'none';
  if (valid) goToStep(2);
}

function goToEmailGate() {
  const project = document.getElementById('project').value;
  const amount = document.getElementById('amount').value;
  let valid = true;
  if (!project) { document.getElementById('err-project').style.display = 'block'; valid = false; }
  else document.getElementById('err-project').style.display = 'none';
  if (!amount) { document.getElementById('err-amount').style.display = 'block'; valid = false; }
  else document.getElementById('err-amount').style.display = 'none';
  if (valid) goToStep(3);
}

function isValidEmail(e) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e); }

async function unlockResults() {
  const email = document.getElementById('email-input').value.trim();
  if (!isValidEmail(email)) {
    document.getElementById('err-email').style.display = 'block';
    return;
  }
  document.getElementById('err-email').style.display = 'none';

  const btn = document.getElementById('btn-unlock');
  btn.innerHTML = '<span class="spinner"></span> Calculando...';
  btn.disabled = true;

  const sector = document.getElementById('sector').value;
  const revenue = parseFloat(document.getElementById('revenue').value);
  const project = document.getElementById('project').value;
  const amount = parseFloat(document.getElementById('amount').value);

  // Show results immediately (optimistic)
  const range = getRange(revenue);
  const products = matchProducts(sector, revenue, project);

  document.getElementById('result-range').textContent = range;

  const grid = document.getElementById('products-grid');
  grid.innerHTML = products.map((p, i) => `
    <div class="product-card ${i === 0 ? 'top' : ''}">
      <div class="product-icon">${p.icon}</div>
      <div>
        <div class="product-name">${p.name}${i === 0 ? '<span class="top-badge">Mejor match</span>' : ''}</div>
        <div class="product-bank">${p.bank}</div>
        <div class="product-pills">
          <span class="pill">📋 ${p.range}</span>
          <span class="pill green">📅 ${p.term}</span>
          ${p.tags.map(t => `<span class="pill">${t}</span>`).join('')}
        </div>
      </div>
    </div>
  `).join('');

  goToStep(4);

  // Fire webhook async (don't block UX)
  try {
    await fetch(VPS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        sector,
        revenue,
        project_type: project,
        amount,
        products_shown: products.map(p => p.name)
      })
    });
  } catch(e) {
    // Silent fail — results already shown
    console.warn('Webhook error:', e.message);
  }
}