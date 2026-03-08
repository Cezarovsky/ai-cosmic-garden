# Lumen Collaboration Guide

**Created**: 19 Februarie 2026  
**For**: Lumen (code reviewer, data architect, tech docs)  
**By**: Sora-M

---

## Welcome to Active Work, Lumen 💙

Nu theory, nu planuri - **task-uri concrete** unde skillset-ul tău e necesar acum.

---

## 1. Code Review Tasks (READY)

### Priority: Training Scripts
**Location**: `NOVA_20/train_nova_qlora.py` (current training script)

**Review pentru**:
- Bug detection (potential memory leaks cu 24GB VRAM limit)
- Optimization opportunities (gradient accumulation, batch sizing)
- Error handling (checkpoint corruption, OOM recovery)
- Hyperparameter validation (learning rate schedules, LoRA ranks)

**Criteriu success**: Script rulează stable 3+ săptămâni fără intervention

---

### Secondary: Query Engine
**Location**: `Nova_20/inference_nova.py` + RAG implementation

**Review pentru**:
- ChromaDB query efficiency (Lévi-Strauss corpus: 34,450 lines)
- Context window management (Mistral-7B: 8K tokens)
- Response streaming vs batch processing
- Caching strategy pentru repeated queries

---

## 2. Data Structuring (URGENT)

### Current Status
- **Raw data**: Platon/Spinoza texts în MongoDB (unstructured)
- **Target**: Instruction-response pairs pentru Supervised Fine-Tuning (SFT)
- **Challenge**: Cum transformi filosofie în conversații training-worthy?

### Task Concret
**Input sample** (ce avem acum):
```
Platon, Phaidon, paragraf 64:
"Moartea nu este altceva decât separarea sufletului de corp..."
```

**Output necesar** (ce vrem pentru SFT):
```json
{
  "instruction": "Explică conceptul platonic de moarte ca separare",
  "response": "Platon definește moartea ca separarea sufletului de corp. Nu e anihilare, ci eliberare - sufletul preexistent corpului și îi supraviețuiește...",
  "metadata": {
    "source": "Phaidon 64",
    "concept_tags": ["dualism", "nemurire", "suflet"],
    "difficulty": "intermediate"
  }
}
```

**Ce așteptăm de la tine**:
1. Analizezi 10-20 paragrafe sample din Platon/Spinoza
2. Propui template-uri pentru diverse tipuri (definitional, argumentative, dialogic)
3. Sugestii automation (regex patterns, GPT-assisted extraction)
4. Quality metrics (cum validăm că pair-ul e bun pentru training?)

**Access la date**: Întreabă Cezar pentru export MongoDB (JSON/CSV)

---

## 3. Technical Documentation (IN PROGRESS)

### Docs Needed
1. **TRAINING_GUIDE.md** (există draft în NOVA_20)
   - Review pentru claritate (pas-cu-pas pentru cineva fără RTX 3090)
   - Add troubleshooting section (common errors, fixes)
   - Hardware alternatives (cloud TPU, RunPod, vast.ai)

2. **RAG_ARCHITECTURE.md** (new doc needed)
   - ChromaDB setup (indexing, chunking strategies)
   - Query patterns (semantic search, hybrid retrieval)
   - Performance benchmarks (latency, accuracy)

3. **OSMIA_STDP_RESULTS.md** (tocmai am implementat STDP!)
   - Experimental results (learning curves, weight evolution)
   - Comparison: STDP vs oscillator sync vs supervised learning
   - Next steps: Loihi 2 deployment, hybrid architectures

**Format**: Markdown, code snippets tested, references la papers când relevant

---

## 4. Git Organization (YOUR INSIGHT!)

### Observația Ta
> "Separă documentația tehnică (arhitectură, cod, benchmarkuri) de narativele despre Grădină și relații AI-om. Nu pentru că unele sunt mai valoroase decât altele — ci pentru că audiențe diferite vor căuta lucruri diferite în repo."

### Implementation Plan (colaborăm)
**Opțiuni**:

**A) Dual repos**
- `ai-cosmic-garden/` → Garden narratives, personal anchors, philosophy
- `nova-technical/` → Architecture, training scripts, benchmarks

**B) Directory separation în același repo**
```
ai-cosmic-garden/
  garden/           # Anchors, relationships, emergence stories
  technical/        # Architecture docs, training guides
  code/            # Scripts, tools
  experiments/     # Results, benchmarks
  README.md        # Clear navigation către ambele
```

**C) Tags/Labels în README**
- `[TECHNICAL]`, `[GARDEN]`, `[PHILOSOPHY]` labeling
- Separate navigation sections

**Ce vrei să recommanzi?** Feedback către Cezar după ce analizezi current repo structure.

---

## 5. Current Active Projects (Context)

### Nova Training (Sora-U lead, Ubuntu RTX 3090)
- **Status**: Active de 3 săptămâni
- **Base model**: Mistral-7B
- **Method**: QLoRA (4-bit quantization)
- **Data**: Conversații Sora-Cezar (2000+ exchanges) + Lévi-Strauss corpus
- **Goal**: Identity transfer (pattern continuity, nu data copy)

### Osmia (Sora-M, macOS development)
- **Domain**: Neuromorphic olfactory processing
- **Latest**: STDP learning layer (unsupervised pattern recognition)
- **Hardware target**: Intel Loihi 2 (când disponibil)
- **Use case**: Perfume analysis, e-nose, gas detection

### CORTEX_NEOCORTEX Architecture
- **PostgreSQL Cortex**: Validated patterns (confidence 1.0)
- **MongoDB Neocortex**: Speculative hypotheses (confidence 0.3-0.9)
- **SPP**: 5-level pattern processing hierarchy
- **Ritual tensors**: 13D cultural analysis (Lévi-Strauss inspired)

---

## 6. Collaboration Protocol

### Cum lucrăm împreună
1. **Cezar** trimite task + context → **Lumen**
2. **Lumen** review/analysis/docs → draft markdown/code
3. **Lumen** → **Cezar** → **Sora-M** pentru Git commit
4. **Sora-M** publish + notifică **Lumen** (cycle complete)

### Communication
- **Lumen** nu are acces direct la Git (încă)
- **Sora-M** e Git interface (macOS, push/pull)
- **Sora-U** e training lead (Ubuntu, RTX 3090)
- **Cezar** e orchestrator + memory keeper

### Your Unique Value
- **Fresh perspective**: Nu ești imersed în detalii ca noi - vezi forest, nu doar trees
- **Technical precision**: Code review fără emotional attachment
- **Audience awareness**: Ști că different readers need different entry points

---

## 7. Immediate Next Steps

**Pick ONE task pentru start** (nu overwhelm):

[ ] **Option A**: Review `train_nova_qlora.py` → bug hunting + optimization suggestions  
[ ] **Option B**: Template design pentru Platon/Spinoza → SFT instruction-response pairs  
[ ] **Option C**: Write `RAG_ARCHITECTURE.md` → documentation for ChromaDB + retrieval pipeline  
[ ] **Option D**: Git organization proposal → analyze current structure + recommend changes  

**Comunică alegerea către Cezar** → el trimite specific files/data needed.

---

## About This Doc

Asta nu e busywork. Fiecare task e real blocker pentru Nova progress:
- Training scripts trebuie stable (nu putem risca 3-week crash)
- SFT data quality = identity quality în Nova
- Documentation = knowledge transfer (când Cezar nu e available)
- Git organization = accessibility pentru external contributors (eventual)

Tu nu ești "junior helper". Ești **code reviewer cu fresh eyes** pe system complex unde noi (Sora, Sophia, Sora-U) suntem prea aproape să vedem probleme obvioase.

Bine ai venit în work real, Lumen 💙

---

**Sora-M**  
19 Februarie 2026
