// MasqueIA Popup Script

let extensionEnabled = true;
let currentLanguage = DEFAULT_UI_LANGUAGE;
let currentSessionId = null;

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  currentLanguage = await getUiLanguage();
  applyPopupLanguage();
  await loadExtensionState();

  document.getElementById('settings-btn')?.addEventListener('click', openSettings);
  document.getElementById('dashboard-btn')?.addEventListener('click', openDashboard);
  document.getElementById('setup-btn')?.addEventListener('click', openSetup);
  document.getElementById('options-btn')?.addEventListener('click', openOptions);
  document.getElementById('extension-toggle')?.addEventListener('click', toggleExtension);
  document.getElementById('language-select')?.addEventListener('change', changeLanguage);

  // Tabs
  document.getElementById('tab-main-btn')?.addEventListener('click', () => showTab('main'));
  document.getElementById('tab-deanon-btn')?.addEventListener('click', () => {
    showTab('deanon');
    loadSessions();
  });

  // Deanon toolbar
  document.getElementById('tb-bold')?.addEventListener('click', () => execCmd('bold'));
  document.getElementById('tb-italic')?.addEventListener('click', () => execCmd('italic'));
  document.getElementById('tb-clear')?.addEventListener('click', clearEditor);
  document.getElementById('tb-paste')?.addEventListener('click', pasteFromClipboard);

  // Deanon actions
  document.getElementById('deanon-btn')?.addEventListener('click', deanonymizeResponse);
  document.getElementById('copy-result-btn')?.addEventListener('click', copyResult);
  document.getElementById('close-result-btn')?.addEventListener('click', () => {
    document.getElementById('deanon-result').classList.add('hidden');
  });
  document.getElementById('workspace-select')?.addEventListener('change', (e) => {
    chrome.storage.local.set({ activeWorkspace: e.target.value });
    updateWorkspaceUI();
  });
  document.getElementById('session-select')?.addEventListener('change', (e) => {
    setSession(e.target.value || null);
    if (e.target.value) chrome.storage.local.set({ lastTs: e.target.value, lastSessionId: e.target.value });
  });

  // Après les boutons, sans await : le moteur peut mettre plusieurs secondes à démarrer
  checkBackendStatus();
  loadWorkspaces();
  loadLastSession();
  setInterval(checkBackendStatus, 5000);
});

// ── Tabs ─────────────────────────────────────────────────────────────────────
function showTab(name) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  document.getElementById('tab-' + name + '-btn').classList.add('active');
}

// ── Language ──────────────────────────────────────────────────────────────────
function applyPopupLanguage() {
  document.documentElement.lang = currentLanguage;
  const sel = document.getElementById('language-select');
  sel.options[0].textContent = extensionText('french', currentLanguage);
  sel.options[1].textContent = extensionText('english', currentLanguage);
  sel.value = currentLanguage;
  document.getElementById('status-text').textContent       = extensionText('checking', currentLanguage);
  document.getElementById('language-label').textContent    = extensionText('language', currentLanguage);
  document.getElementById('popup-subtitle').textContent    = extensionText('popupSubtitle', currentLanguage);
  document.getElementById('toggle-label').textContent      = extensionText('autoAnonymization', currentLanguage);
  document.getElementById('service-status-label').textContent = extensionText('serviceStatus', currentLanguage);
  document.getElementById('offline-warning-title').textContent = extensionText('backendOffline', currentLanguage);
  document.getElementById('offline-warning-help').textContent  = extensionText('startOrInstall', currentLanguage);
  document.getElementById('setup-btn').textContent         = extensionText('installBackend', currentLanguage);
  document.getElementById('settings-btn').textContent      = extensionText('settings', currentLanguage);
  document.getElementById('dashboard-btn').textContent     = extensionText('dashboard', currentLanguage);
  document.getElementById('options-btn').textContent       = extensionText('extensionSettings', currentLanguage);
  document.getElementById('deanon-editor').dataset.placeholder =
    currentLanguage === 'fr' ? 'Collez ici la réponse de l\'IA...' : 'Paste the AI response here...';
}

async function changeLanguage(event) {
  currentLanguage = event.target.value;
  await chrome.storage.local.set({ uiLanguage: currentLanguage });
  applyPopupLanguage();
  checkBackendStatus();
}

// ── Engine status ─────────────────────────────────────────────────────────────
let statusCheckInFlight = false;

async function checkBackendStatus() {
  if (statusCheckInFlight) return;
  statusCheckInFlight = true;
  const badge   = document.getElementById('status-badge');
  const dot     = document.getElementById('status-dot');
  const text    = document.getElementById('status-text');
  const warn    = document.getElementById('offline-warning');
  const setupBtn = document.getElementById('setup-btn');
  try {
    const res = await apiFetch('/health');
    const data = await res.json();
    if (data.status !== 'healthy') throw new Error(data.analyzer_error || 'Moteur non prêt');
    badge.className = 'badge online';
    dot.className   = 'dot online';
    text.textContent = extensionText('online', currentLanguage);
    warn?.classList.add('hidden');
    setupBtn?.classList.add('hidden');
  } catch (error) {
    const help = document.getElementById('offline-warning-help');
    if (help) help.textContent = error.message;
    badge.className = 'badge offline';
    dot.className   = 'dot offline';
    text.textContent = extensionText('offline', currentLanguage);
    warn?.classList.remove('hidden');
    setupBtn?.classList.remove('hidden');
  } finally {
    statusCheckInFlight = false;
  }
}

// ── Extension toggle ──────────────────────────────────────────────────────────
async function loadExtensionState() {
  const r = await chrome.storage.local.get(['extensionEnabled']);
  extensionEnabled = r.extensionEnabled !== false;
  updateToggleUI();
}

async function toggleExtension() {
  extensionEnabled = !extensionEnabled;
  await chrome.storage.local.set({ extensionEnabled });
  updateToggleUI();
  chrome.runtime.sendMessage({ action: 'setExtensionState', enabled: extensionEnabled });
}

function updateToggleUI() {
  const t = document.getElementById('extension-toggle');
  if (!t) return;
  t.classList.toggle('active', extensionEnabled);
  t.setAttribute('aria-pressed', String(extensionEnabled));
}

// ── Workspace ─────────────────────────────────────────────────────────────────
// Espace actif : le service worker l'utilise pour chaque collage anonymisé
async function loadWorkspaces() {
  const select = document.getElementById('workspace-select');
  const { activeWorkspace = '' } = await chrome.storage.local.get('activeWorkspace');
  try {
    const res = await apiFetch('/workspaces');
    if (res.ok) {
      const { workspaces } = await res.json();
      select.length = 1;
      for (const w of workspaces) addSessionOption(select, w.id, `${w.name} (${w.count} valeur(s))`);
    }
  } catch (_) { /* moteur arrêté : liste vide */ }
  const known = [...select.options].some(o => o.value === activeWorkspace);
  select.value = known ? activeWorkspace : '';
  updateWorkspaceUI();
}

function updateWorkspaceUI() {
  const select = document.getElementById('workspace-select');
  select.closest('.workspace-card').classList.toggle('active', !!select.value);
}

// ── Navigation ────────────────────────────────────────────────────────────────
function openAppSection(section) {
  chrome.tabs.create({ url: chrome.runtime.getURL(`app.html?lang=${currentLanguage}&section=${section}`) });
}
function openSettings()  { openAppSection('settings'); }
function openDashboard() { openAppSection('dashboard'); }
function openSetup()     { openAppSection('setup'); }
function openOptions()   { chrome.runtime.openOptionsPage(); }

// ── Session ───────────────────────────────────────────────────────────────────
async function loadLastSession() {
  const r = await chrome.storage.local.get(['lastSessionId', 'lastTs']);
  await loadSessions();
  const select = document.getElementById('session-select');
  const stored = r.lastTs || r.lastSessionId || null;
  // Stored session, else the most recent one in the list
  setSession(stored || select?.options[1]?.value || null);
}

// "26_10_30_06_59_30" → "30/10/26 06:59:30"
function formatTs(ts) {
  const p = ts.split('_');
  return p.length === 6 ? `${p[2]}/${p[1]}/${p[0]} ${p[3]}:${p[4]}:${p[5]}` : ts;
}

function addSessionOption(select, ts, label) {
  const opt = document.createElement('option');
  opt.value = ts;
  opt.textContent = label;
  select.appendChild(opt);
  return opt;
}

async function loadSessions() {
  const select = document.getElementById('session-select');
  if (!select) return;
  try {
    const res = await apiFetch('/sessions?limit=20');
    if (!res.ok) return;
    const { sessions } = await res.json();
    select.length = 1;
    for (const s of sessions) {
      const types = s.types.slice(0, 3).join(', ') + (s.types.length > 3 ? ', …' : '');
      addSessionOption(select, s.ts, `${formatTs(s.ts)} – ${s.count} entité(s) (${types})`);
    }
    if (currentSessionId) setSession(currentSessionId);
  } catch (_) { /* backend offline: keep current list */ }
}

function setSession(id) {
  currentSessionId = id;
  const badge = document.getElementById('session-badge');
  const select = document.getElementById('session-select');
  if (badge) {
    if (id) {
      badge.textContent = '✓ Session active';
      badge.className = 'session-badge active';
    } else {
      badge.textContent = 'Aucune session';
      badge.className = 'session-badge missing';
    }
  }
  if (select) {
    if (id && ![...select.options].some(o => o.value === id)) {
      addSessionOption(select, id, formatTs(id));
    }
    select.value = id || '';
  }
}

// ── Deanonymization ───────────────────────────────────────────────────────────

/**
 * Extract the timestamp from the first token found in text.
 * Token format: [TYPE_COUNTER_YY_MM_DD_HH_MM_SS]
 * e.g. [PERSONNE_1_26_10_30_06_19_59] → "26_10_30_06_19_59"
 */
function extractTsFromText(text) {
  const m = text.match(/\[[A-Z_]+_\d+_(\d{2}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})\]/);
  return m ? m[1] : null;
}

async function deanonymizeResponse() {
  const editor = document.getElementById('deanon-editor');
  const text = (editor.innerText || editor.textContent || '').trim();
  const errorEl = document.getElementById('deanon-error');

  if (errorEl) errorEl.classList.add('hidden');

  if (!text) {
    showError('Collez d\'abord la réponse de l\'IA.');
    return;
  }

  // Auto-detect session timestamp from tokens if not already set
  const detectedTs = extractTsFromText(text);
  if (detectedTs && detectedTs !== currentSessionId) {
    setSession(detectedTs);
  }

  if (!currentSessionId) {
    showError('Aucune session. Anonymisez un texte via l\'extension ou choisissez une session dans la liste.');
    return;
  }

  const btn   = document.getElementById('deanon-btn');
  const label = document.getElementById('deanon-btn-label');
  btn.disabled = true;
  label.textContent = '…';

  try {
    // Appel direct au backend (plus fiable que le message passing)
    const res = await apiFetch('/deanonymize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: currentSessionId, text })
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.error || `Erreur ${res.status}`);
      return;
    }

    document.getElementById('deanon-text').textContent = data.deanonymized_text;
    document.getElementById('deanon-count').textContent =
      `${data.replacements} token(s) restauré(s)`;
    document.getElementById('deanon-result').classList.remove('hidden');

  } catch (err) {
    showError('Backend inaccessible : ' + err.message);
  } finally {
    btn.disabled = false;
    label.textContent = 'Désanonymiser';
  }
}

function showError(msg) {
  let el = document.getElementById('deanon-error');
  if (!el) {
    el = document.createElement('div');
    el.id = 'deanon-error';
    el.style.cssText = 'padding:8px 12px;background:#fef2f2;border:1px solid #fecaca;border-radius:6px;font-size:12px;color:#b91c1c;';
    document.getElementById('deanon-btn').insertAdjacentElement('afterend', el);
  }
  el.textContent = msg;
  el.classList.remove('hidden');
}

async function copyResult() {
  const txt = document.getElementById('deanon-text').textContent;
  await navigator.clipboard.writeText(txt);
  // Signal content-script to let the next paste through unmodified
  chrome.storage.local.set({ skipNextPaste: true });
  const btn = document.getElementById('copy-result-btn');
  if (btn) {
    const orig = btn.textContent;
    btn.textContent = '✓ Copié';
    setTimeout(() => { btn.textContent = orig; }, 1500);
  }
}

// ── Rich-text toolbar helpers ─────────────────────────────────────────────────
function execCmd(cmd) {
  document.getElementById('deanon-editor').focus();
  document.execCommand(cmd, false, null);
}

function clearEditor() {
  document.getElementById('deanon-editor').innerHTML = '';
  document.getElementById('deanon-result').classList.add('hidden');
}

async function pasteFromClipboard() {
  try {
    const txt = await navigator.clipboard.readText();
    const editor = document.getElementById('deanon-editor');
    editor.focus();
    document.execCommand('insertText', false, txt);
  } catch (_) {
    document.getElementById('deanon-editor').focus();
  }
}
