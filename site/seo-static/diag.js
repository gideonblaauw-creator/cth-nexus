/* ===== CSS INJECTION — Diagnóstico Verde UI v2 ===== */
(function(){
var css = `
/* ===== DIAG UI v2 ===== */
.step{display:none!important}.step.active{display:block!important}.error-msg{display:none}

/* --- PAGE CONTEXT CLEANUP --- */
/* Remove Astra theme's large article padding */
article.ast-article-single {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}
/* Hide WordPress-generated junk paragraphs (stray <br>, <meta> etc.) */
.entry-content > p { display: none !important; }
/* Hero bleeds behind sticky nav; padding-top clears nav height */
#primary.content-area { margin-top: 0 !important; }
article.post { padding-bottom: 0 !important; }
.entry-header { display: none !important; }
/* Allow hero to break out of the content column */
.entry-content, article.ast-article-single { overflow: visible !important; }

/* --- HERO --- */
.hero {
  background: linear-gradient(150deg, #083566 0%, #0C498A 55%, #1a5f3a 100%) !important;
  color: white !important;
  text-align: center !important;
  padding: 116px 32px 52px !important;
  margin: 0 !important;
  border-radius: 0 !important;
  position: relative !important;
  overflow: hidden !important;
  /* Full-bleed: break out of the content column */
  width: 100vw !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
}
.hero::before {
  content: '' !important;
  position: absolute !important;
  inset: 0 !important;
  background: radial-gradient(ellipse 60% 50% at 80% 20%, rgba(82,183,136,.18) 0%, transparent 60%),
              radial-gradient(ellipse 50% 60% at 10% 80%, rgba(255,255,255,.05) 0%, transparent 55%) !important;
  pointer-events: none !important;
}
/* Constrain hero content to readable width and center it */
.hero > * {
  max-width: 680px !important;
  margin-left: auto !important;
  margin-right: auto !important;
  text-align: center !important;
  position: relative !important;
}
.hero h1, .hero h2 {
  font-family: 'Rubik', 'Inter', system-ui, sans-serif !important;
  font-size: clamp(20px, 4vw, 28px) !important;
  font-weight: 800 !important;
  color: white !important;
  margin: 0 0 10px !important;
  line-height: 1.25 !important;
  position: relative !important;
}
.hero > p {
  font-size: 13.5px !important;
  color: rgba(255,255,255,.75) !important;
  margin: 0 0 22px !important;
  line-height: 1.65 !important;
  position: relative !important;
}
.hero-pills {
  display: flex !important;
  gap: 8px !important;
  justify-content: center !important;
  flex-wrap: wrap !important;
  position: relative !important;
}
.hero-pill {
  background: rgba(255,255,255,.12) !important;
  border: 1px solid rgba(255,255,255,.2) !important;
  color: rgba(255,255,255,.9) !important;
  padding: 5px 14px !important;
  border-radius: 20px !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  backdrop-filter: blur(4px) !important;
}

/* --- CONTAINER --- */
.container {
  max-width: 640px !important;
  margin: 0 auto !important;
  padding: 0 16px 56px !important;
}

/* --- PROGRESS BAR --- */
.progress-wrap {
  background: white !important;
  border-bottom: 1px solid #E2E8F0 !important;
  padding: 11px 20px !important;
  position: sticky !important;
  top: 0 !important;
  z-index: 50 !important;
  box-shadow: 0 2px 16px rgba(0,0,0,.06) !important;
  display: flex !important;
  align-items: center !important;
  gap: 14px !important;
  margin: 0 -16px !important;
}
.progress-meta {
  display: flex !important;
  flex-direction: column !important;
  gap: 1px !important;
  min-width: 86px !important;
  flex-shrink: 0 !important;
}
.progress-label {
  font-size: 10.5px !important;
  font-weight: 700 !important;
  color: #0C498A !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  line-height: 1.3 !important;
}
.progress-count {
  font-size: 10px !important;
  color: #94A3B8 !important;
  white-space: nowrap !important;
  line-height: 1.3 !important;
}
.progress-bar-bg {
  flex: 1 !important;
  height: 7px !important;
  background: #F1F5F9 !important;
  border-radius: 4px !important;
  overflow: hidden !important;
  min-width: 60px !important;
}
.progress-bar {
  height: 100% !important;
  border-radius: 4px !important;
  background: linear-gradient(90deg, #DC2626 0%, #D97706 45%, #52B788 100%) !important;
  transition: width .8s cubic-bezier(.34,1.2,.64,1) !important;
}

/* --- STEP ANIMATION --- */
.step.active {
  animation: diagSlideIn .38s cubic-bezier(.34,1.15,.64,1) both !important;
}
@keyframes diagSlideIn {
  from { opacity: 0; transform: translateY(14px) scale(.975); }
  to   { opacity: 1; transform: none; }
}

/* --- QUESTION CARD --- */
.q-card {
  background: white !important;
  border-radius: 18px !important;
  padding: 28px 24px !important;
  box-shadow: 0 4px 28px rgba(0,0,0,.07), 0 1px 4px rgba(0,0,0,.04) !important;
  margin: 20px 0 14px !important;
  border: 1px solid #F1F5F9 !important;
}
.q-number { display: none !important; }
.q-text {
  font-size: 17.5px !important;
  font-weight: 800 !important;
  color: #1E293B !important;
  line-height: 1.35 !important;
  margin-bottom: 20px !important;
}

/* --- OPTION BUTTONS --- */
.options { display: grid !important; gap: 8px !important; }
.opt-btn {
  width: 100% !important;
  text-align: left !important;
  padding: 14px 16px !important;
  border: 1.5px solid #E2E8F0 !important;
  border-radius: 12px !important;
  background: #FAFAFA !important;
  cursor: pointer !important;
  font-size: 13.5px !important;
  color: #1E293B !important;
  transition: border-color .18s, background .18s, box-shadow .18s, transform .15s !important;
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  font-family: inherit !important;
  position: relative !important;
}
.opt-btn:hover {
  border-color: #0C498A !important;
  background: #EFF6FF !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 16px rgba(12,73,138,.1) !important;
}
.opt-btn.selected {
  border-color: #0C498A !important;
  background: #EFF6FF !important;
  box-shadow: 0 4px 18px rgba(12,73,138,.13) !important;
}
.opt-btn .opt-icon {
  font-size: 20px !important;
  width: 42px !important;
  height: 42px !important;
  background: white !important;
  border-radius: 10px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  flex-shrink: 0 !important;
  box-shadow: 0 1px 5px rgba(0,0,0,.08) !important;
  line-height: 1 !important;
}
.opt-btn.selected .opt-icon {
  background: linear-gradient(135deg, #EFF6FF 0%, #D8F3DC 100%) !important;
}
.opt-btn .opt-label {
  flex: 1 !important;
  font-weight: 600 !important;
  line-height: 1.35 !important;
}
.opt-btn .opt-check {
  width: 22px !important;
  height: 22px !important;
  border-radius: 50% !important;
  border: 2px solid #CBD5E1 !important;
  flex-shrink: 0 !important;
  transition: all .2s cubic-bezier(.34,1.5,.64,1) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 0 !important;
}
.opt-btn.selected .opt-check {
  background: #0C498A !important;
  border-color: #0C498A !important;
  font-size: 12px !important;
}
.opt-btn.selected .opt-check::after {
  content: '✓' !important;
  color: white !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  line-height: 1 !important;
}

/* --- NAV BUTTONS --- */
.nav-btns {
  display: flex !important;
  gap: 10px !important;
  margin-top: 12px !important;
}
.btn {
  flex: 1 !important;
  padding: 15px !important;
  border: none !important;
  border-radius: 12px !important;
  font-size: 14px !important;
  font-weight: 700 !important;
  cursor: pointer !important;
  transition: transform .15s, box-shadow .15s, opacity .2s !important;
  font-family: inherit !important;
  letter-spacing: 0.2px !important;
}
.btn-primary {
  background: linear-gradient(135deg, #0C498A 0%, #2a7a50 100%) !important;
  color: white !important;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 26px rgba(12,73,138,.3) !important;
}
.btn-primary:disabled { opacity: 0.4 !important; cursor: not-allowed !important; }
.btn-back {
  background: white !important;
  color: #64748B !important;
  border: 1.5px solid #E2E8F0 !important;
  flex: 0 0 auto !important;
  padding: 15px 22px !important;
}
.btn-back:hover { background: #F8FAFC !important; border-color: #CBD5E1 !important; }

/* Standalone continue button (no nav-btns wrapper) */
button.btn.btn-primary:not(.btn-back) {
  margin-top: 12px !important;
}

/* --- EMAIL GATE --- */
.email-gate {
  background: linear-gradient(150deg, #0C498A 0%, #083566 50%, #1a5f3a 100%) !important;
  border-radius: 18px !important;
  padding: 36px 28px !important;
  color: white !important;
  box-shadow: 0 12px 48px rgba(12,73,138,.28) !important;
  margin: 20px 0 !important;
  position: relative !important;
  overflow: hidden !important;
}
.email-gate::before {
  content: '' !important;
  position: absolute !important;
  inset: 0 !important;
  background: radial-gradient(ellipse 55% 45% at 85% 15%, rgba(82,183,136,.18) 0%, transparent 55%) !important;
  pointer-events: none !important;
}
.gate-icon { font-size: 44px !important; margin-bottom: 14px !important; position: relative !important; }
.gate-title {
  font-size: 20px !important;
  font-weight: 800 !important;
  color: white !important;
  margin-bottom: 10px !important;
  line-height: 1.3 !important;
  position: relative !important;
}
.gate-sub {
  font-size: 13px !important;
  color: rgba(255,255,255,.72) !important;
  line-height: 1.65 !important;
  margin-bottom: 24px !important;
  max-width: 420px !important;
  position: relative !important;
}
.gate-name-input, .gate-input {
  width: 100% !important;
  padding: 14px 18px !important;
  border: 2px solid rgba(255,255,255,.28) !important;
  border-radius: 12px !important;
  background: rgba(255,255,255,.13) !important;
  color: white !important;
  font-size: 14px !important;
  font-family: inherit !important;
  outline: none !important;
  margin-bottom: 10px !important;
  box-sizing: border-box !important;
  position: relative !important;
  transition: border-color .2s !important;
}
.gate-name-input::placeholder, .gate-input::placeholder { color: rgba(255,255,255,.44) !important; }
.gate-name-input:focus, .gate-input:focus { border-color: rgba(255,255,255,.7) !important; }
.btn-green {
  background: white !important;
  color: #0C498A !important;
  font-weight: 800 !important;
  width: 100% !important;
  padding: 15px !important;
  border-radius: 12px !important;
  border: none !important;
  font-size: 15px !important;
  cursor: pointer !important;
  font-family: inherit !important;
  transition: transform .15s, box-shadow .15s !important;
  position: relative !important;
}
.btn-green:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 28px rgba(0,0,0,.22) !important;
}
.privacy {
  font-size: 11px !important;
  color: rgba(255,255,255,.44) !important;
  margin-top: 12px !important;
  text-align: center !important;
}
#google-signin-btn { margin: 14px 0 8px !important; display: flex !important; justify-content: center !important; }

/* --- SCORE REVEAL --- */
.score-reveal { text-align: center !important; margin-bottom: 24px !important; }
.score-ring-wrap {
  position: relative !important;
  width: 160px !important;
  height: 160px !important;
  margin: 0 auto 18px !important;
}
.score-ring-wrap svg {
  width: 160px !important;
  height: 160px !important;
  transform: rotate(-90deg) !important;
}
.score-number {
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  font-size: 44px !important;
  font-weight: 900 !important;
  color: #0C498A !important;
  line-height: 1 !important;
}
.score-label {
  position: absolute !important;
  bottom: 22px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  font-size: 10px !important;
  color: #94A3B8 !important;
  font-weight: 600 !important;
  white-space: nowrap !important;
}

/* --- TIER BADGES --- */
.tier-badge {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 9px 20px !important;
  border-radius: 100px !important;
  font-size: 14px !important;
  font-weight: 800 !important;
  margin-bottom: 10px !important;
}
.tier-verde { background: #D8F3DC !important; color: #2D6A4F !important; }
.tier-desarrollo { background: #FEF3C7 !important; color: #92400E !important; }
.tier-formacion { background: #FEE2E2 !important; color: #991B1B !important; }
.tier-desc {
  font-size: 13.5px !important;
  color: #64748B !important;
  line-height: 1.6 !important;
  max-width: 440px !important;
  margin: 0 auto 24px !important;
  text-align: center !important;
}

/* --- SECTION LABEL --- */
.section-label {
  font-size: 10px !important;
  font-weight: 700 !important;
  color: #94A3B8 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.7px !important;
  margin-bottom: 12px !important;
}

/* --- PRODUCT CARDS --- */
.product-card {
  background: white !important;
  border: 1.5px solid #E2E8F0 !important;
  border-radius: 14px !important;
  padding: 16px !important;
  display: flex !important;
  gap: 14px !important;
  margin-bottom: 10px !important;
  align-items: flex-start !important;
  transition: border-color .18s, box-shadow .18s !important;
}
.product-card:hover {
  border-color: #0C498A !important;
  box-shadow: 0 4px 18px rgba(12,73,138,.09) !important;
}
.product-card.best {
  border-color: #52B788 !important;
  background: #F0FFF4 !important;
}
.p-icon { font-size: 28px !important; flex-shrink: 0 !important; margin-top: 2px !important; }
.p-name { font-size: 13.5px !important; font-weight: 700 !important; color: #0C498A !important; line-height: 1.3 !important; }
.p-bank { font-size: 11px !important; color: #94A3B8 !important; margin: 3px 0 7px !important; }
.p-pills { display: flex !important; gap: 5px !important; flex-wrap: wrap !important; }
.pill {
  font-size: 10px !important;
  font-weight: 600 !important;
  padding: 3px 10px !important;
  border-radius: 10px !important;
  background: #EFF6FF !important;
  color: #0C498A !important;
}
.pill.g { background: #D8F3DC !important; color: #2D6A4F !important; }
.best-tag {
  font-size: 9px !important;
  font-weight: 700 !important;
  background: #52B788 !important;
  color: white !important;
  padding: 1px 8px !important;
  border-radius: 4px !important;
  margin-left: 6px !important;
  vertical-align: middle !important;
}

/* --- CTA CARDS --- */
.cta-card {
  border-radius: 16px !important;
  padding: 24px !important;
  text-align: center !important;
  margin-top: 20px !important;
}
.cta-verde  { background: linear-gradient(135deg, #D8F3DC, #EFF6FF) !important; border: 1.5px solid #52B788 !important; }
.cta-desarrollo { background: #FEF3C7 !important; border: 1.5px solid #FCD34D !important; }
.cta-formacion  { background: #FEE2E2 !important; border: 1.5px solid #FCA5A5 !important; }
.cta-card h3 { font-size: 16px !important; font-weight: 800 !important; color: #1E293B !important; margin: 0 0 8px !important; }
.cta-card p  { font-size: 13px !important; color: #64748B !important; line-height: 1.6 !important; margin: 0 0 18px !important; }
.cta-btn {
  display: block !important;
  padding: 16px 24px !important;
  border-radius: 12px !important;
  font-size: 14.5px !important;
  font-weight: 700 !important;
  text-decoration: none !important;
  text-align: center !important;
  transition: transform .15s, box-shadow .15s !important;
}
.cta-btn:hover { transform: translateY(-2px) !important; box-shadow: 0 10px 30px rgba(0,0,0,.2) !important; }
.cta-btn-green { background: linear-gradient(135deg, #2D6A4F, #52B788) !important; color: white !important; }
.cta-btn-blue  { background: linear-gradient(135deg, #0C498A, #1a69bf) !important; color: white !important; }
.cta-btn-gold  { background: linear-gradient(135deg, #D97706, #F59E0B) !important; color: white !important; }

/* --- SHARE ROW --- */
.share-row {
  display: flex !important;
  gap: 8px !important;
  justify-content: center !important;
  margin-top: 16px !important;
  flex-wrap: wrap !important;
}
.share-btn {
  font-size: 12px !important;
  font-weight: 600 !important;
  padding: 8px 16px !important;
  border-radius: 100px !important;
  border: 1.5px solid #E2E8F0 !important;
  background: white !important;
  color: #1E293B !important;
  cursor: pointer !important;
  font-family: inherit !important;
  transition: background .15s, border-color .15s !important;
}
.share-btn:hover { background: #F1F5F9 !important; border-color: #CBD5E1 !important; }

/* --- SPINNER --- */
.spinner {
  display: inline-block !important;
  width: 18px !important;
  height: 18px !important;
  border: 2.5px solid rgba(12,73,138,.18) !important;
  border-top-color: #0C498A !important;
  border-radius: 50% !important;
  animation: diagSpin .75s linear infinite !important;
  vertical-align: middle !important;
  margin-right: 8px !important;
}
@keyframes diagSpin { to { transform: rotate(360deg); } }

/* --- MOBILE --- */
@media (max-width: 540px) {
  .hero { padding: 84px 20px 36px !important; margin: 0 !important; }
  .hero h1, .hero h2 { font-size: 20px !important; }
  .hero > p { font-size: 12.5px !important; }
  .q-card { padding: 22px 18px !important; margin: 14px 0 12px !important; }
  .q-text { font-size: 15.5px !important; }
  .opt-btn { padding: 12px 13px !important; gap: 10px !important; }
  .opt-btn .opt-icon { width: 36px !important; height: 36px !important; font-size: 17px !important; }
  .opt-btn .opt-label { font-size: 12.5px !important; }
  .email-gate { padding: 28px 20px !important; }
  .progress-wrap { margin: 0 -16px !important; padding: 10px 16px !important; }
  .progress-meta { min-width: 72px !important; }
}
`;
var s=document.createElement('style');
s.textContent=css;
document.head.appendChild(s);
})();

const VPS_DIAGNOSTIC = 'https://agents.cleantechhub.net/seo/diagnostic-complete';
const GOOGLE_CLIENT_ID = '229091354163-2v1auknuc9t9f35ncudd4ajmdtr8dvp7.apps.googleusercontent.com';

const answers = {};
let userEmail = '';
let userName = '';

// Scoring weights
const SCORING = {
  sector:    { energia:18, transporte:15, agro:13, industria:15, construccion:13, circular:12 },
  revenue:   { rev_xs:4, rev_s:8, rev_m:12, rev_l:16, rev_xl:18 },
  project:   { eficiencia:12, renovable:12, transporte_p:12, residuos:10, construccion_p:10, agro_p:10 },
  certs:     { iso:15, en_proceso:11, plan:9, ninguna:4 },
  years:     { '10mas':10, '5a10':8, '2a5':5, menos2:2 },
  credit:    { excelente:12, bueno:9, regular:5, sin_historial:2 },
  amount:    { amt_xs:8, amt_s:8, amt_m:8, amt_l:7, amt_xl:5 }
};
const MAX_SCORE = 18+18+12+15+10+12+8; // 93

const PRODUCTS = [
  { name:"Bancolombia Línea Verde PYME", bank:"Bancolombia", icon:"🟢", range:"$50M – $3B COP", term:"Hasta 10 años",
    sectors:["energia","transporte","industria","construccion","circular"], minRev:"rev_s",
    tags:["Crédito directo","Alta aprobación"] },
  { name:"Davivienda Crédito Verde", bank:"Davivienda", icon:"🏦", range:"$30M – $1B COP", term:"Hasta 7 años",
    sectors:["energia","agro","industria","circular"], minRev:"rev_xs",
    tags:["PYME amigable","Agro y energía"] },
  { name:"Bancóldex Sostenibilidad", bank:"Bancóldex", icon:"🌱", range:"$20M – $2B COP", term:"Hasta 10 años",
    sectors:["energia","transporte","industria","construccion","agro","circular"], minRev:"rev_xs",
    tags:["Todos los tamaños","Tasa preferencial"] },
  { name:"FNG Garantía Verde", bank:"Fondo Nacional de Garantías", icon:"🛡️", range:"Hasta 90% cobertura", term:"Según crédito",
    sectors:["energia","transporte","industria","construccion","agro","circular"], minRev:"rev_xs",
    tags:["Sin historial OK","Complementario"] },
  { name:"Finagro Crédito Ecológico", bank:"Finagro", icon:"🌾", range:"$10M – $500M COP", term:"Hasta 15 años",
    sectors:["agro"], minRev:"rev_xs",
    tags:["Sector agro","Plazo largo"] },
  { name:"Banco Agrario Línea Verde", bank:"Banco Agrario", icon:"🌿", range:"$5M – $300M COP", term:"Hasta 12 años",
    sectors:["agro"], minRev:"rev_xs",
    tags:["Rural","Tasa subsidiada"] },
  { name:"BID Invest Green Finance", bank:"BID / IFC", icon:"🌍", range:"$500M+ COP", term:"Hasta 15 años",
    sectors:["energia","transporte","industria"], minRev:"rev_l",
    tags:["Grandes empresas","USD/COP"] }
];

const REV_ORDER = ["rev_xs","rev_s","rev_m","rev_l","rev_xl"];

function revGte(userRev, minRev) {
  return REV_ORDER.indexOf(userRev) >= REV_ORDER.indexOf(minRev);
}

function matchProducts(sector, rev) {
  let matched = PRODUCTS.filter(p => p.sectors.includes(sector) && revGte(rev, p.minRev));
  if (matched.length < 2) {
    const bc = PRODUCTS.find(p => p.bank === 'Bancóldex');
    if (bc && !matched.includes(bc)) matched.push(bc);
    const fng = PRODUCTS.find(p => p.bank.includes('Garantías'));
    if (fng && !matched.includes(fng)) matched.push(fng);
  }
  return matched.slice(0, 3);
}

function calcScore() {
  const ansKeys = [answers[1], answers[2], answers[3], answers[4], answers[5], answers[6], answers[7]];
  const scoreKeys = ['sector','revenue','project','certs','years','credit','amount'];
  let total = 0;
  scoreKeys.forEach((k, i) => { total += SCORING[k][ansKeys[i]] || 0; });
  return Math.round((total / MAX_SCORE) * 100);
}

function getTier(score) {
  if (score >= 70) return 'verde_listo';
  if (score >= 40) return 'en_desarrollo';
  return 'en_formacion';
}

function selectOption(q, val) {
  answers[q] = val;
  document.querySelectorAll(`[data-q="${q}"]`).forEach(b => b.classList.remove('selected'));
  event.currentTarget.classList.add('selected');
  const btn = document.getElementById(`btn-next-${q}`);
  if (btn) btn.disabled = false;
}

function updateProgress(step) {
  const totalSteps = 7;
  const pct = (step / totalSteps) * 100;
  document.getElementById('progress-bar').style.width = pct + '%';
  document.getElementById('progress-label').textContent = `Pregunta ${step} de ${totalSteps}`;
  const notes = {3: '💡 Ya estás a mitad del camino', 5:'💪 ¡Ya casi!', 7:'🎯 Última pregunta'};
  document.getElementById('progress-note').textContent = notes[step] || '';
}

function goNext(step) {
  if (step <= 7) {
    showStep('step-' + step);
    if (step <= 7) updateProgress(step);
  }
}

function goBack(step) {
  showStep('step-' + step);
  updateProgress(step);
}

function showStep(id) {
  document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showEmailGate() {
  // Step 3 button calls this — now just advance to step 4
  if (!answers[3]) return;
  showStep('step-4');
  updateProgress(4);
}

function continueAfterGate() {
  const email = document.getElementById('gate-email').value.trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    document.getElementById('err-gate-email').style.display = 'block';
    return;
  }
  document.getElementById('err-gate-email').style.display = 'none';
  userEmail = email;
  userName = document.getElementById('gate-name').value.trim();
  _renderAndShow();
}

// Called by Google Identity Services after sign-in
function handleGoogleSignIn(response) {
  try {
    // Decode JWT payload (middle part, base64url)
    const payload = JSON.parse(atob(response.credential.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));
    userEmail = payload.email || '';
    userName  = payload.name  || '';
    // Prefill fields so manual flow still validates
    const emailEl = document.getElementById('gate-email');
    const nameEl  = document.getElementById('gate-name');
    if (emailEl) emailEl.value = userEmail;
    if (nameEl)  nameEl.value  = userName;
    // Proceed immediately
    document.getElementById('err-gate-email').style.display = 'none';
    _renderAndShow();
  } catch(e) {
    console.warn('Google sign-in decode failed:', e);
  }
}

function showResults() {
  if (!answers[7]) return;
  if (!userEmail) {
    // All 7 questions done — now ask for email
    document.getElementById('progress-wrap').style.display = 'none';
    showStep('step-email');
    return;
  }
  _renderAndShow();
}

function _renderAndShow() {
  showStep('step-loading');
  setTimeout(() => {
    const score = calcScore();
    const tier = getTier(score);
    const products = matchProducts(answers[1], answers[2]);
    renderResults(score, tier, products);
    sendWebhook(score, tier, products);
    showStep('step-results');
    animateScore(score, tier);
  }, 1800);
}

function animateScore(score, tier) {
  const arc = document.getElementById('score-arc');
  const display = document.getElementById('score-display');
  const circumference = 352;
  const tierColors = { verde_listo:'#52B788', en_desarrollo:'#D97706', en_formacion:'#DC2626' };
  arc.style.stroke = tierColors[tier];

  let current = 0;
  const target = score;
  const interval = setInterval(() => {
    current = Math.min(current + 2, target);
    display.textContent = current;
    arc.style.strokeDashoffset = circumference - (circumference * current / 100);
    if (current >= target) clearInterval(interval);
  }, 18);
}

function renderResults(score, tier, products) {
  const tierData = {
    verde_listo: { label:'✅ Verde Listo', cls:'tier-verde', desc:'Tu empresa tiene un perfil sólido para acceder a financiamiento verde. Los productos de abajo aplican directamente a tu caso.' },
    en_desarrollo: { label:'🔄 En Desarrollo', cls:'tier-desarrollo', desc:'Tu empresa tiene potencial. Con algunos ajustes en tu perfil financiero o proyecto, podrás acceder a crédito verde en los próximos 3-6 meses.' },
    en_formacion: { label:'📚 En Formación', cls:'tier-formacion', desc:'Tu empresa está en etapa temprana. Tenemos recursos gratuitos para prepararte y mejorar tu Green Score.' }
  }[tier];

  document.getElementById('tier-badge-wrap').innerHTML = `<div class="tier-badge ${tierData.cls}">${tierData.label}</div>`;
  document.getElementById('tier-desc').textContent = tierData.desc;

  document.getElementById('products-result').innerHTML = products.map((p, i) => `
    <div class="product-card ${i === 0 ? 'best' : ''}">
      <div class="p-icon">${p.icon}</div>
      <div>
        <div class="p-name">${p.name}${i === 0 ? '<span class="best-tag">Mejor match</span>' : ''}</div>
        <div class="p-bank">${p.bank}</div>
        <div class="p-pills">
          <span class="pill">📋 ${p.range}</span>
          <span class="pill g">📅 ${p.term}</span>
          ${p.tags.map(t => `<span class="pill">${t}</span>`).join('')}
        </div>
      </div>
    </div>
  `).join('');

  // All tiers go to the full apply questionnaire
  const applyUrl = `https://rutaverde.cleantechhub.net/apply.html?utm_source=diagnostico&utm_campaign=${tier}&score=${score}`;
  const ctas = {
    verde_listo: {
      cls:'cta-verde', btnCls:'cta-btn-green',
      title:'🎯 Estás listo para aplicar. Te acompañamos.',
      desc:'Un asesor de CleantechHUB puede guiarte en el proceso completo: documentación, elección del banco correcto y presentación de tu expediente.',
      cta:'Solicitar Asesoría y Acompañamiento →'
    },
    en_desarrollo: {
      cls:'cta-desarrollo', btnCls:'cta-btn-gold',
      title:'📈 Casi listo. Aplica ahora y te orientamos.',
      desc:'Nuestro equipo revisará tu perfil y te indicará exactamente qué ajustes necesitas antes de presentar tu expediente.',
      cta:'Iniciar proceso de aplicación →'
    },
    en_formacion: {
      cls:'cta-formacion', btnCls:'cta-btn-blue',
      title:'📚 Empezar es el primer paso.',
      desc:'Completa el formulario y un asesor te contactará con un plan personalizado para mejorar tu perfil de financiamiento verde.',
      cta:'Iniciar proceso de aplicación →'
    }
  }[tier];

  document.getElementById('cta-block').innerHTML = `
    <div class="cta-card ${ctas.cls}">
      <h3>${ctas.title}</h3>
      <p>${ctas.desc}</p>
      <a href="${applyUrl}" class="cta-btn ${ctas.btnCls}">${ctas.cta}</a>
    </div>
  `;
}

async function sendWebhook(score, tier, products) {
  try {
    await fetch(VPS_DIAGNOSTIC, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: userEmail,
        name: userName,
        score,
        segment: tier,
        answers: {
          sector: answers[1],
          revenue: answers[2],
          project: answers[3],
          certs: answers[4],
          years: answers[5],
          credit: answers[6],
          amount: answers[7]
        },
        products_matched: products.map(p => p.name)
      })
    });
  } catch(e) {
    console.warn('Webhook error:', e.message);
  }
}

function downloadResultsSVG() {
  const score = parseInt(document.getElementById('score-display').textContent) || 0;
  const tierBadge = document.getElementById('tier-badge-wrap').innerText.trim();
  const tierDesc  = document.getElementById('tier-desc').innerText.trim();
  const today = new Date().toLocaleDateString('es-CO', { year:'numeric', month:'long', day:'numeric' });

  // Collect product data from rendered DOM
  const productCards = [...document.getElementById('products-result').querySelectorAll('.product-card')];
  const products = productCards.map((card, i) => ({
    best: card.classList.contains('best'),
    icon: card.querySelector('.p-icon')?.textContent || '',
    name: card.querySelector('.p-name')?.childNodes[0]?.textContent?.trim() || '',
    bank: card.querySelector('.p-bank')?.textContent || '',
    pills: [...card.querySelectorAll('.pill')].map(p => p.textContent)
  }));

  const tierColor = score >= 70 ? '#52B788' : score >= 40 ? '#D97706' : '#DC2626';
  const tierBg    = score >= 70 ? '#D8F3DC' : score >= 40 ? '#FEF3C7' : '#FEE2E2';
  const tierFg    = score >= 70 ? '#2D6A4F' : score >= 40 ? '#92400E' : '#991B1B';

  const CARD_H = 64;
  const totalH = 320 + products.length * (CARD_H + 8) + 48;

  // Build product card SVG rows
  const productRows = products.map((p, i) => {
    const y = 264 + i * (CARD_H + 8);
    const pillsText = p.pills.slice(0, 3).join('  ·  ');
    return `
    <rect x="24" y="${y}" width="552" height="${CARD_H}" rx="8"
      fill="${p.best ? '#F0FFF4' : '#FAFAFA'}"
      stroke="${p.best ? '#52B788' : '#E5E7EB'}" stroke-width="1.5"/>
    <text x="58" y="${y + 22}" font-size="11" font-weight="700" fill="#0C498A" font-family="system-ui,sans-serif">${escSVG(p.name)}${p.best ? '  ★ Mejor match' : ''}</text>
    <text x="58" y="${y + 38}" font-size="10" fill="#6B7280" font-family="system-ui,sans-serif">${escSVG(p.bank)}</text>
    <text x="58" y="${y + 54}" font-size="9" fill="#374151" font-family="system-ui,sans-serif">${escSVG(pillsText)}</text>
    <text x="30" y="${y + 38}" font-size="18" font-family="system-ui,sans-serif">${escSVG(p.icon)}</text>`;
  }).join('');

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="${totalH}" viewBox="0 0 600 ${totalH}">
  <!-- Header -->
  <rect width="600" height="${totalH}" rx="12" fill="#fff"/>
  <rect x="0" y="0" width="600" height="120" rx="12" fill="#0C498A"/>
  <rect x="0" y="108" width="600" height="12" fill="#0C498A"/>
  <text x="300" y="72" text-anchor="middle" font-size="64" font-weight="900" fill="white" font-family="system-ui,sans-serif">${score}</text>
  <text x="300" y="96" text-anchor="middle" font-size="11" fill="rgba(255,255,255,0.75)" font-family="system-ui,sans-serif">GREEN SCORE / 100  ·  CleantechHUB Ruta Verde</text>
  <!-- Tier badge -->
  <rect x="175" y="132" width="250" height="28" rx="14" fill="${tierBg}"/>
  <text x="300" y="151" text-anchor="middle" font-size="12" font-weight="800" fill="${tierFg}" font-family="system-ui,sans-serif">${escSVG(tierBadge)}</text>
  <!-- Tier desc -->
  <text x="300" y="186" text-anchor="middle" font-size="10" fill="#555" font-family="system-ui,sans-serif">${escSVG(tierDesc.slice(0, 72))}</text>
  <text x="300" y="200" text-anchor="middle" font-size="10" fill="#555" font-family="system-ui,sans-serif">${escSVG(tierDesc.slice(72, 144))}</text>
  <!-- Section label -->
  <text x="24" y="246" font-size="9" font-weight="700" fill="#6B7280" letter-spacing="0.6" font-family="system-ui,sans-serif">PRODUCTOS DISPONIBLES PARA TU EMPRESA</text>
  <!-- Product cards -->
  ${productRows}
  <!-- Footer -->
  <line x1="24" y1="${totalH - 32}" x2="576" y2="${totalH - 32}" stroke="#E5E7EB" stroke-width="1"/>
  <text x="300" y="${totalH - 14}" text-anchor="middle" font-size="9" fill="#9CA3AF" font-family="system-ui,sans-serif">cleantechhub.net/diagnostico  ·  ${escSVG(today)}</text>
</svg>`;

  const blob = new Blob([svg], {type: 'image/svg+xml'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `GreenScore_${score}_RutaVerde.svg`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 5000);
}

function escSVG(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Init after full DOM is parsed
document.addEventListener('DOMContentLoaded', function() {
  const pw = document.getElementById('progress-wrap');
  if (pw) pw.style.display = 'none';

  // Hide LinkedIn button
  const liBtn = document.getElementById('share-li');
  if (liBtn) liBtn.style.display = 'none';

  // Rewire print/download button → SVG download
  document.querySelectorAll('.share-btn').forEach(btn => {
    if (btn.textContent.includes('Imprimir') || btn.textContent.includes('Descargar')) {
      btn.textContent = '🖨️ Descargar resultados';
      btn.onclick = function(e) { e.preventDefault(); downloadResultsSVG(); return false; };
    }
  });

  // Show progress on step 1
  const step1 = document.getElementById('step-1');
  if (step1) step1.addEventListener('click', function() {
    document.getElementById('progress-wrap').style.display = 'block';
    updateProgress(1);
  }, { once: true });

  // Init Google Sign-In if client ID is configured
  if (GOOGLE_CLIENT_ID && GOOGLE_CLIENT_ID !== 'YOUR_GOOGLE_CLIENT_ID') {
    const gsiScript = document.createElement('script');
    gsiScript.src = 'https://accounts.google.com/gsi/client';
    gsiScript.async = true;
    gsiScript.defer = true;
    gsiScript.onload = function() {
      google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleSignIn,
        auto_select: false
      });
      const container = document.getElementById('google-signin-btn');
      if (container) {
        google.accounts.id.renderButton(container, {
          type: 'standard',
          shape: 'pill',
          theme: 'outline',
          text: 'continue_with',
          size: 'large',
          width: 320
        });
      }
    };
    document.head.appendChild(gsiScript);
  }
});
