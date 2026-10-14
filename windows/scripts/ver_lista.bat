@echo off
REM Abre mpv con una lista de la carpeta listas\ :  ver_lista.bat "Rakuten TV"
cd /d "%~dp0.."

if "%~1"=="" (
    echo Uso: ver_lista.bat "Nombre de la lista"
    pause
    exit /b 1
)
if not exist "listas\%~1.m3u" (
    echo No existe listas\%~1.m3u
    pause
    exit /b 1
)

where mpv.exe >nul 2>&1
if %errorlevel% equ 0 (
    start "" mpv.exe "listas\%~1.m3u"
    exit /b 0
)
if exist "%PROGRAMFILES%\MPV Player\mpv.exe" (
    start "" "%PROGRAMFILES%\MPV Player\mpv.exe" "listas\%~1.m3u"
    exit /b 0
)
echo No encuentro mpv.exe
pause
exit /b 1
