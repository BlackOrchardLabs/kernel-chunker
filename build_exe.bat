@echo off
echo ======================================
echo   KERNEL CHUNKER - Build Script
echo   Black Orchard Labs
echo ======================================
echo.

echo [1/4] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo       Installing PyInstaller...
    pip install pyinstaller
)
echo       PyInstaller ready

echo [2/4] Checking PyQt6...
pip show pyqt6 >nul 2>&1
if errorlevel 1 (
    echo       Installing PyQt6...
    pip install pyqt6
)
echo       PyQt6 ready

echo [3/4] Building executable...
echo       This may take a minute...

cd /d "%~dp0"
python -m PyInstaller --onefile --windowed --name=KernelChunker --add-data "assets;assets" --noconsole kernel_chunker.pyw

echo.
if exist "dist\KernelChunker.exe" (
    echo [4/4] Build complete!
    echo.
    echo ======================================
    echo   SUCCESS!
    echo   Executable: %~dp0dist\KernelChunker.exe
    echo ======================================
    echo.
    explorer.exe "%~dp0dist"
) else (
    echo [4/4] Build failed!
    echo       Check the output above for errors
)

pause
