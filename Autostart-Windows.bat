@echo off
chcp 65001 >nul
REM ============================================================
REM  MasqueIA - démarrage automatique sous Windows
REM  Double-cliquez : le backend démarrera en arrière-plan
REM  à chaque démarrage de l’ordinateur.
REM  Double-cliquez à nouveau pour désactiver le démarrage automatique.
REM ============================================================
setlocal EnableExtensions
title Presidio Anonymizer - Autostart
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS=%STARTUP%\PresidioAnonymizer.vbs"

if exist "%VBS%" goto :remove

> "%VBS%" echo Set sh = CreateObject("WScript.Shell")
>> "%VBS%" echo sh.CurrentDirectory = "%~dp0"
>> "%VBS%" echo sh.Run """%~dp0Uruchom-Windows.bat""", 0, False

echo [OK] Démarrage automatique ACTIVÉ.
echo Le backend démarrera automatiquement en arrière-plan après le démarrage de Windows.
echo.
echo Pour désactiver le démarrage automatique, cliquez à nouveau sur ce fichier.
echo.
pause
exit /b 0

:remove
del "%VBS%"
echo [OK] Démarrage automatique DÉSACTIVÉ.
echo Vous pouvez maintenant démarrer le backend manuellement avec Uruchom-Windows.bat.
echo.
pause
exit /b 0
