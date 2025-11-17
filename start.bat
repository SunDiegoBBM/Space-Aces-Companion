@echo off
cd /d "%~dp0app"

REM Virtuelle Umgebung aktivieren
call "..\venv\Scripts\activate.bat"

REM App starten
python main.py

REM Venv wieder deaktivieren
call "..\venv\Scripts\deactivate.bat"
pause >nul