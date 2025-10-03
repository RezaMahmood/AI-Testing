#!/bin/bash

# Post-create script for dev container
# This script runs after the dev container has been created and started

echo "🚀 Running post-create setup script..."

apt-get update

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


echo "Installing Node and Chrome Dev Tools"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt-get install nsolid -y
npm install chrome-devtools-mcp@latest -y

echo "✅ Post-create setup completed successfully!"