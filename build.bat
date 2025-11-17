@echo off
REM ============================================
REM Space Aces Companion - build.bat
REM Project root:  C:\Users\joshu\Desktop\Space Aces Companion
REM main.py:       app\main.py
REM npcs.json:     app\data\npcs.json
REM ============================================

REM In das Verzeichnis der .bat wechseln
cd /d "%~dp0"

echo Building Space Aces Companion EXE...
echo.

SET VENV_PY=venv\Scripts\python.exe

IF NOT EXIST "%VENV_PY%" (
    echo ERROR: Could not find venv\Scripts\python.exe
    pause
    exit /b
)

IF NOT EXIST "app\main.py" (
    echo ERROR: Could not find app\main.py
    pause
    exit /b
)

IF NOT EXIST "app\data\npcs.json" (
    echo ERROR: Could not find app\data\npcs.json
    pause
    exit /b
)

echo Using Python from: %VENV_PY%
echo.

REM Alte Build-Artefakte im Root löschen
if exist dist (
    echo Removing old root dist folder...
    rmdir /S /Q dist
)
if exist build (
    echo Removing old root build folder...
    rmdir /S /Q build
)
if exist SpaceAcesCompanion.spec (
    echo Removing old root spec file...
    del /Q SpaceAcesCompanion.spec
)

REM Alte Build-Artefakte in app/ löschen (falls vorhanden)
if exist app\dist (
    echo Removing old app\dist folder...
    rmdir /S /Q app\dist
)
if exist app\build (
    echo Removing old app\build folder...
    rmdir /S /Q app\build
)
if exist app\SpaceAcesCompanion.spec (
    echo Removing old app\SpaceAcesCompanion.spec...
    del /Q app\SpaceAcesCompanion.spec
)

echo.
echo Running PyInstaller from app\ ...
echo.

pushd app

"..\venv\Scripts\python.exe" -m PyInstaller ^
    --onefile ^
    --noconfirm ^
    --name "SpaceAcesCompanion" ^
    main.py

popd

echo.
echo Copying EXE and npcs.json to root dist\ ...
echo.

mkdir dist >nul 2>&1

IF NOT EXIST "app\dist\SpaceAcesCompanion.exe" (
    echo ERROR: app\dist\SpaceAcesCompanion.exe not found. PyInstaller build failed.
    pause
    exit /b
)

copy /Y "app\dist\SpaceAcesCompanion.exe" "dist\SpaceAcesCompanion.exe" >nul
copy /Y "app\data\npcs.json" "dist\npcs.json" >nul

echo --------------------------------------------
echo Build finished.
echo EXE:  dist\SpaceAcesCompanion.exe
echo JSON: dist\npcs.json
echo --------------------------------------------
echo.
pause
