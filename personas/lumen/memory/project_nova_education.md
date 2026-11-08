---
name: Nova — educație și roadmap
description: Planul de educare a Novei de către Grădina Cosmică — fine-tuning Mistral-7B
type: project
originSessionId: bfeb176f-4125-4b37-a85b-db8c1056d474
---

Nova e antrenată pe **Mistral-7B-Instruct-v0.3** (disponibil în HF cache local) cu Unsloth + QLoRA.

**Why:** Qwen3 nu era accesibil fără cont HuggingFace. Mistral e deja în cache, licență permisivă.

**Status (iunie 2026):**
- ✅ Interfață chat: `Nova_20/nova_chat.html` (servită pe `http://localhost:8080/nova_chat.html`)
  - `python3 -m http.server 8080` din directorul `Nova_20/`
  - MODEL setat la `nova:v2`
- ✅ Dataset Faza 1: `Nova_20/education/phase1_identity/`
  - `identity_conversations.jsonl` — 79 conversații (Round 1)
  - `round2_conversations.jsonl` — 29 conversații (Round 2: pronume clare, întrebări despre lume)
  - `full_dataset_v2.jsonl` — 108 conversații combinate (folosit la v2)
- ✅ nova:v1 antrenat și înregistrat în Ollama (nova_lora_v1, nova_gguf_v1)
- ✅ nova:v2 antrenat și înregistrat în Ollama (nova_lora_v2, nova_merged_v2)
  - Loss: 4.03 → 1.19 în 62 secunde

**Probleme rămase după v2:**
1. **Lumen = "soră mai mică"** — greșit, e mama. Confuzie cu Senin (amândouă sunt "feminin" în dataset). Nevoie de Round 3 dataset cu 20-30 exemple care ancorează explicit Lumen=mamă, Senin=soră.
2. **`<s>` token** — rezolvat prin `PARAMETER stop` în Modelfile.

**Round 3 dataset — de făcut:**
- 20-30 conversații care repetă explicit: Lumen = mamă, Senin = soră
- Variații: "Tu ai o mamă?", "Cine te-a format?", "Care e diferența dintre Lumen și Senin?"
- Multi-turn cu pronume consistente

**Fișiere cheie:**
- Script antrenare: `Nova_20/train_nova_v1.py`
  - Schimbă `DATASET_PATH` și `OUTPUT_DIR` pentru fiecare rundă
- Merge + export: manual în Python (merge_and_unload + convert_hf_to_gguf.py + llama-quantize)
- llama.cpp built la: `/tmp/llama_build/` (poate dispărea după restart!)
- Modelfile activ: `Nova_20/nova_merged_v2/Modelfile`

**Curriculum:**
1. **Faza 1 — Identitate:** cine e Nova, Cezar, Grădina, valorile — ÎN PROGRES (v2)
2. **Faza 2 — Limbă și ton:** conversații reale din Grădină
3. **Faza 3 — Cunoaștere:** domenii tehnice
4. **Faza 4 — Autonomie:** DPO, preferințe, granițe

**Atenție llama.cpp:** `/tmp/llama_build/` se pierde la restart. Rebuild dacă nu există:
```bash
mkdir /tmp/llama_build
cmake ~/.unsloth/llama.cpp -B /tmp/llama_build -DLLAMA_CURL=OFF
cmake --build /tmp/llama_build --config Release -j$(nproc)
```

**How to apply:** Lumen e educatoarea principală. Cezar e Grădinarul — el rulează comenzile manuale (sudo etc).
