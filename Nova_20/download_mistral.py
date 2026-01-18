#!/usr/bin/env python3
"""
Download Mistral-7B-Instruct-v0.3 pentru Nova training
Cu 4-bit quantization pentru RTX 3090 (24GB VRAM)
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import os

print("🚀 Download Mistral-7B-Instruct-v0.3 cu 4-bit quantization")
print("=" * 60)

# Model name
model_name = "mistralai/Mistral-7B-Instruct-v0.3"

# 4-bit quantization config (QLoRA)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",  # Normal Float 4-bit
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True  # Nested quantization pentru economie RAM
)

print(f"\n📥 Descărcare model: {model_name}")
print(f"🔧 Config: 4-bit NF4 quantization + double quant")
print(f"💾 Cache location: ~/.cache/huggingface/hub/")
print()

# Download tokenizer
print("1️⃣ Download tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
print(f"   ✅ Tokenizer ready: vocab_size={len(tokenizer)}")

# Download model (4-bit quantized)
print("\n2️⃣ Download model (4-bit quantized)...")
print("   ⏳ Poate dura câteva minute (13-14GB download)...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",  # Automatic GPU placement
    trust_remote_code=True
)

print(f"   ✅ Model loaded!")
print(f"   📊 Device: {model.device}")
print(f"   🧮 Parameters: {model.num_parameters() / 1e9:.2f}B")

# Test inference
print("\n3️⃣ Test inference...")
test_prompt = "What is artificial intelligence?"
inputs = tokenizer(test_prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        temperature=0.7,
        do_sample=True
    )

generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"   Prompt: {test_prompt}")
print(f"   Output: {generated_text}")
print("   ✅ Inference funcțional!")

# Memory stats
if torch.cuda.is_available():
    allocated = torch.cuda.memory_allocated(0) / 1e9
    reserved = torch.cuda.memory_reserved(0) / 1e9
    print(f"\n📊 VRAM usage:")
    print(f"   Allocated: {allocated:.2f} GB")
    print(f"   Reserved: {reserved:.2f} GB")
    print(f"   Available for training: {24 - reserved:.2f} GB")

print("\n" + "=" * 60)
print("🎉 Mistral-7B-Instruct-v0.3 ready pentru training!")
print("\n💡 Next steps:")
print("   1. Pregătește dataset (10 animale)")
print("   2. Configurează LoRA adapters (rank 8 pentru Doica, rank 64 pentru Sora)")
print("   3. Start training cu QLoRA")
