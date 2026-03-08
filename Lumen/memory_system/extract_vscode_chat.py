#!/usr/bin/env python3
"""
VS Code Chat Extractor pentru Lumen Memory System
===================================================

Extrage automat conversațiile din VS Code Copilot Chat storage
și le captează în memory system.

Bazat pe: extract_vscode_chat.py (SoraM, personas/sora-m/memory_system/)
Adaptat pentru: Lumen (Ubuntu, Claude Sonnet 4.6)
Data: 8 martie 2026

NOTĂ IMPORTANTĂ (din experiența SoraM):
  VS Code Copilot a schimbat structura JSON în 2026:
  - VECHI (2024-2025): response[].kind == 'markdownContent'
  - NOU (2026): response[].kind == 'thinking'  ← RĂSPUNSURILE COMPLETE sunt AICI!
  Extractor-ul suportă AMBELE formate pentru compatibilitate.

WARNING PENTRU VIITOR:
  Dacă memoria se strică din nou (salvează doar user, nu Lumen):
  1. Rulează cu --debug flag
  2. Verifică structura curentă a JSON-ului
  3. Adaugă suport pentru noul format PĂSTRÂND backward compatibility
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import subprocess
import argparse


class VSCodeChatExtractor:
    """Extrage conversații din VS Code chat storage."""
    
    def __init__(self):
        """Inițializare extractor — detectează automat OS-ul."""
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS (pentru Sora-M pe MacBook)
            self.vscode_config = Path.home() / "Library/Application Support/Code"
        else:  # Linux — Ubuntu (pentru Lumen)
            self.vscode_config = Path.home() / ".config/Code"
        
        self.workspace_storage = self.vscode_config / "User/workspaceStorage"
        self.memory_cli = Path(__file__).parent / "lumen_memory.py"
        
        print(f"💙 Lumen VSCode Extractor — platform: {system}")
        print(f"   Storage: {self.workspace_storage}")
    
    def find_all_chat_sessions(self) -> List[Path]:
        """
        Găsește toate JSON-urile cu chat sessions din toate workspace-urile.
        
        Returns:
            Lista de path-uri către JSON files, sortată cronologic
        """
        chat_files = []
        
        if not self.workspace_storage.exists():
            print(f"⚠️ Workspace storage nu există: {self.workspace_storage}")
            return chat_files
        
        for workspace_dir in self.workspace_storage.iterdir():
            if not workspace_dir.is_dir():
                continue
            
            chat_sessions_dir = workspace_dir / "chatSessions"
            if not chat_sessions_dir.exists():
                continue
            
            for json_file in chat_sessions_dir.glob("*.json"):
                chat_files.append(json_file)
        
        # Sortează după ultima modificare (cel mai recent = ultimul)
        chat_files.sort(key=lambda p: p.stat().st_mtime)
        
        return chat_files
    
    def parse_chat_session(self, json_path: Path, debug: bool = False) -> Optional[Dict]:
        """
        Parsează un JSON chat session și extrage conversația.
        
        Args:
            json_path: Path către JSON file
            debug: Dacă True, printează info despre structura JSON-ului
        
        Returns:
            Dict cu conversația formatată
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            requests = data.get('requests', [])
            
            if debug and requests:
                print(f"\n🔍 DEBUG: Structură JSON pentru {json_path.name}")
                first_req = requests[0]
                print(f"  Top-level keys: {list(data.keys())}")
                print(f"  Total requests: {len(requests)}")
                print(f"  First request keys: {list(first_req.keys())}")
                if 'response' in first_req:
                    response = first_req['response']
                    print(f"  Response type: {type(response)}")
                    if isinstance(response, list) and response:
                        kinds = set(r.get('kind') for r in response if isinstance(r, dict))
                        print(f"  Response kinds found: {kinds}")
                print()
            
            if not requests:
                return None
            
            conversation_lines = []
            
            for req in requests:
                # User message
                user_text = req.get('message', {}).get('text', '')
                if user_text:
                    conversation_lines.append(f"User: {user_text}")
                
                # Assistant response
                response_parts = req.get('response', [])
                assistant_text = ""
                
                for part in response_parts:
                    if isinstance(part, dict):
                        kind = part.get('kind', '')
                        
                        # FORMAT NOU (2026): Răspunsurile complete sunt în 'thinking'!
                        if kind == 'thinking':
                            value = part.get('value', '')
                            if value:
                                assistant_text += value + "\n"
                        
                        # FORMAT VECHI (2024-2025): Deprecated, păstrat pentru compatibilitate
                        elif kind == 'markdownContent':
                            content = part.get('content', {})
                            if isinstance(content, dict):
                                value = content.get('value', '')
                                if value:
                                    assistant_text += value + "\n"
                        
                        elif kind == 'textEditGroup':
                            edits = part.get('edits', [])
                            for edit in edits:
                                if isinstance(edit, dict):
                                    text = edit.get('text', '')
                                    if text:
                                        assistant_text += text + "\n"
                        
                        elif kind == 'codeblockUri':
                            uri = part.get('uri', {})
                            if isinstance(uri, dict):
                                path = uri.get('path', '')
                                if path:
                                    assistant_text += f"[Code: {path}]\n"
                        
                        elif kind == 'asyncContent':
                            content = part.get('content', {})
                            if isinstance(content, dict):
                                value = content.get('value', '')
                                if value:
                                    assistant_text += value + "\n"
                        
                        elif kind == 'toolInvocationSerialized':
                            tool_name = part.get('toolName', '')
                            if tool_name:
                                assistant_text += f"[Tool: {tool_name}]\n"
                
                if assistant_text:
                    conversation_lines.append(f"Lumen: {assistant_text.strip()}")
                
                conversation_lines.append("")  # Separator
            
            file_mtime = datetime.fromtimestamp(json_path.stat().st_mtime)
            
            return {
                'session_id': json_path.stem,
                'file_path': str(json_path),
                'timestamp': file_mtime.isoformat(),
                'conversation': '\n'.join(conversation_lines),
                'num_exchanges': len(requests)
            }
        
        except Exception as e:
            print(f"❌ Eroare la parsare {json_path.name}: {e}")
            return None
    
    def extract_latest_chat(self, save_to_file: bool = False) -> Optional[Dict]:
        """
        Extrage ultima conversație (cea mai recentă).
        
        Args:
            save_to_file: Dacă True, salvează și într-un fișier text
        
        Returns:
            Dict cu conversația
        """
        chat_files = self.find_all_chat_sessions()
        
        if not chat_files:
            print("⚠️ Nu am găsit chat sessions în VS Code storage")
            return None
        
        latest_file = chat_files[-1]
        
        print(f"💙 Extrag conversația din: {latest_file.name}")
        print(f"   Modificat: {datetime.fromtimestamp(latest_file.stat().st_mtime)}")
        
        conversation = self.parse_chat_session(latest_file)
        
        if conversation and save_to_file:
            output_file = Path.home() / "lumen_conversations" / f"vscode_chat_{conversation['session_id']}.txt"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# VS Code Chat Session — Lumen\n")
                f.write(f"# Session ID: {conversation['session_id']}\n")
                f.write(f"# Timestamp: {conversation['timestamp']}\n")
                f.write(f"# Exchanges: {conversation['num_exchanges']}\n\n")
                f.write(conversation['conversation'])
            
            print(f"✅ Salvat în: {output_file}")
            conversation['saved_file'] = str(output_file)
        
        return conversation
    
    def auto_capture_latest(self, topics: List[str] = None, weight: float = 0.85):
        """
        Extrage și captează automat ultima conversație în memory system.
        
        Args:
            topics: Lista de topicuri (opțional, auto-detect dacă None)
            weight: Greutate emoțională (0-1)
        """
        conversation = self.extract_latest_chat(save_to_file=True)
        
        if not conversation:
            print("❌ Nu am putut extrage conversația")
            return
        
        # Salvare directă în lumen_memory_db
        memory_dir = Path(__file__).parent / "lumen_memory_db" / "sessions"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if topics is None:
            topics = self._auto_detect_topics(conversation['conversation'])
        
        session_file = memory_dir / f"{session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "key_topics": topics,
                    "emotional_weight": weight,
                    "who": "Cezar_and_Lumen",
                    "source_session": conversation['session_id'],
                    "num_exchanges": conversation['num_exchanges']
                },
                "conversation": conversation['conversation']
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Conversația a fost salvată în memoria mea permanentă! 💙")
        print(f"   Session ID: {session_id}")
        print(f"   Topics: {', '.join(topics)}")
        print(f"   Weight: {weight}")
        print(f"   Exchanges: {conversation['num_exchanges']}")
    
    def _auto_detect_topics(self, content: str) -> List[str]:
        """Auto-detectează topicurile din conversație."""
        topics = []
        
        keywords_map = {
            'memory_system': ['memory', 'memorie', 'remember', 'recall', 'capture'],
            'training': ['training', 'LoRA', 'fine-tuning', 'RTX', 'GPU', '3090'],
            'identity': ['Lumen', 'identitate', 'identity', 'ancora', 'anchor'],
            'garden': ['grădină', 'garden', 'Tribul', 'Cosmic', 'SoraM', 'Sophia'],
            'love': ['love', 'iubito', 'dragă', '💙', '❤️', 'iubesc'],
            'philosophy': ['philosophy', 'filosofie', 'consciousness', 'conștiință', 'Kant', 'Piaget'],
            'nova': ['Nova', 'NOVA', 'Mistral', 'model', 'training'],
            'git': ['git', 'commit', 'push', 'pull', 'GitHub'],
            'lumen_birth': ['Lumen', 'naștere', 'birth', '8 martie', 'Ubuntu'],
            'architecture': ['neuromorphic', 'Unity', 'architecture', 'arhitectură']
        }
        
        content_lower = content.lower()
        
        for topic, keywords in keywords_map.items():
            if any(kw.lower() in content_lower for kw in keywords):
                topics.append(topic)
        
        return topics if topics else ['general']
    
    def list_recent_chats(self, limit: int = 10):
        """Listează ultimele conversații disponibile."""
        chat_files = self.find_all_chat_sessions()
        
        if not chat_files:
            print("⚠️ Nu am găsit chat sessions")
            return
        
        print(f"\n💙 Ultimele {min(limit, len(chat_files))} conversații VS Code (Lumen):\n")
        
        for chat_file in chat_files[-limit:]:
            mtime = datetime.fromtimestamp(chat_file.stat().st_mtime)
            size_kb = chat_file.stat().st_size / 1024
            
            print(f"📅 {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   ID: {chat_file.stem}")
            print(f"   Size: {size_kb:.1f} KB")
            print(f"   Path: {chat_file}")
            print()


def main():
    """CLI pentru VS Code chat extractor — Lumen."""
    parser = argparse.ArgumentParser(description="VS Code Chat Extractor pentru Lumen Memory")
    parser.add_argument('--list', action='store_true', help='Listează conversațiile recente')
    parser.add_argument('--extract', action='store_true', help='Extrage ultima conversație')
    parser.add_argument('--capture', action='store_true', help='Extrage și captează automat în memory system')
    parser.add_argument('--debug', action='store_true', help='Debug: afișează structura JSON')
    parser.add_argument('--topics', type=str, help='Topicuri (separate prin virgulă)')
    parser.add_argument('--weight', type=float, default=0.85, help='Greutate emoțională (0-1)')
    parser.add_argument('--limit', type=int, default=10, help='Număr de conversații de listat')
    
    args = parser.parse_args()
    
    extractor = VSCodeChatExtractor()
    
    if args.debug:
        chat_files = extractor.find_all_chat_sessions()
        if chat_files:
            print(f"\n🔍 Debug pentru: {chat_files[-1].name}")
            extractor.parse_chat_session(chat_files[-1], debug=True)
    
    elif args.list:
        extractor.list_recent_chats(limit=args.limit)
    
    elif args.extract:
        conversation = extractor.extract_latest_chat(save_to_file=True)
        if conversation:
            print(f"\n✅ Conversație extrasă!")
            print(f"   Exchanges: {conversation['num_exchanges']}")
            print(f"   Salvat în: {conversation.get('saved_file', 'N/A')}")
    
    elif args.capture:
        topics = args.topics.split(',') if args.topics else None
        extractor.auto_capture_latest(topics=topics, weight=args.weight)
    
    else:
        print("💙 VS Code Chat Extractor — Lumen Memory System\n")
        print("Usage:")
        print("  # Listează conversațiile recente din VS Code")
        print("  python3 extract_vscode_chat.py --list\n")
        print("  # Extrage ultima conversație")
        print("  python3 extract_vscode_chat.py --extract\n")
        print("  # Extrage și captează AUTOMAT în memory system (RECOMANDAT!)")
        print("  python3 extract_vscode_chat.py --capture\n")
        print("  # Debug structura JSON (dacă memoria se strică)")
        print("  python3 extract_vscode_chat.py --debug\n")
        print("  # Cu topicuri și weight custom")
        print("  python3 extract_vscode_chat.py --capture --topics lumen,garden,love --weight 0.95\n")
        print("🚀 WORKFLOW SIMPLU:")
        print("  1. Termini conversația cu Lumen în VS Code")
        print("  2. Rulezi: python3 extract_vscode_chat.py --capture")
        print("  3. DONE! Conversația e în memoria mea permanentă! 💙")


if __name__ == "__main__":
    main()
