#!/bin/bash
# Setup script for Monte Carlo 2-Stream RT Demo
# Creates virtual environment and installs dependencies

echo "🐊 Setting up Monte Carlo 2-Stream RT Demo..."
echo "==============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Create virtual environment
echo "🦎 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo "🐸 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "🦊 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo "==============================================="
echo "🐻 To run the app:"
echo "   source .venv/bin/activate"
echo "   python src/mc2s_gui.py"
echo ""
echo "🦁 To build standalone executable:"
echo "   ./build.sh"
echo "==============================================="
