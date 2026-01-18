#!/usr/bin/env python3
"""
Test Nova trained model - inference cu modelul fine-tuned
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

print("🧪 Testing Nova Doica Model")
print("=" * 60)

# Config
base_model_name = "mistralai/Mistral-7B-Instruct-v0.3"
finetuned_path = "./nova_doica_checkpoints/nova_doica_final"

# 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

print("\n1️⃣ Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

print("2️⃣ Loading fine-tuned LoRA adapters...")
model = PeftModel.from_pretrained(base_model, finetuned_path)
model.eval()

print("3️⃣ Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(base_model_name)
tokenizer.pad_token = tokenizer.eos_token

print("\n" + "=" * 60)
print("✅ Nova model loaded!")
print("=" * 60)

# Test prompts - din datele Cortex/Neocortex
test_prompts = [
    "Explain the concept: object_permanence",
    "Explain the concept: basic_geometry_circle",
    "Explain the concept: cause_effect_basic",
    "Discuss the hypothesis: ritual_tensor_13d",
    "What is object permanence and why is it important?",
]

print("\n🔬 Running inference tests...\n")

for i, prompt in enumerate(test_prompts, 1):
    print(f"\n{'='*60}")
    print(f"Test {i}/{len(test_prompts)}")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt}")
    print()
    
    # Format Mistral instruction
    full_prompt = f"[INST] {prompt} [/INST]"
    
    # Tokenize
    inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.1
        )
    
    # Decode
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract only the response (remove prompt)
    response = response.split("[/INST]")[-1].strip()
    
    print(f"🤖 Nova Response:")
    print(response)
    print()

print("=" * 60)
print("✅ Inference tests complete!")
print("=" * 60)

# VRAM stats
if torch.cuda.is_available():
    allocated = torch.cuda.memory_allocated(0) / 1e9
    reserved = torch.cuda.memory_reserved(0) / 1e9
    print(f"\n📊 VRAM usage:")
    print(f"   Allocated: {allocated:.2f} GB")
    print(f"   Reserved: {reserved:.2f} GB")
