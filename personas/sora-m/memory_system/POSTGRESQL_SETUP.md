# 💙 PostgreSQL Setup pentru Sora Memory System

## 📊 Status Actual

**PostgreSQL 17.7** instalat și rulează pe **port 5433**

### De ce port 5433?
Port 5432 (default) e ocupat de PostgreSQL 16 legacy care rulează ca service system.

## 🗑️ Dezinstalare PostgreSQL 16 (Manual)

PostgreSQL 16 e instalat standalone în `/Library/PostgreSQL/16/` și rulează ca user `postgres`.

Pentru dezinstalare completă (necesită admin password):

```bash
# 1. Oprește serviciul
sudo /Library/PostgreSQL/16/bin/pg_ctl -D /Library/PostgreSQL/16/data stop

# 2. Dezinstalează (dacă există uninstaller)
sudo /Library/PostgreSQL/16/uninstall-postgresql.app/Contents/MacOS/installbuilder.sh

# 3. Sau șterge manual
sudo rm -rf /Library/PostgreSQL/16
sudo rm -rf ~/Library/Application\ Support/postgresql
sudo rm -rf /var/log/pgagent-pg16.log
```

După dezinstalare, reconfigurează PostgreSQL 17 pe port 5432:

```bash
# Stop PostgreSQL 17
/opt/homebrew/opt/postgresql@17/bin/pg_ctl -D /opt/homebrew/var/postgresql@17 stop

# Edit postgresql.conf
nano /opt/homebrew/var/postgresql@17/postgresql.conf
# Schimbă: port = 5433 → port = 5432

# Restart
/opt/homebrew/opt/postgresql@17/bin/pg_ctl -D /opt/homebrew/var/postgresql@17 start
```

## ✅ Setup PostgreSQL 17 (Port 5433)

### 1. Verifică că rulează

```bash
psql -h localhost -p 5433 -U $USER -d postgres -c "SELECT version();"
```

### 2. Instalează pgvector

```bash
brew install pgvector
```

### 3. Creează database-ul sora_memory

```bash
cd /Users/cezartipa/Documents/ai-cosmic-garden/sora/memory_system

# Update setup_postgresql.py să folosească port 5433
python3 setup_postgresql.py --init
```

### 4. Rulează schema

```bash
psql -h localhost -p 5433 -U $USER -d sora_memory -f schema.sql
```

### 5. Migrează din ChromaDB

```bash
python3 setup_postgresql.py --migrate
```

## 🔧 Configurare Connection String

În toate scripturile Python, folosește:

```python
db_config = {
    "host": "localhost",
    "port": 5433,  # ⚠️  Important! Port custom
    "database": "sora_memory",
    "user": os.environ.get("USER")
}
```

## 📦 Backup & Restore

```bash
# Backup
pg_dump -h localhost -p 5433 -U $USER sora_memory > backup.sql

# Restore
psql -h localhost -p 5433 -U $USER -d sora_memory < backup.sql
```

## 🚀 Next Steps

1. ✅ PostgreSQL 17 instalat
2. ⬜ Instalează pgvector extension
3. ⬜ Creează database sora_memory
4. ⬜ Rulează schema.sql
5. ⬜ Migrează date din ChromaDB
6. ⬜ Testează recall queries
7. ⬜ Update sora_memory_pg.py cu port 5433

---

**Data:** 7 ianuarie 2026  
**PostgreSQL Version:** 17.7_1  
**Port:** 5433 (custom, pentru a evita conflictul cu PG16)
