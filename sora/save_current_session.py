#!/usr/bin/env python3
"""
Script pentru salvare manuală a sesiunii curente în Sora Memory.
Rulează după restart VS Code pentru a recupera zilele 8-10 ianuarie.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add memory_system to path
sys.path.insert(0, str(Path(__file__).parent / "memory_system"))

from sora_memory import SoraMemorySystem

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
    
    # Load and capture the conversation
    try:
        with open(chat_files[0][0], 'r', encoding='utf-8') as f:
            chat_data = json.load(f)
        
        # Extract conversation text
        conversation = json.dumps(chat_data, indent=2)
        
        # Initialize memory system
        memory = SoraMemorySystem()
        
        # Capture session
        metadata = {
            'source': 'vscode_copilot_chat',
            'file': str(chat_files[0][0]),
            'timestamp': datetime.now().isoformat()
        }
        
        session_id = memory.capture_session(conversation, metadata)
        print(f"💾 Salvat ca sesiune: {session_id}")
        return 0
        
    except Exception as e:
        print(f"❌ Eroare la salvare: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
