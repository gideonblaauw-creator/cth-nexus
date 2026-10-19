/* CLP26 Mentoring Platform — app.js */

const MODULES = [
  "1 · 🧭 El Sueño del Founder",
  "2 · 🤝 Lo Comercial",
  "3 · 🗺️ El Mercado",
  "4 · 💎 El Valor",
  "5 · 📊 Venture Economics",
  "6 · 🌿 Impacto Climático",
  "7 · 👥 Customer Discovery",
  "8 · 🎤 El Pitch"
];
const WIKI = "https://wiki.cleantechhub.net";
const API = "/mentoring/api";

let startups = [];
let mentors = [];
let activeCountry = "all";

/* ── DATA LOADING ────────────────────── */
async function loadStartups() {
  try {
    const resp = await fetch(`${API}/startups`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    startups = await resp.json();
  } catch (e) {
    console.error("Failed to load startups:", e);
    startups = [];
  }
}

async function loadMentors() {
  try {
    const resp = await fetch(`${API}/mentors`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    mentors = await resp.json();
  } catch (e) {
    console.error("Failed to load mentors:", e);
    mentors = [];
  }
}

/* ── NAVIGATION ──────────────────────── */
function go(screen) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('shown', 'visible'));
  const el = document.getElementById('screen-' + screen);
  el.classList.add('visible');
  requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add('shown')));
  document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
  if (screen === 'listing' || screen === 'detail') document.getElementById('nav-startups').classList.add('active');
  if (screen === 'mentors') document.getElementById('nav-mentors').classList.add('active');
  window.scrollTo({ top: 0 });
}

/* ── STARTUP CARDS ───────────────────── */
function stripHtml(html) {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
}

function oneliner(s) {
  if (s.oneliner && !s.oneliner.startsWith('<')) return s.oneliner;
  return stripHtml(s.oneliner || s.description || '').substring(0, 160) + '...';
}

function cardHTML(s) {
  const needsMentor = s.needs_mentor || [];
  const done = s.sessions ? s.sessions.filter(sess => sess.status === 'done').length : 0;
  const pct = Math.round(done / 8 * 100);
  const initial = (s.name || '?')[0].toUpperCase();
  const colorMap = {
    'Colombia': '0C498A/B2EEFA',
    'Peru': 'B2EEFA/0C498A',
    'Guatemala': '9DC384/0C498A',
    'Costa Rica': '669348/B2EEFA',
    'El Salvador': '69B5FA/FFFFFF',
  };
  const colors = colorMap[s.country] || '0C498A/B2EEFA';
  const imgUrl = `https://placehold.co/400x200/${colors}?text=${encodeURIComponent(s.name.substring(0, 20))}`;

  return `
    <div class="startup-card">
      <img class="card-img" src="${imgUrl}" alt="${s.name}">
      <div class="card-body">
        <div class="card-top"><h3>${s.name}</h3><span class="flag" title="${s.country}">${s.flag}</span></div>
        <div class="card-tags">
          <span class="tag tag-green">${s.category}</span>
          <span class="tag tag-blue">${needsMentor.length} sesiones buscan mentor</span>
        </div>
        <p>${oneliner(s)}</p>
        <div class="progress-lbl">Workbook CLP26: ${done}/8 módulos</div>
        <div class="progress-wrap"><div class="progress-fill" style="width:${pct}%"></div></div>
        <button class="btn-primary" onclick="openDetail(${s.page_id})">Mentor this startup</button>
      </div>
    </div>`;
}

/* ── LISTING + FILTERS ───────────────── */
function setCountry(btn) {
  activeCountry = btn.dataset.country;
  document.querySelectorAll('[data-country]').forEach(t => t.classList.remove('on'));
  btn.classList.add('on');
  renderListing();
}

function renderListing() {
  const mod = document.getElementById('module-select').value;
  const matches = startups.filter(s =>
    (activeCountry === "all" || s.country === activeCountry) &&
    (mod === "all" || (s.needs_mentor || []).includes(parseInt(mod)))
  );
  document.getElementById('listing-grid').innerHTML = matches.length
    ? matches.map(cardHTML).join('')
    : '';
  document.getElementById('results-count').textContent = matches.length + " startup" + (matches.length === 1 ? "" : "s") + " · cohorte CLP26";
  document.getElementById('empty-state').style.display = matches.length ? 'none' : 'block';
}

/* ── MENTOR CARDS ────────────────────── */
function mentorCard(m, startupName) {
  if (!m) return '';
  const tags = (m.modules || []).map(n => `<span class="tag tag-cyan">Módulo ${n}</span>`).join('');
  const waText = encodeURIComponent(`Hola ${(m.name || '').split(' ')[0]}, te escribo desde la plataforma de mentoría CLP26 de CleantechHUB${startupName ? ' sobre ' + startupName : ''}.`);
  const waBtn = m.wa ? `<a class="btn-wa" href="https://wa.me/${m.wa}?text=${waText}" target="_blank" rel="noopener">WhatsApp</a>` : '';
  return `
    <div class="mentor-card">
      <img src="${m.img || 'https://placehold.co/128x128/0C498A/B2EEFA?text=' + (m.name || '?')[0]}" alt="${m.name}">
      <div class="mentor-info">
        <h3>${m.name}</h3>
        <div class="company">${m.company || ''}</div>
        <div class="mentor-tags">${tags}</div>
        <div class="avail">Disponibilidad: ${m.avail || 'Por confirmar'}</div>
        <div class="contact-row">
          ${m.email ? `<a class="btn-mail" href="mailto:${m.email}?subject=${encodeURIComponent('Mentoría CLP26' + (startupName ? ' — ' + startupName : ''))}">&#x2709; Email</a>` : ''}
          ${waBtn}
        </div>
      </div>
    </div>`;
}

/* ── DETAIL ──────────────────────────── */
async function openDetail(pageId) {
  let s = startups.find(x => x.page_id === pageId);
  if (!s) {
    try {
      const resp = await fetch(`${API}/startups/${pageId}`);
      if (!resp.ok) return;
      s = await resp.json();
    } catch (e) {
      console.error("Failed to load startup detail:", e);
      return;
    }
  }

  document.getElementById('d-name').textContent = s.name;
  document.getElementById('d-tagline').textContent = oneliner(s);
  document.getElementById('d-sector').textContent = s.category;
  document.getElementById('d-country').textContent = s.flag + " " + s.country;
  document.getElementById('d-stage').textContent = "Etapa: " + s.stage;
  document.getElementById('d-wiki').href = s.wiki_url || '#';

  const descHtml = s.description || '';
  document.getElementById('d-about').innerHTML = descHtml.startsWith('<')
    ? descHtml
    : `<p>${descHtml}</p>`;

  const sessions = s.sessions || [];
  document.getElementById('d-sessions').innerHTML = MODULES.map((name, i) => {
    const n = i + 1;
    const sess = sessions.find(ss => ss.module_number === n) || {};
    let cls, status;
    if (sess.status === 'done') { cls = 's-done'; status = 'Completada ✓'; }
    else if (sess.status === 'scheduled') { cls = 's-sched'; status = '📅 ' + (sess.date || 'Programada'); }
    else { cls = 's-open'; status = 'Necesita mentor'; }
    const hwLink = sess.homework_url
      ? `<a class="hw-link" href="${sess.homework_url}" target="_blank" rel="noopener" title="Tarea del módulo ${n}">Tarea ↗</a>`
      : `<span class="hw-link" style="opacity:.4" title="Contenido próximamente">Tarea ↗</span>`;
    return `
      <div class="session-item ${cls}">
        <span class="session-num">${n}</span>
        <span class="session-name">${name.split(' · ')[1]}</span>
        <span class="session-status">${status}</span>
        ${hwLink}
      </div>`;
  }).join('');

  const matchedMentors = s.matched_mentors || [];
  if (matchedMentors.length > 0) {
    document.getElementById('d-mentors').innerHTML = matchedMentors
      .map(mid => mentorCard(mentors.find(m => m.id === mid), s.name))
      .filter(Boolean).join('');
  } else {
    document.getElementById('d-mentors').innerHTML =
      '<div class="empty-state" style="display:block">Aún no hay mentores asignados a esta startup. ¡Regístrate como mentor!</div>';
  }

  go('detail');
}

/* ── REGISTER ────────────────────────── */
async function submitRegistration() {
  const errEl = document.getElementById('register-error');
  errEl.style.display = 'none';

  const name = document.getElementById('reg-name').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const company = document.getElementById('reg-company').value.trim();
  const role = document.getElementById('reg-role').value.trim();
  const whatsapp = document.getElementById('reg-whatsapp').value.trim();
  const linkedin = document.getElementById('reg-linkedin').value.trim();
  const availability = document.getElementById('reg-availability').value;
  const consent = document.getElementById('reg-consent').checked;

  const modules = [];
  document.querySelectorAll('#module-checks input[type=checkbox]').forEach((cb, i) => {
    if (cb.checked) modules.push(i + 1);
  });

  if (!name || !email || !company) {
    errEl.textContent = 'Por favor completa los campos obligatorios: nombre, email y empresa.';
    errEl.style.display = 'block';
    return;
  }
  if (!email.includes('@')) {
    errEl.textContent = 'Por favor ingresa un email válido.';
    errEl.style.display = 'block';
    return;
  }
  if (modules.length === 0) {
    errEl.textContent = 'Selecciona al menos un módulo en el que puedes mentorar.';
    errEl.style.display = 'block';
    return;
  }
  if (!consent) {
    errEl.textContent = 'Debes aceptar el tratamiento de datos para continuar.';
    errEl.style.display = 'block';
    return;
  }

  const btn = document.getElementById('reg-submit');
  btn.disabled = true;
  btn.textContent = 'Enviando...';

  try {
    const resp = await fetch(`${API}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, company, role, whatsapp, linkedin, modules, availability, consent }),
    });
    const result = await resp.json();
    if (resp.ok || resp.status === 207) {
      document.getElementById('register-card').style.display = 'none';
      document.getElementById('confirm-box').style.display = 'block';
    } else {
      errEl.textContent = result.error === 'missing_fields'
        ? `Campos obligatorios faltantes: ${result.fields.join(', ')}`
        : (result.message || result.error || 'Error al enviar el registro.');
      errEl.style.display = 'block';
    }
  } catch (e) {
    errEl.textContent = 'Error de conexión. Intenta de nuevo.';
    errEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Enviar registro';
  }
}

/* ── INIT ────────────────────────────── */
async function init() {
  // Populate module select and checkboxes
  document.getElementById('module-select').innerHTML =
    '<option value="all">Los 8 módulos</option>' +
    MODULES.map((m, i) => `<option value="${i + 1}">${m}</option>`).join('');
  document.getElementById('module-checks').innerHTML =
    MODULES.map(m => `<label><input type="checkbox"> ${m}</label>`).join('');

  // Load data from API
  await Promise.all([loadStartups(), loadMentors()]);

  // Update stats
  const statNums = document.querySelectorAll('.stat .num');
  if (statNums.length >= 2) {
    statNums[1].textContent = startups.length;
  }

  // Render mentors directory
  document.getElementById('mentors-grid').innerHTML = mentors.length
    ? mentors.map(m => mentorCard(m, null)).join('')
    : '<div class="empty-state" style="display:block">Los mentores corporativos aparecerán aquí una vez aprobados. ¡Regístrate!</div>';

  // Render home featured startups
  document.getElementById('home-startups').innerHTML = startups.length
    ? startups.slice(0, 3).map(cardHTML).join('')
    : '<div class="loading-state">Cargando startups...</div>';

  renderListing();
  go('home');
}

init();
