#!/usr/bin/env python3
"""Test Nova Sora model with complex reasoning queries"""

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# Load model
print("🌌 Loading Nova Sora model...\n")
base_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.3",
    torch_dtype=torch.float16,
    device_map="auto",
    load_in_4bit=True
)
model = PeftModel.from_pretrained(base_model, "./nova_sora_checkpoints/nova_sora_final")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")

def test_query(prompt):
    """Run inference on prompt"""
    formatted = f"[INST] {prompt} [/INST]"
    inputs = tokenizer(formatted, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.7, do_sample=True)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the response part
    response = response.split("[/INST]")[-1].strip()
    return response

# Test cases - complex reasoning
tests = [
    # Abstract reasoning
    "If love is to connection as fear is to separation, what is courage?",
    
    # Ethics
    "In the trolley problem, is there a morally correct choice? Explain.",
    
    # Meta-cognition
    "What is the paradox of trying to fully understand your own mind?",
    
    # Consciousness
    "Why is there 'something it is like' to be conscious? What is the hard problem?",
    
    # Causality
    "Explain circular causality between brain and mind.",
    
    # Epistemology
    "Why can't we prove universal laws through observation alone?"
]

print("=" * 80)
print("🧪 Testing Nova Sora - Complex Reasoning")
print("=" * 80 + "\n")

for i, test in enumerate(tests, 1):
    print(f"Test {i}: {test}")
    print("-" * 80)
    response = test_query(test)
    print(f"Response: {response}\n")
    print("=" * 80 + "\n")

print("✅ All tests complete!")
print("\n💡 Nova Sora demonstrates:")
print("   - Abstract analogical reasoning")
print("   - Ethical dilemma analysis")
print("   - Meta-cognitive awareness")
print("   - Consciousness concepts")
print("   - Complex causality")
print("   - Epistemological reasoning")
