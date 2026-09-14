/* ── Config ───────────────────────────────────────────────── */
const API = "/api";           // relative — served from same origin
const POLL_INTERVAL = 8000;   // ms between job-status polls
const LB_INTERVAL  = 180000;  // 3 min leaderboard refresh
const DEADLINE_KEY = "cth_deadline";
const TOKEN_KEY    = "cth_token";

/* ── Auth ─────────────────────────────────────────────────── */
function getToken() {
  const p = new URLSearchParams(location.search).get("token");
  if (p) { localStorage.setItem(TOKEN_KEY, p); history.replaceState({}, "", location.pathname); }
  return localStorage.getItem(TOKEN_KEY) || "";
}
const TOKEN = getToken();

async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, {
    ...opts,
    headers: { "Authorization": `Bearer ${TOKEN}`, ...(opts.headers || {}) },
  });
  if (!res.ok) throw Object.assign(new Error(res.statusText), { status: res.status });
  return res.json();
}

/* ── Tab nav ──────────────────────────────────────────────── */
document.querySelectorAll(".navlink, [data-tab]").forEach(el => {
  el.addEventListener("click", () => switchTab(el.dataset.tab));
});

function switchTab(tab) {
  if (!tab) return;
  document.querySelectorAll(".navlink").forEach(b =>
    b.classList.toggle("active", b.dataset.tab === tab));
  document.querySelectorAll(".panel-x").forEach(p =>
    p.classList.toggle("active", p.id === `p-${tab}`));
  if (tab === "leaderboard") loadLeaderboard();
  if (tab === "api")         loadTokenUsage();
  if (tab === "compute")     loadGpu();
}

/* ── Canvas particle network ──────────────────────────────── */
(function initNet() {
  const canvas = document.getElementById("net");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let W, H, pts = [];

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }
  window.addEventListener("resize", resize);
  resize();

  for (let i = 0; i < 60; i++) pts.push({
    x: Math.random() * (W || 1200), y: Math.random() * (H || 400),
    vx: (Math.random() - .5) * .4, vy: (Math.random() - .5) * .4,
  });

  function draw() {
    ctx.clearRect(0, 0, W, H);
    pts.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
    });
    for (let i = 0; i < pts.length; i++) {
      for (let j = i + 1; j < pts.length; j++) {
        const dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y;
        const d  = Math.sqrt(dx * dx + dy * dy);
        if (d < 140) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(178,238,250,${(1 - d/140) * .5})`;
          ctx.lineWidth = .8;
          ctx.moveTo(pts[i].x, pts[i].y);
          ctx.lineTo(pts[j].x, pts[j].y);
          ctx.stroke();
        }
      }
      ctx.beginPath();
      ctx.arc(pts[i].x, pts[i].y, 2, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(178,238,250,.7)";
      ctx.fill();
    }
    requestAnimationFrame(draw);
  }
  draw();
})();

/* ── Countdown clock ──────────────────────────────────────── */
(function initClock() {
  let deadline = parseInt(localStorage.getItem(DEADLINE_KEY), 10);
  if (!deadline || isNaN(deadline)) {
    deadline = Date.now() + 48 * 3600 * 1000;
    localStorage.setItem(DEADLINE_KEY, deadline);
  }

  const heroClock = document.getElementById("heroClock");
  const sbClock   = document.getElementById("sbClock");
  const timeBar   = document.getElementById("timeBar");
  const totalMs   = 48 * 3600 * 1000;

  function tick() {
    const rem = Math.max(0, deadline - Date.now());
    const h = Math.floor(rem / 3600000);
    const m = Math.floor((rem % 3600000) / 60000);
    const s = Math.floor((rem % 60000) / 1000);
    const str = `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
    if (heroClock) heroClock.textContent = str;
    if (sbClock)   sbClock.textContent   = str;
    const pct = Math.max(0, (rem / totalMs) * 100);
    if (timeBar) timeBar.style.width = pct + "%";
  }
  setInterval(tick, 1000);
  tick();
})();

/* ── Team info (live data) ────────────────────────────────── */
async function loadTeam() {
  if (!TOKEN) return;
  try {
    const d = await apiFetch("/team");
    const h2 = document.querySelector("#p-welcome .card-head h2");
    if (h2) h2.textContent = `Bienvenidos, ${d.name}`;

    const rankEl = document.getElementById("teamRank");
    if (rankEl) rankEl.textContent = d.rank;

    const chip = document.getElementById("yourRankChip");
    if (chip) chip.textContent = `You · #${d.rank}`;

    const pill = document.getElementById("subsPill");
    if (pill) pill.textContent = `${d.subs_today} / ${d.subs_limit} today`;

    patchCred("JupyterHub URL", d.jupyter_url);
    patchCred("OpenRouter Key", d.or_key);
    patchCred("Dataset · HuggingFace", d.hf_dataset);

    // Update team badge
    const badge = document.querySelector(".team-badge");
    if (badge && d.name) {
      badge.innerHTML = `<span class="dot"></span>${d.name} · #<span id="teamRank">${d.rank}</span>`;
    }

    // Update notebook link
    if (d.jupyter_url) {
      document.querySelectorAll(`a[href*="runpod.net"]`).forEach(a => a.href = d.jupyter_url);
    }
  } catch (e) {
    if (e.status === 401 || e.status === 403) showAuthError();
  }
}

function patchCred(label, value) {
  if (!value) return;
  document.querySelectorAll(".cred-l").forEach(el => {
    if (el.textContent.trim() === label) {
      const vEl = el.nextElementSibling?.querySelector("span");
      const btn = el.nextElementSibling?.querySelector(".copy");
      if (vEl) vEl.textContent = value;
      if (btn) btn.dataset.copy = value;
    }
  });
}

function showAuthError() {
  document.body.innerHTML = `
    <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
         font-family:system-ui;background:#F8FAFC;padding:32px;text-align:center">
      <div>
        <div style="font-size:28px;font-weight:800;color:#0C498A;margin-bottom:12px">
          CleantechHUB Datathon
        </div>
        <p style="color:#64748B;margin-bottom:24px">
          Access your portal with the unique link sent to your team email.
        </p>
        <code style="background:#E2E8F0;padding:8px 14px;border-radius:6px;font-size:13px">
          datathon.data.cleantechhub.net?token=YOUR_TOKEN
        </code>
      </div>
    </div>`;
}

/* ── Copy buttons ─────────────────────────────────────────── */
document.addEventListener("click", e => {
  const btn = e.target.closest(".copy");
  if (!btn) return;
  navigator.clipboard.writeText(btn.dataset.copy || "").then(() => {
    btn.classList.add("ok");
    showToast("Copied!");
    setTimeout(() => btn.classList.remove("ok"), 1500);
  });
});

/* ── Toast ────────────────────────────────────────────────── */
let toastTimer;
function showToast(msg, dur = 2200) {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), dur);
}

/* ── File drag & drop ─────────────────────────────────────── */
const dropZone  = document.getElementById("drop");
const fileInput = document.getElementById("fileInput");
const fileArea  = document.getElementById("fileArea");
const submitBtn = document.getElementById("submitBtn");
let selectedFile = null;

if (dropZone) {
  dropZone.addEventListener("click", () => fileInput.click());
  dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("over"); });
  dropZone.addEventListener("dragleave", ()=> dropZone.classList.remove("over"));
  dropZone.addEventListener("drop", e => {
    e.preventDefault(); dropZone.classList.remove("over");
    handleFile(e.dataTransfer.files[0]);
  });
}
fileInput?.addEventListener("change", () => handleFile(fileInput.files[0]));

function handleFile(f) {
  if (!f) return;
  if (!f.name.endsWith(".csv")) { showToast("Please select a .csv file"); return; }
  if (f.size > 50 * 1024 * 1024) { showToast("File exceeds 50 MB limit"); return; }
  selectedFile = f;
  const kb = (f.size / 1024).toFixed(1);
  fileArea.innerHTML = `
    <div style="display:flex;align-items:center;gap:10px;padding:10px 14px;
         background:rgba(59,109,17,.06);border:1px solid rgba(59,109,17,.3);
         border-radius:8px;margin-top:10px">
      <svg width="16" height="16" style="color:var(--forest)"><use href="#i-check"></use></svg>
      <span style="font-size:13px;font-weight:600;color:var(--forest)">${f.name}</span>
      <span style="font-size:12px;color:var(--muted);margin-left:auto">${kb} KB</span>
    </div>`;
  if (submitBtn) submitBtn.disabled = false;
}

/* ── Submission flow ──────────────────────────────────────── */
submitBtn?.addEventListener("click", async () => {
  if (!selectedFile) return;
  submitBtn.disabled = true;
  const prog = document.getElementById("subProg");
  const pbar = document.getElementById("pbar");
  const res  = document.getElementById("subRes");
  prog.style.display = "block";
  res.style.display  = "none";
  pbar.style.width   = "5%";

  if (!TOKEN) {
    showToast("No auth token — open portal via your unique link");
    prog.style.display = "none";
    submitBtn.disabled = false;
    return;
  }

  const fd = new FormData();
  fd.append("file", selectedFile);

  try {
    const { job_id } = await apiFetch("/submit", { method: "POST", body: fd });
    showToast("Uploaded — scoring started");
    pollJob(job_id, pbar, prog, res);
  } catch (e) {
    prog.style.display = "none";
    submitBtn.disabled = false;
    showToast(e.status === 429 ? "Daily submission limit reached" : "Upload failed — try again");
  }
});

function pollJob(jobId, pbar, prog, res) {
  let progress = 10;
  const iv = setInterval(async () => {
    try {
      const d = await apiFetch(`/jobs/${jobId}`);
      progress = Math.min(progress + 15, d.status === "done" ? 100 : 85);
      pbar.style.width = progress + "%";
      const meta = document.getElementById("progMeta");
      if (meta) meta.textContent =
        d.status === "scoring" ? "Running on Modal T4…" : "Queued for scoring…";

      if (d.status === "done" || d.status === "error") {
        clearInterval(iv);
        prog.style.display = "none";
        pbar.style.width = "0";
        renderResult(res, d);
        loadSubmissions();
      }
    } catch { clearInterval(iv); }
  }, POLL_INTERVAL);
}

function renderResult(el, d) {
  el.style.display = "block";
  if (d.status === "done") {
    el.innerHTML = `
      <div style="padding:16px;background:rgba(59,109,17,.07);border:1px solid rgba(59,109,17,.35);
           border-radius:var(--r-sm)">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
          <svg width="16" height="16" style="color:var(--forest)"><use href="#i-check"></use></svg>
          <strong style="color:var(--forest)">Scored! R² = ${d.score?.toFixed(5)}</strong>
        </div>
        <p style="font-size:12px;color:var(--muted)">Result posted to leaderboard.</p>
      </div>`;
    showToast(`Score: R² = ${d.score?.toFixed(5)}`);
  } else {
    el.innerHTML = `
      <div style="padding:16px;background:rgba(220,38,38,.07);border:1px solid rgba(220,38,38,.3);
           border-radius:var(--r-sm)">
        <div style="display:flex;align-items:center;gap:8px">
          <svg width="16" height="16" style="color:#DC2626"><use href="#i-x"></use></svg>
          <strong style="color:#DC2626">Scoring error</strong>
        </div>
        <p style="font-size:12px;color:var(--muted);margin-top:5px">${d.error_msg || "Unknown error"}</p>
      </div>`;
  }
}

/* ── Submission history ───────────────────────────────────── */
async function loadSubmissions() {
  if (!TOKEN) return;
  try {
    const { submissions } = await apiFetch("/submissions");
    const tb = document.getElementById("histBody");
    if (!tb) return;
    tb.innerHTML = submissions.map((s, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>${new Date(s.created_at).toLocaleTimeString()}</td>
        <td>${s.score != null ? s.score.toFixed(5) : "—"}</td>
        <td><span class="pill pill-${s.status === 'done' ? 'green' : s.status === 'error' ? 'gold' : 'blue'}">${s.status}</span></td>
      </tr>`).join("") ||
      `<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:20px">No submissions yet</td></tr>`;
  } catch { /* silent — no token in dev/preview mode */ }
}

/* ── Leaderboard ──────────────────────────────────────────── */
async function loadLeaderboard() {
  if (!TOKEN) return;
  try {
    const { leaderboard, your_best } = await apiFetch("/leaderboard");
    renderLb(leaderboard, your_best);
  } catch { /* silent */ }
}

function renderLb(rows, yourBest) {
  const tb   = document.getElementById("lb");
  const chip = document.getElementById("yourRankChip");
  if (!tb) return;
  const myRank = rows.findIndex(r => r.score === yourBest) + 1;
  if (chip && myRank > 0) chip.textContent = `You · #${myRank}`;
  tb.innerHTML = rows.map(r => `
    <tr class="${r.score === yourBest ? 'me' : ''}">
      <td>${r.rank}</td>
      <td>${r.name}</td>
      <td>${r.score.toFixed(5)}</td>
      <td>${r.subs ?? "—"}</td>
    </tr>`).join("") ||
    `<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:20px">No scored submissions yet</td></tr>`;
}

document.getElementById("lbSearch")?.addEventListener("input", function () {
  const q = this.value.toLowerCase();
  document.querySelectorAll("#lb tr").forEach(row => {
    row.style.display = row.textContent.toLowerCase().includes(q) ? "" : "none";
  });
});

setInterval(loadLeaderboard, LB_INTERVAL);

/* ── Token usage ──────────────────────────────────────────── */
async function loadTokenUsage() {
  if (!TOKEN) return;
  try {
    const d = await apiFetch("/token-usage");
    const liquid = document.getElementById("budgetLiquid");
    const val    = document.getElementById("budgetVal");
    const sub    = document.getElementById("budgetSub");
    const pct    = (d.remaining / d.limit) * 100;
    if (liquid) liquid.style.height = pct + "%";
    if (val)    val.textContent = `$${d.remaining.toFixed(2)}`;
    if (sub)    sub.textContent = `of $${d.limit.toFixed(2)} · ${Math.round(pct)}% left`;
  } catch { /* silent */ }
}

/* ── GPU stats ────────────────────────────────────────────── */
async function loadGpu() {
  if (!TOKEN) return;
  try {
    const d = await apiFetch("/gpu");
    const gpuBar  = document.getElementById("gpuBar");
    const vramBar = document.getElementById("vramBar");
    const gpuLbl  = document.getElementById("gpuUtilLbl");
    const vramLbl = document.getElementById("vramLbl");
    if (gpuBar)  gpuBar.style.width  = d.gpu_util + "%";
    if (vramBar) vramBar.style.width = (d.vram_used_gb / d.vram_total_gb * 100) + "%";
    if (gpuLbl)  gpuLbl.textContent  = d.gpu_util + "%";
    if (vramLbl) vramLbl.textContent = `${d.vram_used_gb} / ${d.vram_total_gb} GB`;
  } catch { /* silent */ }
}

/* ── Live API test ────────────────────────────────────────── */
document.getElementById("testApi")?.addEventListener("click", async function () {
  this.disabled = true;
  this.textContent = "Testing…";
  try {
    const d = await apiFetch("/test-llm");
    showToast(`✓ API OK · cost ~$${d.cost?.toFixed(4) || "0.0002"}`);
  } catch {
    showToast("API call failed — check your key");
  } finally {
    this.disabled = false;
    this.innerHTML = `<svg width="15" height="15"><use href="#i-bolt"></use></svg>Test API call`;
  }
});

/* ── Reset demo state ─────────────────────────────────────── */
document.getElementById("resetState")?.addEventListener("click", () => {
  localStorage.removeItem(DEADLINE_KEY);
  localStorage.removeItem(TOKEN_KEY);
  location.reload();
});

/* ── Init ─────────────────────────────────────────────────── */
loadTeam();
loadSubmissions();
loadTokenUsage();
loadGpu();
