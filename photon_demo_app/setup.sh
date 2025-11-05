#!/bin/bash
# Setup script for Real-Time Photon Animation Demo

echo "🐊 Setting up Real-Time Photon Animation Demo..."
echo "================================================"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Create venv
echo "🦎 Creating virtual environment..."
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Upgrade pip
echo "🐸 Upgrading pip..."
pip install --upgrade pip

# Install
echo "🦊 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo "================================================"
echo "🐻 To run the demo:"
echo "   source .venv/bin/activate"
echo "   python src/photon_demo.py"
echo "================================================"
