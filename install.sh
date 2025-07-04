#!/bin/bash

# CylMesh Installation Script
# This script installs CylMesh and its dependencies

echo "🔧 CylMesh Installation Script"
echo "=============================="

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -d "cylmesh" ]; then
    echo "❌ Error: This script must be run from the project root directory."
    echo ""
    echo "If you cloned from git:"
    echo "  cd cylmesh"
    echo "  ./install.sh"
    echo ""
    echo "If you downloaded the source:"
    echo "  cd path/to/cylmesh"
    echo "  ./install.sh"
    exit 1
fi

echo "✅ Found CylMesh package files"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is required but not installed."
    echo "Please install pip and try again."
    exit 1
fi

# Use pip3 if available, otherwise pip
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "✅ pip found: $PIP_CMD"

# Check if Gmsh is installed
if command -v gmsh &> /dev/null; then
    echo "✅ Gmsh found: $(gmsh --version 2>&1 | head -n1)"
else
    echo "⚠️  Gmsh not found!"
    echo ""
    echo "Gmsh is required for CylMesh to work. Please install it:"
    echo ""
    echo "macOS (with Homebrew):"
    echo "  brew install gmsh"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt-get install gmsh"
    echo ""
    echo "Windows:"
    echo "  Download from: https://gmsh.info/#Download"
    echo ""
    echo "You can continue with the installation, but CylMesh won't work without Gmsh."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📦 Installing CylMesh..."

# Install the package
if $PIP_CMD install -e .; then
    echo "✅ CylMesh installed successfully!"
    echo ""
    echo "🚀 Quick test:"
    echo "  cylmesh --help"
    echo ""
    echo "📖 Example usage:"
    echo "  cylmesh --layers 2.0 1.0 2.0 --layer-names 'FM1' 'Spacer' 'FM2'"
    echo ""
    echo "Happy meshing! 🎯✨"
else
    echo "❌ Installation failed!"
    echo "Please check the error messages above and try again."
    exit 1
fi
