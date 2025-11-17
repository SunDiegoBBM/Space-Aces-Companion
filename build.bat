@echo off
echo Building Space Aces Companion...

REM Activate venv
call venv\Scripts\activate

REM Remove old build
echo Cleaning old build...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del SpaceAcesCompanion.spec 2>nul

REM Build EXE without console window
pyinstaller --noconfirm --onefile --windowed --name SpaceAcesCompanion --paths ".\app" --collect-submodules sac_pages app\main.py

echo.
echo Build finished!
echo You can find SpaceAcesCompanion.exe in:
echo %cd%\dist\
pause
