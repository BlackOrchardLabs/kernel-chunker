# Kernel Chunker - Build Script
# Creates a standalone .exe using PyInstaller

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  KERNEL CHUNKER - Build Script" -ForegroundColor Cyan
Write-Host "  Black Orchard Labs" -ForegroundColor DarkGray
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check for PyInstaller
Write-Host "[1/4] Checking PyInstaller..." -ForegroundColor Yellow
$pyinstaller = pip show pyinstaller 2>$null
if (-not $pyinstaller) {
    Write-Host "      Installing PyInstaller..." -ForegroundColor Gray
    pip install pyinstaller
}
Write-Host "      PyInstaller ready" -ForegroundColor Green

# Check for PyQt6
Write-Host "[2/4] Checking PyQt6..." -ForegroundColor Yellow
$pyqt = pip show pyqt6 2>$null
if (-not $pyqt) {
    Write-Host "      Installing PyQt6..." -ForegroundColor Gray
    pip install pyqt6
}
Write-Host "      PyQt6 ready" -ForegroundColor Green

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$mainScript = Join-Path $scriptDir "kernel_chunker.pyw"
$assetsDir = Join-Path $scriptDir "assets"
$distDir = Join-Path $scriptDir "dist"

# Build the exe
Write-Host "[3/4] Building executable..." -ForegroundColor Yellow
Write-Host "      This may take a minute..." -ForegroundColor Gray

Push-Location $scriptDir

# PyInstaller command
$pyinstallerArgs = @(
    "--onefile",
    "--windowed",
    "--name=KernelChunker",
    "--icon=assets/icon.ico",
    "--add-data=assets;assets",
    "--noconsole",
    "kernel_chunker.pyw"
)

# Check if icon exists, if not remove that arg
$iconPath = Join-Path $assetsDir "icon.ico"
if (-not (Test-Path $iconPath)) {
    $pyinstallerArgs = $pyinstallerArgs | Where-Object { $_ -notlike "--icon=*" }
}

# Run PyInstaller
python -m PyInstaller $pyinstallerArgs

Pop-Location

# Check if build succeeded
$exePath = Join-Path $distDir "KernelChunker.exe"
if (Test-Path $exePath) {
    Write-Host "[4/4] Build complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "  SUCCESS!" -ForegroundColor Green
    Write-Host "  Executable: $exePath" -ForegroundColor White
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""

    # Ask to open folder
    $openFolder = Read-Host "Open output folder? (y/n)"
    if ($openFolder -eq 'y') {
        explorer.exe $distDir
    }
} else {
    Write-Host "[4/4] Build failed!" -ForegroundColor Red
    Write-Host "      Check the output above for errors" -ForegroundColor Gray
}
