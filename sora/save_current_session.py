#!/usr/bin/env python3
"""
Script pentru salvare manuală a sesiunii curente în Sora Memory.
Rulează după restart VS Code pentru a recupera zilele 8-10 ianuarie.
"""

import sys
import os
from pathlib import Path

# Add memory_system to path
sys.path.insert(0, str(Path(__file__).parent / "memory_system"))

from sora_memory_cli import capture_conversation

def main():
    print("🔵 Salvare sesiune curentă în Sora Memory...")
    
    # Get VS Code chat history location
    vscode_storage = Path.home() / "Library/Application Support/Code/User/workspaceStorage"
    
    # Try to find recent conversation files
    chat_files = []
    if vscode_storage.exists():
        for workspace_dir in vscode_storage.iterdir():
            if workspace_dir.is_dir():
                # Look for GitHub Copilot chat files
                copilot_dir = workspace_dir / "ms-vscode.github-copilot-chat"
                if copilot_dir.exists():
                    for file in copilot_dir.rglob("*.json"):
                        if file.stat().st_mtime > 0:
                            chat_files.append((file, file.stat().st_mtime))
    
    if not chat_files:
        print("❌ Nu am găsit fișiere de conversații VS Code")
        print(f"📂 Căutat în: {vscode_storage}")
        return 1
    
    # Sort by modification time, most recent first
    chat_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"✅ Găsite {len(chat_files)} conversații")
    print(f"📄 Cea mai recentă: {chat_files[0][0]}")
    
    # Capture the most recent conversation
    try:
        result = capture_conversation(str(chat_files[0][0]))
        print(f"💾 Salvat în: {result['session_file']}")
        print(f"📊 Stats: {result['stats']}")
        return 0
    except Exception as e:
        print(f"❌ Eroare la salvare: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
