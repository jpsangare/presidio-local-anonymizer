# 🧪 Testowanie Rozszerzenia Presidio

## Przygotowanie (WAŻNE!)

### 1. Przeładuj rozszerzenie po zmianach
```
1. Otwórz chrome://extensions/
2. Znajdź "Presidio Browser Anonymizer"
3. Kliknij ikonę odświeżenia (⟳) lub przełącz OFF/ON
4. ZAMKNIJ wszystkie otwarte karty z AI (ChatGPT, Claude, Perplexity)
5. Otwórz je ponownie (F5 nie wystarczy!)
```

### 2. Sprawdź czy rozszerzenie jest włączone
```
1. Kliknij ikonę rozszerzenia w pasku narzędzi
2. Sprawdź czy przycisk "Auto-anonimizacja" jest ZIELONY
3. Jeśli jest szary - kliknij aby włączyć
```

### 3. Sprawdź czy backend działa
```bash
# Test 1: Health check
curl http://localhost:6677/api/health

# Test 2: Anonimizacja
curl -X POST http://localhost:6677/api/anonymize \
  -H "Content-Type: application/json" \
  -d '{"text":"Jan Kowalski, email: jan@example.com, tel: 123456789"}'
```

## Test 1: Strona Testowa (Najszybszy test)

```bash
# Otwórz test-extension.html
open /Users/gaca/presidio-local-anonymizer/test-extension.html
```

### Kroki testowe:
1. Otwórz **DevTools** (F12) → zakładka **Console**
2. Skopiuj tekst testowy:
   ```
   Jan Kowalski, email: jan.kowalski@example.com, tel: 123-456-789, PESEL: 92010212345
   ```
3. Wklej w pole tekstowe (Ctrl+V)
4. **Sprawdź w konsoli czy widzisz:**
   ```
   [Presidio] Paste event detected - extension ENABLED
   [Presidio] Sending anonymization request...
   [Presidio] Received response: ...
   ```
5. **Tekst powinien być zanonimizowany:**
   ```
   [OSOBA], email: [EMAIL], tel: [REGON], PESEL: [PESEL]
   ```

### Jeśli nie widzisz logów:
1. Rozszerzenie nie jest załadowane → Przeładuj (krok 1 powyżej)
2. Rozszerzenie jest wyłączone → Włącz toggle w popup
3. Content script nie działa → Sprawdź czy nie ma błędów w konsoli

### Jeśli widzisz błąd:
1. Sprawdź **background service worker console**:
   - chrome://extensions/
   - "Presidio Browser Anonymizer" → "Inspect views: service worker"
   - Zobacz czy jest błąd w komunikacji z backendem

## Test 2: ChatGPT (https://chatgpt.com)

### Przygotowanie:
1. Zamknij wszystkie karty ChatGPT
2. Otwórz nową kartę: https://chatgpt.com
3. Otwórz DevTools (F12)

### Test A: Wklejanie (Ctrl+V)
1. Skopiuj: `Jan Kowalski, email: jan@example.com, PESEL: 92010212345`
2. Kliknij w pole tekstowe ChatGPT
3. Naciśnij Ctrl+V
4. **Sprawdź:** Tekst powinien być zanonimizowany PRZED wklejeniem

### Test B: Skrót klawiszowy (Ctrl+Shift+A)
1. Wpisz tekst z danymi osobowymi
2. Zaznacz tekst
3. Naciśnij Ctrl+Shift+A (Cmd+Shift+A na Mac)
4. **Sprawdź:** Tekst zostanie zanonimizowany w miejscu

### Test C: Prawy przycisk myszy
1. Wpisz tekst z danymi osobowymi
2. Zaznacz tekst
3. Prawy przycisk myszy → "Anonimizuj zaznaczony tekst"
4. **Sprawdź:** Tekst zostanie zanonimizowany

## Test 3: Claude (https://claude.ai)

Powtórz wszystkie testy jak dla ChatGPT.

**Uwaga:** Claude używa contenteditable, podobnie jak ChatGPT - rozszerzenie powinno działać identycznie.

## Test 4: Perplexity (https://www.perplexity.ai)

Powtórz wszystkie testy jak dla ChatGPT.

**Uwaga:** Perplexity może używać textarea lub contenteditable - rozszerzenie obsługuje oba.

## Test 5: Inne strony AI

Rozszerzenie powinno działać na WSZYSTKICH stronach (<all_urls>), w tym:

- Gemini (gemini.google.com)
- Microsoft Copilot
- You.com
- Poe.com
- Any.chat
- Gmail
- Outlook
- Facebook
- Twitter/X
- LinkedIn
- **Każdy formularz w internecie!**

## Debugowanie Problemów

### Problem: "Błąd anonimizacji. Wklejam oryginalny tekst."

**Możliwe przyczyny:**

1. **Backend nie działa:**
   ```bash
   curl http://localhost:6677/api/health
   # Jeśli nie działa: uruchom backend
   cd /Users/gaca/presidio-local-anonymizer/backend
   source .venv/bin/activate
   python app.py
   ```

2. **Błędny URL backendu:**
   - Otwórz popup rozszerzenia
   - Kliknij "Ustawienia"
   - Sprawdź czy URL to: `http://localhost:6677`

3. **CORS błąd:**
   - Sprawdź background service worker console
   - Jeśli widzisz błąd CORS - backend nie ma prawidłowej konfiguracji

4. **Rozszerzenie nieaktualnepo ładowaniu:**
   - Przeładuj rozszerzenie: chrome://extensions/ → ⟳
   - Zamknij i otwórz ponownie strony AI

### Problem: Brak logów w konsoli

**Rozwiązanie:**

1. Sprawdź czy rozszerzenie jest zainstalowane:
   - chrome://extensions/
   - "Presidio Browser Anonymizer" - WŁĄCZONE

2. Sprawdź czy content script jest załadowany:
   - DevTools → zakładka "Sources"
   - W drzewie po lewej: "Content scripts" → powinien być "content-script.js"

3. Przeładuj stronę (F5) po przeładowaniu rozszerzenia

### Problem: Rozszerzenie wyłącza się automatycznie

**Rozwiązanie:**

Stan rozszerzenia jest zapisywany w `chrome.storage.local`. Sprawdź w background service worker console:

```javascript
chrome.storage.local.get(['extensionEnabled'], (result) => {
  console.log('Extension enabled:', result.extensionEnabled);
});
```

## Sprawdzanie Logów

### 1. Content Script Console (strona WWW)
- Otwórz DevTools (F12) na stronie WWW
- Zakładka "Console"
- Logi zaczynające się od `[Presidio]`

### 2. Background Service Worker Console
- chrome://extensions/
- "Presidio Browser Anonymizer" → "Inspect views: service worker"
- Logi zaczynające się od `[Presidio Background]`

### 3. Backend Logs
- Terminal gdzie uruchomiony jest backend
- Logi Flask pokazują wszystkie requesty:
  ```
  127.0.0.1 - - [15/Nov/2025 15:18:02] "POST /api/anonymize HTTP/1.1" 200 -
  ```

## Czego Szukać w Logach

### ✅ Prawidłowe działanie:

**Content Script:**
```
[Presidio] Content script initialized. Auto-anonymization: ENABLED
[Presidio] Paste event detected - extension ENABLED
[Presidio] Sending anonymization request for pasted text...
[Presidio] Received response: {success: true, data: {...}}
```

**Background Service Worker:**
```
[Presidio Background] Backend URL: http://localhost:6677
[Presidio Background] Sending request to: http://localhost:6677/api/anonymize
[Presidio Background] Response status: 200
[Presidio Background] Anonymization successful: [OSOBA] tel [REGON]
```

**Backend:**
```
2025-11-15 15:18:02 - api.anonymize - INFO - Analyzing with entities: [...]
2025-11-15 15:18:02 - app.anonymizer - INFO - Wykryto encje: {'PERSON': 1, 'PHONE_NUMBER': 1}
2025-11-15 15:18:02 - api.anonymize - INFO - Anonymized text: 2 entities found, 116ms
2025-11-15 15:18:02 - werkzeug - INFO - 127.0.0.1 - - [15/Nov/2025 15:18:02] "POST /api/anonymize HTTP/1.1" 200 -
```

### ❌ Problemy:

**Extension disabled:**
```
[Presidio] Paste event - extension DISABLED, skipping
```
→ Włącz toggle w popup

**Backend offline:**
```
[Presidio Background] Anonymization error: Failed to fetch
```
→ Uruchom backend

**CORS error:**
```
Access to fetch at 'http://localhost:6677/api/anonymize' from origin 'chrome-extension://...' has been blocked by CORS policy
```
→ Sprawdź czy backend ma prawidłową konfigurację CORS

## Porady

### 1. Zawsze przeładowuj rozszerzenie po zmianach w kodzie
```
chrome://extensions/ → ⟳ → Zamknij karty → Otwórz ponownie
```

### 2. Używaj test-extension.html do szybkich testów
```bash
open /Users/gaca/presidio-local-anonymizer/test-extension.html
```

### 3. Sprawdzaj wszystkie 3 logi (content, background, backend)

### 4. Test na prostej stronie przed testowaniem na AI
- test-extension.html najpierw
- Potem dopiero ChatGPT/Claude/Perplexity

### 5. Używaj skrótu Ctrl+Shift+A jako backup
- Jeśli auto-paste nie działa
- Zawsze możesz zaznaczekst i użyć skrótu

## Sukces!

Jeśli wszystkie testy przechodzą, rozszerzenie działa poprawnie na WSZYSTKICH stronach AI:
- ✅ ChatGPT
- ✅ Claude
- ✅ Perplexity
- ✅ Gemini
- ✅ Copilot
- ✅ I każda inna strona z formularzami!
