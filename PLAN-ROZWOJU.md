# 📋 Plan rozwoju, udoskonalenia i utrzymania

**Presidio Browser Anonymizer** — stan na lipiec 2026, wersja 1.4.0.
Dokument jest źródłem prawdy dla kierunku projektu. Aktualizuj go przy każdym wydaniu.

---

## 1. Stan obecny (v1.4.0)

- **Backend:** Flask + Microsoft Presidio 2.2.354 + spaCy `pl_core_news_md`, port **6677** (konfigurowalny przez `PRESIDIO_PORT`), tylko loopback (IPv4+IPv6), bez autoryzacji (świadoma decyzja: usługa wyłącznie lokalna).
- **Wtyczka Chrome:** Manifest V3, trzy mechanizmy: anonimizacja przy wklejaniu (Ctrl+V, najpewniejsza), skrót Ctrl+Shift+A, przechwycenie przycisku „Wyślij".
- **Windows dla laika:** `Uruchom-Windows.bat` (instalacja + start jednym kliknięciem, auto-instalacja Pythona przez winget), `Autostart-Windows.bat`, przewodnik `WINDOWS.md`.
- **Encje:** 28 typów, priorytet polski (PESEL, NIP, REGON, dowód, paszport) + międzynarodowe.

### Znane ograniczenia
- Logi w dashboardzie trzymają **oryginalny tekst z PII w pamięci** procesu (feature do podglądu, ale trzeba to jasno komunikować; patrz 3.2).
- Wykrywanie `PERSON`/`LOCATION` zależy od jakości modelu spaCy `md` — zdarzają się pominięcia i fałszywe trafienia.
- Przechwycenie przycisku „Wyślij" opiera się na heurystyce tekstu przycisku — kruche przy zmianach UI ChatGPT/Claude.
- Brak testów automatycznych i CI w tym repo.

---

## 2. Porządki organizacyjne (zrobić najpierw, ~1 wieczór)

Priorytet, bo obecny stan grozi utratą pracy:

1. **Naprawić bałagan katalogów na dysku.** Katalog `~/projects/personal/presidio-local-anonymizer` to w rzeczywistości repo **second-mind** (remote wskazuje `second-mind.git`) z nałożonym eksperymentalnym backendem „v2.0.0". Właściwe repo projektu jest w `~/projects/personal/presidio-anon-fresh`. Plan:
   - wyciągnąć wartościowy kod v2.0.0 (commit `4787c48`: deanonimizacja, batch, pluginy, multi-język) na osobny branch w TYM repo (`git format-patch` / kopiowanie plików),
   - przywrócić second-mind do czystego stanu (`git revert`/`reset` nakładki presidio),
   - zmienić nazwy katalogów: `presidio-anon-fresh` → `presidio-local-anonymizer`, a obecny `presidio-local-anonymizer` → `second-mind`.
2. **Klucze prywatne:** pliki `*.pem` i `*.crx` leżą luzem w starym katalogu. Nigdy nie commitować (`.gitignore` już to blokuje), przenieść `.pem` do bezpiecznego miejsca poza repo (potrzebny do aktualizacji wtyczki poza Web Store).
3. **Zacommitować i wypchnąć v1.4.0** (migracja portu + fixy + Windows one-click) — obecnie zmiany żyją tylko lokalnie.
4. **Tag `v1.4.0` + GitHub Release** z zipem wtyczki — laik pobiera Release zamiast klonować repo.

---

## 3. Udoskonalenia krótkoterminowe (v1.4.x → v1.5, horyzont 1–2 miesiące)

### 3.1 Jakość i niezawodność
- **Testy pytest** dla API (`/api/health`, `/api/anonymize`, `/api/logs`) + testy wykrywania encji na korpusie przykładów PL (PESEL z/bez separatorów, NIP z myślnikami, telefony w różnych formatach). W starym katalogu istnieją gotowe testy dla v2 — do adaptacji.
- **GitHub Actions CI:** lint (ruff) + pytest na push; job budujący zip wtyczki przy tagu.
- **Smoke-test wtyczki:** rozbudować `test-extension.html` o automatyczny scenariusz (wklej → sprawdź wynik).

### 3.2 Prywatność
- Przełącznik w dashboardzie: „loguj tylko statystyki (bez treści)" — domyślnie WŁĄCZONY; pełne logi z treścią jako opt-in.
- Przejrzeć logi backendu (obecnie logowane są typy encji, nie wartości — utrzymać tę zasadę).

### 3.3 Wykrywanie (rdzeń wartości produktu)
- Walidacja sum kontrolnych: PESEL (cyfra kontrolna + data), NIP, REGON, IBAN — podnosi precyzję z ~90% do ~100% i zabija fałszywe trafienia losowych ciągów cyfr.
- Kontekstowe wzmocnienia Presidio (`context words`: „pesel", „nip", „tel.") dla wyższych score.
- Benchmark: mini-korpus 100 zdań PL z oznaczonym PII + skrypt liczący precision/recall — bez tego każda zmiana wzorców to strzelanie w ciemno.

### 3.4 Dystrybucja
- **Chrome Web Store** — publikacja (materiały gotowe wg CHROME-WEB-STORE.md); to usuwa najtrudniejszy krok laika („Tryb dewelopera" + „Załaduj rozpakowane").
- Rozważyć **Edge Add-ons** (ten sam pakiet MV3, duży zasięg w firmach).

---

## 4. Kierunki średnioterminowe (v2.0, horyzont 3–6 miesięcy)

Fundament już istnieje w porzuconym commicie v2.0.0 (patrz pkt 2.1) — portować po kolei, każdy z testami:

1. **Pseudonimizacja spójna + de-anonimizacja:** `Jan Kowalski` → `[OSOBA_1]` (ta sama osoba = ten sam znacznik) i mapa odwrotna trzymana lokalnie, żeby odpowiedź AI dało się „odanonimizować" jednym kliknięciem. To killer-feature względem prostego maskowania.
2. **Batch API** — anonimizacja plików/wielu tekstów (podstawa pod przyszłe użycie poza przeglądarką: CLI, integracje).
3. **Multi-język** — silnik EN obok PL (Presidio wspiera to natywnie; koszt to drugi model spaCy).
4. **Pluginy encji** — własne wzorce użytkownika dodawane z dashboardu (YAML), bez dotykania kodu.
5. **Firefox** — manifest MV3 jest w ~95% kompatybilny; głównie `browser.*` vs `chrome.*`.
6. **Instalator offline/portable dla Windows** — paczka z wbudowanym Pythonem (python embeddable + wheels), zero pobierania podczas instalacji; opcjonalnie tray-app zamiast czarnego okna.

**Zasada (revenue-first, nie rozpędzać się):** przed budową pkt 2–6 potwierdzić realne użycie — najpierw pseudonimizacja + Web Store, bo to widzi użytkownik.

---

## 5. Utrzymanie (proces stały)

### Rytm kwartalny (30–60 min)
- [ ] `pip list --outdated` w venv → podnieść **presidio-analyzer/anonymizer** i **spaCy** (uwaga: nowy spaCy może wymagać nowej wersji modelu `pl_core_news_md` — zawsze test wykrywania po aktualizacji).
- [ ] Sprawdzić changelog Chrome pod kątem zmian w MV3 (deprecje API, np. losy `document.execCommand`).
- [ ] Ręczny test na 3 stronach: ChatGPT, Claude, Gmail (UI tych stron zmienia się często i psuje heurystykę przycisku „Wyślij").
- [ ] Przegląd issues na GitHubie.

### Checklist wydania (każda wersja)
1. Podbij wersję w: `chrome-extension/manifest.json`, `backend/api/health.py`, badge + stopka w `README.md`.
2. Testy przechodzą (pytest + ręczny smoke na ChatGPT).
3. Zbuduj zip wtyczki: zawartość `chrome-extension/` (bez `.pem`!), nazwa `presidio-extension-vX.Y.Z.zip`.
4. Tag `vX.Y.Z` + GitHub Release z zipem i notką zmian.
5. (Po publikacji w Web Store) upload nowej paczki w konsoli dewelopera.

### Zasady twarde
- **Nigdy** nie commitować `*.pem`, `*.crx`, logów z PII.
- Port domyślny **6677** — zmiany tylko przez `PRESIDIO_PORT` i jednocześnie we wtyczce (options).
- Backend słucha **wyłącznie na loopback** — żadnego `0.0.0.0` bez dodania autoryzacji.
- Każda zmiana wzorców encji = przebieg benchmarku precision/recall (pkt 3.3).

---

## 6. Metryki sukcesu

| Metryka | Teraz | Cel v1.5 | Cel v2.0 |
|---|---|---|---|
| Czas instalacji laika (Windows) | ~10 min (1 klik) | ~5 min (Web Store + 1 klik) | ~3 min (portable) |
| Precision na korpusie PL | brak pomiaru | ≥0.95 | ≥0.97 |
| Recall na korpusie PL | brak pomiaru | ≥0.90 | ≥0.93 |
| Testy automatyczne | 0 | API + korpus w CI | + testy wtyczki |
| Kanały dystrybucji | GitHub ZIP | + Chrome Web Store | + Edge, Firefox |
