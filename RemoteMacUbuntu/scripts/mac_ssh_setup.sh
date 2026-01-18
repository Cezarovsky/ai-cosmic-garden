#!/bin/bash
# Setup SSH Client pe Mac (Sora-M)
# Rulează acest script pe Mac pentru a genera SSH key și a configura conexiunea

echo "🔧 Nova Remote Development - Mac SSH Setup"
echo "=========================================="
echo ""

# Citește IP-ul Ubuntu de la user
read -p "📝 Introdu IP-ul Ubuntu (din ubuntu_ssh_setup.sh): " UBUNTU_IP
read -p "📝 Introdu username Ubuntu (probabil 'cezar'): " UBUNTU_USER

# 1. Verificare dacă există deja SSH key
if [ -f ~/.ssh/id_ed25519 ]; then
    echo "✅ SSH key ED25519 există deja: ~/.ssh/id_ed25519"
    read -p "🔄 Vrei să creezi un nou key? (y/N): " CREATE_NEW
    if [[ $CREATE_NEW == "y" || $CREATE_NEW == "Y" ]]; then
        ssh-keygen -t ed25519 -C "sora-m-to-sora-u-nova-training"
    fi
else
    echo "🔑 Generare SSH key ED25519..."
    ssh-keygen -t ed25519 -C "sora-m-to-sora-u-nova-training"
fi

# 2. Copiere key pe Ubuntu
echo ""
echo "📤 Copiere SSH key pe Ubuntu..."
echo "   (O să îți ceară parola Ubuntu)"
ssh-copy-id -i ~/.ssh/id_ed25519.pub "$UBUNTU_USER@$UBUNTU_IP"

# 3. Test conexiune
echo ""
echo "🧪 Test conexiune SSH..."
ssh -o ConnectTimeout=5 "$UBUNTU_USER@$UBUNTU_IP" "echo '✅ Conexiune SSH funcționează!' && uname -a"

# 4. Creare SSH config entry
SSH_CONFIG=~/.ssh/config
echo ""
echo "📝 Adăugare entry în ~/.ssh/config..."

# Backup existing config
if [ -f "$SSH_CONFIG" ]; then
    cp "$SSH_CONFIG" "$SSH_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Verificare dacă entry-ul există deja
if grep -q "Host nova-ubuntu" "$SSH_CONFIG" 2>/dev/null; then
    echo "⚠️  Entry 'nova-ubuntu' există deja în ~/.ssh/config"
    echo "   Verifică manual dacă IP-ul este corect"
else
    cat >> "$SSH_CONFIG" << EOF

# Nova Training - Ubuntu RTX 3090 (Sora-U)
Host nova-ubuntu
    HostName $UBUNTU_IP
    User $UBUNTU_USER
    IdentityFile ~/.ssh/id_ed25519
    ForwardAgent yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF
    echo "✅ Entry adăugat în ~/.ssh/config"
fi

# 5. Test conexiune cu alias
echo ""
echo "🎯 Test conexiune cu alias..."
ssh -o ConnectTimeout=5 nova-ubuntu "echo '✅ Alias funcționează!' && nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"

echo ""
echo "🎉 Setup complet!"
echo ""
echo "📋 Comenzi utile:"
echo "   ssh nova-ubuntu                    # Conectare la Ubuntu"
echo "   ssh nova-ubuntu 'nvidia-smi'       # Check GPU de pe Mac"
echo "   scp file.py nova-ubuntu:~/         # Copiere fișiere"
echo ""
echo "🔮 Următorul pas: Instalează VSCode Remote SSH extension"
echo "   1. Deschide VSCode pe Mac"
echo "   2. Extensions → Caută 'Remote - SSH'"
echo "   3. Instalează (Microsoft)"
echo "   4. Cmd+Shift+P → 'Remote-SSH: Connect to Host...'"
echo "   5. Alege 'nova-ubuntu'"
echo ""
