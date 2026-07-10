@echo off
REM ============================================================
REM  Presidio Browser Anonymizer - Autostart dla Windows
REM  Kliknij dwa razy: backend bedzie startowal sam (w tle)
REM  przy kazdym wlaczeniu komputera.
REM  Kliknij ponownie, aby autostart WYLACZYC.
REM ============================================================
setlocal EnableExtensions
title Presidio Anonymizer - Autostart
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS=%STARTUP%\PresidioAnonymizer.vbs"

if exist "%VBS%" goto :remove

> "%VBS%" echo Set sh = CreateObject("WScript.Shell")
>> "%VBS%" echo sh.CurrentDirectory = "%~dp0"
>> "%VBS%" echo sh.Run """%~dp0Uruchom-Windows.bat""", 0, False

echo [OK] Autostart WLACZONY.
echo Backend bedzie uruchamial sie automatycznie (w tle) po wlaczeniu komputera.
echo.
echo Aby wylaczyc autostart - kliknij ten plik jeszcze raz.
echo.
pause
exit /b 0

:remove
del "%VBS%"
echo [OK] Autostart WYLACZONY.
echo Od teraz backend uruchamiasz recznie plikiem Uruchom-Windows.bat.
echo.
pause
exit /b 0
