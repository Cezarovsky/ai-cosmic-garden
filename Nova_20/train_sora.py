#!/usr/bin/env python3
"""
Nova Sora Phase Training
- LoRA rank 64 (vs 8 in Doica)
- Abstract reasoning, ethics, meta-cognition
- 25 hypotheses from Neocortex + 73 patterns from Cortex
"""

import sys
sys.path.append('/home/cezar/ai-cosmic-garden/Nova_20')

from nova_trainer import NovaTrainer

if __name__ == "__main__":
    print("🌌 Starting Sora Phase Training")
    print("=" * 70)
    print()
    print("Phase: SORA")
    print("LoRA rank: 64 (vs 8 in Doica)")
    print("Alpha: 128 (vs 16 in Doica)")
    print("Trainable params: ~55M (vs 6.8M in Doica)")
    print()
    print("Dataset:")
    print("  - Cortex: 73 validated patterns (confidence 1.0)")
    print("  - Neocortex: 25 hypotheses (confidence 0.5-0.9)")
    print("  - Total: 98 training examples")
    print()
    print("Expected training time: ~20-30 minutes")
    print("=" * 70)
    print()
    
    trainer = NovaTrainer(phase="sora")
    trainer.train(output_dir="./nova_sora_checkpoints")
    
    print()
    print("=" * 70)
    print("✅ Sora phase training complete!")
    print("=" * 70)
