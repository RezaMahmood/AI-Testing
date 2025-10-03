#!/bin/bash

# Post-create script for dev container
# This script runs after the dev container has been created and started

echo "🚀 Running post-create setup script..."

apt-get update


# Check if Chromium is installed before installing
if ! command -v chromium >/dev/null 2>&1; then
    echo "📦 Installing Chromium browser..."
    sudo apt-get install -y chromium chromium-driver
else
    echo "✅ Chromium is already installed"
    # Optionally check if chromium-driver is also available
    if ! command -v chromedriver >/dev/null 2>&1 && ! command -v chromium-driver >/dev/null 2>&1; then
        echo "📦 Installing Chromium driver..."
        sudo apt-get install -y chromium-driver
    fi
fi



if ! command -v python3 >/dev/null 2>&1; then
    sudo apt-get install -y python3.11
fi

if ! python3 -c "import venv" >/dev/null 2>&1; then
    sudo apt-get install -y python3.11-venv
fi

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r tests/requirements.txt

echo "Installing Node and Chrome Dev Tools"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt-get install nsolid -y
npx chrome-devtools-mcp@latest --help

echo "✅ Post-create setup completed successfully!"