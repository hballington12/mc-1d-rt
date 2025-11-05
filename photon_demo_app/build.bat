@echo off
REM Build script for 2-Stream RT Photon Demo (Windows)
REM Creates a standalone executable using PyInstaller

echo Building 2-Stream RT Photon Demo...
echo ========================================

REM Check if we're in the right directory
if not exist "photon_demo.spec" (
    echo Error: photon_demo.spec not found!
    echo Please run this script from the photon_demo_app directory
    exit /b 1
)

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo Using local virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found!
    echo Please create a venv and install requirements first
    exit /b 1
)

REM Install PyInstaller if not present
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build with PyInstaller
echo Building executable...
pyinstaller photon_demo.spec

REM Check if build was successful
if exist "dist\PhotonDemo.exe" (
    echo.
    echo Build successful!
    echo ========================================
    echo Executable created at:
    echo    dist\PhotonDemo.exe
    echo.
    echo To run:
    echo    dist\PhotonDemo.exe
    echo.
    echo To distribute:
    echo    1. Copy the entire dist folder
    echo    2. Share with users
    echo    3. Users can run PhotonDemo.exe
    echo ========================================
) else (
    echo.
    echo Build failed! Check the output above for errors.
    exit /b 1
)

pause
