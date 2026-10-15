@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3.10 -c "import sys" >nul 2>&1
    if errorlevel 1 (
        py -m venv .venv
    ) else (
        py -3.10 -m venv .venv
    )
    if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -c "import sys; assert sys.version_info >= (3,10); import pygame" >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --timeout 30 --retries 1 -r requirements.txt
    if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" scorched_earth.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo.
echo The game could not start. Check the error above.
echo Requires Python 3.10 or newer. First-time setup requires internet access.
pause
exit /b 1
