@echo off
REM Abre mpv con la lista maestra (TDT + iptv-org, comprobada y sin repetidos).
REM Para regenerarla:  venv\Scripts\python scripts\actualizar.py

cd /d "%~dp0.."

if not exist "datos\canales_maestra.m3u" (
    echo No existe datos\canales_maestra.m3u
    echo Genera la lista con scripts\actualizar.py
    pause
    exit /b 1
)

where mpv.exe >nul 2>&1
if %errorlevel% equ 0 (
    start "" mpv.exe "datos\canales_maestra.m3u"
    exit /b 0
)

if exist "%PROGRAMFILES%\MPV Player\mpv.exe" (
    start "" "%PROGRAMFILES%\MPV Player\mpv.exe" "datos\canales_maestra.m3u"
    exit /b 0
)

echo No encuentro mpv.exe. Instalalo con: winget install shinchiro.mpv
pause
exit /b 1
