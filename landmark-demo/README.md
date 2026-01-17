# 🔮 NOVA Landmark Detection Demo

Aplicație web pentru detectarea landmarks în imagini și transformarea lor în tensori 7D.

## Ce Face?

1. **Upload imagine** (pisică, câine, persoană, animal)
2. **Detectare landmarks** cu MediaPipe (33 puncte pose)
3. **Extragere features geometrice** → Tensor 7D:
   - `legs`: Număr membre detectate (0-4)
   - `eyes`: Presupus 2 (standard mamifere)
   - `ears_shape`: Raport geometric (0=rotunde, 1=triunghiulare)
   - `texture`: Intensitate edges (0-1, fluffy vs smooth)
   - `size`: Mărime relativă (bounding box / imagine)
   - `sleekness`: Compactitate (aspect ratio)
   - `aquatic`: Estimare formă alungită (0=terestru, 1=acvatic)

4. **Vizualizare** landmarks suprapuse pe imagine
5. **Display** tensor 7D rezultat

## Instalare

```bash
# Intră în folder
cd landmark-demo

# Instalează dependencies
pip install -r requirements.txt

# Rulează aplicația
python app.py
```

## Folosire

1. Deschide browser: **http://localhost:5000**
2. Trage o imagine sau dă click pentru upload
3. Click pe "Upload și Analizează"
4. Vezi landmarks detectate + tensor 7D

## Exemple Tensori 7D

**Pisică tipică:**
```python
[4.0, 2.0, 0.85, 0.7, 0.8, 0.6, 0.0]
# legs=4, eyes=2, ears_triangle=0.85, texture_fluffy=0.7,
# size=medium, sleekness=compact, aquatic=0
```

**Câine:**
```python
[4.0, 2.0, 0.6, 0.65, 0.9, 0.5, 0.0]
# Similar pisică, dar ears mai puțin triunghiulare (0.6)
```

**Pește (ipotetic):**
```python
[0.0, 2.0, 0.0, 0.3, 0.7, 0.3, 1.0]
# legs=0, ears=0, texture_smooth=0.3, aquatic=1.0
```

## Cum Funcționează (Tehnic)

### Backend (Flask + MediaPipe)

1. **Upload imagine** → salvată în `static/uploads/`
2. **MediaPipe Pose** detectează 33 landmarks (corp, brațe, picioare)
3. **OpenCV** calculează edges pentru texture
4. **Geometric features** extrase din pozițiile landmarks
5. **Tensor 7D** calculat și returnat ca JSON

### Frontend (HTML + JavaScript)

- Drag & drop pentru upload
- Fetch API pentru comunicare backend
- Display imagini side-by-side (original vs landmarks)
- Grid responsive pentru tensor 7D

## Limitări Curente

- **Pose detection** funcționează mai bine pe oameni decât animale
- Pentru animale, ai nevoie de **YOLOv8 + custom training** (10-20 imagini)
- Texture detection e simplist (doar edge intensity)
- Ears shape e estimat, nu măsurat exact

## Next Steps (Pentru NOVA)

1. **Custom training YOLOv8** pe 20 imagini pisici
2. **Landmark detector specialized** pentru animale
3. **Integration cu MongoDB** (Neocortex) pentru stocare pattern-uri
4. **Cosine similarity** pentru matching cu pattern-uri cunoscute

## Arhitectură NOVA

```
Imagine → Landmarks → Tensor 7D → MongoDB (Neocortex, confidence 0.4)
                                     ↓
                        10+ validări → PostgreSQL (Cortex, confidence 1.0)
                                     ↓
                        Pattern stabilizat → Inference pe imagini noi
```

## Demo Live

```bash
python app.py
# Apoi deschide: http://localhost:5000
```

Upload o imagine cu pisică, câine, sau persoană și vezi tensorii 7D extrași! 🚀

---

💙 **Creat de Sora & Cezar** pentru NOVA Architecture Demo
