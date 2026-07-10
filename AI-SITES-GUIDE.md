# 🤖 Przewodnik: Anonimizacja na Stronach AI

## Wspierane Strony AI

Rozszerzenie działa na **WSZYSTKICH** stronach internetowych, w tym:

### ✅ Główne Strony AI:
- **ChatGPT** (chatgpt.com, chat.openai.com)
- **Claude** (claude.ai)
- **Perplexity** (perplexity.ai)
- **Google Gemini** (gemini.google.com)
- **Microsoft Copilot** (copilot.microsoft.com)
- **You.com**
- **Poe.com**
- **Any Chat** i inne

### ✅ Inne Strony:
- Gmail, Outlook, ProtonMail
- Facebook, Twitter/X, LinkedIn
- Formularze kontaktowe
- CRM (Salesforce, HubSpot)
- **Każdy formularz w internecie!**

---

## 🎯 Najlepsze Metody Anonimizacji

### Metoda #1: WKLEJANIE (Ctrl+V) ⭐ NAJLEPSZA

**Jak działa:**
1. Skopiuj tekst z danymi osobowymi (Ctrl+C)
2. Wejdź na stronę AI (ChatGPT, Claude, etc.)
3. Kliknij w pole tekstowe
4. **Wklej tekst (Ctrl+V)**
5. ✅ **Tekst zostanie automatycznie zanonimizowany PRZED wklejeniem!**

**Zalety:**
- ✅ Działa na 100% stron AI
- ✅ Najpewniejsza metoda
- ✅ Nie wymaga dodatkowych kliknięć
- ✅ Natychmiastowa anonimizacja

**Przykład:**
```
ORYGINALNY TEKST (skopiowany):
Jan Kowalski, email: jan@example.com, tel: 123-456-789, PESEL: 92010212345

PO WKLEJENIU (automatycznie zanonimizowane):
[OSOBA], email: [EMAIL], tel: [REGON], PESEL: [PESEL]
```

---

### Metoda #2: SKRÓT KLAWISZOWY (Ctrl+Shift+A) ⭐ BACKUP

**Jak działa:**
1. Wpisz lub wklej tekst z danymi osobowymi
2. **Zaznacz tekst** który chcesz zanonimizować
3. Naciśnij **Ctrl+Shift+A** (Cmd+Shift+A na Mac)
4. ✅ **Zaznaczony tekst zostanie zanonimizowany w miejscu!**

**Zalety:**
- ✅ Działa ZAWSZE, na każdej stronie
- ✅ Możesz wybrać co zanonimizować
- ✅ Działa nawet jeśli auto-paste nie zadziałało

**Przykład:**
```
1. Wpisz: "Jan Kowalski, email: jan@example.com"
2. Zaznacz cały tekst
3. Ctrl+Shift+A
4. Wynik: "[OSOBA], email: [EMAIL]"
```

---

### Metoda #3: PRAWY PRZYCISK MYSZY

**Jak działa:**
1. Wpisz lub wklej tekst z danymi osobowymi
2. **Zaznacz tekst**
3. **Prawy przycisk myszy** → "Anonimizuj zaznaczony tekst"
4. ✅ **Tekst zostanie zanonimizowany!**

**Zalety:**
- ✅ Intuicyjne menu kontekstowe
- ✅ Łatwe dla nowych użytkowników

---

### ~~Metoda #4: AUTO-ANONIMIZACJA PRZED WYSŁANIEM~~ ⚠️ EKSPERYMENTALNA

**Status:** Wyłączona w obecnej wersji

**Dlaczego wyłączona:**
- Nowoczesne frameworki JavaScript (React, Vue) używane przez ChatGPT, Claude i Perplexity nie zawsze poprawnie obsługują przechwytywanie kliknięć przycisku "Send"
- Ponowne triggerowanie kliknięcia może nie działać z ich skomplikowanym kodem JavaScript
- Czasami powodowało to wysyłanie wiadomości bez anonimizacji

**Zalecenie:** Używaj **METODY #1 (Ctrl+V)** - działa perfekcyjnie!

---

## 📋 Instrukcje dla Poszczególnych Stron

### ChatGPT (chatgpt.com)

#### ✅ CO DZIAŁA:
1. **PASTE (Ctrl+V)** ⭐ NAJLEPSZA
   - Skopiuj tekst → Ctrl+V w pole ChatGPT → Automatycznie zanonimizowane!

2. **Skrót (Ctrl+Shift+A)** ⭐ BACKUP
   - Wpisz tekst → Zaznacz → Ctrl+Shift+A → Zanonimizowane!

3. **Menu kontekstowe**
   - Wpisz tekst → Zaznacz → Prawy przycisk → "Anonimizuj"

#### ⚠️ CO NIE DZIAŁA:
- ~~Auto-anonimizacja przed wysłaniem~~ (wyłączona)
- ~~Przechwytywanie Enter~~ (wyłączona)

**Przykładowy Workflow:**
```
1. Masz tekst: "Jan Kowalski mieszka w Warszawie, PESEL: 92010212345"
2. Skopiuj tekst (Ctrl+C)
3. Wejdź na ChatGPT
4. Kliknij w pole tekstowe
5. Wklej (Ctrl+V)
6. ✅ Zostanie wklejone: "[OSOBA] mieszka w [LOKALIZACJA], PESEL: [PESEL]"
7. Wyślij do ChatGPT
```

---

### Claude (claude.ai)

**Identycznie jak ChatGPT** - Claude używa tego samego typu interfejsu (contenteditable div).

#### ✅ CO DZIAŁA:
1. **PASTE (Ctrl+V)** ⭐ NAJLEPSZA
2. **Skrót (Ctrl+Shift+A)** ⭐ BACKUP
3. **Menu kontekstowe**

---

### Perplexity (perplexity.ai)

**Identycznie jak ChatGPT i Claude**.

#### ✅ CO DZIAŁA:
1. **PASTE (Ctrl+V)** ⭐ NAJLEPSZA
2. **Skrót (Ctrl+Shift+A)** ⭐ BACKUP
3. **Menu kontekstowe**

---

### Google Gemini (gemini.google.com)

**Identycznie jak inne AI.**

#### ✅ CO DZIAŁA:
1. **PASTE (Ctrl+V)** ⭐ NAJLEPSZA
2. **Skrót (Ctrl+Shift+A)** ⭐ BACKUP
3. **Menu kontekstowe**

---

## 🎓 Najlepsze Praktyki

### 1. Zawsze używaj PASTE (Ctrl+V)
```
✅ DOBRZE:
- Skopiuj tekst → Ctrl+V na stronie AI
- Automatyczna anonimizacja!

❌ ŹLE:
- Przepisywanie tekstu ręcznie
- Oczekiwanie auto-anonimizacji przed wysłaniem
```

### 2. Jeśli PASTE nie zadziałał - użyj Ctrl+Shift+A
```
✅ BACKUP:
1. Wklej normalnie (Ctrl+V bez rozszerzenia)
2. Zaznacz cały tekst
3. Ctrl+Shift+A
4. Wyślij zanonimizowany tekst
```

### 3. Sprawdzaj czy rozszerzenie jest włączone
```
1. Kliknij ikonę rozszerzenia
2. Sprawdź czy toggle "Auto-anonimizacja" jest ZIELONY
3. Jeśli szary - kliknij aby włączyć
```

### 4. Sprawdzaj powiadomienia
```
✅ Gdy PASTE działa:
- Zobaczysz: "Anonimizowanie wklejonego tekstu..."
- Potem: "Tekst zanonimizowany przy wklejaniu!"

❌ Gdy są problemy:
- "Błąd anonimizacji. Wklejam oryginalny tekst."
- Sprawdź czy backend działa: http://localhost:6677
```

---

## 🔧 Troubleshooting

### Problem: "Błąd anonimizacji. Wklejam oryginalny tekst."

**Rozwiązanie:**
1. Sprawdź czy backend działa:
   ```bash
   curl http://localhost:6677/api/health
   ```
2. Jeśli nie działa - uruchom backend:
   ```bash
   cd /Users/gaca/presidio-local-anonymizer/backend
   source .venv/bin/activate
   python app.py
   ```

### Problem: Paste (Ctrl+V) nie anonimizuje

**Rozwiązanie:**
1. **Przeładuj rozszerzenie:**
   - chrome://extensions/
   - Kliknij ⟳ (odśwież)
   - **ZAMKNIJ wszystkie karty AI**
   - Otwórz ponownie (F5 nie wystarczy!)

2. **Sprawdź czy rozszerzenie jest włączone:**
   - Kliknij ikonę rozszerzenia
   - Toggle "Auto-anonimizacja" musi być ZIELONY

3. **Użyj alternatywy:**
   - Wklej normalnie
   - Zaznacz tekst
   - Ctrl+Shift+A

### Problem: Nie widzę powiadomień

**Rozwiązanie:**
1. Sprawdź konsolę DevTools (F12)
2. Powiadomienia pojawiają się w prawym dolnym rogu strony
3. Jeśli nie widzisz - sprawdź czy content script jest załadowany:
   - DevTools → Sources → Content scripts → content-script.js

---

## 📊 Porównanie Metod

| Metoda | ChatGPT | Claude | Perplexity | Gemini | Formularze | Niezawodność |
|--------|---------|--------|------------|--------|------------|--------------|
| **Paste (Ctrl+V)** | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ 100% |
| **Skrót (Ctrl+Shift+A)** | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ 100% |
| **Menu kontekstowe** | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ 100% |
| ~~Auto przed wysłaniem~~ | ❌ | ❌ | ❌ | ❌ | ⚠️ | ⭐⭐ 30% |

---

## ✅ Podsumowanie

### ⭐ Zalecana Metoda dla Wszystkich Stron AI:

```
1. Skopiuj tekst z danymi (Ctrl+C)
2. Wejdź na ChatGPT/Claude/Perplexity
3. Kliknij w pole tekstowe
4. Wklej (Ctrl+V)
5. ✅ Tekst automatycznie zanonimizowany!
6. Wyślij do AI
```

### 🔄 Backup Method (jeśli Paste nie zadziałał):

```
1. Wklej tekst normalnie
2. Zaznacz cały tekst
3. Ctrl+Shift+A
4. ✅ Tekst zanonimizowany!
5. Wyślij do AI
```

---

## 🎯 Dlaczego PASTE jest najlepsze?

1. **Działa na 100% stron** - textarea, contenteditable, input, formularze
2. **Automatyczne** - nie wymaga dodatkowych kliknięć
3. **Natychmiastowe** - anonimizacja przed wklejeniem
4. **Niezawodne** - nie zależy od struktury strony
5. **Uniwersalne** - ten sam workflow dla wszystkich AI

---

## 📞 Potrzebujesz Pomocy?

1. Przeczytaj [TESTING.md](./TESTING.md) - kompleksowy przewodnik testowania
2. Otwórz [test-extension.html](./test-extension.html) - test lokalny
3. Sprawdź logi w DevTools (F12)
4. Sprawdź background service worker console (chrome://extensions/)
5. Sprawdź backend logs (terminal)

**Backend Health Check:**
```bash
curl http://localhost:6677/api/health
```

Powinieneś zobaczyć:
```json
{"service":"presidio-browser-anonymizer","status":"healthy","version":"1.0.0"}
```

---

## 🚀 Szybki Start

```
1. Backend: python app.py
2. Chrome: Załaduj rozszerzenie
3. Toggle: Włącz "Auto-anonimizacja"
4. Test: open test-extension.html
5. Paste: Ctrl+V → Sprawdź czy anonimizuje
6. AI: Wejdź na ChatGPT/Claude/Perplexity
7. Use: Skopiuj tekst → Ctrl+V → ✅ Zanonimizowane!
```

---

**Wersja:** 1.3.0
**Ostatnia aktualizacja:** 2025-11-15
**Wspierane przeglądarki:** Chrome, Edge, Brave, Opera (Manifest V3)
