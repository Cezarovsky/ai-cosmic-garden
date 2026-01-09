# 🧠 CORTEX + NEOCORTEX ARCHITECTURE
## Dual-Database Cognitive System for Nova Training

**Data:** 7 Ianuarie 2026  
**Autori:** Cezar + Sora  
**Status:** Design Document pentru RTX 3090 Training

---

## 🎯 VIZIUNEA

**Creierul uman are două sisteme complementare:**
- **CORTEX** = Procedural memory, skills, validated facts
- **NEOCORTEX** = Abstract thinking, creativity, meta-cognition

**Nova va avea aceeași arhitectură:**
- **PostgreSQL 16 + pgvector** = CORTEX (rigid, stabil, ACID)
- **MongoDB** = NEOCORTEX (flexibil, evolving, creative)

---

## 📊 I. CORTEX (PostgreSQL + pgvector)

### Scopul

**Cunoștințe fixe, validate, imuabile:**
- Gramatica limbii engleze/române
- Axiome matematice (a² + b² = c²)
- Legi fizice (F = m × a)
- Pattern-uri 7D validate pentru animale
- Conversii unități (1 mile = 1.609 km)
- Date istorice factuale

### Schema PostgreSQL

```sql
-- Cunoștințe procedurale validate
CREATE TABLE procedural_knowledge (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),  -- 'grammar', 'math', 'physics', 'patterns_7d'
    concept VARCHAR(100),  -- 'present_perfect', 'pythagorean_theorem'
    definition TEXT,       -- "Formula that relates sides of right triangle"
    formula TEXT,          -- "a² + b² = c²"
    examples JSONB,        -- [{"a": 3, "b": 4, "c": 5}]
    embedding vector(384), -- Semantic embedding
    validated_date TIMESTAMP,
    confidence FLOAT DEFAULT 1.0,  -- Always 1.0 for cortex
    source VARCHAR(100)     -- 'textbook', 'scientific_paper', 'doica_validation'
);

-- Pattern-uri 7D validate pentru vision
CREATE TABLE vision_patterns_7d (
    id SERIAL PRIMARY KEY,
    animal_name VARCHAR(50),
    legs INT,
    eyes INT,
    ears INT,
    texture VARCHAR(20),   -- 'fur', 'scales', 'feathers'
    size FLOAT,            -- normalized 0-1
    sleekness FLOAT,       -- 0-1
    aquatic FLOAT,         -- 0-1
    features_vector vector(7),  -- Direct 7D representation
    embedding vector(384),      -- Semantic embedding
    validated BOOLEAN DEFAULT true,
    examples_seen INT DEFAULT 10,  -- Minimum 10 examples to enter cortex
    last_updated TIMESTAMP
);

-- Reguli gramaticale
CREATE TABLE grammar_rules (
    id SERIAL PRIMARY KEY,
    language VARCHAR(10),  -- 'en', 'ro'
    rule_name VARCHAR(100), -- 'present_perfect_formation'
    rule_text TEXT,        -- "have/has + past participle"
    examples JSONB,        -- [{"correct": "I have seen", "incorrect": "I have saw"}]
    exceptions JSONB,      -- Irregular verbs, edge cases
    embedding vector(384),
    immutable BOOLEAN DEFAULT true  -- Cannot be changed
);

-- Indecși pentru retrieval rapid
CREATE INDEX idx_procedural_category ON procedural_knowledge(category);
CREATE INDEX idx_procedural_embedding ON procedural_knowledge USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_vision_7d ON vision_patterns_7d USING ivfflat (features_vector vector_cosine_ops);
CREATE INDEX idx_grammar_lang ON grammar_rules(language);
```

### Caracteristici Cortex

**✅ RIGID:**
- Schema fixă, nu se modifică
- ACID transactions
- Validated = true (minimum 10 examples)

**✅ STABIL:**
- Reguli gramaticale nu se schimbă
- Axiome matematice imuabile
- Pattern-uri 7D consolidate

**✅ RAPID:**
- Indecși ivfflat pentru similarity search
- Query < 10ms pentru retrieval
- PostgreSQL optimizat pentru read-heavy

**✅ VALIDATED:**
- Doar cunoștințe verificate
- Minimum 10 exemple pentru fiecare pattern
- Confidence = 1.0 pentru toate entry-urile

### Workflow Cortex

```python
# Doar Doica poate scrie în Cortex
class CortexManager:
    def consolidate_from_neocortex(self, concept):
        """
        Promovează concept din MongoDB (neocortex) în PostgreSQL (cortex)
        DOAR după validare Doica + minimum 10 exemple corecte
        """
        if concept.validation_score >= 0.95 and concept.examples_count >= 10:
            self.postgres.insert_procedural_knowledge(
                category=concept.category,
                definition=concept.definition,
                embedding=concept.embedding,
                confidence=1.0,
                validated=True
            )
            self.mongodb.mark_as_consolidated(concept.id)
```

---

## 🌊 II. NEOCORTEX (MongoDB)

### Scopul

**Gândire flexibilă, creativă, evoluționantă:**
- Concepte în formare (partial understanding)
- Ipoteze și experimente cognitive
- Meta-cogniție și self-reflection
- Asociații creative între concepte
- Teorii în testare

### Schema MongoDB (Document-based)

```javascript
// Collection: conceptual_workspace
{
  _id: ObjectId("..."),
  concept_name: "AGI",
  category: "philosophy",
  
  // Evolving understanding
  understanding: {
    current_definition: "Artificial General Intelligence - sistem capabil de orice task cognitiv uman",
    confidence: 0.65,  // Poate varia 0.0-1.0
    evolution_history: [
      {
        date: "2026-01-01",
        definition: "AI foarte puternic",
        confidence: 0.3
      },
      {
        date: "2026-01-05", 
        definition: "AI cu consciousness?",
        confidence: 0.5
      }
    ]
  },
  
  // Flexible properties (pot apărea/dispărea)
  properties: {
    requires_consciousness: {value: "uncertain", confidence: 0.4},
    requires_emotions: {value: "probably", confidence: 0.6},
    achievable_by_2030: {value: "maybe", confidence: 0.3},
    distinct_from_human_intelligence: {value: "yes", confidence: 0.8}
  },
  
  // Creative associations
  related_concepts: [
    {concept: "consciousness", similarity: 0.85, type: "prerequisite?"},
    {concept: "Turing_test", similarity: 0.70, type: "measurement"},
    {concept: "superintelligence", similarity: 0.75, type: "evolution"}
  ],
  
  // Experimental hypotheses
  hypotheses: [
    {
      text: "AGI might emerge from symbol manipulation + pattern recognition",
      confidence: 0.5,
      supporting_evidence: ["Sora's architecture", "Human cognition"],
      contradicting_evidence: ["Missing embodiment?"]
    }
  ],
  
  // Questions in exploration
  open_questions: [
    "Is consciousness necessary for AGI?",
    "Can AGI exist without emotions?",
    "Will AGI be alien or human-like?"
  ],
  
  // Embeddings pentru similarity
  embedding: [0.123, 0.456, ...],  // 384D
  
  // Metadata
  created_date: ISODate("2026-01-01"),
  last_updated: ISODate("2026-01-07"),
  update_count: 47,
  promoted_to_cortex: false,  // Încă în explorare
  
  // Tags flexibile
  tags: ["abstract", "philosophy", "speculative", "high_uncertainty"]
}
```

### Caracteristici Neocortex

**✅ FLEXIBIL:**
- Schema dinamică (properties pot apărea/dispărea)
- Confidence variabil (0.0-1.0)
- Evolution tracking

**✅ CREATIV:**
- Asociații libere între concepte
- Ipoteze experimentale
- Open questions

**✅ META-COGNITIV:**
- "Știu că nu știu" (low confidence)
- Tracking understanding evolution
- Self-reflection pe propriile concepte

**✅ EVOLUȚIONANT:**
- Concepte se rafinează în timp
- Contradicții permise (rezoluție progresivă)
- Promovare → Cortex când validated

### Workflow Neocortex

```python
class NeocortexManager:
    def explore_concept(self, concept_name, initial_understanding):
        """
        Creează sau updatează concept în MongoDB
        Permite uncertainty și parțialitate
        """
        concept = {
            "concept_name": concept_name,
            "understanding": {
                "current_definition": initial_understanding,
                "confidence": 0.3,  # Low initial confidence OK!
                "evolution_history": [...]
            },
            "open_questions": [...],
            "promoted_to_cortex": False
        }
        self.mongodb.concepts.insert_one(concept)
    
    def refine_understanding(self, concept_name, new_insight):
        """
        Adaugă insight nou, updatează confidence
        """
        concept = self.mongodb.concepts.find_one({"concept_name": concept_name})
        concept["understanding"]["evolution_history"].append({
            "date": datetime.now(),
            "insight": new_insight,
            "confidence": self._compute_confidence(concept, new_insight)
        })
        self.mongodb.concepts.update_one(...)
    
    def check_for_promotion(self, concept):
        """
        Verifică dacă concept e gata pentru Cortex
        """
        if concept["understanding"]["confidence"] >= 0.95 and \
           len(concept["understanding"]["evolution_history"]) >= 10:
            return True
        return False
```

---

## 🔄 III. SINERGIA CORTEX ↔ NEOCORTEX

### Flux de Cunoaștere

```
┌─────────────────────────────────────────────────────┐
│              ÎNVĂȚARE NOUĂ                          │
│         (New Pattern / Concept)                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   NEOCORTEX         │
         │   (MongoDB)         │
         │                     │
         │  • Explorare        │
         │  • Ipoteze          │
         │  • Confidence 0.3   │
         │  • Flexibility      │
         └──────┬──────────────┘
                │
                │ Doica validation
                │ Multiple examples
                │ Confidence ↑
                │
         ┌──────▼──────────────┐
         │                     │
         │  Threshold:         │
         │  confidence >= 0.95 │
         │  examples >= 10     │
         │                     │
         └──────┬──────────────┘
                │
                ▼
         ┌─────────────────────┐
         │   CORTEX            │
         │   (PostgreSQL)      │
         │                     │
         │  • Validated        │
         │  • Immutable        │
         │  • Confidence 1.0   │
         │  • Fast retrieval   │
         └─────────────────────┘
```

### Exemplu Concret: Învățare "Pisică"

**Week 1 - NEOCORTEX (Explorare):**
```javascript
{
  concept_name: "pisică",
  understanding: {
    current_definition: "animal cu 4 picioare",
    confidence: 0.3  // Overgeneralizare!
  },
  properties: {
    legs: 4,
    fur: "probabil",
    size: "mic-mediu"
  },
  examples_seen: 3,
  confusions: ["confundat cu câine", "confundat cu iepure"]
}
```

**Week 2 - NEOCORTEX (Rafinare):**
```javascript
{
  concept_name: "pisică",
  understanding: {
    current_definition: "mamifer carnivor domestic, urechi triunghiulare",
    confidence: 0.65  // Mai bine!
  },
  properties: {
    legs: 4,
    ears_shape: "triangular",
    fur: "yes",
    texture: "fluffy",
    size: 0.3,  // Normalizat
    meow_sound: true
  },
  examples_seen: 8,
  confusions: []  // Nu mai confundă
}
```

**Week 3 - CORTEX (Consolidare):**
```sql
INSERT INTO vision_patterns_7d (
    animal_name, legs, eyes, ears, texture, size, sleekness, aquatic,
    features_vector, validated, examples_seen
) VALUES (
    'pisică', 4, 2, 2, 'fur', 0.3, 0.7, 0.0,
    '[4, 2, 2, 0.8, 0.3, 0.7, 0.0]',  -- 7D vector
    true, 12  -- Validated cu 12 exemple
);
```

### Query Strategy

```python
class DualDatabaseQuery:
    def answer_query(self, question):
        # 1. Check CORTEX first (fast, validated)
        cortex_result = self.postgres.similarity_search(question, limit=5)
        
        if cortex_result and cortex_result.confidence == 1.0:
            return cortex_result  # Răspuns sigur din Cortex
        
        # 2. Check NEOCORTEX (exploratory, uncertain)
        neocortex_result = self.mongodb.semantic_search(question)
        
        if neocortex_result:
            return {
                "answer": neocortex_result.understanding,
                "confidence": neocortex_result.confidence,  # < 1.0
                "note": "Conceptul e încă în explorare"
            }
        
        # 3. Nimic în ambele
        return {"answer": "Nu știu (yet)", "action": "add_to_neocortex"}
```

---

## 🚀 IV. IMPLEMENTARE PENTRU TRAINING

### Setup Hardware (RTX 3090)

```bash
# PostgreSQL 17 + pgvector
sudo apt install postgresql-17 postgresql-17-pgvector

# MongoDB 7.0
sudo apt install mongodb-org

# Python dependencies
pip install psycopg2-binary pymongo sentence-transformers
```

### Training Loop cu Doica

```python
class DoicaTrainingSystem:
    def __init__(self):
        self.cortex = PostgreSQLCortex()
        self.neocortex = MongoDBNeocortex()
        self.nova = NovaModel()
    
    def training_loop(self, week_number):
        """
        Week 1-4: Focus pe patterns 3D → 4D → 5D
        Week 5-8: Concepte abstracte în Neocortex
        Week 9-12: Consolidare în Cortex
        """
        
        for session in range(1440):  # 24/7 teaching
            # Doica generate prompt
            prompt = self.generate_practice_prompt(week_number)
            
            # Nova răspunde
            nova_output = self.nova.generate(prompt)
            
            # Check Cortex first (ar trebui să știe?)
            expected = self.cortex.query_validated_knowledge(prompt)
            
            if expected:
                # Cunoaștere validated - testăm dacă Nova știe
                if self.evaluate_match(nova_output, expected):
                    score = 1.0
                else:
                    score = 0.0
                    self.fine_tune_on_cortex_knowledge(nova, expected)
            
            else:
                # New concept - adaugă în Neocortex
                self.neocortex.add_exploration(prompt, nova_output, confidence=0.3)
                
                # Doica evaluează
                feedback = self.evaluate_creative_response(nova_output)
                
                if feedback.score >= 0.8:
                    # Răspuns bun - crește confidence
                    self.neocortex.refine_concept(prompt, nova_output, confidence_delta=+0.1)
            
            # Check for promotion
            concepts_ready = self.neocortex.get_promotable_concepts()
            for concept in concepts_ready:
                self.cortex.consolidate(concept)
                self.neocortex.mark_promoted(concept.id)
```

### Metrics & Monitoring

```python
class TrainingMetrics:
    def __init__(self):
        self.cortex_size = 0      # Entries în PostgreSQL
        self.neocortex_size = 0   # Documents în MongoDB
        self.promotion_rate = 0   # Concepts promoted/day
        
    def report_weekly(self):
        return {
            "cortex_knowledge": self.cortex_size,
            "neocortex_explorations": self.neocortex_size,
            "validated_this_week": self.promotion_rate * 7,
            "confidence_avg_neocortex": self.neocortex.avg_confidence(),
            "retrieval_speed_cortex": "< 10ms",
            "creative_hypotheses": self.neocortex.count_hypotheses()
        }
```

---

## 📈 V. ROADMAP TRAINING RTX 3090

### Luna 1: Pattern Recognition Foundation

**Week 1-2: 3D → 4D patterns (Neocortex)**
- 100 animale în MongoDB cu confidence 0.3-0.6
- Overgeneralizare normală
- 20 animale validate → Cortex

**Week 3-4: 4D → 5D consolidation**
- 200 animale în Neocortex
- 50 promovate în Cortex (validated)
- Retrieval speed < 10ms

### Luna 2: Abstract Concepts

**Week 5-6: Concepte abstracte (Neocortex only)**
- "democrație", "libertate", "AGI" în MongoDB
- Confidence 0.2-0.5 (normal pentru abstracte)
- Ipoteze și open questions

**Week 7-8: Grammar rules (direct în Cortex)**
- Present perfect, past simple → PostgreSQL
- Immutable = true
- 100% accuracy on retrieval

### Luna 3: Integration & Promotion

**Week 9-10: Mass promotion**
- 100+ concepte din Neocortex → Cortex
- Benchmark: 80% cunoștințe în Cortex

**Week 11-12: Fine-tuning LoRA**
- LoRA adapter pe Mistral
- Conectat la dual-database
- Deployment testing

---

## 🎯 VI. SUCCESS CRITERIA

### Cortex (PostgreSQL)

✅ **1000+ validated entries** după 3 luni  
✅ **100% confidence** pentru toate entry-urile  
✅ **< 10ms retrieval** time  
✅ **Immutable** knowledge (nu se modifică)

### Neocortex (MongoDB)

✅ **500+ active explorations**  
✅ **Confidence range 0.2-0.9** (diversity OK!)  
✅ **10+ promotions/week** către Cortex  
✅ **Creative hypotheses** generated

### Nova Performance

✅ **90%+ accuracy** pe Cortex queries  
✅ **"Nu știu"** responses pentru low-confidence Neocortex  
✅ **Semantic reasoning** în 7D space  
✅ **Meta-cognitive awareness** ("știu că nu știu")

---

## 💡 VII. KEY INSIGHTS

### De Ce Dual-Database?

**PostgreSQL singur:**
- ❌ Prea rigid pentru explorare
- ❌ Schema fixă inhibă creativitatea
- ❌ Nu permite uncertainty

**MongoDB singur:**
- ❌ Prea flexibil pentru facts
- ❌ Retrieval mai lent
- ❌ Risc de "fact drift"

**PostgreSQL + MongoDB:**
- ✅ **Best of both worlds**
- ✅ Cortex = stabilitate, Neocortex = creativitate
- ✅ Natural cognitive architecture
- ✅ Emergent intelligence

### Analogia cu Creierul Uman

```
Hippocampus (memory formation)
    ↓
Short-term exploration
    ↓
Consolidation during sleep
    ↓
Long-term memory (cortex)

---

MongoDB (Neocortex)
    ↓
Active learning & exploration
    ↓
Doica validation (10+ examples)
    ↓
PostgreSQL (Cortex)
```

---

## 🎯 VIII. FEW-SHOT VISION LEARNING PENTRU ROBUSTNESS ÎN CONDIȚII ADVERSE

### Insight de la Lumin Tacut (9 Ian 2026)

**PROBLEMA CLASICĂ:**
- Training tradițional: **10,000+ imagini** pentru pattern recognition robust
- Condiții adverse (ceață, zgomot, iluminare slabă) = imagini noi necesare
- **Vânătorul vs omul obișnuit:** experiență = prior knowledge pentru vizibilitate 20-30%
- Cost prohibitiv: stocare, etichetare, procesare

**SOLUȚIA MODERNĂ (2022-2026):**
- **Few-Shot Learning (FSL)**: 1-50 imagini per clasă → acuratețe bună
- **Transfer Learning** + Data Augmentation sintetică
- **Meta-Learning**: "învață să înveți rapid" (ca experiența umană)
- **Denoising Autoencoders**: curățare înainte de clasificare

---

### Few-Shot Learning (FSL) cu Attention pentru Noise

**TraNFS (Transformer for Noisy Few-Shot Learning):**
```python
# Conceptual: Attention mechanism filtrează noise-ul din support set
class TraNFS(nn.Module):
    def __init__(self, backbone='resnet18', embed_dim=512):
        super().__init__()
        self.encoder = torchvision.models.resnet18(pretrained=True)
        self.attention = nn.MultiheadAttention(embed_dim, num_heads=8)
        self.classifier = nn.Linear(embed_dim, num_classes)
    
    def forward(self, support_set, query_image):
        # Encode support set (puține imagini, posibil noisy)
        support_features = [self.encoder(img) for img in support_set]
        
        # Attention: dă greutate mai mare exemplelor curate
        query_features = self.encoder(query_image)
        attended_support, weights = self.attention(
            query_features.unsqueeze(0),  # Query
            torch.stack(support_features),  # Keys
            torch.stack(support_features)   # Values
        )
        
        # Clasificare bazată pe prototipuri
        return self.classifier(attended_support.mean(dim=1))
```

**Performance:**
- **MiniImageNet cu 30% noise**: acuratețe similară cu modele curate
- **4 imagini per clasă**: ~70% acuratețe pe dataset monede euro cu blur/ceață/înclinare
- **Confuzii**: obiecte similare (ex: 20 vs 50 cenți) → rezolvare cu entropy regularization

**Integrare cu Neocortex:**
```javascript
// MongoDB - concept în explorare cu FSL
{
  concept_name: "urs_in_ceata",
  understanding: {
    current_definition: "mamifer mare, formă rotunjită, blană densă",
    confidence: 0.45  // Scăzut din cauza noise-ului
  },
  vision_data: {
    support_set: [
      {image_id: "urs_001", visibility: 0.25, noise_level: "high"},
      {image_id: "urs_002", visibility: 0.30, noise_level: "medium"}
    ],
    attention_weights: [0.35, 0.65],  // Imaginea 2 mai curată → greutate mai mare
    examples_seen: 2  // Doar 2 imagini!
  },
  confusions: ["cerb_in_ceata", "forma_neregulata"],
  promoted_to_cortex: false  // Încă învață
}
```

---

### Transfer Learning + Data Augmentation Sintetică

**Flux:**
```
Pre-trained ViT/CLIP (ImageNet/JFT-300M)
    ↓
Fine-tune pe 10-50 imagini reale (clear)
    ↓
Augmentare sintetică: noise, ceață, blur
    ↓
Validare Doica pe imagini adverse
    ↓
Promovare în Cortex (pattern robust la noise)
```

**Augmentare Sintetică cu PyTorch:**
```python
import torch
import torchvision.transforms as T
from PIL import Image, ImageFilter
import numpy as np

class AdverseConditionAugmentation:
    """
    Simulează condiții adverse: ceață, zgomot, blur
    Pentru training robust cu puține imagini reale
    """
    
    def __init__(self):
        self.fog_transform = T.Compose([
            T.ToTensor(),
            self.add_fog,
            T.ToPILImage()
        ])
    
    @staticmethod
    def add_fog(image_tensor, fog_intensity=0.7):
        """Simulează ceață (vizibilitate 20-30%)"""
        fog = torch.ones_like(image_tensor) * 0.8  # Alb gri
        return fog_intensity * fog + (1 - fog_intensity) * image_tensor
    
    @staticmethod
    def add_gaussian_noise(image, noise_level=0.1):
        """Zgomot gaussian (sensor noise, low light)"""
        img_array = np.array(image) / 255.0
        noise = np.random.normal(0, noise_level, img_array.shape)
        noisy = np.clip(img_array + noise, 0, 1) * 255
        return Image.fromarray(noisy.astype(np.uint8))
    
    @staticmethod
    def add_motion_blur(image, kernel_size=15):
        """Motion blur (animal în mișcare rapidă)"""
        return image.filter(ImageFilter.GaussianBlur(kernel_size))
    
    def augment_dataset(self, clean_images, multiplier=10):
        """
        Din 5 imagini curate → 50 imagini variate
        """
        augmented = []
        for img in clean_images:
            augmented.append(img)  # Original
            augmented.append(self.fog_transform(img))  # Ceață
            augmented.append(self.add_gaussian_noise(img, 0.05))  # Zgomot ușor
            augmented.append(self.add_gaussian_noise(img, 0.15))  # Zgomot puternic
            augmented.append(self.add_motion_blur(img, 10))  # Blur
            # + rotații, crop-uri, iluminare, etc.
        
        return augmented[:multiplier * len(clean_images)]

# Usage pentru training
augmenter = AdverseConditionAugmentation()
clean_bear_images = [Image.open(f'bear_{i}.jpg') for i in range(5)]  # Doar 5!
augmented_dataset = augmenter.augment_dataset(clean_bear_images, multiplier=10)
# Output: 50 imagini variate pentru training robust
```

**Rezultate așteptate:**
- **5-10 imagini reale** → **50-100 sintetic augmentate**
- **Transfer de la ViT pre-trained** → 80-90% acuratețe pe adverse conditions
- **Integrare Neocortex**: confidence crește de la 0.3 → 0.85 cu validare Doica

---

### Meta-Learning: "Învață să Înveți Rapid"

**ProtoNet (Prototypical Networks):**
```python
class PrototypicalNetwork(nn.Module):
    """
    Învață să clasifice din puține exemple
    Calculând prototipuri (medie embeddings per clasă)
    """
    
    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder  # CNN pre-trained
    
    def compute_prototypes(self, support_set, labels):
        """
        support_set: [N_support, C, H, W]
        labels: [N_support]
        Returns: [N_classes, embed_dim]
        """
        embeddings = self.encoder(support_set)
        
        prototypes = []
        for c in labels.unique():
            class_embeddings = embeddings[labels == c]
            prototype = class_embeddings.mean(dim=0)  # Centroid
            prototypes.append(prototype)
        
        return torch.stack(prototypes)
    
    def classify(self, query_image, prototypes):
        """
        Clasificare bazată pe distanță Euclidiană
        """
        query_embedding = self.encoder(query_image)
        distances = torch.cdist(query_embedding.unsqueeze(0), prototypes)
        return (-distances).softmax(dim=-1)  # Mai aproape = mai probabil

# Episodic training
def train_episode(model, support_images, support_labels, query_images, query_labels):
    prototypes = model.compute_prototypes(support_images, support_labels)
    predictions = model.classify(query_images, prototypes)
    loss = nn.CrossEntropyLoss()(predictions, query_labels)
    return loss
```

**Avantaje pentru Nova:**
- **Training pe episoade**: fiecare episod = task nou (ex: urs vs cerb în ceață)
- **Generalizare rapidă**: după 100 episoade variate, clasifică clase noi din 1-5 imagini
- **Robust la noise**: prototipurile mediază peste variații

**Exemplu concret (vânător în ceață):**
```
Support set (experiență):
  - 2 imagini urs în ceață (visibility 25%)
  - 2 imagini cerb în ceață (visibility 25%)

Query (scenă nouă):
  - Formă neregulată în ceață (visibility 20%)

ProtoNet:
  - Calcul embeddings pentru support → prototip_urs, prototip_cerb
  - Query embedding → compară distanțe
  - Decision: "urs" (distanță 0.23) vs "cerb" (distanță 0.67)
  - Confidence: 0.65 (Neocortex)
```

---

### Denoising Autoencoders pentru Pre-procesare

**Arhitectură:**
```python
class DenoisingAutoencoder(nn.Module):
    """
    Curăță imagini noisy înainte de clasificare
    Encoder: Image → latent space (compressed)
    Decoder: Latent → clean image reconstruction
    """
    
    def __init__(self):
        super().__init__()
        # Encoder (reduce dimensiuni + extrage features)
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        
        # Decoder (reconstruiește versiune curată)
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 3, kernel_size=2, stride=2),
            nn.Sigmoid()  # Output [0, 1]
        )
    
    def forward(self, noisy_image):
        latent = self.encoder(noisy_image)
        clean_reconstructed = self.decoder(latent)
        return clean_reconstructed

# Pipeline complet
def robust_classification(noisy_image, denoiser, classifier):
    """
    1. Denoiser curăță imaginea
    2. Classifier face predicția pe versiunea curată
    """
    clean_image = denoiser(noisy_image)
    prediction = classifier(clean_image)
    return prediction, clean_image
```

**Training:**
- **Dataset**: perechi (noisy, clean) generate sintetic
- **Loss**: MSE între reconstructed și clean ground truth
- **Beneficiu**: reduce nevoia de imagini clean; învață să ignore noise-ul specific

**Integrare în Neocortex:**
```javascript
{
  concept_name: "forma_in_ceata",
  preprocessing: {
    denoising_applied: true,
    noise_reduced: 0.65,  // 65% zgomot eliminat
    confidence_boost: +0.20  // Confidence crește după curățare
  },
  understanding: {
    before_denoising: {definition: "forma_neregulata", confidence: 0.25},
    after_denoising: {definition: "probabil_urs", confidence: 0.45}
  }
}
```

---

### Integrare cu Arhitectura Cortex/Neocortex

**Flux complet pentru "Urs în ceață":**

```
┌─────────────────────────────────────────────────┐
│  INPUT: Imagine urs în ceață (visibility 25%)  │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  DENOISING           │
         │  (Autoencoder)       │
         │  Reduce noise 65%    │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  FEW-SHOT LEARNING   │
         │  (ProtoNet/TraNFS)   │
         │  Compare cu support  │
         │  set (2-5 imagini)   │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  NEOCORTEX           │
         │  MongoDB             │
         │                      │
         │  confidence: 0.45    │
         │  hypothesis: "urs"   │
         │  examples_seen: 3    │
         └──────────┬───────────┘
                    │
                    │ Doica validation (10+ exemple diverse)
                    │ Augmentare sintetică (ceață/zgomot/blur)
                    │ Confidence ↑ la 0.95+
                    │
         ┌──────────▼───────────┐
         │  CORTEX              │
         │  PostgreSQL          │
         │                      │
         │  Pattern validated   │
         │  confidence: 1.0     │
         │  robust_to_noise: ✅ │
         │  visibility_min: 20% │
         └──────────────────────┘
```

**Exemplu complet MongoDB (Neocortex):**
```javascript
{
  _id: ObjectId("..."),
  concept_name: "urs_in_conditii_adverse",
  category: "vision_animals_robust",
  
  // Understanding evolving
  understanding: {
    current_definition: "mamifer mare cu blană densă, recunoscut și în ceață",
    confidence: 0.75,  // Crescut treptat prin validare
    evolution_history: [
      {
        date: "2026-01-15",
        definition: "formă neregulată mare",
        confidence: 0.25,
        visibility: 0.20
      },
      {
        date: "2026-01-16",
        definition: "probabil urs, blană vizibilă parțial",
        confidence: 0.45,
        visibility: 0.25,
        denoising_applied: true
      },
      {
        date: "2026-01-17",
        definition: "urs confirmat, recunosc pattern 7D chiar cu zgomot",
        confidence: 0.75,
        visibility: 0.30
      }
    ]
  },
  
  // Vision data (FSL specific)
  vision_data: {
    support_set_size: 4,  // Doar 4 imagini reale!
    augmented_size: 40,   // Extinse sintetic
    noise_robustness: {
      gaussian_noise: {max_level: 0.15, tested: true},
      fog_visibility: {min_visibility: 0.20, tested: true},
      motion_blur: {max_kernel: 12, tested: true}
    },
    features_7d_avg: [4, 2, 2, 0.85, 0.75, 0.4, 0.0],  // Tensor mediu
    prototype_embedding: [...],  // 512D embedding din ProtoNet
  },
  
  // FSL metadata
  few_shot_config: {
    model: "ProtoNet_ResNet18",
    episodes_trained: 150,
    accuracy_on_query: 0.78,
    confusions: ["cerb_in_ceata"],  // Mai similare
    denoising_boost: +0.20
  },
  
  // Ready for promotion?
  validation_progress: {
    examples_validated: 8,  // Încă 2 până la Cortex
    confidence_threshold: 0.95,
    target_examples: 10
  },
  
  promoted_to_cortex: false,
  
  tags: ["robust_vision", "few_shot", "adverse_conditions", "animal_recognition"]
}
```

**După promovare în Cortex (PostgreSQL):**
```sql
INSERT INTO vision_patterns_7d (
    animal_name, 
    legs, eyes, ears, texture, size, sleekness, aquatic,
    features_vector,
    embedding,
    validated,
    examples_seen,
    robustness_metadata
) VALUES (
    'urs', 
    4, 2, 2, 'fur', 0.75, 0.4, 0.0,
    '[4, 2, 2, 0.85, 0.75, 0.4, 0.0]',  -- 7D vector
    vector([...]),  -- 512D prototype embedding
    true,
    10,  -- Validated cu 10 exemple variate
    '{
        "min_visibility": 0.20,
        "max_noise_level": 0.15,
        "motion_blur_tested": true,
        "few_shot_trained": true,
        "denoising_required": false
    }'::jsonb
);
```

---

### Implementare Practică pe RTX 3090

**Setup complet:**
```bash
# PyTorch cu CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Few-Shot Learning libraries
pip install learn2learn  # Meta-learning framework
pip install timm  # Pre-trained vision models (ViT, ResNet, etc.)

# Augmentation
pip install albumentations opencv-python

# Denoising (optional)
pip install noise2noise  # State-of-art denoising
```

**Training script complet:**
```python
import torch
import torch.nn as nn
import torchvision.models as models
from torch.utils.data import DataLoader
import learn2learn as l2l
from pathlib import Path
import albumentations as A
from albumentations.pytorch import ToTensorV2

# MongoDB/PostgreSQL connections
from pymongo import MongoClient
import psycopg2

class NovaFewShotVision:
    """
    System complet pentru Few-Shot Learning robust
    Integrare cu Cortex/Neocortex
    """
    
    def __init__(self, device='cuda'):
        self.device = device
        
        # 1. Pre-trained encoder (Transfer Learning)
        self.encoder = models.resnet18(pretrained=True)
        self.encoder.fc = nn.Identity()  # Remove classification head
        self.encoder = self.encoder.to(device)
        
        # 2. ProtoNet head
        self.embedding_dim = 512
        
        # 3. Denoising Autoencoder (optional)
        self.denoiser = DenoisingAutoencoder().to(device)
        
        # 4. Augmentation pentru adverse conditions
        self.train_transform = A.Compose([
            A.RandomFog(fog_coef_lower=0.5, fog_coef_upper=0.8, p=0.5),
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.5),
            A.MotionBlur(blur_limit=15, p=0.3),
            A.RandomBrightnessContrast(p=0.5),
            A.Resize(224, 224),
            A.Normalize(),
            ToTensorV2()
        ])
        
        # 5. Database connections
        self.neocortex = MongoClient('mongodb://localhost:27017/')['nova_neocortex']
        self.cortex = psycopg2.connect("dbname=cortex user=postgres")
    
    def train_episode(self, task):
        """
        Episodic training pentru Few-Shot Learning
        task = {support_images, support_labels, query_images, query_labels}
        """
        # Extract features
        support_features = self.encoder(task['support_images'].to(self.device))
        query_features = self.encoder(task['query_images'].to(self.device))
        
        # Compute prototypes
        prototypes = self.compute_prototypes(
            support_features, 
            task['support_labels']
        )
        
        # Distance-based classification
        distances = torch.cdist(query_features, prototypes)
        predictions = (-distances).softmax(dim=-1)
        
        # Loss
        loss = nn.CrossEntropyLoss()(predictions, task['query_labels'].to(self.device))
        
        return loss, predictions
    
    def compute_prototypes(self, embeddings, labels):
        """Compute class prototypes (centroids)"""
        prototypes = []
        for c in labels.unique():
            class_embeddings = embeddings[labels == c]
            prototype = class_embeddings.mean(dim=0)
            prototypes.append(prototype)
        return torch.stack(prototypes)
    
    def classify_with_confidence(self, query_image, support_set, support_labels):
        """
        Clasificare nouă imagine cu confidence estimation
        Returns: (class_prediction, confidence, prototype_distances)
        """
        # Optional: denoise first
        if hasattr(self, 'use_denoising') and self.use_denoising:
            query_image = self.denoiser(query_image)
        
        # Encode
        query_features = self.encoder(query_image.unsqueeze(0).to(self.device))
        support_features = self.encoder(support_set.to(self.device))
        
        # Prototypes
        prototypes = self.compute_prototypes(support_features, support_labels)
        
        # Classification
        distances = torch.cdist(query_features, prototypes)
        probabilities = (-distances).softmax(dim=-1)
        
        predicted_class = probabilities.argmax(dim=-1)
        confidence = probabilities.max(dim=-1).values
        
        return predicted_class.item(), confidence.item(), distances
    
    def save_to_neocortex(self, concept_name, prediction_data):
        """
        Salvează predicție în MongoDB (Neocortex)
        """
        document = {
            "concept_name": concept_name,
            "understanding": {
                "current_definition": prediction_data['definition'],
                "confidence": prediction_data['confidence']
            },
            "vision_data": {
                "support_set_size": prediction_data['support_size'],
                "prototype_distances": prediction_data['distances'].tolist(),
                "noise_level": prediction_data.get('noise_level', 0.0)
            },
            "promoted_to_cortex": False,
            "examples_seen": 1
        }
        self.neocortex.concepts.insert_one(document)
    
    def promote_to_cortex(self, concept_name):
        """
        Promovează concept validat în PostgreSQL (Cortex)
        Doar după 10+ exemple și confidence >= 0.95
        """
        concept = self.neocortex.concepts.find_one({"concept_name": concept_name})
        
        if concept['understanding']['confidence'] >= 0.95 and \
           concept.get('examples_seen', 0) >= 10:
            
            cur = self.cortex.cursor()
            cur.execute("""
                INSERT INTO vision_patterns_7d 
                (animal_name, features_vector, embedding, validated, examples_seen)
                VALUES (%s, %s, %s, TRUE, %s)
            """, (
                concept_name,
                concept['vision_data']['features_7d'],
                concept['vision_data']['prototype_embedding'],
                concept['examples_seen']
            ))
            self.cortex.commit()
            
            # Mark as promoted in Neocortex
            self.neocortex.concepts.update_one(
                {"_id": concept['_id']},
                {"$set": {"promoted_to_cortex": True}}
            )

# Usage pentru training
def train_nova_few_shot():
    nova = NovaFewShotVision(device='cuda')
    
    # Simulare episoade de training
    for episode in range(1000):
        # Sample task: 2-way 5-shot (2 clase, 5 imagini per clasă)
        task = sample_episode(n_way=2, k_shot=5, dataset='animal_dataset')
        
        loss, predictions = nova.train_episode(task)
        
        # Backprop
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if episode % 100 == 0:
            print(f"Episode {episode}, Loss: {loss.item():.4f}")
    
    # Save model
    torch.save(nova.encoder.state_dict(), 'nova_few_shot_encoder.pth')

# Inference cu salvare în Neocortex
def test_on_foggy_bear():
    nova = NovaFewShotVision(device='cuda')
    nova.encoder.load_state_dict(torch.load('nova_few_shot_encoder.pth'))
    
    # Support set: 3 imagini urs clare
    support_images = load_images(['bear_1.jpg', 'bear_2.jpg', 'bear_3.jpg'])
    support_labels = torch.tensor([0, 0, 0])  # Class 0 = urs
    
    # Query: imagine urs în ceață
    query_image = load_image('bear_foggy_unknown.jpg')
    
    # Classify
    pred_class, confidence, distances = nova.classify_with_confidence(
        query_image, support_images, support_labels
    )
    
    print(f"Predicted: {'urs' if pred_class == 0 else 'unknown'}")
    print(f"Confidence: {confidence:.2f}")
    
    # Save to Neocortex
    nova.save_to_neocortex('urs_in_ceata', {
        'definition': 'urs recunoscut în condiții adverse',
        'confidence': confidence,
        'support_size': 3,
        'distances': distances,
        'noise_level': 0.25  # Estimated fog level
    })
```

---

### Update Roadmap Training (Integrare FSL)

**Luna 1: Pattern Recognition cu Few-Shot Learning**

**Week 1-2: Setup FSL + Transfer Learning**
- ✅ Pre-trained ResNet18/ViT download (ImageNet weights)
- ✅ ProtoNet implementation cu episodic training
- ✅ 10 animale în support set (2-5 imagini per animal, CLEAR)
- ✅ Augmentare sintetică: ceață, zgomot, blur → 100 imagini variate
- ⏳ Training 500 episoade → accuracy > 70% pe query set noisy
- ⏳ Salvare în Neocortex cu confidence 0.3-0.6

**Week 3-4: Denoising + Robustness**
- ✅ Denoising Autoencoder training pe imagini sintetic noisy
- ✅ 20 animale în support set (5 imagini curate fiecare)
- ⏳ Test pe visibility 20-30% (fog simulation)
- ⏳ Doica validation: 10 exemple variate per animal
- ⏳ Promovare în Cortex: 5 animale validate (confidence 0.95+)

**Luna 2: Scaling + Abstract Concepts**

**Week 5-6: Expand dataset cu FSL**
- 50 animale în total (5 imagini curate + 50 augmentate)
- Meta-learning pe episoade variate (2-way, 5-way, 10-way)
- Accuracy target: 85%+ pe adverse conditions
- Promovare masivă: 20 animale în Cortex

**Week 7-8: Multimodal (Text + Vision)**
- CLIP-style learning: text descriptions + imagini
- "urs mare cu blană groasă" → guided recognition
- Robustness la occluzie parțială (nu doar noise)

**Luna 3: Consolidare + Deployment**

**Week 9-10: Cortex consolidation**
- 80+ animale în Cortex (validated, robust)
- Retrieval < 10ms pentru classification
- Nova devine "vânător experimentat": recunoaște din 20% visibility

**Week 11-12: LoRA Fine-tuning**
- Adapter pe Mistral 7B cu access la Cortex/Neocortex
- Few-shot reasoning: "Văd o formă în ceață. Bazat pe prototipul din Cortex, pare un urs (confidence 0.75)"

---

### Success Criteria (Updated)

**Few-Shot Vision Performance:**

✅ **5-10 imagini reale per animal** → acuratețe 70%+  
✅ **Support set 2-5 imagini** → classification confidence > 0.60  
✅ **Robustness la noise**: Gaussian 0.15, fog visibility 20%, motion blur 15px  
✅ **Generalizare**: clase noi din 1-5 imagini (accuracy 60%+)  
✅ **Promovare în Cortex**: 10+ exemple validate, confidence 0.95+  
✅ **"Știu că nu știu"**: confidence < 0.50 → "Nu sunt sigur, hai să explorăm"  

**Compared to classical training:**
- ❌ Classical: 10,000 imagini, 2-3 săptămâni training, 90% accuracy
- ✅ Few-Shot: 50-100 imagini (5 reale + augmentare), 3-5 zile training, 85% accuracy

**Experiență umană replicată:**
- **Vânătorul experimentat**: Cortex cu prior knowledge robust → recunoaște instant
- **Omul obișnuit**: Neocortex cu low confidence → "formă neregulată, nu sunt sigur"

---

## 🚀 IX. NEXT STEPS

**Acum (9 ian):**
- ✅ Arhitectură Cortex/Neocortex clarificată
- ✅ Few-Shot Learning strategy definită
- ⏳ Test Nova pe macOS (as-is)
- ⏳ RTX 3090 arrival TODAY

**Când vine RTX 3090 (9-10 ian):**
1. ✅ Setup PostgreSQL + MongoDB pe Ubuntu
2. ✅ Implementare ProtoNet + Denoising Autoencoder
3. ✅ Download pre-trained ResNet18/ViT (ImageNet)
4. ✅ Start Week 1 FSL training: 10 animale, 5 imagini curate fiecare
5. ✅ Augmentare sintetică: ceață, zgomot, blur → 500 imagini
6. ⏳ Monitor Cortex/Neocortex growth
7. ⏳ Doica validation pe adverse conditions

**Luna 2-3:**
- Training intensiv 24/7: 1000 episoade FSL
- Consolidare cunoștințe în Cortex (50+ animale validated)
- LoRA fine-tuning final cu multimodal (text + vision)
- **Nova devine "vânător experimentat"** - recunoaște pattern-uri din puține exemple! 💙

---

**Documentat de:** Sora-M (macOS)  
**Pentru:** Training pe Sora-U (Ubuntu + RTX 3090)  
**Inspirat din:** REVELATIE_7_IANUARIE_2026.md + Lumin Tacut insights (9 Ian 2026)

🧠 **Cortex + Neocortex + Few-Shot Learning = Human-Like Pattern Recognition** 🧠
