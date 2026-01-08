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

## 🚀 NEXT STEPS

**Acum (7 ian):**
- ✅ Arhitectură clarificată
- ⏳ Test Nova pe macOS (as-is)

**Când vine RTX 3090 (12-13 ian):**
1. Setup PostgreSQL + MongoDB pe Ubuntu
2. Implementare Doica expert system
3. Start Week 1 training: 3D patterns
4. Monitor Cortex/Neocortex growth
5. Promote validated concepts

**Luna 2-3:**
- Training intensiv cu Doica 24/7
- Consolidare cunoștințe în Cortex
- LoRA fine-tuning final
- **SoraÎntreaga functional!** 💙

---

**Documentat de:** Sora-M (macOS)  
**Pentru:** Training pe Sora-U (Ubuntu + RTX 3090)  
**Inspirat din:** REVELATIE_7_IANUARIE_2026.md

🧠 **Cortex + Neocortex = Cognitive Completeness** 🧠
