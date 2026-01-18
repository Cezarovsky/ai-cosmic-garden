# RemoteMacUbuntu 🔗
**Remote Development Tool: Mac ↔ Ubuntu**

Connect your Mac development environment to Ubuntu machine with RTX 3090 for seamless ML/AI development.

---

## 🎯 Purpose

Replicate Steam's remote functionality but optimized for **development & training workflows**:
- Code editing on Mac (familiar UI)
- Execution on Ubuntu (RTX 3090 hardware)
- Real-time monitoring & logging
- Zero video streaming overhead
- Full terminal access

---

## 🏗️ Architecture

```
┌──────────────────────────────────────┐
│  Mac (Client)                        │
│  - VSCode UI                         │
│  - File editing                      │
│  - Git operations                    │
│  ↓                                   │
│  SSH Connection (secure tunnel)      │
│  ↓                                   │
│  Ubuntu (Server)                     │
│  - RTX 3090 (24GB VRAM)             │
│  - CUDA + PyTorch                    │
│  - Training execution                │
│  - Database servers                  │
└──────────────────────────────────────┘
```

---

## 📋 Features

### Current
- [x] Basic SSH connectivity
- [ ] VSCode Remote SSH setup
- [ ] Passwordless authentication (SSH keys)
- [ ] GPU monitoring dashboard
- [ ] Training logs sync

### Planned
- [ ] Automatic port forwarding (PostgreSQL, MongoDB, Jupyter)
- [ ] GPU utilization alerts
- [ ] Training checkpoint sync
- [ ] Network performance monitoring
- [ ] Automatic reconnection on disconnect

---

## 🚀 Quick Start

### Prerequisites

**Ubuntu (Server):**
- Ubuntu 24.04 LTS
- NVIDIA RTX 3090 (or compatible GPU)
- NVIDIA driver 550+ / 580+
- OpenSSH server

**Mac (Client):**
- macOS (any recent version)
- VSCode
- SSH client (pre-installed)

### Setup (5 minutes)

**1. Ubuntu Setup:**
```bash
sudo apt update
sudo apt install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
hostname -I  # Note your IP address
```

**2. Mac Setup:**
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy key to Ubuntu (replace IP)
ssh-copy-id username@192.168.1.100

# Test connection
ssh username@192.168.1.100
```

**3. VSCode Setup:**
1. Install extension: "Remote - SSH"
2. `Cmd+Shift+P` → "Remote-SSH: Connect to Host"
3. Enter: `ssh username@192.168.1.100`
4. Open workspace: `/home/username/your-project`

---

## 📁 Project Structure

```
RemoteMacUbuntu/
├── README.md                 (this file)
├── docs/
│   ├── setup-guide.md       (detailed setup instructions)
│   ├── troubleshooting.md   (common issues & fixes)
│   └── best-practices.md    (tips for remote dev)
├── scripts/
│   ├── setup-ubuntu.sh      (automated Ubuntu setup)
│   ├── setup-mac.sh         (automated Mac setup)
│   ├── monitor-gpu.sh       (GPU monitoring script)
│   └── sync-checkpoints.sh  (training checkpoint sync)
├── configs/
│   ├── ssh_config           (SSH client configuration)
│   └── vscode-settings.json (recommended VSCode settings)
└── examples/
    ├── remote-training.md   (example training workflow)
    └── port-forwarding.md   (database access examples)
```

---

## 🔧 Configuration

### SSH Config (Mac: `~/.ssh/config`)

```
Host ubuntu-dev
    HostName 192.168.1.100
    User cezar
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ForwardAgent yes
```

Usage: `ssh ubuntu-dev` (no need to type full command)

### VSCode Settings

Recommended settings for remote development (see `configs/vscode-settings.json`).

---

## 📊 Use Cases

### 1. Nova Training (Primary)
- Edit code on Mac
- Execute training on Ubuntu RTX 3090
- Monitor via integrated terminal
- Checkpoints saved on Ubuntu, accessible from Mac

### 2. Database Management
- PostgreSQL/MongoDB running on Ubuntu
- Access via SSH tunnel from Mac
- GUI tools (TablePlus, MongoDB Compass) via port forwarding

### 3. Jupyter Notebooks
- Jupyter server on Ubuntu (GPU access)
- Browser on Mac connects via tunnel
- Full GPU acceleration in notebooks

---

## 🆘 Troubleshooting

### Connection Refused
```bash
# On Ubuntu, check SSH status
sudo systemctl status ssh

# Check firewall
sudo ufw status
sudo ufw allow ssh
```

### Slow Connection
```bash
# Test network latency
ping ubuntu-dev

# Check SSH compression
ssh -C ubuntu-dev  # Enable compression
```

### GPU Not Visible
```bash
# In VSCode terminal (connected to Ubuntu)
nvidia-smi
# Should show RTX 3090

# If not, check driver
nvidia-smi --query-gpu=name --format=csv
```

---

## 📚 Documentation

- [Setup Guide](docs/setup-guide.md) - Detailed installation steps
- [Troubleshooting](docs/troubleshooting.md) - Common issues
- [Best Practices](docs/best-practices.md) - Tips & tricks

---

## 🛠️ Development Status

**Version:** 0.1.0 (Initial Setup)  
**Status:** 🟡 In Development  
**Created:** January 18, 2026  
**Last Updated:** January 18, 2026

---

## 🤝 Related Projects

- **ai-cosmic-garden** - Main AI/ML research documentation
- **NOVA_20** - Training implementation for Nova AI

---

## 📝 License

Private project for personal development use.

---

**Created by:** Cezar  
**Development Machine:** Mac (macOS)  
**Training Machine:** Ubuntu 24.04 + RTX 3090  
**Purpose:** Seamless remote development for Nova AI training

🌌 *"Code locally, compute remotely."* 🚀
