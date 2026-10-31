// Content script for Presidio Browser Anonymizer

let extensionEnabled = true;
let currentLanguage = DEFAULT_UI_LANGUAGE;
let lastSessionId = null; // Session ID de la dernière anonymisation (pour désanonymiser)

// Load extension state on initialization
async function loadExtensionState() {
  try {
    const result = await chrome.storage.local.get(['extensionEnabled', 'uiLanguage']);
    extensionEnabled = result.extensionEnabled !== false; // Default to true
    currentLanguage = SUPPORTED_UI_LANGUAGES.includes(result.uiLanguage)
      ? result.uiLanguage
      : DEFAULT_UI_LANGUAGE;
    console.log('[Presidio] Extension state loaded:', extensionEnabled);
  } catch (error) {
    console.error('[Presidio] Failed to load extension state:', error);
    extensionEnabled = true;
  }
}

// Initialize - wait for state to load
(async () => {
  await loadExtensionState();
  console.log('[Presidio] Content script initialized. Auto-anonymization:', extensionEnabled ? 'ENABLED' : 'DISABLED');
})();

// Listen for storage changes
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace !== 'local') return;

  if (changes.uiLanguage) {
    currentLanguage = SUPPORTED_UI_LANGUAGES.includes(changes.uiLanguage.newValue)
      ? changes.uiLanguage.newValue
      : DEFAULT_UI_LANGUAGE;
  }

  if (changes.extensionEnabled) {
    extensionEnabled = changes.extensionEnabled.newValue;
    console.log('[Presidio] Extension state changed:', extensionEnabled ? 'ENABLED' : 'DISABLED');

    if (extensionEnabled) {
      showNotification(extensionText('extensionEnabled', currentLanguage), 'success');
    } else {
      showNotification(extensionText('extensionDisabled', currentLanguage), 'info');
    }
  }
});

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'replaceSelection') {
    replaceSelectedText(request.anonymizedText);
  }
});

// Replace selected text with anonymized version
function replaceSelectedText(anonymizedText) {
  const selection = window.getSelection();

  if (!selection.rangeCount) return;

  const range = selection.getRangeAt(0);
  range.deleteContents();
  range.insertNode(document.createTextNode(anonymizedText));

  // Clear selection
  selection.removeAllRanges();

  // Show notification
  showNotification(extensionText('textAnonymized', currentLanguage), 'success');
}

// Show notification toast
function showNotification(message, type = 'info') {
  const toast = document.createElement('div');
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: ${type === 'success' ? '#10b981' : '#2563eb'};
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    z-index: 999999;
    opacity: 0;
    transition: opacity 0.3s;
  `;

  document.body.appendChild(toast);

  // Fade in
  setTimeout(() => {
    toast.style.opacity = '1';
  }, 10);

  // Fade out and remove
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}

// Keyboard shortcut: Ctrl+Shift+D to deanonymize selected text
document.addEventListener('keydown', async (e) => {
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
    e.preventDefault();

    if (!lastSessionId) {
      showNotification(extensionText('noSession', currentLanguage), 'info');
      return;
    }

    const selectedText = window.getSelection().toString().trim();
    if (!selectedText) {
      showNotification(extensionText('selectText', currentLanguage), 'info');
      return;
    }

    try {
      showNotification(extensionText('deanonymizing', currentLanguage), 'info');
      const response = await chrome.runtime.sendMessage({
        action: 'deanonymize',
        sessionId: lastSessionId,
        text: selectedText
      });

      if (response.success) {
        replaceSelectedText(response.data.deanonymized_text);
        showNotification(extensionText('textDeanonymized', currentLanguage), 'success');
      } else {
        throw new Error(response.error);
      }
    } catch (error) {
      if (error.message?.includes('Extension context invalidated')) return;
      console.error('Deanonymization failed:', error);
      showNotification(extensionText('anonymizationError', currentLanguage), 'error');
    }
  }
});

// Keyboard shortcut: Ctrl+Shift+A to anonymize selected text
document.addEventListener('keydown', async (e) => {
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'A') {
    e.preventDefault();

    const selectedText = window.getSelection().toString().trim();

    if (!selectedText) {
      showNotification(extensionText('selectText', currentLanguage), 'info');
      return;
    }

    try {
      showNotification(extensionText('anonymizing', currentLanguage), 'info');

      const response = await chrome.runtime.sendMessage({
        action: 'anonymize',
        text: selectedText
      });

      if (response.success) {
        replaceSelectedText(response.data.anonymized_text);
      } else {
        throw new Error(response.error);
      }
    } catch (error) {
      if (error.message?.includes('Extension context invalidated')) return;
      console.error('Anonymization failed:', error);
      showNotification(extensionText('anonymizationError', currentLanguage), 'error');
    }
  }
});

// Auto-anonymize on paste (Ctrl+V)
document.addEventListener('paste', async (e) => {
  // Skip if extension is disabled
  if (!extensionEnabled) {
    console.log('[Presidio] Paste event - extension DISABLED, skipping');
    return;
  }

  console.log('[Presidio] Paste event detected - extension ENABLED');
  console.log('[Presidio] Active element:', document.activeElement?.tagName, document.activeElement?.className);

  // Get pasted text from clipboard
  const pastedText = e.clipboardData.getData('text/plain');

  if (!pastedText || pastedText.length === 0) {
    console.log('[Presidio] No text in clipboard, skipping');
    return;
  }

  console.log('[Presidio] Clipboard text length:', pastedText.length);

  // Capturer l'élément cible ET la position du curseur AVANT tout await
  const targetElement = document.activeElement;
  const savedRange = (() => {
    const sel = window.getSelection();
    return sel && sel.rangeCount > 0 ? sel.getRangeAt(0).cloneRange() : null;
  })();

  // CRITICAL: Prevent default AND stop propagation
  e.preventDefault();
  e.stopPropagation();
  e.stopImmediatePropagation();

  try {
    // Check skip flag AFTER preventDefault (flag check is async but paste is already blocked)
    try {
      const skipResult = await chrome.storage.local.get(['skipNextPaste']);
      if (skipResult.skipNextPaste) {
        chrome.storage.local.remove('skipNextPaste');
        console.log('[Presidio] Skipping anonymization - deanonymized result paste');
        // Restore focus and cursor before inserting
        targetElement?.focus();
        if (savedRange && (targetElement?.isContentEditable || targetElement?.contentEditable === 'true')) {
          const sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(savedRange);
        }
        const activeElement = targetElement;
        if (activeElement && (activeElement.tagName === 'TEXTAREA' || activeElement.tagName === 'INPUT')) {
          const start = activeElement.selectionStart || 0;
          const end = activeElement.selectionEnd || 0;
          activeElement.value = activeElement.value.substring(0, start) + pastedText + activeElement.value.substring(end);
          activeElement.selectionStart = activeElement.selectionEnd = start + pastedText.length;
          activeElement.dispatchEvent(new Event('input', { bubbles: true }));
        } else if (activeElement && (activeElement.isContentEditable || activeElement.contentEditable === 'true')) {
          activeElement.focus();
          document.execCommand('insertText', false, pastedText);
        }
        return;
      }
    } catch (_) { /* ignore */ }

    console.log('[Presidio] Sending anonymization request...');
    showNotification(extensionText('anonymizing', currentLanguage), 'info');

    const response = await chrome.runtime.sendMessage({
      action: 'anonymize',
      text: pastedText
    });

    console.log('[Presidio] Anonymization response:', response.success);

    if (response.success) {
      const ts = response.data.ts || response.data.session_id;
      if (ts) lastSessionId = ts;
      const anonymizedText = response.data.anonymized_text;
      // Remettre le focus et restaurer la position du curseur
      targetElement?.focus();
      if (savedRange && (targetElement?.isContentEditable || targetElement?.contentEditable === 'true')) {
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(savedRange);
      }
      const activeElement = targetElement;

      console.log('[Presidio] Inserting anonymized text into:', activeElement?.tagName);

      // METHOD 1: TEXTAREA or INPUT
      if (activeElement && (activeElement.tagName === 'TEXTAREA' || activeElement.tagName === 'INPUT')) {
        const start = activeElement.selectionStart || 0;
        const end = activeElement.selectionEnd || 0;
        const before = activeElement.value.substring(0, start);
        const after = activeElement.value.substring(end);

        // Replace content
        activeElement.value = before + anonymizedText + after;

        // Set cursor position
        const newPos = start + anonymizedText.length;
        activeElement.selectionStart = activeElement.selectionEnd = newPos;

        // Trigger events for React/Vue
        activeElement.dispatchEvent(new Event('input', { bubbles: true }));
        activeElement.dispatchEvent(new Event('change', { bubbles: true }));

        console.log('[Presidio] Text inserted into textarea/input');
      }
      // METHOD 2: ContentEditable (ChatGPT, Claude, Gmail)
      else if (activeElement && (activeElement.isContentEditable || activeElement.contentEditable === 'true')) {
        activeElement.focus();
        const success = document.execCommand('insertText', false, anonymizedText);

        if (!success) {
          // Fallback: manual insertion
          const selection = window.getSelection();
          if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            range.deleteContents();
            const textNode = document.createTextNode(anonymizedText);
            range.insertNode(textNode);

            // Move cursor to end
            range.setStartAfter(textNode);
            range.setEndAfter(textNode);
            selection.removeAllRanges();
            selection.addRange(range);
          }
        }

        // Trigger input event
        activeElement.dispatchEvent(new InputEvent('input', {
          bubbles: true,
          cancelable: true,
          inputType: 'insertText',
          data: anonymizedText
        }));

        console.log('[Presidio] Text inserted into contentEditable');
      }
      // METHOD 3: Shadow DOM or other (Perplexity?)
      else {
        console.log('[Presidio] Unknown element type, trying selection-based insertion');

        const selection = window.getSelection();
        if (selection && selection.rangeCount > 0) {
          const range = selection.getRangeAt(0);
          range.deleteContents();
          const textNode = document.createTextNode(anonymizedText);
          range.insertNode(textNode);

          // Move cursor
          range.setStartAfter(textNode);
          range.setEndAfter(textNode);
          selection.removeAllRanges();
          selection.addRange(range);
        } else {
          console.error('[Presidio] No selection range available');
        }
      }

      showNotification(extensionText('pasteAnonymized', currentLanguage), 'success');
    } else {
      throw new Error(response.error);
    }
  } catch (error) {
    if (error.message?.includes('Extension context invalidated')) return;
    console.error('[Presidio] Paste anonymization failed:', error);
    showNotification(extensionText('pasteError', currentLanguage), 'error');

    // Fallback: paste original text using captured targetElement
    targetElement?.focus();
    if (targetElement && (targetElement.tagName === 'TEXTAREA' || targetElement.tagName === 'INPUT')) {
      const start = targetElement.selectionStart || 0;
      const end = targetElement.selectionEnd || 0;
      const before = targetElement.value.substring(0, start);
      const after = targetElement.value.substring(end);
      targetElement.value = before + pastedText + after;
      targetElement.selectionStart = targetElement.selectionEnd = start + pastedText.length;
      targetElement.dispatchEvent(new Event('input', { bubbles: true }));
    } else if (targetElement && (targetElement.isContentEditable || targetElement.contentEditable === 'true')) {
      document.execCommand('insertText', false, pastedText);
    }
  }
}, true);

// =============================================================================
// AUTO-ANONYMIZE BEFORE SEND (ChatGPT, Gmail, Forms)
// =============================================================================

// Track which textareas we're monitoring
const monitoredTextareas = new WeakSet();

// Function to anonymize textarea content before submission
async function anonymizeBeforeSend(textarea) {
  const text = textarea.value || textarea.textContent || textarea.innerText;

  console.log('[Presidio] anonymizeBeforeSend() called - text length:', text?.length || 0);

  if (!text || text.trim().length === 0) {
    console.log('[Presidio] No text to anonymize, skipping');
    return;
  }

  try {
    console.log('[Presidio] Starting anonymization, text length:', text.length);
    showNotification(extensionText('anonymizingBeforeSend', currentLanguage), 'info');

    const response = await chrome.runtime.sendMessage({
      action: 'anonymize',
      text: text
    });

    if (response.success) {
      // Replace textarea content with anonymized version
      if (textarea.tagName === 'TEXTAREA' || textarea.tagName === 'INPUT') {
        textarea.value = response.data.anonymized_text;
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
      } else if (textarea.isContentEditable || textarea.contentEditable === 'true') {
        textarea.textContent = response.data.anonymized_text;
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
      }

      console.log('[Presidio] Text anonymized before send!');
      showNotification(extensionText('sentAnonymized', currentLanguage), 'success');

      // Flash green border
      textarea.style.transition = 'border-color 0.3s';
      textarea.style.borderColor = '#10b981';
      setTimeout(() => {
        textarea.style.borderColor = '';
      }, 1000);
    } else {
      throw new Error(response.error);
    }
  } catch (error) {
    if (error.message?.includes('Extension context invalidated')) {
      // Extension was reloaded — page refresh needed, nothing to do
      return;
    }
    console.error('[Presidio] Anonymization before send failed:', error);
    showNotification(extensionText('sendError', currentLanguage), 'error');
  }
}

// Monitor form submissions
document.addEventListener('submit', async (e) => {
  // Skip if extension is disabled
  if (!extensionEnabled) {
    return;
  }

  console.log('[Presidio] Form submit detected');

  // Find textarea/input in the form
  const form = e.target;
  const textareas = form.querySelectorAll('textarea, input[type="text"], [contenteditable="true"]');

  if (textareas.length > 0) {
    // Prevent form submission temporarily
    e.preventDefault();
    e.stopPropagation();

    // Anonymize all textareas
    for (const textarea of textareas) {
      await anonymizeBeforeSend(textarea);
    }

    // Submit form after anonymization
    setTimeout(() => {
      form.submit();
    }, 100);
  }
}, true);

// Buttons whose next click should pass through untouched (programmatic re-click
// after anonymization) - without this guard the handler re-triggers itself forever
const passthroughClicks = new WeakSet();

// Monitor button clicks (ChatGPT, Claude, etc.)
document.addEventListener('click', async (e) => {
  // Skip if extension is disabled
  if (!extensionEnabled) {
    return;
  }

  const button = e.target.closest('button');

  if (!button) return;

  if (passthroughClicks.has(button)) {
    passthroughClicks.delete(button);
    return;
  }

  // Check if this is a "Send" button (ChatGPT, Claude, etc.)
  const buttonText = button.textContent.toLowerCase();
  const isSendButton =
    buttonText.includes('send') ||
    buttonText.includes('wyślij') ||
    buttonText.includes('submit') ||
    button.type === 'submit' ||
    button.getAttribute('data-testid')?.includes('send') ||
    button.className.includes('send');

  if (!isSendButton) return;

  console.log('[Presidio] Send button clicked, searching for textarea...');

  // Find nearby textarea or contenteditable
  const parent = button.closest('form') || button.closest('div');
  if (!parent) return;

  const textarea =
    parent.querySelector('textarea') ||
    parent.querySelector('[contenteditable="true"]') ||
    parent.querySelector('input[type="text"]') ||
    document.querySelector('textarea:focus') ||
    document.querySelector('[contenteditable="true"]:focus');

  if (textarea) {
    console.log('[Presidio] Found textarea, anonymizing...');

    // Prevent button click temporarily
    e.preventDefault();
    e.stopPropagation();

    // Anonymize content
    await anonymizeBeforeSend(textarea);

    // Click button after anonymization (passthrough - see guard above)
    passthroughClicks.add(button);
    setTimeout(() => {
      button.click();
    }, 100);
  }
}, true);

// NOTE: Enter-to-send interception was removed - unreliable on ChatGPT/Claude/Perplexity.
// PASTE (Ctrl+V) and send-button interception cover those flows.

// =============================================================================
// BOUTON « DÉSANONYMISER » SOUS LES MESSAGES CONTENANT DES JETONS
// =============================================================================
// Les jetons sont remplacés dans les nœuds texte (la mise en forme est conservée),
// uniquement à l'affichage : rien n'est renvoyé au site.

const TOKEN_RE = /\[[A-Z][A-Z_]*_\d+_(\d{2}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})\]/g;
// Conteneurs de message connus (ChatGPT, Claude, Gemini, Mistral, Perplexity…), sinon le bloc parent
const MESSAGE_SELECTOR = [
  '[data-message-author-role]', '.font-claude-response', '[data-testid="user-message"]',
  'message-content', '.markdown', '.prose', 'article'
].join(',');
const BLOCK_SELECTOR = 'p, li, td, pre, blockquote, div';
// Pas de détection avant 1,5 s de calme (réponse en cours d'écriture), mais au plus
// toutes les 4 s : ChatGPT et Claude modifient la page en continu (animations, minuteries)
const SCAN_DELAY_MS = 1500;
const SCAN_MAX_WAIT_MS = 4000;
const TOKEN_SEPARATOR = '\n␞\n';

const revealStates = new WeakMap(); // message -> { button, revealed, originals }
let scanTimer = null;

function messageContainerOf(node) {
  const el = node.parentElement;
  if (!el || el.closest('textarea, input, [contenteditable="true"], .masqueia-reveal')) return null;
  return el.closest(MESSAGE_SELECTOR) || el.closest(BLOCK_SELECTOR);
}

function tokenTextNodes(root) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode: n => (TOKEN_RE.lastIndex = 0, TOKEN_RE.test(n.data)) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP
  });
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  return nodes;
}

function scanForTokens() {
  if (!document.body) return;
  const messages = new Set();
  for (const node of tokenTextNodes(document.body)) {
    const container = messageContainerOf(node);
    if (container) messages.add(container);
  }
  // Ne garder que les conteneurs les plus externes
  for (const message of messages) {
    const parent = message.parentElement?.closest(MESSAGE_SELECTOR);
    if (parent && messages.has(parent)) continue;
    const state = revealStates.get(message);
    if (!state) {
      addRevealButton(message);
    } else if (!state.button.isConnected) {
      // Le site a redessiné le message (React, Angular) et effacé le bouton
      message.appendChild(state.button);
    }
  }
}

function addRevealButton(message) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'masqueia-reveal';
  button.textContent = extensionText('revealButton', currentLanguage);
  button.style.cssText = `
    display: block; margin: 8px 0 0; padding: 4px 10px;
    font: 500 12px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #2563eb; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; cursor: pointer;
  `;
  const state = { button, revealed: false, originals: [] };
  revealStates.set(message, state);
  button.addEventListener('click', e => {
    e.preventDefault();
    e.stopPropagation();
    state.revealed ? hideOriginals(state) : revealOriginals(message, state);
  });
  message.appendChild(button);
}

// Valeurs d'origine des jetons, par session (le timestamp porté par chaque jeton)
async function resolveTokens(tokens) {
  const bySession = new Map();
  for (const token of tokens) {
    const ts = token.match(/(\d{2}(?:_\d{2}){5})\]$/)[1];
    if (!bySession.has(ts)) bySession.set(ts, []);
    bySession.get(ts).push(token);
  }
  const values = new Map();
  for (const [ts, sessionTokens] of bySession) {
    const response = await chrome.runtime.sendMessage({
      action: 'deanonymize', sessionId: ts, text: sessionTokens.join(TOKEN_SEPARATOR)
    });
    if (!response?.success) continue; // session inconnue : jetons laissés tels quels
    const parts = response.data.deanonymized_text.split(TOKEN_SEPARATOR);
    if (parts.length !== sessionTokens.length) continue;
    sessionTokens.forEach((token, i) => { if (parts[i] !== token) values.set(token, parts[i]); });
  }
  return values;
}

async function revealOriginals(message, state) {
  const nodes = tokenTextNodes(message);
  const tokens = new Set(nodes.flatMap(n => n.data.match(TOKEN_RE) || []));
  let values;
  try {
    values = await resolveTokens(tokens);
  } catch (error) {
    // Extension rechargée ou mise à jour : ce script n'a plus accès au moteur
    if (!chrome.runtime?.id || error.message?.includes('Extension context invalidated')) {
      showNotification(extensionText('reloadPage', currentLanguage), 'error');
      return;
    }
    values = new Map();
  }
  if (values.size === 0) {
    showNotification(extensionText('revealError', currentLanguage), 'error');
    return;
  }
  state.originals = nodes.map(node => ({ node, text: node.data }));
  for (const node of nodes) {
    node.data = node.data.replace(TOKEN_RE, token => values.get(token) ?? token);
  }
  state.revealed = true;
  state.button.textContent = extensionText('hideButton', currentLanguage);
}

function hideOriginals(state) {
  for (const { node, text } of state.originals) {
    if (node.isConnected) node.data = text;
  }
  state.originals = [];
  state.revealed = false;
  state.button.textContent = extensionText('revealButton', currentLanguage);
}

let firstPendingChange = 0;

function runScan() {
  firstPendingChange = 0;
  scanForTokens();
}

new MutationObserver(mutations => {
  // Les ajouts de nos propres boutons ne relancent pas de détection
  if (mutations.every(m => [...m.addedNodes].every(n => n.classList?.contains('masqueia-reveal')))) return;
  const now = Date.now();
  if (!firstPendingChange) firstPendingChange = now;
  clearTimeout(scanTimer);
  const delay = Math.min(SCAN_DELAY_MS, Math.max(0, firstPendingChange + SCAN_MAX_WAIT_MS - now));
  scanTimer = setTimeout(runScan, delay);
}).observe(document.documentElement, { childList: true, subtree: true, characterData: true });
scanTimer = setTimeout(runScan, SCAN_DELAY_MS);
