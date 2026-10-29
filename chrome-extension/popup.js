// Popup script for Presidio Browser Anonymizer

let currentBackendUrl = '';
let extensionEnabled = true;
let currentLanguage = DEFAULT_UI_LANGUAGE;
let currentSessionId = null;

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
  currentLanguage = await getUiLanguage();
  applyPopupLanguage();
  await loadBackendUrl();
  await loadExtensionState();
  await checkBackendStatus();
  await loadLastSession();

  // Add event listeners for buttons
  document.getElementById('settings-btn')?.addEventListener('click', openSettings);
  document.getElementById('dashboard-btn')?.addEventListener('click', openDashboard);
  document.getElementById('setup-btn')?.addEventListener('click', openSetup);
  document.getElementById('options-btn')?.addEventListener('click', openOptions);
  document.getElementById('extension-toggle')?.addEventListener('click', toggleExtension);
  document.getElementById('language-select')?.addEventListener('change', changeLanguage);
  document.getElementById('deanon-btn')?.addEventListener('click', deanonymizeResponse);
  document.getElementById('deanon-clear')?.addEventListener('click', clearDeanon);

  // Auto-refresh status every 5 seconds
  setInterval(checkBackendStatus, 5000);
});

async function loadLastSession() {
  const result = await chrome.storage.local.get(['lastSessionId']);
  if (result.lastSessionId) {
    currentSessionId = result.lastSessionId;
    document.getElementById('deanon-panel')?.classList.remove('hidden');
  }
}

async function deanonymizeResponse() {
  const text = document.getElementById('deanon-input').value.trim();
  if (!text) return;
  if (!currentSessionId) {
    alert(extensionText('noSession', currentLanguage));
    return;
  }
  const btn = document.getElementById('deanon-btn');
  const label = document.getElementById('deanon-btn-label');
  label.textContent = extensionText('deanonymizing', currentLanguage);
  btn.disabled = true;
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'deanonymize',
      sessionId: currentSessionId,
      text
    });
    if (response.success) {
      document.getElementById('deanon-text').textContent = response.data.deanonymized_text;
      document.getElementById('deanon-count').textContent =
        `${response.data.replacements} token(s) restauré(s)`;
      document.getElementById('deanon-result').classList.remove('hidden');
    } else {
      alert(response.error || 'Erreur de désanonymisation');
    }
  } finally {
    label.textContent = extensionText('textDeanonymized', currentLanguage).replace('🔓 ', '') || 'Désanonymiser';
    btn.disabled = false;
  }
}

function clearDeanon() {
  document.getElementById('deanon-input').value = '';
  document.getElementById('deanon-result').classList.add('hidden');
}

function applyPopupLanguage() {
  document.documentElement.lang = currentLanguage;
  const languageSelect = document.getElementById('language-select');
  languageSelect.options[0].textContent = extensionText('french', currentLanguage);
  languageSelect.options[1].textContent = extensionText('english', currentLanguage);
  languageSelect.value = currentLanguage;
  document.getElementById('status-text').textContent = extensionText('checking', currentLanguage);
  document.getElementById('language-label').textContent = extensionText('language', currentLanguage);
  document.getElementById('popup-subtitle').textContent = extensionText('popupSubtitle', currentLanguage);
  document.getElementById('toggle-label').textContent = extensionText('autoAnonymization', currentLanguage);
  document.getElementById('service-status-label').textContent = extensionText('serviceStatus', currentLanguage);
  document.getElementById('offline-warning-title').textContent = extensionText('backendOffline', currentLanguage);
  document.getElementById('offline-warning-help').textContent = extensionText('startOrInstall', currentLanguage);
  document.getElementById('setup-btn').textContent = extensionText('installBackend', currentLanguage);
  document.getElementById('settings-btn').textContent = extensionText('settings', currentLanguage);
  document.getElementById('dashboard-btn').textContent = extensionText('dashboard', currentLanguage);
  document.getElementById('options-btn').textContent = extensionText('extensionSettings', currentLanguage);
}

async function changeLanguage(event) {
  currentLanguage = event.target.value;
  await chrome.storage.local.set({ uiLanguage: currentLanguage });
  applyPopupLanguage();
  updateButtonLinks();
  checkBackendStatus();
}

// Load backend URL from storage
async function loadBackendUrl() {
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getBackendUrl' });
    if (response.success) {
      currentBackendUrl = response.url;
      // Update button links
      updateButtonLinks();
    }
  } catch (error) {
    console.error('Failed to load backend URL:', error);
    currentBackendUrl = 'http://localhost:6677';
    updateButtonLinks();
  }
}

// Update button links with current backend URL
function updateButtonLinks() {
  const settingsBtn = document.getElementById('settings-btn');
  const dashboardBtn = document.getElementById('dashboard-btn');

  if (settingsBtn) {
    settingsBtn.href = `${currentBackendUrl}/?lang=${currentLanguage}`;
  }
  if (dashboardBtn) {
    dashboardBtn.href = `${currentBackendUrl}/dashboard?lang=${currentLanguage}`;
  }
  const setupBtn = document.getElementById('setup-btn');
  if (setupBtn) setupBtn.href = `${currentBackendUrl}/setup?lang=${currentLanguage}`;
}

// Check backend status
async function checkBackendStatus() {
  const statusBadge = document.getElementById('status-badge');
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');
  const offlineWarning = document.getElementById('offline-warning');
  const setupBtn = document.getElementById('setup-btn');
  const settingsBtn = document.getElementById('settings-btn');
  const dashboardBtn = document.getElementById('dashboard-btn');

  try {
    const response = await chrome.runtime.sendMessage({
      action: 'testConnection',
      url: currentBackendUrl
    });

    if (response.success) {
      // Backend is online
      statusBadge.className = 'status-badge online';
      statusDot.className = 'status-dot online';
      statusText.textContent = extensionText('online', currentLanguage);

      // Hide offline warning and setup button
      offlineWarning?.classList.add('hidden');
      setupBtn?.classList.add('hidden');

      // Show normal buttons
      settingsBtn?.classList.remove('hidden');
      dashboardBtn?.classList.remove('hidden');
    } else {
      throw new Error(response.message);
    }
  } catch (error) {
    // Backend is offline
    statusBadge.className = 'status-badge offline';
    statusDot.className = 'status-dot offline';
    statusText.textContent = extensionText('offline', currentLanguage);

    // Show offline warning and setup button
    offlineWarning?.classList.remove('hidden');
    setupBtn?.classList.remove('hidden');

    // Keep normal buttons visible
    // (user might want to manually start backend)

    console.error('Backend check failed:', error);
  }
}

// Load extension state from storage
async function loadExtensionState() {
  try {
    const result = await chrome.storage.local.get(['extensionEnabled']);
    extensionEnabled = result.extensionEnabled !== false; // Default to true
    updateToggleUI();
  } catch (error) {
    console.error('Failed to load extension state:', error);
    extensionEnabled = true;
    updateToggleUI();
  }
}

// Toggle extension on/off
async function toggleExtension() {
  extensionEnabled = !extensionEnabled;

  // Save to storage
  try {
    await chrome.storage.local.set({ extensionEnabled });
    updateToggleUI();

    // Notify background script
    chrome.runtime.sendMessage({
      action: 'setExtensionState',
      enabled: extensionEnabled
    });
  } catch (error) {
    console.error('Failed to save extension state:', error);
  }
}

// Update toggle button UI
function updateToggleUI() {
  const toggle = document.getElementById('extension-toggle');
  if (toggle) {
    if (extensionEnabled) {
      toggle.classList.add('active');
    } else {
      toggle.classList.remove('active');
    }
    toggle.setAttribute('aria-pressed', String(extensionEnabled));
  }
}

// Open settings in new tab
function openSettings(e) {
  e.preventDefault();
  chrome.tabs.create({ url: `${currentBackendUrl}/?lang=${currentLanguage}` });
}

// Open dashboard in new tab
function openDashboard(e) {
  e.preventDefault();
  chrome.tabs.create({ url: `${currentBackendUrl}/dashboard?lang=${currentLanguage}` });
}

// Open setup wizard in new tab
function openSetup(e) {
  e.preventDefault();
  chrome.tabs.create({ url: `${currentBackendUrl}/setup?lang=${currentLanguage}` });
}

// Open extension options
function openOptions(e) {
  if (e) e.preventDefault();
  chrome.runtime.openOptionsPage();
}
