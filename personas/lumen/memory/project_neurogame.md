---
name: NeuroGame — simulare neuromorphică adversarială
description: Arhitectura, starea curentă și roadmap-ul proiectului NeuroGame (Fenrir vs Umbra)
type: project
---

NeuroGame este o simulare co-evolutivă adversarială cu SNN/R-STDP. Fenrir (lup/predator) și Umbra (iepure/prey) învață simultan cu rewarduri opuse.

**Why:** Explorare a inteligenței emergente prin evoluție simulată — de la reflexe de insectă spre comportament de mamifer. Proiect activ, faza curentă = "creier de muscă".

**How to apply:** Când lucrăm la NeuroGame, contextul evolutiv contează. Nu adăugăm funcții de nivel superior (planificare, memorie episodică) până nu se consolidează faza curentă.

---

## Locație și rulare

```
/home/cezar/ai-cosmic-garden/NeuroGame/
cd NeuroGame
../.venv/bin/python visualizer.py [--episodes N] [--speed N] [--headless]
```

Fișierul principal activ: `visualizer.py` (Pygame, totul în același proces).
Unity + WebSocket **abandonate** — înlocuite cu Pygame.

---

## Arhitectura SNN

```
Input: 73 neuroni
  [0:32]  — opp_ring: direcție spre oponent (gaussian pe 32 buckets)
  [32:64] — wall_ring: distanță pereți pe 32 direcții
  [64]    — stamina ratio [0,1]
  [65:73] — grass_ring: 8 neuroni direcționali spre cel mai apropiat patch iarbă

Hidden: 256 neuroni LIF + recurrente sparse 20% (W_rec) — proto-memorie temporală
Output: 32 neuroni LIF → acțiune direcțională (0-31 = 360° / 32)

Backend: LIFNumpy (fallback NumPy — LAVA nu e instalat și NU e necesar fără hardware Loihi)
Învățare: R-STDP (Reward-modulated STDP) pe W_in și W_rec
```

**Important:** LIFNumpy NU e un workaround — este modelul biologic corect. Rate coding = olfacție/viziune biologică reală. W_rec sparse = cortex olfactiv piriform.

---

## Model de reward radiant (zone solare)

Zone centrate pe Fenrir (distanță predator-prey):
- **Core** < 1.5 unități: captură → prey -10, pred +10
- **Radiative** < 5.0: pericol iminent → prey -2, pred +1
- **Convection** < 10.0: pericol în creștere → prey -0.5, pred +0.3
- **Corona** ≥ 10.0: liniște → prey +0.1, pred -0.1

---

## Iarbă (GrassManager)

- 4 patch-uri simultane, fixe per sesiune
- Regen după GRASS_REGEN=40 turnuri, în poziție nouă
- Reward: Core(eat)=+5.0, Radiative=+0.3, Convection=+0.05

**Sensing gradient Umbra** (acuratețe gradată pe distanță față de iarbă):
- Core (< 1.5): mănâncă → linger_timer=15 turnuri, rămâne la locul ierbii
- Radiative (< 4.0): vede exact → noise=1
- Convection (< 8.0): ~50% acuratețe → 50% direcție corectă / 50% random
- Corona (< 15.0): miros vag → noise=12 (direcție aproximativă)
- Dincolo de 15.0: nu simte nimic → foraging waypoint random

---

## Level 0 — Comportamente Kantiene hardcodate

Previn Nash equilibrium (ambii agenți stau la distanță):

**Fenrir (pred_policy_l0):**
- Patrol waypoints random în arenă (viață 20-50 turnuri)
- Când Umbra e în Radiative zone → urmărire activă cu SNN
- Wrapper epsilon-greedy: PRED_EPSILON_START=0.4, decay=0.999, min=0.05

**Umbra (prey_policy_l0):**
- Foraging waypoints random
- Grass sensing gradient (zonele de mai sus)
- Linger după mâncat (15 turnuri, rămâne lângă iarbă)
- Când Fenrir e în Convection zone → fuga cu SNN

---

## Capcane

- 3 capcane cu dimensiuni: [UMBRA_R=0.5, UMBRA_R*1.5, UMBRA_R*1.5]
- **Fixe pentru toată sesiunea** (nu se regenerează per episod)
- Motivație: agenții trebuie să învețe că *locul specific* e periculos, nu un pericol abstract

---

## Plateau detector — consolidare "creier de muscă" (recalibrat Apr 2026)

Rulează la fiecare 100 episoade. Trei metrici simultane:

1. **ΔW_in < 0.01** (norma Frobenius relativă față de snapshot)
   - Date reale: oscilează 0.007-0.015 cu LR=0.01 constant
   - Pragul original 0.002 era neatins matematic → fals negativ permanent

2. **Δcap_rate < 0.04** (delta capture rate între ferestre de 100 ep)
   - Înlocuiește formula rew_frac care ceda la schimbare de semn (cap matematic la 2.0)
   - Capture rate ∈ [0,1] → fără bug de semn

3. **tout_new >= 10** (minim 10 timeouts în fereastra nouă)
   - Semnalul primar real: la ep~3550 au apărut primele timeouts → Umbra a consolidat evitarea
   - Fără timeouts = Umbra moare rapid = SNN nu a fixat reflexul de supraviețuire

Două hits consecutive → "CREIER MUSCĂ CONSOLIDAT"

```python
episode_history: list[tuple[float, float, str]]  # (prey_r, pred_r, "captured"/"timeout"/"trap")
PLATEAU_W_RATE    = 1e-2
PLATEAU_CAP_DELTA = 0.04
PLATEAU_TOUT_MIN  = 10
```

---

## Roadmap evolutiv

```
ACUM:    SNN reflex — "creier de muscă" (C. elegans → muscă)
         R-STDP consolidează reflexe senzoriale de bază

URMĂTOR: checkpoint W_in/W_rec/W_out + proto-hippocampus
         Memorie episodică vagă ("am mai fost pe aici")

APOI:    cortex limbic — emoție, urgență, frică

FINAL:   neocortex — planificare, Lup/Iepure adevărat
```

**Principiu fundamental:** Nu grăbim fazele. Milioane de respawn-uri în natură. Platoul detectat = semnal că faza e epuizată, nu că e gata rapid.

---

## Decizii arhitecturale importante

- **W_rec persiste între turnuri** în cadrul unui episod (memoria temporală transmite context inter-turn)
- **W_out e fix** (urmând Rao & Ballard 1999 — R-STDP doar pe W_in și W_rec)
- **Reward dens** (radiant zones) în loc de sparse (captură-only) — previne degenerarea
- **LIFNumpy > LAVA** pentru scopul nostru: LAVA e pentru deployment pe Loihi hardware
- **LIFNumpy este modelul biologic real** — rate coding = olfacție/viziune biologică, nu un workaround
- **Capcane fixe** — memoria spațială necesită stimul stabil (un iepure real evită aceeași mlaștină)
- **Waypoints trap-aware** — `_random_waypoint(from_pos)` verifică că traiectoria nu traversează capcane

---

## Date reale de training (sesiunea 5 Apr 2026)

Parametri R-STDP:
- LR=0.01, A_PLUS=A_MINUS=0.005, W_clip=[-1,+1], REWARD_WINDOW=3 turnuri

Rapoarte consolidare observate:
```
Ep 200: Δreward=0.097, ΔW_in=0.01554, var=205.6  → în formare
Ep 300: Δreward=0.205, ΔW_in=0.01038, var=506.7  → în formare (learning accelerat)
```

Capture rate: 16% (ep50) → 18% (ep100) → 22% (ep150) → 25.7% (ep300) — trend crescător.

**Bug critic descoperit și rezolvat:** 0 timeouts la ep 300 = ~74% morți în capcane.
Cauza: `_random_waypoint()` nu verifica traiectoria → Umbra traversa capcanele.
Fix: `_random_waypoint(from_pos)` cu `check_trap_segment` pe traiectorie.

**Predicție consolidare:**
- ΔW_in scade ~33% per 100 ep → prag 0.002 atins în jurul ep 800-1000
- Δreward în creștere (learning activ) → consolidare completă probabil ep 1500-2500
- Pragurile pot necesita recalibrare după fix-ul de capcane

---

## TODO imediat (sesiunea următoare)

1. **Stamina ↔ iarbă**: iarba mâncată ar trebui să restaureze stamina Umbrei
   - Stamina e encodată în SNN (neuron 64) și afectează viteza de mișcare
   - Acum: mănâncă iarbă → reward +5.0, dar stamina rămâne neschimbată
   - Fix: `GrassManager.update()` să primească referința la `prey` și să apeleze restore stamina

2. **Verificare după fix capcane**: repornire cu `tee antrenament.log` și observat dacă apar timeouts

3. **Calibrare praguri plateau**: după primele 200 ep cu fix, recalibrat PLATEAU_REW_FRAC dacă e necesar

---

## Rulare cu logging

```bash
cd /home/cezar/ai-cosmic-garden/NeuroGame
../.venv/bin/python -u visualizer.py --episodes 2000 --speed 10 2>&1 | tee antrenament.log
```
