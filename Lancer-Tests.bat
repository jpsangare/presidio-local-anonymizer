@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

rem Lance la suite de tests (hors VS Code). Arguments transmis à pytest, ex. : Lancer-Tests.bat -k api -x

set "PY=%~dp0backend\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" -c "import pytest, presidio_analyzer, flask" >nul 2>&1
if errorlevel 1 (
    echo Installation des dépendances de test...
    "%PY%" -m pip install -r backend\requirements.txt -r backend\requirements-dev.txt
    if errorlevel 1 (
        echo [ERREUR] Impossible d’installer les dépendances.
        if not defined CI pause
        exit /b 1
    )
)

"%PY%" -m pytest %*
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo [OK] Tous les tests sont passés.
) else (
    echo [ÉCHEC] Code de sortie pytest : %RC%
)

if not defined CI pause
exit /b %RC%
