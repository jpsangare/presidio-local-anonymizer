@echo off
REM ============================================================
REM  Presidio Browser Anonymizer - Windows (wszystko w jednym)
REM  Pierwsze uruchomienie: instaluje wszystko automatycznie.
REM  Kolejne uruchomienia: od razu startuje backend.
REM  Wystarczy KLIKNAC DWA RAZY ten plik.
REM ============================================================
setlocal EnableExtensions
title Presidio Anonymizer
cd /d "%~dp0"

set "PORT=6677"
set "VENV_PY=%~dp0backend\.venv\Scripts\python.exe"
set "MARKER=%~dp0backend\.venv\install-ok.txt"

echo ============================================================
echo  Presidio Browser Anonymizer
echo ============================================================
echo.

REM ---------- 1. Znajdz Pythona (py launcher lub python) ----------
set "PY_CMD="
py -3 --version >nul 2>&1 && set "PY_CMD=py -3"
if not defined PY_CMD (
    python --version >nul 2>&1 && set "PY_CMD=python"
)

if defined PY_CMD goto :python_ok

echo [INFO] Python nie jest zainstalowany. Probuje zainstalowac automatycznie...
winget --version >nul 2>&1
if %errorlevel% neq 0 goto :python_manual

echo [INFO] Instaluje Python przez winget (moze potrwac kilka minut)...
winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
if %errorlevel% neq 0 goto :python_manual

echo.
echo [OK] Python zainstalowany!
echo [WAZNE] Zamknij to okno i kliknij plik Uruchom-Windows.bat JESZCZE RAZ.
echo         (Windows musi odswiezyc ustawienia po instalacji Pythona)
echo.
pause
exit /b 0

:python_manual
echo.
echo [BLAD] Nie udalo sie zainstalowac Pythona automatycznie.
echo.
echo Zrob to recznie (2 minuty):
echo   1. Otworzy sie strona www.python.org - kliknij zolty przycisk "Download Python"
echo   2. Uruchom pobrany plik
echo   3. WAZNE: zaznacz na dole "Add Python to PATH", potem "Install Now"
echo   4. Po instalacji kliknij Uruchom-Windows.bat jeszcze raz
echo.
start "" https://www.python.org/downloads/
pause
exit /b 1

:python_ok
echo [OK] Python znaleziony:
%PY_CMD% --version
echo.

REM ---------- 2. Pierwsza instalacja (tylko raz) ----------
if exist "%MARKER%" goto :run_backend

echo ============================================================
echo  PIERWSZE URUCHOMIENIE - instaluje wszystko automatycznie.
echo  To potrwa 5-10 minut i wymaga internetu. Nie zamykaj okna!
echo ============================================================
echo.

if not exist "%VENV_PY%" (
    echo [1/3] Tworze srodowisko Pythona...
    %PY_CMD% -m venv "%~dp0backend\.venv"
    if errorlevel 1 (
        echo [BLAD] Nie udalo sie utworzyc srodowiska. Sprobuj ponownie.
        pause
        exit /b 1
    )
)
echo [OK] Srodowisko gotowe
echo.

echo [2/3] Pobieram biblioteki (Presidio, Flask, spaCy)...
"%VENV_PY%" -m pip install --upgrade pip --quiet
"%VENV_PY%" -m pip install -r "%~dp0backend\requirements.txt"
if errorlevel 1 (
    echo [BLAD] Instalacja bibliotek nie powiodla sie. Sprawdz internet i sprobuj ponownie.
    pause
    exit /b 1
)
echo [OK] Biblioteki zainstalowane
echo.

echo [3/3] Pobieram polski model jezykowy (ok. 80 MB)...
"%VENV_PY%" -m spacy download pl_core_news_md
if errorlevel 1 (
    echo [BLAD] Nie udalo sie pobrac modelu. Sprawdz internet i sprobuj ponownie.
    pause
    exit /b 1
)
echo [OK] Model pobrany
echo.

echo instalacja-zakonczona> "%MARKER%"
echo ============================================================
echo  INSTALACJA ZAKONCZONA! Uruchamiam program...
echo ============================================================
echo.

REM ---------- 3. Start backendu + otwarcie dashboardu ----------
:run_backend
echo ============================================================
echo  BACKEND STARTUJE na http://localhost:%PORT%
echo  Dashboard otworzy sie sam w przegladarce za chwile.
echo.
echo  NIE ZAMYKAJ TEGO OKNA gdy korzystasz z anonimizacji!
echo  (mozesz je zminimalizowac)
echo  Aby zatrzymac: zamknij okno lub nacisnij Ctrl+C
echo ============================================================
echo.

start "" /min cmd /c "timeout /t 8 /nobreak >nul & start "" http://localhost:%PORT%/dashboard"

cd /d "%~dp0backend"
"%VENV_PY%" app.py

pause
