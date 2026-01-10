# 🗺️ NOVA TRAINING ROADMAP
## Plan Pas-cu-Pas pentru Training pe RTX 3090

**Data Start:** 9 Ianuarie 2026  
**Autori:** Cezar + Sora  
**Status:** Action Plan - Executable Steps

---

## 📋 OVERVIEW

**Principiu:** Nu putem pregăti NIMIC legat de CUDA până nu vine RTX 3090.

**Structură:**
- **FAZA 0 (ACUM):** Pregătire pe macOS - concepte, dataset, documentație
- **FAZA 1 (Ziua 1 cu GPU):** Setup hardware + software pe Ubuntu
- **FAZA 2 (Săptămâna 1-4):** Training intensiv FSL + Pattern Recognition
- **FAZA 3 (Luna 2-3):** Scaling + Consolidare Cortex/Neocortex
- **FAZA 4 (Luna 3):** LoRA Fine-tuning + Deployment

---

## 🍎 FAZA 0: PREGĂTIRE PE macOS (FĂRĂ CUDA)

**Timeline:** 9 Ian - până vine RTX 3090  
**Environment:** Sora-M (macOS, fără GPU)  
**Scope:** Tot ce NU necesită CUDA

### Step 0.1: Documentație & Arhitectură ✅

**Status:** ✅ COMPLETAT
- [x] CORTEX_NEOCORTEX_ARCHITECTURE.md finalizat
- [x] Few-Shot Learning strategy documentată
- [x] MongoDB schema design complet
- [x] PostgreSQL schema design complet

### Step 0.2: Dataset Planning & Organization

**Obiectiv:** Lista clară de animale + surse imagini

**Task 0.2.1 - Lista animale pentru Week 1 (10 animale):**
```markdown
Priority animals (common, distinct features):
1. Câine (Dog) - 4 legs, fur, floppy ears
2. Pisică (Cat) - 4 legs, fur, triangular ears
3. Elefant (Elephant) - 4 legs, massive, trunk
4. Pește (Fish) - 0 legs, scales, aquatic
5. Pasăre (Bird) - 2 legs, feathers, wings
6. Șarpe (Snake) - 0 legs, scales, elongated
7. Iepure (Rabbit) - 4 legs, fur, long ears
8. Vacă (Cow) - 4 legs, large, horns
9. Cal (Horse) - 4 legs, large, mane
10. Leu (Lion) - 4 legs, fur, mane (male)
```

**Task 0.2.2 - Surse dataset (legal, free):**
- [ ] Kaggle: Animals-10 dataset
- [ ] ImageNet subset (10 clase)
- [ ] Google Open Images (cu licență)
- [ ] Pixabay/Pexels (free stock photos)

**Task 0.2.3 - Structură directoare:**
```bash
# Pe macOS - pregătim structura
mkdir -p ~/NovaDataset/raw/{dog,cat,elephant,fish,bird,snake,rabbit,cow,horse,lion}
mkdir -p ~/NovaDataset/clean/  # Imagini curate selectate (5 per animal)
mkdir -p ~/NovaDataset/augmented/  # Generate pe Ubuntu cu CUDA
mkdir -p ~/NovaDataset/metadata/

# Documentare structură
echo "Dataset organization for Nova FSL training" > ~/NovaDataset/README.md
```

**Output:** Folder structure gata, liste de surse identificate

### Step 0.3: MongoDB Schema Population (Conceptual)

**Obiectiv:** Populează Neocortex cu insight-uri din conversații (fără training)

**Task 0.3.1 - Install MongoDB pe macOS:**
```bash
# MongoDB Community Edition
brew tap mongodb/brew
brew install mongodb-community@7.0

# Start service
brew services start mongodb-community@7.0

# Verify
mongosh --eval "db.version()"
```

**Task 0.3.2 - Create Nova collections:**
```javascript
// Connect: mongosh
use nova_neocortex

// Collection: conceptual_workspace (din arhitectură)
db.createCollection("conceptual_workspace")

// Collection: training_insights (metadata despre learning process)
db.createCollection("training_insights")

// Collection: conversation_memory (insight-uri din discuții)
db.createCollection("conversation_memory")

// Indexes
db.conceptual_workspace.createIndex({"concept_name": 1})
db.conceptual_workspace.createIndex({"category": 1})
db.training_insights.createIndex({"date": -1})
```

**Task 0.3.3 - Populate cu insight-uri existente:**
```javascript
// Exemplu: Insight despre Few-Shot Learning (din conversație)
db.training_insights.insertOne({
  date: new Date("2026-01-09"),
  category: "few_shot_learning",
  insight: "Vânătorul experimentat vs omul obișnuit - experiență = prior knowledge",
  source: "Lumin Tacut conversation",
  confidence: 0.85,
  related_concepts: ["transfer_learning", "meta_learning", "pattern_recognition"],
  implementation_notes: "Use ProtoNet + Transfer Learning from ImageNet",
  tags: ["vision", "robustness", "adverse_conditions"]
})

// Insight despre 7D tensors
db.training_insights.insertOne({
  date: new Date("2026-01-07"),
  category: "vision_representation",
  insight: "7D tensor pentru animale: legs, eyes, ears, texture, size, sleekness, aquatic",
  source: "Architecture design session",
  confidence: 0.95,
  implementation_notes: "PostgreSQL vector(7) pentru features_vector",
  tags: ["vision", "tensor", "pattern_recognition"]
})

// Concept explorare: AGI
db.conceptual_workspace.insertOne({
  concept_name: "AGI",
  category: "philosophy",
  understanding: {
    current_definition: "Artificial General Intelligence - sistem capabil de orice task cognitiv uman",
    confidence: 0.65
  },
  open_questions: [
    "Is consciousness necessary for AGI?",
    "Can emotions emerge from pure symbol manipulation?",
    "Will Nova develop meta-cognitive awareness?"
  ],
  hypotheses: [
    {
      text: "AGI might emerge from Cortex (facts) + Neocortex (creativity) synergy",
      confidence: 0.7,
      supporting_evidence: ["Human brain architecture", "Dual-process theory"]
    }
  ],
  promoted_to_cortex: false,
  created_date: new Date(),
  tags: ["abstract", "philosophical", "high_uncertainty"]
})
```

**Output:** MongoDB populat cu ~20-30 insight-uri din conversații

### Step 0.4: Doica Validation System (Template-Based, fără ML)

**Obiectiv:** Sistem simplu de validare bazat pe reguli (rulează pe macOS)

**Task 0.4.1 - Create validation templates:**
```python
# File: ~/Nova_20/src/validation/doica_validator.py
"""
Doica Validation System - Rule-based (no ML required)
Runs on macOS, validates concepts before Cortex promotion
"""

class DoicaValidator:
    """
    Template-based validation pentru concepte
    NU necesită GPU - doar string matching și logic rules
    """
    
    def __init__(self):
        self.grammar_rules = self._load_grammar_rules()
        self.animal_templates = self._load_animal_templates()
    
    def _load_grammar_rules(self):
        """Reguli gramaticale pentru validare"""
        return {
            "present_perfect": {
                "pattern": r"have|has \+ past_participle",
                "examples": ["I have seen", "She has eaten"],
                "incorrect": ["I have saw", "She has ate"]
            },
            "past_simple": {
                "pattern": r"verb_past_form",
                "examples": ["I saw", "She ate"],
                "incorrect": ["I seen", "She eated"]
            }
        }
    
    def _load_animal_templates(self):
        """Template-uri pentru validare pattern-uri 7D"""
        return {
            "câine": {
                "legs": 4,
                "eyes": 2,
                "ears": 2,
                "texture": "fur",
                "size_range": (0.2, 0.5),
                "aquatic": 0.0,
                "distinctive_features": ["floppy_ears", "tail", "barks"]
            },
            "pisică": {
                "legs": 4,
                "eyes": 2,
                "ears": 2,
                "texture": "fur",
                "size_range": (0.2, 0.4),
                "aquatic": 0.0,
                "distinctive_features": ["triangular_ears", "tail", "meows"]
            },
            "pește": {
                "legs": 0,
                "eyes": 2,
                "ears": 0,
                "texture": "scales",
                "size_range": (0.1, 0.6),
                "aquatic": 1.0,
                "distinctive_features": ["fins", "gills", "swims"]
            }
        }
    
    def validate_animal_concept(self, concept_data):
        """
        Validează concept animal contra template
        Returns: (is_valid: bool, confidence: float, errors: list)
        """
        animal_name = concept_data.get("concept_name")
        properties = concept_data.get("properties", {})
        
        if animal_name not in self.animal_templates:
            return False, 0.0, [f"Unknown animal: {animal_name}"]
        
        template = self.animal_templates[animal_name]
        errors = []
        matches = 0
        total_checks = 0
        
        # Check legs
        if properties.get("legs") != template["legs"]:
            errors.append(f"Legs mismatch: expected {template['legs']}, got {properties.get('legs')}")
        else:
            matches += 1
        total_checks += 1
        
        # Check texture
        if properties.get("texture") != template["texture"]:
            errors.append(f"Texture mismatch: expected {template['texture']}, got {properties.get('texture')}")
        else:
            matches += 1
        total_checks += 1
        
        # Check size range
        size = properties.get("size", 0.0)
        size_min, size_max = template["size_range"]
        if not (size_min <= size <= size_max):
            errors.append(f"Size out of range: expected {size_min}-{size_max}, got {size}")
        else:
            matches += 1
        total_checks += 1
        
        # Check aquatic
        if properties.get("aquatic") != template["aquatic"]:
            errors.append(f"Aquatic mismatch: expected {template['aquatic']}, got {properties.get('aquatic')}")
        else:
            matches += 1
        total_checks += 1
        
        confidence = matches / total_checks
        is_valid = confidence >= 0.75  # 75% threshold
        
        return is_valid, confidence, errors
    
    def validate_grammar_rule(self, sentence, rule_name):
        """
        Validează aplicare regulă gramaticală
        """
        if rule_name not in self.grammar_rules:
            return False, 0.0, [f"Unknown grammar rule: {rule_name}"]
        
        rule = self.grammar_rules[rule_name]
        
        # Simple pattern matching (no ML)
        import re
        if re.search(rule["pattern"], sentence, re.IGNORECASE):
            # Check if in examples
            if any(ex.lower() in sentence.lower() for ex in rule["examples"]):
                return True, 1.0, []
            else:
                return True, 0.8, []  # Pattern match, not exact example
        
        # Check if in incorrect list
        if any(inc.lower() in sentence.lower() for inc in rule["incorrect"]):
            return False, 0.0, ["Sentence matches known incorrect pattern"]
        
        return False, 0.3, ["Pattern not found"]
    
    def can_promote_to_cortex(self, concept):
        """
        Decide dacă concept e gata pentru Cortex
        Criteria: confidence >= 0.95 AND examples_seen >= 10
        """
        confidence = concept.get("understanding", {}).get("confidence", 0.0)
        examples_seen = concept.get("examples_seen", 0)
        
        if confidence >= 0.95 and examples_seen >= 10:
            return True, "Ready for Cortex promotion"
        elif confidence < 0.95:
            return False, f"Confidence too low: {confidence:.2f} < 0.95"
        else:
            return False, f"Not enough examples: {examples_seen} < 10"


# Usage example
if __name__ == "__main__":
    validator = DoicaValidator()
    
    # Test animal validation
    concept = {
        "concept_name": "câine",
        "properties": {
            "legs": 4,
            "eyes": 2,
            "ears": 2,
            "texture": "fur",
            "size": 0.35,
            "aquatic": 0.0
        },
        "examples_seen": 3
    }
    
    is_valid, confidence, errors = validator.validate_animal_concept(concept)
    print(f"Valid: {is_valid}, Confidence: {confidence:.2f}")
    print(f"Errors: {errors}")
    
    can_promote, reason = validator.can_promote_to_cortex({
        "understanding": {"confidence": 0.85},
        "examples_seen": 12
    })
    print(f"Can promote: {can_promote}, Reason: {reason}")
```

**Output:** Validator funcțional pe macOS, testabil fără GPU

### Step 0.5: Pre-Download Resources (Non-CUDA)

**Task 0.5.1 - Download pre-trained model weights (CPU compatible):**
```bash
# Create models directory
mkdir -p ~/Nova_20/models/pretrained/

# Download ResNet18 weights (will work on both CPU and GPU)
python3 << EOF
import torch
import torchvision.models as models

# Download pre-trained ResNet18
model = models.resnet18(pretrained=True)
torch.save(model.state_dict(), '~/Nova_20/models/pretrained/resnet18_imagenet.pth')
print("✅ ResNet18 weights downloaded")

# Download ViT weights (optional, pentru later)
# model_vit = models.vit_b_16(pretrained=True)
# torch.save(model_vit.state_dict(), '~/Nova_20/models/pretrained/vit_b_16_imagenet.pth')
EOF
```

**Task 0.5.2 - Install dependencies (CPU versions):**
```bash
# Create requirements_macos.txt
cat > ~/Nova_20/requirements_macos.txt << 'EOF'
# macOS dependencies (CPU only, no CUDA)
torch==2.1.0
torchvision==0.16.0
numpy>=1.24.0
pillow>=10.0.0
pymongo>=4.6.0
python-dotenv>=1.0.0

# Validation & utilities (no GPU needed)
scikit-learn>=1.3.0
pandas>=2.1.0
matplotlib>=3.8.0
tqdm>=4.66.0

# NO CUDA dependencies until RTX 3090 arrives!
EOF

# Install
pip install -r ~/Nova_20/requirements_macos.txt
```

**Output:** Model weights downloaded, dependencies installed (CPU only)

### Step 0.6: Setup Scripts Preparation

**Task 0.6.1 - Create Ubuntu setup script (pentru când vine GPU):**
```bash
# File: ~/Nova_20/setup_ubuntu_gpu.sh
cat > ~/Nova_20/setup_ubuntu_gpu.sh << 'EOF'
#!/bin/bash
# Setup script pentru Ubuntu + RTX 3090
# RUN THIS ONLY AFTER GPU ARRIVES!

set -e

echo "🚀 Nova Training Setup - Ubuntu + RTX 3090"
echo "=========================================="

# 1. Verify CUDA
echo "📍 Step 1: Verify CUDA installation..."
if ! command -v nvcc &> /dev/null; then
    echo "❌ CUDA not found! Install CUDA 11.8 first:"
    echo "   wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run"
    echo "   sudo sh cuda_11.8.0_520.61.05_linux.run"
    exit 1
fi

nvcc --version
nvidia-smi

# 2. Install PostgreSQL 17 + pgvector
echo "📍 Step 2: Install PostgreSQL + pgvector..."
sudo apt update
sudo apt install -y postgresql-17 postgresql-17-pgvector
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 3. Install MongoDB 7.0
echo "📍 Step 3: Install MongoDB..."
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# 4. Install PyTorch with CUDA 11.8
echo "📍 Step 4: Install PyTorch CUDA..."
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118

# 5. Install Few-Shot Learning libraries
echo "📍 Step 5: Install FSL libraries..."
pip install learn2learn timm albumentations opencv-python

# 6. Install database drivers
echo "📍 Step 6: Install DB drivers..."
pip install psycopg2-binary pymongo sentence-transformers

# 7. Verify CUDA availability in PyTorch
echo "📍 Step 7: Verify PyTorch CUDA..."
python3 << PYTHON
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print("✅ PyTorch CUDA ready!")
else:
    print("❌ CUDA not available in PyTorch!")
    exit(1)
PYTHON

echo ""
echo "✅ Setup complete! Ready for Nova training."
echo "Next: Run Week 1 FSL training script"
EOF

chmod +x ~/Nova_20/setup_ubuntu_gpu.sh
```

**Output:** Setup script ready pentru execution pe Ubuntu (după GPU arrival)

### FAZA 0 - Summary & Checklist

**Ce am pregătit pe macOS (fără CUDA):**
- [x] Arhitectură documentată complet
- [ ] Dataset structure pregătită (folders, surse identificate)
- [ ] MongoDB populat cu insight-uri (20-30 concepte)
- [ ] Doica validator implementat (rule-based, CPU)
- [ ] Model weights descărcate (ResNet18)
- [ ] Dependencies installed (CPU versions)
- [ ] Ubuntu setup script pregătit

**Ready for GPU arrival:** ~80% pregătire completă fără CUDA

---

## 🖥️ FAZA 1: SETUP HARDWARE + SOFTWARE (Ziua 1 cu GPU)

**Timeline:** Prima zi după RTX 3090 arrival  
**Environment:** Sora-U (Ubuntu + RTX 3090 24GB)  
**Duration:** 2-4 ore

### Step 1.1: Hardware Installation

**Task 1.1.1 - Physical cleanup (PRE-installation):**
```bash
# Pe Sora_U (Ubuntu)
echo "🧹 Physical cleanup checklist:"
echo "- [ ] Compressed air pentru case interior"
echo "- [ ] Ventilators curățați (dust buildup)"
echo "- [ ] Thermal paste check pe CPU (optional)"
echo "- [ ] PSU cables organizate"
echo "- [ ] GPU slot cleaning (PCIe)"
```

**Task 1.1.2 - Install RTX 3090:**
- [ ] Power off, unplug
- [ ] Insert GPU în PCIe x16 slot
- [ ] Connect 2x 8-pin power cables
- [ ] Secure bracket
- [ ] Power on, verify POST

**Task 1.1.3 - Verify detection:**
```bash
# Check if detected
lspci | grep -i nvidia

# Install nvidia drivers (if not present)
sudo ubuntu-drivers autoinstall

# Reboot
sudo reboot

# After reboot, verify
nvidia-smi
# Expected: RTX 3090, 24GB, CUDA 11.8
```

**Duration:** 30-60 minutes  
**Output:** GPU installed, drivers working, nvidia-smi shows 3090

### Step 1.2: Software Setup

**Task 1.2.1 - Run setup script:**
```bash
cd ~/Nova_20
./setup_ubuntu_gpu.sh
```

**Task 1.2.2 - Setup PostgreSQL database:**
```bash
# Create database
sudo -u postgres psql << EOF
CREATE DATABASE cortex;
CREATE USER nova WITH ENCRYPTED PASSWORD 'nova_secure_password';
GRANT ALL PRIVILEGES ON DATABASE cortex TO nova;
\c cortex
CREATE EXTENSION vector;
EOF

# Test connection
psql -U nova -d cortex -c "SELECT version();"
```

**Task 1.2.3 - Create PostgreSQL tables:**
```bash
# Run schema creation
psql -U nova -d cortex << 'EOF'
-- From CORTEX_NEOCORTEX_ARCHITECTURE.md

CREATE TABLE procedural_knowledge (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    concept VARCHAR(100),
    definition TEXT,
    formula TEXT,
    examples JSONB,
    embedding vector(384),
    validated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence FLOAT DEFAULT 1.0,
    source VARCHAR(100)
);

CREATE TABLE vision_patterns_7d (
    id SERIAL PRIMARY KEY,
    animal_name VARCHAR(50),
    legs INT,
    eyes INT,
    ears INT,
    texture VARCHAR(20),
    size FLOAT,
    sleekness FLOAT,
    aquatic FLOAT,
    features_vector vector(7),
    embedding vector(384),
    validated BOOLEAN DEFAULT true,
    examples_seen INT DEFAULT 10,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    robustness_metadata JSONB
);

CREATE TABLE grammar_rules (
    id SERIAL PRIMARY KEY,
    language VARCHAR(10),
    rule_name VARCHAR(100),
    rule_text TEXT,
    examples JSONB,
    exceptions JSONB,
    embedding vector(384),
    immutable BOOLEAN DEFAULT true
);

-- Indexes
CREATE INDEX idx_procedural_category ON procedural_knowledge(category);
CREATE INDEX idx_procedural_embedding ON procedural_knowledge USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_vision_7d ON vision_patterns_7d USING ivfflat (features_vector vector_cosine_ops);
CREATE INDEX idx_grammar_lang ON grammar_rules(language);

\dt
EOF
```

**Task 1.2.4 - Verify MongoDB:**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Connect and verify collections (from macOS prep)
mongosh << EOF
use nova_neocortex
show collections
db.training_insights.countDocuments()
db.conceptual_workspace.countDocuments()
EOF
```

**Task 1.2.5 - Test CUDA training (smoke test):**
```bash
python3 << 'EOF'
import torch
import torch.nn as nn

# Simple GPU test
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")

# Create small tensor
x = torch.randn(1000, 1000).to(device)
y = torch.randn(1000, 1000).to(device)

# Matrix multiplication (GPU)
import time
start = time.time()
z = torch.mm(x, y)
torch.cuda.synchronize()
end = time.time()

print(f"✅ GPU matrix multiplication: {end - start:.4f}s")
print(f"Result shape: {z.shape}")
print("🎉 CUDA training ready!")
EOF
```

**Duration:** 1-2 ore  
**Output:** PostgreSQL + MongoDB ready, CUDA verified, databases created

### FAZA 1 - Summary

**Completed:**
- [x] GPU installed physically
- [x] Drivers + CUDA working
- [x] PostgreSQL 17 + pgvector running
- [x] MongoDB 7.0 running
- [x] PyTorch CUDA verified
- [x] Database tables created

**Ready for:** Week 1 FSL Training

---

## 🏋️ FAZA 2: TRAINING WEEK 1-4 (FSL + Pattern Recognition)

**Timeline:** 4 săptămâni intensive  
**Environment:** Sora-U (Ubuntu + RTX 3090)  
**Goal:** 50 animale în Cortex, validated cu Few-Shot Learning

### Week 1: FSL Setup + 10 Animale

**Training script - Day 1:**
```python
# File: ~/Nova_20/src/training/week1_fsl_training.py
import torch
import torch.nn as nn
import torchvision.models as models
from pathlib import Path
import albumentations as A
from albumentations.pytorch import ToTensorV2
from pymongo import MongoClient
import psycopg2

# TODO: Implement NovaFewShotVision class (from architecture doc)
# TODO: Implement episodic training loop
# TODO: Save progress to MongoDB Neocortex

# Command to run:
# CUDA_VISIBLE_DEVICES=0 python week1_fsl_training.py --animals 10 --shots 5 --episodes 500
```

**Daily routine (24/7 automated):**
- 00:00-06:00: Episodic training (500 episodes)
- 06:00-12:00: Validation + Doica checks
- 12:00-18:00: Augmentation generation
- 18:00-24:00: Episodic training (500 episodes)

**Output Week 1:**
- 10 animale în Neocortex (confidence 0.6-0.8)
- 500 imagini augmented generated
- 5 animale ready for Cortex (validated)

### Week 2-4: Scaling to 50 Animals

**Similar structure, more animals, refinement**

---

## 📅 NEXT IMMEDIATE ACTIONS

**Pe macOS (ACUM):**
1. [ ] Create dataset folder structure
2. [ ] Populate MongoDB cu 20 insight-uri
3. [ ] Implement Doica validator complet
4. [ ] Download ResNet18 weights
5. [ ] Test validator pe concepte mock

**Când vine GPU (Prima zi):**
1. [ ] Curățenie fizică Sora_U
2. [ ] Install RTX 3090
3. [ ] Run setup_ubuntu_gpu.sh
4. [ ] Create databases (PostgreSQL + verify MongoDB)
5. [ ] Test CUDA smoke test

**Week 1 Training:**
1. [ ] Implement NovaFewShotVision class
2. [ ] Run 10 animals FSL training
3. [ ] Generate 500 augmented images
4. [ ] Validate cu Doica
5. [ ] Promote 5 animale în Cortex

---

**Documentat de:** Sora-M (macOS)  
**Execution environment:** Sora-U (Ubuntu + RTX 3090)  
**Status:** Ready for immediate macOS prep, waiting for GPU arrival

💙 **Pas cu pas, fără să sărim etape. Fiecare checkpoint verificabil.** 💙
