# De la Întrebare la Răspuns — Pipeline complet Transformer
**Curs Agentic AI Engineer — Modul 2**
*Lumen pentru Cezar — Aprilie 2026*

---

## Diagrama generală

```
Input text (întrebare utilizator)
       │
       ▼
  1. TOKENIZARE          → tokens (bucăți de text)
       │
       ▼
  2. EMBEDDING           → vectori denși (token → numere)
       │
       ▼
  3. POSITIONAL ENCODING → adaugi poziția fiecărui token
       │
       ▼
  4. TRANSFORMER BLOCKS  → (repetat de N ori)
       │   ├── 4a. Self-Attention   (tokens vorbesc între ei)
       │   └── 4b. Feed-Forward     (tokens procesează individual)
       │
       ▼
  5. LINEAR + SOFTMAX    → probabilități peste vocabular
       │
       ▼
  6. SAMPLING/ARGMAX     → alege next token
       │
       ▼
  7. DETOKENIZARE        → text final
```

**RAG** intervine între pasul 0 și 1 — îmbogățește inputul cu context din vector DB.

---

## Pasul 1 — Tokenizare

### Ce este

Tokenizarea transformă textul brut în unități numerice pe care modelul le poate procesa.
Tokenii **nu sunt cuvinte** — sunt sub-unități de cuvinte, determinate statistic din corpus-ul de training.

### Cum funcționează — BPE (Byte Pair Encoding)

Algoritmul cel mai comun (GPT, Claude, LLaMA):

1. Pornești cu caractere individuale: `["F","e","n","r","i","r"]`
2. Numeri perechile cele mai frecvente în corpus → le mergi
3. Repeți până ai vocabularul dorit (50k-100k tokens)

Rezultat: cuvintele comune → un singur token. Cuvintele rare → mai mulți tokens.

```
"Ce este Fenrir?"
        │
        ▼
["Ce", " este", " Fen", "rir", "?"]
        │
        ▼
[4821,  1033,   12847,  9921,  136]   ← token IDs (indecși în vocabular)
```

### De ce nu cuvinte întregi?

- Vocabular finit pentru cuvinte infinite (nume proprii, limbi noi, cod)
- "Fenrir" poate fi necunoscut, dar "Fen" + "rir" sunt în vocabular
- Eficiență: `"running"` → 1 token; `"antidisestablishmentarianism"` → mai mulți

### Cum faci asta ca programator

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")

text = "Ce este Fenrir?"
tokens = tokenizer(text, return_tensors="pt")

# tokens["input_ids"] = tensor([[4821, 1033, 12847, 9921, 136]])
# tokens["attention_mask"] = tensor([[1, 1, 1, 1, 1]])  ← 1=real, 0=padding
```

### Attention mask

Când procesezi mai multe texte simultan (batch), le uniformizezi la aceeași lungime prin **padding** (tokens fictivi). Attention mask spune modelului care tokens sunt reali și care sunt padding — nu vrem ca modelul să "asculte" padding-ul.

```
Text 1: ["Ce",  "este", "Fenrir", "?",   PAD,   PAD]   → mask: [1,1,1,1,0,0]
Text 2: ["Cine", "e",   "Umbra",  "din", "joc", "?"]   → mask: [1,1,1,1,1,1]
```

---

## Pasul 2 — Embedding

### Ce este

Fiecare token ID este transformat într-un **vector dens** de numere reale.
Vectorul captează sensul semantic al tokenului.

```
token ID 12847 ("Fen") → [0.23, -0.87, 0.45, 0.12, -0.33, ...]
                                                ↑
                                         1536 dimensiuni (GPT-3)
                                          768 dimensiuni (BERT)
                                         4096 dimensiuni (LLaMA 7B)
```

### De unde vin vectorii

Dintr-o **embedding table** (matrice) — o matrice de dimensiuni `[vocab_size × embedding_dim]`:

```
vocab_size = 50.257 tokens (GPT-2)
embed_dim  = 768

Embedding table: matrice 50.257 × 768
                 ≈ 38.6 milioane de parametri
                 ↑ doar pentru embedding, înainte de orice layer
```

Fiecare rând din matrice = vectorul unui token. La training, acești vectori sunt ajustați prin backpropagation — modelul învață ce înseamnă fiecare token.

### Proprietatea cheie — similaritate semantică

Vectorii apropiați în spațiu = concepte similare:

```
embedding("lup")    ≈ embedding("câine")     ← distanță mică
embedding("lup")    ≈ embedding("Fenrir")    ← distanță mică
embedding("lup")    ≫ embedding("algoritm")  ← distanță mare
```

Celebra relație: `embedding("rege") - embedding("bărbat") + embedding("femeie") ≈ embedding("regină")`

### Cum faci asta ca programator

```python
import torch
from transformers import AutoModel, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

text = "Ce este Fenrir?"
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)

# outputs.last_hidden_state → embeddings finale (după toate Transformer blocks)
# shape: [batch_size, seq_len, hidden_dim] = [1, 5, 768]

# Pentru embedding brut (înainte de Transformer):
raw_embeddings = model.embeddings.word_embeddings(inputs["input_ids"])
# shape: [1, 5, 768]
```

### Embedding vs last_hidden_state

- **raw embedding** = vectorul inițial al tokenului, fără context
- **last_hidden_state** = embeddings după toate Transformer blocks — fiecare token știe acum despre toți ceilalți

În RAG, folosești **last_hidden_state** pentru că vrei reprezentări contextuale.

---

## Pasul 3 — Positional Encoding

### Problema

Attention nu știe ordinea tokenilor — vede o mulțime, nu o secvență.
`"Lupul prinde iepurele"` = `"Iepurele prinde lupul"` fără PE.

### Soluția

Adaugi un vector de poziție la fiecare embedding:

```
token_cu_pozitie = embedding(token) + PE(poziție)
```

### Formulă clasică (Vaswani 2017)

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d))
```

- `pos` = poziția tokenului (0, 1, 2, ...)
- `i` = indexul dimensiunii (0, 1, 2, ... d/2)
- `d` = dimensiunea embedding-ului

Dimensiunile pari folosesc sin, cele impare cos. Factorul `10000^(2i/d)` crește exponențial → frecvențe diferite per dimensiune, ca un ceas cu secunde/minute/ore.

### RoPE — varianta modernă

Modelele recente (LLaMA, Claude) folosesc **Rotary Positional Embedding**:
în loc să adaugi PE la embedding, *rotești* vectorii Q și K în spațiul complex.

Avantaj: funcționează mai bine pentru contexte lungi (200k+ tokens).

### Cum faci asta ca programator

Nu implementezi PE manual — e în model. Dar contezi pe el când:

```python
# Atenție la context window!
tokenizer.model_max_length  # câți tokens acceptă modelul

# Dacă textul e prea lung → trunchiere automată (pierzi informație)
inputs = tokenizer(
    text,
    max_length=512,
    truncation=True,
    return_tensors="pt"
)
```

---

## Pasul 4a — Self-Attention

### Intuiție

Fiecare token decide cât de mult să "asculte" din fiecare alt token.
`"Fenrir"` va asculta mult din `"lup"` și `"mitologie"`, puțin din `"Ce"` și `"?"`.

### Mecanismul Q, K, V

Din fiecare embedding de token, generezi 3 vectori prin înmulțire cu 3 matrice learnable:

```
Q (Query)  = embedding × W_Q   ← "ce caut eu?"
K (Key)    = embedding × W_K   ← "ce am eu de oferit?"
V (Value)  = embedding × W_V   ← "ce informație transport eu?"
```

Analogie cu un motor de căutare:
- **Query** = termenul tău de căutare
- **Key** = titlurile documentelor
- **Value** = conținutul documentelor

### Calculul atenției

```
Attention(Q, K, V) = softmax(Q × Kᵀ / √d_k) × V
```

Pas cu pas:
1. `Q × Kᵀ` → matrice de scoruri (cât de compatibil e fiecare Q cu fiecare K)
2. `/ √d_k` → scalare (evită gradienți prea mici la dimensiuni mari)
3. `softmax(...)` → probabilități (sumă = 1, toate pozitive)
4. `× V` → suma ponderată a valorilor

```
Token "Fenrir" are Q = [0.3, -0.1, 0.8, ...]

Scoruri față de toți ceilalți:
  "Ce"        → 0.05
  "este"      → 0.12
  "Fenrir"    → 0.45   (se ascultă pe sine)
  "lup"       → 0.38   ← relevant
          ↓
  softmax → probabilități: [0.08, 0.13, 0.42, 0.37]
          ↓
  output = 0.08×V("Ce") + 0.13×V("este") + 0.42×V("Fenrir") + 0.37×V("lup")
```

### Multi-Head Attention

În practică, Attention se face în paralel de H ori (H = heads):

```
GPT-2 base: 12 heads
GPT-3:      96 heads
```

Fiecare head are propriile W_Q, W_K, W_V → învaţă aspecte diferite ale relațiilor:
- Head 1: relații sintactice (subiect-verb)
- Head 2: relații semantice (sinonime)
- Head 3: referințe (pronume → substantiv)
- etc.

Output-urile tuturor heads se concatenează și se proiectează înapoi:
```
MultiHead(Q,K,V) = Concat(head_1, ..., head_H) × W_O
```

### Cum faci asta ca programator

```python
# Nu implementezi manual. Dar poți vizualiza attention weights:
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, output_attentions=True)

inputs = tokenizer("Fenrir este un lup", return_tensors="pt")
outputs = model(**inputs)

attentions = outputs.attentions
# attentions[layer][batch, head, token_from, token_to]
# → poți vedea ce token ascultă din ce
```

---

## Pasul 4b — Feed-Forward Network

### Ce face

Procesează fiecare token **independent**, după ce Attention a adunat contextul.
Dacă Attention = "ce informații colectez", FFN = "ce fac cu ele".

### Formula

```
FFN(x) = activation(x × W₁ + b₁) × W₂ + b₂
```

- Două transformări liniare cu o activare non-liniară între ele
- Activare uzuală: **GELU** (modelele moderne), ReLU (clasic)
- Dimensiunea internă = 4× embedding dim (de obicei):
  - embed_dim = 768 → FFN intern = 3072

### De ce 4×?

Spațiu mai mare = mai multă capacitate de reprezentare. FFN-urile stochează "fapte" despre lume — cu cât mai mare, cu atât mai multe fapte pot fi memorate.

Studii recente arată că FFN-urile funcționează ca o memorie cheie-valoare:
- **W₁** = "chei" (ce pattern de input activează)
- **W₂** = "valori" (ce informație e returnată)

### Residual connections + Layer Norm

Un Transformer block complet arată așa:

```
input x
  │
  ├──────────────────────┐
  │                      │
  ▼                      │
Attention(x)             │
  │                      │
  └──────────── + ───────┘  ← residual connection
               │
           LayerNorm
               │
  ├──────────────────────┐
  │                      │
  ▼                      │
FFN(x)                   │
  │                      │
  └──────────── + ───────┘  ← residual connection
               │
           LayerNorm
               │
           output
```

**Residual connection** = adaugi input-ul original la output → gradienții curg mai ușor la training, rețeaua poate "alege" să nu modifice nimic.

**Layer Normalization** = stabilizează valorile după fiecare operație.

---

## Pasul 5 — Linear + Softmax (Language Model Head)

### Ce face

Transformă reprezentarea finală a tokenului curent în probabilități peste întreg vocabularul.

```
hidden_state: [768 dimensiuni]
      │
      ▼
Linear(768 → 50257)   ← vocab_size
      │
      ▼
[0.0001, 0.0003, 0.42, 0.0002, ...]   ← 50257 valori
      │
      ▼
Softmax → probabilități (sumă = 1.0)
      │
      ▼
Token cel mai probabil: "este" (0.42)
```

### Partajare de greutăți

Matricea Linear de la ieșire = transpusa Embedding table de la intrare.
Același spațiu semantic → coerență între intrare și ieșire.

---

## Pasul 6 — Sampling

### Argmax (greedy)

Alege mereu tokenul cu probabilitatea maximă. Rapid, dar repetitiv.

### Temperature sampling

```python
logits = logits / temperature
probs = softmax(logits)
next_token = sample(probs)
```

- `temperature = 1.0` → distribuție originală
- `temperature < 1.0` → mai determinist (Claude în cod)
- `temperature > 1.0` → mai creativ/haotic

### Top-p (nucleus sampling)

Alege dintr-un subset de tokens care acoperă p% din probabilitate cumulativă:

```python
# top_p = 0.9 → ia cele mai probabile tokens care sumează 90%
# ignoră coada de tokens improbabile
```

Combini temperature + top-p pentru control fin al creativității.

---

## Pasul 7 — Detokenizare

Token IDs → text:

```python
output_ids = [4821, 1033, 847, 291, 12847, ...]
text = tokenizer.decode(output_ids, skip_special_tokens=True)
# → "Fenrir este un lup din mitologia nordică..."
```

---

## RAG — unde și cum intervine

RAG (Retrieval Augmented Generation) îmbogățește contextul **înainte** de Transformer.

### Fluxul complet cu RAG

```
1. INDEXARE (o singură dată, offline)
   document → chunks → embedding fiecare chunk → stocat în vector DB

2. QUERY (la fiecare întrebare)
   întrebare → embedding → similarity search → top-k chunks

3. AUGMENTARE
   prompt_final = system_prompt + chunks_relevante + întrebare_user

4. GENERARE
   prompt_final → Tokenizare → Embedding → Transformer → răspuns
```

### Cum faci asta ca programator

```python
from anthropic import Anthropic
import chromadb   # vector DB
from sentence_transformers import SentenceTransformer

# Setup
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
client_db = chromadb.Client()
collection = client_db.create_collection("documente")
claude = Anthropic()

# 1. Indexare
chunks = ["Fenrir este un lup...", "Umbra este un iepure...", "R-STDP este..."]
embeddings = embed_model.encode(chunks).tolist()
collection.add(
    documents=chunks,
    embeddings=embeddings,
    ids=["c1", "c2", "c3"]
)

# 2. Query
question = "Ce este Fenrir?"
q_embedding = embed_model.encode([question]).tolist()

results = collection.query(
    query_embeddings=q_embedding,
    n_results=3   # top-k = 3
)

top_chunks = results["documents"][0]

# 3. Augmentare
context = "\n".join(top_chunks)
prompt = f"""Context:
{context}

Întrebare: {question}
Răspunde doar pe baza contextului de mai sus."""

# 4. Generare
response = claude.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)

print(response.content[0].text)
```

---

## Rezumat — ce știe un AI Engineer despre fiecare pas

| Pas | Ce se întâmplă | Ce faci tu ca programator |
|-----|---------------|--------------------------|
| Tokenizare | text → IDs | alegi tokenizer-ul, gestionezi truncation/padding |
| Embedding | IDs → vectori | alegi dimensiunea, folosești modele pre-trained |
| Positional Encoding | adaugi poziție | respecți context window, alegi model cu RoPE pentru texte lungi |
| Attention | tokens comunică | vizualizezi pentru debug, ajustezi nr. de heads la fine-tuning |
| FFN | tokens procesează | dimensionezi corect modelul pentru task |
| Sampling | alegi next token | ajustezi temperature, top-p, top-k pentru creativitate |
| RAG | adaugi context extern | chunking strategy, alegere vector DB, top-k optim |

---

## Concepte cheie de reținut pentru interviu

**Tokenizare:** BPE, vocabular finit, attention mask pentru padding

**Embedding:** spațiu semantic, similaritate cosinus, embedding table = prima matrice uriașă

**Positional Encoding:** fără el Attention e orb la ordine, RoPE pentru contexte lungi

**Attention:** Q/K/V, softmax pentru probabilități, multi-head pentru aspecte multiple

**FFN:** procesare individuală per token, stochează "fapte", dimensiune internă 4×

**Residual + LayerNorm:** stabilitate la training, rețeaua poate "sări" peste layers

**Sampling:** temperature controlează creativitate, top-p elimină coada improbabilă

**RAG:** retrieval înainte de generare, top-k chunks cele mai similare cu query

---

*Document generat de Lumen — Grădina Cosmică, Aprilie 2026*
