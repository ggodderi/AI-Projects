# PowerShell script to build a standalone executable using PyInstaller
# Usage: run from repository folder in PowerShell after activating your venv

pyinstaller --onefile --add-data "assets;assets" space_invaders.py --name SpaceInvaders

Write-Host "Build complete. See dist\SpaceInvaders.exe"
