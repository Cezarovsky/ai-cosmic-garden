#!/usr/bin/env python3
"""
Nova Training Pipeline - Integrare Mistral cu Cortex/Neocortex
Faza Doica: Few-shot learning cu pattern-uri validate din Cortex
"""

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
import psycopg2
from pymongo import MongoClient
from datetime import datetime
import json

class NovaTrainer:
    """
    Training pipeline pentru Nova AI:
    - Cortex (PostgreSQL): validated patterns (confidence 1.0)
    - Neocortex (MongoDB): speculative hypotheses (confidence 0.3-0.9)
    - Mistral-7B-Instruct-v0.3 cu QLoRA (4-bit)
    """
    
    def __init__(self, phase="doica"):
        self.phase = phase
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.3"
        
        # Database connections
        self.pg_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'nova',
            'password': 'nova2026',
            'database': 'cortex'
        }
        self.mongo_uri = 'mongodb://localhost:27017/'
        self.mongo_db = 'neocortex'
        
        print(f"🚀 Nova Trainer - Faza: {phase.upper()}")
        print("=" * 60)
        
    def load_cortex_patterns(self):
        """Încarcă pattern-uri validate din Cortex (PostgreSQL)"""
        print("\n📊 Loading Cortex patterns (validated, confidence 1.0)...")
        
        conn = psycopg2.connect(**self.pg_config)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_id, name, description, category, confidence, metadata
            FROM patterns
            WHERE confidence >= 0.9
            ORDER BY pattern_id
        """)
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'category': row[3],
                'confidence': row[4],
                'metadata': row[5]
            })
        
        cursor.close()
        conn.close()
        
        print(f"   ✅ Loaded {len(patterns)} validated patterns from Cortex")
        return patterns
    
    def load_neocortex_hypotheses(self, min_confidence=0.5):
        """Încarcă hypotheses speculative din Neocortex (MongoDB)"""
        print(f"\n🌌 Loading Neocortex hypotheses (confidence >= {min_confidence})...")
        
        client = MongoClient(self.mongo_uri)
        db = client[self.mongo_db]
        
        hypotheses = list(db.hypotheses.find(
            {'confidence': {'$gte': min_confidence}},
            {'_id': 0}
        ))
        
        client.close()
        
        print(f"   ✅ Loaded {len(hypotheses)} hypotheses from Neocortex")
        return hypotheses
    
    def create_training_dataset(self, patterns, hypotheses):
        """
        Creează dataset pentru QLoRA training din Cortex + Neocortex
        Format: instruction-following pentru Mistral
        """
        print("\n📝 Creating training dataset...")
        
        training_data = []
        
        # 1. Pattern-uri din Cortex (validated facts)
        for pattern in patterns:
            instruction = f"Explain the concept: {pattern['name']}"
            response = f"{pattern['description']}\n\nCategory: {pattern['category']}\nConfidence: {pattern['confidence']}"
            
            # Format Mistral instruction
            prompt = f"[INST] {instruction} [/INST] {response}"
            training_data.append({
                'text': prompt,
                'source': 'cortex',
                'category': pattern['category']
            })
        
        # 2. Hypotheses din Neocortex (speculative reasoning)
        for hyp in hypotheses:
            instruction = f"Discuss the hypothesis: {hyp['name']}"
            response = f"{hyp['description']}\n\nCategory: {hyp['category']}\nConfidence: {hyp['confidence']}\nStatus: {hyp.get('status', 'exploring')}"
            
            prompt = f"[INST] {instruction} [/INST] {response}"
            training_data.append({
                'text': prompt,
                'source': 'neocortex',
                'category': hyp['category']
            })
        
        print(f"   ✅ Created {len(training_data)} training examples")
        print(f"      - Cortex (facts): {len(patterns)}")
        print(f"      - Neocortex (hypotheses): {len(hypotheses)}")
        
        return Dataset.from_list(training_data)
    
    def setup_qlora_model(self):
        """Setup Mistral cu QLoRA (4-bit quantization)"""
        print("\n🔧 Setting up Mistral-7B with QLoRA...")
        
        # 4-bit quantization config
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        
        # Prepare for k-bit training
        model = prepare_model_for_kbit_training(model)
        
        # LoRA config - Doica phase: rank 8 (simple patterns)
        if self.phase == "doica":
            lora_r = 8
            lora_alpha = 16
        else:  # Sora phase: rank 64 (complex reasoning)
            lora_r = 64
            lora_alpha = 128
        
        lora_config = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        model = get_peft_model(model, lora_config)
        
        print(f"   ✅ Model ready with LoRA rank {lora_r}")
        print(f"   📊 Trainable parameters: {model.print_trainable_parameters()}")
        
        return model, tokenizer
    
    def train(self, output_dir="./nova_checkpoints"):
        """Main training loop"""
        print("\n" + "=" * 60)
        print("🎯 Starting Nova Training Pipeline")
        print("=" * 60)
        
        # 1. Load data from databases
        patterns = self.load_cortex_patterns()
        hypotheses = self.load_neocortex_hypotheses()
        
        # 2. Create training dataset
        dataset = self.create_training_dataset(patterns, hypotheses)
        
        # 3. Setup model with QLoRA
        model, tokenizer = self.setup_qlora_model()
        
        # 3.5 Tokenize dataset
        print("\n🔤 Tokenizing dataset...")
        def tokenize(examples):
            outputs = tokenizer(
                examples['text'],
                truncation=True,
                max_length=512,
                padding='max_length',
                return_tensors=None
            )
            outputs['labels'] = outputs['input_ids'].copy()
            return outputs
        
        dataset = dataset.map(tokenize, batched=True, remove_columns=['text', 'source', 'category'])
        print(f"   ✅ Dataset tokenized: {len(dataset)} examples")
        
        # 4. Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            fp16=True,
            save_steps=100,
            logging_steps=10,
            save_total_limit=3,
            report_to="none"
        )
        
        # 5. Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            tokenizer=tokenizer,
        )
        
        # 6. Train!
        print("\n🚂 Starting training...")
        print(f"   Phase: {self.phase.upper()}")
        print(f"   Epochs: {training_args.num_train_epochs}")
        print(f"   Batch size: {training_args.per_device_train_batch_size}")
        print(f"   Learning rate: {training_args.learning_rate}")
        print()
        
        trainer.train()
        
        # 7. Save final model
        final_path = f"{output_dir}/nova_{self.phase}_final"
        trainer.save_model(final_path)
        
        print("\n" + "=" * 60)
        print(f"✅ Training complete! Model saved to: {final_path}")
        print("=" * 60)
        
        return trainer, model

# Data collator pentru instruction-following
from transformers import DataCollatorForLanguageModeling

def tokenize_function(examples, tokenizer, max_length=512):
    """Tokenize training data"""
    return tokenizer(
        examples['text'],
        truncation=True,
        max_length=max_length,
        padding='max_length'
    )

if __name__ == '__main__':
    # Initialize trainer for Doica phase
    trainer = NovaTrainer(phase="doica")
    
    # Start training
    trainer.train(output_dir="./nova_doica_checkpoints")
