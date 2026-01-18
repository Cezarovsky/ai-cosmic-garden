# 🔗 Nova Remote Development - Connection Info

**Generated:** 2026-01-18  
**Ubuntu Machine:** Sora-U (RTX 3090)

---

## 📋 Connection Details

```
IP Address:  192.168.0.207
Username:    cezar
SSH Key:     ~/.ssh/id_ed25519 (already generated)
Port:        22 (default)
```

---

## 🚀 Setup pe Mac (Sora-M)

### 1. Copiază SSH Key pe Mac

**Cheia publică (să adaugi în ~/.ssh/authorized_keys pe Mac dacă dorești și Mac → Ubuntu):**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPIbn4+dq4V3dZrnu7p2tbELNtF0oKuCeHJ684FZzOnb cezar@nova-ubuntu
```

**DAR:** Dacă vrei sa lucrezi de pe Mac → Ubuntu, trebuie să:
1. Generezi SSH key PE MAC (dacă nu ai)
2. Copiezi cheia publică de pe Mac pe Ubuntu

**Sau:** Poți copia cheia PRIVATĂ de pe Ubuntu pe Mac (mai simplu, dar mai puțin sigur):
```bash
# Pe Ubuntu - afișează cheia privată
cat ~/.ssh/id_ed25519

# Pe Mac - salvează în ~/.ssh/id_ed25519_nova
# Apoi: chmod 600 ~/.ssh/id_ed25519_nova
```

### 2. Adaugă în ~/.ssh/config pe Mac

```bash
# Pe Mac, editează: nano ~/.ssh/config

# Adaugă:
Host nova-ubuntu
    HostName 192.168.0.207
    User cezar
    IdentityFile ~/.ssh/id_ed25519_nova  # sau ~/.ssh/id_ed25519 dacă ai generat pe Mac
    ForwardAgent yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    
    # Optional: Port forwarding automat
    LocalForward 5432 localhost:5432  # PostgreSQL
    LocalForward 27017 localhost:27017  # MongoDB
```

### 3. Test Conexiune de pe Mac

```bash
# Test basic
ssh nova-ubuntu

# Test cu GPU check
ssh nova-ubuntu 'nvidia-smi'

# Test PyTorch CUDA
ssh nova-ubuntu 'cd ~/ai-cosmic-garden/Nova_20 && source venv_nova/bin/activate && python -c "import torch; print(torch.cuda.is_available())"'
```

---

## 🎨 VSCode Remote SSH Setup

### 1. Instalează Extension

1. Deschide VSCode pe Mac
2. `Cmd+Shift+X` (Extensions)
3. Caută: **Remote - SSH**
4. Instalează: **Remote - SSH** (Microsoft)
5. Reload VSCode

### 2. Conectează la Ubuntu

1. `Cmd+Shift+P`
2. Tastează: **Remote-SSH: Connect to Host...**
3. Alege: **nova-ubuntu** (din ~/.ssh/config)
4. Selectează: **Linux**
5. Așteaptă instalare VS Code Server (~1-2 min prima dată)
6. `Cmd+O` → `/home/cezar/ai-cosmic-garden/Nova_20`

### 3. Instalează Extensions Remote

Pe remote Ubuntu, instalează:
- **Python** (Microsoft)
- **Pylance** (pentru IntelliSense)
- **Jupyter** (pentru notebooks)

---

## 🔥 Comenzi Utile

### Monitor GPU de pe Mac
```bash
ssh nova-ubuntu 'watch -n 1 nvidia-smi'  # Real-time monitoring
```

### Training Logs
```bash
ssh nova-ubuntu 'tail -f ~/ai-cosmic-garden/Nova_20/training.log'
```

### File Transfer
```bash
# Mac → Ubuntu
scp local_file.py nova-ubuntu:~/ai-cosmic-garden/Nova_20/

# Ubuntu → Mac
scp nova-ubuntu:~/ai-cosmic-garden/Nova_20/results.json ./
```

### Port Forwarding Manual (dacă nu e în config)
```bash
# TensorBoard
ssh -L 6006:localhost:6006 nova-ubuntu
# Apoi: http://localhost:6006 în browser pe Mac

# Jupyter
ssh -L 8888:localhost:8888 nova-ubuntu
# Apoi: http://localhost:8888 în browser pe Mac
```

---

## 🆘 Troubleshooting

### Connection Refused
```bash
# Verifică SSH service pe Ubuntu
ssh nova-ubuntu 'sudo systemctl status ssh'

# Verifică firewall
ssh nova-ubuntu 'sudo ufw status'
```

### Permission Denied (publickey)
- Verifică că ai cheia corectă în ~/.ssh/config pe Mac
- Verifică permissions: `chmod 600 ~/.ssh/id_ed25519_nova`
- Verifică că cheia publică e în authorized_keys pe Ubuntu

### VSCode Server Install Fails
```bash
# Pe Ubuntu, șterge server vechi
ssh nova-ubuntu 'rm -rf ~/.vscode-server'

# Retry conexiune din VSCode
```

---

## 🎯 Workflow Recomandat

1. **Edit pe Mac** - VSCode connected la Ubuntu
2. **Run pe Ubuntu** - Terminal în VSCode (automatic pe Ubuntu)
3. **Monitor pe Mac** - nvidia-smi în terminal separat
4. **Debug pe Mac** - VSCode debugger funcționează transparent
5. **Git pe Mac sau Ubuntu** - ambele funcționează (SSH keys sync)

---

## 📝 Notes

- SSH key deja generată pe Ubuntu pentru GitHub
- Aceeași key poate fi folosită pentru remote development
- VSCode Remote SSH e mai eficient decât X11 forwarding
- Toate operațiile GPU rămân pe Ubuntu, doar UI e pe Mac
- Training logs pot fi monitorizate în timp real

**Status:** ✅ SSH Server ready on Ubuntu  
**Next:** Setup SSH config pe Mac + test conexiune

---

**Connection String pentru quick reference:**
```
ssh cezar@192.168.0.207
```
