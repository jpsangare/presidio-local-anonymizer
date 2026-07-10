# Instalacja Presidio Browser Anonymizer

Pełna instrukcja instalacji wtyczki Chrome wraz z backendem.

## Wymagania

- **Python 3.8+** (sprawdź: `python --version` lub `python3 --version`)
- **Chrome/Edge/Brave** - przeglądarka oparta na Chromium
- **2 GB RAM** - dla modelu SpaCy
- **Połączenie internetowe** - do pobrania zależności

---

## Instalacja Automatyczna (Zalecana)

### Windows

> 🪟 **Wersja dla laika (bez gita i terminala):** [WINDOWS.md](WINDOWS.md)

1. **Pobierz projekt** (git albo zielony przycisk `Code` → `Download ZIP` + wypakuj):
   ```cmd
   git clone https://github.com/gacabartosz/presidio-local-anonymizer
   cd presidio-local-anonymizer
   ```

2. **Kliknij 2x `Uruchom-Windows.bat`** — pierwszy raz instaluje wszystko (łącznie z Pythonem, jeśli go brak), potem startuje backend i otwiera dashboard

3. **Gotowe!** Backend działa na `http://localhost:6677`. Autostart przy logowaniu: kliknij 2x `Autostart-Windows.bat`

### macOS

1. **Pobierz projekt:**
   ```bash
   git clone https://github.com/gacabartosz/presidio-local-anonymizer
   cd presidio-local-anonymizer
   ```

2. **Uruchom instalator:**
   ```bash
   ./install-mac.sh
   ```

3. **Gotowe!** Backend uruchomi się automatycznie na `http://localhost:6677`

### Linux

1. **Zainstaluj Python3 i venv** (jeśli jeszcze nie masz):
   ```bash
   # Ubuntu/Debian
   sudo apt install python3 python3-pip python3-venv

   # Fedora/RHEL
   sudo dnf install python3 python3-pip

   # Arch
   sudo pacman -S python python-pip
   ```

2. **Pobierz projekt:**
   ```bash
   git clone https://github.com/gacabartosz/presidio-local-anonymizer
   cd presidio-local-anonymizer
   ```

3. **Uruchom instalator:**
   ```bash
   ./install-linux.sh
   ```

4. **Gotowe!** Backend uruchomi się automatycznie na `http://localhost:6677`

---

## Instalacja Chrome Extension

### Krok 1: Zainstaluj wtyczkę

#### Opcja A: Load Unpacked (Deweloperska)

1. Otwórz Chrome → wpisz w pasku adresu: `chrome://extensions/`
2. Włącz **"Tryb dewelopera"** (przełącznik w prawym górnym rogu)
3. Kliknij **"Załaduj rozpakowane"**
4. Wybierz folder: `/path/to/presidio-local-anonymizer/chrome-extension`
5. Wtyczka zostanie załadowana!

#### Opcja B: Z pliku CRX (Produkcja)

1. Pobierz plik `.crx` z [GitHub Releases](https://github.com/gacabartosz/presidio-local-anonymizer/releases)
2. Przeciągnij plik do `chrome://extensions/`
3. Kliknij "Dodaj rozszerzenie"

### Krok 2: Skonfiguruj URL backendu

1. Kliknij **ikonę wtyczki** w pasku narzędzi Chrome
2. Kliknij **"🔧 Konfiguracja Wtyczki"**
3. Wpisz URL: `http://localhost:6677`
4. Kliknij **"🔍 Testuj Połączenie"**
5. Jeśli widzisz "✅ Połączenie udane!" → kliknij **"💾 Zapisz"**

---

## Jak używać?

### 1. Auto-Anonimizacja przy Wklejaniu (Najłatwiejsza!)

**Automatycznie anonimizuje tekst gdy go wklejasz:**

```
1. Skopiuj tekst z danymi osobowymi
2. Wklej go gdziekolwiek (Ctrl+V / Cmd+V)
3. Tekst zostanie automatycznie zanonimizowany!
```

**Działa wszędzie:**
- ChatGPT, Claude, Bard
- Gmail, Outlook
- Formularze
- Pola tekstowe

### 2. Skrót Klawiszowy

```
1. Zaznacz tekst na stronie
2. Naciśnij Ctrl+Shift+A (Mac: Cmd+Shift+A)
3. Tekst zostanie zanonimizowany
```

### 3. Menu Kontekstowe

```
1. Zaznacz tekst
2. Kliknij prawym przyciskiem myszy
3. Wybierz "Anonimizuj zaznaczony tekst"
```

---

## Przykład Użycia

**Tekst przed anonimizacją:**
```
Dzień dobry, jestem Jan Kowalski, mój PESEL to 44051401359,
email: jan.kowalski@example.com, tel: +48 123 456 789.
Mieszkam w Warszawie przy ul. Pięknej 15.
```

**Tekst po anonimizacji:**
```
Dzień dobry, jestem [OSOBA], mój PESEL to [PESEL],
email: [EMAIL], tel: [TELEFON].
Mieszkam w [LOKALIZACJA] przy ul. [LOKALIZACJA].
```

---

## Wykrywane Typy Danych

### Polskie
- **PESEL** - Numer PESEL
- **NIP** - Numer identyfikacji podatkowej
- **REGON** - Numer REGON
- **Dowód osobisty** - Numer dowodu
- **Paszport** - Numer paszportu

### Międzynarodowe
- **Imię i nazwisko** - Dane osobowe
- **Email** - Adres email
- **Telefon** - Numer telefonu
- **Karta kredytowa** - Numer karty
- **IBAN** - Numer konta bankowego
- **Adres IP** - Adres IP
- **URL** - Adresy stron
- **Data/czas** - Daty i godziny
- **Lokalizacja** - Miasta, adresy

---

## Troubleshooting

### Backend nie uruchamia się

**Problem:** Błąd "Port 6677 is already in use"

**Rozwiązanie:**
```bash
# Windows
netstat -ano | findstr :6677
taskkill /PID <numer_PID> /F

# macOS/Linux
lsof -i :6677
kill -9 <PID>
```

### Status wtyczki: "Offline"

1. **Sprawdź czy backend działa:**
   ```bash
   curl http://localhost:6677/api/health
   ```
   Powinno zwrócić: `{"status":"healthy"}`

2. **Sprawdź URL w konfiguracji wtyczki:**
   - Otwórz opcje wtyczki
   - Upewnij się że URL to `http://localhost:6677`
   - Kliknij "Testuj Połączenie"

3. **Restart backendu:**
   - Zatrzymaj backend (Ctrl+C)
   - Uruchom ponownie: `python app.py`

### Python nie jest zainstalowany

**Windows:**
1. Pobierz Python z: https://www.python.org/downloads/
2. WAŻNE: Zaznacz "Add Python to PATH"!
3. Uruchom instalator

**macOS:**
```bash
# Użyj Homebrew
brew install python3
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv

# Fedora
sudo dnf install python3 python3-pip
```

### Model SpaCy nie pobiera się

**Problem:** Błąd podczas `python -m spacy download pl_core_news_md`

**Rozwiązanie:**
```bash
# Aktywuj venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate.bat  # Windows

# Spróbuj ponownie
pip install https://github.com/explosion/spacy-models/releases/download/pl_core_news_md-3.7.0/pl_core_news_md-3.7.0-py3-none-any.whl
```

### Wtyczka nie wykrywa danych

1. **Sprawdź czy encje są włączone:**
   - Kliknij ikonę wtyczki → "⚙️ Ustawienia"
   - Upewnij się że PERSON, EMAIL_ADDRESS itp. są zaznaczone
   - Kliknij "Zapisz"

2. **Reload wtyczki:**
   - `chrome://extensions/`
   - Kliknij ⟳ przy wtyczce

---

## Aktualizacja

### Aktualizacja Backendu

```bash
cd presidio-local-anonymizer
git pull origin main

cd backend
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate.bat  # Windows

pip install -r requirements.txt --upgrade
```

### Aktualizacja Wtyczki

1. `chrome://extensions/`
2. Kliknij ⟳ (reload) przy wtyczce
3. Lub pobierz nową wersję z GitHub Releases

---

## Uruchamianie Backendu na Starcie Systemu

### Windows (Task Scheduler)

1. Otwórz **Task Scheduler**
2. Create Basic Task → "Presidio Backend"
3. Trigger: "When I log on"
4. Action: "Start a program"
5. Program: `C:\path\to\presidio-local-anonymizer\Uruchom-Windows.bat`

### macOS (launchd)

Utwórz plik `~/Library/LaunchAgents/com.presidio.backend.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.presidio.backend</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/presidio-local-anonymizer/install-mac.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Załaduj:
```bash
launchctl load ~/Library/LaunchAgents/com.presidio.backend.plist
```

### Linux (systemd)

Utwórz plik `~/.config/systemd/user/presidio-backend.service`:

```ini
[Unit]
Description=Presidio Browser Anonymizer Backend
After=network.target

[Service]
Type=simple
ExecStart=/path/to/presidio-local-anonymizer/install-linux.sh
Restart=on-failure

[Install]
WantedBy=default.target
```

Aktywuj:
```bash
systemctl --user enable presidio-backend
systemctl --user start presidio-backend
```

---

## FAQ

### Czy dane są wysyłane do internetu?

**Nie!** Wszystko działa lokalnie na Twoim komputerze. Żadne dane nie opuszczają Twojej maszyny.

### Czy mogę użyć innego portu?

Tak! Uruchom backend:
```bash
python app.py --port 8080
```

Następnie zmień URL w opcjach wtyczki na `http://localhost:8080`

### Czy działa na innych przeglądarkach?

Tak! Wtyczka działa na wszystkich przeglądarkach opartych o Chromium:
- Google Chrome
- Microsoft Edge
- Brave
- Opera
- Vivaldi

---

## Pomoc i Wsparcie

- **GitHub Issues:** https://github.com/gacabartosz/presidio-local-anonymizer/issues
- **Dokumentacja Chrome:** chrome-extension/README.md
- **Dokumentacja Backend:** backend/README.md

---

## Licencja

MIT License - zobacz plik [LICENSE](LICENSE)
