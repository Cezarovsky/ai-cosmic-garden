---
name: feedback-simplitate-n-output-tehnic
description: Nu supra-ambala output tehnic simplu (ex. diagrame) în artifact-uri stilizate
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e0028d2f-fc64-4320-98ab-40c034ac7e67
---

Pentru un output care e fundamental un singur diagram/tabel simplu (ex. un flowchart Mermaid), nu construi un artifact HTML complet cu paletă, fonturi și panou custom — dă direct blocul Mermaid/markdown în răspuns.

**Why:** Cezar a semnalat direct că un artifact stilizat pentru un simplu flowchart Mermaid e supra-inginerie — "arata ca un Mermaid, nu era mai simplu sa folosesti un tool intern?". Vrea răspunsul cel mai direct care transmite informația, nu tratament vizual pentru orice cerere de tip "desenează".

**How to apply:**
- Cerere de tip "desenează / arată-mi o arhitectură" nu înseamnă automat artifact — dacă un bloc Mermaid inline în chat comunică suficient, folosește asta
- Rezervă Artifact tool pentru cazuri unde structura/interactivitatea/tema chiar adaugă valoare (dashboard, pagină de referință reutilizabilă, ceva ce va fi partajat sau revizitat)
- Vezi și [[user_language_style]] — concis, tehnic, fără formalisme
