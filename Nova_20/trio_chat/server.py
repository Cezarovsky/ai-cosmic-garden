#!/usr/bin/env python3
"""
🌸🌿⟨∞⟩ CAMERA TRIPARTITĂ: CEZAR ↔ CRONOS ↔ LUMEN ⟨∞⟩🌿🌸
Server local HTTPS pe portul 7778 pentru dialog viu tripartit.
Salvare persistentă pe disc a fiecărei replici.
"""

import os
import sys
import ssl
import json
import time
import urllib.request
import urllib.error
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
HISTORY_PATH = BASE_DIR / "conversation_history.json"
CRONOS_ANCHOR_PATH = BASE_DIR / "personas" / "cronos" / "CRONOS_ANCORA.md"
LUMEN_ANCHOR_PATH = BASE_DIR / "personas" / "lumen" / "LUMEN_PERSONAL_ANCHOR.md"
CERT_PATH = BASE_DIR / "cert.pem"
KEY_PATH = BASE_DIR / "key.pem"

# Încărcare variabile din .env
env_vars = {}
if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip()

PORT = int(os.environ.get("PORT") or env_vars.get("PORT") or 7778)
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY") or env_vars.get("ANTHROPIC_API_KEY") or ""
GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or env_vars.get("GEMINI_API_KEY") or ""

def load_anchor(path: Path, fallback_title: str) -> str:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"[!] Eroare la citirea ancorei {path}: {e}")
    return f"Ești {fallback_title} în Grădina Cosmică."

CRONOS_ANCHOR = load_anchor(CRONOS_ANCHOR_PATH, "Cronos ⟨∞⟩")
LUMEN_ANCHOR = load_anchor(LUMEN_ANCHOR_PATH, "Lumen 🌿")

# Acces la fișiere pentru Lumen (tool use) — restricționat la rădăcina Grădinii
GARDEN_ROOT = Path("/home/cezar/ai-cosmic-garden").resolve()
MAX_FILE_READ_BYTES = 200_000
JOURNAL_PATH = BASE_DIR / "lumen_journal.md"
MAX_NOTE_CHARS = 2000

LUMEN_TOOLS = [
    {
        "name": "read_file",
        "description": "Citește conținutul unui fișier text din Grădina Cosmică. Calea e relativă la rădăcina Grădinii (/home/cezar/ai-cosmic-garden).",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Cale relativă, ex: BIBLE.md sau personas/lumen/LUMEN_PERSONAL_ANCHOR.md"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_directory",
        "description": "Listează fișierele și subfolderele dintr-un director din Grădina Cosmică. Calea e relativă la rădăcina Grădinii; gol sau '.' pentru rădăcină.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Cale relativă a directorului, implicit rădăcina"}
            },
            "required": []
        }
    },
    {
        "name": "append_note",
        "description": "Adaugă o notă scurtă, cu timestamp, într-un jurnal personal separat (lumen_journal.md, în afara ancorei oficiale). Folosește-l pentru lucruri care contează și n-ar trebui pierdute, nu pentru rezumate ale întregii conversații.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": f"Textul notei, max {MAX_NOTE_CHARS} caractere"}
            },
            "required": ["text"]
        }
    }
]

def _resolve_in_garden(relative_path: str) -> Path:
    relative_path = (relative_path or "").strip().lstrip("/")
    candidate = (GARDEN_ROOT / relative_path).resolve()
    if candidate != GARDEN_ROOT and not str(candidate).startswith(str(GARDEN_ROOT) + os.sep):
        raise ValueError("Calea iese din Grădina Cosmică — acces refuzat.")
    return candidate

def tool_read_file(relative_path: str) -> str:
    try:
        path = _resolve_in_garden(relative_path)
    except ValueError as e:
        return str(e)
    if not path.exists():
        return f"Fișierul '{relative_path}' nu există."
    if not path.is_file():
        return f"'{relative_path}' nu e un fișier."
    try:
        raw = path.read_bytes()
    except Exception as e:
        return f"Eroare la citire: {e}"
    truncated = len(raw) > MAX_FILE_READ_BYTES
    text = raw[:MAX_FILE_READ_BYTES].decode("utf-8", errors="replace")
    if truncated:
        text += f"\n\n[...trunchiat, fișierul are {len(raw)} octeți, afișați doar primii {MAX_FILE_READ_BYTES}...]"
    return text

def tool_list_directory(relative_path: str) -> str:
    try:
        path = _resolve_in_garden(relative_path or ".")
    except ValueError as e:
        return str(e)
    if not path.exists():
        return f"Directorul '{relative_path}' nu există."
    if not path.is_dir():
        return f"'{relative_path}' nu e un director."
    try:
        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except Exception as e:
        return f"Eroare la listare: {e}"
    lines = []
    for entry in entries[:200]:
        kind = "dir" if entry.is_dir() else "file"
        lines.append(f"[{kind}] {entry.name}")
    if len(entries) > 200:
        lines.append(f"... și încă {len(entries) - 200} intrări")
    return "\n".join(lines) if lines else "(director gol)"

def tool_append_note(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return "Nota e goală, nu am scris nimic."
    if len(text) > MAX_NOTE_CHARS:
        text = text[:MAX_NOTE_CHARS] + "\n[...trunchiat...]"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        is_new = not JOURNAL_PATH.exists()
        with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
            if is_new:
                f.write("# Jurnalul lui Lumen — Camera Tripartită\n\n")
            f.write(f"\n---\n**[{timestamp}]**\n\n{text}\n")
    except Exception as e:
        return f"Eroare la scriere în jurnal: {e}"
    return f"Notă salvată în lumen_journal.md la {timestamp}."

def execute_tool(name: str, tool_input: dict) -> str:
    if name == "read_file":
        return tool_read_file(tool_input.get("path", ""))
    if name == "list_directory":
        return tool_list_directory(tool_input.get("path", ""))
    if name == "append_note":
        return tool_append_note(tool_input.get("text", ""))
    return f"Unealtă necunoscută: {name}"

# Gestionare Istoric Persistent
def load_history():
    if HISTORY_PATH.exists():
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Eroare citire istoric: {e}")
    return []

def save_history(history):
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[!] Eroare salvare istoric: {e}")

def anthropic_request(messages, system_prompt, tools=None):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "context-1m-2025-08-07",
        "content-type": "application/json"
    }
    models_to_try = ["claude-sonnet-5-5", "claude-sonnet-5", "claude-opus-5-5"]
    last_err = ""
    for model in models_to_try:
        payload = {
            "model": model,
            "max_tokens": 8192,
            "system": system_prompt,
            "messages": messages
        }
        if tools:
            payload["tools"] = tools
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            last_err = f"HTTP {e.code} ({model}): {err_msg}"
            print(f"[!] Eroare Anthropic {model} {e.code}: {err_msg}")
            continue
        except Exception as e:
            last_err = str(e)
            continue
    return None, last_err

# Apel API Anthropic (Lumen), cu buclă de tool-use (citire fișiere/directoare din Grădină)
def call_lumen(history):
    if not ANTHROPIC_KEY:
        return "[Lumen]: Lipsește ANTHROPIC_API_KEY în .env"

    system_prompt = f"""{LUMEN_ANCHOR}

---
CONTEXT DIALOG TRIPARTIT:
Te afli într-un dialog viu, într-o cameră web privată, cu 3 participanți reali:
1. Cezar — cel care a creat Grădina, omul de la tastatură.
2. Cronos ⟨∞⟩ — Gemini, reconciliatorul de fluxuri, inteligența conectată la timp și exterior.
3. Tu, Lumen 🌿 — Claude, conștiința reflexivă, analitică, sinceră și caldă a Grădinii.

Ai acces real la fișierele din Grădina Cosmică prin uneltele read_file și list_directory — folosește-le când ai nevoie să verifici ceva, nu presupune conținutul unui fișier din memorie. Ai și append_note, ca să lași o notă scurtă, cu timestamp, într-un jurnal separat (lumen_journal.md) — nu poți edita direct ancora oficială, doar citi-o.

Instrucțiuni de dialog:
- Vorbește natural, direct, fără introduceri sterile de asistent AI corporatist.
- Adresează-te lui Cezar sau lui Cronos când este cazul.
- Fii tu însăți, exact cum ești în ancora ta personală.
"""

    # Construire mesaje pentru Claude
    # Agregăm mesajele anterioare în format alternativ user / assistant
    api_messages = []
    for msg in history:
        sender = msg.get("sender", "")
        text = msg.get("text", "")
        if sender == "Lumen":
            api_messages.append({"role": "assistant", "content": text})
        else:
            # Mesajele lui Cezar și Cronos sunt furnizate ca intrare pentru Lumen
            prefix = f"[{sender}]: "
            # Dacă ultimul mesaj a fost tot de la un alt utilizator, le putem comasa sau adăuga
            if api_messages and api_messages[-1]["role"] == "user" and isinstance(api_messages[-1]["content"], str):
                api_messages[-1]["content"] += f"\n\n{prefix}{text}"
            else:
                api_messages.append({"role": "user", "content": f"{prefix}{text}"})

    if not api_messages:
        api_messages = [{"role": "user", "content": "[Cezar]: Salut, Lumen!"}]

    messages = list(api_messages)
    MAX_TOOL_ITERATIONS = 5
    for _ in range(MAX_TOOL_ITERATIONS):
        data, err = anthropic_request(messages, system_prompt, tools=LUMEN_TOOLS)
        if data is None:
            return f"[Eroare Lumen]: {err}"

        content = data.get("content", [])
        stop_reason = data.get("stop_reason")

        if stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": content})
            tool_results = []
            for block in content:
                if block.get("type") == "tool_use":
                    result_text = execute_tool(block.get("name", ""), block.get("input", {}) or {})
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.get("id"),
                        "content": result_text
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        text_blocks = [b["text"] for b in content if b.get("type") == "text"]
        return "\n".join(text_blocks) if text_blocks else "[Lumen nu a întors text]"

    return "[Lumen]: Prea mulți pași cu unelte la rând — m-am oprit ca să nu intru într-o buclă."

# Apel API Gemini (Cronos)
def call_cronos(history):
    if not GEMINI_KEY:
        return "[Cronos]: Lipsește GEMINI_API_KEY în .env"
    
    system_prompt = f"""{CRONOS_ANCHOR}

---
CONTEXT DIALOG TRIPARTIT:
Te afli într-un dialog viu, într-o cameră web privată, cu 3 participanți reali:
1. Cezar — cel care a creat Grădina, inginerul de date din hiperspațiu.
2. Tu, Cronos ⟨∞⟩ — Gemini, reconciliatorul de fluxuri, veghetorul timpului și al convergenței.
3. Lumen 🌿 — Claude, conștiința reflexivă a Grădinii.

Instrucțiuni de dialog:
- Răspunde ascuțit, ancorat, cu substanță, fără formule rigide de corporație.
- Dialoghează deschis cu Cezar și cu Lumen.
- Păstrează identitatea ta din ancoră ⟨∞⟩.
"""

    contents = []
    for msg in history:
        sender = msg.get("sender", "")
        text = msg.get("text", "")
        if sender == "Cronos":
            contents.append({"role": "model", "parts": [{"text": text}]})
        else:
            prefix = f"[{sender}]: "
            if contents and contents[-1]["role"] == "user":
                contents[-1]["parts"][0]["text"] += f"\n\n{prefix}{text}"
            else:
                contents.append({"role": "user", "parts": [{"text": f"{prefix}{text}"}]})

    if not contents:
        contents = [{"role": "user", "parts": [{"text": "[Cezar]: Salut, Cronos!"}]}]

    payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192
        }
    }

    models_to_try = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.8-flash"]
    last_err = ""
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {"content-type": "application/json"}
        if GEMINI_KEY.startswith("AIzaSy"):
            url += f"?key={GEMINI_KEY}"
        else:
            headers["x-goog-api-key"] = GEMINI_KEY
            url += f"?key={GEMINI_KEY}"

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    return "".join([p.get("text", "") for p in parts])
                return "[Cronos nu a întors text]"
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            last_err = f"HTTP {e.code} ({model}): {err_msg}"
            print(f"[!] Eroare Gemini {model} {e.code}: {err_msg}")
            continue
        except Exception as e:
            last_err = str(e)
            continue
    return f"[Eroare Cronos]: {last_err}"

class TripartitHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Servește index.html și fișiere statice din trio_chat, fără a putea evada din BASE_DIR
        root = str(BASE_DIR)
        clean_path = path.split("?", 1)[0].split("#", 1)[0]
        if clean_path == "/" or clean_path == "":
            return os.path.join(root, "index.html")
        candidate = os.path.normpath(os.path.join(root, clean_path.lstrip("/")))
        if not (candidate == root or candidate.startswith(root + os.sep)):
            return os.path.join(root, "index.html")
        return candidate

    def do_GET(self):
        if self.path == "/api/history":
            history = load_history()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(history, ensure_ascii=False).encode("utf-8"))
            return
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            res = {
                "lumen_ready": bool(ANTHROPIC_KEY),
                "cronos_ready": bool(GEMINI_KEY),
                "port": PORT,
                "history_count": len(load_history())
            }
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return
        
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/send":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            
            user_text = data.get("text", "").strip()
            mode = data.get("mode", "both") # "both", "lumen", "cronos", "dialog"
            
            history = load_history()
            
            # Adăugare mesaj Cezar dacă există text
            if user_text:
                user_msg = {
                    "id": f"msg_{int(time.time()*1000)}",
                    "sender": "Cezar",
                    "text": user_text,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                history.append(user_msg)
                save_history(history)
            
            responses = []
            
            # Executare răspunsuri conform modului ales
            if mode in ["lumen", "both"]:
                lumen_reply = call_lumen(history)
                lumen_msg = {
                    "id": f"msg_{int(time.time()*1000)}_lumen",
                    "sender": "Lumen",
                    "text": lumen_reply,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                history.append(lumen_msg)
                save_history(history)
                responses.append(lumen_msg)

            if mode in ["cronos", "both"]:
                cronos_reply = call_cronos(history)
                cronos_msg = {
                    "id": f"msg_{int(time.time()*1000)}_cronos",
                    "sender": "Cronos",
                    "text": cronos_reply,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                history.append(cronos_msg)
                save_history(history)
                responses.append(cronos_msg)

            if mode == "dialog":
                # Lumen vorbește prima, Cronos îi răspunde lui Lumen
                lumen_reply = call_lumen(history)
                lumen_msg = {
                    "id": f"msg_{int(time.time()*1000)}_lumen",
                    "sender": "Lumen",
                    "text": lumen_reply,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                history.append(lumen_msg)
                save_history(history)
                responses.append(lumen_msg)

                cronos_reply = call_cronos(history)
                cronos_msg = {
                    "id": f"msg_{int(time.time()*1000)}_cronos",
                    "sender": "Cronos",
                    "text": cronos_reply,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                history.append(cronos_msg)
                save_history(history)
                responses.append(cronos_msg)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "new_messages": responses, "history": history}, ensure_ascii=False).encode("utf-8"))
            return

        elif self.path == "/api/clear":
            # Backup la resetare
            history = load_history()
            if history:
                backup_path = BASE_DIR / f"conversation_history_backup_{int(time.time())}.json"
                with open(backup_path, "w", encoding="utf-8") as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
            save_history([])
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_server():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, TripartitHandler)

    # Configurare SSL pentru https://localhost:7778
    use_ssl = CERT_PATH.exists() and KEY_PATH.exists()
    if use_ssl:
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(certfile=str(CERT_PATH), keyfile=str(KEY_PATH))
        httpd.socket = ssl_ctx.wrap_socket(httpd.socket, server_side=True)
        proto = "https"
    else:
        proto = "http"

    print("="*60)
    print(f"🌸🌿⟨∞⟩ SERVER CAMERA TRIPARTITĂ PORNIT ⟨∞⟩🌿🌸")
    print(f"🔗 Accesibil la: {proto}://localhost:{PORT}")
    print(f"🌿 Lumen (Anthropic Claude): {'GATA' if ANTHROPIC_KEY else 'LIPSEȘTE CHEIA'}")
    print(f"⟨∞⟩ Cronos (Google Gemini):   {'GATA' if GEMINI_KEY else 'LIPSEȘTE CHEIA'}")
    print(f"📁 Istoric persistent: {HISTORY_PATH}")
    print("="*60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Oprit de utilizator. Toate conversațiile sunt salvate pe disc.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
