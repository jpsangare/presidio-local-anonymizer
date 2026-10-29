// MasqueIA Popup Script

let currentBackendUrl = '';
let extensionEnabled = true;
let currentLanguage = DEFAULT_UI_LANGUAGE;
let currentSessionId = null;

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  currentLanguage = await getUiLanguage();
  applyPopupLanguage();
  await loadBackendUrl();
  await loadExtensionState();
  await checkBackendStatus();
  await loadLastSession();

  document.getElementById('settings-btn')?.addEventListener('click', openSettings);
  document.getElementById('dashboard-btn')?.addEventListener('click', openDashboard);
  document.getElementById('setup-btn')?.addEventListener('click', openSetup);
  document.getElementById('options-btn')?.addEventListener('click', openOptions);
  document.getElementById('extension-toggle')?.addEventListener('click', toggleExtension);
  document.getElementById('language-select')?.addEventListener('change', changeLanguage);

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
  updateButtonLinks();
  checkBackendStatus();
}

// ── Backend URL ───────────────────────────────────────────────────────────────
async function loadBackendUrl() {
  try {
    const r = await chrome.runtime.sendMessage({ action: 'getBackendUrl' });
    currentBackendUrl = r.success ? r.url : 'http://localhost:6677';
  } catch (_) {
    currentBackendUrl = 'http://localhost:6677';
  }
  updateButtonLinks();
}

function updateButtonLinks() {
  const l = currentLanguage;
  document.getElementById('settings-btn').href  = `${currentBackendUrl}/?lang=${l}`;
  document.getElementById('dashboard-btn').href = `${currentBackendUrl}/dashboard?lang=${l}`;
  const sb = document.getElementById('setup-btn');
  if (sb) sb.href = `${currentBackendUrl}/setup?lang=${l}`;
}

// ── Backend status ────────────────────────────────────────────────────────────
async function checkBackendStatus() {
  const badge   = document.getElementById('status-badge');
  const dot     = document.getElementById('status-dot');
  const text    = document.getElementById('status-text');
  const warn    = document.getElementById('offline-warning');
  const setupBtn = document.getElementById('setup-btn');
  try {
    const r = await chrome.runtime.sendMessage({ action: 'testConnection', url: currentBackendUrl });
    if (!r.success) throw new Error(r.message);
    badge.className = 'badge online';
    dot.className   = 'dot online';
    text.textContent = extensionText('online', currentLanguage);
    warn?.classList.add('hidden');
    setupBtn?.classList.add('hidden');
  } catch (_) {
    badge.className = 'badge offline';
    dot.className   = 'dot offline';
    text.textContent = extensionText('offline', currentLanguage);
    warn?.classList.remove('hidden');
    setupBtn?.classList.remove('hidden');
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

// ── Navigation ────────────────────────────────────────────────────────────────
function openSettings(e)  { e.preventDefault(); chrome.tabs.create({ url: `${currentBackendUrl}/?lang=${currentLanguage}` }); }
function openDashboard(e) { e.preventDefault(); chrome.tabs.create({ url: `${currentBackendUrl}/dashboard?lang=${currentLanguage}` }); }
function openSetup(e)     { e.preventDefault(); chrome.tabs.create({ url: `${currentBackendUrl}/setup?lang=${currentLanguage}` }); }
function openOptions(e)   { if (e) e.preventDefault(); chrome.runtime.openOptionsPage(); }

// ── Session ───────────────────────────────────────────────────────────────────
async function loadLastSession() {
  const r = await chrome.storage.local.get(['lastSessionId']);
  setSession(r.lastSessionId || null);
}

function setSession(id) {
  currentSessionId = id;
  const badge = document.getElementById('session-badge');
  if (!badge) return;
  if (id) {
    badge.textContent = '✓ Session active';
    badge.className = 'session-badge active';
  } else {
    badge.textContent = 'Aucune session';
    badge.className = 'session-badge missing';
  }
}

// ── Deanonymization ───────────────────────────────────────────────────────────
async function deanonymizeResponse() {
  const editor = document.getElementById('deanon-editor');
  const text = editor.innerText.trim();
  if (!text) return;

  if (!currentSessionId) {
    alert(extensionText('noSession', currentLanguage));
    showTab('main');
    return;
  }

  const btn   = document.getElementById('deanon-btn');
  const label = document.getElementById('deanon-btn-label');
  btn.disabled = true;
  label.textContent = extensionText('deanonymizing', currentLanguage);

  try {
    const r = await chrome.runtime.sendMessage({
      action: 'deanonymize',
      sessionId: currentSessionId,
      text
    });

    if (r.success) {
      const resultEl = document.getElementById('deanon-result');
      document.getElementById('deanon-text').textContent = r.data.deanonymized_text;
      document.getElementById('deanon-count').textContent =
        `${r.data.replacements} token(s) restauré(s)`;
      resultEl.classList.remove('hidden');
    } else {
      alert(r.error || 'Erreur de désanonymisation');
    }
  } catch (err) {
    alert('Erreur : ' + err.message);
  } finally {
    btn.disabled = false;
    label.textContent = 'Désanonymiser';
  }
}

async function copyResult() {
  const txt = document.getElementById('deanon-text').textContent;
  await navigator.clipboard.writeText(txt);
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
