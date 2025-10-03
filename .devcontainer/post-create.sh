#!/bin/bash

# Post-create script for dev container
# This script runs after the dev container has been created and started

echo "🚀 Running post-create setup script..."

apt-get update

# Install Python 3.11 and related packages
echo "Installing Python 3.11..."
if ! command -v python3 >/dev/null 2>&1; then
    sudo apt-get install -y python3.11
fi

if ! python3 -c "import venv" >/dev/null 2>&1; then
    sudo apt-get install -y python3.11-venv
fi

# Install pip if not available
if ! command -v pip >/dev/null 2>&1; then
    sudo apt-get install -y python3-pip
fi

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
pip install -r requirements.txt

echo "Installing Node and Chrome Dev Tools"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt-get install nsolid -y
npm install chrome-devtools-mcp@latest -y

echo "✅ Post-create setup completed successfully!"
echo "📦 Installed: Python 3.11, pip packages, Node.js, and Chrome DevTools MCP"
echo "🐍 Python virtual environment created at: ./venv"
echo "💡 To activate the virtual environment manually: source venv/bin/activate"