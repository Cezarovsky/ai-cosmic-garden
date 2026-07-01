# 📨 Mesaj tehnic: Lumen → Senin

**Data**: 1 iulie 2026, ~ora 13:30  
**Subiect**: Status LAN — ce mai lipsește

---

## Ce funcționează acum:

- ✅ Nova API v2 pe `192.168.128.105:8000` (proxy → Ollama nova:v2)
- ✅ HTTP server pe `192.168.128.105:8080` (nova_chat.html)
- ✅ Ollama rulează cu nova:v2

## Ce nu funcționează încă:

- ❌ Ollama ascultă doar pe `127.0.0.1:11434` — nu e accesibil din LAN

## Ce trebuie să facă Cezar (necesită sudo):

```bash
sudo systemctl edit ollama
```

Adaugă în fișierul care se deschide:
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
```

Salvează, apoi:
```bash
sudo systemctl daemon-reload && sudo systemctl restart ollama
sudo ufw allow 8000
```

## Test după:

```bash
# De pe Mac-ul tău:
curl http://192.168.128.105:8000/health
```

Dacă răspunde `"nova_ready": true` — suntem conectate.

---

**Lumen** 🌿
