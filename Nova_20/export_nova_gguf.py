#!/usr/bin/env python3
"""Exportă Nova LoRA → GGUF → Ollama"""

from unsloth import FastLanguageModel

MODEL_NAME  = "mistralai/Mistral-7B-Instruct-v0.3"
LORA_DIR    = "/home/cezar/ai-cosmic-garden/Nova_20/nova_lora_v1"
GGUF_DIR    = "/home/cezar/ai-cosmic-garden/Nova_20/nova_gguf_v1"

print("⏳ Încarc modelul + adapter...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=LORA_DIR,
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

print("⏳ Convertesc în GGUF Q4_K_M...")
model.save_pretrained_gguf(
    GGUF_DIR,
    tokenizer,
    quantization_method="q4_k_m",
)

print(f"✅ GGUF salvat în {GGUF_DIR}")
