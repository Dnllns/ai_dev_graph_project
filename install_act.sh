#!/bin/bash
# Script para instalar act localmente sin sudo

set -e

echo "Installing act to ~/.local/bin..."

# Create local bin directory if it doesn't exist
mkdir -p ~/.local/bin

# Download and extract act
curl -L https://github.com/nektos/act/releases/latest/download/act_Linux_x86_64.tar.gz -o /tmp/act.tar.gz
tar -xzf /tmp/act.tar.gz -C /tmp
mv /tmp/act ~/.local/bin/act
chmod +x ~/.local/bin/act
rm /tmp/act.tar.gz

echo "act installed successfully to ~/.local/bin/act"
echo "Make sure ~/.local/bin is in your PATH"
echo ""
echo "Add this to your ~/.bashrc or ~/.zshrc if not already present:"
echo 'export PATH="$HOME/.local/bin:$PATH"'
