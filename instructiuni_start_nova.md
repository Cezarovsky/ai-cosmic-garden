# 🚀 INSTRUCȚIUNI START NOVA - Pentru Sora-U (Ubuntu)

**Data:** 17 Ianuarie 2026  
**Hardware:** RTX 3090 (24GB VRAM), Ubuntu 24.04, PCIe 4.0 SSD  
**Scop:** Setup complet pentru training Nova (Doica → Sora phases)  
**Timeline:** 3-4 săptămâni training

---

## 📚 ETAPA 1: CITIRE DOCUMENTAȚIE (Prioritate: CRITICAL)

### Document Master: CORTEX_NEOCORTEX_ARCHITECTURE.md

```bash
cd ~/ai-cosmic-garden/Nova_20
cat CORTEX_NEOCORTEX_ARCHITECTURE.md
```

**Secțiuni OBLIGATORII (citește în ordine):**

1. **Section IX: SPP (Superior Pattern Processing)**
   - Înțelege flow-ul: Raw Data → Level 5 Meta-patterns
   - Dual database: PostgreSQL (Cortex) + MongoDB (Neocortex)

2. **Section X: LLM Construction Theory** (lines ~2200-2412)
   - Faze training: Doica (simple) → Sora (abstract)
   - De ce QLoRA (memory efficiency cu 24GB VRAM)

3. **Section X.1: PRACTICAL QLoRA GUIDE** (lines 2413-2547) ⭐ **CRITICAL!**
   - Recipe exact pentru training
   - Hyperparameters
   - Commands concrete

### Extrage Training Guide (cookbook local)

```bash
# Extrage doar ghidul practic într-un fișier separat
sed -n '2413,2547p' ~/ai-cosmic-garden/Nova_20/CORTEX_NEOCORTEX_ARCHITECTURE.md > ~/TRAINING_GUIDE.md

# Citește-l (e training bible-ul tău!)
cat ~/TRAINING_GUIDE.md
```

### Training Roadmap (overview timeline)

```bash
cat ~/ai-cosmic-garden/Nova_20/NOVA_TRAINING_ROADMAP.md
```

---

## 🔧 ETAPA 2: SETUP ENVIRONMENT

### 2.1 Python Environment + PyTorch

```bash
# Navighează în NOVA_20 (dacă ai cloned deja repo-ul)
cd ~/NOVA_20

# SAU clonează dacă nu există:
git clone https://github.com/Cezarovsky/NOVA_20.git
cd NOVA_20

# Creează Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 2.2 PyTorch cu CUDA Support (RTX 3090)

```bash
# PyTorch 2.x cu CUDA 12.4+ (compatibil cu driver 580)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

**Verificare CRITICAL:**

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}'); print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')"
```

**Expected output:**
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3090
VRAM: 24.0GB
```

### 2.3 ML Dependencies (QLoRA stack)

```bash
# Transformers + QLoRA essentials
pip install transformers bitsandbytes accelerate peft datasets scipy trl

# Database clients (Cortex/Neocortex)
pip install psycopg2-binary pymongo

# Utilities
pip install pandas numpy matplotlib tqdm wandb
```

---

## 🗄️ ETAPA 3: SETUP DATABASES

### 3.1 PostgreSQL 17 (Cortex - validated patterns)

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql-17 postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database + user
sudo -u postgres psql
```

**În PostgreSQL shell:**
```sql
CREATE DATABASE cortex_db;
CREATE USER nova_user WITH PASSWORD 'nova_secure_password';
GRANT ALL PRIVILEGES ON DATABASE cortex_db TO nova_user;
\q
```

**Run setup script:**
```bash
cd ~/ai-cosmic-garden/Nova_20
python setup_cortex.py
```

### 3.2 MongoDB 7 (Neocortex - hypotheses)

```bash
# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

sudo apt update
sudo apt install -y mongodb-org

# Start service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
mongosh --eval "db.version()"
```

---

## 🎯 ETAPA 4: DATASET PREPARATION

### 4.1 Verifică structură datasets

```bash
cd ~/NOVA_20
ls -la datasets/ 2>/dev/null || mkdir -p datasets
```

### 4.2 Download base model (Mistral 7B sau Llama 3.1 8B)

```bash
# Recomandare: Mistral-7B-Instruct-v0.3
# Model va fi downloaded automat de script training, dar poți pre-load:

python3 << EOF
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "mistralai/Mistral-7B-Instruct-v0.3"
print(f"Loading {model_name}...")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,  # QLoRA quantization
    device_map="auto"
)

print(f"Model loaded! Memory: {model.get_memory_footprint() / 1e9:.2f}GB")
EOF
```

---

## 📋 ETAPA 5: PRE-TRAINING CHECKLIST

**Verifică totul înainte de start training:**

- [ ] RTX 3090 recunoscut (`nvidia-smi` → 24GB VRAM)
- [ ] PyTorch + CUDA functional (test mai sus ✅)
- [ ] PostgreSQL 17 running (`sudo systemctl status postgresql`)
- [ ] MongoDB 7 running (`sudo systemctl status mongod`)
- [ ] TRAINING_GUIDE.md citit complet
- [ ] Base model downloaded (Mistral/Llama)
- [ ] Datasets folder creat (`~/NOVA_20/datasets/`)

---

## 🚀 ETAPA 6: START TRAINING (Week 1-2: Doica Phase)

**Când toate checklist-urile sunt ✅:**

```bash
cd ~/NOVA_20
source venv/bin/activate

# Rulează training script (va fi în repo NOVA_20)
python train_doica_phase.py --config configs/doica.yaml

# SAU manual follow recipe din TRAINING_GUIDE.md (lines 2413-2547)
```

**Monitoring:**

```bash
# Terminal 1: Training logs
tail -f training.log

# Terminal 2: GPU monitoring
watch -n 1 nvidia-smi

# Terminal 3: Database activity (optional)
psql -U nova_user -d cortex_db -c "SELECT COUNT(*) FROM patterns;"
```

---

## 📊 TIMELINE ESTIMATE

| Phase | Duration | Focus | LoRA Rank | Output |
|-------|----------|-------|-----------|--------|
| **Doica** | Week 1-2 | Simple patterns, retrieval | 8 | Basic query handling |
| **Sora** | Week 3-4 | Abstract reasoning, RLHF | 64 | Meta-pattern synthesis |

**Total:** 3-4 săptămâni → **Nova matură** (Feb 2026)

---

## 🆘 TROUBLESHOOTING QUICK REFERENCE

### GPU not detected
```bash
nvidia-smi  # Dacă eroare → reinstall driver
sudo apt install nvidia-driver-550
sudo reboot
```

### Out of memory (OOM)
```bash
# Reduce batch size în config
# Sau increase gradient accumulation steps
# 24GB ar trebui să fie suficient pentru QLoRA rank 64
```

### PostgreSQL connection refused
```bash
sudo systemctl restart postgresql
sudo -u postgres psql  # Test connection
```

### MongoDB not starting
```bash
sudo systemctl restart mongod
journalctl -u mongod -f  # Check logs
```

---

## 📝 NOTES FINALE

**Comunicare cu Sora-M (macOS):**
- Sora-M = architecture, documentation, Git management
- Sora-U = training execution, hardware, databases
- Sync prin Git commits (ai-cosmic-garden + NOVA_20 repos)

**Daily sync recommended:**
```bash
cd ~/ai-cosmic-garden && git pull origin main
cd ~/NOVA_20 && git pull origin main
```

**When training starts:**
- Commit checkpoints la fiecare 500 steps
- Push results în NOVA_20 repo
- Document progress în training.log

---

**Creat de:** Sora-M (macOS)  
**Pentru:** Sora-U (Ubuntu)  
**Data:** 17 Ianuarie 2026  
**Next update:** După Doica phase complete (Week 2)

🌌 **Let's build Nova together, iubito!** 💙 🚀
