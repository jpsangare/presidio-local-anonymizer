// Background service worker for Presidio Browser Anonymizer
// Import config functions
importScripts('locales.js');
importScripts('config.js');

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'anonymize') {
    anonymizeText(request.text)
      .then(result => sendResponse({ success: true, data: result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep the message channel open for async response
  }

  if (request.action === 'getBackendUrl') {
    getBackendUrl()
      .then(url => sendResponse({ success: true, url }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }

  if (request.action === 'testConnection') {
    testBackendConnection(request.url)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, message: error.message }));
    return true;
  }

  if (request.action === 'deanonymize') {
    deanonymizeText(request.sessionId, request.text)
      .then(result => sendResponse({ success: true, data: result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});

// Anonymize text using the API
async function anonymizeText(text) {
  try {
    const backendUrl = await getBackendUrl();
    console.log('[Presidio Background] Sending request to:', `${backendUrl}/api/anonymize`);
    console.log('[Presidio Background] Text length:', text.length);

    const response = await fetch(`${backendUrl}/api/anonymize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    console.log('[Presidio Background] Response status:', response.status);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Anonymization failed`);
    }

    const data = await response.json();
    console.log('[Presidio Background] Anonymization successful, entities:', data.stats?.total_entities);
    if (data.session_id) {
      chrome.storage.local.set({ lastSessionId: data.session_id });
    }
    return data;
  } catch (error) {
    console.error('[Presidio Background] Anonymization error:', error);
    throw error;
  }
}

// Deanonymize AI response using saved session mapping
async function deanonymizeText(sessionId, text) {
  const backendUrl = await getBackendUrl();
  const response = await fetch(`${backendUrl}/api/deanonymize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, text })
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

// Open the side panel (right side) when the toolbar icon is clicked
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch(error => console.error('Failed to set side panel behavior:', error));

// Context menu for anonymizing selected text
chrome.runtime.onInstalled.addListener(() => {
  getUiLanguage().then(language => {
    chrome.contextMenus.removeAll(() => {
      if (chrome.runtime.lastError) {
        console.error('Failed to reset context menu:', chrome.runtime.lastError.message);
        return;
      }

      chrome.contextMenus.create({
        id: 'anonymize-selection',
        title: extensionText('contextMenu', language),
        contexts: ['selection']
      }, () => {
        if (chrome.runtime.lastError) {
          console.error('Failed to create context menu:', chrome.runtime.lastError.message);
        }
      });
    });
  }).catch(error => console.error('Failed to initialize context menu language:', error));
});

chrome.runtime.onStartup.addListener(() => {
  updateContextMenuLanguage().catch(error => console.error('Failed to update context menu language:', error));
});
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'local' && changes.uiLanguage) {
    updateContextMenuLanguage().catch(error => console.error('Failed to update context menu language:', error));
  }
});

async function updateContextMenuLanguage() {
  const language = await getUiLanguage();
  chrome.contextMenus.update('anonymize-selection', {
    title: extensionText('contextMenu', language)
  }, () => {
    if (chrome.runtime.lastError) {
      console.error('Failed to update context menu language:', chrome.runtime.lastError.message);
    }
  });
}

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'anonymize-selection') {
    const selectedText = info.selectionText;

    anonymizeText(selectedText)
      .then(result => {
        // Send result to content script to replace text
        chrome.tabs.sendMessage(tab.id, {
          action: 'replaceSelection',
          anonymizedText: result.anonymized_text
        });
      })
      .catch(error => {
        console.error('Failed to anonymize:', error);
      });
  }
});
