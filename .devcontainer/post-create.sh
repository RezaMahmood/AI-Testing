#!/bin/bash

# Post-create script for Python dev container
# This script runs after the dev container has been created and started

echo "🚀 Running Python-focused post-create setup script..."

# Update package lists
sudo apt-get update

# Create virtual environment and install Python packages
echo "Setting up Python virtual environment and installing packages..."
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install requirements
echo "Installing Python packages from requirements.txt..."
source venv/bin/activate
pip install --upgrade pip

# Install Python requirements if they exist
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Python packages installed from requirements.txt"
else
    echo "⚠️ No requirements.txt found, skipping Python package installation"
fi

echo "Installing Chrome Dev Tools MCP..."
npm install chrome-devtools-mcp@latest

echo "✅ Post-create setup completed successfully!"
echo "📦 Installed: Python packages, Node.js 20, and Chrome DevTools MCP"
echo "🐍 Python virtual environment created at: ./venv"
echo "💡 To activate the virtual environment manually: source venv/bin/activate"
echo "🧪 To run tests: pytest --tb=short --verbose"