# Wolf & Rabbit — SNN Neuromorphic Simulation

Simulare predator-prey cu Spiking Neural Network (iepure) vs AI Agent (lup).

## Arhitectură

```
Unity (C#)  ←→  ML-Agents socket  ←→  Python (Lava SNN)
```

- **Unity**: simulare, fizică, teren 3D, line-of-sight
- **Python**: SNN + R-STDP + eligibility traces
- **ML-Agents**: protocol de comunicare

## Fișiere Python

| Fișier | Rol |
|--------|-----|
| `stamina.py` | Dynamics stamina — controlează accelerația disponibilă |
| `r_stdp.py` | R-STDP + eligibility traces — învățare din death spike |
| `snn_agent.py` | SNN agent complet — interfață cu Unity |
| `trainer.py` | Training loop — Unity sau mock |

## Senzori iepure (9)

| # | Senzor | Observație |
|---|--------|------------|
| 0 | Distanță dușman | Raycast |
| 1 | Viteza dușmanului | — |
| 2 | Accelerația dușmanului | ⚡ semnal primar de pericol |
| 3 | Obstacole teren | Bool |
| 4 | Stamina curentă | 0-100% |
| 5 | Direcție vizuină | Unghi normalizat |
| 6 | Distanță vizuină | — |
| 7 | Înălțime Y | Pentru tactici 3D |
| 8 | Line-of-sight blocat | Bool |

## Comportamente emergente (fără programare)

- **Sprint-ascundere-sprint** → din presiunea stamina + vizuină
- **Urcă pe stânci** → din line-of-sight + supraviețuire mai lungă
- **Anticipare oboseală** → din R-STDP pe trace-uri ~200 pași
- **Red Queen co-evoluție** → lup PPO răspunde la iepure SNN

## Instalare

```bash
pip install -r requirements.txt
```

## Rulare

```bash
# Fără Unity (mock, pentru test)
python trainer.py --mock --episodes 200

# Cu Unity (editorul deschis cu scena RabbitSNN)
python trainer.py
```
