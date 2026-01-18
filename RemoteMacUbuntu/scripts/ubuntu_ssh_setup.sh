#!/bin/bash
# Setup SSH Server pe Ubuntu (Sora-U)
# Rulează acest script pe mașina Ubuntu cu RTX 3090

echo "🔧 Nova Remote Development - Ubuntu SSH Setup"
echo "=============================================="
echo ""

# 1. Update package list
echo "📦 Actualizare pachete..."
sudo apt update

# 2. Install OpenSSH Server
echo "🔐 Instalare OpenSSH Server..."
sudo apt install -y openssh-server

# 3. Start și enable SSH service
echo "🚀 Pornire SSH service..."
sudo systemctl start ssh
sudo systemctl enable ssh

# 4. Verificare status
echo ""
echo "✅ Status SSH service:"
sudo systemctl status ssh --no-pager | head -n 10

# 5. Configurare firewall (dacă e activ)
echo ""
echo "🔥 Configurare firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow ssh
    sudo ufw status
fi

# 6. Afișare IP address
echo ""
echo "🌐 IP Address Ubuntu:"
hostname -I | awk '{print $1}'
echo ""
echo "📋 Informații conexiune:"
echo "   Username: $(whoami)"
echo "   IP: $(hostname -I | awk '{print $1}')"
echo "   Port: 22 (default)"
echo ""
echo "✨ SSH Server gata! Următorul pas: rulează ubuntu_test_connection.sh pe Mac"
