#!/bin/bash
# Build script for Monte Carlo 2-Stream RT Demo
# Creates a standalone executable using PyInstaller

echo "🦁 Building Monte Carlo 2-Stream RT Demo..."
echo "============================================"

# Activate virtual environment
source .venv/bin/activate

# Install PyInstaller if not already installed
if ! command -v pyinstaller &> /dev/null; then
    echo "🐸 Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🦊 Cleaning previous builds..."
rm -rf build dist

# Build with PyInstaller
echo "🐻 Building executable..."
pyinstaller mc2s_app.spec

# Check if build was successful
if [ -d "dist/MC2S_Demo.app" ]; then
    echo ""
    echo "✅ Build successful!"
    echo "============================================"
    echo "🦎 macOS App Bundle created at:"
    echo "   dist/MC2S_Demo.app"
    echo ""
    echo "To run the app:"
    echo "   open dist/MC2S_Demo.app"
    echo ""
    echo "To distribute:"
    echo "   1. Compress: zip -r MC2S_Demo.zip dist/MC2S_Demo.app"
    echo "   2. Share the .zip file with students"
    echo "   3. Users extract and double-click to run"
    echo "============================================"
elif [ -f "dist/MC2S_Demo" ]; then
    echo ""
    echo "✅ Build successful!"
    echo "============================================"
    echo "🦎 Executable created at:"
    echo "   dist/MC2S_Demo"
    echo ""
    echo "To run:"
    echo "   ./dist/MC2S_Demo"
    echo "============================================"
else
    echo ""
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi
