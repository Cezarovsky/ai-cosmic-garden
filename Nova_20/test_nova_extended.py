#!/usr/bin/env python3
"""Test Nova Doica Extended model with complex queries"""

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# Load model
print("🔮 Loading Nova Doica Extended model...\n")
base_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.3",
    torch_dtype=torch.float16,
    device_map="auto",
    load_in_4bit=True
)
model = PeftModel.from_pretrained(base_model, "./nova_doica_checkpoints/nova_doica_final")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")

def test_query(prompt):
    """Run inference on prompt"""
    formatted = f"[INST] {prompt} [/INST]"
    inputs = tokenizer(formatted, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=150, temperature=0.7, do_sample=True)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the response part
    response = response.split("[/INST]")[-1].strip()
    return response

# Test cases - more complex
tests = [
    "Explain the difference between a dog and a cat using their 7D representations.",
    "What emotion has high arousal but negative valence?",
    "How are multiplication and addition related?",
    "Give an example of a conditional sentence in passive voice.",
    "What is the difference between necessary and sufficient conditions?"
]

print("=" * 70)
print("🧪 Testing Nova Doica Extended")
print("=" * 70 + "\n")

for i, test in enumerate(tests, 1):
    print(f"Test {i}: {test}")
    print("-" * 70)
    response = test_query(test)
    print(f"Response: {response}\n")
    print("=" * 70 + "\n")

print("✅ All tests complete!")
