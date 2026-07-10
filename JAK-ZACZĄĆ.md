# 🚀 Jak zacząć? - Przewodnik dla każdego

**Prosty przewodnik instalacji Presidio Browser Anonymizer**
*Dla osób bez wiedzy technicznej - wszystko krok po kroku!*

> 🪟 **Masz Windows?** Jest jeszcze prostsza droga: [WINDOWS.md](WINDOWS.md) — pobierasz ZIP i klikasz dwa razy jeden plik. Nic więcej.

---

## 🤔 Co to w ogóle jest?

To wtyczka do przeglądarki Chrome, która **automatycznie ukrywa Twoje dane osobowe** gdy wklejasz tekst do:
- ChatGPT
- Claude
- Gmail
- Formularzy internetowych
- Wszystkiego innego!

**Przykład:**
- **Wklejasz:** "Nazywam się Jan Kowalski, email: jan@example.com, tel: 123-456-789"
- **Otrzymujesz:** "Nazywam się [OSOBA], email: [EMAIL], tel: [TELEFON]"

**Wszystko działa LOKALNIE na Twoim komputerze** - żadne dane nie wychodzą na internet! 🔒

---

## ✅ Czego potrzebujesz?

- ✅ Komputer z systemem Windows, Mac lub Linux
- ✅ Przeglądarka Chrome (lub Edge, Brave, Opera)
- ✅ 10 minut czasu
- ✅ Połączenie z internetem (tylko do pobrania)

---

## 📥 KROK 1: Pobierz program

### Sposób 1: Jeśli masz zainstalowane "git"

**Windows:**
1. Otwórz "Wiersz polecenia" (CMD)
2. Wpisz:
```
git clone https://github.com/gacabartosz/presidio-local-anonymizer
cd presidio-local-anonymizer
```

**Mac lub Linux:**
1. Otwórz Terminal
2. Wpisz:
```bash
git clone https://github.com/gacabartosz/presidio-local-anonymizer
cd presidio-local-anonymizer
```

### Sposób 2: Pobierz ZIP (jeśli nie masz "git")

1. Wejdź na: https://github.com/gacabartosz/presidio-local-anonymizer
2. Kliknij zielony przycisk **"Code"**
3. Wybierz **"Download ZIP"**
4. Rozpakuj pobrany plik do folderu, np. `C:\presidio\` (Windows) lub `~/presidio/` (Mac/Linux)
5. Otwórz ten folder w Wierszu polecenia (Windows) lub Terminalu (Mac/Linux)

---

## 🔧 KROK 2: Zainstaluj backend (silnik anonimizacji)

Backend to program, który będzie wykrywał i ukrywał dane osobowe.

### Windows

1. **W folderze z programem kliknij 2x na: `Uruchom-Windows.bat`** — i to wszystko!
   - Skrypt sam sprawdzi Pythona (a jeśli go nie masz — sam go zainstaluje)
   - Pobierze biblioteki i polski model językowy (5-10 minut, ~500 MB, tylko za pierwszym razem)
   - Uruchomi backend i sam otworzy panel w przeglądarce ✅
2. **Opcjonalnie:** kliknij 2x `Autostart-Windows.bat`, żeby backend startował sam po włączeniu komputera

> Szczegółowy przewodnik z rozwiązywaniem problemów: [WINDOWS.md](WINDOWS.md)

### Mac

1. **Sprawdź czy masz Pythona:**
   - Otwórz Terminal (Aplikacje → Narzędzia → Terminal)
   - Wpisz: `python3 --version`
   - Jeśli widzisz wersję → **OK!**
   - Jeśli nie:
     ```bash
     brew install python3
     ```
     (jeśli nie masz brew, wejdź na: https://brew.sh)

2. **Uruchom instalator:**
   ```bash
   chmod +x install-mac.sh
   ./install-mac.sh
   ```
   - Poczekaj 5-10 minut
   - Gdy zobaczysz: `Backend uruchomiony na http://localhost:6677` → **DZIAŁA!** ✅

### Linux (Ubuntu/Debian)

1. **Zainstaluj Pythona:**
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```

2. **Uruchom instalator:**
   ```bash
   chmod +x install-linux.sh
   ./install-linux.sh
   ```
   - Poczekaj 5-10 minut
   - Gdy zobaczysz: `Backend uruchomiony na http://localhost:6677` → **DZIAŁA!** ✅

---

## 🌐 KROK 3: Zainstaluj wtyczkę w Chrome

1. **Otwórz Chrome**

2. **Wejdź na stronę rozszerzeń:**
   - Wpisz w pasku adresu: `chrome://extensions/`
   - Lub: Menu (⋮) → Więcej narzędzi → Rozszerzenia

3. **Włącz tryb dewelopera:**
   - W prawym górnym rogu znajdź przełącznik **"Tryb dewelopera"**
   - Kliknij, aby włączyć (powinien być niebieski)

4. **Załaduj wtyczkę:**
   - Kliknij przycisk **"Załaduj rozpakowane"**
   - Wybierz folder: `presidio-local-anonymizer/chrome-extension/`
   - Kliknij "Wybierz folder"

5. **Gotowe!** ✅
   - Powinieneś zobaczyć kafelek "Presidio Browser Anonymizer"
   - Jeśli pytanie o uprawnienia - kliknij "Zezwól"

---

## 🎉 KROK 4: Sprawdź czy działa!

### Test 1: Sprawdź połączenie

1. Kliknij ikonę wtyczki w pasku Chrome (puzzle 🧩)
2. Znajdź "Presidio Browser Anonymizer"
3. Kliknij na nią
4. Powinieneś zobaczyć: **"Status: Online"** (zielony) ✅
5. Jeśli widzisz "Offline" (czerwony):
   - Sprawdź czy terminal/wiersz polecenia z backendem jest wciąż otwarty
   - Jeśli nie, uruchom ponownie: `Uruchom-Windows.bat` (Windows) lub `./install-mac.sh` (Mac)

### Test 2: Wypróbuj na ChatGPT

1. Otwórz https://chatgpt.com (lub https://claude.ai)

2. Skopiuj ten tekst (Ctrl+C / Cmd+C):
   ```
   Dzień dobry, nazywam się Anna Kowalska, mój email to anna.kowalska@example.com, telefon: +48 123 456 789, PESEL: 92010212345
   ```

3. Wklej go w ChatGPT (Ctrl+V / Cmd+V)

4. **Co powinieneś zobaczyć:**
   ```
   Dzień dobry, nazywam się [OSOBA], mój email to [EMAIL], telefon: [TELEFON], PESEL: [PESEL]
   ```

5. Jeśli dane zostały ukryte → **DZIAŁA!** 🎉

6. Jeśli dane **NIE zostały** ukryte:
   - Sprawdź czy wtyczka ma status "ON" (kliknij ikonę wtyczki)
   - Sprawdź czy backend działa (terminal/wiersz polecenia powinien być otwarty)
   - Przeładuj wtyczkę: `chrome://extensions/` → znajdź wtyczkę → kliknij ⟳

---

## 📊 Panel kontrolny (Dashboard)

Możesz podejrzeć co wtyczka robi:

1. Otwórz w przeglądarce: http://localhost:6677/dashboard

2. Zobaczysz:
   - ✅ Status serwisu (online/offline)
   - 📊 Statystyki (ile zapytań, ile wykryto danych)
   - 🧪 Tester - możesz przetestować anonimizację bez wtyczki
   - 📋 Logi - historia: co wklejono → co wyszło

---

## ❓ Najczęstsze problemy

### Problem 1: "Nie mam Pythona"

**Rozwiązanie:**
- **Windows:** Pobierz z https://www.python.org/downloads/
  - WAŻNE: Podczas instalacji zaznacz "Add Python to PATH"!
- **Mac:** Zainstaluj: `brew install python3`
- **Linux:** Zainstaluj: `sudo apt install python3`

### Problem 2: "Backend pokazuje błąd"

**Rozwiązanie:**
1. Zamknij terminal/wiersz polecenia
2. Uruchom ponownie instalator:
   - Windows: `Uruchom-Windows.bat`
   - Mac: `./install-mac.sh`
   - Linux: `./install-linux.sh`

### Problem 3: "Wtyczka pokazuje 'Offline'"

**Rozwiązanie:**
1. Sprawdź czy terminal z backendem jest otwarty
2. Jeśli nie, uruchom ponownie backend:
   ```bash
   cd presidio-local-anonymizer/backend
   python app.py
   ```
3. Przeładuj wtyczkę w Chrome: `chrome://extensions/` → ⟳

### Problem 4: "Dane nie są ukrywane"

**Sprawdź:**
1. Czy backend działa? (terminal otwarty, bez błędów)
2. Czy wtyczka ma status ON? (kliknij ikonę wtyczki)
3. Czy używasz WKLEJANIA (Ctrl+V)? - to najlepiej działa!
4. Przeładuj stronę ChatGPT/Claude

---

## 🎚️ Włączanie/wyłączanie wtyczki

**Chcesz czasem wyłączyć anonimizację?**

1. Kliknij ikonę wtyczki w Chrome
2. Zobaczysz przełącznik ON/OFF
3. Kliknij, aby włączyć/wyłączyć
4. **ON** = anonimizacja działa ✅
5. **OFF** = anonimizacja wyłączona ⛔

---

## 🔒 Bezpieczeństwo

**Czy moje dane są bezpieczne?**

✅ **TAK!**
- Wszystko działa **lokalnie** na Twoim komputerze
- **Żadne dane NIE są wysyłane do internetu**
- Backend działa tylko na Twoim komputerze (localhost)
- Microsoft Presidio to profesjonalny silnik od Microsoftu

**Co widzi wtyczka?**
- Tylko tekst, który WKLEJASZ
- Nie czyta haseł, cookies, historii

---

## 📖 Dodatkowe pomoce

**Chcesz wiedzieć więcej?**

- 📄 [README.md](README.md) - Pełna dokumentacja (po angielsku)
- 🤖 [AI-SITES-GUIDE.md](AI-SITES-GUIDE.md) - Szczegółowy przewodnik dla ChatGPT, Claude, Perplexity
- 🧪 [TESTING.md](TESTING.md) - Jak testować wtyczkę
- 💾 [INSTALLATION.md](INSTALLATION.md) - Zaawansowana instalacja

---

## 💬 Potrzebujesz pomocy?

**Gdzie szukać pomocy?**

1. **Sprawdź Dashboard:** http://localhost:6677/dashboard
   - Zobacz logi, co się dzieje

2. **GitHub Issues:** https://github.com/gacabartosz/presidio-local-anonymizer/issues
   - Opisz problem
   - Dodaj zrzut ekranu
   - Napisz jaki system (Windows/Mac/Linux)

3. **Email autora:** (jeśli w projekcie jest podany)

---

## 🎯 Skrócona instrukcja (dla wprawionych)

**Windows:**
```cmd
git clone https://github.com/gacabartosz/presidio-local-anonymizer
cd presidio-local-anonymizer
Uruchom-Windows.bat
```

**Mac:**
```bash
git clone https://github.com/gacabartosz/presidio-local-anonymizer
cd presidio-local-anonymizer
./install-mac.sh
```

**Linux:**
```bash
git clone https://github.com/gacabartosz/presidio-local-anonymizer
cd presidio-local-anonymizer
./install-linux.sh
```

**Wtyczka Chrome:**
1. `chrome://extensions/`
2. Włącz "Tryb dewelopera"
3. "Załaduj rozpakowane" → wybierz `chrome-extension/`
4. Gotowe!

---

## ✨ Wskazówki

**💡 Jak najlepiej używać?**

1. **ZAWSZE używaj WKLEJANIA (Ctrl+V)**
   - To najbardziej niezawodna metoda!
   - Działa w ChatGPT, Claude, Gmail, wszędzie

2. **Sprawdzaj status wtyczki**
   - Kliknij ikonę → zobacz czy ON czy OFF
   - Zielony = działa, czerwony = wyłączona

3. **Sprawdzaj logi w Dashboard**
   - http://localhost:6677/dashboard → Logi
   - Zobacz co zostało wykryte i ukryte

4. **Nie zamykaj terminala!**
   - Terminal/Wiersz polecenia z backendem musi być otwarty
   - Możesz go zminimalizować

---

## 🎊 Gotowe!

**Gratulacje!** Masz działającą wtyczkę do anonimizacji danych! 🎉

**Teraz możesz bezpiecznie:**
- Wklejać teksty do ChatGPT
- Wysyłać wiadomości przez Gmail
- Wypełniać formularze
- I wiele więcej!

**Pamiętaj:**
- Backend musi być włączony (terminal/wiersz polecenia otwarty)
- Wtyczka musi mieć status ON
- Używaj WKLEJANIA (Ctrl+V)

---

<p align="center">
  <strong>Miłego używania! 🚀</strong><br/>
  <sub>Jeśli masz problem - sprawdź Dashboard lub GitHub Issues</sub>
</p>

<p align="center">
  <a href="README.md">Dokumentacja techniczna</a> •
  <a href="AI-SITES-GUIDE.md">Przewodnik AI</a> •
  <a href="https://github.com/gacabartosz/presidio-local-anonymizer/issues">Zgłoś problem</a>
</p>
