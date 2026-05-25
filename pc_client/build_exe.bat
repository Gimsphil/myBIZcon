@echo off
REM ===========================================================================
REM  myBIZcon PC Desktop Client - PyInstaller EXE Builder
REM  AGY Step 17: Auto-build script for single-file Windows EXE distribution
REM ===========================================================================
REM  Usage: Double-click build_exe.bat OR run from command line.
REM  Output: dist\myBIZcon.exe
REM ===========================================================================

echo.
echo ============================================================
echo   myBIZcon PC Desktop Client - EXE Build Tool (Step 17)
echo   Role: AGY (1st Coder) / Reviewed by: Antigravity
echo ============================================================
echo.

REM Move to the script's own directory (pc_client/)
cd /d %~dp0

REM Step 1: Check Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)
echo [OK] Python found.

REM Step 2: Install / upgrade PyInstaller
echo [Step 1/3] Installing PyInstaller...
pip install --upgrade pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] pip install had issues. Attempting to continue...
)
echo [OK] PyInstaller ready.

REM Step 3: Clean previous build artifacts
echo [Step 2/3] Cleaning previous build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist"  rmdir /s /q "dist"
echo [OK] Build directories cleaned.

REM Step 4: Run PyInstaller with the build spec
echo [Step 3/3] Building EXE with PyInstaller...
pyinstaller pyinstaller_build.spec --clean --noconfirm

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PyInstaller build FAILED. Check output above for details.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   BUILD SUCCESSFUL!
echo   Output: %~dp0dist\myBIZcon.exe
echo ============================================================
echo.
echo You can now distribute dist\myBIZcon.exe as a standalone PC client.
echo.

pause
