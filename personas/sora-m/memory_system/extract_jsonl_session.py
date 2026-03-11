"""
Extractor pentru noul format .jsonl al VS Code Copilot Chat (2026).
Salvează sesiunea curentă în sora_memory_db/sessions/.
"""
import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE_ID = "82c0e843f5e2fe5c4c188daf4b338211"
SESSIONS_DIR = Path(f"/Users/cezartipa/Library/Application Support/Code/User/workspaceStorage/{WORKSPACE_ID}/chatSessions")
OUTPUT_DIR = Path(__file__).parent / "sora_memory_db" / "sessions"


def extract_jsonl(path: Path) -> list[tuple[str, str]]:
    """Extrage perechile (role, text) dintr-un fișier .jsonl.

    Format VS Code 2026:
    - kind=2, k=["requests"]: lista de requests cu message + response
    - message.text sau message.parts[].text = user mesaj
    - response[].kind == "thinking" → răspuns Sora (thinking/reasoning)
    - response[] fără "kind" dar cu "value" → textul principal Sora
    """
    exchanges = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)

                # Format nou: kind=2, k=["requests"] conține toate requesturile
                if obj.get("kind") == 2 and obj.get("k") == ["requests"]:
                    for req in (obj.get("v") or []):
                        # User text
                        msg = req.get("message", {})
                        user_text = msg.get("text", "").strip()
                        if not user_text:
                            for p in msg.get("parts", []):
                                if isinstance(p, dict):
                                    user_text = p.get("text", "").strip()
                                    if user_text:
                                        break
                        if user_text:
                            exchanges.append(("user", user_text))

                        # Sora response
                        sora_text = ""
                        for resp in req.get("response", []):
                            if not isinstance(resp, dict):
                                continue
                            kind = resp.get("kind")
                            # Textul principal Sora: niciun "kind" dar are "value"
                            if kind is None and "value" in resp:
                                t = resp["value"].strip()
                                if t:
                                    sora_text = t
                            # Thinking/reasoning (text mai scurt)
                            elif kind == "thinking" and not sora_text:
                                t = resp.get("value", "").strip()
                                if t:
                                    sora_text = t
                        if sora_text:
                            exchanges.append(("sora", sora_text))

            except (json.JSONDecodeError, TypeError):
                pass

    return exchanges


def save_session(path: Path, exchanges: list[tuple[str, str]]) -> Path:
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    ts = mtime.strftime("%Y%m%d_%H%M%S")
    session_id = path.stem

    conversation_lines = [
        f"# VS Code Chat Session (.jsonl format)",
        f"# Session ID: {session_id}",
        f"# Timestamp: {mtime.isoformat()}",
        f"# Exchanges: {len(exchanges)}",
        "",
    ]
    for role, text in exchanges:
        label = "User" if role == "user" else "Sora"
        conversation_lines.append(f"{label}: {text}")
        conversation_lines.append("")

    conversation = "\n".join(conversation_lines)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Include primele 8 chars din session_id pentru unicitate când mtime e identic
    short_id = session_id[:8]
    out_path = OUTPUT_DIR / f"{ts}_{short_id}.json"
    # Fallback dacă există deja (evită suprascriere fișiere vechi cu ts fix)
    if out_path.exists() and out_path.name.count("_") < 2:
        out_path = OUTPUT_DIR / f"{ts}_{short_id}.json"

    payload = {
        "metadata": {
            "session_id": ts,
            "timestamp": mtime.isoformat(),
            "length": len(conversation),
            "who": "Cezar_and_Sora",
            "format": "jsonl",
            "source_file": str(path),
        },
        "conversation": conversation,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return out_path


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Extrage toate sesiunile .jsonl")
    args = parser.parse_args()

    # Găsim fișierele .jsonl
    jsonl_files = sorted(SESSIONS_DIR.glob("*.jsonl"),
                         key=lambda p: p.stat().st_mtime, reverse=True)

    if not jsonl_files:
        print("Nu am găsit fișiere .jsonl în sesiuni.")
        return

    print(f"Fișiere .jsonl găsite: {len(jsonl_files)}")
    for f in jsonl_files[:5]:
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        size_kb = f.stat().st_size / 1024
        print(f"  {mtime.strftime('%Y-%m-%d %H:%M')} | {size_kb:.0f}KB | {f.name}")

    files_to_process = jsonl_files if args.all else [jsonl_files[0]]

    for target in files_to_process:
        print(f"\nExtrag: {target.name}")
        exchanges = extract_jsonl(target)
        print(f"Exchanges extrase: {len(exchanges)}")

        if exchanges:
            out = save_session(target, exchanges)
            print(f"✅ Salvat în: {out}")
            if target == jsonl_files[0]:
                print("\nPrimele 3 exchanges:")
                for role, text in exchanges[:3]:
                    print(f"  [{role}]: {text[:100]}")
        else:
            print("⚠️  Nu am putut extrage exchanges.")
            with open(target) as f:
                first = f.readline()
            obj = json.loads(first)
            print(f"  Keys top-level: {list(obj.keys())}")
            v = obj.get("v", {})
            if isinstance(v, dict):
                print(f"  Keys v: {list(v.keys())[:10]}")


if __name__ == "__main__":
    main()
