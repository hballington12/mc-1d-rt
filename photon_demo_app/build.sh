#!/bin/bash
# Build script for 2-Stream RT Photon Demo
# Creates a standalone executable using PyInstaller

echo "🦊 Building 2-Stream RT Photon Demo..."
echo "========================================"

# Check if we're in the right directory
if [ ! -f "photon_demo.spec" ]; then
    echo "❌ Error: photon_demo.spec not found!"
    echo "   Please run this script from the photon_demo_app directory"
    exit 1
fi

# Activate virtual environment (use mc2s_app venv since it has pygame-ce)
if [ -d "../mc2s_app/.venv" ]; then
    echo "🐻 Using mc2s_app virtual environment..."
    source ../mc2s_app/.venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🐻 Using local virtual environment..."
    source .venv/bin/activate
else
    echo "❌ Error: No virtual environment found!"
    exit 1
fi

# Install PyInstaller if not present
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Build with PyInstaller
echo "🔨 Building executable..."
pyinstaller photon_demo.spec

# Check if build was successful
if [ -d "dist/PhotonDemo.app" ]; then
    echo ""
    echo "✅ Build successful!"
    echo "========================================"
    echo "🎉 macOS App Bundle created at:"
    echo "   dist/PhotonDemo.app"
    echo ""
    echo "To run the app:"
    echo "   open dist/PhotonDemo.app"
    echo ""
    echo "To distribute:"
    echo "   cd dist"
    echo "   zip -r PhotonDemo.zip PhotonDemo.app"
    echo "   Share PhotonDemo.zip with users"
    echo "========================================"
elif [ -f "dist/PhotonDemo" ]; then
    echo ""
    echo "✅ Build successful!"
    echo "========================================"
    echo "🎉 Linux executable created at:"
    echo "   dist/PhotonDemo"
    echo ""
    echo "To run:"
    echo "   ./dist/PhotonDemo"
    echo "========================================"
else
    echo ""
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi
