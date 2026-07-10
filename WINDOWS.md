# 🪟 Windows — instalacja dla każdego (bez wiedzy technicznej)

Ten przewodnik jest dla osób, które **nie są programistami**. Nie potrzebujesz gita, terminala ani żadnej wiedzy technicznej. Całość to **3 kroki i około 10 minut** (tylko za pierwszym razem — potem uruchomienie zajmuje kilka sekund).

---

## Co będziesz mieć na końcu?

Gdy wkleisz do ChatGPT, Claude albo Gmaila tekst z danymi osobowymi (PESEL, e-mail, telefon, numer karty…), wtyczka **automatycznie je zamaskuje**, zanim trafią do internetu. Wszystko dzieje się na Twoim komputerze — żadne dane nie wychodzą na zewnątrz.

---

## Krok 1: Pobierz program (2 minuty)

1. Wejdź na stronę: **https://github.com/gacabartosz/presidio-local-anonymizer**
2. Kliknij zielony przycisk **„Code"**, a potem **„Download ZIP"**
3. Otwórz folder **Pobrane** i kliknij prawym przyciskiem na pobrany plik → **„Wyodrębnij wszystkie…"** → **„Wyodrębnij"**
4. Otworzy się folder `presidio-local-anonymizer-main` — zostaw go otwarty

> 💡 **Wskazówka:** przenieś ten folder np. do `Dokumenty`, żeby przypadkiem go nie skasować. Program działa z tego folderu.

## Krok 2: Uruchom program (pierwszy raz: 5–10 minut)

1. W folderze znajdź plik **`Uruchom-Windows`** (typ: plik wsadowy Windows) i **kliknij go dwa razy**
2. Jeśli Windows pokaże niebieskie okno „System Windows ochronił ten komputer":
   kliknij **„Więcej informacji"** → **„Uruchom mimo to"** (program jest bezpieczny — cały kod jest publiczny na GitHub)
3. Czarne okno zrobi wszystko samo:
   - sprawdzi, czy masz Pythona (jeśli nie — zainstaluje go automatycznie; czasem poprosi, żeby kliknąć plik jeszcze raz)
   - pobierze potrzebne biblioteki i polski model językowy
   - uruchomi program i **samo otworzy panel w przeglądarce**
4. Gdy zobaczysz w przeglądarce panel (Dashboard) — działa! ✅

> ⚠️ **Nie zamykaj czarnego okna**, gdy korzystasz z anonimizacji. Możesz je zminimalizować.
>
> Przy **kolejnych** uruchomieniach ten sam plik startuje program w kilka sekund (nic już nie instaluje).

## Krok 3: Zainstaluj wtyczkę w Chrome (2 minuty)

1. Otwórz Chrome i wpisz w pasku adresu: `chrome://extensions/`
2. Włącz przełącznik **„Tryb dewelopera"** (prawy górny róg)
3. Kliknij **„Załaduj rozpakowane"**
4. Wskaż folder **`chrome-extension`** (jest w folderze programu z Kroku 1)
5. Gotowe! Ikona wtyczki pojawi się obok paska adresu

---

## Sprawdź, czy działa (30 sekund)

1. Skopiuj ten tekst:
   ```
   Jan Kowalski, PESEL: 92010212345, email: jan@example.com, tel: +48 123 456 789
   ```
2. Wejdź na https://chatgpt.com i wklej go (Ctrl+V) w okno rozmowy
3. Powinno pojawić się: `Jan Kowalski, PESEL: [PESEL], email: [EMAIL], tel: [TELEFON]` ✅

---

## Autostart (opcjonalnie)

Chcesz, żeby program włączał się sam po uruchomieniu komputera (w tle, bez czarnego okna)?

- Kliknij dwa razy plik **`Autostart-Windows`** → autostart WŁĄCZONY
- Kliknij go ponownie → autostart WYŁĄCZONY

---

## Najczęstsze problemy

| Problem | Rozwiązanie |
|---|---|
| Wtyczka pokazuje „Offline" | Program nie jest uruchomiony — kliknij `Uruchom-Windows` |
| „System Windows ochronił ten komputer" | „Więcej informacji" → „Uruchom mimo to" |
| Okno mignęło i zniknęło | Kliknij plik jeszcze raz; jeśli się powtarza, uruchom ponownie komputer i spróbuj znowu |
| Instalacja Pythona się nie udała | Wejdź na https://www.python.org/downloads/, pobierz Pythona, **zaznacz „Add Python to PATH"** przy instalacji, potem kliknij `Uruchom-Windows` jeszcze raz |
| Tekst się nie maskuje | Kliknij ikonę wtyczki i sprawdź, czy przełącznik jest WŁĄCZONY; odśwież stronę (F5) |
| Chcę zobaczyć, co zostało zamaskowane | Otwórz http://localhost:6677/dashboard → zakładka „Logi" |

Więcej pomocy: [JAK-ZACZĄĆ.md](JAK-ZACZĄĆ.md) • [INSTALLATION.md](INSTALLATION.md)
